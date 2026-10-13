# MedOracle Backend: Implementation Plan & Roadmap

This document outlines the step-by-step engineering roadmap for the MedOracle backend service, adapted from the project brief (`docs/architecture/PROJECT_BRIEF.md`) and project rules (`.agent/rules/medoracle-backend.md`).

---

## Architectural Principles & Locked Decisions

1. **Pure Python Clinical Foundations**:
   - Validated clinical formulas (Framingham 10-year CVD risk, FINDRISC diabetes risk, CKD-EPI 2021 eGFR) serve as the deterministic mathematical backbone.
   - LLM agents build explanatory, contextual, and debate layers on top of clinical scores.
2. **Multi-Agent Consensus & Debate (Core Research Contribution)**:
   - Specialised agents: Symptom, Medical History, Laboratory, and Risk Prediction.
   - Governed by a 5-step consensus protocol: (1) Evidence submission, (2) Contradiction detection, (3) Challenge round, (4) Confidence adjustment, (5) Consensus resolution.
   - Structured JSON output contract for every agent: `role`, `findings`, `confidence` (0–100), `reasoning_chain`, `evidence`, `challenges`.
   - Agents never see each other's prompts, only outputs and confidence scores (anti-sycophancy).
3. **LLM Routing & Resilience**:
   - Primary: Groq (`llama-3.3-70b-versatile` for complex reasoning/debate, `llama-3.1-8b-instant` for structured extraction).
   - Fallback: Google Gemini Flash (`gemini-2.5-flash` or current stable flash endpoint).
   - Mock provider for all unit/integration tests (zero external network calls during CI/testing).
4. **Data & Persistence**:
   - SQLAlchemy 2.0 with sync engine and `psycopg` 3 for PostgreSQL (Supabase in production).
   - Generic `JSON` column types to allow test execution on in-memory SQLite without dialect incompatibility.
   - Repository pattern: all database queries encapsulated in `app/database/repositories.py`.
5. **Asynchronous Execution**:
   - Native FastAPI `BackgroundTasks` with polling status on `analysis_sessions` (Celery & Redis deferred to Step 13 hardening due to native Windows constraints).
6. **Security & Auth**:
   - Custom JWT auth (`python-jose`) with direct `bcrypt` password hashing (no `passlib`).

---

## Detailed Step-by-Step Roadmap

### Step 0: Audit & Plan (Current Step)
- **Goal**: Audit existing repository structure, reconcile requirements vs virtual environment, write skeleton contracts, and establish project baseline.
- **Artifacts**: `IMPLEMENTATION_PLAN.md`, `PROJECT_STATUS.md`, `API_CONTRACT.md`.
- **Definition of Done**: All planning documents populated; environment differences catalogued; ready for Step 1.

---

### Step 1: App Foundation
- **Goal**: Initialize the FastAPI application shell, configuration management, CORS, structured error handlers, and health probe.
- **Target Files**:
  - `backend/app/core/config.py` (Pydantic Settings reading `.env`)
  - `backend/app/main.py` (FastAPI application factory, middleware, routers)
  - `backend/app/api/router.py` (Top-level API router aggregator)
  - `backend/app/api/v1/__init__.py` (V1 prefix router mounting)
  - `backend/.env.example` (Updated with standardized variable keys)
  - `scripts/run_backend.bat` & `scripts/setup_backend.bat` (Verified runnable commands)
- **Dependencies**: `fastapi`, `uvicorn[standard]`, `pydantic-settings`.
- **Testing**:
  - `backend/tests/unit/test_config.py`: Configuration loading, default values, env overrides.
  - `backend/tests/integration/test_health.py`: HTTP GET `/health` and root endpoints.
- **Definition of Done**: `pytest` passes; `uvicorn app.main:app` boots cleanly; `scripts\run_backend.bat` starts the service.

---

### Step 2: Database & Migrations
- **Goal**: Implement SQLAlchemy ORM models, session management, migration environment via Alembic, and database repositories.
- **Target Files**:
  - `backend/app/database/session.py` (Engine, sessionmaker, `get_db` dependency)
  - `backend/app/database/models.py` (Users, PatientProfile, MedicalHistory, SymptomReport, LabResult, AnalysisSession, AgentOutput, RiskResult, Doctor)
  - `backend/app/database/repositories.py` (Data access layer wrapping all queries)
  - `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/script.py.mako`, `backend/migrations/versions/`
- **Dependencies**: `sqlalchemy`, `psycopg[binary]`, `alembic`.
- **Testing**:
  - `backend/tests/unit/test_database.py`: In-memory SQLite table creation, CRUD repository operations.
