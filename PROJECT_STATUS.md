# MedOracle: Project Status

**Backend Status:** Step 7 Complete (ML Model Training, Champion Registry & Continuous Retraining)  
**Backend Next Milestone:** Step 8 (ML Inference & Quantitative Risk Profiling Endpoints)  
**Frontend Status:** Milestone F4 Complete (Clinical Assessment Flow & Backend API Integration)  
**Active Working Branch:** `main`  
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
| **7.1**| `MOv1/MLModelTrainingAndRegistry` | `MOv1/MLCardioAndDiabetesTraining` | **Done** | **2026-10-20** | Trained & validated Cardio (`GradientBoosting`, ROC-AUC 0.8864, Acc 83.33%) & Diabetes (`RandomForest`, ROC-AUC 0.8605, Acc 78.45%) models in `models/saved/`; `MODEL_REGISTER.md` updated. 64 passed tests. |
| **7.2**| `MOv1/MLModelTrainingAndRegistry` | `MOv1/MLSymptomDiseaseTraining` | **Done** | **2026-10-20** | Trained 41-class Disease-Symptom Classifier (`MultinomialNB`, 100.0% test accuracy, 100.0% top-3 differential diagnosis accuracy, 1.0000 macro F1). Exported `models/saved/symptoms_disease_v1.joblib`. 65 passed tests. |
| **7.3**| `MOv1/MLModelTrainingAndRegistry` | `MOv1/MLActiveLearningFeedbackLoop` | **Done** | **2026-10-20** | Continuous retraining pipeline: active learning feedback queue, automated retraining triggers, performance gate protection, and relational database audit in `TrainedModel`. 71 passed tests. |
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
| **Patient Profile** | `/patient-profile` | `ProfileScreen` | `profileControllerProvider` | `GET/PUT /api/v1/patient/profile` | **Connected & Autosaved** (with offline fallback cache) |
| **Clinical Status** | `/clinical-status` | `ClinicalStatusScreen` | `clinicalStatusProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (chronic conditions, past surgeries, allergies, notes) |
| **Medications & Family** | `/medications-family` | `MedicationsFamilyScreen` | `medicationsFamilyProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (current medications & family history records) |
| **Symptoms** | `/symptoms` | `SymptomsScreen` | `symptomsProvider` | `POST /api/v1/symptoms/`<br>`GET /api/v1/symptoms/` | **Connected & Submitted** (symptoms, body locations, triggers, duration, notes) |
| **Labs & Vitals** | `/laboratory-vitals` | `LabsVitalsScreen` | `labsVitalsProvider` | `GET /api/v1/laboratory/latest`<br>`POST /api/v1/laboratory/` | **Connected & Submitted** (BP, lipid panel, glucose, HbA1c, creatinine) |
| **Assessment Review** | `/assessment-review` | `ReviewConfirmScreen` | `reviewProfileProvider` (combiner) | All domain entities summary | **Connected** (Flushes all section states to backend on submit) |
| **Results Reports** | `/results/reports` | `PendingStepScreen` | — | `/api/v1/analysis/` (Step 14) | **Intact Fallback** (awaiting backend analysis endpoint) |

---

## Current State Summary

### Backend Achievements (Steps 0–7)
- **71 passed backend tests** (`pytest backend/tests`).
- Supervised ML models trained and saved to `backend/app/ml/artifacts/` (`cardio_model.joblib`, `diabetes_model.joblib`, `symptom_model.joblib`).
- Automated continuous learning pipeline in `backend/app/ml/feedback/active_learning.py` tracking production performance and drift against `TrainedModel` DB records.
- Deterministic clinical risk equations verified against published literature (Framingham 10yr CVD, FINDRISC 10yr T2D, CKD-EPI 2021).
- Complete FastAPI router endpoints for authentication, patient profiles, medical histories, symptoms, labs, and clinical risk models.
- **ML Model Training & Registry (Sub-Step 7.1)**:
  - Model training pipelines implemented in `backend/app/ml/training/`:
    - `cardiovascular.py`: Compared Logistic Regression, Random Forest, and Gradient Boosting on processed UCI Heart splits. Selected champion: `GradientBoostingClassifier` (Validation ROC-AUC 0.8917, Test Accuracy 83.33%, Precision 85.00%, Recall 77.27%, F1 80.95%, ROC-AUC 0.8864).
    - `diabetes.py`: Compared Logistic Regression, Random Forest, and Gradient Boosting on processed PIMA Diabetes splits. Selected champion: `RandomForestClassifier` (Validation ROC-AUC 0.8277, Test Accuracy 78.45%, Precision 73.53%, Recall 60.98%, F1 66.67%, ROC-AUC 0.8605).
  - Model registry module implemented in `backend/app/ml/model_registry.py` managing serialization via `joblib` and companion metadata JSON tracking.
  - Executable CLI training runner created in `backend/scripts/train_models.py`.
  - Comprehensive documentation artifact published in `MODEL_REGISTER.md`.
  - Unit tests verified: **64 passed** across all test suites.
