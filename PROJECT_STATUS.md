# MedOracle Backend: Project Status

**Current Milestone:** Step 3 Complete (Authentication & Security)  
**Next Milestone:** Step 4 (Patient Data APIs)  
**Last Updated:** 2026-10-14  
**Active Environment:** Windows 10, Python 3.14.0 (`backend\.venv`), FastAPI  

---

## Roadmap Execution Status

| Step | Milestone Name | Status | Completion Date | Key Outputs / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Audit and Plan** | **Done** | **2026-10-13** | Architecture audit, roadmap defined, skeleton API contract, dependency comparison complete. |
| **1** | **App Foundation** | **Done** | **2026-10-13** | Config class, app factory, CORS, request logging, standard error handlers, `/health`, `/api/v1/`, runner script verified. |
| **2** | **Complete Database, Schemas & Schema Docs** | **Done** | **2026-10-14** | 10 SQLAlchemy 2.0 ORM models, Alembic baseline migration, Pydantic v2 schemas, database repositories, unit test suite (17 passed), and `docs/architecture/DATABASE_SCHEMA.md`. |
| **3** | **Authentication & Security** | **Done** | **2026-10-14** | Custom JWT (`python-jose`) + `bcrypt` 5.x directly (rounds=12), `/register`, `/login`, `/refresh`, `/me`, `get_current_user` dependency, 32 passed tests. |
| **4** | Patient Data APIs | Pending (Next) | — | Profiles, symptoms, history, labs with strict tenant isolation. |
| **5** | Clinical Risk Models | Pending | — | Pure Python: Framingham 10-year CVD, FINDRISC, CKD-EPI 2021 with citations. |
| **6** | ML Dataset Acquisition & Preprocessing | Pending | — | Download UCI Heart, PIMA Diabetes, Disease-Symptom datasets; cleaning, scaling, and splitting pipelines. |
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
- Test suite: **32 passed** across unit configuration tests, health integration tests, database/repository tests, security tests, and auth integration tests.
- **Authentication & Security (Step 3)**:
  - Custom JWT authentication using `python-jose` with HS256 algorithm and standard claims (`sub`, `exp`, `type`, `iat`).
  - Direct `bcrypt` password hashing (rounds=12) avoiding incompatible legacy wrappers.
  - Auth endpoints implemented and mounted under `/api/v1/auth`:
    - `POST /register`: Registers new users, checks uniqueness, creates User and PatientProfile records, returns 201 Created.
    - `POST /login`: Validates credentials, rejects inactive accounts, issues access and refresh tokens.
    - `POST /refresh`: Validates refresh token type and expiration, issues new access token.
    - `GET /me`: Returns authenticated user's profile and metadata via `get_current_user` dependency.

### Security Audit (Step 3 Verification)
- **Zero Plaintext Passwords**: `users.hashed_password` only stores salted bcrypt hashes (work factor 12).
- **No Passlib Incompatibility**: Using modern, actively maintained `bcrypt` directly.
- **Strong Token Separation**: Access and refresh tokens carry explicit `type` claims (`type="access"` vs `type="refresh"`); refresh endpoint explicitly rejects access tokens and vice-versa.
- **Signature & Tamper Protection**: All JWTs verify HMAC-SHA256 signature with secret key; tampered or expired tokens return 401 Unauthorized immediately.
- **UUID v4 Identifiers**: All primary keys are UUIDs (`String(36)`), preventing ID enumeration.
- **SQL Injection Prevention**: Only SQLAlchemy 2.0 ORM select/insert/update expressions are used; zero raw string interpolation.
- **Strict Multi-Tenant Scoping**: All patient health data models and queries enforce `user_id` foreign keys with cascade deletion.
- **Credential Hygiene**: No secrets committed; database URL and JWT secrets point to configurable environment variables (`.env` git-ignored).

### Next Action
- Awaiting user instruction to begin **Step 4: Patient Data APIs**.
