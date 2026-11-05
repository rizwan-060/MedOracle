"""Security, cryptography, and token authentication services for MedOracle.

Implements direct bcrypt password hashing and python-jose JWT creation/verification.
No passlib dependency is used, ensuring 100% compatibility with bcrypt 5.x.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.database.models import User
from app.database.repositories import UserRepository
from app.schemas.auth import TokenPayload

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    auto_error=False,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt with work factor 12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(subject),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token's signature and expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: Resolves authenticated User from Bearer token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    token_type = payload.get("type")
    user_id = payload.get("sub")

    if token_type != "access" or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type or missing identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def validate_patient_access(
    patient_id: Optional[str],
    current_user: User,
    db: Optional[Session] = None,
) -> bool:
    """Validate that the authenticated user has legitimate authorization to access patient_id.

    Verifies:
    1. If patient_id is omitted or equals current_user.id -> Authorized (accessing own record).
    2. If patient_id matches current_user.patient_profile.id -> Authorized.
    3. If db is provided and patient_id matches a PatientProfile owned by current_user.id in DB -> Authorized.
    4. Otherwise -> Raises HTTP 403 Forbidden. No synthetic bypasses permitted.
    """
    if not patient_id or patient_id == current_user.id:
        return True

    # Check relation via in-memory current_user.patient_profile if already loaded
    if getattr(current_user, "patient_profile", None) is not None:
        if current_user.patient_profile.id == patient_id:
            return True

    # Persistent database-backed ownership validation
    if db is not None:
        from app.database.models import PatientProfile
        from sqlalchemy import select
        profile = db.scalars(
            select(PatientProfile).where(
                (PatientProfile.id == patient_id) & (PatientProfile.user_id == current_user.id)
            )
        ).first()
        if profile is not None:
            return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cross-tenant access forbidden: Cannot access or process clinical data for another patient.",
    )

