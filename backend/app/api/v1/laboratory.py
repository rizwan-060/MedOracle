"""Laboratory and clinical biomarker endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models import User
from app.database.repositories import LabResultRepository
import time
from app.database.session import get_db
from app.schemas.laboratory import (
    BiomarkerNormalizationBatchRequest,
    BiomarkerNormalizationBatchResponse,
    LabResultCreate,
    LabResultResponse,
)
from app.services.biomarker_normalizer import BiomarkerEntityNormalizer

router = APIRouter(prefix="/laboratory", tags=["Laboratory"])


@router.post(
    "/biomarkers/normalize",
    response_model=BiomarkerNormalizationBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Normalize OCR-extracted laboratory biomarkers and perform canonical unit conversions (Step 8.4.3)",
)
def normalize_biomarkers(
    payload: BiomarkerNormalizationBatchRequest,
    current_user: User = Depends(get_current_user),
) -> BiomarkerNormalizationBatchResponse:
    """Normalize raw OCR-extracted laboratory items, convert units, and validate against clinical registries.

    Features:
    - Resolves raw test names (e.g. 'Fasting B.S.', 'S. Creatinine') to canonical MedOracle IDs.
    - Strictly delineates non-interchangeable biomarkers (BNP vs. NT-proBNP; Troponin I vs. T; hs vs. standard).
    - Converts SI and traditional clinical units (mmol/L -> mg/dL, µmol/L -> mg/dL, g/L -> g/dL).
    - Retains full provenance: raw strings, conversion multipliers, laboratory reference intervals, and audit caveats.
    - Returns clean canonical_biomarkers_dict ready for immediate consumption by downstream ML/risk models.
    """
    start_time = time.perf_counter()

    batch_result = BiomarkerEntityNormalizer.normalize_batch(
        extracted_items=[item.model_dump() for item in payload.extracted_items],
        patient_id=payload.patient_id or current_user.id,
        source_document_id=payload.source_document_id,
        source_document_url=payload.source_document_url,
        lab_name=payload.lab_name,
        specimen_collection_date=payload.specimen_collection_date,
        report_date=payload.report_date,
    )

    execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    batch_result["execution_time_ms"] = execution_time_ms

    return BiomarkerNormalizationBatchResponse(**batch_result)


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
