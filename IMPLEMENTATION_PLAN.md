# MedOracle Backend: Implementation Plan & Roadmap

This document outlines the step-by-step engineering roadmap for the MedOracle backend service, adapted from the project brief (`docs/architecture/PROJECT_BRIEF.md`), project rules (`.agent/rules/medoracle-backend.md`), and updated architecture directives.

---

## Architectural Principles & Locked Decisions

1. **Schema-First Foundation (Step 2 Priority)**:
   - Complete data model definition precedes downstream API and agent logic.
   - All relational entities (Users, PatientProfiles, MedicalHistories, SymptomReports, LabResults, AnalysisSessions, AgentOutputs, RiskResults, Doctors, TrainedModels) are mapped to SQLAlchemy 2.0 ORM models and Pydantic v2 domain schemas.
   - Generic `JSON` column types allow SQLite test execution while supporting PostgreSQL/Supabase in production.
   - **Schema Documentation Artifact**: A dedicated specification (`docs/architecture/DATABASE_SCHEMA.md`) documents all tables, column types, constraints, entity relationships in tabular form, and concrete example data rows.
2. **Dual Quantitative Backbone: Clinical Equations + Supervised ML Models**:
   - **Deterministic Clinical Formulas**: Framingham 10-year CVD risk, FINDRISC diabetes risk, CKD-EPI 2021 eGFR serve as cited, transparent clinical formulas.
   - **Supervised ML Models**: Models trained on public benchmark datasets (UCI Heart Disease, PIMA Indians Diabetes, Kaggle Disease-Symptom dataset) provide data-driven probability estimates and feature importance scores.
   - Both quantitative streams feed directly into the Risk Prediction Agent.
3. **Multi-Agent Consensus & Debate (Core Research Contribution)**:
   - Specialized agents: Symptom, Medical History, Laboratory, and Risk Prediction.
   - 5-step debate protocol: (1) Evidence submission, (2) Contradiction detection, (3) Challenge round, (4) Confidence adjustment, (5) Consensus resolution.
   - Standardized structured JSON output contract: `role`, `findings`, `confidence` (0–100), `reasoning_chain`, `evidence`, `challenges`.
   - Agents never see each other's prompts, only outputs and confidence scores.
4. **LLM Routing & Resilience**:
   - Primary: Groq (`llama-3.3-70b-versatile` for debate, `llama-3.1-8b-instant` for structured extraction).
   - Fallback: Google Gemini Flash (`gemini-2.5-flash`).
   - Mock provider for deterministic, network-free unit and integration testing.
5. **Security & Authentication**:
   - Custom JWT (`python-jose`) with direct `bcrypt` password hashing (no `passlib`).
6. **Asynchronous Execution**:
   - FastAPI `BackgroundTasks` with status polling on `analysis_sessions`.

---

## Step-by-Step Roadmap

### Step 0: Audit & Plan (Done - 2026-10-13)
- Baseline audit of repository, requirements reconciliation, skeleton API contract, and roadmap design.

---

### Step 1: App Foundation (Done - 2026-10-13)
- Application factory `create_app()`, `Settings` management with `pydantic-settings`, CORS middleware, request latency logging, consistent exception handling (422, 404, 500), `/health`, `/api/v1/`, runner script `scripts\run_backend.bat`, and 8 passing unit/integration tests.

---

### Step 2: Complete Database, Schemas, Migrations & Schema Documentation (Next Step)
- **Goal**: Establish the complete database schema, migrations, Pydantic domain models, data access repositories, and exhaustive markdown schema documentation.
- **Target Files**:
  - `backend/app/database/session.py` (Engine, session factory, `get_db` FastAPI dependency)
  - `backend/app/database/models.py` (SQLAlchemy 2.0 ORM models for Users, PatientProfile, MedicalHistory, SymptomReport, LabResult, AnalysisSession, AgentOutput, RiskResult, Doctor, TrainedModel)
  - `backend/app/database/repositories.py` (Repository classes with clean CRUD abstractions)
  - `backend/app/schemas/` (`auth.py`, `patient.py`, `symptoms.py`, `laboratory.py`, `analysis.py`, `risk.py`, `doctor.py`)
  - `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/script.py.mako`, `backend/migrations/versions/` (Baseline migration)
  - `docs/architecture/DATABASE_SCHEMA.md` (Mandatory documentation artifact)
