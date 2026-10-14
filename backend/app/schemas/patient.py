"""Patient profile and longitudinal medical history Pydantic v2 schemas."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PatientProfileBase(BaseModel):
    """Base biometric and demographic parameters."""

    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    height_cm: Optional[float] = Field(None, ge=40.0, le=250.0)
    weight_kg: Optional[float] = Field(None, ge=2.0, le=350.0)
    waist_circumference_cm: Optional[float] = Field(None, ge=30.0, le=200.0)
    smoking_status: Optional[str] = Field(None, pattern="^(never|former|current_smoker)$")
    activity_level: Optional[str] = Field(None, pattern="^(sedentary|low|moderate|high)$")
    blood_group: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")


class PatientProfileCreate(PatientProfileBase):
    """Profile creation schema."""

    pass


class PatientProfileUpdate(PatientProfileBase):
    """Profile update schema (all fields optional)."""

    pass


class PatientProfileResponse(PatientProfileBase):
    """Profile response schema."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FamilyHistoryItem(BaseModel):
    """Structured family history item."""

    relative: str = Field(..., description="e.g. father, mother, sibling")
    condition: str = Field(..., description="e.g. myocardial_infarction, type_2_diabetes")
    age_at_onset: Optional[int] = Field(None, ge=0, le=120)


class MedicationItem(BaseModel):
    """Current medication record."""

    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None


class MedicalHistoryBase(BaseModel):
    """Base medical and family history attributes."""

    chronic_conditions: List[str] = Field(default_factory=list)
    past_surgeries: List[str] = Field(default_factory=list)
    current_medications: List[Dict[str, Any]] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    family_history: List[Dict[str, Any]] = Field(default_factory=list)
    notes: Optional[str] = None


class MedicalHistoryCreate(MedicalHistoryBase):
    """Create medical history schema."""

    pass


class MedicalHistoryUpdate(MedicalHistoryBase):
    """Update medical history schema."""

    pass


class MedicalHistoryResponse(MedicalHistoryBase):
    """Response medical history schema."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
