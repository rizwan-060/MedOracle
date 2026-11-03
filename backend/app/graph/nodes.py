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


def contradiction_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Contradiction Detection Engine within LangGraph (Step 12.1)."""
    logger.info("Executing contradiction_node for session: %s", state.get("session_id"))
    try:
        from app.agents.consensus.contradiction_detector import ContradictionDetector

        detector = ContradictionDetector()
        result = detector.evaluate_contradictions(
            symptoms_data=state.get("symptoms_data") or {},
            medical_history_data=state.get("medical_history_data") or {},
            laboratory_data=state.get("laboratory_data") or {},
            clinical_scores=state.get("clinical_scores") or {},
            ml_predictions=state.get("ml_predictions") or {},
            agent_outputs=state.get("agent_outputs") or [],
            session_id=state.get("session_id"),
            patient_id=state.get("user_id") or "anon",
        )
        return {
            "contradiction_result": result.model_dump(),
            "current_phase": "contradiction_detection_completed",
        }
    except Exception as exc:
        logger.error("contradiction_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"ContradictionDetector execution failure: {str(exc)}"],
            "warnings": ["Contradiction detection unavailable; proceeding with debate."],
        }


def debate_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Adversarial Debate Protocol within LangGraph (Step 12.2)."""
    logger.info("Executing debate_node for session: %s", state.get("session_id"))
    try:
        from app.agents.consensus.debate_protocol import DebateProtocolEngine
        from app.schemas.consensus import ContradictionMatrixResult

        engine = DebateProtocolEngine(max_rounds=2)
        raw_cm = state.get("contradiction_result")
        cm_obj = ContradictionMatrixResult(**raw_cm) if raw_cm else None

        transcript = engine.execute_debate(
            contradiction_result=cm_obj,
            agent_outputs=state.get("agent_outputs") or [],
            symptoms_data=state.get("symptoms_data") or {},
            medical_history_data=state.get("medical_history_data") or {},
            laboratory_data=state.get("laboratory_data") or {},
            clinical_scores=state.get("clinical_scores") or {},
            ml_predictions=state.get("ml_predictions") or {},
            session_id=state.get("session_id"),
            patient_id=state.get("user_id") or "anon",
        )
        return {
            "debate_transcript": transcript.model_dump(),
            "current_phase": "adversarial_debate_completed",
        }
    except Exception as exc:
        logger.error("debate_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"DebateProtocolEngine execution failure: {str(exc)}"],
            "warnings": ["Adversarial debate protocol unavailable; proceeding with recalibration."],
        }


def recalibration_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Confidence Recalibration Engine within LangGraph (Step 12.3)."""
    logger.info("Executing recalibration_node for session: %s", state.get("session_id"))
    try:
        from app.agents.consensus.recalibration import ConfidenceRecalibrator
        from app.schemas.consensus import ContradictionMatrixResult, DebateTranscript

        recalibrator = ConfidenceRecalibrator()
        raw_cm = state.get("contradiction_result")
        cm_obj = ContradictionMatrixResult(**raw_cm) if raw_cm else None
        raw_dt = state.get("debate_transcript")
        dt_obj = DebateTranscript(**raw_dt) if raw_dt else None

        result = recalibrator.recalibrate_panel(
            agent_outputs=state.get("agent_outputs") or [],
            contradiction_matrix=cm_obj,
            debate_transcript=dt_obj,
            symptoms_data=state.get("symptoms_data") or {},
            medical_history_data=state.get("medical_history_data") or {},
            laboratory_data=state.get("laboratory_data") or {},
            clinical_scores=state.get("clinical_scores") or {},
            ml_predictions=state.get("ml_predictions") or {},
            session_id=state.get("session_id"),
            patient_id=state.get("user_id") or "anon",
        )
        return {
            "recalibration_result": result.model_dump(),
            "current_phase": "confidence_recalibration_completed",
        }
    except Exception as exc:
        logger.error("recalibration_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"ConfidenceRecalibrator execution failure: {str(exc)}"],
            "warnings": ["Confidence recalibration unavailable; proceeding with consensus resolution."],
        }


def consensus_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Consensus Resolution Engine within LangGraph (Step 12.4)."""
    logger.info("Executing consensus_node for session: %s", state.get("session_id"))
    try:
        from app.agents.consensus.consensus_resolver import ConsensusResolver
        from app.schemas.consensus import (
            ConfidenceRecalibrationResult,
            ContradictionMatrixResult,
            DebateTranscript,
        )

        resolver = ConsensusResolver()
        raw_cm = state.get("contradiction_result")
        cm_obj = ContradictionMatrixResult(**raw_cm) if raw_cm else None
        raw_dt = state.get("debate_transcript")
        dt_obj = DebateTranscript(**raw_dt) if raw_dt else None
        raw_rc = state.get("recalibration_result")
        rc_obj = ConfidenceRecalibrationResult(**raw_rc) if raw_rc else None

        resolution = resolver.resolve_consensus(
            recalibration_result=rc_obj,
            contradiction_matrix=cm_obj,
            debate_transcript=dt_obj,
            agent_outputs=state.get("agent_outputs") or [],
            symptoms_data=state.get("symptoms_data") or {},
            medical_history_data=state.get("medical_history_data") or {},
            laboratory_data=state.get("laboratory_data") or {},
            clinical_scores=state.get("clinical_scores") or {},
            ml_predictions=state.get("ml_predictions") or {},
            session_id=state.get("session_id"),
            patient_id=state.get("user_id") or "anon",
        )

        return {
            "consensus_resolution": resolution.model_dump(),
            "audit_transcript": resolution.audit_transcript.model_dump(),
            "current_phase": "consensus_resolution_completed",
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.error("consensus_node failed: %s", exc, exc_info=True)
        return {
            "errors": [f"ConsensusResolver execution failure: {str(exc)}"],
            "warnings": ["Consensus resolution failed."],
            "status": "failed",
        }
