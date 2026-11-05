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

import hashlib
import json
import math
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.analysis import AgentOutputResponse


class EvidenceSupportClassification(str, Enum):
    """Explicit claim-specific evidence classification."""

    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT = "INSUFFICIENT"
    UNVERIFIABLE = "UNVERIFIABLE"
    MISSING = "MISSING"
    UNVERIFIED = "UNVERIFIED"
    STALE = "STALE"
    CONFLICTING_SOURCE = "CONFLICTING_SOURCE"
    INVALID = "INVALID"


class EvidenceValidityState(str, Enum):
    """Clinical validity and presence state of required evidence."""

    VERIFIED_PRESENT = "VERIFIED_PRESENT"
    NOT_COLLECTED = "NOT_COLLECTED"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    MISSING = "MISSING"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"
    STALE = "STALE"
    INSUFFICIENT = "INSUFFICIENT"
    INCONCLUSIVE = "INCONCLUSIVE"


class TargetOrganDamageState(str, Enum):
    """Explicit states of acute target-organ damage in hypertensive presentations."""

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"
    SUSPECTED = "SUSPECTED"
    UNVERIFIED = "UNVERIFIED"


class SerialTroponinValidationStatus(str, Enum):
    """Serial cardiac troponin protocol validation state."""

    VALID_SERIAL_SERIES = "VALID_SERIAL_SERIES"
    INSUFFICIENT_TIMING = "INSUFFICIENT_TIMING"
    INCOMPLETE_SERIAL_SERIES = "INCOMPLETE_SERIAL_SERIES"
    INCOMPATIBLE_ASSAY = "INCOMPATIBLE_ASSAY"
    MISSING_TIMESTAMP = "MISSING_TIMESTAMP"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    INSUFFICIENT_METADATA = "INSUFFICIENT_METADATA"


