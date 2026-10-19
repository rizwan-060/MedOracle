# MedOracle Backend: Project Status

**Current Milestone:** Step 6 Complete (ML Datasets & Preprocessing Pipelines)  
**Next Milestone:** Step 7 (ML Model Training & Registry)  
**Last Updated:** 2026-10-19  
**Active Environment:** Windows 10, Python 3.14.0 (`backend\.venv`), FastAPI  

---

## Hierarchical Branch Architecture

All MedOracle development adheres to a structured, 2-tier Git hierarchy:
- **Milestone Parent Branch (`MOv1/<MilestoneName>`)**: Targets `main`. Serves as the stable parent branch for each major milestone step.
- **Sub-step Child Branches (`MOv1/<SubTaskName>`)**: Target their respective Milestone Parent Branch. Individual tasks are developed, tested, and reviewed here before merging into the milestone branch.
- **Approval Protocol**: No branch is pushed without explicit user sign-off. Milestone branches merge to `main` only after complete validation.

---

## Roadmap Execution Status

| Step | Milestone Parent Branch (➔ `main`) | Sub-Step Child Branch (➔ Parent) | Status | Completion Date | Key Outputs / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | `MOv1/AuditAndPlan` | — | **Done** | **2026-10-13** | Architecture audit, roadmap defined, skeleton API contract. |
| **1** | `MOv1/AppFoundation` | — | **Done** | **2026-10-13** | App factory, config, CORS, logging, error handlers, `/health`, `/api/v1/`. |
| **2** | `MOv1/AuthAndDb` | `MOv1/DbModelsAndSession`<br>`MOv1/RepositoriesAndSchemas`<br>`MOv1/AlembicAndSchemaDocs` | **Done** | **2026-10-14** | 10 SQLAlchemy ORM models, Alembic baseline, Pydantic v2 schemas, repositories, `docs/architecture/DATABASE_SCHEMA.md`. |
| **3** | `MOv1/AuthAndDb` | `MOv1/SecurityCoreBcryptJwt`<br>`MOv1/AuthEndpointsAndDeps` | **Done** | **2026-10-14** | JWT (`python-jose`) + `bcrypt` 5.x, `/register`, `/login`, `/refresh`, `/me`, route security deps. |
| **4** | `MOv1/PatientDataApis` | `MOv1/PatientProfileAndHistoryApi`<br>`MOv1/SymptomsAndLabsApi` | **Done** | **2026-10-14** | Patient profile, medical history, symptom reports, and lab results APIs with tenant isolation. |
| **5** | `MOv1/ClinicalRiskModels` | `MOv1/ClinicalEquationsPurePython`<br>`MOv1/RiskCalculationEndpoints` | **Done** | **2026-10-19** | Deterministic formulas: Framingham (CVD), FINDRISC (Diabetes), CKD-EPI (Kidney). Endpoints at `/api/v1/risk/`. |
| **6** | `MOv1/MLdatasetandpreprocessing` | `MOv1/MLDatasetAcquisition`<br>`MOv1/MLDatasetPreprocessing` | **Done** | **2026-10-19** | **6.1**: UCI Heart, PIMA, Disease-Symptom ingestion & `DATASET_REGISTER.md`.<br>**6.2**: Imputation, scaling, stratified 70/15/15 splits. 60 passed tests. |
| **7** | `MOv1/MLModelTrainingAndRegistry` | `MOv1/MLCardioAndDiabetesTraining`<br>`MOv1/MLSymptomDiseaseTraining`<br>`MOv1/MLActiveLearningFeedbackLoop` | Pending (Next) | — | Supervised classifiers (Cardio, Diabetes, 41-class Symptoms); `MODEL_REGISTER.md`; Continuous learning feedback loop & model audit tracking. |
| **8** | `MOv1/MLInferenceAndEvaluation` | `MOv1/MLEvaluationMetrics`<br>`MOv1/MLRealtimePredictorService` | Pending | — | Validation metrics (ROC-AUC, PR-AUC, F1); real-time feature transformation & inference predictor in `app/ml/inference/`. |
| **9** | `MOv1/LLMServiceRouting` | `MOv1/LLMProviderCore`<br>`MOv1/LLMStructuredOutputEngine` | Pending | — | Groq (primary) + Gemini (fallback) + Mock provider; strict Pydantic JSON schema validation. |
| **10**| `MOv1/MultiAgentDomainAgents` | `MOv1/AgentBaseContract`<br>`MOv1/SymptomAndHistoryAgents`<br>`MOv1/LabAndRiskPredictionAgents` | Pending | — | Unified agent contract (findings, confidence 0-100, reasoning, evidence, challenges); domain agents ensembling clinical + ML + LLM. |
| **11**| `MOv1/LangGraphPipeline` | `MOv1/GraphStateAndNodes`<br>`MOv1/GraphWorkflowExecution` | Pending | — | LangGraph directed workflow: parallel data agent fan-out and fan-in aggregation. |
| **12**| `MOv1/ConsensusDebateFramework` | `MOv1/ContradictionDetection`<br>`MOv1/DebateProtocolEngine`<br>`MOv1/ConsensusResolution` | Pending | — | 5-step consensus debate protocol with contradiction detection & dynamic confidence recalibration (Core FYP Research). |
| **13**| `MOv1/ExplainabilityAndForecasting` | `MOv1/ExplainabilityGraphExporter`<br>`MOv1/TrajectoryAndCounterfactual`<br>`MOv1/DoctorMatcherEngine` | Pending | — | Flutter `graphview` JSON export; 30d/6m/1y trajectory; "What-If" lifestyle counterfactual simulator; doctor recommendations. |
| **14**| `MOv1/AnalysisOrchestrationApi` | `MOv1/AsyncJobDispatcher`<br>`MOv1/AnalysisResultsEndpoints` | Pending | — | Async analysis dispatch (`BackgroundTasks`), polling `/status/{id}`, and comprehensive report retrieval. |
| **15**| `MOv1/SystemBenchmarkValidation` | `MOv1/BenchmarkEvaluationSuite`<br>`MOv1/PerformanceStressTesting` | Pending | — | Automated benchmark validation across held-out splits; concurrency & latency stress testing. |
| **16**| `MOv1/ProductionHardeningAndDeploy` | `MOv1/SecurityRateLimiting`<br>`MOv1/DockerAndCiPipeline`<br>`MOv1/ProductionDocsAndDeployment` | Pending | — | Rate limiting, Docker containerization, CI/CD with automated retraining triggers, cloud deployment. |

