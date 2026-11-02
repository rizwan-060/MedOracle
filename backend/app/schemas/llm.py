"""Pydantic schemas for LLM provider status and test endpoints (Step 9.2)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMProviderInfo(BaseModel):
    """Status details for an individual provider."""

    available: bool
    primary_model: Optional[str] = None
    fast_model: Optional[str] = None
    fallback_model: Optional[str] = None
    simulated_latency_ms: Optional[float] = None


class LLMStatusResponse(BaseModel):
    """System-level LLM router readiness and cache diagnostic response."""

    configured_default: str
    cache_backend: str
    cache_enabled: bool
    providers: Dict[str, Any]


class LLMTestRequest(BaseModel):
    """Payload to test prompt completion and schema validation."""

    prompt: str = Field(
        default="Synthesize cardiovascular and metabolic risk considerations for an individual with fasting blood sugar 128 mg/dL and systolic BP 142 mmHg.",
        description="Prompt to evaluate through the LLM pipeline.",
    )
    provider: Optional[str] = Field(
        default=None,
        description="Optional provider override ('groq', 'gemini', or 'mock').",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override.",
    )
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    use_cache: bool = Field(default=True, description="Enable response caching.")


class LLMClinicalTestOutput(BaseModel):
    """Standard structured output adhering to the MedOracle agent contract."""

    agent_role: str = Field(default="Clinical Risk Evaluator")
    findings: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    reasoning_chain: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
