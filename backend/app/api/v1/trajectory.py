"""Disease Trajectory Forecasting API Router."""

import logging
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.disease_trajectory_agent import DiseaseTrajectoryAgent
from app.core.security import get_current_user, validate_patient_access
from app.database.models import User
from app.database.repositories import (
    LabResultRepository,
    MedicalHistoryRepository,
    SymptomReportRepository,
    TrajectoryForecastRepository,
)
from app.database.session import get_db
from app.schemas.trajectory import (
    DiseaseTrajectoryResult,
    TrajectoryComparisonResponse,
    TrajectoryForecastRequest,
    TrajectoryForecastResponse,
    TrajectoryObservationCreate,
    TrajectoryObservationResponse,
)

logger = logging.getLogger("trajectory_api")

router = APIRouter(prefix="/trajectory", tags=["Disease Trajectory Forecasting"])


@router.post(
    "/forecast",
    response_model=TrajectoryForecastResponse,
    summary="Generate and persist a multi-horizon disease trajectory forecast",
)
def generate_trajectory_forecast(
    payload: TrajectoryForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrajectoryForecastResponse:
    """Generate a disease trajectory forecast from patient longitudinal history and Step 12 consensus."""
    validate_patient_access(payload.patient_id, current_user, db)
    target_patient_id = payload.patient_id or current_user.id
    start_time = time.perf_counter()

    # Load longitudinal records from DB when not explicitly overridden in payload
    lab_history = payload.lab_history
    if lab_history is None:
        db_labs = LabResultRepository(db).list_by_user_id(target_patient_id, limit=50)
        lab_history = [
            {
                "id": rec.id,
                "test_date": rec.test_date.isoformat() if rec.test_date else rec.created_at.isoformat(),
                "biomarkers": rec.biomarkers or {},
            }
            for rec in db_labs
        ]

    symptom_history = payload.symptom_history
    if symptom_history is None:
        db_syms = SymptomReportRepository(db).list_by_user_id(target_patient_id, limit=50)
        symptom_history = [
            {
                "id": rec.id,
                "created_at": rec.created_at.isoformat(),
                "severity_self_rating": rec.severity_self_rating,
            }
            for rec in db_syms
        ]

    med_history = payload.medical_history_data
    if med_history is None:
        db_hist = MedicalHistoryRepository(db).get_latest_by_user_id(target_patient_id)
        if db_hist:
            med_history = {
                "chronic_conditions": db_hist.chronic_conditions or [],
                "current_medications": db_hist.current_medications or [],
                "notes": db_hist.notes or "",
            }

    agent = DiseaseTrajectoryAgent()
    result = agent.forecast_trajectory(
        patient_id=target_patient_id,
        analysis_session_id=payload.analysis_session_id,
        lab_history=lab_history,
        symptom_history=symptom_history,
        medical_history_data=med_history,
        consensus_resolution=payload.consensus_resolution,
        horizons_days=payload.horizons_days,
        disease_domain=payload.disease_domain,
        current_risk_percent=payload.current_risk_percent,
        epistemic_doubt_score=payload.epistemic_doubt_score,
    )

    repo = TrajectoryForecastRepository(db)
    repo.create(
        forecast_id=result.forecast_id,
        user_id=target_patient_id,
        analysis_session_id=payload.analysis_session_id,
        model_version=result.model_version,
        model_type=result.model_type,
        disease_domain=payload.disease_domain,
        overall_direction=result.overall_direction.value,
        current_risk_percent=result.current_risk_percent,
        epistemic_doubt_score=result.epistemic_doubt_score,
        forecast_payload=result.model_dump(mode="json"),
        input_evidence_refs=result.input_evidence_references,
        safety_warnings_preserved=result.preserved_safety_warnings,
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return TrajectoryForecastResponse(
        status="success",
        forecast=result,
        persisted=True,
        execution_time_ms=elapsed_ms,
    )


@router.get(
    "/history",
    response_model=List[DiseaseTrajectoryResult],
    summary="List historical disease trajectory forecasts for the authenticated patient",
)
def list_trajectory_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DiseaseTrajectoryResult]:
    """Retrieve historical trajectory forecasts scoped strictly to the authenticated user."""
    records = TrajectoryForecastRepository(db).list_by_user_id(current_user.id, limit=limit)
    return [DiseaseTrajectoryResult.model_validate(r.forecast_payload) for r in records]


@router.get(
    "/compare/{forecast_id_a}/{forecast_id_b}",
    response_model=TrajectoryComparisonResponse,
    summary="Compare two successive trajectory forecasts for the same patient",
)
def compare_trajectory_forecasts(
    forecast_id_a: str,
    forecast_id_b: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrajectoryComparisonResponse:
    """Compare two trajectory forecasts with strict tenant isolation."""
    repo = TrajectoryForecastRepository(db)
    rec_a = repo.get_by_id(forecast_id_a)
    rec_b = repo.get_by_id(forecast_id_b)
    if not rec_a or not rec_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both forecasts not found.")
    if rec_a.user_id != current_user.id or rec_b.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot access another user's forecast.")

    earlier, later = (rec_a, rec_b) if rec_a.created_at <= rec_b.created_at else (rec_b, rec_a)
    res_earlier = DiseaseTrajectoryResult.model_validate(earlier.forecast_payload)
    res_later = DiseaseTrajectoryResult.model_validate(later.forecast_payload)

    later_by_h = {h.horizon_days: h for h in res_later.horizons}
    deltas = []
    for h_e in res_earlier.horizons:
        h_l = later_by_h.get(h_e.horizon_days)
        if h_l and h_e.projected_risk_percent is not None and h_l.projected_risk_percent is not None:
            deltas.append({
                "horizon_days": h_e.horizon_days,
                "earlier_projected_risk": h_e.projected_risk_percent,
                "later_projected_risk": h_l.projected_risk_percent,
                "delta_risk_percent": round(h_l.projected_risk_percent - h_e.projected_risk_percent, 2),
            })

    shift = f"{res_earlier.overall_direction.value} -> {res_later.overall_direction.value}"
    return TrajectoryComparisonResponse(
        patient_id=current_user.id,
        earlier_forecast_id=earlier.id,
        later_forecast_id=later.id,
        earlier_generated_at=res_earlier.generated_at,
        later_generated_at=res_later.generated_at,
        direction_shift=shift,
        horizon_deltas=deltas,
        summary=f"Trajectory shifted ({shift}) across {len(deltas)} matching horizon(s).",
    )


@router.get(
    "/{forecast_id}",
    response_model=DiseaseTrajectoryResult,
    summary="Retrieve a specific persisted disease trajectory forecast",
)
def get_trajectory_forecast(
    forecast_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiseaseTrajectoryResult:
    """Retrieve a persisted forecast by ID with strict tenant verification."""
    rec = TrajectoryForecastRepository(db).get_by_id(forecast_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Forecast '{forecast_id}' not found.")
    if rec.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot access another user's forecast.")
    return DiseaseTrajectoryResult.model_validate(rec.forecast_payload)


@router.post(
    "/{forecast_id}/observations",
    response_model=TrajectoryObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record an actual subsequent clinical observation for future forecast evaluation",
)
def record_trajectory_observation(
    forecast_id: str,
    payload: TrajectoryObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrajectoryObservationResponse:
    """Record ground-truth observation against a previously generated forecast."""
    repo = TrajectoryForecastRepository(db)
    rec = repo.get_by_id(forecast_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Forecast '{forecast_id}' not found.")
    if rec.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot attach observation to another user's forecast.")

    obs = repo.record_observation(
        forecast_id=forecast_id,
        user_id=current_user.id,
        actual_outcome_label=payload.actual_outcome_label,
        observed_risk_percent=payload.observed_risk_percent,
        observed_biomarkers=payload.observed_biomarkers,
        notes=payload.notes,
        observed_at=payload.observed_at,
    )
    return TrajectoryObservationResponse(
        id=obs.id,
        forecast_id=obs.forecast_id,
        user_id=obs.user_id,
        observed_at=obs.observed_at.isoformat(),
        actual_outcome_label=obs.actual_outcome_label,
        observed_risk_percent=obs.observed_risk_percent,
        observed_biomarkers=obs.observed_biomarkers or {},
        notes=obs.notes,
        created_at=obs.created_at.isoformat(),
    )
