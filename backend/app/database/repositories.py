"""Database repository implementations for MedOracle.

Encapsulates all database persistence operations using SQLAlchemy 2.0 select/insert/update
constructs, strictly preventing raw SQL string concatenation.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database.models import (
    AgentOutput,
    AnalysisSession,
    Doctor,
    LabResult,
    MedicalHistory,
    PatientProfile,
    RiskResult,
    SymptomReport,
    TrainedModel,
    User,
)


class UserRepository:
    """Data access repository for User accounts."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower())
        return self.db.scalars(stmt).first()

    def create(self, email: str, hashed_password: str, full_name: str) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class PatientProfileRepository:
    """Data access repository for patient demographic and biometric profiles."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> Optional[PatientProfile]:
        stmt = select(PatientProfile).where(PatientProfile.user_id == user_id)
        return self.db.scalars(stmt).first()

    def create_or_update(self, user_id: str, **kwargs) -> PatientProfile:
        profile = self.get_by_user_id(user_id)
        if not profile:
            profile = PatientProfile(user_id=user_id, **kwargs)
            self.db.add(profile)
        else:
            for key, val in kwargs.items():
                if val is not None and hasattr(profile, key):
                    setattr(profile, key, val)
        self.db.commit()
        self.db.refresh(profile)
        return profile


class MedicalHistoryRepository:
    """Data access repository for personal medical conditions, surgeries, and family history."""

    def __init__(self, db: Session):
        self.db = db

    def get_latest_by_user_id(self, user_id: str) -> Optional[MedicalHistory]:
        stmt = (
            select(MedicalHistory)
            .where(MedicalHistory.user_id == user_id)
            .order_by(MedicalHistory.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def create(self, user_id: str, **kwargs) -> MedicalHistory:
        history = MedicalHistory(user_id=user_id, **kwargs)
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def update(self, history_id: str, user_id: str, **kwargs) -> Optional[MedicalHistory]:
        stmt = select(MedicalHistory).where(
            MedicalHistory.id == history_id, MedicalHistory.user_id == user_id
        )
        history = self.db.scalars(stmt).first()
        if not history:
            return None
        for key, val in kwargs.items():
            if val is not None and hasattr(history, key):
                setattr(history, key, val)
        self.db.commit()
        self.db.refresh(history)
        return history

    def create_or_update(self, user_id: str, **kwargs) -> MedicalHistory:
        history = self.get_latest_by_user_id(user_id)
        if not history:
            history = MedicalHistory(user_id=user_id, **kwargs)
            self.db.add(history)
        else:
            for key, val in kwargs.items():
                if val is not None and hasattr(history, key):
                    setattr(history, key, val)
        self.db.commit()
        self.db.refresh(history)
        return history


class SymptomReportRepository:
    """Data access repository for patient symptom reporting."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, report_id: str, user_id: Optional[str] = None) -> Optional[SymptomReport]:
        stmt = select(SymptomReport).where(SymptomReport.id == report_id)
        if user_id:
            stmt = stmt.where(SymptomReport.user_id == user_id)
        return self.db.scalars(stmt).first()

    def list_by_user_id(self, user_id: str, limit: int = 50) -> List[SymptomReport]:
        stmt = (
            select(SymptomReport)
            .where(SymptomReport.user_id == user_id)
            .order_by(SymptomReport.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, user_id: str, reported_text: str, **kwargs) -> SymptomReport:
        report = SymptomReport(user_id=user_id, reported_text=reported_text, **kwargs)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report_id: str, user_id: str) -> bool:
        report = self.get_by_id(report_id, user_id=user_id)
        if not report:
            return False
        self.db.delete(report)
        self.db.commit()
        return True


