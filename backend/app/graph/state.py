"""Typed state definition for MedOracle LangGraph multi-agent orchestration (Step 11).

Defines the shared, immutable-reduction state passed between asynchronous agent nodes.
"""

from datetime import datetime, timezone
import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class ClinicalAgentState(TypedDict, total=False):
    """Shared state dictionary tracked and updated across LangGraph workflow nodes."""

    session_id: str
    user_id: Optional[str]

    # Raw Clinical Context Inputs
    patient_demographics: Dict[str, Any]
    symptoms_data: Dict[str, Any]
    medical_history_data: Dict[str, Any]
    laboratory_data: Dict[str, Any]
    clinical_scores: Dict[str, Any]
    ml_predictions: Dict[str, Any]

    # Execution & Telemetry Controls
    provider: Optional[str]
    use_cache: bool

    # Domain Specialist Agent Outputs (State mapping)
    symptom_output: Optional[Dict[str, Any]]
    medical_history_output: Optional[Dict[str, Any]]
    laboratory_output: Optional[Dict[str, Any]]
    risk_prediction_output: Optional[Dict[str, Any]]

    # Universal Accumulators (appends via operator.add reducer)
    agent_outputs: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]

    # Workflow Status Tracking
    current_phase: str
    status: str
    completed_at: Optional[str]


def create_initial_graph_state(
    patient_demographics: Optional[Dict[str, Any]] = None,
    symptoms_data: Optional[Dict[str, Any]] = None,
    medical_history_data: Optional[Dict[str, Any]] = None,
    laboratory_data: Optional[Dict[str, Any]] = None,
    clinical_scores: Optional[Dict[str, Any]] = None,
    ml_predictions: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    provider: Optional[str] = None,
    use_cache: bool = True,
) -> ClinicalAgentState:
    """Helper factory constructing a sanitized initial state for LangGraph execution."""
    return {
        "session_id": session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "user_id": user_id,
        "patient_demographics": patient_demographics or {},
        "symptoms_data": symptoms_data or {},
        "medical_history_data": medical_history_data or {},
        "laboratory_data": laboratory_data or {},
        "clinical_scores": clinical_scores or {},
        "ml_predictions": ml_predictions or {},
        "provider": provider,
        "use_cache": use_cache,
        "symptom_output": None,
        "medical_history_output": None,
        "laboratory_output": None,
        "risk_prediction_output": None,
        "agent_outputs": [],
        "errors": [],
        "warnings": [],
        "current_phase": "initialization",
        "status": "pending",
        "completed_at": None,
    }