class ContradictionSeverity(str, Enum):
    """Clinical severity grading for detected multi-agent contradictions."""

    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class ContradictionType(str, Enum):
    """Formal taxonomy of clinical contradiction and discrepancy types (Section 4.1)."""

    DIRECT_CLINICAL_CONTRADICTION = "direct_clinical_contradiction"
    MEASUREMENT_DISCREPANCY = "measurement_discrepancy"
    TEMPORAL_DISCREPANCY = "temporal_discrepancy"
    HISTORICAL_VS_CURRENT_DISCREPANCY = "historical_vs_current_discrepancy"
    PATIENT_REPORTED_VS_OBJECTIVELY_MEASURED = "patient_reported_vs_objectively_measured"
    DIFFERENT_CLINICAL_INTERPRETATIONS = "different_clinical_interpretations"
    MISSING_EVIDENCE = "missing_evidence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNVERIFIED_EVIDENCE = "unverified_evidence"
    UNSUPPORTED_AGENT_ASSERTION = "unsupported_agent_assertion"
    INCONCLUSIVE_EVIDENCE = "inconclusive_evidence"


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
    contradiction_type: ContradictionType = Field(
        default=ContradictionType.DIRECT_CLINICAL_CONTRADICTION,
        description="Formal taxonomy type distinguishing direct contradictions from measurement, temporal, or unverified claims.",
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
    INCONCLUSIVE = "inconclusive"



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


# =============================================================================
# Sub-Step 12.3: Confidence Recalibration & Epistemic Doubt Schemas
# =============================================================================

class ClaimRecalibrationRecord(BaseModel):
    """Auditable mathematical recalibration record for an individual specialist agent claim."""

    agent_id: str = Field(..., description="Specialist agent role or identifier.")
    claim_id: str = Field(..., description="Unique claim identifier.")
    claim_text: str = Field(..., description="Exact claim or diagnostic statement.")
    clinical_domain: str = Field(
        default="general",
        description="Clinical domain ('ischemia', 'lipidology', 'hemodynamics', 'glycemia', 'cardiovascular_risk', 'general').",
    )
    original_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Original confidence score expressed by the agent (0.0 to 100.0 scale).",
    )
    evidence_grounding_adjustment: float = Field(
        default=0.0,
        ge=0.0,
        le=15.0,
        description="Positive multiplier adjustment (+0% to +15%) based on verified, independent patient records.",
    )
    contradiction_penalty: float = Field(
        default=0.0,
        ge=0.0,
        le=25.0,
        description="Negative penalty adjustment (-0% to -25%) based on unresolved, active contradictions.",
    )
    missing_evidence_cap_applied: bool = Field(
        default=False,
        description="True if confidence was bounded at 40% due to missing essential clinical evidence.",
    )
    missing_evidence_cap_value: Optional[float] = Field(
        default=None,
        description="Maximum allowed confidence cap (40.0% when essential evidence is missing).",
    )
    missing_evidence_details: List[str] = Field(
        default_factory=list,
        description="Specific missing biomarkers or diagnostic records triggering the cap.",
    )
    recalibrated_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Intermediate confidence score after grounding multiplier and contradiction penalties.",
    )
    final_confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Final post-cap recalibrated confidence score (bounded strictly to [0.0, 100.0]).",
    )
    grounding_evidence_references: List[str] = Field(
        default_factory=list,
        description="Verified independent biomarker keys or clinical sources substantiating this claim.",
    )
    conflicting_evidence_references: List[str] = Field(
        default_factory=list,
        description="Verified biomarker or clinical sources that conflict with or fail to support this claim.",
    )
    evidence_quality_caveats: List[str] = Field(
        default_factory=list,
        description="Quality, staleness, or normalization caveats regarding cited clinical evidence.",
    )
    contradiction_issue_ids: List[str] = Field(
        default_factory=list,
        description="Contradiction issue IDs from Step 12.1 that affected this claim.",
    )
    debate_outcome: Optional[str] = Field(
        default=None,
        description="Debate resolution status ('conceded', 'revised', 'unresolved_disagreement', 'unsupported', 'no_challenge').",
    )
    concession_reason: Optional[str] = Field(
        default=None,
        description="Clinical rationale if the claim was formally conceded.",
    )
    is_withdrawn: bool = Field(
        default=False,
        description="True if claim was formally withdrawn by the specialist during debate.",
    )
    evidence_classifications: Dict[str, str] = Field(
        default_factory=dict,
        description="Explicit classification of each evaluated evidence item (SUPPORTS, CONTRADICTS, NEUTRAL, INSUFFICIENT, UNVERIFIABLE).",
    )
    evidence_states: Dict[str, str] = Field(
        default_factory=dict,
        description="Clinical validity and presence states for required analytes (VERIFIED_PRESENT, MISSING, STALE, AMBIGUOUS, etc.).",
    )
    conflicting_evidence_references: List[str] = Field(
        default_factory=list,
        description="Verified biomarker keys or clinical sources contradicting this claim.",
    )
    evidence_quality_caveats: List[str] = Field(
        default_factory=list,
        description="Quality and validation caveats regarding evidence supporting or affecting this claim.",
    )
    claim_support_score: Optional[float] = Field(
        default=None,
        description="Explicit claim support score (heuristic, not disease probability).",
    )
    heuristic_support_score: Optional[float] = Field(
        default=None,
        description="Alternative naming alias for claim support score.",
    )
    epistemic_doubt_score: Optional[float] = Field(
        default=None,
        description="Domain epistemic doubt associated with this claim.",
    )
    recalibration_explanation: str = Field(
        ...,
        description="Human-readable mathematical audit trail explaining grounding, penalties, caps, and final confidence.",
    )

    @field_validator("original_confidence", "recalibrated_confidence", "final_confidence", mode="before")
    @classmethod
    def validate_finite_confidence(cls, v: Any) -> float:
        try:
            val = float(v)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Confidence score must be a valid numeric float: {v}") from e
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Confidence score cannot be NaN or Infinite: {val}")
        return val

    model_config = ConfigDict(from_attributes=True)


