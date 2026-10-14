"""SQLAlchemy 2.0 ORM models for MedOracle.

Defines all relational data entities:
- Users (authentication & identity)
- PatientProfiles (demographics & biometric measurements)
- MedicalHistories (chronic conditions, medications, family history)
- SymptomReports (patient-reported symptoms & severity)
- LabResults (biomarkers, test values, panel dates)
- AnalysisSessions (multi-agent analysis orchestration lifecycle)
- AgentOutputs (structured findings and confidence from individual agents)
- RiskResults (calculated quantitative risk scores & stratifications)
- Doctors (specialty referral directory)
- TrainedModels (serialized ML model registry entries)
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


def generate_uuid() -> str:
    """Generate a RFC 4122 v4 UUID string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account model for authentication and data tenancy."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    patient_profile = relationship(
        "PatientProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    medical_histories = relationship(
        "MedicalHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    symptom_reports = relationship(
        "SymptomReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lab_results = relationship(
        "LabResult",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    analysis_sessions = relationship(
        "AnalysisSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    risk_results = relationship(
        "RiskResult",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PatientProfile(Base):
    """Demographics, physical measurements, and baseline health profile."""

    __tablename__ = "patient_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # "male", "female", "other"
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    waist_circumference_cm = Column(Float, nullable=True)
    smoking_status = Column(String(30), nullable=True)  # "never", "former", "current_smoker"
    activity_level = Column(String(30), nullable=True)  # "sedentary", "low", "moderate", "high"
    blood_group = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="patient_profile")


class MedicalHistory(Base):
    """Longitudinal personal medical conditions, surgeries, medications, and hereditary risk."""

    __tablename__ = "medical_histories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chronic_conditions = Column(JSON, default=list, nullable=False)
    past_surgeries = Column(JSON, default=list, nullable=False)
    current_medications = Column(JSON, default=list, nullable=False)
    allergies = Column(JSON, default=list, nullable=False)
    family_history = Column(JSON, default=list, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="medical_histories")


class SymptomReport(Base):
    """Patient-reported symptoms, perceived severity, and contextual annotations."""

    __tablename__ = "symptom_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reported_text = Column(Text, nullable=False)
    duration_days = Column(Integer, nullable=True)
    severity_self_rating = Column(Integer, nullable=True)  # 1 to 10 scale
    body_locations = Column(JSON, default=list, nullable=False)
    triggers = Column(JSON, default=list, nullable=False)
    structured_symptoms = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="symptom_reports")


class LabResult(Base):
    """Biomarkers, metabolic panel values, and clinical laboratory metrics."""

    __tablename__ = "lab_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_date = Column(Date, nullable=False)
    lab_name = Column(String(255), nullable=True)
    biomarkers = Column(JSON, nullable=False)  # Map of biomarker name -> numeric/text value
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="lab_results")


class AnalysisSession(Base):
    """Orchestration session for the multi-agent pipeline and consensus debate."""

    __tablename__ = "analysis_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    symptom_report_id = Column(
        String(36), ForeignKey("symptom_reports.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status = Column(
        String(30), default="pending", nullable=False, index=True
    )  # "pending", "running", "completed", "failed"
    current_phase = Column(
        String(50), default="queued", nullable=False
    )  # "queued", "agent_analysis", "risk_calculation", "consensus_debate", "completed", "failed"
    progress_percent = Column(Integer, default=0, nullable=False)

    # Multi-agent results
    consensus_verdict = Column(JSON, nullable=True)
    debate_summary = Column(JSON, nullable=True)
    disease_trajectory = Column(JSON, nullable=True)
    counterfactuals = Column(JSON, nullable=True)
    reasoning_graph = Column(JSON, nullable=True)
    recommended_specialty = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="analysis_sessions")
    symptom_report = relationship("SymptomReport")
    agent_outputs = relationship(
        "AgentOutput",
        back_populates="analysis_session",
        cascade="all, delete-orphan",
    )
    risk_results = relationship(
        "RiskResult",
        back_populates="analysis_session",
        cascade="all, delete-orphan",
    )


class AgentOutput(Base):
    """Structured output record from an individual specialized agent in a session."""

    __tablename__ = "agent_outputs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_session_id = Column(
        String(36), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_role = Column(
        String(50), nullable=False, index=True
    )  # "symptom_agent", "medical_history_agent", "laboratory_agent", "risk_prediction_agent", "consensus_agent"
    findings = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 to 100.0
    reasoning_chain = Column(JSON, default=list, nullable=False)
    evidence = Column(JSON, default=list, nullable=False)
    challenges = Column(JSON, default=list, nullable=False)
    metadata_payload = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    analysis_session = relationship("AnalysisSession", back_populates="agent_outputs")


class RiskResult(Base):
    """Quantitative risk calculations computed by clinical equations or ML models."""

    __tablename__ = "risk_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_session_id = Column(
        String(36), ForeignKey("analysis_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_name = Column(String(100), nullable=False)
    model_type = Column(
        String(30), nullable=False
    )  # "clinical_formula", "machine_learning", "ensemble"
    risk_score = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)  # "low", "moderate", "high", "very_high"
    horizon = Column(String(30), nullable=True)  # "10_year", "30_day", "6_month", "1_year"
    input_parameters = Column(JSON, nullable=False)
    missing_or_assumed = Column(JSON, default=list, nullable=False)
    disclaimer = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="risk_results")
    user = relationship("User", back_populates="risk_results")


class Doctor(Base):
    """Doctor and clinic directory for clinical second opinion recommendations."""

    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    specialty = Column(String(100), nullable=False, index=True)
    sub_specialty = Column(String(100), nullable=True)
    hospital_clinic = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    area = Column(String(150), nullable=False)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, default=5.0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class TrainedModel(Base):
    """Model registry cataloging trained machine learning model artifacts."""

    __tablename__ = "trained_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(30), nullable=False)
    target_disease = Column(String(100), nullable=False)
    algorithm = Column(String(100), nullable=False)
    dataset_source = Column(String(100), nullable=False)
    artifact_path = Column(String(255), nullable=False)
    metrics = Column(JSON, nullable=False)
    feature_names = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