---

## Current State Summary

### What Works
- Virtual environment verified at `backend\.venv` running Python 3.14.0.
- Application factory `create_app()` implemented in `backend/app/main.py`.
- Central configuration in `backend/app/core/config.py` using `pydantic-settings` with `.env` reading and cached singleton.
- CORS middleware, request logging middleware with millisecond timing, and standardized exception handling.
- **Complete Database & Schema Foundation (Step 2)**:
  - 10 SQLAlchemy 2.0 ORM models in `app/database/models.py` (`users`, `patient_profiles`, `medical_histories`, `symptom_reports`, `lab_results`, `analysis_sessions`, `agent_outputs`, `risk_results`, `doctors`, `trained_models`).
  - Session and engine management in `app/database/session.py` supporting PostgreSQL in production and SQLite in tests.
  - Complete Pydantic v2 domain schemas in `app/schemas/` for all entities.
  - Full data access repositories in `app/database/repositories.py` preventing SQL injection through parameterized expression queries.
  - Alembic migrations environment initialized (`alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`, and baseline migration `001_initial_schema.py`).
  - Comprehensive Markdown specification artifact published at `docs/architecture/DATABASE_SCHEMA.md` with full table inventory, ER table, column specifications, and realistic sample data rows.
- Test suite: **54 passed** across unit configuration tests, health integration tests, database/repository tests, security tests, auth integration tests, patient data API integration tests, and clinical risk model tests.
- **Authentication & Security (Step 3)**:
  - Custom JWT authentication using `python-jose` with HS256 algorithm and standard claims (`sub`, `exp`, `type`, `iat`).
  - Direct `bcrypt` password hashing (rounds=12) avoiding incompatible legacy wrappers.
  - Auth endpoints implemented and mounted under `/api/v1/auth`: `/register`, `/login`, `/refresh`, `/me`.
