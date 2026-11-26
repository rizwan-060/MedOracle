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
from app.schemas.debate_events import EventStatus, EventType
from app.services.consensus.event_publisher import safe_publish_event
from app.services.llm_service import LLMService

logger = logging.getLogger("graph.nodes")


def symptom_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Symptom Analysis Specialist Agent within the LangGraph workflow."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing symptom_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.AGENT_ACTIVATED,
        {"agent_role": "symptom_agent"},
        patient_id=patient_id,
        agent_role="symptom_agent",
    )
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

        safe_publish_event(
            session_id,
            EventType.AGENT_ANALYSIS_COMPLETED,
            {"agent_role": "symptom_agent", "confidence": output.confidence},
            patient_id=patient_id,
            agent_role="symptom_agent",
            status=EventStatus.COMPLETED,
        )
        if output.findings:
            safe_publish_event(
                session_id,
                EventType.AGENT_CLAIM_SUBMITTED,
                {"finding": output.findings, "confidence": output.confidence},
                patient_id=patient_id,
                agent_role="symptom_agent",
                evidence_references=list(output.evidence or []),
            )

        return {
            "symptom_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("symptom_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "symptom_analysis", "error_type": type(exc).__name__},
            patient_id=patient_id,
            agent_role="symptom_agent",
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"SymptomAgent execution failure: {str(exc)}"],
            "warnings": ["Symptom domain analysis unavailable; proceeding with remaining clinical graph."],
        }


def medical_history_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Medical History Specialist Agent within the LangGraph workflow."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing medical_history_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.AGENT_ACTIVATED,
        {"agent_role": "medical_history_agent"},
        patient_id=patient_id,
        agent_role="medical_history_agent",
    )
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

        safe_publish_event(
            session_id,
            EventType.AGENT_ANALYSIS_COMPLETED,
            {"agent_role": "medical_history_agent", "confidence": output.confidence},
            patient_id=patient_id,
            agent_role="medical_history_agent",
            status=EventStatus.COMPLETED,
        )
        if output.findings:
            safe_publish_event(
                session_id,
                EventType.AGENT_CLAIM_SUBMITTED,
                {"finding": output.findings, "confidence": output.confidence},
                patient_id=patient_id,
                agent_role="medical_history_agent",
                evidence_references=list(output.evidence or []),
            )

        return {
            "medical_history_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("medical_history_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "medical_history_analysis", "error_type": type(exc).__name__},
            patient_id=patient_id,
            agent_role="medical_history_agent",
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"MedicalHistoryAgent execution failure: {str(exc)}"],
            "warnings": ["Medical history domain analysis unavailable; proceeding with remaining clinical graph."],
        }


def laboratory_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Laboratory Biomarker Specialist Agent within the LangGraph workflow."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing laboratory_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.AGENT_ACTIVATED,
        {"agent_role": "laboratory_agent"},
        patient_id=patient_id,
        agent_role="laboratory_agent",
    )
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

        safe_publish_event(
            session_id,
            EventType.AGENT_ANALYSIS_COMPLETED,
            {"agent_role": "laboratory_agent", "confidence": output.confidence},
            patient_id=patient_id,
            agent_role="laboratory_agent",
            status=EventStatus.COMPLETED,
        )
        if output.findings:
            safe_publish_event(
                session_id,
                EventType.AGENT_CLAIM_SUBMITTED,
                {"finding": output.findings, "confidence": output.confidence},
                patient_id=patient_id,
                agent_role="laboratory_agent",
                evidence_references=list(output.evidence or []),
            )

        return {
            "laboratory_output": output_dict,
            "agent_outputs": [output_dict],
        }
    except Exception as exc:
        logger.error("laboratory_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "laboratory_analysis", "error_type": type(exc).__name__},
            patient_id=patient_id,
            agent_role="laboratory_agent",
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"LaboratoryAgent execution failure: {str(exc)}"],
            "warnings": ["Laboratory biomarker analysis unavailable; proceeding with remaining clinical graph."],
        }


