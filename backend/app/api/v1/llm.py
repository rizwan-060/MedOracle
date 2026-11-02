"""LLM Router, Diagnostics, and Clinical Testing Endpoints (Step 9.2).

Provides endpoints for:
1. Checking LLM provider readiness, models, and cache diagnostics.
2. Executing structured clinical completions with caching and failover validation.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.database.models import User
from app.schemas.llm import (
    LLMClinicalTestOutput,
    LLMStatusResponse,
    LLMTestRequest,
)
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger("llm_api")

router = APIRouter(prefix="/llm", tags=["LLM Services"])


@router.get(
    "/status",
    response_model=LLMStatusResponse,
    summary="Check LLM provider readiness and cache status",
)
def get_llm_status(
    service: LLMService = Depends(get_llm_service),
) -> LLMStatusResponse:
    """Return operational readiness, active models, and caching diagnostics for LLM providers."""
    status_data = service.get_provider_status()
    return LLMStatusResponse.model_validate(status_data)


@router.post(
    "/test",
    response_model=LLMClinicalTestOutput,
    summary="Test structured LLM generation with failover and response caching",
)
def test_llm_generation(
    payload: LLMTestRequest,
    current_user: User = Depends(get_current_user),
    service: LLMService = Depends(get_llm_service),
) -> LLMClinicalTestOutput:
    """Generate and validate a structured clinical output conforming to the MedOracle agent contract.

    Verifies:
    - Primary provider (Groq) or fallback provider (Gemini) or Mock execution.
    - Pydantic schema validation.
    - Response caching in Redis / In-Memory cache (subsequent calls return cached=True).
    """
    try:
        obj, response = service.generate_structured(
            prompt=payload.prompt,
            schema=LLMClinicalTestOutput,
            system_prompt=(
                "You are an expert clinical reasoning assistant in the MedOracle diagnostic platform. "
                "Synthesize clinical evidence, provide balanced reasoning chains, estimate confidence, "
                "and formulate critical challenges for other agents to review."
            ),
            provider=payload.provider,
            model=payload.model,
            temperature=payload.temperature,
            use_cache=payload.use_cache,
        )

        # Attach execution metadata
        obj.execution_metadata = {
            "provider": response.provider,
            "model": response.model,
            "latency_ms": response.latency_ms,
            "cached": response.cached,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
            "invoked_by_user_id": current_user.id,
        }
        return obj

    except Exception as exc:
        logger.error("LLM test generation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM generation failed: {str(exc)}",
        ) from exc
