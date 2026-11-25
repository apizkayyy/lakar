from openai import OpenAI
from app.config import settings

class OpenAISTT:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def transcribe(
        self, audio_path: str, language: str | None = None, prompt: str | None = None
    ) -> str:
        with open(audio_path, "rb") as audio:
            kwargs = {"model": settings.stt_model, "file": audio}
            if language:
                kwargs["language"] = language
            if prompt:
                kwargs["prompt"] = prompt
            return self.client.audio.transcriptions.create(**kwargs).text