- **Definition of Done**: Alembic migration generated and executable; repositories tested with clean rollbacks on SQLite.

---

### Step 3: Authentication & Security
- **Goal**: Implement secure user registration, credential verification, JWT access/refresh token generation, and FastAPI security dependencies.
- **Target Files**:
  - `backend/app/core/security.py` (Password hashing using `bcrypt`, JWT encoding/decoding)
  - `backend/app/schemas/auth.py` (Token schemas, UserRegister, UserLogin, UserResponse)
  - `backend/app/api/v1/auth.py` (`/register`, `/login`, `/refresh`, `/me`)
- **Dependencies**: `python-jose[cryptography]`, `bcrypt`.
- **Testing**:
  - `backend/tests/unit/test_security.py`: Password hashing/verifying, token expiration, tamper rejection.
  - `backend/tests/integration/test_auth_api.py`: Registration, login, token refresh, `/me` authenticated round-trip.
- **Definition of Done**: Happy path and failure cases (expired token, wrong password, duplicate email) thoroughly tested and passing.

---

### Step 4: Patient Data APIs
- **Goal**: Provide CRUD endpoints for patient profiles, medical/family history, symptom reports, and lab results, enforcing strict user tenant isolation.
- **Target Files**:
  - `backend/app/schemas/patient.py`, `backend/app/schemas/symptoms.py`, `backend/app/schemas/laboratory.py`
  - `backend/app/api/v1/symptoms.py`, `backend/app/api/v1/medical_history.py`, `backend/app/api/v1/laboratory.py`
  - `backend/app/database/repositories.py` (Extended with patient queries)
