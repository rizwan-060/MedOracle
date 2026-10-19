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

## Git Branching Hierarchy Architecture & Protocol

To maintain complete auditability, clean commit histories, and safe rollback boundaries, the MedOracle development follows a strict **Hierarchical Branching Model**:

```
main (Production Stable)
  ▲
  └── MOv1/<MilestoneName> (Milestone Parent Branch - Targets main)
        ▲
        ├── MOv1/<MilestoneName>-<SubStepA> (Child Branch - Merges into Milestone Parent)
        ├── MOv1/<MilestoneName>-<SubStepB> (Child Branch - Merges into Milestone Parent)
        └── MOv1/<MilestoneName>-<SubStepC> (Child Branch - Merges into Milestone Parent)
```

### Hierarchy Rules:
1. **Milestone Parent Branch (`MOv1/<MilestoneName>`)**:
   - Represents the cohesive deliverable for that roadmap milestone (e.g., `MOv1/MLdatasetandpreprocessing`, `MOv1/MLModelTrainingAndRegistry`).
   - Directly targets `main`.
   - Never receives direct ad-hoc code edits; it aggregates tested commits from its Sub-step Child branches.
2. **Sub-step Child Branches (`MOv1/<SubTaskName>`)**:
   - Every major roadmap step is divided into 2 to 3 bite-sized, independently testable sub-steps.
   - Each sub-step is developed in its own dedicated branch (e.g., `MOv1/MLDatasetAcquisition`, `MOv1/MLDatasetPreprocessing`).
   - Child branches merge into their Milestone Parent branch once unit tests pass.
3. **Approval Gate**:
   - No branch is pushed to remote `origin` without explicit user sign-off.
   - Merging the Milestone Parent branch into `main` occurs only after all sub-step children are merged and end-to-end integration tests pass.

---

## Step-by-Step Hierarchical Roadmap

### Step 0: Audit & Plan (Done - 2026-10-13)
- **Milestone Branch:** `MOv1/AuditAndPlan` ➔ `main`
- Baseline audit of repository, requirements reconciliation, skeleton API contract, and roadmap design.

---

### Step 1: App Foundation (Done - 2026-10-13)
- **Milestone Branch:** `MOv1/AppFoundation` ➔ `main`
- Application factory `create_app()`, `Settings` management with `pydantic-settings`, CORS middleware, request latency logging, consistent exception handling (422, 404, 500), `/health`, `/api/v1/`, runner script `scripts\run_backend.bat`, and 8 passing unit/integration tests.

---

### Step 2: Complete Database, Schemas, Migrations & Schema Documentation (Done - 2026-10-14)
- **Milestone Parent Branch:** `MOv1/AuthAndDb` ➔ `main`
- **Sub-step 2.1 (`MOv1/DbModelsAndSession`):**
  - Engine, session factory, `get_db` FastAPI dependency in `app/database/session.py`.
  - 10 SQLAlchemy 2.0 ORM models in `app/database/models.py`.
- **Sub-step 2.2 (`MOv1/RepositoriesAndSchemas`):**
  - Pydantic v2 schemas in `app/schemas/`.
  - CRUD repository classes with parameterized queries in `app/database/repositories.py`.
- **Sub-step 2.3 (`MOv1/AlembicAndSchemaDocs`):**
  - Baseline migration `001_initial_schema.py`.
  - Exhaustive database architecture specification artifact `docs/architecture/DATABASE_SCHEMA.md`.

---

### Step 3: Authentication & Security (Done - 2026-10-14)
- **Milestone Parent Branch:** `MOv1/AuthAndDb` ➔ `main`
- **Sub-step 3.1 (`MOv1/SecurityCoreBcryptJwt`):**
  - Direct `bcrypt` password hashing (rounds=12) avoiding deprecated wrappers.
  - JWT token encoding/decoding (`python-jose`) with HS256 algorithm and expiration checks in `app/core/security.py`.
- **Sub-step 3.2 (`MOv1/AuthEndpointsAndDeps`):**
  - Endpoints `/register`, `/login`, `/refresh`, `/me` in `app/api/v1/auth.py`.
  - `get_current_user` FastAPI dependency for route protection.

---

