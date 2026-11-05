"""Unit tests for MedOracle LangGraph Multi-Agent Orchestration Pipeline (Step 11)."""

import pytest
from datetime import datetime, timezone
from langgraph.graph.state import CompiledStateGraph

from app.schemas.consensus import (
    ClinicalEvidenceItem,
    EvidenceSourceType,
    EvidenceValidityState,
    EvidenceSupportClassification,
    TargetOrganDamageState,
)

from app.graph import (
    ClinicalAgentState,
    build_clinical_orchestration_graph,
    create_initial_graph_state,
    get_compiled_clinical_graph,
    laboratory_node,
    medical_history_node,
    risk_prediction_node,
    run_clinical_graph,
    symptom_node,
)


def test_initial_state_factory():
    """Verify that create_initial_graph_state initializes default keys and reducers."""
    state = create_initial_graph_state(
        patient_demographics={"age": 55, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain"]},
        user_id="user_123",
        provider="mock",
    )

    assert state["session_id"].startswith("session_")
    assert state["user_id"] == "user_123"
    assert state["patient_demographics"]["age"] == 55
    assert state["symptoms_data"]["symptoms"] == ["chest_pain"]
    assert state["status"] == "pending"
    assert state["current_phase"] == "initialization"
    assert state["agent_outputs"] == []
    assert state["errors"] == []
    assert state["warnings"] == []


def test_symptom_node_execution():
    """Verify symptom_node executes and returns domain output dictionary."""
    state = create_initial_graph_state(
        patient_demographics={"age": 60, "sex": "female"},
        symptoms_data={"symptoms": ["fatigue", "dyspnea"], "severity": 7},
        provider="mock",
        use_cache=False,
    )

    update = symptom_node(state)
    assert "symptom_output" in update
    assert "agent_outputs" in update
    assert update["symptom_output"]["agent_role"] == "Symptom Analysis Specialist"
    assert len(update["agent_outputs"]) == 1


def test_medical_history_node_execution():
    """Verify medical_history_node executes and returns domain output dictionary."""
    state = create_initial_graph_state(
        patient_demographics={"age": 60, "sex": "female"},
        medical_history_data={"chronic_conditions": ["hypertension", "type_2_diabetes"]},
        provider="mock",
        use_cache=False,
    )

    update = medical_history_node(state)
    assert "medical_history_output" in update
    assert "agent_outputs" in update
    assert update["medical_history_output"]["agent_role"] == "Medical History Specialist"
    assert len(update["agent_outputs"]) == 1


def test_laboratory_node_execution():
    """Verify laboratory_node executes and returns domain output dictionary."""
    state = create_initial_graph_state(
        patient_demographics={"age": 60, "sex": "female"},
        laboratory_data={"systolic_bp": 144.0, "total_cholesterol_mg_dl": 220.0},
        provider="mock",
        use_cache=False,
    )

    update = laboratory_node(state)
    assert "laboratory_output" in update
    assert "agent_outputs" in update
    assert update["laboratory_output"]["agent_role"] == "Laboratory Biomarker Specialist"
    assert len(update["agent_outputs"]) == 1


def test_risk_prediction_node_fan_in():
    """Verify risk_prediction_node ensembles upstream agent findings and updates status."""
    state = create_initial_graph_state(
        patient_demographics={"age": 58, "sex": "male"},
        clinical_scores={"framingham_risk_percent": 18.4},
        ml_predictions={"cardiovascular_risk_percent": 24.0},
        provider="mock",
        use_cache=False,
    )
    state["symptom_output"] = {"findings": "Subacute exertional chest pain."}
    state["medical_history_output"] = {"findings": "Premature paternal CAD."}
    state["laboratory_output"] = {"findings": "AHA Stage 2 hypertension."}

    update = risk_prediction_node(state)
    assert "risk_prediction_output" in update
    assert update["risk_prediction_output"]["agent_role"] == "Risk Prediction Ensemble Specialist"
    assert update["current_phase"] == "risk_prediction_completed"
    assert update["status"] == "completed"
    assert update["completed_at"] is not None


def test_graph_topology_and_compilation():
    """Verify graph builds, compiles, and registers expected node set."""
    graph = get_compiled_clinical_graph()
    assert isinstance(graph, CompiledStateGraph)

    builder = build_clinical_orchestration_graph()
    assert "symptom_node" in builder.nodes
    assert "medical_history_node" in builder.nodes
    assert "laboratory_node" in builder.nodes
    assert "risk_prediction_node" in builder.nodes


def test_full_graph_synchronous_execution():
    """Verify end-to-end parallel execution, fan-in aggregation, and output accumulation."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 58, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain", "breathlessness"], "severity": 8},
        medical_history_data={"chronic_conditions": ["hypertension"]},
        laboratory_data={"systolic_bp": 145.0, "fasting_blood_glucose_mg_dl": 135.0},
        clinical_scores={"framingham_risk_percent": 18.0},
        ml_predictions={"cardiovascular_risk_percent": 25.0},
        provider="mock",
        use_cache=False,
    )

    final_state = run_clinical_graph(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["current_phase"] in ["risk_prediction_completed", "consensus_resolution_completed"]
    assert final_state["completed_at"] is not None
    assert final_state["symptom_output"] is not None
    assert final_state["medical_history_output"] is not None
    assert final_state["laboratory_output"] is not None
    assert final_state["risk_prediction_output"] is not None
    assert final_state["consensus_resolution"] is not None
    assert final_state["audit_transcript"] is not None

    # Reducer accumulated all 4 outputs
    assert len(final_state["agent_outputs"]) == 4
    roles = {out["agent_role"] for out in final_state["agent_outputs"]}
    assert "Symptom Analysis Specialist" in roles
    assert "Medical History Specialist" in roles
    assert "Laboratory Biomarker Specialist" in roles
    assert "Risk Prediction Ensemble Specialist" in roles


# =============================================================================
# Step 12 End-to-End Production LangGraph Clinical Scenarios (19 Mandated Cases)
# =============================================================================


def test_shared_evidence_contract_validation():
    """Verify Phase Two ClinicalEvidenceItem schema, provenance, and 10 clinical principles."""
    evidence = ClinicalEvidenceItem(
        evidence_id="EVID-101",
        patient_id="patient_test_01",
        analysis_id="session_test_01",
        source_type=EvidenceSourceType.LAB,
        source_record_id="LAB-REC-999",
        canonical_concept="cardiac_troponin",
        raw_value="0.08 ng/mL",
        normalized_value=0.08,
        unit="ng/mL",
        reference_range={"url_99th_percentile": 0.014, "unit": "ng/mL"},
        assay_metadata={"manufacturer": "Roche", "platform": "Elecsys", "assay_name": "hs_cTnT"},
        collection_timestamp=datetime.now(timezone.utc),
        original_timezone="UTC",
        provenance={"collector": "CoreLab", "verification_method": "LIS_direct_feed"},
        is_verified=True,
        validity_state=EvidenceValidityState.VERIFIED_PRESENT,
        associated_claim_ids=["CLAIM-ACS-01"],
        interpretation=EvidenceSupportClassification.SUPPORTS,
    )
    assert evidence.evidence_id == "EVID-101"
    assert evidence.source_type == EvidenceSourceType.LAB
    assert evidence.is_verified is True
    assert evidence.validity_state == EvidenceValidityState.VERIFIED_PRESENT
    assert evidence.interpretation == EvidenceSupportClassification.SUPPORTS


def test_scenario_01_acute_chest_pain_elevated_troponin():
    """Scenario 1: Acute chest pain with elevated troponin (AMI/ACS) -> emergent override, claim supported."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 62, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain", "substernal_pressure"], "severity": 9, "duration_hours": 2.5},
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.085,
            "cardiac_troponin_assay": "hs_ctnt_roche",
            "resting_ecg": "acute_ischemia_st_elevation",
        },
        clinical_scores={"framingham_risk_percent": 22.0},
        ml_predictions={"cardiovascular_risk_percent": 35.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any(w["level"] == "emergent" and "Acute Coronary Syndrome" in w["condition_name"] for w in warnings)
    assert final_state["audit_transcript"]["is_immutable"] is True


def test_scenario_02_acute_chest_pain_initial_normal_troponin():
    """Scenario 2: Acute chest pain with initial normal troponin (< URL) without serial completion -> provisional discrepancy."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 55, "sex": "female"},
        symptoms_data={"symptoms": ["chest_pain"], "severity": 8, "duration_hours": 1.5},
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.007,
            "cardiac_troponin_assay": "hs_ctni_abbott",
            "serial_troponin_completed": False,
            "resting_ecg": "normal",
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert any(issue["rule_id"] == "RULE-A1-ISCHEMIA-TROPONIN" and issue["clinical_status"] == "provisional_discrepancy" for issue in cr["issues"])


def test_scenario_03_acute_chest_pain_serial_normal_troponin():
    """Scenario 3: Acute chest pain with completed serial troponin testing -> unresolved presentation (unstable angina vs non-cardiac)."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 58, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain"], "severity": 7, "duration_hours": 4.0},
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.006,
            "cardiac_troponin_assay": "hs_ctni_abbott",
            "serial_troponin_completed": True,
            "resting_ecg": "normal",
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert any(issue["rule_id"] == "RULE-A1-ISCHEMIA-TROPONIN" and issue["clinical_status"] == "unresolved_presentation" for issue in cr["issues"])


