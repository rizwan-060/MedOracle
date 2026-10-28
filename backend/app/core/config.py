"""Application configuration and settings management for MedOracle.

All configuration is loaded via pydantic-settings from environment variables
or the backend/.env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central configuration for MedOracle backend."""

    # Application
    app_name: str = "MedOracle"
    app_env: str = "development"
    debug: bool = True
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5000",
            "http://localhost:8000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8080",
        ]
    )

    # Database
    database_url: str = (
        "postgresql+psycopg://medoracle_user:CHANGE_ME@localhost:5432/medoracle_db"
    )

    # Security & JWT
    secret_key: str = "REPLACE_WITH_A_LOCAL_SECRET_KEY_FOR_DEVELOPMENT"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # LLM Providers (Groq primary, Gemini Flash fallback)
    llm_provider: str = "mock"  # "groq", "gemini", or "mock"
    groq_api_key: str | None = None
    groq_model_primary: str = "llama-3.3-70b-versatile"
    groq_model_fast: str = "llama-3.1-8b-instant"
    gemini_api_key: str | None = None
    gemini_model_fallback: str = "gemini-2.5-flash"

    # Redis & Caching (Step 9.1)
    redis_url: str | None = None  # e.g. "redis://localhost:6379/0"
    redis_cache_enabled: bool = True
    redis_default_ttl: int = 600  # Default TTL in seconds (10 mins)
    redis_key_prefix: str = "medoracle"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
