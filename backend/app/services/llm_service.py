"""Multi-Provider LLM Service with Fallback Routing and Response Caching (Step 9.2).

Provides:
1. Unified BaseLLMProvider interface for synchronous/asynchronous LLM calls.
2. Concrete providers:
   - GroqLLMProvider: Primary high-throughput provider (Llama-3.3-70b-versatile, Llama-3.1-8b-instant).
   - GeminiLLMProvider: Resilient secondary fallback provider (Gemini 2.5/3.8 Flash).
   - MockLLMProvider: Deterministic, offline provider for zero-cost unit testing & development.
3. Resilient failover routing: Groq -> Gemini -> Mock (in dev/test).
4. Exponential backoff retries for rate limits (HTTP 429) and transient connection failures.
5. Pydantic-validated structured output generation.
6. Redis and In-Memory response caching to eliminate redundant token consumption.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, Field

try:
    import groq
    from groq import Groq
except ImportError:
    groq = None  # type: ignore
    Groq = None  # type: ignore

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None  # type: ignore
    genai_types = None  # type: ignore

from app.core.cache import CacheManager, get_cache_manager
from app.core.config import get_settings

logger = logging.getLogger("llm_service")

T = TypeVar("T", bound=BaseModel)


# =============================================================================
# Custom LLM Service Exceptions
# =============================================================================
class LLMServiceError(Exception):
    """Base exception for all LLM service failures."""


class LLMProviderError(LLMServiceError):
    """Exception raised when an individual LLM provider encounters an error."""

    def __init__(self, provider: str, message: str, status_code: Optional[int] = None):
        super().__init__(f"[{provider}] {message}")
        self.provider = provider
        self.status_code = status_code


class LLMRateLimitError(LLMProviderError):
    """Exception raised when an LLM provider exceeds rate limits or quotas (HTTP 429)."""


class LLMValidationError(LLMServiceError):
    """Exception raised when model output fails Pydantic schema validation."""


# =============================================================================
# Response & Metadata Models
# =============================================================================
class LLMResponse(BaseModel):
    """Metadata and raw content for an LLM execution."""

    content: str
    provider: str
    model: str
    latency_ms: float
    cached: bool = False
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Helper Utilities
# =============================================================================
def strip_markdown_json(text: str) -> str:
    """Extract and sanitize raw JSON from possible markdown fences or conversational wrappers."""
    if not text:
        return ""
    text = text.strip()

    # Pattern 1: Strip standard ```json ... ``` codeblocks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()

    # Pattern 2: Locate boundary between outermost '{' and '}' or '[' and ']'
    first_brace = text.find("{")
    first_bracket = text.find("[")

    if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
        last_bracket = text.rfind("]")
        if last_bracket != -1 and last_bracket > first_bracket:
            return text[first_bracket : last_bracket + 1]
    elif first_brace != -1:
        last_brace = text.rfind("}")
        if last_brace != -1 and last_brace > first_brace:
            return text[first_brace : last_brace + 1]

    return text


def build_cache_digest(
    provider: str,
    model: str,
    system_prompt: Optional[str],
    user_prompt: str,
    schema_name: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    """Compute deterministic SHA-256 digest for LLM caching."""
    seed = (
        f"{provider}|{model}|{system_prompt or ''}|{user_prompt}|"
        f"{schema_name or 'text'}|{round(temperature, 2)}"
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


# =============================================================================
# Abstract Base LLM Provider
# =============================================================================
class BaseLLMProvider(ABC):
    """Abstract interface defining required LLM capabilities."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'groq', 'gemini', 'mock')."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider dependencies and authentication credentials are ready."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate unstructured text completion."""

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[T, LLMResponse]:
        """Generate structured output validated against a Pydantic v2 schema."""


