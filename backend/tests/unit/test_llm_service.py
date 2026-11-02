"""Unit tests for Multi-Provider LLM Service, Failover Routing, and Response Caching (Step 9.2)."""

import json
import time
from typing import List, Optional
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, Field
import pytest

from app.core.cache import CacheManager, InMemoryCacheBackend
from app.core.config import Settings
from app.schemas.analysis import AgentOutputResponse, ConsensusVerdictSchema
from app.schemas.llm import LLMClinicalTestOutput
from app.services.llm_service import (
    BaseLLMProvider,
    GeminiLLMProvider,
    GroqLLMProvider,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponse,
    LLMService,
    LLMServiceError,
    LLMValidationError,
    MockLLMProvider,
    build_cache_digest,
    strip_markdown_json,
)


# =============================================================================
# Test Schema Fixtures
# =============================================================================
class SimpleRiskSchema(BaseModel):
    category: str
    urgency: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    findings: str
    evidence: List[str] = Field(default_factory=list)


@pytest.fixture
def clean_cache() -> CacheManager:
    """Isolated in-memory cache manager for LLM test isolation."""
    backend = InMemoryCacheBackend()
    manager = CacheManager(backend=backend)
    manager.clear()
    return manager


@pytest.fixture
def mock_provider() -> MockLLMProvider:
    """Clean MockLLMProvider with minimal simulated latency."""
    provider = MockLLMProvider(simulated_latency_ms=0.5)
    provider.clear_mocks()
    return provider


@pytest.fixture
def llm_service(clean_cache: CacheManager, mock_provider: MockLLMProvider) -> LLMService:
    """Isolated LLMService orchestrator using mock provider and clean cache."""
    return LLMService(
        cache_manager=clean_cache,
        mock_provider=mock_provider,
    )


# =============================================================================
# 1. Helper Function Tests
# =============================================================================
def test_strip_markdown_json():
    """Verify markdown fences and text wrappers are correctly stripped."""
    # Raw JSON
    assert strip_markdown_json('{"key": "val"}') == '{"key": "val"}'

    # ```json codeblock
    fenced = "```json\n{\n  \"findings\": \"elevated\"\n}\n```"
    assert json.loads(strip_markdown_json(fenced)) == {"findings": "elevated"}

    # ``` with surrounding prose
    wrapped = "Here is the result:\n```\n{\"confidence\": 85.0}\n```\nHope this helps!"
    assert json.loads(strip_markdown_json(wrapped)) == {"confidence": 85.0}

    # JSON array
    array_text = "Analysis list: [{\"id\": 1}, {\"id\": 2}]"
    assert json.loads(strip_markdown_json(array_text)) == [{"id": 1}, {"id": 2}]

    # Empty / none
    assert strip_markdown_json("") == ""


def test_build_cache_digest():
    """Verify deterministic SHA-256 digest generation."""
    d1 = build_cache_digest("groq", "llama-3.3-70b-versatile", "sys prompt", "user prompt", "schema", 0.2)
    d2 = build_cache_digest("groq", "llama-3.3-70b-versatile", "sys prompt", "user prompt", "schema", 0.2)
    d3 = build_cache_digest("groq", "llama-3.3-70b-versatile", "diff prompt", "user prompt", "schema", 0.2)

    assert d1 == d2
    assert d1 != d3
    assert len(d1) == 64


# =============================================================================
# 2. MockLLMProvider Core Tests
# =============================================================================
def test_mock_provider_text_generation(mock_provider: MockLLMProvider):
    """Verify unstructured text generation produces plausible output with metrics."""
    prompt = "Analyze patient with fasting blood glucose 135 mg/dL."
    resp = mock_provider.generate_text(prompt=prompt)

    assert resp.provider == "mock"
    assert resp.cached is False
    assert resp.latency_ms > 0
    assert "Mock Clinical Assessment" in resp.content
    assert resp.total_tokens is not None and resp.total_tokens > 0