### Step 4: Patient Data APIs (Done - 2026-10-14)
- **Milestone Parent Branch:** `MOv1/PatientDataApis` ➔ `main`
- **Sub-step 4.1 (`MOv1/PatientProfileAndHistoryApi`):**
  - Patient Profile CRUD (`GET/PUT /api/v1/patient/profile`).
  - Medical History endpoints (`GET/POST/PUT /api/v1/medical-history/`).
- **Sub-step 4.2 (`MOv1/SymptomsAndLabsApi`):**
  - Symptom Reports CRUD (`POST/GET/DELETE /api/v1/symptoms/`).
  - Laboratory Results CRUD (`POST/GET/DELETE /api/v1/laboratory/`).
  - Strict tenant isolation enforced on every query (`user_id = current_user.id`).

---

### Step 5: Clinical Risk Models (Deterministic Core) (Done - 2026-10-19)
- **Milestone Parent Branch:** `MOv1/ClinicalRiskModels` ➔ `main`
- **Sub-step 5.1 (`MOv1/ClinicalEquationsPurePython`):**
  - Framingham General CVD 10-year risk (D'Agostino 2008 Cox proportional hazards) in `app/clinical/cardiovascular.py`.
  - FINDRISC type 2 diabetes score (Lindström 2003 point system) in `app/clinical/diabetes.py`.
  - CKD-EPI 2021 race-free eGFR equation (Inker 2021) in `app/clinical/kidney.py`.
- **Sub-step 5.2 (`MOv1/RiskCalculationEndpoints`):**
  - REST endpoints mounted at `/api/v1/risk/cardiovascular`, `/diabetes`, `/kidney`.
  - Mandatory clinical non-diagnostic disclaimer in every response.
  - Documented in `POSTMAN_API_TESTING_GUIDE.md`. 54 passed tests.

---

### Step 6: ML Datasets & Preprocessing Pipelines (Done - 2026-10-19)
- **Milestone Parent Branch:** `MOv1/MLdatasetandpreprocessing` ➔ `main`
- **Sub-step 6.1 (`MOv1/MLDatasetAcquisition`):**
  - Download runner in `backend/scripts/download_datasets.py`.
  - Raw benchmark datasets in `datasets/raw/`: UCI Heart Disease (303 rows), PIMA Indians Diabetes (768 rows), Columbia Disease-Symptom matrix (4,920 rows).
  - Schema documentation and provenance published in `DATASET_REGISTER.md`.
- **Sub-step 6.2 (`MOv1/MLDatasetPreprocessing`):**
  - Pure Python modular preprocessing pipelines in `backend/app/ml/preprocessing/`:
    - `heart.py`: Mode imputation, target binarization, z-score scaling, stratified 70/15/15 train/val/test splits.
    - `diabetes.py`: Median imputation for physiological zero values, z-score scaling, stratified splits.
    - `symptoms.py`: 41-class label encoding with reversible mappings, stratified splits.
  - Exported processed CSVs and `metadata.json` to `datasets/processed/`. 60 passed tests.

---

### Step 7: ML Model Training & Continuous Retraining Registry (Next Step)
- **Milestone Parent Branch:** `MOv1/MLModelTrainingAndRegistry` ➔ `main`
- **Sub-step 7.1 (`MOv1/MLCardioAndDiabetesTraining`):**
  - Train Cardiovascular Disease Classifier (Logistic Regression / Random Forest baseline on UCI Heart).
  - Train Type 2 Diabetes Classifier (Random Forest / Gradient Boosting on PIMA Diabetes).
  - Serialize model weights, scalers, and hyperparameters to `backend/app/ml/models/`.
- **Sub-step 7.2 (`MOv1/MLSymptomDiseaseTraining`):**
  - Train 41-class Disease-Symptom Classifier (Multinomial Naive Bayes / Random Forest).
  - Predict top-N disease candidates with calibrated probability distributions.
  - Document model metrics and hyperparameters in `MODEL_REGISTER.md`.
- **Sub-step 7.3 (`MOv1/MLActiveLearningFeedbackLoop`):**
  - **Continuous Model Retraining Pipeline**: Implement active feedback data collector.
  - When verified clinical outcomes or doctor corrections are entered, new anonymized samples are appended to an audited retraining queue.
  - Versioned model checkpointing registered in the `TrainedModel` database table with rollback support.

---

### Step 8: ML Model Evaluation & Real-Time Inference Service
- **Milestone Parent Branch:** `MOv1/MLInferenceAndEvaluation` ➔ `main`
- **Sub-step 8.1 (`MOv1/MLEvaluationMetrics`):**
  - Evaluation engine in `backend/app/ml/evaluation/metrics.py`: ROC-AUC, PR-AUC, F1-score, sensitivity, specificity, and confusion matrix generation.
  - Automated evaluation script `backend/scripts/evaluate_models.py` executing against the held-out test splits.
- **Sub-step 8.2 (`MOv1/MLRealtimePredictorService`):**
  - Real-time feature transformer and inference engine in `backend/app/ml/inference/predictor.py`.
  - Ingests user profile and lab values, applies stored preprocessing scalers, runs model inference, and returns probabilities + top contributing risk features.
  - Exposes programmatic hook for Risk Prediction Agent.

---

### Step 9: LLM Service & Fallback Provider Routing
- **Milestone Parent Branch:** `MOv1/LLMServiceRouting` ➔ `main`
- **Sub-step 9.1 (`MOv1/LLMProviderCore`):**
  - Implement unified LLM interface in `backend/app/services/llm_service.py`.
  - Primary provider: Groq (`llama-3.3-70b-versatile` for clinical debate, `llama-3.1-8b-instant` for fast extraction).
  - Fallback provider: Google Gemini (`gemini-2.5-flash`).
  - Mock LLM provider for zero-cost, network-free, deterministic unit testing.
- **Sub-step 9.2 (`MOv1/LLMStructuredOutputEngine`):**
  - Enforce strict JSON schema validation for all LLM responses using Pydantic.
  - Automatic JSON retry repair mechanism on malformed completions.
  - Prompt template manager for clinical agents.

---

### Step 10: Multi-Agent Base & Domain Agents
- **Milestone Parent Branch:** `MOv1/MultiAgentDomainAgents` ➔ `main`
- **Sub-step 10.1 (`MOv1/AgentBaseContract`):**
  - Base agent contract in `backend/app/agents/base.py`.
  - Enforces standard output schema: `role`, `findings`, `confidence` (0–100), `reasoning_chain`, `evidence`, `challenges`.
  - Prompt isolation: agents see other agents' outputs and confidence scores, never their internal prompts.
- **Sub-step 10.2 (`MOv1/SymptomAndHistoryAgents`):**
  - Symptom Agent (`app/agents/symptom_agent.py`): Extracts temporal pattern, severity, symptom clustering.
  - Medical History Agent (`app/agents/medical_history_agent.py`): Evaluates pre-existing conditions, medication contraindications, genetic risk.
- **Sub-step 10.3 (`MOv1/LabAndRiskPredictionAgents`):**
  - Laboratory Agent (`app/agents/laboratory_agent.py`): Analyzes biomarker out-of-range patterns and trends.
  - Risk Prediction Agent (`app/agents/risk_prediction_agent.py`): Blends Step 5 deterministic formulas + Step 8 ML predictions + LLM clinical reasoning.

---

### Step 11: LangGraph Multi-Agent Orchestration Pipeline
- **Milestone Parent Branch:** `MOv1/LangGraphPipeline` ➔ `main`
- **Sub-step 11.1 (`MOv1/GraphStateAndNodes`):**
  - Directed graph state definition (`AgentState`) in `backend/app/graph/state.py`.
  - Specialized node wrappers for Symptom, History, and Lab agents.
  - Parallel execution fan-out of independent data agents.
- **Sub-step 11.2 (`MOv1/GraphWorkflowExecution`):**
  - Fan-in aggregation node assembling data agent outputs.
  - Fault tolerance: node-level error handlers preventing single-agent failure from aborting the pipeline.
  - Session state snapshotting in `app/graph/workflow.py`.

---

### Step 12: Consensus & Multi-Agent Debate Framework (Core FYP Research Contribution)
- **Milestone Parent Branch:** `MOv1/ConsensusDebateFramework` ➔ `main`
- **Sub-step 12.1 (`MOv1/ContradictionDetection`):**
  - Automated contradiction detection engine in `backend/app/agents/consensus_agent.py`.
  - Flags conflicting findings (e.g., Symptom Agent predicts acute cardiac event while Lab Agent notes normal troponin/lipids).
- **Sub-step 12.2 (`MOv1/DebateProtocolEngine`):**
  - 5-step debate protocol execution:
    1. Evidence submission.
    2. Contradiction identification.
    3. Challenge round (agents cross-examine conflicting findings).
    4. Confidence recalibration (agents adjust confidence 0–100 based on counter-evidence).
    5. Consensus synthesis.
  - Maximum debate rounds bound (default: 2 rounds) to prevent infinite loops and limit token expenditure.
- **Sub-step 12.3 (`MOv1/ConsensusResolution`):**
  - Final consensus verdict generation with confidence score and minority opinion preservation.
  - Full audit transcript persisted to `agent_outputs` table for clinical explainability.

---

### Step 13: Explainability, Disease Trajectory & Doctor Recommendation
- **Milestone Parent Branch:** `MOv1/ExplainabilityAndForecasting` ➔ `main`
- **Sub-step 13.1 (`MOv1/ExplainabilityGraphExporter`):**
  - Explainability Agent in `backend/app/agents/explainability_agent.py`.
  - Exports clinical reasoning graph formatted for Flutter `graphview` (nodes = findings/hypotheses, edges = evidential support/contradiction, weights = confidence).
- **Sub-step 13.2 (`MOv1/TrajectoryAndCounterfactual`):**
  - Disease Trajectory Forecaster in `backend/app/forecasting/trajectory.py`: Projected risk curves at 30 days, 6 months, and 1 year.
  - "What-If" Counterfactual Lifestyle Simulator in `backend/app/counterfactual/simulator.py`: Demonstrates risk score reductions based on simulated lifestyle changes (e.g., -10 mmHg SBP, cessation of smoking).
- **Sub-step 13.3 (`MOv1/DoctorMatcherEngine`):**
  - Specialist doctor recommendation engine in `backend/app/doctors/recommendations.py`.
  - Matches patient risk profile to appropriate medical specialties with structured referral summaries.

---

### Step 14: Analysis Orchestration API & Background Polling
- **Milestone Parent Branch:** `MOv1/AnalysisOrchestrationApi` ➔ `main`
- **Sub-step 14.1 (`MOv1/AsyncJobDispatcher`):**
  - Asynchronous analysis submission endpoint `POST /api/v1/analysis/start` using FastAPI `BackgroundTasks`.
  - Session tracking and status polling endpoint `GET /api/v1/analysis/status/{id}` (`pending`, `running`, `debating`, `completed`, `failed`).
- **Sub-step 14.2 (`MOv1/AnalysisResultsEndpoints`):**
  - Results endpoints: `GET /api/v1/analysis/{id}/report`, `GET /api/v1/analysis/{id}/graph`, `GET /api/v1/analysis/{id}/counterfactual`.
  - Integration with `POSTMAN_API_TESTING_GUIDE.md` for end-to-end endpoint verification.

---

### Step 15: End-to-End System Benchmark & Clinical Validation
- **Milestone Parent Branch:** `MOv1/SystemBenchmarkValidation` ➔ `main`
- **Sub-step 15.1 (`MOv1/BenchmarkEvaluationSuite`):**
  - Automated benchmark test suite running synthetic and public patient profiles through the entire multi-agent pipeline.
  - Quantitative metrics: Clinical equation calibration vs ML probability vs Final Agent Consensus.
- **Sub-step 15.2 (`MOv1/PerformanceStressTesting`):**
  - Concurrency testing, latency profiling under multi-agent debate load, token usage monitoring, and fallback failover testing.

---

### Step 16: Hardening, Production Deployment & Continuous Pipeline CI
- **Milestone Parent Branch:** `MOv1/ProductionHardeningAndDeploy` ➔ `main`
- **Sub-step 16.1 (`MOv1/SecurityRateLimiting`):**
  - Production rate limiting (SlowAPI), input payload size limits, header security (HSTS, CSP), and vulnerability audit.
- **Sub-step 16.2 (`MOv1/DockerAndCiPipeline`):**
  - Multi-stage `Dockerfile` and `docker-compose.yml`.
  - GitHub Actions CI pipeline (`backend-ci.yml`) running linting, formatting, test suite, and continuous retraining trigger tests.
- **Sub-step 16.3 (`MOv1/ProductionDocsAndDeployment`):**
  - Deployment configuration for cloud hosting (Render / Supabase).
  - Final FYP technical report documentation and API reference completion.

