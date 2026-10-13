"""Unit tests for MedOracle configuration management."""

import os
from app.core.config import Settings, get_settings


def test_default_settings():
    """Verify default settings values when no environment overrides exist."""
    settings = Settings()
    assert settings.app_name == "MedOracle"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.debug is True
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.llm_provider in ["mock", "groq", "gemini"]


def test_settings_env_override(monkeypatch):
    """Verify environment variables override configuration defaults."""
    monkeypatch.setenv("APP_NAME", "MedOracle Custom")
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("API_V1_PREFIX", "/api/custom")

    settings = Settings()
    assert settings.app_name == "MedOracle Custom"
    assert settings.app_env == "staging"
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/custom"


def test_get_settings_caching():
    """Verify get_settings returns a cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
