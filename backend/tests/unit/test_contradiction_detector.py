"""Unit tests for the Contradiction Detection Engine (Sub-Step 12.1).

Validates:
1. Subjective symptoms vs. Objective laboratory biomarkers
2. Longitudinal medication adherence vs. Active biomarker endpoints
3. Deterministic cohort equations vs. Machine learning classifiers
4. Qualitative narrative findings cross-examination
5. Epistemic doubt score mathematical bounds and convergence
6. Concordant (zero contradiction) scenarios
"""

import pytest
from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    ContradictionCategory,
    ContradictionMatrixResult,
    ContradictionSeverity,
)


@pytest.fixture
def detector() -> ContradictionDetector:
    """Fixture providing an initialized ContradictionDetector."""
    return ContradictionDetector()


def test_rule_a1_acute_chest_pain_vs_normal_troponin_ecg(detector: ContradictionDetector) -> None:
    """Test Rule A1: Acute severe ischemic chest pain with normal troponin/ECG generates critical contradiction."""
    symptoms = {
        "symptoms": ["chest_pain", "substernal_pressure", "radiating_chest_pain"],
        "severity": 8,
        "notes": "Severe crushing substernal chest pressure radiating to the left jaw.",
    }
    labs = {
        "cardiac_troponin_ng_ml": 0.01,  # strictly normal (< 0.04)
        "resting_ecg": "normal_sinus_rhythm",
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-SUBJ-OBJ-001" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-SUBJ-OBJ-001")
    assert issue.category == ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "Symptom Analysis Specialist" in issue.conflicting_agents
    assert "Laboratory Biomarker Specialist" in issue.conflicting_agents
    assert "troponin" in issue.physiological_rationale.lower()
    assert result.critical_count >= 1
    assert result.preliminary_epistemic_doubt >= 0.25


def test_rule_a2_severe_dyspnea_vs_normal_bnp(detector: ContradictionDetector) -> None:
    """Test Rule A2: Severe acute dyspnea with normal BNP generates moderate contradiction."""
    symptoms = {
        "symptoms": ["breathlessness", "orthopnea"],
        "severity": 8,
        "notes": "Patient complains of inability to catch breath.",
    }
    labs = {
        "bnp_pg_ml": 45.0,  # normal (< 100 pg/mL)
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-SUBJ-OBJ-002" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-SUBJ-OBJ-002")
    assert issue.category == ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE
    assert issue.severity == ContradictionSeverity.MODERATE
    assert "BNP" in issue.diverging_claims["Laboratory Biomarker Specialist"]


def test_rule_a3_asymptomatic_vs_malignant_hypertension(detector: ContradictionDetector) -> None:
    """Test Rule A3: Asymptomatic patient with Stage 2 malignant hypertension generates critical contradiction."""
    symptoms = {
        "symptoms": [],
        "severity": 1,
        "notes": "Patient presents for routine workplace wellness checkup, reports feeling completely well.",
    }
    labs = {
        "systolic_bp": 174.0,
        "diastolic_bp": 104.0,
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-SUBJ-OBJ-003" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-SUBJ-OBJ-003")
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "silent killer" in issue.physiological_rationale.lower()


def test_rule_b1_statin_therapy_vs_extreme_ldl(detector: ContradictionDetector) -> None:
    """Test Rule B1: Active statin therapy with extreme LDL (>= 190 mg/dL) generates critical contradiction."""
    history = {
        "current_medications": [
            {"name": "Atorvastatin", "dosage": "40mg"},
            {"name": "Aspirin", "dosage": "81mg"},
        ],
    }
    labs = {
        "ldl_cholesterol_mg_dl": 204.0,  # extreme elevation >= 190
        "total_cholesterol_mg_dl": 290.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-MED-BIO-001" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-MED-BIO-001")
    assert issue.category == ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "atorvastatin" in issue.diverging_claims["Medical History Specialist"].lower()


def test_rule_b2_antihypertensives_vs_stage_2_hypertension(detector: ContradictionDetector) -> None:
    """Test Rule B2: Documented antihypertensive medications with persistent Stage 2 hypertension."""
    history = {
        "current_medications": [
            {"name": "Lisinopril", "dosage": "20mg"},
            {"name": "Amlodipine", "dosage": "5mg"},
        ],
    }
    labs = {
        "systolic_bp": 152.0,
        "diastolic_bp": 94.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-MED-BIO-002" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-MED-BIO-002")
    assert issue.category == ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER
    assert issue.severity == ContradictionSeverity.MODERATE


def test_rule_b3_antidiabetic_medications_vs_uncontrolled_glycemia(detector: ContradictionDetector) -> None:
    """Test Rule B3: Documented antidiabetic medications with HbA1c >= 8.5%."""
    history = {
        "current_medications": [{"name": "Metformin", "dosage": "1000mg twice daily"}],
    }
    labs = {
        "hba1c_percent": 9.4,
        "fasting_blood_glucose_mg_dl": 210.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-MED-BIO-003" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-MED-BIO-003")
    assert issue.category == ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER
    assert issue.severity == ContradictionSeverity.MODERATE


def test_rule_b4_denies_diabetes_vs_diagnostic_labs(detector: ContradictionDetector) -> None:
    """Test Rule B4: History reports no diabetes, yet HbA1c >= 6.5% and FPG >= 126 mg/dL."""
    history = {
        "chronic_conditions": ["hypertension", "osteoarthritis"],
        "current_medications": [{"name": "Amlodipine", "dosage": "5mg"}],
    }
    labs = {
        "fasting_blood_glucose_mg_dl": 145.0,
        "hba1c_percent": 7.2,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-MED-BIO-004" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-MED-BIO-004")
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "undiagnosed" in issue.physiological_rationale.lower()


