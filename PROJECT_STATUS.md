# MedOracle Backend: Project Status

**Current Milestone:** Step 5 Complete (Clinical Risk Models)  
**Next Milestone:** Step 6 (ML Dataset Acquisition & Preprocessing)  
**Last Updated:** 2026-10-19  
**Active Environment:** Windows 10, Python 3.14.0 (`backend\.venv`), FastAPI  

---

## Roadmap Execution Status

| Step | Milestone Name | Status | Completion Date | Key Outputs / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Audit and Plan** | **Done** | **2026-10-13** | Architecture audit, roadmap defined, skeleton API contract, dependency comparison complete. |
| **1** | **App Foundation** | **Done** | **2026-10-13** | Config class, app factory, CORS, request logging, standard error handlers, `/health`, `/api/v1/`, runner script verified. |
| **2** | **Complete Database, Schemas & Schema Docs** | **Done** | **2026-10-14** | 10 SQLAlchemy 2.0 ORM models, Alembic baseline migration, Pydantic v2 schemas, database repositories, unit test suite (17 passed), and `docs/architecture/DATABASE_SCHEMA.md`. |
| **3** | **Authentication & Security** | **Done** | **2026-10-14** | Custom JWT (`python-jose`) + `bcrypt` 5.x directly (rounds=12), `/register`, `/login`, `/refresh`, `/me`, `get_current_user` dependency, 32 passed tests. |
| **4** | **Patient Data APIs** | **Done** | **2026-10-14** | Profiles, medical/family history, symptom reports, and lab results APIs with strict multi-user tenant isolation. 39 passed tests. |
| **5** | **Clinical Risk Models** | **Done** | **2026-10-19** | Pure Python: Framingham 10-year CVD (D'Agostino 2008), FINDRISC (Lindström 2003), CKD-EPI 2021 race-free eGFR (Inker 2021). Endpoints mounted at `/api/v1/risk/`. 54 passed tests. |
| **6** | ML Dataset Acquisition & Preprocessing | Pending (Next) | — | Download UCI Heart, PIMA Diabetes, Disease-Symptom datasets; cleaning, scaling, and splitting pipelines. |
| **7** | ML Model Training & Registry | Pending | — | Training classification models (RF, LightGBM, Logistic Regression); artifact serialization; `MODEL_REGISTER.md`. |
| **8** | ML Evaluation & Inference Service | Pending | — | Evaluation metrics (ROC-AUC, F1); real-time feature transformation and prediction service in `app/ml/inference/`. |
| **9** | LLM Service & Fallback Routing | Pending | — | Groq (primary) + Gemini (fallback) + Mock provider, structured JSON validation. |
| **10**| Agent Base & Domain Agents | Pending | — | Standard agent contract: Symptom, History, Lab, and Risk agents (ensembling clinical formulas + ML inference). |
| **11**| LangGraph Pipeline | Pending | — | Graph state, parallel data agent execution, fault-tolerant aggregation. |
| **12**| Consensus & Debate Framework | Pending | — | 5-step consensus debate protocol (core FYP research contribution). |
| **13**| Explainability, Forecasting & Doctors | Pending | — | Flutter `graphview` export, 30d/6m/1y trajectory, counterfactual simulator, doctor matcher. |
| **14**| Analysis Orchestration API | Pending | — | Async analysis dispatch, polling, end-to-end result aggregation. |
| **15**| End-to-End System Benchmark | Pending | — | Benchmark validation on held-out test splits; clinical accuracy vs agent reasoning. |
| **16**| Hardening and Deployment | Pending | — | Rate limiting, Dockerfile, Render config, CI pipeline, final docs. |

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

### Security Audit (Step 5 Verification)
- **Strict Authentication**: All risk calculation endpoints require `get_current_user`; unauthenticated requests return 401 Unauthorized.
- **Pydantic Validation**: Biological parameters strictly bounded (e.g., age 18-120, serum creatinine > 0, cholesterol 50-600 mg/dL, systolic BP 60-260 mmHg) with 422 Unprocessable Entity returned on out-of-range inputs.
- **Medical Safety Disclaimer**: Every response carries a legally compliant clinical decision-support disclaimer.

### Next Action
- Awaiting user instruction to begin **Step 6: ML Dataset Acquisition & Preprocessing Pipeline**.
