# MedOracle API Contract

**Base URL (Development):** `http://localhost:8000`  
**API Version:** `v1`  
**API V1 Prefix:** `/api/v1`  
**Mandatory Clinical Disclaimer:**  
> "MedOracle is a clinical decision-support assistant designed for proactive health risk assessment. It does not replace medical advice, clinical judgment, or professional diagnosis."

---

## 1. Conventions & Standards

### Authentication
- Uses Bearer JWT authentication: `Authorization: Bearer <access_token>`.
- Token contains user identifier (`sub`), issued timestamp (`iat`), and expiration (`exp`).

### Standard Error Schema
All error responses return a standardized JSON structure with appropriate HTTP status codes:
```json
{
  "detail": "Descriptive error message",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2026-10-13T23:50:00Z"
}
```

---

## 2. Health & System Endpoints

### `GET /`
- **Auth:** None
- **Response `200 OK`**:
```json
{
  "project": "MedOracle",
  "message": "MedOracle API is running",
  "version": "0.1.0",
  "environment": "development"
}
```

### `GET /health`
- **Auth:** None
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "medoracle-backend",
  "version": "0.1.0",
  "environment": "development"
}
```

### `GET /api/v1/`
- **Auth:** None
- **Response `200 OK`**:
```json
{
  "version": "v1",
  "status": "active",
  "description": "MedOracle API v1 root"
}
```

---

## 3. Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/register`
- **Auth:** None
- **Request Body**:
```json
{
  "email": "patient@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "age": 45,
  "gender": "male"
}
```
- **Response `201 Created`**:
```json
{
  "id": "usr_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "patient@example.com",
  "full_name": "John Doe",
  "created_at": "2026-10-13T23:50:00Z"
}
```
- **Error Codes:** `400 Bad Request` (Email already registered, weak password), `422 Validation Error`.

### `POST /api/v1/auth/login`
- **Auth:** None
- **Request Body**:
```json
{
  "username": "patient@example.com",
  "password": "SecurePassword123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
- **Error Codes:** `401 Unauthorized` (Invalid credentials).

### `POST /api/v1/auth/refresh`
- **Auth:** None
- **Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn..."
}
```
- **Response `200 OK`**: Same token structure as `/login`.
- **Error Codes:** `401 Unauthorized` (Invalid or expired refresh token).

### `GET /api/v1/auth/me`
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "id": "usr_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "patient@example.com",
  "full_name": "John Doe",
  "age": 45,
  "gender": "male",
  "created_at": "2026-10-13T23:50:00Z"
}
```
- **Error Codes:** `401 Unauthorized`.

---

## 4. Patient Data APIs

### `GET /api/v1/patient/profile`
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "user_id": "usr_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "date_of_birth": "1981-05-14",
  "gender": "male",
  "height_cm": 178.0,
  "weight_kg": 84.5,
  "waist_circumference_cm": 94.0,
  "smoking_status": "current_smoker",
  "activity_level": "low"
}
```

### `PUT /api/v1/patient/profile`
- **Auth:** Bearer Token
- **Request Body**: JSON fields matching profile schema.
- **Response `200 OK`**: Updated profile.

### `POST /api/v1/symptoms`
- **Auth:** Bearer Token
- **Request Body**:
```json
{
  "reported_text": "Severe chest tightness radiating to left arm when climbing stairs, shortness of breath for past 3 days.",
  "duration_days": 3,
  "severity_self_rating": 8
}
```
- **Response `201 Created`**:
```json
{
  "id": "sym_01h7x8...",
  "user_id": "usr_9b1deb4d...",
  "reported_text": "Severe chest tightness...",
  "duration_days": 3,
  "severity_self_rating": 8,
  "created_at": "2026-10-13T23:50:00Z"
}
```

### `GET /api/v1/symptoms`
- **Auth:** Bearer Token
- **Response `200 OK`**: List of recorded symptom reports for the current user.

### `POST /api/v1/medical-history`
- **Auth:** Bearer Token
- **Request Body**:
```json
{
  "conditions": ["hypertension"],
  "medications": ["amlodipine 5mg"],
  "family_history": [
    {"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 52},
    {"relative": "mother", "condition": "type_2_diabetes", "age_at_onset": 60}
  ],
  "allergies": []
}
```
- **Response `201 Created`**: Saved medical history object.