class DomainEpistemicDoubt(BaseModel):
    """Domain-level residual epistemic doubt decomposition."""

    domain: str = Field(..., description="Clinical domain ('ischemia', 'lipidology', 'hemodynamics', 'glycemia', 'cardiovascular_risk').")
    doubt_contribution: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Residual uncertainty contribution for this domain (0.0 to 1.0).",
    )
    unresolved_issues_count: int = Field(default=0, ge=0, description="Count of active unresolved contradictions in this domain.")
    missing_essential_evidence: List[str] = Field(default_factory=list, description="Missing essential biomarkers in this domain.")
    quality_uncertainty_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Uncertainty contribution from OCR quality, stale records, or normalization flags.")
    rationale: str = Field(..., description="Detailed clinical justification for this domain's doubt score.")

    model_config = ConfigDict(from_attributes=True)


class ConfidenceRecalibrationResult(BaseModel):
    """Comprehensive output of the Sub-Step 12.3 Mathematical Confidence Recalibration Engine."""

    session_id: Optional[str] = Field(default=None, description="Traceable session identifier.")
    patient_id: Optional[str] = Field(default=None, description="Traceable patient identifier.")
    recalibrated_claims: List[ClaimRecalibrationRecord] = Field(
        default_factory=list,
        description="Recalibrated confidence records for each agent claim.",
    )
    global_epistemic_doubt_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Global Epistemic Doubt Score representing residual uncertainty across the analysis (0.0 = total certainty, 1.0 = maximum doubt).",
    )
    domain_uncertainty_contributions: List[DomainEpistemicDoubt] = Field(
        default_factory=list,
        description="Domain-decomposed uncertainty contributions.",
    )
    missing_evidence_summary: List[str] = Field(
        default_factory=list,
        description="Essential missing clinical evidence that capped confidence.",
    )
    calibration_status: str = Field(
        default="heuristic_recalibration_v1.0.0",
        description="Methodological status: 'heuristic_recalibration_v1.0.0' (deterministic rule-based, not statistically calibrated).",
    )
    limitations_and_warnings: List[str] = Field(
        default_factory=list,
        description="Clinical and statistical caveats regarding confidence interpretation vs disease probability.",
    )
    summary: str = Field(
        ...,
        description="Executive summary of confidence adjustments and residual epistemic doubt.",
    )
    recalibrated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 recalibration timestamp.",
    )

    model_config = ConfigDict(from_attributes=True)


class RecalibrationTestRequest(BaseModel):
    """Request payload for testing the Confidence Recalibration Engine."""

    session_id: Optional[str] = Field(default=None, description="Optional session identifier.")
    patient_id: Optional[str] = Field(default=None, description="Optional patient identifier.")
    disagreement_threshold: float = Field(default=25.0, ge=5.0, le=50.0)
    agent_outputs: Optional[List[AgentOutputResponse]] = Field(default=None)
    contradiction_matrix: Optional[ContradictionMatrixResult] = Field(default=None)
    debate_transcript: Optional[DebateTranscript] = Field(default=None)
    symptoms_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    medical_history_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    laboratory_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    clinical_scores: Optional[Dict[str, Any]] = Field(default_factory=dict)
    ml_predictions: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class RecalibrationTestResponse(BaseModel):
    """Response payload for testing the Confidence Recalibration Engine."""

    status: str = Field(default="success")
    contradiction_result: ContradictionMatrixResult = Field(...)
    debate_transcript: DebateTranscript = Field(...)
    recalibration_result: ConfidenceRecalibrationResult = Field(...)
    execution_time_ms: float = Field(..., ge=0.0)

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Sub-Step 12.4: Consensus Resolution & Audit Debate Transcript Schemas
# =============================================================================

class ClaimConsensusState(str, Enum):
    """Explicit claim-level consensus resolution state model."""

    SUPPORTED = "SUPPORTED"
    PROVISIONAL = "PROVISIONAL"
    CONFLICTING = "CONFLICTING"
    UNRESOLVED = "UNRESOLVED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED = "UNSUPPORTED"
    WITHDRAWN = "WITHDRAWN"


