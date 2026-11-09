import mimetypes

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool

from services.entity_extraction import (
    GeminiConfigurationError,
    extract_entities,
)

router = APIRouter()


@router.post("/extract")
async def extract_entities_from_acord125(file: UploadFile = File(...)):
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0]
    if mime_type not in {"application/pdf", "image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Upload a PDF, PNG, JPEG, or WEBP file.",
        )

    try:
        entities = await run_in_threadpool(extract_entities, file_bytes, mime_type)
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini extraction failed: {exc}",
        ) from exc

    return {"entities": entities}