"""Patient medical and family history endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models import User
from app.database.repositories import MedicalHistoryRepository
from app.database.session import get_db
from app.schemas.patient import (
    MedicalHistoryCreate,
    MedicalHistoryResponse,
    MedicalHistoryUpdate,
)

router = APIRouter(prefix="/medical-history", tags=["Medical History"])


@router.get("/", response_model=MedicalHistoryResponse)
def get_medical_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the latest medical and family history for the authenticated user."""
    repo = MedicalHistoryRepository(db)
    history = repo.get_latest_by_user_id(current_user.id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No medical history found for this user.",
        )
    return history


@router.post("/", response_model=MedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_medical_history(
    payload: MedicalHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a new medical and family history entry for the authenticated user."""
    repo = MedicalHistoryRepository(db)
    history = repo.create(user_id=current_user.id, **payload.model_dump())
    return history


@router.put("/", response_model=MedicalHistoryResponse)
def update_or_create_medical_history(
    payload: MedicalHistoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the current user's active medical history record."""
    repo = MedicalHistoryRepository(db)
    data = payload.model_dump(exclude_unset=True)
    history = repo.create_or_update(user_id=current_user.id, **data)
    return history
