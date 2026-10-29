"""Unit tests for MedOracle Multi-Agent Clinical Framework and Base Agent (Step 10.1)."""

from typing import Any, Dict
from unittest.mock import MagicMock
import pytest

from app.agents.base import AgentExecutionError, BaseClinicalAgent
from app.core.cache import CacheManager, InMemoryCacheBackend
from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import (
    LLMResponse,
    LLMService,
    LLMServiceError,
    MockLLMProvider,
)


class DummyClinicalAgent(BaseClinicalAgent):
    """Concrete clinical agent implementation for testing BaseClinicalAgent."""

    @property
    def agent_role(self) -> str:
        return "Dummy Clinical Specialist"

    @property
    def system_prompt(self) -> str:
        return "You are a test clinical reasoning specialist evaluating patient observations."

    def build_prompt(self, context: Dict[str, Any]) -> str:
        symptoms = context.get("symptoms", [])
        return f"Evaluate patient presenting with symptoms: {', '.join(symptoms)}."


@pytest.fixture
def clean_cache() -> CacheManager:
    """Isolated cache manager for agent testing."""
    backend = InMemoryCacheBackend()
    manager = CacheManager(backend=backend)
    manager.clear()
    return manager


@pytest.fixture
def mock_llm_service(clean_cache: CacheManager) -> LLMService:
    """LLMService backed by MockLLMProvider and in-memory cache."""
    mock_prov = MockLLMProvider(simulated_latency_ms=0.5)
    return LLMService(
        cache_manager=clean_cache,
        mock_provider=mock_prov,
    )


@pytest.fixture
def dummy_agent(mock_llm_service: LLMService) -> DummyClinicalAgent:
    """Instantiated DummyClinicalAgent using mock LLM service."""
    return DummyClinicalAgent(llm_service=mock_llm_service)


# =============================================================================
# 1. Base Agent Contract & Properties Tests
# =============================================================================
def test_base_agent_properties(dummy_agent: DummyClinicalAgent):
    """Verify agent role, system prompt, and prompt builder."""
    assert dummy_agent.agent_role == "Dummy Clinical Specialist"
    assert "test clinical reasoning" in dummy_agent.system_prompt
    prompt = dummy_agent.build_prompt({"symptoms": ["chest pain", "dyspnea"]})
    assert "chest pain, dyspnea" in prompt


def test_base_agent_context_validation(dummy_agent: DummyClinicalAgent):
    """Verify that invalid context raises AgentExecutionError."""
    with pytest.raises(AgentExecutionError) as exc_info:
        dummy_agent.analyze("invalid string context")  # type: ignore

    assert "Context must be a dictionary" in str(exc_info.value)
    assert exc_info.value.agent_role == "Dummy Clinical Specialist"


# =============================================================================
# 2. Base Agent Execution & Output Contract Tests
# =============================================================================
def test_base_agent_successful_analysis(dummy_agent: DummyClinicalAgent):
    """Verify that agent analysis produces a valid AgentOutputResponse with metadata."""
    context = {"symptoms": ["fatigue", "elevated blood sugar"]}
    output = dummy_agent.analyze(context)

    assert isinstance(output, AgentOutputResponse)
    assert output.agent_role == "Dummy Clinical Specialist"
    assert 0.0 <= output.confidence <= 100.0
    assert len(output.findings) > 0
    assert len(output.reasoning_chain) > 0
    assert len(output.evidence) > 0
    assert len(output.challenges) > 0

    # Telemetry inspection
    meta = output.metadata_payload
    assert meta is not None
    assert meta["agent_role"] == "Dummy Clinical Specialist"
    assert meta["provider_used"] == "mock"
    assert meta["cached"] is False
    assert meta["latency_ms"] >= 0.0
    assert "analyzed_at" in meta


# =============================================================================
# 3. Base Agent Response Caching Tests
# =============================================================================
def test_base_agent_response_caching(dummy_agent: DummyClinicalAgent, clean_cache: CacheManager):
    """Verify that identical agent requests hit the cache on subsequent executions."""
    context = {"symptoms": ["polyuria", "polydipsia"]}

    # Call 1: Miss
    out1 = dummy_agent.analyze(context, use_cache=True)
    assert out1.metadata_payload["cached"] is False

    # Call 2: Hit
    out2 = dummy_agent.analyze(context, use_cache=True)
    assert out2.metadata_payload["cached"] is True
    assert out2.metadata_payload["latency_ms"] == 0.0
    assert out1.findings == out2.findings
    assert out1.confidence == out2.confidence
    assert clean_cache.hits >= 1


# =============================================================================
# 4. Error Wrapping & Resilience Tests
# =============================================================================
def test_base_agent_error_wrapping(clean_cache: CacheManager):
    """When LLM service fails, BaseClinicalAgent must wrap the error in AgentExecutionError."""
    failing_llm = MagicMock(spec=LLMService)
    failing_llm.generate_structured.side_effect = LLMServiceError("All upstream LLM models timed out")

    agent = DummyClinicalAgent(llm_service=failing_llm)

    with pytest.raises(AgentExecutionError) as exc_info:
        agent.analyze({"symptoms": ["headache"]})

    assert "All upstream LLM models timed out" in str(exc_info.value)
    assert exc_info.value.agent_role == "Dummy Clinical Specialist"
    assert exc_info.value.original_exception is not None
