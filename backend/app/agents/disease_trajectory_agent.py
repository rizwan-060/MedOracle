"""Disease Trajectory Agent for MedOracle multi-agent pipeline.

Consumes validated Step 12 consensus outputs and longitudinal patient records
to project future clinical trajectories without overriding safety alerts or
fabricating missing clinical history.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ml.forecasting.longitudinal import LongitudinalFeatureExtractor
from app.ml.forecasting.trajectory import ClinicalTrendForecaster
from app.schemas.trajectory import DiseaseTrajectoryResult

logger = logging.getLogger("agents.disease_trajectory")


class DiseaseTrajectoryAgent:
    """Agent orchestrating longitudinal feature extraction and trajectory projection."""

    agent_role: str = "Disease Trajectory Forecaster"

    def __init__(self) -> None:
        self.extractor = LongitudinalFeatureExtractor()
        self.forecaster = ClinicalTrendForecaster()

    def forecast_trajectory(
        self,
        patient_id: Optional[str] = None,
        analysis_session_id: Optional[str] = None,
        lab_history: Optional[List[Dict[str, Any]]] = None,
        symptom_history: Optional[List[Dict[str, Any]]] = None,
        current_labs: Optional[Dict[str, Any]] = None,
        current_symptoms: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        consensus_resolution: Optional[Dict[str, Any]] = None,
        horizons_days: Optional[List[int]] = None,
        disease_domain: str = "cardiovascular",
        current_risk_percent: Optional[float] = None,
        epistemic_doubt_score: Optional[float] = None,
    ) -> DiseaseTrajectoryResult:
        """Execute longitudinal extraction and trajectory projection."""
        combined_labs = list(lab_history or [])
        if current_labs:
            combined_labs.append({
                "id": f"current_{analysis_session_id or 'lab'}",
                "test_date": current_labs.get("test_date") or current_labs.get("timestamp") or "2026-11-25T00:00:00Z",
                "biomarkers": current_labs,
            })

        combined_symptoms = list(symptom_history or [])
        if current_symptoms and (current_symptoms.get("severity") is not None or current_symptoms.get("symptoms")):
            combined_symptoms.append({
                "id": f"current_{analysis_session_id or 'sym'}",
                "created_at": current_symptoms.get("timestamp") or "2026-11-25T00:00:00Z",
                "severity": current_symptoms.get("severity"),
            })

        features = self.extractor.extract(
            lab_history=combined_labs,
            symptom_history=combined_symptoms,
            medical_history=medical_history_data,
            patient_id=patient_id,
        )

        # Determine baseline current risk from Step 11 scores / ML if not explicitly provided
        baseline_risk = current_risk_percent
        if baseline_risk is None:
            scores = clinical_scores or {}
            ml = ml_predictions or {}
            if disease_domain == "diabetes":
                baseline_risk = scores.get("findrisc_risk_percent") or ml.get("diabetes_risk_percent")
            else:
                baseline_risk = scores.get("framingham_risk_percent") or ml.get("cardiovascular_risk_percent")

        result = self.forecaster.forecast(
            longitudinal_features=features,
            current_risk_percent=baseline_risk,
            horizons_days=horizons_days,
            disease_domain=disease_domain,
            consensus_resolution=consensus_resolution,
            epistemic_doubt_score=epistemic_doubt_score,
            analysis_session_id=analysis_session_id,
        )
        logger.info(
            "Trajectory forecast generated (id=%s, direction=%s, doubt=%.3f, warnings=%d)",
            result.forecast_id,
            result.overall_direction.value,
            result.epistemic_doubt_score,
            len(result.preserved_safety_warnings),
        )
        return result

