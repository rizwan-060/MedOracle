"""Authentication and user account Pydantic v2 schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    """Base user attributes."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserRegister(UserBase):
    """Schema for user registration request."""

    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Schema for credentials login request, accepting email or username."""

    username: Optional[EmailStr] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_identifier(self) -> "UserLogin":
        if not self.username and not self.email:
            raise ValueError("Either 'email' or 'username' must be provided.")
        if not self.username:
            self.username = self.email
        return self


class UserResponse(UserBase):
    """Public user response schema (never exposes hashed password)."""

    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT access and refresh token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""

    sub: str
    type: str = "access"
    exp: int
    iat: int


class RefreshTokenRequest(BaseModel):
    """Refresh token exchange request."""

    refresh_token: str
