"""Clinical and machine learning risk calculation Pydantic v2 schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_DISCLAIMER = (
    "MedOracle is a clinical decision-support assistant and does not provide "
    "clinical diagnosis or replace professional medical consultation."
)


class FraminghamRiskRequest(BaseModel):
    """Input parameters for Framingham 10-year general CVD risk calculation."""

    age: int = Field(..., ge=20, le=79)
    gender: str = Field(..., pattern="^(male|female)$")
    total_cholesterol_mg_dl: float = Field(..., ge=100, le=450)
    hdl_cholesterol_mg_dl: float = Field(..., ge=10, le=130)
    systolic_bp: float = Field(..., ge=80, le=240)
    is_treated_for_hypertension: bool = False
    is_smoker: bool = False
    has_diabetes: bool = False


class FindriscRequest(BaseModel):
    """Input parameters for FINDRISC 10-year type 2 diabetes risk calculation."""

    age: int = Field(..., ge=18, le=100)
    bmi: float = Field(..., ge=10.0, le=70.0)
    waist_circumference_cm: float = Field(..., ge=40.0, le=180.0)
    gender: str = Field(..., pattern="^(male|female)$")
    daily_physical_activity_30min: bool
    daily_vegetable_fruit_intake: bool
    takes_antihypertensive_meds: bool
    history_of_high_blood_glucose: bool
    family_history_of_diabetes: str = Field(
        ..., pattern="^(none|second_degree|first_degree)$"
    )


class CkdEpiRequest(BaseModel):
    """Input parameters for CKD-EPI 2021 creatinine eGFR calculation."""

    serum_creatinine_mg_dl: float = Field(..., ge=0.1, le=20.0)
    age: int = Field(..., ge=18, le=120)
    gender: str = Field(..., pattern="^(male|female)$")


class RiskCalculationResponse(BaseModel):
    """Output schema for pure clinical formula calculation."""

    model_name: str
    risk_score: float
    risk_category: str  # "low", "moderate", "high", "very_high"
    horizon: Optional[str] = None
    missing_or_assumed: List[str] = Field(default_factory=list)
    disclaimer: str = DEFAULT_DISCLAIMER


class RiskResultResponse(BaseModel):
    """Saved risk result record schema."""

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