def test_mock_provider_structured_synthesis(mock_provider: MockLLMProvider):
    """Verify automatic synthesis of complex Pydantic models with clinical validity."""
    prompt = "Assess cardiovascular risk for 55yo male with hypertension."
    obj, resp = mock_provider.generate_structured(prompt=prompt, schema=AgentOutputResponse)

    assert isinstance(obj, AgentOutputResponse)
    assert 0.0 <= obj.confidence <= 100.0
    assert len(obj.reasoning_chain) > 0
    assert len(obj.evidence) > 0
    assert len(obj.challenges) > 0
    assert resp.provider == "mock"
    assert resp.cached is False

    # Also test ConsensusVerdictSchema
    verdict, _ = mock_provider.generate_structured(prompt=prompt, schema=ConsensusVerdictSchema)
    assert isinstance(verdict, ConsensusVerdictSchema)
    assert 0.0 <= verdict.consensus_confidence <= 100.0
    assert verdict.overall_urgency in ("low", "moderate", "high", "immediate")


def test_mock_provider_custom_registered_responses(mock_provider: MockLLMProvider):
    """Verify that user-registered custom mock outputs are returned when prompt matches."""
    custom_output = SimpleRiskSchema(
        category="Metabolic Syndrome",
        urgency="high",
        confidence=96.0,
        findings="Impaired fasting glucose and dyslipidemia.",
        evidence=["FBG: 145 mg/dL", "Triglycerides: 220 mg/dL"],
    )
    mock_provider.register_mock_response("metabolic trigger", custom_output)

    obj, resp = mock_provider.generate_structured(
        prompt="Patient presents with metabolic trigger symptoms",
        schema=SimpleRiskSchema,
    )

    assert obj.category == "Metabolic Syndrome"
    assert obj.confidence == 96.0
    assert obj.urgency == "high"


# =============================================================================
# 3. LLM Response Caching Tests
# =============================================================================
def test_llm_response_caching(llm_service: LLMService, clean_cache: CacheManager):
    """Verify that repeated calls hit the cache with zero latency and cached=True."""
    prompt = "Evaluate Framingham CVD profile."

    # Call 1: Cache Miss
    obj1, resp1 = llm_service.generate_structured(
        prompt=prompt,
        schema=LLMClinicalTestOutput,
        use_cache=True,
    )
    assert resp1.cached is False
    assert clean_cache.hits == 0

    # Call 2: Cache Hit
    obj2, resp2 = llm_service.generate_structured(
        prompt=prompt,
        schema=LLMClinicalTestOutput,
        use_cache=True,
    )
    assert resp2.cached is True
    assert resp2.latency_ms == 0.0
    assert clean_cache.hits >= 1
    assert obj1.findings == obj2.findings
    assert obj1.confidence == obj2.confidence


def test_llm_text_caching(llm_service: LLMService, clean_cache: CacheManager):
    """Verify text completion caching."""
    prompt = "What is normal fasting blood glucose?"

    r1 = llm_service.generate_text(prompt=prompt, use_cache=True)
    assert r1.cached is False

    r2 = llm_service.generate_text(prompt=prompt, use_cache=True)
    assert r2.cached is True
    assert r2.latency_ms == 0.0
    assert r1.content == r2.content


def test_llm_cache_bypass(llm_service: LLMService):
    """Verify that use_cache=False forces re-execution."""
    prompt = "Evaluate cache bypass"
    _, r1 = llm_service.generate_structured(prompt=prompt, schema=SimpleRiskSchema, use_cache=False)
    _, r2 = llm_service.generate_structured(prompt=prompt, schema=SimpleRiskSchema, use_cache=False)

    assert r1.cached is False
    assert r2.cached is False


