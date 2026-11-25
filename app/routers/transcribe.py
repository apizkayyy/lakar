import os, tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.config import settings
from app.schemas import TranscriptResponse
from app.providers.stt import get_stt_provider

router = APIRouter(prefix="/transcribe", tags=["transcribe"])

@router.post("", response_model=TranscriptResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: str | None = None,
    stt=Depends(get_stt_provider),
):
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Audio over {settings.max_upload_mb}MB")

    suffix = os.path.splitext(file.filename or "")[1] or ".mp3"

    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
        text = stt.transcribe(path, language)
    finally:
        os.remove(path)

    return TranscriptResponse(transcript=text)