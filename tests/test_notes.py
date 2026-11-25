from fastapi.testclient import TestClient
from app.main import app
from app.schemas import Note
from app.services.notes import get_notes_generator

client = TestClient(app)


class FakeGenerator:
    def generate(self, transcript: str) -> Note:
        return Note(
            title="Sprint planning",
            summary="Team agreed on the sprint scope.",
            key_points=["Scope agreed"],
            action_items=["Hafiz to draft the spec"],
        )


def test_notes_ok():
    app.dependency_overrides[get_notes_generator] = lambda: FakeGenerator()
    try:
        r = client.post("/notes", json={"transcript": "x" * 30})
        assert r.status_code == 200
        assert r.json()["title"] == "Sprint planning"
        assert r.json()["action_items"] == ["Hafiz to draft the spec"]
    finally:
        app.dependency_overrides.clear()


def test_notes_rejects_short_transcript():
    r = client.post("/notes", json={"transcript": "hi"})
    assert r.status_code == 422