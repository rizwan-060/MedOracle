"""Integration tests for authentication APIs (/api/v1/auth)."""

from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    """Test successful user registration."""
    payload = {
        "email": "dr.ahmed@example.com",
        "password": "StrongPassword123!",
        "full_name": "Dr. Ahmed Bilal",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "dr.ahmed@example.com"
    assert data["full_name"] == "Dr. Ahmed Bilal"
    assert "id" in data
    assert "hashed_password" not in data
    assert data["is_active"] is True


def test_register_duplicate_email_fails(client: TestClient):
    """Test duplicate registration with same email returns 400 Bad Request."""
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123!",
        "full_name": "First User",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with duplicate email
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_register_invalid_data(client: TestClient):
    """Test validation errors on weak password or invalid email format."""
    # Short password (< 8 chars)
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "valid@example.com", "password": "short", "full_name": "Name"},
    )
    assert res.status_code == 422


def test_login_success(client: TestClient):
    """Test login with valid credentials returns access and refresh tokens."""
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login.test@example.com",
            "password": "ValidPassword123!",
            "full_name": "Login User",
        },
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "login.test@example.com", "password": "ValidPassword123!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] > 0


def test_login_invalid_password(client: TestClient):
    """Test login with wrong password returns 401 Unauthorized."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "RealPassword123!",
            "full_name": "Test User",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPassword!"},
    )
    assert res.status_code == 401
    assert "invalid" in res.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient):
    """Test login with unknown email returns 401 Unauthorized."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert res.status_code == 401


def test_refresh_token_flow(client: TestClient):
    """Test token refresh exchange with valid refresh token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "Password123!",
            "full_name": "Refresh User",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "Password123!"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Exchange refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


def test_refresh_rejects_access_token(client: TestClient):
    """Test refresh endpoint rejects access tokens."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "tokenreject@example.com",
            "password": "Password123!",
            "full_name": "Reject User",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "tokenreject@example.com", "password": "Password123!"},
    )
    access_token = login_res.json()["access_token"]

    # Try refreshing using an access token instead of refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": access_token}
    )
    assert refresh_res.status_code == 401


def test_get_current_user_me(client: TestClient):
    """Test /api/v1/auth/me returns authenticated user profile."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "me.endpoint@example.com",
            "password": "Password123!",
            "full_name": "Me Profile",
        },
    )
    user_id = reg.json()["id"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "me.endpoint@example.com", "password": "Password123!"},
    )
    token = login.json()["access_token"]

    # Call /me with Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["id"] == user_id
    assert profile["email"] == "me.endpoint@example.com"
    assert profile["full_name"] == "Me Profile"


def test_get_current_user_unauthorized(client: TestClient):
    """Test /api/v1/auth/me fails when unauthenticated."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
