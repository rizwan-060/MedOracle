"""Laboratory and clinical biomarker endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models import User
from app.database.repositories import LabResultRepository
from app.database.session import get_db
from app.schemas.laboratory import LabResultCreate, LabResultResponse

router = APIRouter(prefix="/laboratory", tags=["Laboratory"])


@router.post("/", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
def record_lab_result(
    payload: LabResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a clinical laboratory test report with biomarkers for the authenticated user."""
    repo = LabResultRepository(db)
    lab = repo.create(user_id=current_user.id, **payload.model_dump())
    return lab


@router.get("/", response_model=List[LabResultResponse])
def list_lab_results(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve historical laboratory test reports for the authenticated user."""
    repo = LabResultRepository(db)
    return repo.list_by_user_id(user_id=current_user.id, limit=limit)


@router.get("/latest", response_model=LabResultResponse)
def get_latest_lab_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the most recent laboratory test report for the authenticated user."""
    repo = LabResultRepository(db)
    lab = repo.get_latest_by_user_id(user_id=current_user.id)
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No laboratory results recorded for this user.",
        )
    return lab


@router.get("/{lab_id}", response_model=LabResultResponse)
def get_lab_result(
    lab_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a specific laboratory test report by identifier with tenant isolation."""
    repo = LabResultRepository(db)
    lab = repo.get_by_id(lab_id=lab_id, user_id=current_user.id)
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratory result not found.",
        )
    return lab


@router.delete("/{lab_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_result(
    lab_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a laboratory test report by identifier with tenant isolation."""
    repo = LabResultRepository(db)
    deleted = repo.delete(lab_id=lab_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratory result not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