class LabResultRepository:
    """Data access repository for clinical laboratory test results."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, lab_id: str, user_id: Optional[str] = None) -> Optional[LabResult]:
        stmt = select(LabResult).where(LabResult.id == lab_id)
        if user_id:
            stmt = stmt.where(LabResult.user_id == user_id)
        return self.db.scalars(stmt).first()

    def get_latest_by_user_id(self, user_id: str) -> Optional[LabResult]:
        stmt = (
            select(LabResult)
            .where(LabResult.user_id == user_id)
            .order_by(LabResult.test_date.desc(), LabResult.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def list_by_user_id(self, user_id: str, limit: int = 50) -> List[LabResult]:
        stmt = (
            select(LabResult)
            .where(LabResult.user_id == user_id)
            .order_by(LabResult.test_date.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, user_id: str, **kwargs) -> LabResult:
        lab = LabResult(user_id=user_id, **kwargs)
        self.db.add(lab)
        self.db.commit()
        self.db.refresh(lab)
        return lab

    def delete(self, lab_id: str, user_id: str) -> bool:
        lab = self.get_by_id(lab_id, user_id=user_id)
        if not lab:
            return False
        self.db.delete(lab)
        self.db.commit()
        return True


class AnalysisSessionRepository:
    """Data access repository for multi-agent analysis sessions."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, session_id: str, user_id: Optional[str] = None) -> Optional[AnalysisSession]:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        if user_id:
            stmt = stmt.where(AnalysisSession.user_id == user_id)
        return self.db.scalars(stmt).first()

    def list_by_user_id(self, user_id: str, limit: int = 20) -> List[AnalysisSession]:
        stmt = (
            select(AnalysisSession)
            .where(AnalysisSession.user_id == user_id)
            .order_by(AnalysisSession.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, user_id: str, symptom_report_id: Optional[str] = None) -> AnalysisSession:
        session = AnalysisSession(
            user_id=user_id,
            symptom_report_id=symptom_report_id,
            status="pending",
            current_phase="queued",
            progress_percent=0,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_status(
        self,
        session_id: str,
        status: str,
        current_phase: str,
        progress_percent: int,
        error_message: Optional[str] = None,
    ) -> Optional[AnalysisSession]:
        session = self.get_by_id(session_id)
        if not session:
            return None
        session.status = status
        session.current_phase = current_phase
        session.progress_percent = progress_percent
        if error_message:
            session.error_message = error_message
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_results(self, session_id: str, **kwargs) -> Optional[AnalysisSession]:
        session = self.get_by_id(session_id)
        if not session:
            return None
        for key, val in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, val)
        self.db.commit()
        self.db.refresh(session)
        return session


class AgentOutputRepository:
    """Data access repository for individual agent output logs."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        analysis_session_id: str,
        agent_role: str,
        findings: str,
        confidence: float,
        reasoning_chain: List[str],
        evidence: List[str],
        challenges: Optional[List[str]] = None,
        metadata_payload: Optional[Dict[str, Any]] = None,
    ) -> AgentOutput:
        output = AgentOutput(
            analysis_session_id=analysis_session_id,
            agent_role=agent_role,
            findings=findings,
            confidence=confidence,
            reasoning_chain=reasoning_chain or [],
            evidence=evidence or [],
            challenges=challenges or [],
            metadata_payload=metadata_payload or {},
        )
        self.db.add(output)
        self.db.commit()
        self.db.refresh(output)
        return output

    def list_by_session_id(self, analysis_session_id: str) -> List[AgentOutput]:
        stmt = (
            select(AgentOutput)
            .where(AgentOutput.analysis_session_id == analysis_session_id)
            .order_by(AgentOutput.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())


class RiskResultRepository:
    """Data access repository for quantitative clinical & ML risk scores."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str,
        model_name: str,
        model_type: str,
        risk_score: float,
        risk_category: str,
        input_parameters: Dict[str, Any],
        disclaimer: str,
        analysis_session_id: Optional[str] = None,
        horizon: Optional[str] = None,
        missing_or_assumed: Optional[List[str]] = None,
    ) -> RiskResult:
        result = RiskResult(
            user_id=user_id,
            analysis_session_id=analysis_session_id,
            model_name=model_name,
            model_type=model_type,
            risk_score=risk_score,
            risk_category=risk_category,
            horizon=horizon,
            input_parameters=input_parameters,
            missing_or_assumed=missing_or_assumed or [],
            disclaimer=disclaimer,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def list_by_user_id(self, user_id: str, limit: int = 50) -> List[RiskResult]:
        stmt = (
            select(RiskResult)
            .where(RiskResult.user_id == user_id)
            .order_by(RiskResult.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())


class DoctorRepository:
    """Data access repository for the doctor and specialist referral directory."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doctor_id: str) -> Optional[Doctor]:
        stmt = select(Doctor).where(Doctor.id == doctor_id)
        return self.db.scalars(stmt).first()

    def search_by_specialty(
        self, specialty: str, city: Optional[str] = None, limit: int = 10
    ) -> List[Doctor]:
        stmt = select(Doctor).where(Doctor.is_available.is_(True))
        if specialty:
            stmt = stmt.where(Doctor.specialty.ilike(f"%{specialty}%"))
        if city:
            stmt = stmt.where(Doctor.city.ilike(f"%{city}%"))
        stmt = stmt.order_by(Doctor.rating.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs) -> Doctor:
        doctor = Doctor(**kwargs)
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor


class TrainedModelRepository:
    """Data access repository for the trained ML model registry."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_by_name(self, name: str) -> Optional[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .where(TrainedModel.name == name, TrainedModel.is_active.is_(True))
            .order_by(TrainedModel.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def list_active(self) -> List[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .where(TrainedModel.is_active.is_(True))
            .order_by(TrainedModel.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def register_model(self, **kwargs) -> TrainedModel:
        model = TrainedModel(**kwargs)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
