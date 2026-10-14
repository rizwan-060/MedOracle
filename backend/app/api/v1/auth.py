"""Authentication and account lifecycle API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.database.session import get_db
from app.database.models import User
from app.database.repositories import UserRepository
from app.schemas.auth import (
    RefreshTokenRequest,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient user account",
)
def register_user(
    data: UserRegister, db: Session = Depends(get_db)
) -> UserResponse:
    """Register a new user account with hashed credentials."""
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    hashed_pw = get_password_hash(data.password)
    new_user = user_repo.create(
        email=data.email,
        hashed_password=hashed_pw,
        full_name=data.full_name,
    )
    return UserResponse.model_validate(new_user)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT access and refresh tokens",
)
def login_user(
    data: UserLogin, db: Session = Depends(get_db)
) -> Token:
    """Validate credentials and return fresh JWT tokens."""
    identifier = data.username or data.email
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(str(identifier))

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact support.",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Exchange valid refresh token for fresh access and refresh tokens",
)
def refresh_token(
    data: RefreshTokenRequest, db: Session = Depends(get_db)
) -> Token:
    """Validate refresh token and issue new token pair."""
    payload = decode_token(data.refresh_token)
    token_type = payload.get("type")
    user_id = payload.get("sub")

    if token_type != "refresh" or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided token is not a valid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve authenticated user profile",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
