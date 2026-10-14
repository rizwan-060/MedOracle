"""Symptom reporting Pydantic v2 schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SymptomReportBase(BaseModel):
    """Base symptom report schema."""

    reported_text: str = Field(..., min_length=5, max_length=5000)
    duration_days: Optional[int] = Field(None, ge=0, le=3650)
    severity_self_rating: Optional[int] = Field(None, ge=1, le=10)
    body_locations: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    structured_symptoms: List[str] = Field(default_factory=list)


class SymptomReportCreate(SymptomReportBase):
    """Schema for creating a symptom report."""

    pass


class SymptomReportResponse(SymptomReportBase):
    """Schema for returning a symptom report."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