- **Mandatory Documentation Requirement (`DATABASE_SCHEMA.md`)**:
  1. Complete inventory of database tables.
  2. Tabular Entity-Relationship (ER) map showing primary keys, foreign keys, cardinality (1:1, 1:N, N:M), and cascade behavior.
  3. Column-by-column schema tables (field name, type, constraints, default, description).
  4. Tabular mock/example data rows for every table illustrating real-world data shapes.
- **Testing**:
  - `backend/tests/unit/test_database.py`: In-memory SQLite table generation, repository CRUD operations, constraint enforcement.
- **Definition of Done**: Alembic migration executes without error; repository tests pass on SQLite; `docs/architecture/DATABASE_SCHEMA.md` is generated and verified.

---

### Step 3: Authentication & Security
- **Goal**: Implement secure user registration, credential verification, JWT access/refresh token generation, and FastAPI security dependencies.
- **Target Files**:
  - `backend/app/core/security.py` (Direct `bcrypt` hashing, JWT encoding/decoding)
  - `backend/app/schemas/auth.py`
  - `backend/app/api/v1/auth.py` (`/register`, `/login`, `/refresh`, `/me`)
- **Testing**:
  - `backend/tests/unit/test_security.py` and `backend/tests/integration/test_auth_api.py`.
- **Definition of Done**: Registration, login, token refresh, and `/me` authentication flow verified with unit tests.

---

### Step 4: Patient Data APIs
- **Goal**: CRUD endpoints for profiles, medical history, symptom reports, and lab results, enforcing strict user tenant isolation.
- **Target Files**:
  - `backend/app/api/v1/symptoms.py`, `medical_history.py`, `laboratory.py`
  - `backend/app/database/repositories.py`
