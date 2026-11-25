from fastapi.testclient import TestClient
from app.main import app
from app.schemas import Branch, MindMap, Flowchart, FlowNode, FlowEdge
from app.services.illustrate import clean, get_mindmap_generator, render_mermaid, render_flowchart

client = TestClient(app)


def test_clean_strips_unsafe_chars():
    assert clean('Deploy (v2): "now"') == "Deploy v2 now"


def test_clean_truncates_and_never_empty():
    assert len(clean("x" * 200)) <= 60
    assert clean("()") == "-"


def test_render_mermaid():
    mm = MindMap(root="Sprint", branches=[Branch(label="Scope", children=["API", "UI"])])
    assert render_mermaid(mm) == (
        "mindmap\n  root((Sprint))\n    Scope\n      API\n      UI"
    )


class FakeGenerator:
    def generate(self, note):
        return MindMap(root="Sprint", branches=[Branch(label="Scope", children=["API"])])


def test_illustrate_endpoint():
    app.dependency_overrides[get_mindmap_generator] = lambda: FakeGenerator()
    try:
        r = client.post(
            "/illustrate",
            json={"title": "t", "summary": "s", "key_points": ["a"], "action_items": []},
        )
        assert r.status_code == 200
        assert r.json()["mermaid"].startswith("mindmap")
    finally:
        app.dependency_overrides.clear()

def test_render_flowchart_drops_bad_edges_and_sanitizes():
    fc = Flowchart(
        nodes=[
            FlowNode(id="a", label="Start", kind="start_end"),
            FlowNode(id="b", label="Valid?", kind="decision"),
            FlowNode(id="c", label="Save (db)", kind="step"),
        ],
        edges=[
            FlowEdge(source="a", target="b", label=""),
            FlowEdge(source="b", target="c", label="Yes"),
            FlowEdge(source="b", target="zzz", label="No"),  # unknown id, dropped
        ],
    )
    assert render_flowchart(fc) == "\n".join([
        "flowchart TD",
        '  n0(["Start"])',
        '  n1{"Valid?"}',
        '  n2["Save db"]',
        "  n0 --> n1",
        '  n1 -->|"Yes"| n2',
    ])