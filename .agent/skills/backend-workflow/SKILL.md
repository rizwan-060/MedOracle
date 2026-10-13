---
name: backend-workflow
description: Runs one step of the MedOracle backend roadmap (FastAPI, database, auth, clinical models, LLM layer, agents, LangGraph, consensus, API). Use whenever the user asks to start, continue, or do the next backend step, or invokes /backend-workflow.
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
6. **Report and stop.** Reply with: what was built, how to run and test it (exact CMD commands), test results, decisions you made, what you need from the user, and a suggested git commit message. Then wait. Do not start the next step.

## Definition of done for every step
- `pytest` passes, with new tests for the new behaviour.
- `uvicorn app.main:app` starts without errors and `/health` responds.
- No secrets in the repo. New settings are in `.env.example`.
- Status and API docs are updated.

## Roadmap

Statuses live in `PROJECT_STATUS.md`. The step numbers below are stable. Use them when talking to the user.

### Step 0. Audit and plan (no application code)
Inspect `backend/` and the root docs. Fill `IMPLEMENTATION_PLAN.md` with this roadmap, adapted to what you find, and create the status table in `PROJECT_STATUS.md`. Write a skeleton `API_CONTRACT.md`. Check `requirements.txt` against what `.venv` has installed and list what is missing for later steps. Report any conflict between the proposal and the repo.

### Step 1. App foundation
Files: `app/core/config.py`, `app/main.py`, `app/api/router.py`, `app/api/v1/__init__.py`, `.env.example`.
Settings class, app factory, CORS, request logging, consistent error responses, `/health`, versioned router mounted at `/api/v1`. Tests: `tests/unit` for config, `tests/integration` for `/health`. Confirm `scripts\run_backend.bat` works.

### Step 2. Database and migrations
Files: `app/database/session.py`, `models.py`, `repositories.py`, `migrations/` (Alembic), `alembic.ini`.
Tables for users, patient profiles, medical history entries, symptom reports, lab results, analysis sessions, agent outputs, risk results, doctors. Use the generic `JSON` type for flexible payloads. `migrations/` is empty apart from a `.gitkeep`: create `env.py`, `script.py.mako` and `versions/` there by hand or by running `alembic init` into a temporary folder and copying the files in. Generate the first migration and apply it. Repository classes wrap all queries. Tests run on in-memory SQLite.

### Step 3. Authentication
Files: `app/core/security.py`, `app/schemas/auth.py`, `app/api/v1/auth.py`.
Register, login, refresh, current user, access and refresh JWTs, bcrypt hashing, a reusable `get_current_user` dependency. Tests for the happy path, wrong password, duplicate email, expired and tampered tokens.

### Step 4. Patient data APIs
Files: `app/schemas/patient.py`, `symptoms.py`, `laboratory.py`, `app/api/v1/symptoms.py`, `medical_history.py`, `laboratory.py`.
Create, read, update and list endpoints for profile, medical and family history, symptom reports, and lab results. Every record belongs to the logged-in user and one user can never read another's data (test this explicitly).

### Step 5. Clinical risk models (pure Python, no LLM)
Files: `app/clinical/cardiovascular.py`, `diabetes.py`, `kidney.py`.
Framingham 10-year cardiovascular risk, FINDRISC diabetes score, CKD-EPI eGFR. Follow the clinical correctness rules: cited equations, worked-example tests, ask when unsure. Each returns the value, the category, and the inputs that were missing or assumed.

### Step 6. LLM service
Files: `app/services/llm_service.py`, `app/core/config.py` (LLM settings).
One interface with Groq primary, Gemini fallback, and a mock provider for tests. Structured JSON output validated against a Pydantic schema, retry with backoff, timeout, automatic fallback on provider failure, token and latency logging. Keys come from `.env`. Ask the user for their keys when you reach the manual smoke test.

### Step 7. Agent base and the first agents
Files: `app/agents/` (shared agent output model and base class, then `symptom_agent.py`, `medical_history_agent.py`, `laboratory_agent.py`, `risk_prediction_agent.py`).
Every agent follows the output contract in the rules. Each works deterministically when the LLM is unavailable (rules and clinical models) and adds LLM reasoning when it is. Risk Prediction combines the other agents' outputs with the clinical models for 30-day, 6-month and 1-year horizons.

### Step 8. LangGraph pipeline
Files: `app/graph/state.py`, `nodes.py`, `workflow.py`.
Symptom, history and lab agents run in parallel, then risk prediction, then a placeholder consensus node, then output. Typed shared state, per-node error handling so one failed agent does not kill the run, and a recorded trace of every node's output.

### Step 9. Consensus and debate agent (core research contribution)
Files: `app/agents/consensus_agent.py`, `app/graph/` (debate nodes).
The five-step protocol from the brief: evidence submission, contradiction detection, challenge round, confidence adjustment, consensus resolution. Contradiction detection must be deterministic and testable. Bound the number of rounds. Keep the full debate transcript, because the app and the report both need it. Test with hand-built contradictory agent outputs.

### Step 10. Explainability, forecasting, counterfactuals, doctors
Files: `app/agents/explainability_agent.py`, `app/forecasting/trajectory.py`, `app/counterfactual/simulator.py`, `app/agents/counterfactual_agent.py`, `app/agents/disease_trajectory_agent.py`, `app/agents/doctor_recommendation_agent.py`, `app/doctors/recommendations.py`.
Reasoning graph as JSON nodes and edges the Flutter `graphview` package can draw. Trajectory over 30 days, 6 months and 1 year. A counterfactual simulator with at least three interventions (daily walking, diet change, smoking cessation). Doctor matching from the consensus verdict to a specialty, ranked by specialty match and distance, over a small sample dataset until the real one exists.

### Step 11. Analysis API and orchestration
Files: `app/services/analysis_service.py`, `prediction_service.py`, `app/schemas/analysis.py`, `risk.py`, `app/api/v1/analysis.py`, `risk.py`, `doctors.py`.
Start an analysis (returns a session id immediately), poll its status, fetch the full result (agent outputs, debate, risk, trajectory, counterfactuals, reasoning graph, doctors, disclaimer). Finalize `API_CONTRACT.md` so the Flutter developers can build against it.

### Step 12. Validation against public datasets
Files: `app/ml/evaluation/`, `app/ml/preprocessing/`, `app/ml/model_registry.py`, `scripts/`, `tests/ml/`.
Validate the clinical models and the pipeline against UCI Heart Disease, PIMA Indians Diabetes and Framingham. The user must download the datasets into `datasets/raw/` first (ask for them). Report honest metrics, including where the system performs badly. Update `DATASET_REGISTER.md` and `MODEL_REGISTER.md`.

### Step 13. Hardening and deployment
Rate limiting, input size limits, security review, structured logging, optional Celery and Redis, Dockerfile, Render deployment config, GitHub Actions running the tests, final README.

## Stop-and-ask list
Stop and ask the user instead of continuing when:
- you need an API key, database URL, or dataset they have not provided
- a clinical coefficient, threshold or reference range is uncertain
- the proposal and the repo disagree, or a roadmap step needs a decision not covered by the rules
- tests fail and the cause is outside the current step
