"""Pydantic v2 schemas for Disease Trajectory Forecasting."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TrajectoryDirection(str, Enum):
    """Direction of predicted disease or biomarker trajectory."""

    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"
    INSUFFICIENT_DATA = "insufficient_data"


class BiomarkerTrendSummary(BaseModel):
    """Temporal feature summary for a single clinical biomarker without false interpolation."""

    biomarker_name: str
    unit: Optional[str] = None
    observation_count: int = Field(..., ge=0)
    latest_value: Optional[float] = None
    previous_value: Optional[float] = None
    latest_timestamp: Optional[str] = None
    time_since_previous_days: Optional[float] = None
    observation_span_days: float = 0.0
    sampling_frequency_per_30d: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    rate_of_change_per_30d: Optional[float] = None
    moving_average_3: Optional[float] = None
    variability_std: Optional[float] = None
    abnormal_value_duration_days: float = 0.0
    is_missing: bool = False
    insufficient_history: bool = False
    trend_direction: TrajectoryDirection = TrajectoryDirection.INSUFFICIENT_DATA
    source_record_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class LongitudinalFeatureVector(BaseModel):
    """Extracted longitudinal feature representation preserving provenance and missingness."""

    patient_id: Optional[str] = None
    extracted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_lab_visits: int = 0
    total_symptom_reports: int = 0
    observation_window_days: float = 0.0
    missingness_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    biomarker_trends: Dict[str, BiomarkerTrendSummary] = Field(default_factory=dict)
    symptom_severity_latest: Optional[float] = None
    symptom_severity_slope_per_30d: Optional[float] = None
    medication_count: int = 0
    adherence_inconsistent: bool = False
    source_record_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class HorizonProjection(BaseModel):
    """Projected risk and uncertainty bounds for a specific future time horizon."""

    horizon_days: int = Field(..., gt=0)
    horizon_label: str
    projected_risk_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    uncertainty_lower_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    uncertainty_upper_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    confidence_level: float = Field(default=0.0, ge=0.0, le=100.0)
    is_calibrated_probability: bool = False
    direction: TrajectoryDirection = TrajectoryDirection.INSUFFICIENT_DATA
    status_label: str = "insufficient_data"
    key_drivers: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DiseaseTrajectoryResult(BaseModel):
    """Complete output of the Disease Trajectory Forecasting Engine."""

    forecast_id: str
    patient_id: Optional[str] = None
    analysis_session_id: Optional[str] = None
    model_version: str
    model_type: str
    is_clinically_validated: bool = False
    current_risk_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    overall_direction: TrajectoryDirection = TrajectoryDirection.INSUFFICIENT_DATA
    horizons: List[HorizonProjection] = Field(default_factory=list)
    epistemic_doubt_score: float = Field(default=0.0, ge=0.0, le=1.0)
    unresolved_contradiction_count: int = 0
    preserved_safety_warnings: List[Dict[str, Any]] = Field(default_factory=list)
    longitudinal_summary: LongitudinalFeatureVector
    input_evidence_references: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    decision_support_disclaimer: str = (
        "MedOracle Disease Trajectory Forecasting provides investigational decision support only. "
        "A predicted trajectory is a statistical/rule-based projection and is NOT an established clinical diagnosis."
    )
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = ConfigDict(from_attributes=True)


class TrajectoryForecastRequest(BaseModel):
    """Request payload for generating a disease trajectory forecast."""

    patient_id: Optional[str] = None
    analysis_session_id: Optional[str] = None
    horizons_days: List[int] = Field(default_factory=lambda: [30, 180, 365])
    disease_domain: str = Field(default="cardiovascular", description="Target domain: 'cardiovascular', 'diabetes', or 'general'.")
    current_risk_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    lab_history: Optional[List[Dict[str, Any]]] = None
    symptom_history: Optional[List[Dict[str, Any]]] = None
    medical_history_data: Optional[Dict[str, Any]] = None
    consensus_resolution: Optional[Dict[str, Any]] = None
    epistemic_doubt_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class TrajectoryForecastResponse(BaseModel):
    """API response wrapper for trajectory forecast generation."""

    status: str = "success"
    forecast: DiseaseTrajectoryResult
    persisted: bool = False
    execution_time_ms: float = 0.0


class TrajectoryComparisonResponse(BaseModel):
    """Comparison between two successive trajectory forecasts for the same patient."""

    patient_id: str
    earlier_forecast_id: str
    later_forecast_id: str
    earlier_generated_at: str
    later_generated_at: str
    direction_shift: str
    horizon_deltas: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str


class TrajectoryObservationCreate(BaseModel):
    """Record an actual subsequent clinical observation for future forecast evaluation."""

    observed_at: Optional[datetime] = None
    actual_outcome_label: Optional[int] = Field(default=None, ge=0, le=1)
    observed_risk_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    observed_biomarkers: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class TrajectoryObservationResponse(BaseModel):
    """Persisted subsequent observation linked to a trajectory forecast."""

    id: str
    forecast_id: str
    user_id: str
    observed_at: str
    actual_outcome_label: Optional[int] = None
    observed_risk_percent: Optional[float] = None
    observed_biomarkers: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