# =============================================================================
# Concrete Provider: Mock LLM Provider (Offline & Testing)
# =============================================================================
class MockLLMProvider(BaseLLMProvider):
    """Deterministic, zero-cost mock provider for testing and offline development."""

    def __init__(self, simulated_latency_ms: float = 1.0):
        self.simulated_latency_ms = simulated_latency_ms
        self.custom_responses: Dict[str, Any] = {}
        self.call_history: List[Dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def register_mock_response(self, prompt_substring: str, response: Any) -> None:
        """Register specific mock response for a matching prompt substring."""
        self.custom_responses[prompt_substring] = response

    def clear_mocks(self) -> None:
        """Clear custom registered mock responses and history."""
        self.custom_responses.clear()
        self.call_history.clear()

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        t0 = time.perf_counter()
        self.call_history.append(
            {
                "type": "text",
                "prompt": prompt,
                "system_prompt": system_prompt,
                "model": model or "mock-clinical-v1",
            }
        )

        for sub, resp in self.custom_responses.items():
            if sub in prompt:
                content = str(resp) if not isinstance(resp, str) else resp
                break
        else:
            content = (
                "Mock Clinical Assessment: Patient evaluation completed based on deterministic "
                "clinical formulas and baseline multi-agent observations. No acute emergency detected."
            )

        duration_ms = (time.perf_counter() - t0) * 1000 + self.simulated_latency_ms
        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model or "mock-clinical-v1",
            latency_ms=round(duration_ms, 2),
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
            total_tokens=len(prompt.split()) + len(content.split()),
            cached=False,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[T, LLMResponse]:
        t0 = time.perf_counter()
        self.call_history.append(
            {
                "type": "structured",
                "schema": schema.__name__,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "model": model or "mock-structured-v1",
            }
        )

        # Check for registered custom mock
        for sub, resp in self.custom_responses.items():
            if sub in prompt:
                if isinstance(resp, schema):
                    obj = resp
                elif isinstance(resp, dict):
                    obj = schema.model_validate(resp)
                elif isinstance(resp, str):
                    obj = schema.model_validate_json(strip_markdown_json(resp))
                else:
                    obj = self._synthesize_mock_instance(schema, prompt)
                break
        else:
            obj = self._synthesize_mock_instance(schema, prompt)

        raw_json = obj.model_dump_json()
        duration_ms = (time.perf_counter() - t0) * 1000 + self.simulated_latency_ms
        response = LLMResponse(
            content=raw_json,
            provider=self.provider_name,
            model=model or "mock-structured-v1",
            latency_ms=round(duration_ms, 2),
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(raw_json.split()),
            total_tokens=len(prompt.split()) + len(raw_json.split()),
            cached=False,
        )
        return obj, response

    def _synthesize_mock_instance(self, schema: Type[T], prompt: str) -> T:
        """Synthesize a valid mock instance of a Pydantic schema using intelligent field defaults."""
        data: Dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            if field_info.default is not None and not str(field_info.default).startswith("PydanticUndefined"):
                if field_info.default == [] and ("reasoning" in field_name or "evidence" in field_name or "challenge" in field_name):
                    pass
                else:
                    data[field_name] = field_info.default
                    continue
            if field_info.default_factory is not None:
                val = field_info.default_factory()
                if val == [] and ("reasoning" in field_name or "evidence" in field_name or "challenge" in field_name):
                    pass
                else:
                    data[field_name] = val
                    continue

            annotation = field_info.annotation
            origin = getattr(annotation, "__origin__", None)
            ann_str = str(annotation).lower()

            # 1. Lists
            if origin is list or "list" in ann_str:
                if "reasoning" in field_name:
                    data[field_name] = [
                        "Analyzed reported biomarkers and history indicators",
                        "Cross-referenced Framingham deterministic equation",
                        "Stratified confidence based on symptom progression",
                    ]
                elif "evidence" in field_name:
                    data[field_name] = [
                        "Systolic blood pressure >= 140 mmHg",
                        "BMI in overweight stratification range",
                    ]
                elif "challenge" in field_name:
                    data[field_name] = [
                        "Requires fasting lipid panel to rule out familial hypercholesterolemia",
                    ]
                else:
                    data[field_name] = ["Clinical observation item"]

            # 2. Dicts
            elif origin is dict or "dict" in ann_str:
                data[field_name] = {}

            # 3. Floats
            elif "float" in ann_str:
                if "confidence" in field_name:
                    data[field_name] = 84.5
                elif "weight" in field_name:
                    data[field_name] = 1.0
                else:
                    data[field_name] = 0.5

            # 4. Ints
            elif "int" in ann_str:
                if "progress" in field_name:
                    data[field_name] = 100
                else:
                    data[field_name] = 1

            # 5. Booleans
            elif "bool" in ann_str:
                data[field_name] = True

            # 6. Strings
            elif "str" in ann_str:
                if "role" in field_name:
                    data[field_name] = "Symptom Analysis Specialist"
                elif "urgency" in field_name:
                    data[field_name] = "moderate"
                elif "category" in field_name:
                    data[field_name] = "Cardiovascular Risk - Moderate"
                elif "finding" in field_name:
                    data[field_name] = (
                        "Clinical findings indicate moderate risk profile requiring lifestyle modification "
                        "and physician follow-up."
                    )
                elif "summary" in field_name:
                    data[field_name] = (
                        "Multi-agent assessment shows concordance across Framingham 10-year risk and FINDRISC score."
                    )
                elif field_name == "id" or field_name.endswith("_id"):
                    data[field_name] = "mock_node_01"
                elif field_name == "type":
                    data[field_name] = "symptom"
                elif field_name == "label":
                    data[field_name] = "Dyspnea On Exertion"
                elif field_name == "source":
                    data[field_name] = "mock_node_01"
                elif field_name == "target":
                    data[field_name] = "mock_node_02"
                else:
                    data[field_name] = f"Simulated {field_name} observation"
            else:
                data[field_name] = None

        return schema.model_validate(data)


# =============================================================================
# Concrete Provider: Groq LLM Provider (Primary Fast Inference)
# =============================================================================
class GroqLLMProvider(BaseLLMProvider):
    """High-performance Groq Cloud inference provider using Llama-3.3/3.1."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        primary_model: str = "llama-3.3-70b-versatile",
        fast_model: str = "llama-3.1-8b-instant",
        timeout: float = 30.0,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.groq_api_key
        self.primary_model = primary_model or settings.groq_model_primary
        self.fast_model = fast_model or settings.groq_model_fast
        self.timeout = timeout

        self._client: Optional[Any] = None
        if self.api_key and Groq is not None:
            try:
                self._client = Groq(api_key=self.api_key, timeout=self.timeout)
            except Exception as e:
                logger.warning("Failed to initialize Groq client: %s", e)
                self._client = None

    @property
    def provider_name(self) -> str:
        return "groq"

    def is_available(self) -> bool:
        return self._client is not None and bool(self.api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        if not self.is_available():
            raise LLMProviderError(self.provider_name, "Groq client is not configured or missing API key.")

        selected_model = model or self.primary_model
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        t0 = time.perf_counter()
        try:
            completion = self._client.chat.completions.create(  # type: ignore
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            self._handle_groq_exception(e)

        duration_ms = (time.perf_counter() - t0) * 1000
        content = completion.choices[0].message.content or ""
        usage = getattr(completion, "usage", None)

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=selected_model,
            latency_ms=round(duration_ms, 2),
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            cached=False,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[T, LLMResponse]:
        if not self.is_available():
            raise LLMProviderError(self.provider_name, "Groq client is not configured or missing API key.")

        selected_model = model or self.primary_model
        schema_json = json.dumps(schema.model_json_schema(), indent=2)

        base_system = (
            "You are a clinical decision-support AI within the MedOracle platform. "
            "You must respond ONLY with a single valid JSON object strictly complying with the following schema:\n"
            f"{schema_json}\n"
            "Do not output markdown codeblocks, notes, or conversational text. Return only valid raw JSON."
        )
        if system_prompt:
            combined_system = f"{system_prompt}\n\n{base_system}"
        else:
            combined_system = base_system

        messages = [
            {"role": "system", "content": combined_system},
            {"role": "user", "content": prompt},
        ]

        t0 = time.perf_counter()
        try:
            completion = self._client.chat.completions.create(  # type: ignore
                model=selected_model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            self._handle_groq_exception(e)

        duration_ms = (time.perf_counter() - t0) * 1000
        raw_text = completion.choices[0].message.content or "{}"
        cleaned_json = strip_markdown_json(raw_text)

        try:
            parsed_obj = schema.model_validate_json(cleaned_json)
        except Exception as err:
            logger.error("Groq JSON schema validation failed: %s | Raw output: %s", err, raw_text)
            raise LLMValidationError(f"Failed to validate Groq response against {schema.__name__}: {err}") from err

        usage = getattr(completion, "usage", None)
        response = LLMResponse(
            content=cleaned_json,
            provider=self.provider_name,
            model=selected_model,
            latency_ms=round(duration_ms, 2),
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            cached=False,
        )
        return parsed_obj, response

    def _handle_groq_exception(self, exc: Exception) -> None:
        """Map Groq client exceptions to unified LLMService errors."""
        err_msg = str(exc)
        err_lower = err_msg.lower()

        if "rate limit" in err_lower or "429" in err_lower or "quota" in err_lower:
            logger.warning("Groq rate limit encountered: %s", exc)
            raise LLMRateLimitError(self.provider_name, err_msg, status_code=429) from exc

        if "timeout" in err_lower or "connection" in err_lower:
            logger.warning("Groq connection timeout/transient error: %s", exc)
            raise LLMRateLimitError(self.provider_name, f"Transient network error: {err_msg}") from exc

        logger.error("Groq API error encountered: %s", exc)
        raise LLMProviderError(self.provider_name, err_msg) from exc


# =============================================================================
# Concrete Provider: Gemini LLM Provider (Secondary Fallback)
# =============================================================================
class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini Flash inference provider using the official google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        timeout: float = 30.0,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model_fallback
        self.timeout = timeout

        self._client: Optional[Any] = None
        if self.api_key and genai is not None:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to initialize Gemini client: %s", e)
                self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return self._client is not None and bool(self.api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        if not self.is_available():
            raise LLMProviderError(self.provider_name, "Gemini client is not configured or missing API key.")

        selected_model = model or self.model_name
        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        t0 = time.perf_counter()
        try:
            resp = self._client.models.generate_content(  # type: ignore
                model=selected_model,
                contents=prompt,
                config=config,
            )
        except Exception as e:
            self._handle_gemini_exception(e)

        duration_ms = (time.perf_counter() - t0) * 1000
        content = resp.text or ""
        usage = getattr(resp, "usage_metadata", None)

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=selected_model,
            latency_ms=round(duration_ms, 2),
            prompt_tokens=getattr(usage, "prompt_token_count", None),
            completion_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
            cached=False,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[T, LLMResponse]:
        if not self.is_available():
            raise LLMProviderError(self.provider_name, "Gemini client is not configured or missing API key.")

        selected_model = model or self.model_name
        base_instruction = (
            "You are a clinical decision-support AI within the MedOracle platform. "
            "You must return ONLY a structured JSON response matching the requested schema."
        )
        combined_system = f"{system_prompt}\n\n{base_instruction}" if system_prompt else base_instruction

        config = genai_types.GenerateContentConfig(
            system_instruction=combined_system,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=schema,
        )

        t0 = time.perf_counter()
        try:
            resp = self._client.models.generate_content(  # type: ignore
                model=selected_model,
                contents=prompt,
                config=config,
            )
        except Exception as e:
            self._handle_gemini_exception(e)

        duration_ms = (time.perf_counter() - t0) * 1000
        raw_text = resp.text or "{}"
        cleaned_json = strip_markdown_json(raw_text)

        try:
            parsed_obj = schema.model_validate_json(cleaned_json)
        except Exception as err:
            logger.error("Gemini JSON schema validation failed: %s | Raw output: %s", err, raw_text)
            raise LLMValidationError(f"Failed to validate Gemini response against {schema.__name__}: {err}") from err

        usage = getattr(resp, "usage_metadata", None)
        response = LLMResponse(
            content=cleaned_json,
            provider=self.provider_name,
            model=selected_model,
            latency_ms=round(duration_ms, 2),
            prompt_tokens=getattr(usage, "prompt_token_count", None),
            completion_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
            cached=False,
        )
        return parsed_obj, response

    def _handle_gemini_exception(self, exc: Exception) -> None:
        """Map Gemini client exceptions to unified LLMService errors."""
        err_msg = str(exc)
        err_lower = err_msg.lower()

        if "429" in err_lower or "resource_exhausted" in err_lower or "quota" in err_lower:
            logger.warning("Gemini quota/rate limit encountered: %s", exc)
            raise LLMRateLimitError(self.provider_name, err_msg, status_code=429) from exc

        if "timeout" in err_lower or "deadline" in err_lower or "connection" in err_lower:
            logger.warning("Gemini network timeout/transient error: %s", exc)
            raise LLMRateLimitError(self.provider_name, f"Transient network error: {err_msg}") from exc

        logger.error("Gemini API error encountered: %s", exc)
        raise LLMProviderError(self.provider_name, err_msg) from exc


# =============================================================================
# Unified LLM Service (Orchestrator with Routing, Caching & Failover)
# =============================================================================
class LLMService:
    """Enterprise multi-provider LLM orchestrator for MedOracle.

    Manages:
    - Primary provider (Groq) with secondary fallback (Gemini Flash) and offline mock.
    - Redis / In-memory caching for both unstructured text and structured Pydantic schemas.
    - Exponential backoff retry on transient errors or HTTP 429 rate limits.
    - Failover chaining when a provider exhausts retries.
    """

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        mock_provider: Optional[MockLLMProvider] = None,
        groq_provider: Optional[GroqLLMProvider] = None,
        gemini_provider: Optional[GeminiLLMProvider] = None,
    ):
        self.settings = get_settings()
        self.cache_mgr = cache_manager or get_cache_manager()

        self.mock_provider = mock_provider or MockLLMProvider()
        self.groq_provider = groq_provider or GroqLLMProvider(
            api_key=self.settings.groq_api_key,
            primary_model=self.settings.groq_model_primary,
            fast_model=self.settings.groq_model_fast,
            timeout=self.settings.llm_timeout,
        )
        self.gemini_provider = gemini_provider or GeminiLLMProvider(
            api_key=self.settings.gemini_api_key,
            model_name=self.settings.gemini_model_fallback,
            timeout=self.settings.llm_timeout,
        )

        self._providers: Dict[str, BaseLLMProvider] = {
            "mock": self.mock_provider,
            "groq": self.groq_provider,
            "gemini": self.gemini_provider,
        }

    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        """Resolve specific or default LLM provider."""
        target = (name or self.settings.llm_provider).lower()
        if target in self._providers:
            return self._providers[target]
        logger.warning("Unrecognized provider '%s'. Defaulting to mock.", target)
        return self.mock_provider

    def get_provider_status(self) -> Dict[str, Any]:
        """Return diagnostic health and readiness status for all configured providers."""
        return {
            "configured_default": self.settings.llm_provider,
            "cache_backend": self.cache_mgr.backend_type,
            "cache_enabled": self.cache_mgr.enabled,
            "providers": {
                "groq": {
                    "available": self.groq_provider.is_available(),
                    "primary_model": self.settings.groq_model_primary,
                    "fast_model": self.settings.groq_model_fast,
                },
                "gemini": {
                    "available": self.gemini_provider.is_available(),
                    "fallback_model": self.settings.gemini_model_fallback,
                },
                "mock": {
                    "available": True,
                    "simulated_latency_ms": self.mock_provider.simulated_latency_ms,
                },
            },
        }

    # -------------------------------------------------------------------------
    # Public Execution Methods
    # -------------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
    ) -> LLMResponse:
        """Generate text completion with caching and failover routing."""
        configured_provider = (provider or self.settings.llm_provider).lower()
        target_model = model or self._resolve_default_model(configured_provider)

        # 1. Check Redis / In-memory Cache
        cache_key = None
        if use_cache and self.cache_mgr.enabled:
            digest = build_cache_digest(
                provider=configured_provider,
                model=target_model,
                system_prompt=system_prompt,
                user_prompt=prompt,
                schema_name="text",
                temperature=temperature,
            )
            cache_key = self.cache_mgr.build_key("llm", "text", digest)
            cached_data = self.cache_mgr.get(cache_key)
            if cached_data is not None and isinstance(cached_data, dict):
                logger.info("LLM text response cache HIT [%s]", cache_key)
                cached_data["cached"] = True
                cached_data["latency_ms"] = 0.0
                return LLMResponse.model_validate(cached_data)

        # 2. Build execution chain with failover
        chain = self._resolve_execution_chain(provider)

        # 3. Execute with retries & failover
        response, active_provider = self._execute_text_chain(
            chain=chain,
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 4. Save successful output to cache
        if use_cache and cache_key and self.cache_mgr.enabled:
            self.cache_mgr.set(
                key=cache_key,
                value=response.model_dump(),
                ttl=self.settings.llm_cache_ttl,
            )

        return response

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        use_cache: bool = True,
    ) -> Tuple[T, LLMResponse]:
        """Generate structured output validated against a Pydantic schema with caching and failover."""
        configured_provider = (provider or self.settings.llm_provider).lower()
        target_model = model or self._resolve_default_model(configured_provider)

        # 1. Check Redis / In-memory Cache
        cache_key = None
        if use_cache and self.cache_mgr.enabled:
            digest = build_cache_digest(
                provider=configured_provider,
                model=target_model,
                system_prompt=system_prompt,
                user_prompt=prompt,
                schema_name=schema.__name__,
                temperature=temperature,
            )
            cache_key = self.cache_mgr.build_key("llm", "structured", digest)
            cached_payload = self.cache_mgr.get(cache_key)
            if cached_payload is not None and isinstance(cached_payload, dict):
                try:
                    obj_dict = cached_payload.get("data")
                    resp_dict = cached_payload.get("response", {})
                    if obj_dict is not None:
                        obj = schema.model_validate(obj_dict)
                        resp_dict["cached"] = True
                        resp_dict["latency_ms"] = 0.0
                        logger.info("LLM structured cache HIT for %s [%s]", schema.__name__, cache_key)
                        return obj, LLMResponse.model_validate(resp_dict)
                except Exception as e:
                    logger.warning("Corrupted cached structured payload (%s); recomputing.", e)

        # 2. Build execution chain with failover
        chain = self._resolve_execution_chain(provider)

        # 3. Execute with retries & failover
        obj, response, active_provider = self._execute_structured_chain(
            chain=chain,
            prompt=prompt,
            schema=schema,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
        )

        # 4. Save successful output to cache
        if use_cache and cache_key and self.cache_mgr.enabled:
            self.cache_mgr.set(
                key=cache_key,
                value={
                    "data": obj.model_dump(),
                    "response": response.model_dump(),
                },
                ttl=self.settings.llm_cache_ttl,
            )

        return obj, response

    # -------------------------------------------------------------------------
    # Chain & Failover Execution Internals
    # -------------------------------------------------------------------------
    def _resolve_default_model(self, provider_name: str) -> str:
        if provider_name == "groq":
            return self.settings.groq_model_primary
        if provider_name == "gemini":
            return self.settings.gemini_model_fallback
        return "mock-clinical-v1"

    def _resolve_execution_chain(self, explicit_provider: Optional[str]) -> List[BaseLLMProvider]:
        """Resolve ordered list of providers for failover routing."""
        if explicit_provider:
            return [self.get_provider(explicit_provider)]

        default = self.settings.llm_provider.lower()
        if default == "mock":
            return [self.mock_provider]
        if default == "groq":
            chain = [self.groq_provider, self.gemini_provider]
        elif default == "gemini":
            chain = [self.gemini_provider, self.groq_provider]
        else:
            chain = [self.mock_provider]

        # In development / testing environments, if all configured providers are unavailable,
        # append mock provider to guarantee zero-downtime offline functionality.
        if self.settings.app_env in ("development", "test"):
            chain.append(self.mock_provider)

        return chain

    def _execute_text_chain(
        self,
        chain: List[BaseLLMProvider],
        prompt: str,
        system_prompt: Optional[str],
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> Tuple[LLMResponse, str]:
        errors: List[str] = []

        for provider in chain:
            if not provider.is_available():
                logger.debug("Provider '%s' unavailable (missing credentials); skipping.", provider.provider_name)
                continue

            for attempt in range(self.settings.llm_max_retries + 1):
                try:
                    response = provider.generate_text(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return response, provider.provider_name
                except LLMRateLimitError as rle:
                    errors.append(f"{provider.provider_name} (attempt {attempt + 1}): {rle}")
                    if attempt < self.settings.llm_max_retries:
                        backoff = self.settings.llm_retry_backoff * (2**attempt)
                        logger.warning(
                            "[%s] Rate limit hit. Backing off for %.2fs (attempt %d/%d)...",
                            provider.provider_name,
                            backoff,
                            attempt + 1,
                            self.settings.llm_max_retries,
                        )
                        time.sleep(backoff)
                    else:
                        logger.warning(
                            "[%s] Rate limits exhausted after %d attempts. Failing over to next provider.",
                            provider.provider_name,
                            self.settings.llm_max_retries + 1,
                        )
                        break
                except Exception as err:
                    errors.append(f"{provider.provider_name}: {err}")
                    logger.warning(
                        "[%s] Call failed (%s). Failing over to next provider.",
                        provider.provider_name,
                        err,
                    )
                    break

        raise LLMServiceError(f"All LLM providers in execution chain failed: {' | '.join(errors)}")

    def _execute_structured_chain(
        self,
        chain: List[BaseLLMProvider],
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str],
        model: Optional[str],
        temperature: float,
    ) -> Tuple[T, LLMResponse, str]:
        errors: List[str] = []

        for provider in chain:
            if not provider.is_available():
                logger.debug("Provider '%s' unavailable (missing credentials); skipping.", provider.provider_name)
                continue

            for attempt in range(self.settings.llm_max_retries + 1):
                try:
                    obj, response = provider.generate_structured(
                        prompt=prompt,
                        schema=schema,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=temperature,
                    )
                    return obj, response, provider.provider_name
                except LLMRateLimitError as rle:
                    errors.append(f"{provider.provider_name} (attempt {attempt + 1}): {rle}")
                    if attempt < self.settings.llm_max_retries:
                        backoff = self.settings.llm_retry_backoff * (2**attempt)
                        logger.warning(
                            "[%s] Rate limit hit. Backing off for %.2fs (attempt %d/%d)...",
                            provider.provider_name,
                            backoff,
                            attempt + 1,
                            self.settings.llm_max_retries,
                        )
                        time.sleep(backoff)
                    else:
                        logger.warning(
                            "[%s] Rate limits exhausted after %d attempts. Failing over to next provider.",
                            provider.provider_name,
                            self.settings.llm_max_retries + 1,
                        )
                        break
                except Exception as err:
                    errors.append(f"{provider.provider_name}: {err}")
                    logger.warning(
                        "[%s] Structured call failed (%s). Failing over to next provider.",
                        provider.provider_name,
                        err,
                    )
                    break

        raise LLMServiceError(f"All LLM providers failed for {schema.__name__}: {' | '.join(errors)}")


# =============================================================================
# Global Singleton Accessor
# =============================================================================
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Return singleton LLMService orchestrator."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance


def reset_llm_service() -> None:
    """Reset singleton instance (useful for unit test isolation)."""
    global _llm_service_instance
    _llm_service_instance = None