class ClaimRelationshipType(str, Enum):
    """Pairwise claim relationship classifications."""

    COMPATIBLE = "COMPATIBLE"
    INDEPENDENT = "INDEPENDENT"
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"
    CONTRADICTORY = "CONTRADICTORY"
    HIERARCHICAL = "HIERARCHICAL"
    RELATED = "RELATED"


class ClaimRelationship(BaseModel):
    """Pairwise relationship modeled between specialist claims."""

    source_claim_id: str = Field(..., description="Source claim identifier.")
    target_claim_id: str = Field(..., description="Target claim identifier.")
    relationship_type: ClaimRelationshipType = Field(..., description="Relationship type classification.")
    clinical_rationale: str = Field(..., description="Physiological explanation of relationship.")
    is_compatible: bool = Field(default=True, description="True if claims can validly coexist.")

    model_config = ConfigDict(from_attributes=True)


class OverallConsensusOutcome(str, Enum):
    """Analysis-level multi-claim aggregate consensus outcome."""

    CONSENSUS_SUPPORTED = "CONSENSUS_SUPPORTED"
    CONSENSUS_PROVISIONAL = "CONSENSUS_PROVISIONAL"
    PARTIAL_CONSENSUS = "PARTIAL_CONSENSUS"
    UNRESOLVED_CONSENSUS = "UNRESOLVED_CONSENSUS"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class SafetyOverrideLevel(str, Enum):
    """Urgency grading for clinical safety overrides."""

    EMERGENT = "emergent"
    URGENT = "urgent"
    WARNING = "warning"


class SafetyOverrideLifecycleState(str, Enum):
    """Lifecycle tracking states for active clinical safety alerts."""

    ACTIVE = "ACTIVE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESOLVED = "RESOLVED"
    SUPERSEDED = "SUPERSEDED"


class SafetyOverrideWarning(BaseModel):
    """Critical clinical safety warning preserved independently of consensus."""

    warning_id: str = Field(..., description="Unique collision-proof safety warning identifier.")
    condition_name: str = Field(..., description="High-risk clinical condition (e.g. 'Acute Coronary Syndrome', 'DKA', 'Hypertensive Emergency').")
    level: SafetyOverrideLevel = Field(..., description="Safety override urgency level ('emergent', 'urgent', 'warning').")
    lifecycle_state: SafetyOverrideLifecycleState = Field(
        default=SafetyOverrideLifecycleState.ACTIVE,
        description="Lifecycle tracking state of the clinical safety override.",
    )
    trigger_rationale: str = Field(..., description="Objective clinical rationale triggering the safety alert.")
    action_recommendation: str = Field(..., description="Immediate clinical action recommendation (decision support language).")
    overrides_consensus: bool = Field(default=True, description="True if alert remains active regardless of agent agreement or debate outcome.")

    model_config = ConfigDict(from_attributes=True)


class ClaimResolutionRecord(BaseModel):
    """Auditable claim-level consensus decision record."""

    claim_id: str = Field(..., description="Unique claim identifier.")
    agent_id: str = Field(..., description="Specialist agent role or identifier.")
    original_claim: str = Field(..., description="Original claim narrative as formulated pre-debate.")
    clinical_domain: str = Field(..., description="Clinical domain ('ischemia', 'lipidology', 'hemodynamics', 'glycemia', 'cardiovascular_risk', 'general').")
    consensus_state: ClaimConsensusState = Field(..., description="Claim-level consensus outcome.")
    claim_type: str = Field(default="primary", description="Clinical hierarchy role: 'primary', 'secondary', 'differential', or 'safety_critical'.")
    is_safety_critical: bool = Field(default=False, description="True if claim addresses acute or emergent conditions.")
    recalibrated_confidence: float = Field(..., ge=0.0, le=100.0, description="Recalibrated support score.")
    final_confidence: float = Field(..., ge=0.0, le=100.0, description="Post-cap bounded confidence.")
    evidence_grounding_references: List[str] = Field(default_factory=list, description="Verified patient evidence keys directly supporting this claim.")
    evidence_classifications: Dict[str, str] = Field(default_factory=dict, description="Classifications for all evaluated evidence items.")
    conflicting_evidence_references: List[str] = Field(default_factory=list, description="Evidence items that contradict this claim.")
    missing_evidence_details: List[str] = Field(default_factory=list, description="Essential clinical evidence missing for this claim.")
    contradiction_issue_ids: List[str] = Field(default_factory=list, description="Contradiction issue IDs from Step 12.1 affecting this claim.")
    debate_outcome: Optional[str] = Field(default=None, description="Debate outcome ('conceded', 'revised', 'unresolved_disagreement', 'unsupported').")
    is_withdrawn: bool = Field(default=False, description="True if claim was formally withdrawn by specialist.")
    is_revised: bool = Field(default=False, description="True if claim was modified during debate.")
    revised_claim_text: Optional[str] = Field(default=None, description="Revised claim narrative if applicable.")
    domain_epistemic_doubt: float = Field(default=0.0, ge=0.0, le=1.0, description="Residual epistemic doubt for this claim's domain.")
    resolution_rationale: str = Field(..., description="Transparent clinical decision rationale explaining consensus state.")

    model_config = ConfigDict(from_attributes=True)


