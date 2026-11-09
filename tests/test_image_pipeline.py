import unittest
from io import BytesIO
from unittest.mock import patch

import cv2
import numpy as np
import pymupdf
import pytesseract
from PIL import Image

from services.image_pipeline import (
    MAX_PDF_PAGES,
    ImagePipelineError,
    process_document,
)


def fake_ocr_data(*args, **kwargs):
    return {"text": ["CLAIM", "FORM"], "conf": ["90", "80"]}


def make_test_image() -> bytes:
    image = np.full((240, 360, 3), 255, dtype=np.uint8)
    cv2.putText(image, "CLAIM FORM", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    encoded, buffer = cv2.imencode(".png", image)
    if not encoded:
        raise AssertionError("Could not encode the synthetic test image.")
    return buffer.tobytes()


def make_test_pdf(page_count: int) -> bytes:
    document = pymupdf.open()
    for _ in range(page_count):
        page = document.new_page(width=360, height=240)
        page.insert_text((20, 100), "CLAIM FORM", fontsize=20)
    content = document.tobytes()
    document.close()
    return content


class ImagePipelineTests(unittest.TestCase):
    @patch("services.image_pipeline.pytesseract.image_to_data", side_effect=fake_ocr_data)
    def test_image_runs_baseline_and_enhanced_ocr_and_produces_stages(self, ocr):
        result = process_document(make_test_image(), "image/png")

        self.assertEqual(ocr.call_count, 2)
        self.assertEqual(result.processed_mime_type, "image/png")
        self.assertEqual(result.pages[0].baseline_text, "CLAIM FORM")
        self.assertEqual(result.pages[0].enhanced_text, "CLAIM FORM")
        self.assertEqual(result.pages[0].baseline_confidence, 85)
        self.assertEqual(
            set(result.pages[0].previews),
            {
                "Original upload",
                "Grayscale",
                "CLAHE contrast",
                "Adaptive threshold",
                "Morphology cleanup",
                "Segmented text regions",
            },
        )
        enhanced = cv2.imdecode(
            np.frombuffer(result.processed_bytes, dtype=np.uint8),
            cv2.IMREAD_GRAYSCALE,
        )
        self.assertIsNotNone(enhanced)

    @patch("services.image_pipeline.pytesseract.image_to_data", side_effect=fake_ocr_data)
    def test_pdf_processes_each_page_and_returns_enhanced_pdf(self, ocr):
        result = process_document(make_test_pdf(2), "application/pdf")

        self.assertEqual(ocr.call_count, 4)
        self.assertEqual(len(result.pages), 2)
        self.assertEqual(result.processed_mime_type, "application/pdf")
        with pymupdf.open(stream=result.processed_bytes, filetype="pdf") as enhanced_pdf:
            self.assertEqual(enhanced_pdf.page_count, 2)

    @patch("services.image_pipeline.pytesseract.image_to_data", side_effect=fake_ocr_data)
    def test_pdf_over_page_limit_fails_explicitly(self, ocr):
        with self.assertRaisesRegex(ImagePipelineError, str(MAX_PDF_PAGES)):
            process_document(make_test_pdf(MAX_PDF_PAGES + 1), "application/pdf")
        ocr.assert_not_called()

    @patch("services.image_pipeline.pytesseract.image_to_data")
    def test_oversized_image_is_rejected_before_full_decode(self, ocr):
        image_bytes = BytesIO()
        Image.new("1", (5_000, 5_000), 1).save(image_bytes, format="PNG")

        with self.assertRaisesRegex(ImagePipelineError, "20 megapixels"):
            process_document(image_bytes.getvalue(), "image/png")
        ocr.assert_not_called()

    @patch(
        "services.image_pipeline.pytesseract.image_to_data",
        side_effect=pytesseract.TesseractNotFoundError,
    )
    def test_missing_tesseract_is_reported_as_an_installation_error(self, _ocr):
        with self.assertRaisesRegex(ImagePipelineError, "Tesseract OCR is unavailable"):
            process_document(make_test_image(), "image/png")


if __name__ == "__main__":
    unittest.main()
