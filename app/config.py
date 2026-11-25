from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: str = ""
    stt_provider: str = "openai"
    stt_model: str = "gpt-4o-transcribe"
    max_upload_mb: int = 25
    notes_model: str = "gpt-4o-mini"

settings = Settings()