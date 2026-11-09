from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any

import cv2
import numpy as np
import pymupdf
import pytesseract
from PIL import Image, UnidentifiedImageError


MAX_PDF_PAGES = 10
MAX_IMAGE_PIXELS = 20_000_000
MAX_IMAGE_DIMENSION = 3_000
PDF_RENDER_DPI = 180
OCR_CONFIG = "--oem 3 --psm 6"


class ImagePipelineError(RuntimeError):
    """Raised when an uploaded document cannot be processed locally."""


@dataclass
class ProcessedPage:
    page_number: int
    previews: dict[str, bytes]
    baseline_text: str
    enhanced_text: str
    baseline_confidence: float | None
    enhanced_confidence: float | None
    region_count: int


@dataclass
class ProcessedDocument:
    pages: list[ProcessedPage]
    processed_bytes: bytes
    processed_mime_type: str

    @property
    def baseline_text(self) -> str:
        return _join_page_text(self.pages, "baseline_text")

    @property
    def enhanced_text(self) -> str:
        return _join_page_text(self.pages, "enhanced_text")

    def mean_confidence(self, field: str) -> float | None:
        confidences = [
            confidence
            for page in self.pages
            if (confidence := getattr(page, field)) is not None
        ]
        if not confidences:
            return None
        return sum(confidences) / len(confidences)


def _join_page_text(pages: list[ProcessedPage], field: str) -> str:
    return "\n\n".join(getattr(page, field).strip() for page in pages)


def _run_ocr(image: np.ndarray) -> tuple[str, float | None]:
    try:
        data: dict[str, Any] = pytesseract.image_to_data(
            image,
            config=OCR_CONFIG,
            output_type=pytesseract.Output.DICT,
        )
    except (pytesseract.TesseractNotFoundError, pytesseract.TesseractError) as exc:
        raise ImagePipelineError(
            "Tesseract OCR is unavailable. Install the Tesseract executable and "
            "English language data, then restart the app."
        ) from exc

    lines: dict[tuple[int, int, int], list[str]] = {}
    confidences: list[float] = []
    word_count = len(data["text"])
    block_numbers = data.get("block_num", [0] * word_count)
    paragraph_numbers = data.get("par_num", [0] * word_count)
    line_numbers = data.get("line_num", [0] * word_count)
    for text, raw_confidence, block, paragraph, line in zip(
        data["text"],
        data["conf"],
        block_numbers,
        paragraph_numbers,
        line_numbers,
    ):
        word = str(text).strip()
        if word:
            lines.setdefault((int(block), int(paragraph), int(line)), []).append(word)
        try:
            confidence = float(raw_confidence)
        except (TypeError, ValueError):
            continue
        if confidence >= 0:
            confidences.append(confidence)

    mean_confidence = (
        sum(confidences) / len(confidences) if confidences else None
    )
    text = "\n".join(" ".join(words) for words in lines.values())
    return text, mean_confidence


def _preview(image: np.ndarray, *, color: bool = False) -> bytes:
    height, width = image.shape[:2]
    scale = min(1.0, MAX_IMAGE_DIMENSION / max(height, width))
    if scale < 1:
        image = cv2.resize(
            image,
            (round(width * scale), round(height * scale)),
            interpolation=cv2.INTER_AREA,
        )
    if color:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    encoded, buffer = cv2.imencode(".png", image)
    if not encoded:
        raise ImagePipelineError("Could not encode an image preview.")
    return buffer.tobytes()


