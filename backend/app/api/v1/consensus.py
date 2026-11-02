"""Consensus & Multi-Agent Debate APIs (Step 12).

Provides standalone endpoints for:
1. Contradiction Detection Engine (/api/v1/consensus/contradictions/test)
2. Multi-Agent Adversarial Debate Protocol (/api/v1/consensus/debate/test) [Sub-Step 12.2]
3. Consensus Resolution & Debate Transcript (/api/v1/consensus/verdict/test) [Sub-Step 12.4]
"""

import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.core.security import get_current_user
from app.database.models import User
from app.schemas.consensus import (
    ContradictionTestRequest,
    ContradictionTestResponse,
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
