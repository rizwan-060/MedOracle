"""Node wrappers for MedOracle LangGraph multi-agent pipeline (Step 11).

Wraps each domain specialist agent in an asynchronous/synchronous node execution
with node-level error containment and state reducer compatibility.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional

from app.agents.laboratory_agent import LaboratoryAgent
from app.agents.medical_history_agent import MedicalHistoryAgent
from app.agents.risk_prediction_agent import RiskPredictionAgent
from app.agents.symptom_agent import SymptomAgent
from app.graph.state import ClinicalAgentState
from app.services.llm_service import LLMService

logger = logging.getLogger("graph.nodes")


def symptom_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Symptom Analysis Specialist Agent within the LangGraph workflow."""
    logger.info("Executing symptom_node for session: %s", state.get("session_id"))
    try:
        context: Dict[str, Any] = dict(state.get("symptoms_data") or {})

        # Enrich with demographics if available
        demo = state.get("patient_demographics") or {}
        if demo and "patient_demographics" not in context:
            context["patient_demographics"] = demo
            context.setdefault("age", demo.get("age"))
            context.setdefault("sex", demo.get("sex"))

        agent = SymptomAgent()
        output = agent.analyze(
            context=context,
            provider=state.get("provider"),
            use_cache=state.get("use_cache", True),
        )
        output_dict = output.model_dump()

        return {
            "symptom_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("symptom_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"SymptomAgent execution failure: {str(exc)}"],
            "warnings": ["Symptom domain analysis unavailable; proceeding with remaining clinical graph."],
        }


def medical_history_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Medical History Specialist Agent within the LangGraph workflow."""
    logger.info("Executing medical_history_node for session: %s", state.get("session_id"))
    try:
        context: Dict[str, Any] = dict(state.get("medical_history_data") or {})

        demo = state.get("patient_demographics") or {}
        if demo and "patient_demographics" not in context:
            context["patient_demographics"] = demo
            context.setdefault("age", demo.get("age"))
            context.setdefault("sex", demo.get("sex"))

        # Link active symptoms for cross-examination if available
        symptoms_data = state.get("symptoms_data") or {}
        if "active_symptoms" not in context and symptoms_data.get("symptoms"):
            context["active_symptoms"] = symptoms_data.get("symptoms")

        agent = MedicalHistoryAgent()
        output = agent.analyze(
            context=context,
            provider=state.get("provider"),
            use_cache=state.get("use_cache", True),
        )
        output_dict = output.model_dump()

        return {
            "medical_history_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("medical_history_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"MedicalHistoryAgent execution failure: {str(exc)}"],
            "warnings": ["Medical history domain analysis unavailable; proceeding with remaining clinical graph."],
        }


def laboratory_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Laboratory Biomarker Specialist Agent within the LangGraph workflow."""
    logger.info("Executing laboratory_node for session: %s", state.get("session_id"))
    try:
        context: Dict[str, Any] = dict(state.get("laboratory_data") or {})

        demo = state.get("patient_demographics") or {}
        if demo and "patient_demographics" not in context:
            context["patient_demographics"] = demo
            context.setdefault("age", demo.get("age"))
            context.setdefault("sex", demo.get("sex"))

        agent = LaboratoryAgent()
        output = agent.analyze(
            context=context,
            provider=state.get("provider"),
            use_cache=state.get("use_cache", True),
        )
        output_dict = output.model_dump()

        return {
            "laboratory_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("laboratory_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"LaboratoryAgent execution failure: {str(exc)}"],
            "warnings": ["Laboratory biomarker analysis unavailable; proceeding with remaining clinical graph."],
        }


def risk_prediction_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Risk Prediction Ensemble Specialist Agent within the LangGraph workflow.

    Synthesizes outputs from upstream domain agents (Symptom, Medical History, Laboratory)
    with deterministic risk calculators and trained machine learning predictions.
    """
    logger.info("Executing risk_prediction_node for session: %s", state.get("session_id"))
    try:
        symptom_out = state.get("symptom_output") or {}
        history_out = state.get("medical_history_output") or {}
        lab_out = state.get("laboratory_output") or {}

        agent_findings: Dict[str, Any] = {}
        if symptom_out.get("findings"):
            agent_findings["symptom_findings"] = symptom_out["findings"]
        if history_out.get("findings"):
            agent_findings["medical_history_findings"] = history_out["findings"]
        if lab_out.get("findings"):
            agent_findings["laboratory_findings"] = lab_out["findings"]

        context: Dict[str, Any] = {
            "patient_demographics": state.get("patient_demographics") or {},
            "clinical_scores": state.get("clinical_scores") or {},
            "ml_predictions": state.get("ml_predictions") or {},
            "agent_findings": agent_findings,
        }

        agent = RiskPredictionAgent()
        output = agent.analyze(
            context=context,
            provider=state.get("provider"),
            use_cache=state.get("use_cache", True),
        )
        output_dict = output.model_dump()

        return {
            "risk_prediction_output": output_dict,
            "agent_outputs": [output_dict],
            "current_phase": "risk_prediction_completed",
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.error("risk_prediction_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"RiskPredictionAgent execution failure: {str(exc)}"],
            "warnings": ["Risk prediction ensemble synthesis unavailable."],
            "status": "failed",
        }
