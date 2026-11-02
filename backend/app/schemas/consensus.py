"""Pydantic v2 schemas for Consensus & Multi-Agent Debate Framework (Step 12).

Defines structured data contracts for:
1. Contradiction Detection Engine (Sub-Step 12.1)
   - Cross-referencing subjective symptoms vs. objective biomarkers (with serial testing & onset timing caveats)
   - Longitudinal medication adherence & therapeutic latency vs. active biomarker endpoints
   - Cohort equations vs. ML models (with horizon/outcome compatibility validation)
   - Full evidence provenance, collision-proof issue tracking, and clinical limitations
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
    INCOMPARABLE_PREDICTIONS = "incomparable_predictions"
    SYMPTOM_VS_HISTORY_DISCORDANCE = "symptom_vs_history_discordance"
    QUALITATIVE_CLAIM_DISCORDANCE = "qualitative_claim_discordance"


class ContradictionIssue(BaseModel):
    """Structured representation of an individual detected clinical contradiction with full provenance."""

    issue_id: str = Field(
        ...,
        description="Unique, collision-proof issue identifier (e.g. 'ISSUE-SUBJ-OBJ-001-A1B2C3D4').",
    )
    rule_id: str = Field(
        default="RULE-GENERAL",
        description="Formal clinical rule identifier (e.g. 'RULE-A1-ISCHEMIA-TROPONIN').",
    )
    rule_version: str = Field(
        default="1.1.0",
        description="Version of the clinical contradiction detection rule.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Traceable analysis session identifier.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Traceable patient identifier.",
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
        description="Exact original conflicting claims or data values mapped by agent role/source.",
    )
    normalized_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Standardized clinical values, assay types, and SI/conventional units.",
    )
    measurement_timestamps: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Collection timestamps or onset timeframes for each piece of evidence.",
    )
    evidence_sources: List[str] = Field(
        default_factory=list,
        description="Evidence origin types (e.g. 'laboratory_biomarkers', 'symptom_report', 'medical_history').",
    )
    physiological_rationale: str = Field(
        ...,
        description="Clinical rationale explaining why the claims are physiologically or pharmacologically contradictory.",
    )
    clinical_limitations: List[str] = Field(
        default_factory=list,
        description="Authoritative clinical caveats, confounding factors, and diagnostic limitations.",
    )
    suggested_challenge: str = Field(
        ...,
        description="Targeted challenge prompt formulated for the adversarial debate round (Sub-Step 12.2).",
    )
    evidence_references: List[str] = Field(
        default_factory=list,
        description="Keys or names of specific biomarkers, medications, or scores involved.",
    )
    is_confirmed_contradiction: bool = Field(
        default=True,
        description="True if definitively contradictory; False if provisional/indeterminate pending serial or confirmatory testing.",
    )

    model_config = ConfigDict(from_attributes=True)


class ContradictionMatrixResult(BaseModel):
    """Comprehensive output of the multi-agent contradiction detection matrix with provenance & doubt audit."""

    session_id: Optional[str] = Field(
        default=None,
        description="Traceable analysis session identifier.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Traceable patient identifier.",
    )
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
        description="Preliminary epistemic doubt score (0.0 to 1.0) scaled by deduplicated contradiction severities.",
    )
    doubt_calculation_method: str = Field(
        default="deduplicated_heuristic_severity_weighting",
        description="Mathematical methodology used for the preliminary doubt score.",
    )
    doubt_limitations: str = Field(
        default=(
            "Preliminary heuristic score for input ranking only. Not a calibrated posterior probability. "
            "Co-dependent contradictions are deduplicated prior to scoring. Full epistemic recalibration deferred to Sub-Step 12.3."
        ),
        description="Explicit methodological caveats for the preliminary doubt score.",
    )
    category_statuses: Dict[str, str] = Field(
        default_factory=lambda: {
            "subjective_vs_objective": "operational",
            "history_medication_vs_biomarker": "operational",
            "equation_vs_ml_discordance": "operational",
            "incomparable_predictions": "operational",
            "qualitative_claim_discordance": "unimplemented_deferred_to_12_2",
        },
        description="Operational implementation status of each contradiction category.",
    )
    model_comparisons: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Structured outcome and horizon compatibility evaluation for quantitative models.",
    )
    summary: str = Field(
        ...,
        description="Clinical narrative summarizing the detected contradictions, limitations, and debate triggers.",
    )
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 evaluation timestamp.",
    )

    model_config = ConfigDict(from_attributes=True)


class ContradictionTestRequest(BaseModel):
    """Request payload for standalone testing of the Contradiction Detection Engine."""

    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for end-to-end traceability.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Optional patient identifier for audit tracking.",
    )
    disagreement_threshold: float = Field(
        default=25.0,
        ge=5.0,
        le=50.0,
        description="Configurable percentage-point disagreement threshold for equation vs ML comparison (heuristic disparity flag, not an established clinical standard).",
    )
    agent_outputs: Optional[List[AgentOutputResponse]] = Field(
        default=None,
        description="Optional list of structured outputs from upstream domain agents.",
    )
    symptoms_data: Optional[Dict[str, Any]] = Field(
        default={
            "symptoms": ["chest_pain", "breathlessness", "palpitations"],
            "severity": 8,
            "duration_days": 2,
            "duration_hours": 48.0,
            "notes": "Patient describes acute substernal chest pressure radiating to left shoulder on exertion.",
        },
        description="Patient presenting symptoms and narrative.",
    )
    medical_history_data: Optional[Dict[str, Any]] = Field(
        default={
            "chronic_conditions": ["hypertension", "hyperlipidemia"],
            "current_medications": [
                {
                    "name": "Atorvastatin",
                    "dosage": "40mg",
                    "frequency": "daily",
                    "treatment_duration_weeks": 24,
                    "adherence": "consistent",
                },
                {
                    "name": "Lisinopril",
                    "dosage": "20mg",
                    "frequency": "daily",
                    "treatment_duration_weeks": 52,
                    "adherence": "consistent",
                },
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
            "cardiac_troponin_assay": "hs_cTnI",
            "serial_troponin_completed": True,
            "resting_ecg": "normal_sinus_rhythm",
            "test_date": "2026-11-01",
        },
        description="Objective laboratory biomarkers and vitals.",
    )
    clinical_scores: Optional[Dict[str, Any]] = Field(
        default={
            "framingham_risk_percent": 14.5,
            "framingham_risk_category": "moderate",
            "target_outcome": "10_year_incident_cvd",
            "prediction_horizon": "10_years",
            "findrisc_score": 6,
            "findrisc_risk_category": "low",
        },
        description="Deterministic population risk equation scores.",
    )
    ml_predictions: Optional[Dict[str, Any]] = Field(
        default={
            "cardiovascular_risk_percent": 45.2,
            "cardiovascular_risk_category": "high",
            "target_outcome": "angiographic_coronary_artery_disease_presence",
            "prediction_horizon": "cross_sectional",
            "calibrated": False,
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
