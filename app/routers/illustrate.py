from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from app.schemas import IllustrateResponse, Note, Flowchart
from app.services.illustrate import (
    IllustrationError,
    MindMapGenerator,
    get_mindmap_generator,
    render_mermaid,
)

router = APIRouter(prefix="/illustrate", tags=["illustrate"])


@router.post("", response_model=IllustrateResponse)
def illustrate(
    note: Note,
    style: Literal["mindmap", "flowchart"] = "mindmap",
    generator: MindMapGenerator = Depends(get_mindmap_generator),
):
    try:
        if style == "flowchart":
            fc = generator.generate_flowchart(note)
            return IllustrateResponse(
                style=style, flowchart=fc, mermaid=render_flowchart(fc)
            )
        mm = generator.generate(note)
    except IllustrationError as e:
        raise HTTPException(502, f"Could not generate illustration: {e}")
    return IllustrateResponse(style=style, mindmap=mm, mermaid=render_mermaid(mm))