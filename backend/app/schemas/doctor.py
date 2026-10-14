"""Doctor directory and recommendation Pydantic v2 schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DoctorBase(BaseModel):
    """Base doctor information schema."""

    name: str = Field(..., max_length=255)
    specialty: str = Field(..., max_length=100)
    sub_specialty: Optional[str] = Field(None, max_length=100)
    hospital_clinic: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    area: str = Field(..., max_length=150)
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: float = Field(5.0, ge=0.0, le=5.0)
    is_available: bool = True


class DoctorCreate(DoctorBase):
    """Schema for creating a doctor directory entry."""

    pass


class DoctorResponse(DoctorBase):
    """Response schema for doctor profile."""

    id: str
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorRecommendationResponse(BaseModel):
    """Doctor recommendations matched to consensus verdict."""

    specialty: str
    urgency: str
    recommended_doctors: List[DoctorResponse]
    disclaimer: str = (
        "Doctor recommendations are provided for second opinion referral and decision support."
    )
