"""Comprehensive Unit tests for the Contradiction Detection Engine (Sub-Step 12.1).

Validates:
1. Rule A1: Acute ischemia vs. normal troponin/ECG (early vs. serial timing, unstable angina caveats)
2. Rule A2: Severe dyspnea vs. natriuretic peptides (BNP vs NT-proBNP assay cutoffs, obesity/eGFR confounders)
3. Rule A3: Asymptomatic presentation vs. Stage 2 HTN vs. Hypertensive Urgency vs. Glucotoxicity
4. Rule B1: Statin therapy vs. LDL-C (therapeutic latency < 6 weeks, non-adherence, baseline reduction)
5. Rule B2: Antihypertensive therapy vs. Blood pressure (latency, single reading limitations, non-adherence)
6. Rule B3: Antidiabetic therapy vs. Glycemia (2-3 month HbA1c turnover lag, individualized targets)
7. Rule B4: Undiagnosed diabetes (ADA 2026 confirmed dual-marker vs. provisional single-marker)
8. Rules C1 & C2: Quantitative model comparisons (Framingham vs. UCI ML CAD, FINDRISC vs. PIMA, INCOMPARABLE_PREDICTIONS)
9. Missing laboratory measurements (troponin=None or BNP=None is UNTESTED, not normal)
10. Measurement timestamps & temporal qualification
11. Duplicate contradiction detection & deduplicated doubt scoring
12. Repeated patient analysis session collision-free issue IDs
13. Qualitative contradiction category behavior (unimplemented_deferred_to_12_2)
14. Completely concordant scenarios
15. Doubt score mathematical bounds [0.0, 1.0]
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
    return ContradictionDetector(default_disagreement_threshold=25.0)


# =============================================================================
# Dimension 1: Subjective vs. Objective Tests
# =============================================================================

def test_rule_a1_adequate_timeframe_normal_troponin_ecg(detector: ContradictionDetector) -> None:
    """Test Rule A1: Acute severe ischemic chest pain with symptoms >= 24h and normal troponin/ECG generates critical contradiction."""
    symptoms = {
        "symptoms": ["chest_pain", "substernal_pressure", "radiating_chest_pain"],
        "severity": 8,
        "duration_days": 2,
        "duration_hours": 48.0,
        "notes": "Severe crushing substernal chest pressure radiating to the left jaw.",
    }
    labs = {
        "cardiac_troponin_ng_ml": 0.01,
        "cardiac_troponin_assay": "hs_cTnI",
        "serial_troponin_completed": True,
        "resting_ecg": "normal_sinus_rhythm",
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    assert any("SUBJ-OBJ-001" in i.issue_id for i in result.issues)
    issue = next(i for i in result.issues if "SUBJ-OBJ-001" in i.issue_id)
    assert issue.rule_id == "RULE-A1-ISCHEMIA-TROPONIN"
    assert issue.category == ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert issue.is_confirmed_contradiction is True
    assert "troponin" in issue.physiological_rationale.lower()
    assert len(issue.clinical_limitations) >= 2


def test_rule_a1_early_presentation_not_definitive_contradiction(detector: ContradictionDetector) -> None:
    """Test Rule A1: Early normal troponin (< 6h) without serial testing is provisional/moderate, not definitive."""
    symptoms = {
        "symptoms": ["chest_pain"],
        "severity": 8,
        "duration_hours": 2.5,  # early presentation (< 6 hours)
        "notes": "Sudden onset chest pain started 2.5 hours ago.",
    }
    labs = {
        "cardiac_troponin_ng_ml": 0.01,  # initial normal
        "serial_troponin_completed": False,  # serial NOT yet done
        "resting_ecg": "normal_sinus_rhythm",
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "SUBJ-OBJ-001" in i.issue_id)
    assert issue.severity == ContradictionSeverity.MODERATE
    assert issue.is_confirmed_contradiction is False
    assert any("serial" in lim.lower() for lim in issue.clinical_limitations)
    assert "cannot definitively rule out evolving" in issue.physiological_rationale


def test_missing_troponin_never_treated_as_normal(detector: ContradictionDetector) -> None:
    """Test that missing laboratory measurements (troponin=None) are NOT treated as normal and do not trigger false contradiction."""
    symptoms = {
        "symptoms": ["chest_pain"],
        "severity": 8,
        "duration_days": 1,
    }
    labs = {
        "cardiac_troponin_ng_ml": None,  # untested
        "resting_ecg": "normal_sinus_rhythm",
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    # Missing troponin should NOT trigger RULE-A1-ISCHEMIA-TROPONIN
    assert not any(i.rule_id == "RULE-A1-ISCHEMIA-TROPONIN" for i in result.issues)


def test_rule_a2_severe_dyspnea_vs_normal_bnp(detector: ContradictionDetector) -> None:
    """Test Rule A2: Severe acute dyspnea with normal BNP (< 100 pg/mL) generates moderate contradiction with HFpEF/obesity caveats."""
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
    issue = next(i for i in result.issues if "SUBJ-OBJ-002" in i.issue_id)
    assert issue.rule_id == "RULE-A2-DYSPNEA-BNP"
    assert issue.severity == ContradictionSeverity.MODERATE
    assert "BNP" in issue.diverging_claims["Laboratory Biomarker Specialist"]
    assert any("obesity" in lim.lower() for lim in issue.clinical_limitations)


def test_rule_a2_nt_probnp_assay_cutoff_applied(detector: ContradictionDetector) -> None:
    """Test Rule A2: Distinguishes NT-proBNP from BNP and applies 300 pg/mL rule-out threshold."""
    symptoms = {
        "symptoms": ["dyspnea"],
        "severity": 7,
    }
    labs = {
        "nt_pro_bnp_pg_ml": 180.0,  # Normal for NT-proBNP (< 300 pg/mL)
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "SUBJ-OBJ-002" in i.issue_id)
    assert "NT-proBNP" in issue.diverging_claims["Laboratory Biomarker Specialist"]


def test_rule_a3_asymptomatic_stage_2_hypertension(detector: ContradictionDetector) -> None:
    """Test Rule A3: Asymptomatic patient with Stage 2 hypertension (SBP 174/104) uses accurate clinical terminology."""
    symptoms = {
        "symptoms": [],
        "severity": 1,
        "notes": "Patient presents for routine wellness checkup, reports feeling completely well.",
    }
    labs = {
        "systolic_bp": 174.0,
        "diastolic_bp": 104.0,
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "SUBJ-OBJ-003" in i.issue_id)
    assert issue.rule_id == "RULE-A3-ASYMPTOMATIC-HTN"
    assert issue.severity == ContradictionSeverity.MODERATE
    assert "Stage 2 Hypertension" in issue.diverging_claims["Laboratory Biomarker Specialist"]
    assert "silent killer" in issue.physiological_rationale.lower()


def test_rule_a3_asymptomatic_hypertensive_urgency_level(detector: ContradictionDetector) -> None:
    """Test Rule A3: Asymptomatic patient with BP >= 180/120 flags Hypertensive Urgency (Critical) without target-organ damage."""
    symptoms = {
        "symptoms": [],
        "severity": 1,
    }
    labs = {
        "systolic_bp": 186.0,
        "diastolic_bp": 122.0,
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "SUBJ-OBJ-003" in i.issue_id)
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "Urgency" in issue.diverging_claims["Laboratory Biomarker Specialist"]


def test_rule_a3_asymptomatic_severe_glucotoxicity(detector: ContradictionDetector) -> None:
    """Test Rule A3: Separates asymptomatic hyperglycemia from hypertension as distinct clinical finding."""
    symptoms = {
        "symptoms": [],
        "severity": 1,
    }
    labs = {
        "fasting_blood_glucose_mg_dl": 280.0,
        "hba1c_percent": 11.2,
    }

    result = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "SUBJ-OBJ-004" in i.issue_id)
    assert issue.rule_id == "RULE-A3-ASYMPTOMATIC-GLUCOSE"
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "glucotoxicity" in issue.physiological_rationale.lower()


# =============================================================================
# Dimension 2: Medication vs. Biomarkers Tests
# =============================================================================

def test_rule_b1_statin_therapy_chronic_adherence_vs_extreme_ldl(detector: ContradictionDetector) -> None:
    """Test Rule B1: Chronic adherent statin therapy with extreme LDL (>= 190 mg/dL) generates critical contradiction."""
    history = {
        "current_medications": [
            {
                "name": "Atorvastatin",
                "dosage": "40mg",
                "treatment_duration_weeks": 24,
                "adherence": "consistent",
            },
        ],
    }
    labs = {
        "ldl_cholesterol_mg_dl": 204.0,  # >= 190
        "total_cholesterol_mg_dl": 290.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "MED-BIO-001" in i.issue_id)
    assert issue.rule_id == "RULE-B1-STATIN-LDL"
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert "atorvastatin" in issue.diverging_claims["Medical History Specialist"].lower()
    assert issue.is_confirmed_contradiction is True


def test_rule_b1_newly_initiated_statin_not_contradiction(detector: ContradictionDetector) -> None:
    """Test Rule B1: Statin newly initiated < 6 weeks has expected therapeutic latency and does not flag contradiction."""
    history = {
        "current_medications": [
            {
                "name": "Atorvastatin",
                "dosage": "20mg",
                "treatment_duration_weeks": 2,  # newly initiated (< 6 weeks)
            },
        ],
    }
    labs = {
        "ldl_cholesterol_mg_dl": 204.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert not any(i.rule_id == "RULE-B1-STATIN-LDL" for i in result.issues)


def test_rule_b1_documented_non_adherence_downgrades_severity(detector: ContradictionDetector) -> None:
    """Test Rule B1: When patient history documents non-adherence, severity is moderate and explains non-compliance."""
    history = {
        "current_medications": [
            {
                "name": "Atorvastatin",
                "dosage": "40mg",
                "treatment_duration_weeks": 16,
                "adherence": "inconsistent",
            },
        ],
        "notes": "Patient admits inconsistent statin compliance and frequently forgets doses.",
    }
    labs = {
        "ldl_cholesterol_mg_dl": 195.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "MED-BIO-001" in i.issue_id)
    assert issue.severity == ContradictionSeverity.MODERATE
    assert "non-adherence" in issue.physiological_rationale.lower()


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
    issue = next(i for i in result.issues if "MED-BIO-002" in i.issue_id)
    assert issue.rule_id == "RULE-B2-ANTIHYPERTENSIVE-BP"
    assert issue.severity == ContradictionSeverity.MODERATE
    assert any("white-coat" in lim.lower() for lim in issue.clinical_limitations)


def test_rule_b3_antidiabetic_medications_vs_uncontrolled_glycemia(detector: ContradictionDetector) -> None:
    """Test Rule B3: Documented antidiabetic medications with HbA1c >= 8.5% accounts for 2-3 month turnover lag."""
    history = {
        "current_medications": [{"name": "Metformin", "dosage": "1000mg twice daily"}],
    }
    labs = {
        "hba1c_percent": 9.4,
        "fasting_blood_glucose_mg_dl": 210.0,
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "MED-BIO-003" in i.issue_id)
    assert issue.rule_id == "RULE-B3-ANTIDIABETIC-HBA1C"
    assert issue.severity == ContradictionSeverity.MODERATE
    assert any("2 to 3 months" in lim for lim in issue.clinical_limitations)


def test_rule_b4_undiagnosed_diabetes_confirmed_dual_marker(detector: ContradictionDetector) -> None:
    """Test Rule B4: Denies diabetes + concordant FPG >= 126 AND HbA1c >= 6.5 confirms diagnosis per ADA 2026."""
    history = {
        "chronic_conditions": ["hypertension"],  # denies diabetes
        "current_medications": [],
    }
    labs = {
        "fasting_blood_glucose_mg_dl": 145.0,  # >= 126
        "hba1c_percent": 7.2,                  # >= 6.5
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "MED-BIO-004" in i.issue_id)
    assert issue.rule_id == "RULE-B4-UNDIAGNOSED-DIABETES"
    assert issue.severity == ContradictionSeverity.CRITICAL
    assert issue.is_confirmed_contradiction is True
    assert "concordant" in issue.physiological_rationale.lower()


def test_rule_b4_undiagnosed_diabetes_provisional_single_marker(detector: ContradictionDetector) -> None:
    """Test Rule B4: Denies diabetes + single abnormal marker flags provisional dysglycemia requiring repeat testing per ADA."""
    history = {
        "chronic_conditions": [],
        "current_medications": [],
    }
    labs = {
        "fasting_blood_glucose_mg_dl": 138.0,  # >= 126
        "hba1c_percent": None,                 # not tested
    }

    result = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "MED-BIO-004" in i.issue_id)
    assert issue.severity == ContradictionSeverity.MODERATE
    assert issue.is_confirmed_contradiction is False
    assert "provisional dysglycemia" in issue.physiological_rationale.lower()
    assert any("repeat confirmatory" in lim.lower() for lim in issue.clinical_limitations)


# =============================================================================
# Dimension 3: Quantitative Model Comparisons & Incomparable Horizons
# =============================================================================

def test_rule_c1_framingham_vs_uci_ml_horizon_disparity(detector: ContradictionDetector) -> None:
    """Test Rule C1: Framingham 10-Yr incident CVD vs. UCI cross-sectional angiographic CAD flags INCOMPARABLE_PREDICTIONS."""
    scores = {
        "framingham_risk_percent": 11.2,
        "framingham_risk_category": "moderate",
        "target_outcome": "10_year_incident_cvd",
        "prediction_horizon": "10_years",
    }
    ml = {
        "cardiovascular_risk_percent": 41.5,
        "cardiovascular_risk_category": "high",
        "target_outcome": "cross_sectional_angiographic_cad",
        "prediction_horizon": "cross_sectional",
    }

    result = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml)

    assert result.contradictions_detected is True
    issue = next(i for i in result.issues if "EQ-ML-001" in i.issue_id)
    assert issue.rule_id == "RULE-C1-FRAMINGHAM-UCI-HORIZON"
    assert issue.category == ContradictionCategory.INCOMPARABLE_PREDICTIONS
    assert issue.severity == ContradictionSeverity.MODERATE
    assert issue.is_confirmed_contradiction is False
    assert "Methodological Horizon & Endpoint Disparity" in issue.physiological_rationale

    # Verify model comparisons audit record
    assert len(result.model_comparisons) >= 1
    comp = result.model_comparisons[0]
    assert comp["status"] == "INCOMPARABLE_PREDICTIONS"
    assert comp["disparity_gap_pct"] == 30.3


def test_rule_c2_findrisc_vs_pima_diabetes_incomparable(detector: ContradictionDetector) -> None:
    """Test Rule C2: FINDRISC 10-Yr incident diabetes vs. PIMA cross-sectional presence flags INCOMPARABLE_PREDICTIONS."""
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
    issue = next(i for i in result.issues if "EQ-ML-002" in i.issue_id)
    assert issue.rule_id == "RULE-C2-FINDRISC-PIMA-HORIZON"
    assert issue.category == ContradictionCategory.INCOMPARABLE_PREDICTIONS


def test_configurable_disagreement_threshold(detector: ContradictionDetector) -> None:
    """Test that equation vs ML comparison respects configurable heuristic threshold."""
    # When threshold is set high (50%), a 30% gap in compatible models does NOT trigger
    scores = {
        "framingham_risk_percent": 15.0,
        "target_outcome": "10_year_incident_cvd",
        "prediction_horizon": "10_years",
    }
    ml = {
        "cardiovascular_risk_percent": 40.0,  # 25% gap
        "target_outcome": "10_year_incident_cvd",  # compatible target
        "prediction_horizon": "10_years",
    }

    # At threshold 30.0, 25.0% gap does not trigger
    result = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml, disagreement_threshold=30.0)
    assert not any(i.rule_id == "RULE-C1-COMPATIBLE-GAP" for i in result.issues)

    # At threshold 20.0, 25.0% gap triggers
    result_triggered = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml, disagreement_threshold=20.0)
    assert any(i.rule_id == "RULE-C1-COMPATIBLE-GAP" for i in result_triggered.issues)


# =============================================================================
# Provenance, Traceability, Deduplication, and System Integrity Tests
# =============================================================================

def test_session_id_traceability_and_collision_proof_ids(detector: ContradictionDetector) -> None:
    """Test that session_id and patient_id propagate to all issues and result in unique traceable IDs."""
    symptoms = {"symptoms": ["chest_pain"], "severity": 8, "duration_hours": 48.0}
    labs = {"cardiac_troponin_ng_ml": 0.01, "serial_troponin_completed": True}

    res1 = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        laboratory_data=labs,
        session_id="session_ALPHA",
        patient_id="patient_101",
    )
    res2 = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        laboratory_data=labs,
        session_id="session_BETA",
        patient_id="patient_102",
    )

    issue1 = res1.issues[0]
    issue2 = res2.issues[0]

    assert issue1.session_id == "session_ALPHA"
    assert issue1.patient_id == "patient_101"
    assert issue2.session_id == "session_BETA"
    assert issue2.patient_id == "patient_102"
    assert issue1.issue_id != issue2.issue_id  # collision-proof across sessions!
    assert "session_ALPHA" in issue1.issue_id
    assert "session_BETA" in issue2.issue_id


def test_deduplicated_doubt_score_prevents_inflation(detector: ContradictionDetector) -> None:
    """Test that preliminary epistemic doubt score deduplicates co-dependent issues in the same clinical domain."""
    # Two blood pressure issues (one from symptom vs lab, one from med vs lab) belong to hemodynamic domain
    history = {
        "current_medications": [{"name": "Lisinopril", "treatment_duration_weeks": 20}],
    }
    symptoms = {"symptoms": [], "severity": 1}
    labs = {"systolic_bp": 170.0, "diastolic_bp": 105.0}

    result = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        medical_history_data=history,
        laboratory_data=labs,
    )

    # 2 issues detected (RULE-A3 and RULE-B2)
    assert result.total_contradictions == 2
    # Both are hemodynamic domain (Moderate = 0.12). Deduplication scores only once!
    assert result.preliminary_epistemic_doubt == 0.12


def test_qualitative_category_unimplemented_status(detector: ContradictionDetector) -> None:
    """Test that qualitative claim discordance is documented as unimplemented deferred to 12.2."""
    result = detector.evaluate_contradictions()
    assert result.category_statuses["qualitative_claim_discordance"] == "unimplemented_deferred_to_12_2"


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
    """Test that preliminary epistemic doubt cannot exceed 1.0 even with multiple critical issues across distinct domains."""
    symptoms = {"symptoms": ["chest_pain"], "severity": 9, "duration_hours": 48.0}
    labs = {
        "cardiac_troponin_ng_ml": 0.01,
        "serial_troponin_completed": True,
        "resting_ecg": "normal_sinus_rhythm",
        "ldl_cholesterol_mg_dl": 220.0,
        "systolic_bp": 185.0,
        "diastolic_bp": 125.0,
        "fasting_blood_glucose_mg_dl": 150.0,
        "hba1c_percent": 7.5,
    }
    history = {
        "current_medications": [
            {"name": "Atorvastatin", "treatment_duration_weeks": 20},
            {"name": "Lisinopril", "treatment_duration_weeks": 20},
        ],
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
    assert 0.0 <= result.preliminary_epistemic_doubt <= 1.0