def _analyze_page(rgb: np.ndarray, page_number: int) -> tuple[ProcessedPage, np.ndarray]:
    if rgb.shape[0] * rgb.shape[1] > MAX_IMAGE_PIXELS:
        raise ImagePipelineError(
            f"Page {page_number} exceeds the {MAX_IMAGE_PIXELS // 1_000_000}-megapixel "
            "processing limit. Resize the image or upload fewer pages."
        )

    baseline_text, baseline_confidence = _run_ocr(rgb)

    grayscale = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(grayscale)
    threshold = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35,
        9,
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    ink = cv2.bitwise_not(threshold)
    opened = cv2.morphologyEx(ink, cv2.MORPH_OPEN, kernel)
    cleaned_ink = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    morphology = cv2.bitwise_not(cleaned_ink)

    line_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(15, rgb.shape[1] // 45), max(2, rgb.shape[0] // 500)),
    )
    text_regions = cv2.dilate(cleaned_ink, line_kernel, iterations=1)
    contours, _ = cv2.findContours(
        text_regions,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    minimum_area = max(20, rgb.shape[0] * rgb.shape[1] * 0.00002)
    boxes = sorted(
        (
            cv2.boundingRect(contour)
            for contour in contours
            if cv2.contourArea(contour) >= minimum_area
        ),
        key=lambda box: (box[1], box[0]),
    )
    segmented = rgb.copy()
    for x, y, width, height in boxes:
        cv2.rectangle(segmented, (x, y), (x + width, y + height), (14, 165, 133), 3)

    enhanced_text, enhanced_confidence = _run_ocr(morphology)
    page = ProcessedPage(
        page_number=page_number,
        previews={
            "Original upload": _preview(rgb, color=True),
            "Grayscale": _preview(grayscale),
            "CLAHE contrast": _preview(contrast),
            "Adaptive threshold": _preview(threshold),
            "Morphology cleanup": _preview(morphology),
            "Segmented text regions": _preview(segmented, color=True),
        },
        baseline_text=baseline_text,
        enhanced_text=enhanced_text,
        baseline_confidence=baseline_confidence,
        enhanced_confidence=enhanced_confidence,
        region_count=len(boxes),
    )
    return page, morphology


def _decode_image(file_bytes: bytes) -> np.ndarray:
    try:
        with Image.open(BytesIO(file_bytes)) as image:
            width, height = image.size
    except (
        Image.DecompressionBombError,
        UnidentifiedImageError,
        OSError,
    ) as exc:
        raise ImagePipelineError("The uploaded image could not be decoded.") from exc
    if width * height > MAX_IMAGE_PIXELS:
        raise ImagePipelineError(
            f"Images are limited to {MAX_IMAGE_PIXELS // 1_000_000} megapixels "
            "for reliable processing on the free deployment."
        )

    decoded = cv2.imdecode(np.frombuffer(file_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if decoded is None:
        raise ImagePipelineError("The uploaded image could not be decoded.")
    return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)


def _render_pdf_page(page: pymupdf.Page) -> np.ndarray:
    scale = PDF_RENDER_DPI / 72
    if page.rect.width * page.rect.height * scale * scale > MAX_IMAGE_PIXELS:
        raise ImagePipelineError(
            "A PDF page exceeds the processing limit at the configured render "
            "resolution. Reduce the page size or resolution and upload again."
        )
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
    samples = np.frombuffer(pixmap.samples, dtype=np.uint8)
    image = samples.reshape(pixmap.height, pixmap.width, pixmap.n)
    if pixmap.n == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    elif pixmap.n == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return image


def process_document(file_bytes: bytes, mime_type: str) -> ProcessedDocument:
    """Run baseline OCR and the visible OpenCV pipeline; return only enhanced pages for AI."""
    if not file_bytes:
        raise ImagePipelineError("The uploaded document is empty.")

    pages: list[ProcessedPage] = []
    if mime_type == "application/pdf":
        try:
            source_pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
        except (pymupdf.FileDataError, ValueError) as exc:
            raise ImagePipelineError("The uploaded PDF could not be opened.") from exc

        with source_pdf:
            if source_pdf.needs_pass:
                raise ImagePipelineError("Password-protected PDFs are not supported.")
            if source_pdf.page_count > MAX_PDF_PAGES:
                raise ImagePipelineError(
                    f"PDFs are limited to {MAX_PDF_PAGES} pages on the free deployment. "
                    "Split the document and process each part separately."
                )
            if source_pdf.page_count == 0:
                raise ImagePipelineError("The uploaded PDF contains no pages.")

            enhanced_pdf = pymupdf.open()
            with enhanced_pdf:
                for index in range(source_pdf.page_count):
                    source_page = source_pdf.load_page(index)
                    rgb = _render_pdf_page(source_page)
                    processed_page, morphology = _analyze_page(rgb, index + 1)
                    pages.append(processed_page)
                    encoded, buffer = cv2.imencode(".png", morphology)
                    if not encoded:
                        raise ImagePipelineError(
                            f"Could not encode processed PDF page {index + 1}."
                        )
                    target_page = enhanced_pdf.new_page(
                        width=source_page.rect.width,
                        height=source_page.rect.height,
                    )
                    target_page.insert_image(target_page.rect, stream=buffer.tobytes())

                processed_bytes = enhanced_pdf.tobytes(garbage=4, deflate=True)
        return ProcessedDocument(pages, processed_bytes, "application/pdf")

    if mime_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise ImagePipelineError(
            "Unsupported file type. Upload a PDF, PNG, or JPEG image."
        )

    rgb = _decode_image(file_bytes)
    page, morphology = _analyze_page(rgb, 1)
    encoded, buffer = cv2.imencode(".png", morphology)
    if not encoded:
        raise ImagePipelineError("Could not encode the processed image.")
    return ProcessedDocument([page], buffer.tobytes(), "image/png")
