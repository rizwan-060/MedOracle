---
description: Runs one step of the MedOracle backend roadmap (FastAPI, database, auth, clinical models, ML datasets & training, LLM layer, agents, LangGraph, consensus, API). Use whenever the user asks to start, continue, or do the next backend step, or invokes /backend-workflow.
---

# MedOracle backend workflow

Build the backend one step at a time. Each run of this skill completes exactly one step from the roadmap below, proves it works, records it, and stops.

## The loop (follow in order)

1. **Orient.** Read the project rules in `.agent/rules/medoracle-backend.md`, `docs/architecture/PROJECT_BRIEF.md`, `PROJECT_STATUS.md` and `IMPLEMENTATION_PLAN.md`. Pick the first step in the roadmap not marked done in `PROJECT_STATUS.md`. If the user named a step, use that one.
2. **Plan in the reply.** List the files you will fill in or create, the dependencies you will add, and anything you need from the user. If something blocks the step (a key, a dataset, a decision), ask now, before writing code.
3. **Build.** Implement only this step. Use the existing placeholder files listed in the roadmap. Do not build ahead.
4. **Test.** Write tests, run `backend\.venv\Scripts\python -m pytest backend\tests`, and for steps that change the running app, start it and call the real endpoints. Fix failures. Do not mark a step done while anything fails or is skipped.
5. **Record.**
   - Update `PROJECT_STATUS.md`: step status, date, what works, known gaps.
   - Update `API_CONTRACT.md` with every endpoint added or changed (method, path, auth, request and response JSON examples, error codes).
   - Update `.env.example`, `requirements.txt`, and `MODEL_REGISTER.md` or `DATASET_REGISTER.md` if the step touched models or datasets.
   - If Step 2, generate `docs/architecture/DATABASE_SCHEMA.md` documenting all tables, relations in tabular form, and sample data.
6. **Report and stop.** Reply with: what was built, how to run and test it (exact CMD commands), test results, decisions you made, what you need from the user, and a suggested git commit message. Then wait. Do not start the next step.

## Definition of done for every step
- `pytest` passes, with new tests for the new behaviour.
- `uvicorn app.main:app` starts without errors and `/health` responds.
- No secrets in the repo. New settings are in `.env.example`.
- Status, schema specifications, and API docs are updated.

## Roadmap

Statuses live in `PROJECT_STATUS.md`. The step numbers below are stable. Use them when talking to the user.

### Step 0. Audit and plan (Done)
Inspect `backend/` and root docs. Align architecture, dependency audit, skeleton contracts.

### Step 1. App foundation (Done)
Files: `app/core/config.py`, `app/main.py`, `app/api/router.py`, `app/api/v1/__init__.py`, `.env.example`.
Settings class, app factory, CORS, request logging, consistent error responses, `/health`, versioned router mounted at `/api/v1`. Tests: `tests/unit` for config, `tests/integration` for `/health`. Verified `scripts\run_backend.bat`.

### Step 2. Complete Database, Schemas, Migrations & Schema Documentation
Files: `app/database/session.py`, `app/database/models.py`, `app/database/repositories.py`, `app/schemas/` (auth, patient, symptoms, laboratory, analysis, risk), `migrations/` (Alembic), `alembic.ini`, and `docs/architecture/DATABASE_SCHEMA.md`.
Implement all SQLAlchemy 2.0 ORM tables (Users, PatientProfiles, MedicalHistories, SymptomReports, LabResults, AnalysisSessions, AgentOutputs, RiskResults, Doctors, TrainedModels). Setup Alembic migration environment and generate the initial baseline migration. Write corresponding Pydantic v2 schemas and repository CRUD wrappers. Tests run on in-memory SQLite.
**Mandatory Requirement**: Generate `docs/architecture/DATABASE_SCHEMA.md` with the full table list, entity relationships in tabular form, column types/constraints, and realistic example data for every table.

### Step 3. Authentication & User Security
Files: `app/core/security.py`, `app/schemas/auth.py`, `app/api/v1/auth.py`.
Register, login, token refresh, `/me` profile check, access and refresh JWTs (`python-jose`), direct `bcrypt` password hashing, reusable `get_current_user` FastAPI dependency. Tests for happy path, wrong password, duplicate email, expired and tampered tokens.

### Step 4. Patient Data APIs
Files: `app/schemas/patient.py`, `symptoms.py`, `laboratory.py`, `app/api/v1/symptoms.py`, `medical_history.py`, `laboratory.py`.
Create, read, update, and list endpoints for patient profile, medical and family history, symptom reports, and lab results. Multi-user tenant isolation: each record strictly belongs to the authenticated user and cannot be accessed by other users.