def test_rule_c1_framingham_vs_ml_cvd_divergence(detector: ContradictionDetector) -> None:
    """Test Rule C1: Framingham CVD risk vs. ML CVD probability divergence >= 25%."""
    scores = {
        "framingham_risk_percent": 11.2,
        "framingham_risk_category": "moderate",
    }
    ml = {
        "cardiovascular_risk_percent": 41.5,
        "cardiovascular_risk_category": "high",
    }

    result = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-EQ-ML-001" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-EQ-ML-001")
    assert issue.category == ContradictionCategory.EQUATION_VS_ML_DISCORDANCE
    assert "11.2%" in issue.diverging_claims["Framingham Risk Equation"]
    assert "41.5%" in issue.diverging_claims["Machine Learning CVD Classifier"]


def test_rule_c2_findrisc_vs_ml_diabetes_discordance(detector: ContradictionDetector) -> None:
    """Test Rule C2: Low FINDRISC score (< 7) vs. High ML Diabetes probability (>= 40%)."""
    scores = {
        "findrisc_score": 5,
        "findrisc_risk_category": "low",
    }
    ml = {
        "diabetes_risk_percent": 46.2,
        "diabetes_risk_category": "high",
    }

    result = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-EQ-ML-002" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-EQ-ML-002")
    assert issue.category == ContradictionCategory.EQUATION_VS_ML_DISCORDANCE
    assert issue.severity == ContradictionSeverity.MODERATE


def test_rule_d_qualitative_agent_findings(detector: ContradictionDetector) -> None:
    """Test Rule D: Qualitative conflict between symptom findings and medical history findings."""
    agent_outputs = [
        AgentOutputResponse(
            agent_role="Symptom Analysis Specialist",
            findings="Patient exhibits chronic exertional dyspnea consistent with significant smoking history and COPD exacerbation.",
            confidence=85.0,
        ),
        AgentOutputResponse(
            agent_role="Medical History Specialist",
            findings="Comprehensive history confirms patient is a verified lifelong never smoker with no environmental exposures.",
            confidence=90.0,
        ),
    ]

    result = detector.evaluate_contradictions(agent_outputs=agent_outputs)

    assert result.contradictions_detected is True
    assert any(i.issue_id == "ISSUE-QUAL-001" for i in result.issues)
    issue = next(i for i in result.issues if i.issue_id == "ISSUE-QUAL-001")
    assert issue.category == ContradictionCategory.QUALITATIVE_CLAIM_DISCORDANCE
    assert issue.severity == ContradictionSeverity.MINOR


def test_completely_concordant_scenario(detector: ContradictionDetector) -> None:
    """Test fully concordant scenario produces zero contradictions and 0.0 epistemic doubt."""
    symptoms = {
        "symptoms": ["chest_pain"],
        "severity": 4,
        "notes": "Mild non-exertional chest twinge after heavy meals.",
    }
    history = {
        "chronic_conditions": [],
        "current_medications": [],
    }
    labs = {
        "systolic_bp": 118.0,
        "diastolic_bp": 76.0,
        "total_cholesterol_mg_dl": 175.0,
        "ldl_cholesterol_mg_dl": 98.0,
        "fasting_blood_glucose_mg_dl": 90.0,
        "hba1c_percent": 5.2,
    }
    scores = {
        "framingham_risk_percent": 4.5,
        "framingham_risk_category": "low",
        "findrisc_score": 4,
        "findrisc_risk_category": "low",
    }
    ml = {
        "cardiovascular_risk_percent": 6.2,
        "cardiovascular_risk_category": "low",
        "diabetes_risk_percent": 5.0,
        "diabetes_risk_category": "low",
    }

    result = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        medical_history_data=history,
        laboratory_data=labs,
        clinical_scores=scores,
        ml_predictions=ml,
    )

    assert result.contradictions_detected is False
    assert result.total_contradictions == 0
    assert result.critical_count == 0
    assert result.moderate_count == 0
    assert result.minor_count == 0
    assert result.preliminary_epistemic_doubt == 0.0
    assert "Concordant" in result.summary


def test_epistemic_doubt_capped_at_one(detector: ContradictionDetector) -> None:
    """Test that preliminary epistemic doubt cannot exceed 1.0 even with multiple critical issues."""
    # Create compound multi-critical conflict
    symptoms = {"symptoms": ["chest_pain"], "severity": 9}
    labs = {
        "cardiac_troponin_ng_ml": 0.01,
        "resting_ecg": "normal_sinus_rhythm",
        "ldl_cholesterol_mg_dl": 220.0,
        "systolic_bp": 170.0,
        "diastolic_bp": 105.0,
        "fasting_blood_glucose_mg_dl": 150.0,
        "hba1c_percent": 7.5,
    }
    history = {
        "current_medications": [{"name": "Atorvastatin"}, {"name": "Lisinopril"}],
        "chronic_conditions": [],  # denies diabetes
    }
    scores = {"framingham_risk_percent": 10.0, "framingham_risk_category": "low"}
    ml = {"cardiovascular_risk_percent": 55.0, "cardiovascular_risk_category": "high"}

    result = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        medical_history_data=history,
        laboratory_data=labs,
        clinical_scores=scores,
        ml_predictions=ml,
    )

    assert result.contradictions_detected is True
    assert result.critical_count >= 3
    assert 0.0 <= result.preliminary_epistemic_doubt <= 1.0