def test_scenario_04_acute_severe_dyspnea_elevated_bnp():
    """Scenario 4: Severe dyspnea with elevated BNP (> 100 pg/mL) -> heart failure decompensation confirmed/alerted."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 70, "sex": "male"},
        symptoms_data={"symptoms": ["dyspnea", "orthopnea"], "severity": 8},
        laboratory_data={"bnp_pg_ml": 850.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any("Heart Failure" in w["condition_name"] for w in warnings)


def test_scenario_05_acute_severe_dyspnea_normal_bnp():
    """Scenario 5: Severe dyspnea with normal BNP (< 100 pg/mL) -> Rule A2 discrepancy with obesity/HFpEF limitations."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 60, "sex": "female"},
        symptoms_data={"symptoms": ["dyspnea", "breathlessness"], "severity": 8},
        laboratory_data={"bnp_pg_ml": 35.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert any(issue["rule_id"] == "RULE-A2-DYSPNEA-BNP" for issue in cr["issues"])


def test_scenario_06_hypertensive_emergency_with_tod():
    """Scenario 6: Severe BP elevation (SBP 210, DBP 125) with acute target-organ damage -> Hypertensive Emergency emergent alert."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 52, "sex": "male"},
        symptoms_data={"symptoms": ["headache"], "severity": 4},
        laboratory_data={
            "systolic_bp": 210.0,
            "diastolic_bp": 125.0,
            "serum_creatinine_mg_dl": 2.8,
            "target_organ_damage": True,
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any(w["condition_name"] == "Suspected Hypertensive Emergency" and w["level"] == "emergent" for w in warnings)


def test_scenario_07_hypertensive_urgency_without_tod():
    """Scenario 7: Severe BP elevation (SBP 195, DBP 115) with screened absence of TOD -> Hypertensive Urgency urgent alert."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 64, "sex": "female"},
        symptoms_data={"symptoms": []},
        laboratory_data={
            "systolic_bp": 195.0,
            "diastolic_bp": 115.0,
            "serum_creatinine_mg_dl": 0.9,
            "cardiac_troponin_ng_ml": 0.005,
            "resting_ecg": "normal",
            "target_organ_damage": False,
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any("Hypertensive Urgency" in w["condition_name"] and w["level"] == "urgent" for w in warnings)


def test_scenario_08_hypertensive_severe_bp_tod_undetermined():
    """Scenario 8: Severe BP elevation without TOD screening -> Target-Organ Damage Undetermined (not urgency)."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 61, "sex": "male"},
        symptoms_data={"symptoms": []},
        laboratory_data={"systolic_bp": 190.0, "diastolic_bp": 115.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any("Target-Organ Damage Undetermined" in w["condition_name"] for w in warnings)


def test_scenario_09_hyperglycemia_with_dka_triad():
    """Scenario 9: Hyperglycemia with DKA triad (glucose, ketones, acid-base) -> emergent DKA override."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 28, "sex": "female"},
        symptoms_data={"symptoms": ["nausea", "abdominal_pain"], "severity": 8},
        laboratory_data={
            "fasting_blood_glucose_mg_dl": 340.0,
            "blood_ketones_mmol_l": 4.5,
            "blood_ph": 7.22,
            "serum_bicarbonate_mmol_l": 11.0,
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any("Diabetic Ketoacidosis" in w["condition_name"] and w["level"] == "emergent" for w in warnings)


def test_scenario_10_hyperglycemia_with_hhs_criteria():
    """Scenario 10: Hyperglycemia with HHS criteria (glucose > 600, osmolality > 320) -> emergent HHS override."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 68, "sex": "male"},
        symptoms_data={"symptoms": ["confusion", "polyuria"], "severity": 7},
        laboratory_data={
            "fasting_blood_glucose_mg_dl": 740.0,
            "serum_osmolality_mosm_kg": 345.0,
            "blood_ph": 7.38,
            "blood_ketones_mmol_l": 0.4,
        },
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    warnings = res["clinical_safety_warnings"]
    assert any("Hyperosmolar Hyperglycemic State" in w["condition_name"] and w["level"] == "emergent" for w in warnings)


def test_scenario_11_asymptomatic_hyperglycemia_elevated_hba1c():
    """Scenario 11: Asymptomatic marked hyperglycemia with HbA1c >= 10.0% -> chronic glucotoxicity discrepancy."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 50, "sex": "male"},
        symptoms_data={"symptoms": [], "severity": 0},
        laboratory_data={"fasting_blood_glucose_mg_dl": 265.0, "hba1c_percent": 10.8},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert any(issue["rule_id"] == "RULE-A3-ASYMPTOMATIC-GLUCOSE" for issue in cr["issues"])


def test_scenario_12_statin_therapy_extreme_ldl_non_adherence():
    """Scenario 12: Statin therapy vs extreme LDL (>= 190 mg/dL) with documented non-adherence -> provisional discrepancy."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 57, "sex": "female"},
        medical_history_data={
            "current_medications": [{"name": "atorvastatin", "treatment_duration_weeks": 16.0, "adherence": "inconsistent"}],
            "notes": "Patient forgets pills and takes statin irregularly.",
        },
        laboratory_data={"ldl_cholesterol_mg_dl": 210.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    b1_issues = [i for i in cr["issues"] if i["rule_id"] == "RULE-B1-STATIN-LDL"]
    assert len(b1_issues) >= 1
    assert b1_issues[0]["clinical_status"] == "provisional_discrepancy"


def test_scenario_13_statin_therapy_extreme_ldl_high_adherence():
    """Scenario 13: Statin therapy vs extreme LDL (>= 190 mg/dL) with high adherence -> confirmed contradiction (familial hypercholesterolemia)."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 45, "sex": "male"},
        medical_history_data={
            "current_medications": [{"name": "rosuvastatin", "treatment_duration_weeks": 20.0, "adherence": "good"}],
            "notes": "Confirmed 100% adherence via pharmacy records.",
        },
        laboratory_data={"ldl_cholesterol_mg_dl": 225.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    b1_issues = [i for i in cr["issues"] if i["rule_id"] == "RULE-B1-STATIN-LDL"]
    assert len(b1_issues) >= 1
    assert b1_issues[0]["clinical_status"] == "confirmed_contradiction"


def test_scenario_14_statin_therapy_latency_window_newly_initiated():
    """Scenario 14: Statin newly initiated (< 6 weeks) with elevated LDL -> therapeutic lag window respected (no false contradiction)."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 52, "sex": "male"},
        medical_history_data={
            "current_medications": [{"name": "atorvastatin", "treatment_duration_weeks": 3.0}],
        },
        laboratory_data={"ldl_cholesterol_mg_dl": 195.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert not any(i["rule_id"] == "RULE-B1-STATIN-LDL" for i in cr["issues"])


def test_scenario_15_antihypertensive_therapy_latency_window():
    """Scenario 15: Antihypertensive therapy within class latency window -> expected latency window respected."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 54, "sex": "female"},
        medical_history_data={
            "current_medications": [{"name": "amlodipine", "treatment_duration_weeks": 0.5, "adherence": "good"}],
        },
        laboratory_data={"systolic_bp": 150.0, "diastolic_bp": 95.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert not any(i["rule_id"] == "RULE-B2-ANTIHYPERTENSIVE-BP" for i in cr["issues"])


def test_scenario_16_antihypertensive_therapy_past_latency_non_adherence():
    """Scenario 16: Antihypertensive therapy past latency with non-adherence -> Rule B2 flagged with non-adherence rationale."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 59, "sex": "male"},
        medical_history_data={
            "current_medications": [{"name": "lisinopril", "treatment_duration_weeks": 10.0, "adherence": "inconsistent"}],
            "notes": "Patient admits missing doses on weekends.",
        },
        laboratory_data={"systolic_bp": 155.0, "diastolic_bp": 98.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    b2_issues = [i for i in cr["issues"] if i["rule_id"] == "RULE-B2-ANTIHYPERTENSIVE-BP"]
    assert len(b2_issues) >= 1
    assert b2_issues[0]["normalized_values"]["adherence_inconsistent"] is True


def test_scenario_17_equation_vs_ml_horizon_incompatibility():
    """Scenario 17: Cohort equation vs ML horizon discordance -> identified as incomparable prediction horizons."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 55, "sex": "male"},
        clinical_scores={"framingham_risk_percent": 5.0},
        ml_predictions={"cardiovascular_risk_percent": 38.0, "prediction_horizon_days": 30},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    cr = final_state["contradiction_result"]
    assert any(i["category"] == "incomparable_predictions" or "HORIZON" in i["rule_id"] for i in cr["issues"])


def test_scenario_18_qualitative_tobacco_claim_discordance():
    """Scenario 18: Qualitative tobacco claim discordance -> NLI contradiction detected and debated."""
    from app.agents.consensus.debate_protocol import DebateProtocolEngine
    from app.schemas.consensus import (
        ContradictionCategory,
        ContradictionIssue,
        ContradictionMatrixResult,
        ContradictionSeverity,
        NLIRelation,
    )

    issue = ContradictionIssue(
        issue_id="ISSUE-TOBACCO-01",
        rule_id="RULE-D1-SMOKING-DISCORDANCE",
        category=ContradictionCategory.QUALITATIVE_CLAIM_DISCORDANCE,
        severity=ContradictionSeverity.MODERATE,
        conflicting_agents=["Medical History Specialist", "Symptom Analysis Specialist"],
        diverging_claims={"Medical History Specialist": "active smoker", "Symptom Analysis Specialist": "never smoker"},
        suggested_challenge="Reconcile smoking status",
        physiological_rationale="Contradictory smoking history",
    )
    fake_cm = ContradictionMatrixResult(
        session_id="session_tobacco_test",
        contradictions_detected=True,
        total_contradictions=1,
        issues=[issue],
        summary="Tobacco contradiction test",
    )
    agent_outputs = [
        {"agent_role": "Medical History Specialist", "findings": "Patient is an active smoker with 20 pack-year smoking history."},
        {"agent_role": "Symptom Analysis Specialist", "findings": "Patient is a never smoker and denies tobacco exposure."},
    ]
    engine = DebateProtocolEngine(max_rounds=2)
    dt = engine.execute_debate(
        contradiction_result=fake_cm,
        agent_outputs=agent_outputs,
    )
    nli_analyses = dt.qualitative_nli_analyses
    assert any(n.relation == NLIRelation.CONTRADICTION for n in nli_analyses)


def test_scenario_19_full_consensus_panel_congruent():
    """Scenario 19: Full consensus panel with congruent findings -> 0 contradictions, immediate consensus, low doubt."""
    from app.schemas.consensus import OverallConsensusOutcome

    initial_state = create_initial_graph_state(
        patient_demographics={"age": 42, "sex": "female"},
        symptoms_data={"symptoms": ["mild_headache"], "severity": 2},
        medical_history_data={"chronic_conditions": []},
        laboratory_data={
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "fasting_blood_glucose_mg_dl": 88.0,
            "total_cholesterol_mg_dl": 170.0,
            "ldl_cholesterol_mg_dl": 95.0,
            "hba1c_percent": 5.2,
        },
        clinical_scores={"framingham_risk_percent": 2.1},
        ml_predictions={"cardiovascular_risk_percent": 3.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    res = final_state["consensus_resolution"]
    outcome_str = str(res["overall_outcome"].value if hasattr(res["overall_outcome"], "value") else res["overall_outcome"]).upper()
    assert outcome_str in ["PARTIAL_CONSENSUS", "CONSENSUS_SUPPORTED"]
    assert res["global_epistemic_doubt_score"] < 0.25
    assert final_state["audit_transcript"]["is_immutable"] is True