class AuditDebateTranscript(BaseModel):
    """Complete, immutable, and traceable audit transcript of multi-agent deliberation and consensus resolution."""

    transcript_id: str = Field(..., description="Unique collision-proof audit transcript identifier.")
    session_id: Optional[str] = Field(default=None, description="Traceable analysis session identifier.")
    analysis_id: Optional[str] = Field(default=None, description="Traceable analysis identifier.")
    patient_id: Optional[str] = Field(default=None, description="Traceable patient identifier.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 creation timestamp.")
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 completion timestamp.")
    participating_agents: List[str] = Field(default_factory=list, description="List of specialist agent roles participating in deliberation.")
    original_claims: List[Dict[str, Any]] = Field(default_factory=list, description="All pre-debate specialist claims with initial confidence.")
    evidence_references: List[str] = Field(default_factory=list, description="All verified patient biomarkers and clinical sources cited.")
    contradiction_records: List[Dict[str, Any]] = Field(default_factory=list, description="All detected contradiction issues with severity.")
    debate_rounds_executed: int = Field(default=2, ge=1, le=2, description="Total debate rounds executed (bounded at 2).")
    challenges: List[Dict[str, Any]] = Field(default_factory=list, description="Round 1 challenges issued across specialist agents.")
    rebuttals: List[Dict[str, Any]] = Field(default_factory=list, description="Round 2 rebuttals, defenses, and concessions submitted.")
    revisions: List[Dict[str, Any]] = Field(default_factory=list, description="Recorded claim revisions during debate.")
    concessions: List[Dict[str, Any]] = Field(default_factory=list, description="Recorded concessions during debate.")
    unsupported_findings: List[str] = Field(default_factory=list, description="Findings identified as lacking empirical evidentiary backing.")
    recalibrated_claim_support_scores: Dict[str, float] = Field(default_factory=dict, description="Recalibrated support scores mapped by claim ID.")
    epistemic_doubt_values: Dict[str, float] = Field(default_factory=dict, description="Domain-decomposed epistemic doubt scores.")
    claim_resolutions: List[ClaimResolutionRecord] = Field(default_factory=list, description="Claim-level consensus resolution decisions.")
    claim_relationships: List[ClaimRelationship] = Field(default_factory=list, description="Explicit pairwise claim relationship models.")
    overall_outcome: OverallConsensusOutcome = Field(..., description="Aggregate multi-claim consensus outcome.")
    clinical_safety_warnings: List[SafetyOverrideWarning] = Field(default_factory=list, description="Active emergency/urgent clinical safety overrides.")
    unresolved_issues: List[str] = Field(default_factory=list, description="Summary of unresolved disagreements and epistemic uncertainties.")
    final_resolution_rationale: str = Field(..., description="Comprehensive clinical rationale explaining final outcome.")
    transcript_version: str = Field(default="consensus_audit_v1.0.0", description="Audit schema version.")
    is_immutable: bool = Field(default=True, description="Audit immutability guarantee.")
    canonical_transcript_hash: Optional[str] = Field(default=None, description="SHA-256 cryptographic hash of canonical transcript representation.")
    previous_block_hash: Optional[str] = Field(default=None, description="Hash of preceding audit block for tamper-evident chaining.")
    milestone_hashes: Dict[str, str] = Field(default_factory=dict, description="Cryptographic checkpoints across deliberation milestones.")

    model_config = ConfigDict(from_attributes=True)

    def compute_transcript_hash(self) -> str:
        """Compute deterministic SHA-256 hash across canonical serialized fields (excluding hash itself)."""
        data = self.model_dump(exclude={"canonical_transcript_hash"})
        canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def verify_transcript_integrity(self) -> bool:
        """Verify that the transcript has not been altered since sealing."""
        if not self.canonical_transcript_hash:
            return False
        expected = self.compute_transcript_hash()
        return self.canonical_transcript_hash == expected