- **Testing**:
  - `backend/tests/integration/test_patient_data.py`: Tenant isolation tests (User A cannot access User B's records).

---

### Step 5: Clinical Risk Models (Deterministic Core)
- **Goal**: Implement exact published clinical equations in pure Python with complete academic citations and no LLM dependencies.
- **Target Files**:
  - `backend/app/clinical/cardiovascular.py` (Framingham 10-Year General CVD Risk, D'Agostino 2008)
  - `backend/app/clinical/diabetes.py` (FINDRISC - Finnish Diabetes Risk Score, Lindström 2003)
  - `backend/app/clinical/kidney.py` (CKD-EPI 2021 eGFR, Inker 2021)
- **Testing**:
  - `backend/tests/unit/test_clinical_models.py`: Worked examples from original published papers.

---

### Step 6: ML Dataset Acquisition & Preprocessing Pipeline
- **Goal**: Ingest benchmark datasets and build automated preprocessing pipelines.
- **Target Files**:
  - `backend/scripts/download_datasets.py` (Automated downloader / verification script for UCI Heart Disease, PIMA Indians Diabetes, and Kaggle Disease-Symptom dataset)
  - `backend/app/ml/preprocessing/cleaning.py`, `encoding.py`, `split.py`
  - `DATASET_REGISTER.md`
- **Testing**:
  - `backend/tests/ml/test_preprocessing.py`: Verify missing-value handling, scaling transforms, and split reproducibility.
- **Definition of Done**: Datasets ingested in `datasets/raw/`, preprocessing pipelines functional, `DATASET_REGISTER.md` updated.

---

### Step 7: ML Model Training & Model Registry
- **Goal**: Train supervised classification models, serialize artifacts, and track versions.
- **Target Files**:
  - `backend/app/ml/training/trainer.py`
  - `backend/scripts/train_models.py` (CLI training script)
  - `backend/app/ml/model_registry.py` (Registry metadata manager)
  - `MODEL_REGISTER.md`
- **Models Trained**:
  1. Cardiovascular Disease Risk Classifier (UCI Heart Disease)
  2. Type 2 Diabetes Classifier (PIMA Indians Diabetes)
  3. Symptom-to-Disease Category Classifier (Disease-Symptom dataset)
- **Testing**:
  - `backend/tests/ml/test_training.py`: Artifact creation, model serialization, registry integration.
- **Definition of Done**: Trained models serialized in `backend/app/ml/models/`, metadata recorded in `MODEL_REGISTER.md`.

---

### Step 8: ML Model Evaluation & Real-Time Inference Service
- **Goal**: Compute rigorous validation metrics and build real-time inference service.
- **Target Files**:
  - `backend/app/ml/evaluation/metrics.py` (ROC-AUC, F1, precision, recall, confusion matrix)
  - `backend/scripts/evaluate_models.py`
  - `backend/app/ml/inference/predictor.py`
- **Testing**:
  - `backend/tests/ml/test_inference.py`: Real-time prediction latency, probability output calibration.
- **Definition of Done**: Evaluation reports generated; inference predictor ready for consumption by agents.

---

### Step 9: LLM Service & Fallback Routing
- **Goal**: Unified LLM interface with Groq primary, Gemini Flash fallback, Mock provider for testing, and structured JSON output validation.
- **Target Files**:
  - `backend/app/services/llm_service.py`
  - `backend/app/core/config.py`
- **Testing**:
  - `backend/tests/unit/test_llm_service.py`: Schema enforcement, mock responses, fallback switching.

---

### Step 10: Multi-Agent Base & Domain Agents
- **Goal**: Unified agent contract and domain agents combining quantitative formulas, ML inference, and LLM reasoning.
- **Target Files**:
  - `backend/app/agents/base.py`
  - `backend/app/agents/symptom_agent.py`
  - `backend/app/agents/medical_history_agent.py`
  - `backend/app/agents/laboratory_agent.py`
  - `backend/app/agents/risk_prediction_agent.py` (ensembles Step 5 clinical scores + Step 8 ML predictions + LLM reasoning)
- **Testing**:
  - `backend/tests/unit/test_agents.py`: Deterministic fallback operation and mock LLM reasoning.

---

### Step 11: LangGraph Multi-Agent Pipeline
- **Goal**: Wire domain agents into a directed LangGraph workflow executing data agents in parallel before aggregating into risk prediction.
- **Target Files**:
  - `backend/app/graph/state.py`, `nodes.py`, `workflow.py`
- **Testing**:
  - `backend/tests/unit/test_graph_workflow.py`: Parallel fan-out and fan-in execution with error boundaries.

---

### Step 12: Consensus & Debate Framework (Core Research Contribution)
- **Goal**: Implement 5-step consensus debate protocol with contradiction detection, challenge round, and confidence adjustment.
- **Target Files**:
  - `backend/app/agents/consensus_agent.py`, `backend/app/graph/debate_nodes.py`
- **Testing**:
  - `backend/tests/unit/test_consensus_debate.py`: Contradictory agent inputs, bounded debate rounds, full transcript capture.

---

### Step 13: Explainability, Disease Trajectory & Counterfactual Simulator
- **Goal**: Reasoning graph JSON for Flutter `graphview`, 30d/6m/1y trajectory forecast, counterfactual lifestyle simulator, and doctor matching.
- **Target Files**:
  - `backend/app/agents/explainability_agent.py`
  - `backend/app/forecasting/trajectory.py`
  - `backend/app/counterfactual/simulator.py`
  - `backend/app/doctors/recommendations.py`
- **Testing**:
  - `backend/tests/unit/test_forecasting.py`, `test_counterfactual.py`, `test_doctor_recommendations.py`.

---

### Step 14: Analysis Orchestration API
- **Goal**: Expose end-to-end analysis endpoints with async job dispatching, polling status, and comprehensive results retrieval.
- **Target Files**:
  - `backend/app/services/analysis_service.py`, `app/schemas/analysis.py`
  - `backend/app/api/v1/analysis.py`, `risk.py`, `doctors.py`
- **Testing**:
  - `backend/tests/integration/test_analysis_pipeline.py`.

---

### Step 15: End-to-End System Benchmark & Validation
- **Goal**: Validate end-to-end system outputs against held-out benchmark patient records.
- **Target Files**:
  - `backend/tests/integration/test_end_to_end.py`, `backend/scripts/evaluate_models.py`
- **Testing**:
  - Automated benchmark suite comparing clinical scores, ML predictions, and multi-agent consensus verdicts.

---

### Step 16: Hardening & Production Deployment
- **Goal**: Security review, rate limiting, Docker containerization, CI/CD pipeline, and deployment guide.
- **Target Files**:
  - `backend/Dockerfile`, `docker-compose.yml`, `.github/workflows/backend-ci.yml`, final documentation.
