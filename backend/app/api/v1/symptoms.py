"""Patient symptom reporting endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models import User
from app.database.repositories import SymptomReportRepository
from app.database.session import get_db
from app.schemas.symptoms import SymptomReportCreate, SymptomReportResponse

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])


@router.post("/", response_model=SymptomReportResponse, status_code=status.HTTP_201_CREATED)
def record_symptoms(
    payload: SymptomReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new symptom report for clinical analysis."""
    repo = SymptomReportRepository(db)
    data = payload.model_dump()
    reported_text = data.pop("reported_text")
    # Auto-extract canonical symptoms via NLP extractor if structured_symptoms is empty
    if not data.get("structured_symptoms") and reported_text:
        try:
            from app.ml.inference.predictor import RealtimePredictor
            extractor = RealtimePredictor.get_instance().nlp_extractor
            nlp_result = extractor.extract(reported_text)
            data["structured_symptoms"] = nlp_result.get("detected_symptoms", [])
        except Exception:
            pass
    report = repo.create(user_id=current_user.id, reported_text=reported_text, **data)
    return report


@router.get("/", response_model=List[SymptomReportResponse])
def list_symptoms(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List historical symptom reports recorded by the authenticated user."""
    repo = SymptomReportRepository(db)
    return repo.list_by_user_id(user_id=current_user.id, limit=limit)


@router.get("/{report_id}", response_model=SymptomReportResponse)
def get_symptom_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a specific symptom report by identifier with tenant isolation."""
    repo = SymptomReportRepository(db)
    report = repo.get_by_id(report_id=report_id, user_id=current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom report not found.",
        )
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_symptom_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a symptom report by identifier with tenant isolation."""
    repo = SymptomReportRepository(db)
    deleted = repo.delete(report_id=report_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom report not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
