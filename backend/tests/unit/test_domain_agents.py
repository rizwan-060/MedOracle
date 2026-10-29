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


# =============================================================================
# 5. SymptomAgent Specific Unit Tests
# =============================================================================
from app.agents.symptom_agent import ACUTE_RED_FLAGS, SymptomAgent


@pytest.fixture
def symptom_agent(mock_llm_service: LLMService) -> SymptomAgent:
    """Instantiated SymptomAgent with mock LLM backend."""
    return SymptomAgent(llm_service=mock_llm_service)


def test_symptom_agent_properties(symptom_agent: SymptomAgent):
    """Verify SymptomAgent role and persona guidelines."""
    assert symptom_agent.agent_role == "Symptom Analysis Specialist"
    assert "RED FLAGS" in symptom_agent.system_prompt
    assert "Symptom Analysis Specialist" in symptom_agent.system_prompt


def test_symptom_agent_validation_empty_context(symptom_agent: SymptomAgent):
    """Verify that context missing any symptom signal is rejected."""
    with pytest.raises(AgentExecutionError) as exc:
        symptom_agent.analyze({})

    assert "Context must provide at least one symptom source" in str(exc.value)


def test_symptom_agent_red_flag_prompt_escalation(symptom_agent: SymptomAgent):
    """Verify that acute emergency symptoms trigger safety escalation in the briefing prompt."""
    context = {
        "symptoms": ["chest pain", "severe diaphoresis"],
        "severity": 9,
        "duration_days": 1,
        "notes": "Patient collapsed with substernal pressure",
    }
    prompt = symptom_agent.build_prompt(context)

    assert "AUTOMATED SAFETY ESCALATION" in prompt
    assert "Chest Pain" in prompt
    assert "Substernal Pressure" in prompt


def test_symptom_agent_nlp_and_ml_integration_prompt(symptom_agent: SymptomAgent):
    """Verify that affirmed/negated NLP entities and ML differential candidates are structured into prompt."""
    context = {
        "symptoms": ["fatigue"],
        "patient_demographics": {"age": 58, "sex": "female"},
        "nlp_entities": [
            {"canonical_symptom": "fatigue", "negated": False, "confidence": 0.95},
            {"canonical_symptom": "fever", "negated": True, "confidence": 0.90},
        ],
        "differential_candidates": [
            {"disease": "Type 2 Diabetes", "probability": 0.72},
            {"disease": "Coronary Artery Disease", "probability": 0.18},
        ],
    }
    prompt = symptom_agent.build_prompt(context)

    assert "Age: 58 | Biological Sex: female" in prompt
    assert "Affirmed Present:** fatigue (conf: 95%)" in prompt
    assert "Explicitly Denied (NegEx Negated):** fever" in prompt
    assert "Type 2 Diabetes**: 72.0%" in prompt


def test_symptom_agent_execution_contract(symptom_agent: SymptomAgent):
    """Verify that SymptomAgent executes and produces valid AgentOutputResponse."""
    context = {
        "symptoms": ["dyspnea", "fatigue"],
        "severity": 6,
        "duration_days": 7,
        "notes": "Shortness of breath on walking two blocks.",
    }
    output = symptom_agent.analyze(context)

    assert isinstance(output, AgentOutputResponse)
    assert output.agent_role == "Symptom Analysis Specialist"
    assert 0.0 <= output.confidence <= 100.0
    assert len(output.findings) > 0
    assert len(output.reasoning_chain) > 0
    assert len(output.evidence) > 0
    assert len(output.challenges) > 0
    assert output.metadata_payload["provider_used"] == "mock"
    assert output.metadata_payload["cached"] is False


# =============================================================================
# 6. MedicalHistoryAgent Specific Unit Tests
# =============================================================================
from app.agents.medical_history_agent import MedicalHistoryAgent


@pytest.fixture
def history_agent(mock_llm_service: LLMService) -> MedicalHistoryAgent:
    """Instantiated MedicalHistoryAgent with mock LLM backend."""
    return MedicalHistoryAgent(llm_service=mock_llm_service)


def test_medical_history_agent_properties(history_agent: MedicalHistoryAgent):
    """Verify MedicalHistoryAgent role and clinical guidelines."""
    assert history_agent.agent_role == "Medical History Specialist"
    assert "PREMATURE CORONARY ARTERY DISEASE" in history_agent.system_prompt
    assert "Medical History Specialist" in history_agent.system_prompt


def test_medical_history_agent_validation_empty_context(history_agent: MedicalHistoryAgent):
    """Verify that context without any historical data raises AgentExecutionError."""
    with pytest.raises(AgentExecutionError) as exc:
        history_agent.analyze({})

    assert "Context must provide at least one historical source" in str(exc.value)


def test_medical_history_agent_premature_cad_alert(history_agent: MedicalHistoryAgent):
    """Verify that premature first-degree CAD is flagged in the clinical briefing prompt."""
    context = {
        "chronic_conditions": ["hypertension"],
        "current_medications": [{"name": "Amlodipine", "dosage": "5mg", "frequency": "daily"}],
        "family_history": [
            {"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 48},
        ],
        "lifestyle": {"smoking_status": "former", "activity_level": "moderate"},
    }
    prompt = history_agent.build_prompt(context)

    assert "Premature First-Degree CAD Detected" in prompt
    assert "Father (Myocardial Infarction at age 48)" in prompt


def test_medical_history_agent_cardiometabolic_triad_alert(history_agent: MedicalHistoryAgent):
    """Verify that co-existing HTN, Diabetes, and Dyslipidemia trigger Cardiometabolic Triad alert."""
    context = {
        "chronic_conditions": ["hypertension", "type_2_diabetes", "hyperlipidemia"],
        "current_medications": [
            {"name": "Metformin", "dosage": "1000mg", "frequency": "twice daily"},
            {"name": "Lisinopril", "dosage": "20mg", "frequency": "daily"},
        ],
        "lifestyle": {"smoking_status": "current_smoker", "activity_level": "sedentary"},
    }
    prompt = history_agent.build_prompt(context)

    assert "Cardiometabolic Triad Identified" in prompt
    assert "Hypertension, Diabetes, and Dyslipidemia" in prompt


def test_medical_history_agent_execution_contract(history_agent: MedicalHistoryAgent):
    """Verify that MedicalHistoryAgent executes and produces valid AgentOutputResponse."""
    context = {
        "chronic_conditions": ["hypertension"],
        "current_medications": [{"name": "Losartan", "dosage": "50mg", "frequency": "once daily"}],
        "family_history": [{"relative": "mother", "condition": "stroke", "age_at_onset": 72}],
        "smoking_status": "never",
        "activity_level": "moderate",
        "notes": "Patient diagnosed with stage 1 hypertension in 2021, good medication compliance.",
        "active_symptoms": ["headache"],
    }
    output = history_agent.analyze(context)

    assert isinstance(output, AgentOutputResponse)
    assert output.agent_role == "Medical History Specialist"
    assert 0.0 <= output.confidence <= 100.0
    assert len(output.findings) > 0
    assert len(output.reasoning_chain) > 0
    assert len(output.evidence) > 0
    assert len(output.challenges) > 0
    assert output.metadata_payload["provider_used"] == "mock"
    assert output.metadata_payload["cached"] is False