### `POST /api/v1/laboratory`
- **Auth:** Bearer Token
- **Request Body**:
```json
{
  "test_date": "2026-10-10",
  "values": {
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "total_cholesterol_mg_dl": 240,
    "hdl_cholesterol_mg_dl": 38,
    "fasting_blood_glucose_mg_dl": 115,
    "serum_creatinine_mg_dl": 1.1,
    "hba1c_percent": 6.1
  }
}
```
- **Response `201 Created`**: Saved laboratory record.

---

## 5. Pure Clinical Risk Models (`/api/v1/risk`)

Direct deterministic risk calculation endpoints (pure Python, verified equations):

### `POST /api/v1/risk/cardiovascular`
- **Auth:** Bearer Token
- **Request Body**:
```json
{
  "age": 55,
  "gender": "male",
  "total_cholesterol_mg_dl": 220,
  "hdl_cholesterol_mg_dl": 42,
  "systolic_bp": 140,
  "is_treated_for_hypertension": true,
  "is_smoker": true,
  "has_diabetes": false
}
```
- **Response `200 OK`**:
```json
{
  "model": "Framingham 10-Year General Cardiovascular Risk (D'Agostino 2008)",
  "risk_score_percent": 21.4,
  "risk_category": "high",
  "missing_or_assumed": [],
  "disclaimer": "MedOracle is a decision-support assistant and does not provide clinical diagnosis."
}
```

### `POST /api/v1/risk/diabetes`
- **Auth:** Bearer Token
- **Request Body**: FINDRISC parameters (age, BMI, waist circumference, physical activity, vegetable/fruit intake, hypertension medication, history of high blood glucose, family history of diabetes).
- **Response `200 OK`**: FINDRISC score (0–26), 10-year risk category (low to very high), and disclaimer.

### `POST /api/v1/risk/kidney`
- **Auth:** Bearer Token
- **Request Body**: Serum creatinine, age, gender.
- **Response `200 OK`**: CKD-EPI 2021 eGFR (mL/min/1.73m²), stage classification (G1–G5), and disclaimer.

---

## 6. Multi-Agent Analysis Pipeline (`/api/v1/analysis`)

### `POST /api/v1/analysis/start`
Triggers background LangGraph orchestration.
- **Auth:** Bearer Token
- **Request Body**:
```json
{
  "symptom_report_id": "sym_01h7x8...",
  "include_latest_labs": true,
  "include_medical_history": true
}
```
- **Response `202 Accepted`**:
```json
{
  "session_id": "ses_550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "created_at": "2026-10-13T23:50:00Z",
  "estimated_duration_seconds": 12
}
```

### `GET /api/v1/analysis/{session_id}/status`
Polling endpoint for client progress bar.
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "session_id": "ses_550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "current_phase": "consensus_debate",
  "progress_percent": 75,
  "error": null
}
```

### `GET /api/v1/analysis/{session_id}/result`
Complete multi-agent analysis output.
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "session_id": "ses_550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "consensus_verdict": {
    "primary_risk_category": "Cardiovascular Disease / Coronary Artery Disease Risk",
    "overall_urgency": "high",
    "consensus_confidence": 88.5,
    "summary": "High risk of premature CAD suggested by exertional symptoms and strong paternal early CAD history."
  },
  "agent_outputs": {
    "symptom_agent": {
      "role": "Symptom Analysis Agent",
      "findings": "Exertional angina symptom cluster identified.",
      "confidence": 85.0,
      "reasoning_chain": ["Reported chest tightness with arm radiation", "Triggered by physical exertion"],
      "evidence": ["Duration 3 days", "Severity rating 8/10"],
      "challenges": []
    },
    "medical_history_agent": {
      "role": "Medical History Agent",
      "findings": "Significant hereditary multiplier from father's premature MI at age 52.",
      "confidence": 90.0,
      "reasoning_chain": ["First-degree relative premature CVD"],
      "evidence": ["Paternal MI < 55 yrs"],
      "challenges": []
    },
    "laboratory_agent": {
      "role": "Laboratory Analysis Agent",
      "findings": "Dyslipidemia and borderline fasting glucose.",
      "confidence": 82.0,
      "reasoning_chain": ["Total cholesterol 240 mg/dL > 200", "HDL 38 < 40"],
      "evidence": ["Lab record dated 2026-10-10"],
      "challenges": []
    },
    "risk_prediction_agent": {
      "role": "Risk Prediction Agent",
      "findings": "Framingham 10-year risk calculated at 21.4% (high risk tier).",
      "confidence": 88.0,
      "reasoning_chain": ["Integrated clinical formula with biomarker and symptom profile"],
      "evidence": ["Calculated score: 21.4%"],
      "challenges": []
    }
  },
  "debate_summary": {
    "rounds_conducted": 2,
    "contradictions_detected": ["Lab agent noted normal renal markers vs Symptom agent rating severity 8"],
    "resolution_notes": "Symptom agent maintained high urgency based on exertional nature; consensus weighted clinical risk."
  },
  "trajectory": {
    "30_days": {"projected_risk_score": 22.0, "status": "stable_high"},
    "6_months": {"projected_risk_score": 24.5, "status": "progressive"},
    "1_year": {"projected_risk_score": 27.8, "status": "progressive_elevated"}
  },
  "counterfactuals": [
    {
      "intervention": "Smoking cessation",
      "projected_risk_1_year": 18.2,
      "risk_reduction_absolute": 9.6
    },
    {
      "intervention": "Daily 30-minute brisk walking",
      "projected_risk_1_year": 23.1,
      "risk_reduction_absolute": 4.7
    },
    {
      "intervention": "Combined lifestyle optimization (Diet + Exercise + Smoking Cessation)",
      "projected_risk_1_year": 14.5,
      "risk_reduction_absolute": 13.3
    }
  ],
  "recommended_specialty": "Cardiology",
  "disclaimer": "MedOracle is a decision-support assistant and does not provide clinical diagnosis. Consult a qualified medical practitioner."
}
```

