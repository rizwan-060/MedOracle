"""Consensus & Multi-Agent Debate APIs (Step 12).

Provides standalone endpoints for:
1. Contradiction Detection Engine (/api/v1/consensus/contradictions/test) [Sub-Step 12.1]
2. Multi-Agent Adversarial Debate Protocol (/api/v1/consensus/debate/test) [Sub-Step 12.2]
3. Consensus Resolution & Debate Transcript (/api/v1/consensus/verdict/test) [Sub-Step 12.4]
"""

import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine
from app.core.security import get_current_user
from app.database.models import User
from app.schemas.consensus import (
    ContradictionTestRequest,
    ContradictionTestResponse,
    DebateTestRequest,
    DebateTestResponse,
)

logger = logging.getLogger("consensus_api")

router = APIRouter(prefix="/consensus", tags=["Consensus & Multi-Agent Debate"])


@router.post(
    "/contradictions/test",
    response_model=ContradictionTestResponse,
    summary="Evaluate multi-agent clinical hypotheses for physiological contradictions",
)
def test_contradiction_detection(
    payload: ContradictionTestRequest,
    current_user: User = Depends(get_current_user),
) -> ContradictionTestResponse:
    """Evaluate multi-agent clinical hypotheses against the Contradiction Matrix.

    Evaluates:
    - Subjective symptoms vs. objective biomarkers (e.g. acute chest pain vs. normal troponin/ECG).
    - Longitudinal medication adherence vs. uncontrolled laboratory endpoints (e.g. statins vs. LDL >= 190).
    - Deterministic cohort equations vs. machine learning risk classifiers (e.g. Framingham vs ML gap >= 25%).
    - Generates targeted debate challenges for contradictory agent pairs.
    - Computes mathematical preliminary Epistemic Doubt Score (0.00 to 1.00).
    """
    start_time = time.perf_counter()
    try:
        detector = ContradictionDetector(default_disagreement_threshold=payload.disagreement_threshold)
        result = detector.evaluate_contradictions(
            symptoms_data=payload.symptoms_data,
            medical_history_data=payload.medical_history_data,
            laboratory_data=payload.laboratory_data,
            clinical_scores=payload.clinical_scores,
            ml_predictions=payload.ml_predictions,
            agent_outputs=payload.agent_outputs,
            session_id=payload.session_id,
            patient_id=payload.patient_id,
            disagreement_threshold=payload.disagreement_threshold,
        )

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return ContradictionTestResponse(
            status="success",
            result=result,
            execution_time_ms=execution_time_ms,
        )
    except Exception as exc:
        logger.error("Contradiction detection failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contradiction detection failed: {str(exc)}",
        ) from exc


@router.post(
    "/debate/test",
    response_model=DebateTestResponse,
    summary="Execute multi-agent adversarial debate protocol and cross-examination (Sub-Step 12.2)",
)
def test_adversarial_debate(
    payload: DebateTestRequest,
    current_user: User = Depends(get_current_user),
) -> DebateTestResponse:
    """Execute the two-round multi-agent adversarial debate protocol.

    Workflow:
    1. Evaluates multi-agent hypotheses against the Contradiction Matrix.
    2. Round 1: Formulates targeted cross-domain adversarial challenges (excluding incomparable predictions).
    3. Round 2: Routes challenges to agents for evidence-grounded rebuttals, revisions, or formal concessions.
    4. Evaluates qualitative narrative findings using Natural Language Inference (NLI).
    5. Enforces strict maximum 2-round termination and convergence detection.
    6. Returns complete auditable DebateTranscript.
    """
    start_time = time.perf_counter()
    try:
        # Step 1: Detect contradictions
        detector = ContradictionDetector(default_disagreement_threshold=payload.disagreement_threshold)
        contradiction_result = detector.evaluate_contradictions(
            symptoms_data=payload.symptoms_data,
            medical_history_data=payload.medical_history_data,
            laboratory_data=payload.laboratory_data,
            clinical_scores=payload.clinical_scores,
            ml_predictions=payload.ml_predictions,
            agent_outputs=payload.agent_outputs,
            session_id=payload.session_id,
            patient_id=payload.patient_id,
            disagreement_threshold=payload.disagreement_threshold,
        )

        # Step 2: Execute two-round adversarial debate
        engine = DebateProtocolEngine(max_rounds=2)
        transcript = engine.execute_debate(
            contradiction_result=contradiction_result,
            agent_outputs=payload.agent_outputs,
            symptoms_data=payload.symptoms_data,
            medical_history_data=payload.medical_history_data,
            laboratory_data=payload.laboratory_data,
            clinical_scores=payload.clinical_scores,
            ml_predictions=payload.ml_predictions,
            session_id=payload.session_id,
            patient_id=payload.patient_id,
        )

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return DebateTestResponse(
            status="success",
            contradiction_result=contradiction_result,
            debate_transcript=transcript,
            execution_time_ms=execution_time_ms,
        )
    except Exception as exc:
        logger.error("Adversarial debate protocol failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Adversarial debate protocol failed: {str(exc)}",
        ) from exc
