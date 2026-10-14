"""Laboratory test results and biomarker Pydantic v2 schemas."""

from datetime import date, datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class BiomarkerValues(BaseModel):
    """Commonly referenced metabolic and clinical biomarkers."""

    systolic_bp: Optional[float] = Field(None, ge=50, le=280, description="mmHg")
    diastolic_bp: Optional[float] = Field(None, ge=30, le=180, description="mmHg")
    total_cholesterol_mg_dl: Optional[float] = Field(None, ge=50, le=600, description="mg/dL")
    hdl_cholesterol_mg_dl: Optional[float] = Field(None, ge=10, le=150, description="mg/dL")
    ldl_cholesterol_mg_dl: Optional[float] = Field(None, ge=20, le=400, description="mg/dL")
    triglycerides_mg_dl: Optional[float] = Field(None, ge=20, le=1500, description="mg/dL")
    fasting_blood_glucose_mg_dl: Optional[float] = Field(None, ge=30, le=600, description="mg/dL")
    hba1c_percent: Optional[float] = Field(None, ge=3.0, le=20.0, description="%")
    serum_creatinine_mg_dl: Optional[float] = Field(None, ge=0.1, le=25.0, description="mg/dL")
    estimated_gfr: Optional[float] = Field(None, ge=1.0, le=200.0, description="mL/min/1.73m2")


class LabResultBase(BaseModel):
    """Base laboratory record schema."""

    test_date: date
    lab_name: Optional[str] = Field(None, max_length=255)
    biomarkers: Dict[str, Any] = Field(
        ..., description="Biomarker key-value mapping (e.g. cholesterol, creatinine)"
    )
    notes: Optional[str] = None


class LabResultCreate(LabResultBase):
    """Create lab result schema."""

    pass


class LabResultResponse(LabResultBase):
    """Response lab result schema."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