### `GET /api/v1/analysis/{session_id}/debate`
Detailed turn-by-turn debate transcript for FYP report evaluation and frontend debate inspection.
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "session_id": "ses_550e8400...",
  "transcript": [
    {
      "step": 1,
      "phase": "evidence_submission",
      "contributions": [...]
    },
    {
      "step": 2,
      "phase": "contradiction_detection",
      "flagged_contradictions": [...]
    },
    {
      "step": 3,
      "phase": "challenge_round",
      "exchanges": [...]
    },
    {
      "step": 4,
      "phase": "confidence_adjustment",
      "adjusted_scores": {"symptom": 85.0, "history": 90.0, "lab": 82.0}
    },
    {
      "step": 5,
      "phase": "consensus_resolution",
      "final_verdict": "..."
    }
  ]
}
```

### `GET /api/v1/analysis/{session_id}/reasoning-graph`
Node-and-edge graph payload designed specifically for Flutter's `graphview` package.
- **Auth:** Bearer Token
- **Response `200 OK`**:
```json
{
  "nodes": [
    {"id": "n_symptom", "label": "Exertional Angina (Severity 8)", "type": "symptom", "confidence": 85.0},
    {"id": "n_history", "label": "Paternal Premature MI (Age 52)", "type": "history", "confidence": 90.0},
    {"id": "n_lab", "label": "Cholesterol 240 mg/dL", "type": "lab", "confidence": 82.0},
    {"id": "n_risk", "label": "Framingham 10-Yr Risk: 21.4%", "type": "risk", "confidence": 88.0},
    {"id": "n_consensus", "label": "High CAD Risk Consensus", "type": "consensus", "confidence": 88.5}
  ],
  "edges": [
    {"source": "n_symptom", "target": "n_risk", "weight": 0.8},
    {"source": "n_history", "target": "n_risk", "weight": 0.9},
    {"source": "n_lab", "target": "n_risk", "weight": 0.82},
    {"source": "n_risk", "target": "n_consensus", "weight": 1.0}
  ]
}
```

---

## 7. Doctor Recommendation APIs (`/api/v1/doctors`)

### `GET /api/v1/doctors/recommendations`
Returns nearby doctors matching the specialty derived from the consensus verdict.
- **Auth:** Bearer Token
- **Query Parameters**:
  - `specialty`: e.g. `Cardiology`, `Endocrinology`, `Nephrology`
  - `urgency`: `low`, `moderate`, `high`, `immediate`
  - `lat`: optional float
  - `lng`: optional float
  - `limit`: default 5
- **Response `200 OK`**:
```json
{
  "specialty": "Cardiology",
  "urgency": "high",
  "doctors": [
    {
      "id": "doc_101",
      "name": "Dr. Sarah Khan",
      "specialty": "Cardiology",
      "hospital_clinic": "National Institute of Cardiovascular Diseases",
      "area": "Gulberg, Lahore",
      "contact_phone": "+92 42 111 222 333",
      "distance_km": 3.4,
      "rating": 4.9
    }
  ],
  "disclaimer": "Doctor recommendations are provided for second opinion referral and decision support."
}
```
