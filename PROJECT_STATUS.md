# MedOracle: Project Status

**Backend Status:** Step 7 Complete (ML Model Training & Continuous Learning Registry)  
**Backend Next Milestone:** Step 8 (ML Inference & Evaluation)  
**Frontend Status:** Milestone F4 Complete (Intake Assessment Wizard & Backend API Integration)  
**Active Working Branch:** `frontend/assessment-input-integration` (child branch of `frontend/assessment-input-screen`)  
**Last Updated:** 2026-10-21  
**Environments:**
- Backend: Windows 10, Python 3.14.0 (`backend\.venv`), FastAPI, SQLAlchemy 2.0, PostgreSQL / SQLite
- Frontend: Flutter (Dart 3.13.5), Riverpod (`flutter_riverpod: ^3.3.2`), GoRouter (`go_router: ^14.8.1`), HTTP (`http: ^1.2.2`)

---

## Hierarchical Branch Architecture

All MedOracle development adheres to a structured, 2-tier Git hierarchy:
- **Milestone Parent Branch (`MOv1/<MilestoneName>` or `frontend/<FeatureName>`)**: Targets `main` or team base branches. Serves as the stable parent branch for each major milestone step.
- **Sub-step Child Branches (`MOv1/<SubTaskName>` or `frontend/<FeatureName>/<SubTask>`)**: Target their respective Milestone Parent Branch. Individual tasks are developed, tested, and reviewed here before merging into the milestone branch.
- **Approval Protocol**: No branch is pushed without explicit user sign-off. Milestone branches merge only after complete verification.

---

## Backend Roadmap Execution Status

| Step | Milestone Parent Branch (➔ `main`) | Sub-Step Child Branch (➔ Parent) | Status | Completion Date | Key Outputs / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | `MOv1/AuditAndPlan` | — | **Done** | **2026-10-13** | Architecture audit, roadmap defined, skeleton API contract. |
| **1** | `MOv1/AppFoundation` | — | **Done** | **2026-10-13** | App factory, config, CORS, logging, error handlers, `/health`, `/api/v1/`. |
| **2** | `MOv1/AuthAndDb` | `MOv1/DbModelsAndSession`<br>`MOv1/RepositoriesAndSchemas`<br>`MOv1/AlembicAndSchemaDocs` | **Done** | **2026-10-14** | 10 SQLAlchemy ORM models, Alembic baseline, Pydantic v2 schemas, repositories, `docs/architecture/DATABASE_SCHEMA.md`. |
| **3** | `MOv1/AuthAndDb` | `MOv1/SecurityCoreBcryptJwt`<br>`MOv1/AuthEndpointsAndDeps` | **Done** | **2026-10-14** | JWT (`python-jose`) + `bcrypt` 5.x, `/register`, `/login`, `/refresh`, `/me`, route security deps. |
| **4** | `MOv1/PatientDataApis` | `MOv1/PatientProfileAndHistoryApi`<br>`MOv1/SymptomsAndLabsApi` | **Done** | **2026-10-14** | Patient profile, medical history, symptom reports, and lab results APIs with tenant isolation. |
| **5** | `MOv1/ClinicalRiskModels` | `MOv1/ClinicalEquationsPurePython`<br>`MOv1/RiskCalculationEndpoints` | **Done** | **2026-10-19** | Deterministic formulas: Framingham (CVD), FINDRISC (Diabetes), CKD-EPI (Kidney). Endpoints at `/api/v1/risk/`. |
| **6** | `MOv1/MLdatasetandpreprocessing` | `MOv1/MLDatasetAcquisition`<br>`MOv1/MLDatasetPreprocessing` | **Done** | **2026-10-19** | **6.1**: UCI Heart, PIMA, Disease-Symptom ingestion & `DATASET_REGISTER.md`.<br>**6.2**: Imputation, scaling, stratified 70/15/15 splits. 60 passed tests. |
| **7** | `MOv1/MLModelTrainingAndRegistry` | `MOv1/MLCardioAndDiabetesTraining`<br>`MOv1/MLSymptomDiseaseTraining`<br>`MOv1/MLActiveLearningFeedbackLoop` | **Done** | **2026-10-21** | **7.1**: Logistic Regression & Random Forest for CVD & Diabetes.<br>**7.2**: Multi-class classifier for 41 diseases.<br>**7.3**: Active continuous learning feedback loop, `TrainedModel` DB audit, `MODEL_REGISTER.md`. 71 passed tests. |
| **8** | `MOv1/MLInferenceAndEvaluation` | `MOv1/MLEvaluationMetrics`<br>`MOv1/MLRealtimePredictorService` | Pending (Next Backend) | — | Validation metrics (ROC-AUC, PR-AUC, F1); real-time feature transformation & inference predictor in `app/ml/inference/`. |
| **9** | `MOv1/LLMServiceRouting` | `MOv1/LLMProviderCore`<br>`MOv1/LLMStructuredOutputEngine` | Pending | — | Groq (primary) + Gemini (fallback) + Mock provider; strict Pydantic JSON schema validation. |
| **10**| `MOv1/MultiAgentDomainAgents` | `MOv1/AgentBaseContract`<br>`MOv1/SymptomAndHistoryAgents`<br>`MOv1/LabAndRiskPredictionAgents` | Pending | — | Unified agent contract (findings, confidence 0-100, reasoning, evidence, challenges); domain agents ensembling clinical + ML + LLM. |
| **11**| `MOv1/LangGraphPipeline` | `MOv1/GraphStateAndNodes`<br>`MOv1/GraphWorkflowExecution` | Pending | — | LangGraph directed workflow: parallel data agent fan-out and fan-in aggregation. |
| **12**| `MOv1/ConsensusDebateFramework` | `MOv1/ContradictionDetection`<br>`MOv1/DebateProtocolEngine`<br>`MOv1/ConsensusResolution` | Pending | — | 5-step consensus debate protocol with contradiction detection & dynamic confidence recalibration (Core FYP Research). |
| **13**| `MOv1/ExplainabilityAndForecasting` | `MOv1/ExplainabilityGraphExporter`<br>`MOv1/TrajectoryAndCounterfactual`<br>`MOv1/DoctorMatcherEngine` | Pending | — | Flutter `graphview` JSON export; 30d/6m/1y trajectory; "What-If" lifestyle counterfactual simulator; doctor recommendations. |
| **14**| `MOv1/AnalysisOrchestrationApi` | `MOv1/AsyncJobDispatcher`<br>`MOv1/AnalysisResultsEndpoints` | Pending | — | Async analysis dispatch (`BackgroundTasks`), polling `/status/{id}`, and comprehensive report retrieval. |
| **15**| `MOv1/SystemBenchmarkValidation` | `MOv1/BenchmarkEvaluationSuite`<br>`MOv1/PerformanceStressTesting` | Pending | — | Automated benchmark validation across held-out splits; concurrency & latency stress testing. |
| **16**| `MOv1/ProductionHardeningAndDeploy` | `MOv1/SecurityRateLimiting`<br>`MOv1/DockerAndCiPipeline`<br>`MOv1/ProductionDocsAndDeployment` | Pending | — | Rate limiting, Docker containerization, CI/CD with automated retraining triggers, cloud deployment. |