def risk_prediction_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Risk Prediction Ensemble Specialist Agent within the LangGraph workflow.

    Synthesizes outputs from upstream domain agents (Symptom, Medical History, Laboratory)
    with deterministic risk calculators and trained machine learning predictions.
    """
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing risk_prediction_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.AGENT_ACTIVATED,
        {"agent_role": "risk_prediction_agent"},
        patient_id=patient_id,
        agent_role="risk_prediction_agent",
    )
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

        safe_publish_event(
            session_id,
            EventType.AGENT_ANALYSIS_COMPLETED,
            {"agent_role": "risk_prediction_agent", "confidence": output.confidence},
            patient_id=patient_id,
            agent_role="risk_prediction_agent",
            status=EventStatus.COMPLETED,
        )
        if output.findings:
            safe_publish_event(
                session_id,
                EventType.AGENT_CLAIM_SUBMITTED,
                {"finding": output.findings, "confidence": output.confidence},
                patient_id=patient_id,
                agent_role="risk_prediction_agent",
                evidence_references=list(output.evidence or []),
            )

        return {
            "risk_prediction_output": output_dict,
            "agent_outputs": [output_dict],
            "current_phase": "risk_prediction_completed",
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.error("risk_prediction_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "risk_prediction", "error_type": type(exc).__name__},
            patient_id=patient_id,
            agent_role="risk_prediction_agent",
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"RiskPredictionAgent execution failure: {str(exc)}"],
            "warnings": ["Risk prediction ensemble synthesis unavailable."],
            "status": "failed",
        }


def contradiction_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Contradiction Detection Engine within LangGraph (Step 12.1)."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing contradiction_node for session: %s", session_id)
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
            session_id=session_id,
            patient_id=patient_id or "anon",
        )
        for issue in result.issues:
            sev_status = (
                EventStatus.CRITICAL
                if issue.severity.value == "critical"
                else EventStatus.WARNING
                if issue.severity.value == "moderate"
                else EventStatus.INFO
            )
            safe_publish_event(
                session_id,
                EventType.CONTRADICTION_DETECTED,
                {
                    "issue_id": issue.issue_id,
                    "rule_id": issue.rule_id,
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "conflicting_agents": issue.conflicting_agents,
                    "clinical_urgency": issue.clinical_urgency,
                },
                patient_id=patient_id,
                evidence_references=list(issue.evidence_references or []),
                status=sev_status,
            )
            safe_publish_event(
                session_id,
                EventType.CONTRADICTION_CLASSIFIED,
                {
                    "issue_id": issue.issue_id,
                    "contradiction_type": issue.contradiction_type.value,
                    "clinical_status": issue.clinical_status,
                },
                patient_id=patient_id,
                status=sev_status,
            )
        return {
            "contradiction_result": result.model_dump(),
            "current_phase": "contradiction_detection_completed",
        }
    except Exception as exc:
        logger.error("contradiction_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "contradiction_detection", "error_type": type(exc).__name__},
            patient_id=patient_id,
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"ContradictionDetector execution failure: {str(exc)}"],
            "warnings": ["Contradiction detection unavailable; proceeding with debate."],
        }


def debate_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Adversarial Debate Protocol within LangGraph (Step 12.2)."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing debate_node for session: %s", session_id)
    try:
        from app.agents.consensus.debate_protocol import DebateProtocolEngine
        from app.schemas.consensus import ContradictionMatrixResult, RebuttalDisposition

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
            session_id=session_id,
            patient_id=patient_id or "anon",
        )
        for ch in transcript.challenges:
            safe_publish_event(
                session_id,
                EventType.CHALLENGE_SUBMITTED,
                {
                    "challenge_id": ch.challenge_id,
                    "issue_id": ch.issue_id,
                    "challenge_text": ch.challenge_text,
                },
                patient_id=patient_id,
                agent_role=ch.challenging_agent,
                target_agent_role=ch.challenged_agent,
                round_number=ch.round_number,
                evidence_references=list(ch.evidence_basis or []),
            )
        for rb in transcript.rebuttals:
            safe_publish_event(
                session_id,
                EventType.REBUTTAL_SUBMITTED,
                {
                    "rebuttal_id": rb.rebuttal_id,
                    "challenge_id": rb.challenge_id,
                    "disposition": rb.disposition.value,
                    "rebuttal_text": rb.rebuttal_text,
                },
                patient_id=patient_id,
                agent_role=rb.responding_agent,
                round_number=rb.round_number,
                evidence_references=list(rb.grounding_evidence or []),
            )
            if rb.disposition == RebuttalDisposition.CONCEDE:
                safe_publish_event(
                    session_id,
                    EventType.CLAIM_CONCEDED,
                    {"rebuttal_id": rb.rebuttal_id, "challenge_id": rb.challenge_id},
                    patient_id=patient_id,
                    agent_role=rb.responding_agent,
                    round_number=rb.round_number,
                    status=EventStatus.WARNING,
                )
            elif rb.disposition == RebuttalDisposition.REVISE:
                safe_publish_event(
                    session_id,
                    EventType.CLAIM_REVISED,
                    {"rebuttal_id": rb.rebuttal_id, "challenge_id": rb.challenge_id},
                    patient_id=patient_id,
                    agent_role=rb.responding_agent,
                    round_number=rb.round_number,
                )
            elif rb.disposition == RebuttalDisposition.DEFEND:
                safe_publish_event(
                    session_id,
                    EventType.CLAIM_DEFENDED,
                    {"rebuttal_id": rb.rebuttal_id, "challenge_id": rb.challenge_id},
                    patient_id=patient_id,
                    agent_role=rb.responding_agent,
                    round_number=rb.round_number,
                )
        if transcript.challenges or transcript.rebuttals:
            safe_publish_event(
                session_id,
                EventType.DEBATE_ROUND_COMPLETED,
                {
                    "rounds_executed": transcript.total_rounds_executed,
                    "convergence_status": transcript.convergence_status,
                },
                patient_id=patient_id,
                round_number=transcript.total_rounds_executed,
                status=EventStatus.COMPLETED,
            )
        return {
            "debate_transcript": transcript.model_dump(),
            "current_phase": "adversarial_debate_completed",
        }
    except Exception as exc:
        logger.error("debate_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "adversarial_debate", "error_type": type(exc).__name__},
            patient_id=patient_id,
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"DebateProtocolEngine execution failure: {str(exc)}"],
            "warnings": ["Adversarial debate protocol unavailable; proceeding with recalibration."],
        }


def recalibration_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Confidence Recalibration Engine within LangGraph (Step 12.3)."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing recalibration_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.CONFIDENCE_RECALIBRATION_STARTED,
        {"session_id": session_id},
        patient_id=patient_id,
    )
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
            session_id=session_id,
            patient_id=patient_id or "anon",
        )
        for rec in result.recalibrated_claims:
            safe_publish_event(
                session_id,
                EventType.CONFIDENCE_RECALIBRATION_COMPLETED,
                {
                    "claim_id": rec.claim_id,
                    "original_confidence": rec.original_confidence,
                    "recalibrated_confidence": rec.final_confidence,
                    "missing_evidence_cap_applied": rec.missing_evidence_cap_applied,
                },
                patient_id=patient_id,
                agent_role=rec.agent_id,
                claim_id=rec.claim_id,
                evidence_references=list(rec.grounding_evidence_references or []),
                status=EventStatus.COMPLETED,
            )
        safe_publish_event(
            session_id,
            EventType.EPISTEMIC_DOUBT_CALCULATED,
            {
                "global_epistemic_doubt_score": result.global_epistemic_doubt_score,
                "calibration_status": result.calibration_status,
            },
            patient_id=patient_id,
            status=EventStatus.WARNING if result.global_epistemic_doubt_score >= 0.4 else EventStatus.INFO,
        )
        return {
            "recalibration_result": result.model_dump(),
            "current_phase": "confidence_recalibration_completed",
        }
    except Exception as exc:
        logger.error("recalibration_node failed: %s", exc, exc_info=True)
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "confidence_recalibration", "error_type": type(exc).__name__},
            patient_id=patient_id,
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"ConfidenceRecalibrator execution failure: {str(exc)}"],
            "warnings": ["Confidence recalibration unavailable; proceeding with consensus resolution."],
        }


def consensus_node(state: ClinicalAgentState) -> Dict[str, Any]:
    """Execute Consensus Resolution Engine within LangGraph (Step 12.4)."""
    session_id = state.get("session_id")
    patient_id = state.get("user_id")
    logger.info("Executing consensus_node for session: %s", session_id)
    safe_publish_event(
        session_id,
        EventType.CONSENSUS_RESOLUTION_STARTED,
        {"session_id": session_id},
        patient_id=patient_id,
    )
    try:
        from app.agents.consensus.consensus_resolver import ConsensusResolver
        from app.schemas.consensus import (
            ConfidenceRecalibrationResult,
            ContradictionMatrixResult,
            DebateTranscript,
            OverallConsensusOutcome,
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
            session_id=session_id,
            patient_id=patient_id or "anon",
        )

        outcome = resolution.overall_outcome
        outcome_event = (
            EventType.CONSENSUS_REACHED
            if outcome in [OverallConsensusOutcome.CONSENSUS_SUPPORTED, OverallConsensusOutcome.CONSENSUS_PROVISIONAL]
            else EventType.CONSENSUS_PARTIAL
            if outcome == OverallConsensusOutcome.PARTIAL_CONSENSUS
            else EventType.CONSENSUS_UNRESOLVED
        )
        safe_publish_event(
            session_id,
            outcome_event,
            {
                "overall_outcome": outcome.value,
                "safety_warning_count": len(resolution.clinical_safety_warnings),
            },
            patient_id=patient_id,
            status=EventStatus.CRITICAL if resolution.clinical_safety_warnings else EventStatus.COMPLETED,
        )
        safe_publish_event(
            session_id,
            EventType.FINAL_VERDICT_GENERATED,
            {
                "overall_outcome": outcome.value,
                "global_epistemic_doubt_score": resolution.global_epistemic_doubt_score,
                "transcript_hash": resolution.audit_transcript.canonical_transcript_hash,
            },
            patient_id=patient_id,
            status=EventStatus.COMPLETED,
        )
        safe_publish_event(
            session_id,
            EventType.DEBATE_COMPLETED,
            {"session_id": session_id, "overall_outcome": outcome.value},
            patient_id=patient_id,
            status=EventStatus.COMPLETED,
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
        safe_publish_event(
            session_id,
            EventType.DEBATE_FAILED,
            {"phase": "consensus_resolution", "error_type": type(exc).__name__},
            patient_id=patient_id,
            status=EventStatus.FAILED,
        )
        return {
            "errors": [f"ConsensusResolver execution failure: {str(exc)}"],
            "warnings": ["Consensus resolution failed."],
            "status": "failed",
        }