- **Testing**:
  - `backend/tests/integration/test_patient_data.py`: Multi-user isolation test (User A cannot read or modify User B's records), validation errors on invalid ranges.
- **Definition of Done**: All patient data endpoints protected and isolated per user; full validation tests pass.

---

### Step 5: Clinical Risk Models (Deterministic Core)
- **Goal**: Implement exact published clinical equations in pure Python with complete academic citations and no LLM dependencies.
- **Target Files**:
  - `backend/app/clinical/cardiovascular.py` (Framingham 10-Year General Cardiovascular Risk Profile, D'Agostino et al., 2008)
  - `backend/app/clinical/diabetes.py` (FINDRISC - Finnish Diabetes Risk Score, Lindström & Tuomilehto, 2003)
  - `backend/app/clinical/kidney.py` (CKD-EPI 2021 Creatinine Equation, Inker et al., 2021)
- **Outputs**: Quantified numerical score, risk category/stratification, list of missing/assumed parameters, and clinical disclaimer.
- **Testing**:
  - `backend/tests/unit/test_clinical_models.py`: Unit tests validating output against worked examples from original published papers and clinical calculators.
- **Definition of Done**: Worked test cases match published figures to within rounding precision.

---

### Step 6: LLM Service & Fallback Routing
- **Goal**: Build unified LLM interface with structured Pydantic JSON output, automatic retry with exponential backoff, Groq -> Gemini fallback, and a deterministic Mock provider.
- **Target Files**:
  - `backend/app/services/llm_service.py` (LLMProvider interface, GroqProvider, GeminiProvider, MockLLMProvider)
  - `backend/app/core/config.py` (API keys, model IDs, temperature, timeouts)
  - `backend/.env.example`
- **Dependencies**: `groq`, `google-genai` (pinned).
- **Testing**:
  - `backend/tests/unit/test_llm_service.py`: Schema validation, mock responses, fallback triggering on simulated network failure.
- **Definition of Done**: Fallback and JSON schema enforcement pass unit tests with 0 network calls.

---

### Step 7: Agent Base & Domain Agents
- **Goal**: Define unified Agent base class and domain agents (Symptom, Medical History, Laboratory, Risk Prediction) producing standardized structured outputs.
- **Target Files**:
  - `backend/app/agents/base.py` (Shared agent output contract: role, findings, confidence 0-100, reasoning chain, evidence, challenges)
  - `backend/app/agents/symptom_agent.py`
  - `backend/app/agents/medical_history_agent.py`
  - `backend/app/agents/laboratory_agent.py`
  - `backend/app/agents/risk_prediction_agent.py` (integrates Step 5 clinical calculators with agent findings)
- **Testing**:
  - `backend/tests/unit/test_agents.py`: Deterministic fallback operation (when LLM is disabled) and mock LLM reasoning.
- **Definition of Done**: All 4 agents return valid structured output schemas conforming to project rules.

---

### Step 8: LangGraph Pipeline Orchestration
- **Goal**: Wire domain agents into a directed LangGraph workflow executing data extraction agents in parallel before aggregating into risk prediction.
- **Target Files**:
  - `backend/app/graph/state.py` (Typed shared state representation)
  - `backend/app/graph/nodes.py` (Node execution wrappers with error boundaries)
  - `backend/app/graph/workflow.py` (Graph builder, parallel fan-out / fan-in)
- **Dependencies**: `langgraph`, `langchain-core`.
- **Testing**:
  - `backend/tests/unit/test_graph_workflow.py`: Execution of full graph with mock agents; verification that failure in one agent does not crash pipeline.
- **Definition of Done**: State transitions verify proper parallel execution and clean aggregation.

---

### Step 9: Consensus & Debate Framework (Core Research Contribution)
- **Goal**: Implement the 5-step consensus debate protocol to identify contradictions, exchange challenges, adjust confidences, and formulate an explainable consensus verdict.
- **Target Files**:
  - `backend/app/agents/consensus_agent.py`
  - `backend/app/graph/debate_nodes.py`
  - `backend/app/graph/workflow.py` (Integration of debate loop)
- **Testing**:
  - `backend/tests/unit/test_consensus_debate.py`: Hand-built contradictory agent outputs (e.g. high lab markers vs low symptom severity); verification of contradiction detection, confidence adjustment bounded within rounds, and full debate transcript capture.
- **Definition of Done**: Deterministic contradiction detection and multi-turn debate successfully produce resolution without infinite looping.

---

### Step 10: Explainability, Forecasting, Counterfactuals & Doctors
- **Goal**: Build reasoning graph export for Flutter (`graphview`), 30-day/6-month/1-year trajectory forecast, counterfactual lifestyle simulator, and specialty-based doctor matching.
- **Target Files**:
  - `backend/app/agents/explainability_agent.py` (Node-and-edge JSON graph builder)
  - `backend/app/forecasting/trajectory.py` & `backend/app/agents/disease_trajectory_agent.py`
  - `backend/app/counterfactual/simulator.py` & `backend/app/agents/counterfactual_agent.py` (Walking, diet change, smoking cessation)
  - `backend/app/doctors/recommendations.py` & `backend/app/agents/doctor_recommendation_agent.py` (Specialty and proximity ranking)
- **Testing**:
  - `backend/tests/unit/test_forecasting.py`, `test_counterfactual.py`, `test_doctor_recommendations.py`.
- **Definition of Done**: Valid JSON graph structure generated; 3 counterfactual interventions calculated; doctor ranking tested with sample directory.

---

### Step 11: Analysis Orchestration API
- **Goal**: Expose end-to-end analysis endpoints with async job dispatching, polling status, and comprehensive results retrieval.
- **Target Files**:
  - `backend/app/services/analysis_service.py`, `backend/app/services/prediction_service.py`
  - `backend/app/schemas/analysis.py`, `backend/app/schemas/risk.py`
  - `backend/app/api/v1/analysis.py`, `backend/app/api/v1/risk.py`, `backend/app/api/v1/doctors.py`
  - `API_CONTRACT.md` (Finalized specification for Flutter team)
- **Testing**:
  - `backend/tests/integration/test_analysis_pipeline.py`: Start analysis -> Poll pending/complete -> Retrieve full structured payload.
- **Definition of Done**: End-to-end analysis lifecycle executes asynchronously without blocking the web event loop.

---

### Step 12: Public Dataset Validation
- **Goal**: Validate clinical formulas and agent pipeline outputs against standard medical benchmark datasets.
- **Target Files**:
  - `backend/app/ml/preprocessing/`, `backend/app/ml/evaluation/`, `backend/app/ml/model_registry.py`
  - `backend/scripts/evaluate_models.py`
  - `DATASET_REGISTER.md`, `MODEL_REGISTER.md`
- **Datasets**: UCI Heart Disease, PIMA Indians Diabetes, Framingham Heart Study.
- **Testing**:
  - `backend/tests/ml/`: Automated validation test verifying clinical sensitivity, specificity, and calibration.
- **Definition of Done**: Transparent metrics recorded in registers, highlighting exact performance bounds.

---

### Step 13: Hardening & Production Readiness
- **Goal**: Production configuration, security hardening, rate limiting, request size limits, Docker packaging, and CI workflows.
- **Target Files**:
  - `backend/Dockerfile`, `backend/docker-compose.yml`
  - `.github/workflows/backend-ci.yml`
  - Security review, structured logging, Render deployment configuration, final documentation.
- **Definition of Done**: App container builds; automated CI passes linting and test suites.
