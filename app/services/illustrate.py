import re
from openai import OpenAI
from app.config import settings
from app.schemas import Flowchart, MindMap, Note

SYSTEM_PROMPT = """You convert structured notes into a mind map outline.

Rules:
- Write labels in the SAME language as the notes. Keep Malay/English mixing natural.
- root: the main topic, under 6 words.
- branches: 3-6 main themes drawn from the key points and action items.
- Each branch has 0-4 children: short supporting details.
- Every label must be under 6 words. No full sentences.
- Use only information in the notes. Do not invent facts."""

FLOW_PROMPT = """You convert structured notes into a process flowchart.

Rules:
- Write labels in the SAME language as the notes. Keep Malay/English mixing natural.
- Exactly one node with kind "start_end" at the beginning and one at the end.
- Use kind "step" for actions and kind "decision" for yes/no questions.
- Give every node a short unique id (a, b, c...). Every edge must use ids that exist.
- Decision nodes need two outgoing edges labelled like "Yes" and "No" (in the notes' language).
- All other edges use an empty string as the label.
- 4-12 nodes in total. Every label under 8 words.
- Follow the order in the notes. If the notes are not a process, present the key points as a simple sequence.
- Use only information in the notes. Do not invent steps."""

MAX_NODES = 15
MAX_EDGES = 25
MAX_EDGE_LABEL = 20

MAX_BRANCHES = 8
MAX_CHILDREN = 5
MAX_LABEL = 60

# Characters that have meaning in Mermaid mindmap syntax
_UNSAFE = re.compile(r'[()\[\]{}"`:;#<>|\\]')

class IllustrationError(Exception):
    pass

def clean(text: str, max_len: int = MAX_LABEL) -> str:
    text = _UNSAFE.sub(" ", text)
    text = " ".join(text.split())  # collapse whitespace and newlines
    if len(text) > max_len:
        text = text[: max_len - 3].rstrip() + "..."
    return text or "-"


def render_mermaid(mm: MindMap) -> str:
    lines = ["mindmap", f"  root(({clean(mm.root)}))"]
    for branch in mm.branches[:MAX_BRANCHES]:
        lines.append(f"    {clean(branch.label)}")
        for child in branch.children[:MAX_CHILDREN]:
            lines.append(f"      {clean(child)}")
    return "\n".join(lines)

def render_flowchart(fc: Flowchart) -> str:
    nodes = fc.nodes[:MAX_NODES]
    ids = {n.id: f"n{i}" for i, n in enumerate(nodes)}  # our ids, never the LLM's

    lines = ["flowchart TD"]
    for n in nodes:
        nid, label = ids[n.id], clean(n.label)
        if n.kind == "decision":
            lines.append(f'  {nid}{{"{label}"}}')
        elif n.kind == "start_end":
            lines.append(f'  {nid}(["{label}"])')
        else:
            lines.append(f'  {nid}["{label}"]')

    for e in fc.edges[:MAX_EDGES]:
        if e.source not in ids or e.target not in ids:
            continue  # drop edges that point at nodes that don't exist
        src, dst = ids[e.source], ids[e.target]
        text = clean(e.label, MAX_EDGE_LABEL) if e.label.strip() else ""
        if text and text != "-":
            lines.append(f'  {src} -->|"{text}"| {dst}')
        else:
            lines.append(f"  {src} --> {dst}")
    return "\n".join(lines)


class MindMapGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, note: Note) -> MindMap:
        completion = self.client.chat.completions.parse(
            model=settings.notes_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": note.model_dump_json()},
            ],
            response_format=MindMap,
            temperature=0.2,
        )
        message = completion.choices[0].message
        if message.parsed is None:
            raise IllustrationError(message.refusal or "Invalid model output")
        return message.parsed
    
    def generate_flowchart(self, note: Note) -> Flowchart:
        completion = self.client.chat.completions.parse(
            model=settings.notes_model,
            messages=[
                {"role": "system", "content": FLOW_PROMPT},
                {"role": "user", "content": note.model_dump_json()},
            ],
            response_format=Flowchart,
            temperature=0.2,
        )
        message = completion.choices[0].message
        if message.parsed is None:
            raise IllustrationError(message.refusal or "Invalid model output")
        if len(message.parsed.nodes) < 2:
            raise IllustrationError("Not enough steps to draw a flowchart")
        return message.parsed


def get_mindmap_generator() -> MindMapGenerator:
    return MindMapGenerator()