### Step 5. Clinical Risk Models (Deterministic Core)
Files: `app/clinical/cardiovascular.py`, `diabetes.py`, `kidney.py`.
Pure Python implementations of Framingham 10-year CVD risk (D'Agostino 2008), FINDRISC diabetes score (Lindström 2003), and CKD-EPI 2021 eGFR equation. Complete academic citations, zero LLM reliance, worked-example unit tests, stratified categories, and clinical disclaimer.

### Step 6. ML Dataset Acquisition & Preprocessing Pipeline
Files: `backend/app/ml/preprocessing/`, `backend/scripts/download_datasets.py`, `DATASET_REGISTER.md`.
Download and ingest benchmark datasets: UCI Heart Disease, PIMA Indians Diabetes, and Kaggle Disease-to-Symptom dataset into `datasets/raw/`. Implement preprocessing, missing-value imputation, feature encoding, scaling, and train/val/test split pipelines in `app/ml/preprocessing/`. Update `DATASET_REGISTER.md` with schema, sources, and data distributions.

### Step 7. ML Model Training & Model Registry
Files: `backend/app/ml/training/`, `backend/app/ml/model_registry.py`, `backend/scripts/train_models.py`, `MODEL_REGISTER.md`.
Implement training pipelines in `app/ml/training/` and runnable CLI training script `scripts/train_models.py`. Train supervised classification models (e.g. Random Forest, Logistic Regression, LightGBM/XGBoost) for cardiovascular disease, diabetes risk, and symptom-disease mapping. Serialize artifacts into `backend/app/ml/models/`. Save model metadata and versioning in `model_registry.py` and `MODEL_REGISTER.md`.

### Step 8. ML Model Evaluation & Real-Time Inference Service
Files: `backend/app/ml/evaluation/`, `backend/app/ml/inference/`, `backend/scripts/evaluate_models.py`, `tests/ml/`.
Implement model evaluation metrics (ROC-AUC, F1, precision, recall, confusion matrix) in `scripts/evaluate_models.py`. Build real-time inference service in `app/ml/inference/` that loads serialized models, transforms incoming patient data, and returns probabilities, confidence intervals, and feature attributions. Unit tests for inference outputs.

### Step 9. LLM Service & Fallback Routing
Files: `app/services/llm_service.py`, `app/core/config.py` (LLM settings).
Unified LLM interface with Groq primary (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), Gemini Flash fallback, and Mock provider for testing. Pydantic-validated structured JSON output, exponential backoff retries, provider fallback logic, and latency logging.

### Step 10. Agent Base & Domain Agents
Files: `app/agents/` (`base.py`, `symptom_agent.py`, `medical_history_agent.py`, `laboratory_agent.py`, `risk_prediction_agent.py`).
Standard agent output contract: `role`, `findings`, `confidence` (0-100), `reasoning_chain`, `evidence`, `challenges`. Risk prediction agent ensembles deterministic clinical formulas (Step 5) with trained ML model probabilities (Step 8) and contextual LLM reasoning.

### Step 11. LangGraph Multi-Agent Pipeline
Files: `app/graph/state.py`, `nodes.py`, `workflow.py`.
Directed workflow graph: parallel execution of Symptom, History, and Lab agents, flowing into the Risk Prediction agent and consensus aggregator. Typed shared state and per-node error resilience.

### Step 12. Consensus & Debate Agent Framework
Files: `app/agents/consensus_agent.py`, `app/graph/debate_nodes.py`.
5-step multi-agent debate protocol: (1) evidence submission, (2) contradiction detection, (3) challenge round, (4) confidence adjustment, (5) consensus resolution. Captures full audit debate transcript for frontend and FYP evaluation.

### Step 13. Explainability, Disease Trajectory & Counterfactual Simulator
Files: `app/agents/explainability_agent.py`, `app/forecasting/trajectory.py`, `app/counterfactual/simulator.py`, `app/doctors/recommendations.py`.
Reasoning graph JSON generation for Flutter `graphview`. 30-day, 6-month, 1-year disease trajectory projection. Counterfactual simulation for lifestyle interventions (walking, diet, smoking cessation). Doctor recommendation matching by specialty and proximity.

### Step 14. Analysis Orchestration API
Files: `app/services/analysis_service.py`, `app/schemas/analysis.py`, `app/api/v1/analysis.py`, `risk.py`, `doctors.py`.
Asynchronous analysis dispatch, polling endpoint (`/status`), and full results retrieval (`/result`, `/debate`, `/reasoning-graph`). Finalizes `API_CONTRACT.md`.

### Step 15. End-to-End System Benchmark & Validation
Files: `backend/tests/integration/test_end_to_end.py`, `scripts/evaluate_models.py`.
Validate end-to-end multi-agent pipeline performance on held-out benchmark splits. Report clinical concordance, debate resolution efficacy, and honest metric boundaries.

### Step 16. Hardening, Security & Deployment
Files: `backend/Dockerfile`, `docker-compose.yml`, `.github/workflows/`, rate limiting, input sanitization, security review, Render deployment guide, final README.

## Stop-and-ask list
Stop and ask the user instead of continuing when:
- you need an API key, database URL, or dataset they have not provided
- a clinical coefficient, threshold or reference range is uncertain
- the proposal and the repo disagree, or a roadmap step needs a decision not covered by the rules
- tests fail and the cause is outside the current step
