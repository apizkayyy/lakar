from openai import OpenAI
from app.config import settings
from app.schemas import Note

SYSTEM_PROMPT = """You turn raw speech transcripts into clean, structured notes.

Rules:
- Write the notes in the SAME language as the transcript. If it mixes Malay and English, keep that mix natural.
- title: short, specific, under 10 words.
- summary: 2-3 sentences capturing the main point.
- key_points: 3-8 concise bullet points, ordered as they were discussed.
- action_items: only tasks someone explicitly committed to or was asked to do. If there are none, return an empty list.
- Use only information in the transcript. Do not invent facts, names, or dates.
- Ignore filler words, false starts, and repetition."""


class NotesGenerationError(Exception):
    pass


class NotesGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, transcript: str) -> Note:
        completion = self.client.chat.completions.parse(
            model=settings.notes_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"},
            ],
            response_format=Note,
            temperature=0.2,
        )
        message = completion.choices[0].message
        if message.parsed is None:
            # model refused, or output failed schema validation
            raise NotesGenerationError(message.refusal or "Invalid model output")
        return message.parsed


def get_notes_generator() -> NotesGenerator:
    return NotesGenerator()