class ConsensusResolutionResult(BaseModel):
    """Output of the Sub-Step 12.4 Consensus Resolution Engine."""

    session_id: Optional[str] = Field(default=None, description="Session identifier.")
    analysis_id: Optional[str] = Field(default=None, description="Analysis identifier.")
    patient_id: Optional[str] = Field(default=None, description="Patient identifier.")
    overall_outcome: OverallConsensusOutcome = Field(..., description="Overall analysis consensus outcome.")
    claim_resolutions: List[ClaimResolutionRecord] = Field(default_factory=list, description="Resolved claim-level records.")
    claim_relationships: List[ClaimRelationship] = Field(default_factory=list, description="Modeled relationships between claims.")
    clinical_safety_warnings: List[SafetyOverrideWarning] = Field(default_factory=list, description="Independent safety overrides.")
    primary_diagnoses: List[str] = Field(default_factory=list, description="Primary confirmed or supported clinical diagnoses.")
    secondary_diagnoses: List[str] = Field(default_factory=list, description="Secondary confirmed comorbidities.")
    differential_diagnoses: List[str] = Field(default_factory=list, description="Differential diagnoses under active consideration.")
    safety_critical_diagnoses: List[str] = Field(default_factory=list, description="Acute safety-critical findings requiring immediate action.")
    global_epistemic_doubt_score: float = Field(..., ge=0.0, le=1.0, description="Global epistemic doubt score.")
    audit_transcript: AuditDebateTranscript = Field(..., description="Complete auditable debate and consensus transcript.")
    resolution_summary: str = Field(..., description="Executive clinical resolution summary.")
    methodological_notes: List[str] = Field(default_factory=list, description="Methodological limitations and safety guardrails.")
    resolved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 resolution timestamp.")

    model_config = ConfigDict(from_attributes=True)


class ConsensusResolutionRequest(BaseModel):
    """Request payload for Consensus Resolution & Audit Transcript Generation."""

    session_id: Optional[str] = Field(default=None, description="Optional session identifier.")
    analysis_id: Optional[str] = Field(default=None, description="Optional analysis identifier.")
    patient_id: Optional[str] = Field(default=None, description="Optional patient identifier for authorization.")
    disagreement_threshold: float = Field(default=25.0, ge=5.0, le=50.0)
    agent_outputs: Optional[List[AgentOutputResponse]] = Field(default=None)
    contradiction_matrix: Optional[ContradictionMatrixResult] = Field(default=None)
    debate_transcript: Optional[DebateTranscript] = Field(default=None)
    recalibration_result: Optional[ConfidenceRecalibrationResult] = Field(default=None)
    symptoms_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    medical_history_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    laboratory_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    clinical_scores: Optional[Dict[str, Any]] = Field(default_factory=dict)
    ml_predictions: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ConsensusResolutionResponse(BaseModel):
    """Response payload for Consensus Resolution API."""

    status: str = Field(default="success", description="Status string ('success', 'failed').")
    resolution: ConsensusResolutionResult = Field(..., description="Consensus resolution result with transcript.")
    execution_time_ms: float = Field(..., ge=0.0, description="Latency in milliseconds.")

    model_config = ConfigDict(from_attributes=True)