- **Patient Data APIs (Step 4)**:
  - Patient Profile (`GET /api/v1/patient/profile`, `PUT /api/v1/patient/profile`): Biometrics, lifestyle factors, demographics with auto-provisioning.
  - Medical History (`GET /api/v1/medical-history/`, `POST /api/v1/medical-history/`, `PUT /api/v1/medical-history/`): Chronic conditions, surgeries, medications, allergies, family history.
  - Symptom Reports (`POST /api/v1/symptoms/`, `GET /api/v1/symptoms/`, `GET /api/v1/symptoms/{id}`, `DELETE /api/v1/symptoms/{id}`): Natural language complaint text, duration, severity rating, body locations, triggers.
  - Laboratory Results (`POST /api/v1/laboratory/`, `GET /api/v1/laboratory/`, `GET /api/v1/laboratory/latest`, `GET /api/v1/laboratory/{id}`, `DELETE /api/v1/laboratory/{id}`): Structured biomarkers (BP, cholesterol panels, glucose, HbA1c, creatinine, eGFR).
  - Strict tenant isolation: All queries enforce `current_user.id`, returning 404 on cross-tenant access attempts.
- **Clinical Risk Models (Step 5)**:
  - Pure Python mathematical implementations of Framingham General CVD 10-year risk (D'Agostino 2008 Cox proportional hazards regression), FINDRISC diabetes score (Lindström 2003 point-scoring system), and CKD-EPI 2021 race-free eGFR formula (Inker 2021).
  - Endpoints mounted under `/api/v1/risk`: `POST /api/v1/risk/cardiovascular`, `POST /api/v1/risk/diabetes`, `POST /api/v1/risk/kidney`.
  - Academic citations embedded in docstrings; mandatory non-diagnostic clinical disclaimer returned in every calculation response.
  - Interactive Postman documentation updated in `POSTMAN_API_TESTING_GUIDE.md`.
- **ML Dataset Acquisition & Registry (Sub-Step 6.1)**:
  - Acquisition runner implemented in `backend/scripts/download_datasets.py`.
  - Canonical raw benchmark datasets ingested in `datasets/raw/`:
    - `heart_disease_uci.csv` (Cleveland cohort, 303 instances, 14 features)
    - `diabetes_pima.csv` (NIDDK cohort, 768 instances, 9 features)
    - `symptoms_disease.csv` (Columbia diagnostic matrix, 4,920 instances, 132 symptom features across 41 disease targets)
  - Comprehensive metadata registry published in `DATASET_REGISTER.md`.
- **ML Preprocessing & Splitting Pipelines (Sub-Step 6.2)**:
  - Preprocessing pipelines implemented in `backend/app/ml/preprocessing/`:
    - `heart.py`: Mode imputation for `ca`/`thal`, target binarization, z-score scaling, stratified 70/15/15 splits.
    - `diabetes.py`: Median imputation for physiologically impossible zeroes (Glucose, BP, SkinThickness, Insulin, BMI), z-score scaling, stratified 70/15/15 splits.
    - `symptoms.py`: 41-class label encoding with reversible mapping, stratified 70/15/15 splits.
  - Processed datasets and metadata exported to `datasets/processed/` (`heart`, `diabetes`, `symptoms`).
  - Unit tests verified: **60 passed** across all test suites.

### Security & Data Audit (Step 6 Verification)
- **Data Integrity**: All raw and processed splits verified for row balance, no missing values / NaNs, and class stratification.
- **Strict Authentication**: All active API endpoints require `get_current_user`; unauthenticated requests return 401 Unauthorized.
- **Continuous Learning Architecture**: Roadmap updated to incorporate continuous model retraining / active learning feedback loop in Step 7 & 8 using the database `TrainedModel` audit table.

### Next Action
- Step 6 fully completed. Ready for **Step 7: ML Model Training & Registry** (Branch `MOv1/MLModelTraining`).
