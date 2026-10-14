"""Shared test fixtures for MedOracle backend test suite."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.database.session import Base, get_db
from app.main import create_app
# Ensure all models are loaded
import app.database.models  # noqa: F401


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
def test_engine():
    """Fixture returning an in-memory SQLite engine with StaticPool."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Fixture returning an active SQLAlchemy database session bound to test_engine."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(monkeypatch, test_settings: Settings, test_engine):
    """Fixture returning a TestClient bound to test_engine."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.core.config.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.main.get_settings", lambda: test_settings)

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
