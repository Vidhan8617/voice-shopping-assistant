"""
Application configuration.

We use pydantic-settings so config is validated at startup (fail fast if a
required env var is missing) instead of crashing later mid-request.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Voice Shopping Assistant API"
    environment: str = "development"

    # Database — defaults to local SQLite file, swap via env var in prod
    database_url: str = "sqlite:///./shopping_assistant.db"

    # Groq is used as the LLM fallback for flexible voice phrasing.
    # Optional on purpose: the app must still work (via rule-based parsing)
    # if this key is missing or the free-tier quota is hit.
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"

    # CORS — the frontend origin(s) allowed to call this API
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Cached so we don't re-parse .env on every request — Settings() is called
    once per process via dependency injection.
    """
    return Settings()
