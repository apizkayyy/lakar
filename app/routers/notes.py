from fastapi import APIRouter, Depends, HTTPException
from app.schemas import Note, NotesRequest
from app.services.notes import (
    NotesGenerationError,
    NotesGenerator,
    get_notes_generator,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note)
def make_notes(
    body: NotesRequest,
    generator: NotesGenerator = Depends(get_notes_generator),
):
    try:
        return generator.generate(body.transcript)
    except NotesGenerationError as e:
        raise HTTPException(502, f"Could not generate notes: {e}")