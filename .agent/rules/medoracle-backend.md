---
trigger: always_on
---

# MedOracle: project rules (always on)

MedOracle is a final year project: a multi-agent disease forecasting platform. Flutter app in `frontend/`, Python FastAPI service in `backend/`. Read `docs/architecture/PROJECT_BRIEF.md` for what the system is. This file says how to work on it.

## Environment
- OS is Windows 10. Use CMD or PowerShell syntax in terminal commands, never bash-only syntax.
- The backend virtual environment already exists at `backend\.venv` (Python 3.14). Run tools through it:
  - `backend\.venv\Scripts\python -m pytest backend\tests`
  - `backend\.venv\Scripts\python -m pip install <pkg>`
  - `backend\.venv\Scripts\python -m uvicorn app.main:app --reload` (run from `backend\`)
- Every new dependency goes into `backend\requirements.txt` with a pinned version, in the same step that first imports it.
- If a dependency has no Python 3.14 wheel or fails to install, stop and tell the user. Do not switch Python versions or work around it silently.
- Helper scripts already exist in `scripts\`: `setup_backend.bat`, `run_backend.bat`, `verify_structure.bat`. Reuse them, don't duplicate them.

## Repository rules
- The folder structure already exists. Put code in the existing files and folders first. Create a new file only when no existing one fits, and say why in your summary.
- Existing empty placeholder files (0 bytes) are meant to be filled in. Keep `__init__.py` files.
- Never touch `frontend/` while doing backend work, and never edit anything inside `.venv`.
- Never commit or write real secrets. Secrets live in `backend\.env` (git-ignored). Add every variable to `backend\.env.example` with a dummy value.
- Do not run `git push`, `git reset`, `git rebase` or any history-changing command. At the end of a step, suggest a commit message and let the user commit.

## Technical decisions already made
These differ slightly from the proposal because of what is installed. Do not revisit them without asking.
- Auth is custom JWT (`python-jose`) with passwords hashed using the `bcrypt` package directly. The proposal names `fastapi-users`, but it is not installed and the existing file layout (`core/security.py`, `api/v1/auth.py`) fits a custom setup. Do not use `passlib`: version 1.7.4 is incompatible with the installed `bcrypt` 5.x.
- Database: SQLAlchemy 2.x with the sync engine and `psycopg` 3 (PostgreSQL, Supabase in production). Use the generic `JSON` column type so the same models run on SQLite in unit tests.
- Background work: start with FastAPI `BackgroundTasks` and a status field on the analysis session that the app polls. Celery and Redis are deferred to the hardening step, because Redis does not run natively on Windows.
- LLM providers: Groq is primary and Gemini Flash is the fallback. Verify the current model IDs against the providers' documentation before writing them into config, because model names change. Model IDs and API keys come from settings, never hard-coded.
- No model training from scratch. Clinical risk formulas are the quantitative backbone and LLM agents add reasoning on top.

## Engineering standards
- Python 3.14, type hints everywhere, Pydantic v2 models for every API input and output.
- Routers stay thin: validation and HTTP only. Logic lives in `services/`, `agents/`, `clinical/`. Database access lives only in `database/repositories.py`.
- All settings come from `core/config.py` (pydantic-settings). No `os.environ` calls scattered around.
- Every agent returns the same structured output: role, findings, confidence (0 to 100), reasoning chain, evidence, challenges. Agents see only each other's outputs and confidence scores, never each other's prompts.
- Unit tests never call a real LLM or the network. Use the mock LLM provider.
- Every new behaviour gets a test in `backend/tests/unit` or `backend/tests/integration`. A step is not finished until `pytest` passes and the app starts.
- Keep functions small and docstrings short. Comments explain why, not what.

## Clinical correctness (the part that cannot be faked)
- Never invent coefficients, thresholds or reference ranges. Implement Framingham, FINDRISC and CKD-EPI from the published equations, put the citation in the docstring, and add a test using a worked example from the paper or a trusted calculator.
- If you are not certain of a coefficient or cut-off, stop and ask the user. Do not guess and do not leave a plausible-looking placeholder.
- The proposal cites Lloyd-Jones 2004 (lifetime risk) for Framingham. If you implement a different Framingham equation, say exactly which one in your summary so the report can cite it correctly.
- MedOracle is decision support, not diagnosis. Every risk response includes a disclaimer field, and no text the system generates may claim a diagnosis.

## Working style
- Do one roadmap step at a time using the `backend-workflow` skill. Do not start the next step until the user says so.
- Keep the user informed in plain language. End every step with: what was built, how to run it, what was tested, and what you need from the user.
- Stop and ask when you need an API key, a dataset, a decision, or when something in the proposal and the repo disagree.