# =============================================================================
# 4. Failover Routing Tests
# =============================================================================
def test_failover_routing_from_groq_to_gemini(clean_cache: CacheManager, mock_provider: MockLLMProvider):
    """When primary provider (Groq) fails with error, service must route to fallback (Gemini)."""
    # Create mock Groq provider that always raises error
    failing_groq = MagicMock(spec=BaseLLMProvider)
    failing_groq.provider_name = "groq"
    failing_groq.is_available.return_value = True
    failing_groq.generate_structured.side_effect = LLMProviderError("groq", "Simulated Groq 500 API outage")

    # Create mock Gemini provider that succeeds
    successful_gemini = MagicMock(spec=BaseLLMProvider)
    successful_gemini.provider_name = "gemini"
    successful_gemini.is_available.return_value = True
    successful_gemini.generate_structured.return_value = (
        SimpleRiskSchema(
            category="Low Risk",
            urgency="low",
            confidence=90.0,
            findings="Gemini Fallback Assessment Successful",
            evidence=["Gemini fallback executed"],
        ),
        LLMResponse(
            content='{"category": "Low Risk"}',
            provider="gemini",
            model="gemini-2.5-flash",
            latency_ms=15.0,
            cached=False,
        ),
    )

    service = LLMService(
        cache_manager=clean_cache,
        mock_provider=mock_provider,
        groq_provider=failing_groq,
        gemini_provider=successful_gemini,
    )
    # Patch default provider to groq
    service.settings = Settings(
        app_env="production",
        llm_provider="groq",
        groq_api_key="fake-groq-key",
        gemini_api_key="fake-gemini-key",
        llm_max_retries=1,
    )

    obj, resp = service.generate_structured(
        prompt="Check failover routing",
        schema=SimpleRiskSchema,
        use_cache=False,
    )

    assert resp.provider == "gemini"
    assert obj.findings == "Gemini Fallback Assessment Successful"
    assert failing_groq.generate_structured.called
    assert successful_gemini.generate_structured.called


def test_failover_exhaustion_raises_llm_service_error(clean_cache: CacheManager):
    """When all providers fail, service must raise LLMServiceError."""
    failing_groq = MagicMock(spec=BaseLLMProvider)
    failing_groq.provider_name = "groq"
    failing_groq.is_available.return_value = True
    failing_groq.generate_text.side_effect = LLMProviderError("groq", "Groq down")

    failing_gemini = MagicMock(spec=BaseLLMProvider)
    failing_gemini.provider_name = "gemini"
    failing_gemini.is_available.return_value = True
    failing_gemini.generate_text.side_effect = LLMProviderError("gemini", "Gemini down")

    service = LLMService(
        cache_manager=clean_cache,
        groq_provider=failing_groq,
        gemini_provider=failing_gemini,
    )
    service.settings = Settings(
        app_env="production",
        llm_provider="groq",
        groq_api_key="fake-groq-key",
        gemini_api_key="fake-gemini-key",
        llm_max_retries=0,
    )

    with pytest.raises(LLMServiceError) as exc_info:
        service.generate_text("Should fail all", use_cache=False)

    assert "All LLM providers in execution chain failed" in str(exc_info.value)


# =============================================================================
# 5. Exponential Backoff Retry on Rate Limit Tests
# =============================================================================
def test_rate_limit_retry_succeeds_with_backoff(clean_cache: CacheManager):
    """Provider hitting rate limit on attempt 1 but succeeding on attempt 2 must recover."""
    rate_limited_groq = MagicMock(spec=BaseLLMProvider)
    rate_limited_groq.provider_name = "groq"
    rate_limited_groq.is_available.return_value = True

    # 1st call raises LLMRateLimitError; 2nd call succeeds
    success_resp = LLMResponse(
        content="Recovered after backoff",
        provider="groq",
        model="llama-3.3-70b-versatile",
        latency_ms=25.0,
        cached=False,
    )
    rate_limited_groq.generate_text.side_effect = [
        LLMRateLimitError("groq", "Rate limit 429", status_code=429),
        success_resp,
    ]

    service = LLMService(
        cache_manager=clean_cache,
        groq_provider=rate_limited_groq,
    )
    service.settings = Settings(
        app_env="production",
        llm_provider="groq",
        llm_max_retries=2,
        llm_retry_backoff=0.01,  # Short backoff for fast test execution
    )

    resp = service.generate_text("Prompt with rate limit recovery", use_cache=False)

    assert resp.content == "Recovered after backoff"
    assert rate_limited_groq.generate_text.call_count == 2


# =============================================================================
# 6. Provider Diagnostics & Status Tests
# =============================================================================
def test_provider_status_inspection(llm_service: LLMService):
    """Verify diagnostic status inspection returns availability of all providers."""
    status = llm_service.get_provider_status()

    assert "configured_default" in status
    assert "cache_backend" in status
    assert "providers" in status
    assert "mock" in status["providers"]
    assert "groq" in status["providers"]
    assert "gemini" in status["providers"]
    assert status["providers"]["mock"]["available"] is True
