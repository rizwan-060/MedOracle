"""Domain Agents Standalone Testing & Diagnostic APIs (Step 10).

Provides standalone evaluation endpoints for:
1. Symptom Specialist Agent (/api/v1/agents/symptom/test)
2. Medical History Specialist Agent (/api/v1/agents/medical-history/test)
3. Laboratory Biomarker Specialist Agent (/api/v1/agents/laboratory/test)
4. Risk Prediction Ensemble Agent (/api/v1/agents/risk-prediction/test)
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.symptom_agent import SymptomAgent
from app.core.security import get_current_user
from app.database.models import User
from app.ml.inference.predictor import RealtimePredictor
from app.schemas.analysis import AgentOutputResponse, SymptomAgentTestRequest

logger = logging.getLogger("agents_api")

router = APIRouter(prefix="/agents", tags=["Domain Clinical Agents"])


@router.post(
    "/symptom/test",
    response_model=AgentOutputResponse,
    summary="Evaluate patient symptoms using the Symptom Specialist Agent",
)
def test_symptom_agent(
    payload: SymptomAgentTestRequest,
    current_user: User = Depends(get_current_user),
) -> AgentOutputResponse:
    """Execute standalone clinical reasoning through the Symptom Specialist Agent.

    Features:
    - Automatically processes free-text notes through the Clinical NLP Extractor with NegEx.
    - Synthesizes ML differential diagnosis probabilities from the 41-class classifier.
    - Detects acute emergency RED FLAGS (e.g. substernal pressure, diaphoresis).
    - Returns structured AgentOutputResponse with findings, confidence, reasoning, evidence, and challenges.
    - Results are cached in Redis / In-Memory cache for identical inputs.
    """
    try:
        context: Dict[str, Any] = {
            "symptoms": payload.symptoms,
            "severity": payload.severity,
            "duration_days": payload.duration_days,
            "notes": payload.notes,
            "patient_demographics": {
                "age": payload.age,
                "sex": payload.sex,
            },
        }

        # If clinical narrative or notes provided, enhance with Clinical NLP & ML Differential
        if payload.notes:
            try:
                predictor = RealtimePredictor.get_instance()
                nlp_res = predictor.nlp_extractor.extract(payload.notes)
                context["nlp_entities"] = [
                    {
                        "text": m.text,
                        "canonical_symptom": m.canonical_symptom,
                        "negated": m.negated,
                        "confidence": m.confidence,
                    }
                    for m in nlp_res.entities
                ]

                # Run differential prediction if symptoms identified
                diff_symptoms = list(set(payload.symptoms + nlp_res.extracted_canonical_symptoms))
                if diff_symptoms:
                    diff_res = predictor.predict_symptom_disease(diff_symptoms)
                    context["differential_candidates"] = [
                        {
                            "disease": cand.disease,
                            "probability": cand.probability,
                        }
                        for cand in diff_res.top_candidates
                    ]
            except Exception as ml_err:
                logger.warning("Optional NLP/ML enrichment failed (non-fatal): %s", ml_err)

        agent = SymptomAgent()
        output = agent.analyze(
            context=context,
            provider=payload.provider,
            use_cache=payload.use_cache,
        )
        return output

    except Exception as exc:
        logger.error("SymptomAgent execution failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SymptomAgent analysis failed: {str(exc)}",
        ) from exc
