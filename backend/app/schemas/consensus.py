"""Pydantic v2 schemas for Consensus & Multi-Agent Debate Framework (Step 12).

Defines structured data contracts for:
1. Contradiction Detection Engine (Sub-Step 12.1)
2. Adversarial Debate Protocol (Sub-Step 12.2)
3. Confidence Recalibration & Doubt Scoring (Sub-Step 12.3)
4. Consensus Resolution & Debate Transcript (Sub-Step 12.4)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import AgentOutputResponse


class ContradictionSeverity(str, Enum):
    """Clinical severity grading for detected multi-agent contradictions."""

    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class ContradictionCategory(str, Enum):
    """Clinical category of physiological or pharmacological discordance."""

    SUBJECTIVE_VS_OBJECTIVE = "subjective_vs_objective"
    HISTORY_MEDICATION_VS_BIOMARKER = "history_medication_vs_biomarker"
    EQUATION_VS_ML_DISCORDANCE = "equation_vs_ml_discordance"
    SYMPTOM_VS_HISTORY_DISCORDANCE = "symptom_vs_history_discordance"
    QUALITATIVE_CLAIM_DISCORDANCE = "qualitative_claim_discordance"


class ContradictionIssue(BaseModel):
    """Structured representation of an individual detected clinical contradiction."""

    issue_id: str = Field(
        ...,
        description="Unique issue identifier (e.g. 'ISSUE-SUBJ-OBJ-001').",
    )
    category: ContradictionCategory = Field(
        ...,
        description="Category of clinical discordance.",
    )
    severity: ContradictionSeverity = Field(
        ...,
        description="Clinical severity grade ('minor', 'moderate', 'critical').",
    )
    conflicting_agents: List[str] = Field(
        ...,
        min_length=2,
        description="Agent roles involved in the contradiction.",
    )
    diverging_claims: Dict[str, str] = Field(
        ...,
        description="Mapping from agent role or data source to its specific claim or data value.",
    )
    physiological_rationale: str = Field(
        ...,
        description="Clinical rationale explaining why the claims are physiologically or pharmacologically contradictory.",
    )
    suggested_challenge: str = Field(
        ...,
        description="Targeted challenge prompt formulated for the adversarial debate round.",
    )
    evidence_references: List[str] = Field(
        default_factory=list,
        description="Keys or names of specific biomarkers, medications, or scores involved.",
    )

    model_config = ConfigDict(from_attributes=True)


class ContradictionMatrixResult(BaseModel):
    """Comprehensive output of the multi-agent contradiction detection matrix."""

    contradictions_detected: bool = Field(
        ...,
        description="True if one or more clinical contradictions were identified.",
    )
    total_contradictions: int = Field(
        default=0,
        ge=0,
        description="Total count of detected contradiction issues.",
    )
    critical_count: int = Field(
        default=0,
        ge=0,
        description="Count of critical-severity contradictions.",
    )
    moderate_count: int = Field(
        default=0,
        ge=0,
        description="Count of moderate-severity contradictions.",
    )
    minor_count: int = Field(
        default=0,
        ge=0,
        description="Count of minor-severity contradictions.",
    )
    issues: List[ContradictionIssue] = Field(
        default_factory=list,
        description="List of structured contradiction issues.",
    )
    preliminary_epistemic_doubt: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Preliminary epistemic doubt score (0.0 to 1.0) scaled by contradiction severities.",
    )
    summary: str = Field(
        ...,
        description="Clinical narrative summarizing the detected contradictions and debate triggers.",
    )
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 evaluation timestamp.",
    )

    model_config = ConfigDict(from_attributes=True)


class ContradictionTestRequest(BaseModel):
    """Request payload for standalone testing of the Contradiction Detection Engine."""

    agent_outputs: Optional[List[AgentOutputResponse]] = Field(
        default=None,
        description="Optional list of structured outputs from upstream domain agents.",
    )
    symptoms_data: Optional[Dict[str, Any]] = Field(
        default={
            "symptoms": ["chest_pain", "breathlessness", "palpitations"],
            "severity": 8,
            "duration_days": 2,
            "notes": "Patient describes acute substernal chest pressure radiating to left shoulder on exertion.",
        },
        description="Patient presenting symptoms and narrative.",
    )
    medical_history_data: Optional[Dict[str, Any]] = Field(
        default={
            "chronic_conditions": ["hypertension", "hyperlipidemia"],
            "current_medications": [
                {"name": "Atorvastatin", "dosage": "40mg", "frequency": "daily"},
                {"name": "Lisinopril", "dosage": "20mg", "frequency": "daily"},
            ],
            "family_history": [{"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 50}],
            "smoking_status": "current_smoker",
        },
        description="Pharmacological and longitudinal medical history.",
    )
    laboratory_data: Optional[Dict[str, Any]] = Field(
        default={
            "systolic_bp": 154.0,
            "diastolic_bp": 96.0,
            "total_cholesterol_mg_dl": 275.0,
            "hdl_cholesterol_mg_dl": 35.0,
            "ldl_cholesterol_mg_dl": 195.0,
            "fasting_blood_glucose_mg_dl": 105.0,
            "hba1c_percent": 5.6,
            "cardiac_troponin_ng_ml": 0.01,
            "resting_ecg": "normal_sinus_rhythm",
        },
        description="Objective laboratory biomarkers and vitals.",
    )
    clinical_scores: Optional[Dict[str, Any]] = Field(
        default={
            "framingham_risk_percent": 14.5,
            "framingham_risk_category": "moderate",
            "findrisc_score": 6,
            "findrisc_risk_category": "low",
        },
        description="Deterministic population risk equation scores.",
    )
    ml_predictions: Optional[Dict[str, Any]] = Field(
        default={
            "cardiovascular_risk_percent": 45.2,
            "cardiovascular_risk_category": "high",
            "diabetes_risk_percent": 12.0,
            "diabetes_risk_category": "low",
            "top_differential_conditions": [
                {"disease": "coronary_artery_disease", "probability": 0.52},
                {"disease": "essential_hypertension", "probability": 0.28},
            ],
        },
        description="Supervised machine learning model predictions.",
    )

    model_config = ConfigDict(from_attributes=True)


class ContradictionTestResponse(BaseModel):
    """Response payload for standalone testing of the Contradiction Detection Engine."""

    status: str = Field(default="success", description="Evaluation status ('success', 'failed').")
    result: ContradictionMatrixResult = Field(
        ...,
        description="Evaluation results from the contradiction matrix.",
    )
    execution_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Execution latency in milliseconds.",
    )

    model_config = ConfigDict(from_attributes=True)
