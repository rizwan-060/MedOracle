"""Integration tests for MedOracle health, root, and baseline infrastructure."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify root endpoint responds with project information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "MedOracle Test"
    assert "message" in data
    assert data["environment"] == "testing"


def test_health_endpoint(client: TestClient):
    """Verify health endpoint reports healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "medoracle-backend"
    assert data["environment"] == "testing"


def test_v1_root_endpoint(client: TestClient):
    """Verify versioned router is mounted at /api/v1."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "v1"
    assert data["status"] == "active"


def test_cors_headers(client: TestClient):
    """Verify CORS headers are returned for allowed origin."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_not_found_error_format(client: TestClient):
    """Verify 404 response follows consistent error response schema."""
    response = client.get("/nonexistent-endpoint-path")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["error_code"] == "HTTP_ERROR"
    assert "timestamp" in data
