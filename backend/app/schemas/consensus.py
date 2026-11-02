"""Pydantic v2 schemas for Consensus & Multi-Agent Debate Framework (Step 12).

Defines structured data contracts for:
1. Contradiction Detection Engine (Sub-Step 12.1)
   - Cross-referencing subjective symptoms vs. objective biomarkers (with serial testing & onset timing caveats)
   - Longitudinal medication adherence & therapeutic latency vs. active biomarker endpoints
   - Cohort equations vs. ML models (with horizon/outcome compatibility validation)
   - Full evidence provenance, collision-proof issue tracking, and clinical limitations
   - Separation of clinical urgency from contradiction severity
2. Adversarial Debate Protocol (Sub-Step 12.2)
   - Round 1 evidence submission and targeted challenge issuance
   - Round 2 rebuttals, physiological grounding, concessions, and convergence
   - Natural Language Inference (NLI) qualitative claim analysis
   - Multi-agent debate transcript and audit history
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
        description="Globally unique, collision-proof issue identifier (e.g. 'ISSUE-session_1-SUBJ-OBJ-001-a1b2c3d4').",
    )
    rule_id: str = Field(
        default="RULE-GENERAL",
        description="Formal clinical rule identifier (e.g. 'RULE-A1-ISCHEMIA-TROPONIN').",
    )
    rule_version: str = Field(
        default="1.2.0",
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
        description="Clinical severity grade of contradiction ('minor', 'moderate', 'critical').",
    )
    clinical_urgency: str = Field(
        default="routine",
        description="Urgency of medical evaluation ('routine', 'prompt', 'urgent', 'emergent', 'undetermined'). Strictly separated from contradiction severity.",
    )
    clinical_status: str = Field(
        default="confirmed_contradiction",
        description="Epistemic status ('confirmed_contradiction', 'provisional_discrepancy', 'unresolved_presentation', 'history_versus_evidence_discrepancy', 'incomparable_models').",
    )
    target_organ_damage_status: Optional[str] = Field(
        default=None,
        description="Status of acute target-organ damage ('present', 'absent', 'undetermined').",
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
            "qualitative_claim_discordance": "operational",
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


# =============================================================================
# Sub-Step 12.2: Adversarial Debate Protocol Schemas
# =============================================================================

class ChallengeStatus(str, Enum):
    """Status of an adversarial challenge within the debate protocol."""

    ISSUED = "issued"
    DEFENDED = "defended"
    REVISED = "revised"
    CONCEDED = "conceded"
    UNRESOLVED_DISAGREEMENT = "unresolved_disagreement"
    UNSUPPORTED = "unsupported"
    INCOMPARABLE_EXCLUDED = "incomparable_excluded"


class RebuttalDisposition(str, Enum):
    """Formal disposition chosen by a challenged agent in Round 2."""

    DEFEND = "defend"
    REVISE = "revise"
    CONCEDE = "concede"
    UNSUPPORTED = "unsupported"
    INCONCLUSIVE = "inconclusive"


class NLIRelation(str, Enum):
    """Natural Language Inference semantic relationship between agent narrative claims."""

    ENTAILMENT = "entailment"
    CONTRADICTION = "contradiction"
    NEUTRAL = "neutral"
    UNCERTAIN = "uncertain"


class AgentChallenge(BaseModel):
    """Round 1 cross-domain adversarial challenge generated from detected contradiction."""

    challenge_id: str = Field(
        ...,
        description="Unique identifier for the challenge.",
    )
    issue_id: str = Field(
        ...,
        description="Underlying contradiction issue ID.",
    )
    round_number: int = Field(
        default=1,
        description="Debate round number (1 for initial challenge issuance).",
    )
    challenging_agent: str = Field(
        ...,
        description="Agent role issuing the challenge.",
    )
    challenged_agent: str = Field(
        ...,
        description="Agent role targeted by the challenge.",
    )
    challenged_claim: str = Field(
        ...,
        description="Exact claim or hypothesis being challenged.",
    )
    evidence_basis: List[str] = Field(
        default_factory=list,
        description="Objective evidence, biomarkers, or scores used to substantiate the challenge.",
    )
    physiological_rationale: str = Field(
        ...,
        description="Physiological or clinical reasoning for the challenge.",
    )
    challenge_text: str = Field(
        ...,
        description="Targeted adversarial challenge prompt presented to the agent.",
    )
    clinical_limitations: List[str] = Field(
        default_factory=list,
        description="Known clinical confounders or caveats associated with the challenge.",
    )
    status: ChallengeStatus = Field(
        default=ChallengeStatus.ISSUED,
        description="Current resolution status of the challenge.",
    )

    model_config = ConfigDict(from_attributes=True)


class AgentRebuttal(BaseModel):
    """Round 2 rebuttal, physiological grounding, or formal concession from challenged agent."""

    rebuttal_id: str = Field(
        ...,
        description="Unique identifier for the rebuttal.",
    )
    challenge_id: str = Field(
        ...,
        description="Corresponding challenge ID being addressed.",
    )
    issue_id: str = Field(
        ...,
        description="Underlying contradiction issue ID.",
    )
    round_number: int = Field(
        default=2,
        description="Debate round number (2 for rebuttal/concession).",
    )
    responding_agent: str = Field(
        ...,
        description="Agent role providing the rebuttal.",
    )
    disposition: RebuttalDisposition = Field(
        ...,
        description="Formal stance taken ('defend', 'revise', 'concede', 'unsupported', 'inconclusive').",
    )
    rebuttal_text: str = Field(
        ...,
        description="Clinical argument defending, revising, or conceding the challenged claim.",
    )
    grounding_evidence: List[str] = Field(
        default_factory=list,
        description="Specific biomarkers, historical records, or model endpoints grounding the response.",
    )
    revised_claim: Optional[str] = Field(
        default=None,
        description="Updated claim if disposition is 'revise'.",
    )
    concession_reason: Optional[str] = Field(
        default=None,
        description="Explicit clinical rationale if conceding the claim.",
    )
    acknowledged_limitations: List[str] = Field(
        default_factory=list,
        description="Diagnostic and clinical limitations acknowledged by the agent.",
    )
    evidence_missing: bool = Field(
        default=False,
        description="True if required evidence is absent in patient record rather than fabricated.",
    )

    model_config = ConfigDict(from_attributes=True)


class NLIAnalysisRecord(BaseModel):
    """Audit record of Natural Language Inference between qualitative agent claims."""

    pair_id: str = Field(
        ...,
        description="Unique identifier for the claim comparison pair.",
    )
    agent_a: str = Field(..., description="First agent role.")
    claim_a: str = Field(..., description="First agent narrative claim.")
    agent_b: str = Field(..., description="Second agent role.")
    claim_b: str = Field(..., description="Second agent narrative claim.")
    relation: NLIRelation = Field(
        ...,
        description="Classified semantic relationship ('entailment', 'contradiction', 'neutral', 'uncertain').",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the NLI classification.",
    )
    method: str = Field(
        ...,
        description="NLI model or deterministic method employed.",
    )
    limitations: str = Field(
        default="",
        description="Methodological limitations of the NLI evaluation.",
    )

    model_config = ConfigDict(from_attributes=True)


class DebateTranscript(BaseModel):
    """Complete, auditable transcript of the two-round adversarial debate protocol."""

    debate_id: str = Field(
        ...,
        description="Unique identifier for this debate execution.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Traceable session identifier.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Traceable patient identifier.",
    )
    total_rounds_executed: int = Field(
        default=2,
        ge=1,
        le=2,
        description="Total rounds executed (bounded at maximum 2 rounds).",
    )
    max_rounds_allowed: int = Field(
        default=2,
        description="Strict maximum allowed debate rounds.",
    )
    challenges: List[AgentChallenge] = Field(
        default_factory=list,
        description="All Round 1 challenges issued across domain agents.",
    )
    rebuttals: List[AgentRebuttal] = Field(
        default_factory=list,
        description="All Round 2 rebuttals, defenses, and concessions submitted.",
    )
    conceded_challenges: List[str] = Field(
        default_factory=list,
        description="Challenge IDs where the challenged agent formally conceded.",
    )
    unresolved_disagreements: List[str] = Field(
        default_factory=list,
        description="Challenge IDs where disagreement persisted with valid clinical grounding.",
    )
    unsupported_challenges: List[str] = Field(
        default_factory=list,
        description="Challenge IDs where supporting evidence was missing or insufficient.",
    )
    qualitative_nli_analyses: List[NLIAnalysisRecord] = Field(
        default_factory=list,
        description="Natural language inference analysis records for qualitative agent claims.",
    )
    convergence_status: str = Field(
        default="converged",
        description="Final convergence status ('converged', 'partial_convergence', 'unresolved_divergence', 'no_contradictions').",
    )
    summary: str = Field(
        ...,
        description="Executive summary of the debate outcome, concessions, and active disagreements.",
    )
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 start timestamp.",
    )
    completed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 completion timestamp.",
    )

    model_config = ConfigDict(from_attributes=True)


class DebateTestRequest(BaseModel):
    """Request payload for testing the Multi-Agent Adversarial Debate Protocol."""

    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for traceability.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Optional patient identifier for audit tracking.",
    )
    disagreement_threshold: float = Field(
        default=25.0,
        ge=5.0,
        le=50.0,
        description="Disagreement threshold for model horizon comparison.",
    )
    agent_outputs: Optional[List[AgentOutputResponse]] = Field(
        default=None,
        description="Optional list of upstream agent outputs.",
    )
    symptoms_data: Optional[Dict[str, Any]] = Field(
        default={
            "symptoms": ["chest_pain", "breathlessness", "palpitations"],
            "severity": 8,
            "duration_days": 2,
            "duration_hours": 48.0,
            "notes": "Patient describes acute substernal chest pressure radiating to left shoulder on exertion.",
        },
        description="Presenting symptoms data (defaults to sample if omitted).",
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
        description="Patient medical and medication history.",
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
        description="Deterministic risk equation scores.",
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
        description="Supervised ML model predictions.",
    )

    model_config = ConfigDict(from_attributes=True)


class DebateTestResponse(BaseModel):
    """Response payload for the Multi-Agent Adversarial Debate Protocol test endpoint."""

    status: str = Field(default="success", description="Execution status ('success', 'failed').")
    contradiction_result: ContradictionMatrixResult = Field(
        ...,
        description="Underlying contradiction detection matrix output.",
    )
    debate_transcript: DebateTranscript = Field(
        ...,
        description="Complete auditable transcript of the adversarial debate protocol.",
    )
    execution_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Total execution latency in milliseconds.",
    )

    model_config = ConfigDict(from_attributes=True)
