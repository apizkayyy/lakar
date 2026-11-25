from typing import Protocol

class STTProvider(Protocol):
    def transcribe(
        self, audio_path: str, language: str | None = None, prompt: str | None = None
    ) -> str: ...