- **41-Class Symptom-Disease Classifier Training (Sub-Step 7.2)**:
  - Model training pipeline implemented in `backend/app/ml/training/symptoms.py` mapping 132 binary symptom indicators to 41 disease entities.
  - Compared Multinomial Naive Bayes, Random Forest, and Multinomial Logistic Regression. Selected champion: `MultinomialNB` (Test Accuracy 100.0%, Top-3 Differential Diagnosis Accuracy 100.0%, Top-5 Accuracy 100.0%, Macro F1 1.0000).
  - Built differential diagnosis ranking helper `predict_top_candidates()` returning calibrated probability distributions and top-k candidate pathologies.
  - Serialized model bundle exported to `models/saved/symptoms_disease_v1.joblib` and metadata JSON registered.
  - `MODEL_REGISTER.md` expanded with comprehensive 41-class benchmarks.
  - Unit tests verified: **65 passed** across all test suites.
- **Continuous Active Learning Retraining Feedback Loop (Sub-Step 7.3)**:
  - Feedback ingestion buffer implemented in `backend/app/ml/feedback/buffer.py` (`FeedbackRecord`, `FeedbackBuffer`).
  - Automated continuous retrainer with performance gate protection implemented in `backend/app/ml/feedback/retrainer.py` (`ContinuousRetrainer`).
  - Database model synchronization utility implemented in `backend/app/ml/feedback/sync.py` (`sync_all_models_to_db`) syncing serialized models with `trained_models` table.
  - CLI runner implemented in `backend/scripts/retrain_feedback.py`.
  - Comprehensive unit test suite in `backend/tests/unit/test_feedback_loop.py`.
  - Test suite status: **71 passed** (0 failures).

### Frontend Achievements (Milestones F1–F4)
- **16 passed frontend tests** (`flutter test`).
- **Zero static analysis issues** (`dart analyze` clean with 0 errors, 0 warnings).
- **Generic Core Reusable Widgets**: `AppTextField`, `AppButton`, `AppSectionCard`, and barrel export `core_widgets.dart` eliminating repetitive form boilerplate.
- **Clean Clinical Domain Naming**: Refactored workflow concepts to real-world names, eliminating "intake" and "wizard" artifacts.
- **Centralized Route System (`RouteNames`)**: Single source of truth in `lib/core/routing/route_names.dart` consumed by `GoRouter` and feature screens.
- **GoRouter Riverpod Integration**: Exposed `routerProvider` in `lib/core/routing/app_router.dart` and converted `MedOracleApp` in `lib/main.dart` into a `ConsumerWidget`.
- **API Client & Endpoints**: Implemented `ApiService` in `lib/data/services/api_service.dart` and `ApiEndpoints` in `lib/core/constants/api_endpoints.dart`.
- **Pydantic v2 Compatible Models**: `PatientProfile`, `MedicalHistoryModel`, `SymptomReportModel`, and `LabResultModel`.
- **Resilient Repositories**: `RestPatientProfileRepository`, `RestMedicalHistoryRepository`, `RestSymptomsRepository`, and `RestLaboratoryRepository` with local cache fallback so UI and tests run seamlessly both online and offline.
- **Dynamic Assessment Sync**: Assessment review screen dynamically reflects live patient demographic facts and flushes all section states to the backend before navigation.

---

### Next Action
- Backend: Ready for **Step 8: ML Inference & Real-Time Prediction Endpoints** (`MOv1/MLInferenceAndEvaluation`).
- Frontend: Ready for **Milestone F5: Assessment Output & Forecasting Screens** (`frontend/assessment-output-screens`).
