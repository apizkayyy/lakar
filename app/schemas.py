from pydantic import BaseModel, Field
from typing import Literal

class TranscriptResponse(BaseModel):
    transcript: str

class Note(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    action_items: list[str] = []

class NotesRequest(BaseModel):
    transcript: str = Field(min_length=20, max_length=60_000)

class Branch(BaseModel):
    label: str
    children: list[str]

class MindMap(BaseModel):
    root: str
    branches: list[Branch]

class FlowNode(BaseModel):
    id: str
    label: str
    kind: Literal["start_end", "step", "decision"]

class FlowEdge(BaseModel):
    source: str
    target: str
    label: str  # empty string when the edge needs no label

class Flowchart(BaseModel):
    nodes: list[FlowNode]
    edges: list[FlowEdge]

class IllustrateResponse(BaseModel):
    style: str = "mindmap"
    mindmap: MindMap | None = None
    flowchart: Flowchart | None = None
    mermaid: str