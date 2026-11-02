"""Base Clinical Agent Framework for MedOracle (Step 10.1).

Defines the abstract foundation for all autonomous clinical reasoning agents.
Enforces the universal AgentOutputResponse schema contract:
- agent_role: Role/specialty of the agent
- findings: Concise clinical findings and observations
- confidence: Quantitative confidence score (0.0 to 100.0)
- reasoning_chain: Explicit step-by-step reasoning bullets
- evidence: Grounded patient biomarkers, symptoms, or histories
- challenges: Critical doubts or questions for the multi-agent debate
- metadata_payload: Execution telemetry, latency, provider, and cache info
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Type

from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import LLMService, get_llm_service

logger = logging.getLogger("agents.base")


class AgentExecutionError(Exception):
    """Exception raised when a domain agent fails during analysis execution."""

    def __init__(self, agent_role: str, message: str, original_exception: Optional[Exception] = None):
        super().__init__(f"[{agent_role}] {message}")
        self.agent_role = agent_role
        self.original_exception = original_exception


class BaseClinicalAgent(ABC):
    """Abstract base class for all MedOracle specialized clinical agents."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm = llm_service or get_llm_service()

    @property
    @abstractmethod
    def agent_role(self) -> str:
        """Formal clinical role of the agent (e.g. 'Symptom Specialist')."""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt establishing agent persona, clinical domain, and reasoning guidelines."""

    @abstractmethod
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Construct the domain-specific prompt from incoming patient data context."""

    def validate_context(self, context: Dict[str, Any]) -> None:
        """Validate that incoming context contains minimum required fields for this domain.
        Subclasses may override this to enforce domain-specific requirements.
        """
        if not isinstance(context, dict):
            raise AgentExecutionError(
                self.agent_role,
                f"Context must be a dictionary, received {type(context).__name__}",
            )

    def analyze(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        use_cache: bool = True,
    ) -> AgentOutputResponse:
        """Execute domain reasoning pipeline and return a structured AgentOutputResponse.

        Args:
            context: Dictionary containing patient records, symptoms, histories, or labs.
            provider: Optional LLM provider override ('groq', 'gemini', or 'mock').
            model: Optional model name override.
            temperature: Sampling temperature for reasoning stability.
            use_cache: Whether to leverage Redis / In-Memory response caching.

        Returns:
            Validated AgentOutputResponse conforming strictly to the multi-agent contract.
        """
        t0 = time.perf_counter()
        self.validate_context(context)

        prompt = self.build_prompt(context)
        logger.info("[%s] Initiating clinical analysis (cache=%s)", self.agent_role, use_cache)

        try:
            output, response = self.llm.generate_structured(
                prompt=prompt,
                schema=AgentOutputResponse,
                system_prompt=self.system_prompt,
                provider=provider,
                model=model,
                temperature=temperature,
                use_cache=use_cache,
            )
        except Exception as exc:
            logger.error("[%s] Analysis generation failed: %s", self.agent_role, exc, exc_info=True)
            raise AgentExecutionError(self.agent_role, f"Failed generating analysis: {exc}", exc) from exc

        duration_ms = 0.0 if response.cached else (time.perf_counter() - t0) * 1000

        # Enforce agent role integrity
        output.agent_role = self.agent_role

        # Embed execution telemetry into metadata_payload
        telemetry = {
            "agent_role": self.agent_role,
            "provider_used": response.provider,
            "model_used": response.model,
            "latency_ms": round(duration_ms, 2),
            "cached": response.cached,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        if output.metadata_payload is None:
            output.metadata_payload = telemetry
        else:
            output.metadata_payload.update(telemetry)

        logger.info(
            "[%s] Completed analysis in %.2fms (confidence=%.1f%%, cached=%s)",
            self.agent_role,
            output.metadata_payload["latency_ms"],
            output.confidence,
            output.metadata_payload["cached"],
        )
        return output
