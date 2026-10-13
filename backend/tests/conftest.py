"""Shared test fixtures for MedOracle backend test suite."""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings, get_settings


@pytest.fixture
def test_settings() -> Settings:
    """Fixture returning settings configured for testing."""
    return Settings(
        app_name="MedOracle Test",
        app_env="testing",
        debug=True,
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key-for-unit-and-integration-tests",
        llm_provider="mock",
    )


@pytest.fixture
def client(monkeypatch, test_settings: Settings) -> TestClient:
    """Fixture returning a TestClient bound to a test app instance."""
    # Override get_settings with test settings
    monkeypatch.setattr("app.core.config.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.main.get_settings", lambda: test_settings)
    app = create_app()
    return TestClient(app)
