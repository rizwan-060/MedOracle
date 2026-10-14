"""MedOracle Pydantic v2 schemas package."""

from app.schemas.auth import (
    RefreshTokenRequest,
    Token,
    TokenPayload,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.schemas.patient import (
    MedicalHistoryCreate,
    MedicalHistoryResponse,
    MedicalHistoryUpdate,
    PatientProfileCreate,
    PatientProfileResponse,
    PatientProfileUpdate,
)
from app.schemas.symptoms import SymptomReportCreate, SymptomReportResponse
from app.schemas.laboratory import LabResultCreate, LabResultResponse
from app.schemas.risk import (
    CkdEpiRequest,
    FindriscRequest,
    FraminghamRiskRequest,
    RiskCalculationResponse,
    RiskResultResponse,
)
from app.schemas.analysis import (
    AgentOutputResponse,
    AnalysisSessionResponse,
    AnalysisSessionStatusResponse,
    AnalysisStartRequest,
    ConsensusVerdictSchema,
    GraphEdge,
    GraphNode,
    ReasoningGraphSchema,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorRecommendationResponse,
    DoctorResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "PatientProfileCreate",
    "PatientProfileUpdate",
    "PatientProfileResponse",
    "MedicalHistoryCreate",
    "MedicalHistoryUpdate",
    "MedicalHistoryResponse",
    "SymptomReportCreate",
    "SymptomReportResponse",
    "LabResultCreate",
    "LabResultResponse",
    "FraminghamRiskRequest",
    "FindriscRequest",
    "CkdEpiRequest",
    "RiskCalculationResponse",
    "RiskResultResponse",
    "AgentOutputResponse",
    "ConsensusVerdictSchema",
    "GraphNode",
    "GraphEdge",
    "ReasoningGraphSchema",
    "AnalysisStartRequest",
    "AnalysisSessionStatusResponse",
    "AnalysisSessionResponse",
    "DoctorCreate",
    "DoctorResponse",
    "DoctorRecommendationResponse",
]
