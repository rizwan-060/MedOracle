"""Clinical and machine learning risk calculation Pydantic v2 schemas."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_DISCLAIMER = (
    "MedOracle is a decision-support assistant and does not provide "
    "clinical diagnosis. Consult a qualified healthcare professional."
)


class FraminghamRiskRequest(BaseModel):
    """Input parameters for Framingham 10-year general CVD risk calculation."""

    age: int = Field(..., ge=20, le=100, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex ('male' or 'female')")
    total_cholesterol_mg_dl: float = Field(..., ge=50.0, le=600.0, description="Total cholesterol (mg/dL)")
    hdl_cholesterol_mg_dl: float = Field(..., ge=10.0, le=150.0, description="HDL cholesterol (mg/dL)")
    systolic_bp: float = Field(..., ge=60.0, le=260.0, description="Systolic BP (mmHg)")
    is_treated_for_hypertension: bool = Field(False, description="Treated with antihypertensive medication")
    is_smoker: bool = Field(False, description="Current cigarette smoker")
    has_diabetes: bool = Field(False, description="Diagnosis of diabetes mellitus")


class FraminghamRiskResponse(BaseModel):
    """Output schema for Framingham 10-year CVD risk calculation."""

    model: str
    risk_score_percent: float = Field(..., description="10-year probability of CVD in percent")
    risk_category: Literal["low", "moderate", "high"]
    missing_or_assumed: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any]
    disclaimer: str = DEFAULT_DISCLAIMER


class FindriscRequest(BaseModel):
    """Input parameters for FINDRISC 10-year type 2 diabetes risk calculation."""

    age: int = Field(..., ge=18, le=110, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex ('male' or 'female')")
    bmi: Optional[float] = Field(None, ge=10.0, le=80.0, description="BMI in kg/m2 (optional if height/weight provided)")
    height_cm: Optional[float] = Field(None, ge=40.0, le=250.0, description="Height in cm")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=350.0, description="Weight in kg")
    waist_circumference_cm: Optional[float] = Field(None, ge=30.0, le=200.0, description="Waist circumference in cm")
    daily_physical_activity_30min: bool = Field(True, description=">= 30 mins physical activity daily")
    daily_vegetable_fruit_intake: bool = Field(True, description="Eats vegetables/fruits daily")
    takes_antihypertensive_meds: bool = Field(False, description="Regular antihypertensive medications")
    history_of_high_blood_glucose: bool = Field(False, description="Past high blood glucose readings")
    family_history_of_diabetes: Literal["none", "second_degree", "first_degree"] = Field(
        "none", description="Family history tier"
    )


class FindriscResponse(BaseModel):
    """Output schema for FINDRISC diabetes score."""

    model: str
    total_score: int = Field(..., ge=0, le=26, description="Total score out of 26")
    max_score: int = 26
    risk_category: Literal["low", "slightly_elevated", "moderate", "high", "very_high"]
    ten_year_risk_percent_approx: float = Field(..., description="Approximate 10-year probability percentage")
    missing_or_assumed: List[str] = Field(default_factory=list)
    points_breakdown: Dict[str, int]
    parameters: Dict[str, Any]
    disclaimer: str = DEFAULT_DISCLAIMER


class CkdEpiRequest(BaseModel):
    """Input parameters for CKD-EPI 2021 creatinine eGFR calculation."""

    serum_creatinine_mg_dl: float = Field(..., ge=0.1, le=25.0, description="Serum creatinine (mg/dL)")
    age: int = Field(..., ge=18, le=120, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex ('male' or 'female')")


class CkdEpiResponse(BaseModel):
    """Output schema for CKD-EPI 2021 eGFR calculation."""

    model: str
    egfr_ml_min_1_73m2: float = Field(..., description="eGFR in mL/min/1.73m2")
    kdigo_stage: Literal["G1", "G2", "G3a", "G3b", "G4", "G5"]
    stage_description: str
    clinical_severity: Literal["normal", "mild", "moderate", "substantial", "severe", "critical"]
    parameters: Dict[str, Any]
    disclaimer: str = DEFAULT_DISCLAIMER


class RiskCalculationResponse(BaseModel):
    """Output schema for pure clinical formula calculation."""

    model_name: str
    risk_score: float
    risk_category: str  # "low", "moderate", "high", "very_high"
    horizon: Optional[str] = None
    missing_or_assumed: List[str] = Field(default_factory=list)
    disclaimer: str = DEFAULT_DISCLAIMER


class RiskResultResponse(BaseModel):
    """Saved risk result record schema for database repository."""

    id: str
    analysis_session_id: Optional[str] = None
    user_id: str
    model_name: str
    model_type: str
    risk_score: float
    risk_category: str
    horizon: Optional[str] = None
    input_parameters: Dict[str, Any]
    missing_or_assumed: List[str] = Field(default_factory=list)
    disclaimer: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
