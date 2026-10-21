# MedOracle Frontend: Project Status

**Current Milestone:** Milestone F4 (Backend Connectivity & Wizard Flow Integration) — Completed  
**Active Working Branch:** `frontend/assessment-input-integration` (child branch of `frontend/assessment-input-screen`)  
**Team Base Branches on Remote:**
- `origin/frontend/assessment-input-screen` (Steps 1–5 intake wizard screens, Riverpod step providers, UI widgets)
- `origin/frontend/assessment-output-screens` (Initial Step 1 profile screen and base token definitions)
- `origin/frontend/auth-screens` (Auth screens base)  
**Last Updated:** 2026-10-21  
**Framework:** Flutter (Dart 3.13.5), Riverpod (`flutter_riverpod: ^3.3.2`), GoRouter (`go_router: ^14.8.1`), HTTP (`http: ^1.2.2`)  
**Static Analysis:** 0 errors, 0 warnings (`dart analyze` clean)  
**Test Suite:** 12 passed tests across widget and backend integration suites (`flutter test`)  

---

## Screen Hierarchy & Backend Route Map

| Step / Flow | Route Path | Screen Widget | Provider / Controller | Backend API Target | Connectivity Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Intake Step 1** | `/intake/step-1` | `ProfileScreen` | `profileControllerProvider` | `GET/PUT /api/v1/patient/profile` | **Connected & Autosaved** (with offline cache fallback) |
| **Intake Step 2A** | `/intake/step-2a` | `ClinicalStatusScreen` | `clinicalStatusProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (chronic conditions, past surgeries, allergies, notes) |
| **Intake Step 2B** | `/intake/step-2b` | `MedicationsFamilyScreen` | `medicationsFamilyProvider` | `GET/PUT /api/v1/medical-history/` | **Connected & Autosaved** (current medications & family history records) |
| **Intake Step 3** | `/intake/step-3` | `SymptomsScreen` | `symptomsProvider` | `POST /api/v1/symptoms/`<br>`GET /api/v1/symptoms/` | **Connected & Submitted** (chief symptoms, location, triggers, duration, notes) |
| **Intake Step 4** | `/intake/step-4` | `LabsVitalsScreen` | `labsVitalsProvider` | `GET /api/v1/laboratory/latest`<br>`POST /api/v1/laboratory/` | **Connected & Submitted** (metabolic panel, BP, lipid panel, creatinine) |
| **Intake Step 5** | `/intake/step-5` | `ReviewConfirmScreen` | `reviewProfileProvider` (combiner) | All domain entities summary | **Connected** (Flushes all controllers to backend on submit) |
| **Results (Placeholder)**| `/results/reports` | `PendingStepScreen` | — | `/api/v1/analysis/` (deferred to Step 14) | **Intact Fallback** (awaiting backend analysis endpoint) |
| **Assessment Output** | `/results/trajectory` | TBD (Milestone F5) | — | Multi-agent forecasting API | Scheduled |
| **Reasoning Graph** | `/results/reasoning` | TBD (Milestone F6) | — | `/api/v1/analysis/{id}/graph` | Scheduled |

---

## Key Architectural Deliverables Completed

1. **GoRouter via Riverpod Provider**:
   - `routerProvider` declared in `lib/core/routing/app_router.dart` exposing reactive `GoRouter`.
   - `MedOracleApp` in `lib/main.dart` refactored to `ConsumerWidget` watching `routerProvider`.
2. **REST API Client Service**:
   - `ApiService` implemented in `lib/data/services/api_service.dart` wrapping `http.Client`.
   - Supports configurable `MEDORACLE_API_URL` environment variable defaulting to `http://127.0.0.1:8000/api/v1`.
   - Built-in Bearer JWT header handling, 10-second timeout enforcement, and standardized `ApiException` decoding.
3. **Pydantic v2 Aligned Domain Models**:
   - `PatientProfile`: bidirectional conversion between UI presentation and backend snake_case format (`date_of_birth`, `smoking_status`, `activity_level`).
   - `MedicalHistoryModel`: structured mapping of conditions, surgeries, allergies, medications, and family records.
   - `SymptomReportModel`: validation with `min_length` handling for clinical symptom submissions.
   - `LabResultModel`: structured biomarker mapping for metabolic, cardiovascular, and renal laboratory values.
4. **Resilient Repository Pattern**:
   - `RestIntakeRepository`, `RestMedicalHistoryRepository`, `RestSymptomsRepository`, and `RestLaboratoryRepository` created and injected via `repository_providers.dart`.
   - All repositories include graceful local cache fallbacks so local offline widget tests and network outages never crash the user interface.
5. **Multi-Step State Synchronization**:
   - Step 5 `ReviewConfirmScreen` now dynamically reads live patient demographic facts from `profileControllerProvider`.
   - "Submit Assessment" flushes and synchronizes state across all step controllers before routing forward.

---

## Verification & Test Results

- `dart analyze`: **0 errors, 0 warnings** across all files.
- `flutter test`: **12/12 passed tests**:
  - `profile_screen_test.dart`: Section rendering, accordions, and autosave transitions.
  - `step1_render_test.dart`: Step 1 layout rendering at 390x844.
  - `widget_test.dart`: Wizard navigation smoke test.
  - `intake_integration_test.dart`: Route constants, model serialization, and resilient fallback handling.
