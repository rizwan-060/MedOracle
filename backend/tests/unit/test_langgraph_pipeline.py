"""Unit tests for MedOracle LangGraph Multi-Agent Orchestration Pipeline (Step 11)."""

import pytest
from langgraph.graph.state import CompiledStateGraph

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
    assert final_state["current_phase"] == "risk_prediction_completed"
    assert final_state["completed_at"] is not None
    assert final_state["symptom_output"] is not None
    assert final_state["medical_history_output"] is not None
    assert final_state["laboratory_output"] is not None
    assert final_state["risk_prediction_output"] is not None

    # Reducer accumulated all 4 outputs
    assert len(final_state["agent_outputs"]) == 4
    roles = {out["agent_role"] for out in final_state["agent_outputs"]}
    assert "Symptom Analysis Specialist" in roles
    assert "Medical History Specialist" in roles
    assert "Laboratory Biomarker Specialist" in roles
    assert "Risk Prediction Ensemble Specialist" in roles