---

## Frontend Roadmap & Integration Status

| Step / Flow | Route Path | Screen Widget | State Management | Backend Target | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Intake Step 1** | `/intake/step-1` | `ProfileScreen` | `profileControllerProvider` | `GET/PUT /api/v1/patient/profile` | **Connected & Autosaved** (with offline fallback cache) |
| **Intake Step 2A** | `/intake/step-2a` | `ClinicalStatusScreen` | `clinicalStatusProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (chronic conditions, past surgeries, allergies, notes) |
| **Intake Step 2B** | `/intake/step-2b` | `MedicationsFamilyScreen` | `medicationsFamilyProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (current medications & family history records) |
| **Intake Step 3** | `/intake/step-3` | `SymptomsScreen` | `symptomsProvider` | `POST /api/v1/symptoms/`<br>`GET /api/v1/symptoms/` | **Connected & Submitted** (symptoms, body locations, triggers, duration, notes) |
| **Intake Step 4** | `/intake/step-4` | `LabsVitalsScreen` | `labsVitalsProvider` | `GET /api/v1/laboratory/latest`<br>`POST /api/v1/laboratory/` | **Connected & Submitted** (BP, lipid panel, glucose, HbA1c, creatinine) |
| **Intake Step 5** | `/intake/step-5` | `ReviewConfirmScreen` | `reviewProfileProvider` (combiner) | All domain entities summary | **Connected** (Flushes all step states to backend on submit) |
| **Results Flow** | `/results/reports` | `PendingStepScreen` | — | `/api/v1/analysis/` (Step 14) | **Intact Fallback** (awaiting backend analysis endpoint) |

---

## Current State Summary

### Backend Achievements (Steps 0–7)
- 71 passed backend tests (`pytest backend/tests`).
- Supervised ML models trained and saved to `backend/app/ml/artifacts/` (`cardio_model.joblib`, `diabetes_model.joblib`, `symptom_model.joblib`).
- Automated continuous learning pipeline in `backend/app/ml/feedback/active_learning.py` tracking production performance and drift against `TrainedModel` DB records.
- Deterministic clinical risk equations verified against published literature (Framingham 10yr CVD, FINDRISC 10yr T2D, CKD-EPI 2021).
- Complete FastAPI router endpoints for authentication, patient profiles, medical histories, symptoms, labs, and clinical risk models.

### Frontend Achievements (Milestone F1–F4)
- 12 passed tests across widget and integration test suites (`flutter test`).
- Zero static analysis issues (`dart analyze` clean with 0 errors, 0 warnings).
- **GoRouter Riverpod Integration**: Exposed `routerProvider` in `lib/core/routing/app_router.dart` and converted `MedOracleApp` in `lib/main.dart` into a `ConsumerWidget`.
- **API Client & Endpoints**: Implemented `ApiService` in `lib/data/services/api_service.dart` and `ApiEndpoints` in `lib/core/constants/api_endpoints.dart`.
- **Pydantic v2 Compatible Models**: `PatientProfile`, `MedicalHistoryModel`, `SymptomReportModel`, and `LabResultModel`.
- **Resilient Repositories**: `RestIntakeRepository`, `RestMedicalHistoryRepository`, `RestSymptomsRepository`, and `RestLaboratoryRepository` with local cache fallback so UI and tests run seamlessly both online and offline.
- **Dynamic Wizard Sync**: Step 5 Review & Confirm dynamically reflects live patient demographic facts and flushes all step states to the backend before navigation.
