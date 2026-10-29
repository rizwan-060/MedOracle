"""Analysis session, multi-agent debate, and reasoning graph Pydantic v2 schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AgentOutputResponse(BaseModel):
    """Structured output contract returned by an individual agent."""

    id: Optional[str] = None
    agent_role: str
    findings: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    reasoning_chain: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConsensusVerdictSchema(BaseModel):
    """Final consensus verdict reached by multi-agent debate protocol."""

    primary_risk_category: str
    overall_urgency: str  # "low", "moderate", "high", "immediate"
    consensus_confidence: float = Field(..., ge=0.0, le=100.0)
    summary: str


class GraphNode(BaseModel):
    """Reasoning graph node formatted for Flutter graphview."""

    id: str
    label: str
    type: str  # "symptom", "history", "lab", "risk", "consensus"
    confidence: Optional[float] = None


class GraphEdge(BaseModel):
    """Reasoning graph directed connection."""

    source: str
    target: str
    weight: Optional[float] = None
    label: Optional[str] = None


class ReasoningGraphSchema(BaseModel):
    """Complete reasoning graph with nodes and directed edges."""

    nodes: List[GraphNode]
    edges: List[GraphEdge]


class AnalysisStartRequest(BaseModel):
    """Request payload to initiate a multi-agent analysis session."""

    symptom_report_id: Optional[str] = None
    include_latest_labs: bool = True
    include_medical_history: bool = True


class SymptomAgentTestRequest(BaseModel):
    """Request payload for standalone testing of the Symptom Specialist Agent."""

    symptoms: List[str] = Field(
        default=["chest_pain", "breathlessness", "sweating"],
        description="List of active canonical symptoms.",
    )
    severity: int = Field(default=8, ge=1, le=10, description="Severity on 1-10 scale.")
    duration_days: int = Field(default=2, ge=0, description="Duration of symptoms in days.")
    notes: Optional[str] = Field(
        default="Substernal pressure worsening on mild exertion, patient denies cough or fever.",
        description="Patient clinical narrative or physician notes.",
    )
    age: Optional[int] = Field(default=56, description="Patient age.")
    sex: Optional[str] = Field(default="male", description="Biological sex ('male' or 'female').")
    provider: Optional[str] = Field(default=None, description="Optional LLM provider ('mock', 'groq', 'gemini').")
    use_cache: bool = Field(default=True, description="Enable response caching.")


class MedicalHistoryAgentTestRequest(BaseModel):
    """Request payload for standalone testing of the Medical History Specialist Agent."""

    chronic_conditions: List[str] = Field(
        default=["hypertension", "type_2_diabetes", "hyperlipidemia"],
        description="Diagnosed pre-existing chronic conditions.",
    )
    current_medications: List[Dict[str, Any]] = Field(
        default=[
            {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily"},
            {"name": "Atorvastatin", "dosage": "20mg", "frequency": "once daily at bedtime"},
        ],
        description="Current prescriptions with dosages.",
    )
    family_history: List[Dict[str, Any]] = Field(
        default=[
            {"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 52},
            {"relative": "mother", "condition": "type_2_diabetes", "age_at_onset": 60},
        ],
        description="Family pedigree records with condition and age at onset.",
    )
    past_surgeries: List[str] = Field(
        default=["appendectomy (2012)"],
        description="Past surgical history.",
    )
    allergies: List[str] = Field(
        default=["penicillin"],
        description="Known drug and environmental allergies.",
    )
    smoking_status: Optional[str] = Field(
        default="current_smoker",
        description="Smoking history ('never', 'former', 'current_smoker').",
    )
    activity_level: Optional[str] = Field(
        default="sedentary",
        description="Physical activity tier ('sedentary', 'low', 'moderate', 'high').",
    )
    notes: Optional[str] = Field(
        default="Patient diagnosed with hypertension 8 years ago; reports inconsistent medication compliance on weekends.",
        description="Clinical intake narrative or physician history notes.",
    )
    age: Optional[int] = Field(default=58, description="Patient age.")
    sex: Optional[str] = Field(default="male", description="Biological sex ('male' or 'female').")
    active_symptoms: Optional[List[str]] = Field(
        default=["chest_tightness", "fatigue"],
        description="Presenting symptoms for cross-examination.",
    )
    provider: Optional[str] = Field(default=None, description="Optional LLM provider ('mock', 'groq', 'gemini').")
    use_cache: bool = Field(default=True, description="Enable response caching.")


class LaboratoryAgentTestRequest(BaseModel):
    """Request payload for standalone testing of the Laboratory Biomarker Specialist Agent."""

    systolic_bp: Optional[float] = Field(default=142.0, ge=50, le=280, description="Systolic blood pressure (mmHg).")
    diastolic_bp: Optional[float] = Field(default=88.0, ge=30, le=180, description="Diastolic blood pressure (mmHg).")
    total_cholesterol_mg_dl: Optional[float] = Field(default=225.0, ge=50, le=600, description="Total serum cholesterol (mg/dL).")
    hdl_cholesterol_mg_dl: Optional[float] = Field(default=38.0, ge=10, le=150, description="High-density lipoprotein cholesterol (mg/dL).")
    ldl_cholesterol_mg_dl: Optional[float] = Field(default=145.0, ge=20, le=400, description="Low-density lipoprotein cholesterol (mg/dL).")
    triglycerides_mg_dl: Optional[float] = Field(default=210.0, ge=20, le=1500, description="Serum triglycerides (mg/dL).")
    fasting_blood_glucose_mg_dl: Optional[float] = Field(default=138.0, ge=30, le=600, description="Fasting plasma glucose (mg/dL).")
    hba1c_percent: Optional[float] = Field(default=7.4, ge=3.0, le=20.0, description="Glycated hemoglobin percentage (%).")
    serum_creatinine_mg_dl: Optional[float] = Field(default=1.1, ge=0.1, le=25.0, description="Serum creatinine (mg/dL).")
    estimated_gfr: Optional[float] = Field(default=72.0, ge=1.0, le=200.0, description="Estimated glomerular filtration rate (mL/min/1.73m2).")
    test_date: Optional[str] = Field(default="2026-10-15", description="Date of laboratory specimen collection.")
    age: Optional[int] = Field(default=58, description="Patient age.")
    sex: Optional[str] = Field(default="male", description="Biological sex ('male' or 'female').")
    provider: Optional[str] = Field(default=None, description="Optional LLM provider ('mock', 'groq', 'gemini').")
    use_cache: bool = Field(default=True, description="Enable response caching.")


class RiskPredictionAgentTestRequest(BaseModel):
    """Request payload for standalone testing of the Risk Prediction Ensemble Specialist Agent."""

    age: Optional[int] = Field(default=58, ge=1, le=120, description="Patient age.")
    sex: Optional[str] = Field(default="male", description="Biological sex ('male' or 'female').")
    clinical_scores: Optional[Dict[str, Any]] = Field(
        default={
            "framingham_risk_percent": 18.4,
            "framingham_risk_category": "moderate",
            "findrisc_score": 14,
            "findrisc_risk_category": "moderate",
            "ckd_epi_egfr": 72.0,
            "ckd_stage": "G2",
        },
        description="Deterministic clinical risk equation calculations.",
    )
    ml_predictions: Optional[Dict[str, Any]] = Field(
        default={
            "cardiovascular_risk_percent": 24.6,
            "cardiovascular_risk_category": "high",
            "diabetes_risk_percent": 38.2,
            "diabetes_risk_category": "moderate",
            "top_differential_conditions": [
                {"disease": "coronary_artery_disease", "probability": 0.42},
                {"disease": "essential_hypertension", "probability": 0.31},
                {"disease": "type_2_diabetes", "probability": 0.18},
            ],
        },
        description="Trained machine learning classifier risk predictions.",
    )
    agent_findings: Optional[Dict[str, Any]] = Field(
        default={
            "symptom_findings": "Subacute exertional chest tightness radiating to the left shoulder with associated dyspnea.",
            "medical_history_findings": "Premature paternal CAD history, 8-year history of essential hypertension, active 20 pack-year smoking.",
            "laboratory_findings": "AHA Stage 2 hypertension, atherogenic dyslipidemia (elevated LDL and TG, low HDL), elevated HbA1c (7.4%).",
        },
        description="Qualitative findings from upstream specialist agents.",
    )
    provider: Optional[str] = Field(default=None, description="Optional LLM provider ('mock', 'groq', 'gemini').")
    use_cache: bool = Field(default=True, description="Enable response caching.")



class AnalysisSessionStatusResponse(BaseModel):

    """Polling status schema for client progress indicators."""

    session_id: str
    status: str  # "pending", "running", "completed", "failed"
    current_phase: str
    progress_percent: int
    error_message: Optional[str] = None


class AnalysisSessionResponse(BaseModel):
    """Complete analysis session result including all agent outputs and debate."""

    id: str
    user_id: str
    symptom_report_id: Optional[str] = None
    status: str
    current_phase: str
    progress_percent: int
    consensus_verdict: Optional[Dict[str, Any]] = None
    debate_summary: Optional[Dict[str, Any]] = None
    disease_trajectory: Optional[Dict[str, Any]] = None
    counterfactuals: Optional[List[Dict[str, Any]]] = None
    reasoning_graph: Optional[Dict[str, Any]] = None
    recommended_specialty: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    agent_outputs: List[AgentOutputResponse] = Field(default_factory=list)
    disclaimer: str = (
        "MedOracle is a decision-support assistant and does not provide clinical diagnosis. "
        "Consult a qualified healthcare professional."
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
