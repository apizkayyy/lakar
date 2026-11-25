from app.config import settings
from app.providers.stt.base import STTProvider

def get_stt_provider() -> STTProvider:
    if settings.stt_provider == "openai":
        from app.providers.stt.openai_stt import OpenAISTT
        return OpenAISTT()
    raise ValueError(f"Unknown STT provider: {settings.stt_provider}")