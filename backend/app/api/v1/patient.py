"""Patient demographic and biometric profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models import User
from app.database.repositories import PatientProfileRepository
from app.database.session import get_db
from app.schemas.patient import PatientProfileResponse, PatientProfileUpdate

router = APIRouter(prefix="/patient", tags=["Patient Profile"])


@router.get("/profile", response_model=PatientProfileResponse)
def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the biometric profile of the authenticated user."""
    repo = PatientProfileRepository(db)
    profile = repo.get_by_user_id(current_user.id)
    if not profile:
        # Automatically provision default profile container if not yet populated
        profile = repo.create_or_update(user_id=current_user.id)
    return profile


@router.put("/profile", response_model=PatientProfileResponse)
def update_patient_profile(
    payload: PatientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update demographic and biometric parameters for the authenticated user."""
    repo = PatientProfileRepository(db)
    update_data = payload.model_dump(exclude_unset=True)
    profile = repo.create_or_update(user_id=current_user.id, **update_data)
    return profile
