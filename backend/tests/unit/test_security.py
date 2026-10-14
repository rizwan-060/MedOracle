"""Unit tests for security, bcrypt password hashing, and JWT handling."""

from datetime import timedelta
import pytest
from fastapi import HTTPException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing_and_verification():
    """Verify bcrypt hash generation and validation."""
    raw_pw = "SuperSecretPassword123!"
    hashed = get_password_hash(raw_pw)

    assert hashed != raw_pw
    assert hashed.startswith("$2b$")
    assert verify_password(raw_pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_access_token_creation_and_payload():
    """Verify access token generation and claims."""
    user_id = "test-user-uuid-12345"
    token = create_access_token(user_id)
    payload = decode_token(token)

    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_refresh_token_creation_and_payload():
    """Verify refresh token generation and claims."""
    user_id = "test-user-uuid-67890"
    token = create_refresh_token(user_id)
    payload = decode_token(token)

    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_expired_token_rejection():
    """Verify expired token raises 401 HTTPException."""
    user_id = "test-user-uuid-expired"
    # Create token expired 10 minutes ago
    expired_token = create_access_token(
        user_id, expires_delta=timedelta(minutes=-10)
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_tampered_token_rejection():
    """Verify tampered token raises 401 HTTPException."""
    user_id = "test-user-uuid-tampered"
    valid_token = create_access_token(user_id)
    # Tamper with the payload segment
    tampered_token = valid_token[:-4] + "wxyz"
    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered_token)
    assert exc_info.value.status_code == 401
