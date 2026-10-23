# MedOracle Postman API Testing Guide & Specification

> **Base URL:** `http://127.0.0.1:8000`  
> **API Version Prefix:** `/api/v1`  
> **Documentation Rule:** Whenever a new endpoint is created or updated in the backend, its request specification, example JSON payloads, expected status codes, and Postman test script **must** be added to this file.

---

## Table of Contents
1. [Postman Environment Configuration](#1-postman-environment-configuration)
2. [Testing Sequence & Workflow](#2-testing-sequence--workflow)
3. [System Endpoints](#3-system-endpoints)
4. [Authentication APIs (`/api/v1/auth`)](#4-authentication-apis-apiv1auth)
5. [Patient Profile APIs (`/api/v1/patient`)](#5-patient-profile-apis-apiv1patient)
6. [Medical History APIs (`/api/v1/medical-history`)](#6-medical-history-apis-apiv1medical-history)
7. [Symptom Reporting APIs (`/api/v1/symptoms`)](#7-symptom-reporting-apis-apiv1symptoms)
8. [Laboratory Biomarker APIs (`/api/v1/laboratory`)](#8-laboratory-biomarker-apis-apiv1laboratory)
9. [Clinical Risk Prediction APIs (`/api/v1/risk`)](#9-clinical-risk-prediction-apis-apiv1risk)
10. [Real-Time Machine Learning Prediction APIs (`/api/v1/predictions`)](#10-real-time-machine-learning-prediction-apis-apiv1predictions)
11. [Future Endpoints Checklist](#11-future-endpoints-checklist)

---

## 1. Postman Environment Configuration

To make testing seamless, set up a Postman Environment named **`MedOracle Local`** with the following variables:

| Variable Name | Initial Value | Current Value | Description |
| :--- | :--- | :--- | :--- |
| `baseUrl` | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` | Local FastAPI server URL |
| `accessToken` | *(leave empty)* | *(auto-set by Login/Refresh)* | Bearer JWT access token (expires in 30 mins) |
| `refreshToken` | *(leave empty)* | *(auto-set by Login/Refresh)* | Long-lived JWT refresh token (expires in 7 days) |
| `userId` | *(leave empty)* | *(auto-set by Register/Login)* | Authenticated User UUID |
| `symptomReportId`| *(leave empty)* | *(auto-set by Create Symptom)*| ID of newly created symptom report |
| `labResultId` | *(leave empty)* | *(auto-set by Create Lab)* | ID of newly created lab record |

### Common Headers
For all authenticated requests, configure the following header:
```http
Authorization: Bearer {{accessToken}}
Content-Type: application/json
```

---

## 2. Testing Sequence & Workflow

For an end-to-end regression pass, execute requests in this order:

```
[System Health]
   ├── 1. GET /health
   └── 2. GET /api/v1/
        │
[Authentication]
   ├── 3. POST /api/v1/auth/register (Create patient account)
   ├── 4. POST /api/v1/auth/login    (Stores {{accessToken}} & {{refreshToken}})
   ├── 5. GET  /api/v1/auth/me       (Verify token identity)
   └── 6. POST /api/v1/auth/refresh  (Test token renewal)
        │
[Patient Profile]
   ├── 7. GET  /api/v1/patient/profile (Initial auto-provisioned profile)
   └── 8. PUT  /api/v1/patient/profile (Update biometrics & vitals)
        │
[Medical History]
   ├── 9. GET  /api/v1/medical-history/ (Initial 404 check)
   ├── 10. POST /api/v1/medical-history/ (Record chronic diseases, meds, family history)
   └── 11. PUT  /api/v1/medical-history/ (Update history records)
        │
[Symptoms]
   ├── 12. POST   /api/v1/symptoms/ (Submit exertional angina symptoms)
   ├── 13. GET    /api/v1/symptoms/ (List symptoms with pagination)
   ├── 14. GET    /api/v1/symptoms/{{symptomReportId}} (Retrieve single symptom)
   └── 15. DELETE /api/v1/symptoms/{{symptomReportId}} (Clean up symptom report)
        │
[Laboratory Results]
   ├── 16. POST   /api/v1/laboratory/ (Submit lipid panel & biomarkers)
   ├── 17. GET    /api/v1/laboratory/latest (Verify latest lab record)
   ├── 18. GET    /api/v1/laboratory/ (List historical lab reports)
   ├── 19. GET    /api/v1/laboratory/{{labResultId}} (Retrieve single lab report)
   └── 20. DELETE /api/v1/laboratory/{{labResultId}} (Clean up lab report)
        │
[Clinical Risk Prediction]
   ├── 21. POST   /api/v1/risk/cardiovascular (Framingham 10-Yr CVD score)
   ├── 22. POST   /api/v1/risk/diabetes       (FINDRISC Type 2 score)
   └── 23. POST   /api/v1/risk/kidney         (CKD-EPI 2021 race-free eGFR)
        │
[Real-Time ML Predictions & Differential Diagnosis]
   ├── 24. POST   /api/v1/predictions/cardiovascular (GradientBoosting 13-feature CVD risk)
   ├── 25. POST   /api/v1/predictions/diabetes       (RandomForest 8-feature metabolic T2D risk)
   ├── 26. POST   /api/v1/predictions/symptoms       (MultinomialNB 41-class differential diagnosis)
   ├── 27. POST   /api/v1/predictions/feedback       (Active learning feedback queue ingestion)
   └── 28. POST   /api/v1/predictions/patient/me     (Unified multi-model assessment from stored records)
```

---

## 3. System Endpoints

### 3.1. Health Check
- **Method:** `GET`
- **URL:** `{{baseUrl}}/health`
- **Auth:** None
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "status": "healthy",
  "service": "medoracle-backend",
  "version": "0.1.0",
  "environment": "development"
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
pm.test("Service is healthy", () => {
    const json = pm.response.json();
    pm.expect(json.status).to.eql("healthy");
});
```

### 3.2. API V1 Root Check
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/`
- **Auth:** None
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "version": "v1",
  "status": "active",
  "description": "MedOracle API v1 root"
}
```

---

## 4. Authentication APIs (`/api/v1/auth`)

### 4.1. Register New Patient
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/auth/register`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "test.patient@medoracle.org",
  "password": "Password123!",
  "full_name": "Tariq Mahmood"
}
```
- **Expected Status:** `201 Created`
- **Response Example:**
```json
{
  "id": "e3b0c442-98fc-1c14-9afb-4c8996fb9242",
  "email": "test.patient@medoracle.org",
  "full_name": "Tariq Mahmood",
  "is_active": true,
  "created_at": "2026-10-19T14:30:00Z"
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
if (json.id) {
    pm.environment.set("userId", json.id);
}
```

### 4.2. Login Patient
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/auth/login`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "test.patient@medoracle.org",
  "password": "Password123!"
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```
- **Postman Tests Script (Auto-Saves Tokens):**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.access_token).to.not.be.empty;
pm.expect(json.refresh_token).to.not.be.empty;
pm.environment.set("accessToken", json.access_token);
pm.environment.set("refreshToken", json.refresh_token);
```

### 4.3. Get Current User Profile (`/me`)
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/auth/me`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "id": "e3b0c442-98fc-1c14-9afb-4c8996fb9242",
  "email": "test.patient@medoracle.org",
  "full_name": "Tariq Mahmood",
  "is_active": true,
  "created_at": "2026-10-19T14:30:00Z"
}
```

### 4.4. Refresh Access Token
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/auth/refresh`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "refresh_token": "{{refreshToken}}"
}
```
- **Expected Status:** `200 OK`
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.environment.set("accessToken", json.access_token);
pm.environment.set("refreshToken", json.refresh_token);
```

---

## 5. Patient Profile APIs (`/api/v1/patient`)

### 5.1. Get Biometric Profile
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/patient/profile`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`
- **Note:** If profile does not exist yet, the system auto-provisions a blank profile container for the user.

### 5.2. Update Biometric Profile
- **Method:** `PUT`
- **URL:** `{{baseUrl}}/api/v1/patient/profile`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "date_of_birth": "1975-06-15",
  "gender": "male",
  "height_cm": 176.5,
  "weight_kg": 84.0,
  "waist_circumference_cm": 96.0,
  "smoking_status": "current_smoker",
  "activity_level": "low",
  "blood_group": "B+"
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "id": "b47c945b-7b2f-4e08-9da4-984eb813eb98",
  "user_id": "e3b0c442-98fc-1c14-9afb-4c8996fb9242",
  "date_of_birth": "1975-06-15",
  "gender": "male",
  "height_cm": 176.5,
  "weight_kg": 84.0,
  "waist_circumference_cm": 96.0,
  "smoking_status": "current_smoker",
  "activity_level": "low",
  "blood_group": "B+",
  "created_at": "2026-10-19T14:35:00Z",
  "updated_at": "2026-10-19T14:35:00Z"
}
```

---

## 6. Medical History APIs (`/api/v1/medical-history`)

### 6.1. Get Medical History
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/medical-history/`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK` (or `404 Not Found` if no history has been submitted yet)

### 6.2. Create Medical History
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/medical-history/`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "chronic_conditions": ["hypertension", "dyslipidemia"],
  "past_surgeries": ["appendectomy"],
  "current_medications": [
    {
      "name": "Amlodipine",
      "dosage": "5mg",
      "frequency": "daily"
    },
    {
      "name": "Atorvastatin",
      "dosage": "20mg",
      "frequency": "nightly"
    }
  ],
  "allergies": ["penicillin"],
  "family_history": [
    {
      "relative": "father",
      "condition": "myocardial_infarction",
      "age_at_onset": 52
    },
    {
      "relative": "mother",
      "condition": "type_2_diabetes",
      "age_at_onset": 58
    }
  ],
  "notes": "Patient has strong paternal family history of premature CAD."
}
```
- **Expected Status:** `201 Created`
- **Postman Tests Script:**
```javascript
pm.test("Status code is 201", () => pm.response.to.have.status(201));
```

### 6.3. Update Medical History
- **Method:** `PUT`
- **URL:** `{{baseUrl}}/api/v1/medical-history/`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):** Partial or full update payload
- **Expected Status:** `200 OK`

---

## 7. Symptom Reporting APIs (`/api/v1/symptoms`)

### 7.1. Submit Symptom Report
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/symptoms/`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "reported_text": "Severe pressure and tightness across central chest radiating to the left jaw and shoulder during stairs climbing, lasting 10 minutes with mild breathlessness.",
  "duration_days": 4,
  "severity_self_rating": 8,
  "body_locations": ["chest", "left shoulder", "jaw"],
  "triggers": ["physical exertion", "climbing stairs"],
  "structured_symptoms": ["chest_pain", "angina", "dyspnea"]
}
```
- **Expected Status:** `201 Created`
- **Postman Tests Script:**
```javascript
pm.test("Status code is 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.expect(json.id).to.not.be.empty;
pm.environment.set("symptomReportId", json.id);
```

### 7.2. List Symptom Reports
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/symptoms/?limit=50`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`

### 7.3. Get Specific Symptom Report
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/symptoms/{{symptomReportId}}`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`

### 7.4. Delete Symptom Report
- **Method:** `DELETE`
- **URL:** `{{baseUrl}}/api/v1/symptoms/{{symptomReportId}}`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `204 No Content`

---

## 8. Laboratory Biomarker APIs (`/api/v1/laboratory`)

### 8.1. Record Laboratory Test Panel
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/laboratory/`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "test_date": "2026-10-18",
  "lab_name": "Chughtai Lab - Main Boulevard Branch",
  "biomarkers": {
    "systolic_bp": 142.0,
    "diastolic_bp": 92.0,
    "total_cholesterol_mg_dl": 235.0,
    "hdl_cholesterol_mg_dl": 38.0,
    "ldl_cholesterol_mg_dl": 154.0,
    "triglycerides_mg_dl": 215.0,
    "fasting_blood_glucose_mg_dl": 118.0,
    "hba1c_percent": 6.2,
    "serum_creatinine_mg_dl": 1.15
  },
  "notes": "12-hour fasting confirmed by technician."
}
```
- **Expected Status:** `201 Created`
- **Postman Tests Script:**
```javascript
pm.test("Status code is 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.expect(json.id).to.not.be.empty;
pm.environment.set("labResultId", json.id);
```

### 8.2. Get Latest Laboratory Report
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/laboratory/latest`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`

### 8.3. List Laboratory Reports
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/laboratory/?limit=50`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`

### 8.4. Get Specific Laboratory Report
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/laboratory/{{labResultId}}`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `200 OK`

### 8.5. Delete Laboratory Report
- **Method:** `DELETE`
- **URL:** `{{baseUrl}}/api/v1/laboratory/{{labResultId}}`
- **Headers:** `Authorization: Bearer {{accessToken}}`
- **Expected Status:** `204 No Content`

---

## 9. Clinical Risk Prediction APIs (`/api/v1/risk`)

All clinical risk endpoints require a valid Bearer JWT access token and return deterministic risk calculations grounded in published medical algorithms, complete with mandatory clinical decision-support disclaimers.

### 9.1. Framingham 10-Year Cardiovascular Disease Risk
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/risk/cardiovascular`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "age": 55,
  "gender": "male",
  "total_cholesterol_mg_dl": 220.0,
  "hdl_cholesterol_mg_dl": 42.0,
  "systolic_bp": 140.0,
  "is_treated_for_hypertension": true,
  "is_smoker": true,
  "has_diabetes": false
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model": "Framingham 10-Year General Cardiovascular Risk (D'Agostino 2008)",
  "risk_score_percent": 21.41,
  "risk_category": "high",
  "missing_or_assumed": [],
  "parameters": {
    "age": 55,
    "gender": "male",
    "total_cholesterol_mg_dl": 220.0,
    "hdl_cholesterol_mg_dl": 42.0,
    "systolic_bp": 140.0,
    "is_treated_for_hypertension": true,
    "is_smoker": true,
    "has_diabetes": false
  },
  "disclaimer": "MedOracle is a decision-support assistant and does not provide clinical diagnosis. Consult a qualified healthcare professional."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.risk_score_percent).to.be.a("number");
pm.expect(["low", "moderate", "high"]).to.include(json.risk_category);
pm.expect(json.disclaimer).to.include("MedOracle is a decision-support assistant");
```

---

### 9.2. FINDRISC Type 2 Diabetes 10-Year Risk
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/risk/diabetes`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "age": 52,
  "gender": "female",
  "bmi": 28.4,
  "waist_circumference_cm": 86.0,
  "daily_physical_activity_30min": false,
  "daily_vegetable_fruit_intake": true,
  "takes_antihypertensive_meds": true,
  "history_of_high_blood_glucose": false,
  "family_history_of_diabetes": "second_degree"
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model": "FINDRISC Type 2 Diabetes 10-Year Risk (Lindström 2003)",
  "total_score": 11,
  "max_score": 26,
  "risk_category": "slightly_elevated",
  "ten_year_risk_percent_approx": 4.0,
  "missing_or_assumed": [],
  "points_breakdown": {
    "age": 2,
    "bmi": 1,
    "waist_circumference": 3,
    "physical_activity": 2,
    "vegetables_fruit": 0,
    "hypertension_meds": 2,
    "high_blood_glucose_history": 0,
    "family_history": 3
  },
  "parameters": {
    "age": 52,
    "gender": "female",
    "bmi": 28.4,
    "waist_circumference_cm": 86.0,
    "physical_activity_30min_daily": false,
    "daily_fruit_veg_intake": true,
    "takes_hypertension_meds": true,
    "history_high_blood_glucose": false,
    "family_history_diabetes": "second_degree"
  },
  "disclaimer": "MedOracle is a decision-support assistant and does not provide clinical diagnosis. Consult a qualified healthcare professional."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.total_score).to.be.within(0, 26);
pm.expect(json.points_breakdown).to.be.an("object");
pm.expect(json.disclaimer).to.include("MedOracle is a decision-support assistant");
```

---

### 9.3. CKD-EPI 2021 Race-Free Kidney Function & eGFR
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/risk/kidney`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "serum_creatinine_mg_dl": 1.25,
  "age": 58,
  "gender": "male"
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model": "CKD-EPI 2021 Race-Free Creatinine eGFR (Inker 2021)",
  "egfr_ml_min_1_73m2": 66.4,
  "kdigo_stage": "G2",
  "stage_description": "Mildly decreased kidney function",
  "clinical_severity": "mild",
  "parameters": {
    "serum_creatinine_mg_dl": 1.25,
    "age": 58,
    "gender": "male"
  },
  "disclaimer": "MedOracle is a decision-support assistant and does not provide clinical diagnosis. Consult a qualified healthcare professional."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.egfr_ml_min_1_73m2).to.be.above(0);
pm.expect(["G1", "G2", "G3a", "G3b", "G4", "G5"]).to.include(json.kdigo_stage);
pm.expect(json.disclaimer).to.include("MedOracle is a decision-support assistant");
```

---

## 10. Real-Time Machine Learning Prediction APIs (`/api/v1/predictions`)

> **Authentication Required:** All endpoints in this section require an active Bearer JWT token.  
> If `{{accessToken}}` is empty or expired, run **Request 4.2: `POST /api/v1/auth/login`** first with:
> ```json
> {
>   "email": "test.patient@medoracle.org",
>   "password": "Password123!"
> }
> ```
> The login test script will automatically populate `{{accessToken}}`. All requests below must include the header:  
> `Authorization: Bearer {{accessToken}}`

---

### 10.1. Real-Time Cardiovascular Disease Risk Prediction
Predicts patient cardiovascular disease probability, binary risk classification, categorical risk tier, calibrated confidence score, and top contributing clinical factors using the champion GradientBoostingClassifier trained on the UCI Heart Disease benchmark.

- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/predictions/cardiovascular`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "age": 63,
  "sex": 1,
  "cp": 3,
  "trestbps": 145.0,
  "chol": 233.0,
  "fbs": 1,
  "restecg": 0,
  "thalach": 150.0,
  "exang": 0,
  "oldpeak": 2.3,
  "slope": 0,
  "ca": 0,
  "thal": 1
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model_id": "cardiovascular_risk_v1",
  "model_version": "1.0.0",
  "probability": 0.1737,
  "predicted_class": 0,
  "risk_tier": "low",
  "confidence_score": 82.63,
  "top_contributing_factors": [
    {
      "feature": "thalach",
      "value": 150.0,
      "importance": 0.1852,
      "impact_score": 0.0032
    },
    {
      "feature": "oldpeak",
      "value": 2.3,
      "importance": 0.1641,
      "impact_score": 0.1783
    },
    {
      "feature": "age",
      "value": 63.0,
      "importance": 0.1419,
      "impact_score": 0.1347
    },
    {
      "feature": "chol",
      "value": 233.0,
      "importance": 0.1205,
      "impact_score": 0.0319
    }
  ],
  "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.model_id).to.eql("cardiovascular_risk_v1");
pm.expect(json.probability).to.be.within(0.0, 1.0);
pm.expect([0, 1]).to.include(json.predicted_class);
pm.expect(["low", "moderate", "high"]).to.include(json.risk_tier);
pm.expect(json.confidence_score).to.be.within(50.0, 100.0);
pm.expect(json.top_contributing_factors).to.be.an("array");
pm.expect(json.disclaimer).to.include("clinical decision support");
```

---

### 10.2. Real-Time Type 2 Diabetes Risk Prediction
Predicts Type 2 diabetes risk probability, categorical risk tier, calibrated confidence, and influential metabolic biomarkers using the champion RandomForestClassifier trained on the PIMA Indians Diabetes benchmark. Automatically handles biological zero imputation for Glucose, BloodPressure, SkinThickness, Insulin, and BMI.

- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/predictions/diabetes`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "pregnancies": 6,
  "glucose": 148.0,
  "blood_pressure": 72.0,
  "skin_thickness": 35.0,
  "insulin": 0.0,
  "bmi": 33.6,
  "diabetes_pedigree": 0.627,
  "age": 50
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model_id": "diabetes_risk_v1",
  "model_version": "1.0.0",
  "probability": 0.6235,
  "predicted_class": 1,
  "risk_tier": "high",
  "confidence_score": 62.35,
  "top_contributing_factors": [
    {
      "feature": "Glucose",
      "value": 148.0,
      "importance": 0.3124,
      "impact_score": 0.2707
    },
    {
      "feature": "BMI",
      "value": 33.6,
      "importance": 0.2185,
      "impact_score": 0.0364
    },
    {
      "feature": "Age",
      "value": 50.0,
      "importance": 0.1542,
      "impact_score": 0.2198
    },
    {
      "feature": "DiabetesPedigreeFunction",
      "value": 0.627,
      "importance": 0.1106,
      "impact_score": 0.0518
    }
  ],
  "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.model_id).to.eql("diabetes_risk_v1");
pm.expect(json.probability).to.be.within(0.0, 1.0);
pm.expect([0, 1]).to.include(json.predicted_class);
pm.expect(["low", "moderate", "high"]).to.include(json.risk_tier);
pm.expect(json.confidence_score).to.be.within(50.0, 100.0);
pm.expect(json.top_contributing_factors).to.be.an("array");
pm.expect(json.disclaimer).to.include("clinical decision support");
```

---

### 10.3. Real-Time 41-Class Symptom Differential Diagnosis
Maps clinical symptom entities against the 132-symptom diagnostic matrix using the champion Multinomial Naive Bayes model. Returns top-k ranked differential diagnostic candidates, posterior probabilities, and tracks unrecognized symptom tokens.

- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/predictions/symptoms`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "symptoms": [
    "chills",
    "high_fever",
    "sweating",
    "headache",
    "nausea"
  ],
  "top_k": 5
}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "model_id": "symptoms_disease_v1",
  "model_version": "1.0.0",
  "top_candidates": [
    {
      "rank": 1,
      "disease": "Malaria",
      "probability": 0.9971,
      "confidence_score": 99.71
    },
    {
      "rank": 2,
      "disease": "Dengue",
      "probability": 0.0024,
      "confidence_score": 0.24
    },
    {
      "rank": 3,
      "disease": "Typhoid",
      "probability": 0.0003,
      "confidence_score": 0.03
    },
    {
      "rank": 4,
      "disease": "Jaundice",
      "probability": 0.0001,
      "confidence_score": 0.01
    },
    {
      "rank": 5,
      "disease": "Tuberculosis",
      "probability": 0.0001,
      "confidence_score": 0.01
    }
  ],
  "detected_symptoms": [
    "chills",
    "headache",
    "high_fever",
    "nausea",
    "sweating"
  ],
  "unrecognized_symptoms": [],
  "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.model_id).to.eql("symptoms_disease_v1");
pm.expect(json.top_candidates).to.be.an("array");
pm.expect(json.top_candidates.length).to.be.above(0);
pm.expect(json.top_candidates[0].rank).to.eql(1);
pm.expect(json.top_candidates[0].disease).to.be.a("string");
pm.expect(json.top_candidates[0].probability).to.be.within(0.0, 1.0);
pm.expect(json.detected_symptoms).to.include("chills");
```

---

### 10.4. Submit Clinician-Verified Diagnostic Feedback
Ingests clinician-verified ground truth into the active learning queue for continuous model retraining and drift mitigation.

- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/predictions/feedback`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "target_disease": "cardio",
  "features": {
    "age": 60,
    "sex": 1,
    "cp": 2,
    "trestbps": 140.0,
    "chol": 250.0,
    "fbs": 0,
    "restecg": 1,
    "thalach": 145.0,
    "exang": 1,
    "oldpeak": 1.5,
    "slope": 1,
    "ca": 1,
    "thal": 2
  },
  "ground_truth_label": 1,
  "confidence_at_prediction": 78.5,
  "notes": "Coronary angiography confirmed 75% LAD stenosis."
}
```
- **Expected Status:** `201 Created`
- **Response Example:**
```json
{
  "sample_id": "c7a8b9f0-1234-4567-89ab-cdef01234567",
  "target_disease": "cardio",
  "status": "recorded",
  "message": "Verified feedback queued successfully for cardio retraining queue."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.expect(json.sample_id).to.be.a("string");
pm.expect(json.target_disease).to.eql("cardio");
pm.expect(json.status).to.eql("recorded");
```

---

### 10.5. Generate Unified Multi-Model Assessment from Stored Patient Records
Ingests the authenticated patient's saved biometric profile, latest laboratory panel, and active reported symptoms directly from the database. Transforms clinical features, applies stored normalization scalers, runs all 3 ML models simultaneously, and returns a unified risk assessment and clinical summary.

- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/predictions/patient/me`
- **Headers:**  
  `Authorization: Bearer {{accessToken}}`  
  `Content-Type: application/json`
- **Body (raw JSON):**
```json
{}
```
- **Expected Status:** `200 OK`
- **Response Example:**
```json
{
  "user_id": "e3b0c442-98fc-1c14-9afb-4c8996fb9242",
  "patient_age": 51,
  "patient_gender": "male",
  "cardiovascular": {
    "model_id": "cardiovascular_risk_v1",
    "model_version": "1.0.0",
    "probability": 0.2245,
    "predicted_class": 0,
    "risk_tier": "moderate",
    "confidence_score": 77.55,
    "top_contributing_factors": [
      {
        "feature": "thalach",
        "value": 142.0,
        "importance": 0.1852,
        "impact_score": 0.0617
      },
      {
        "feature": "chol",
        "value": 245.0,
        "importance": 0.1205,
        "impact_score": 0.0418
      }
    ],
    "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
  },
  "diabetes": {
    "model_id": "diabetes_risk_v1",
    "model_version": "1.0.0",
    "probability": 0.6582,
    "predicted_class": 1,
    "risk_tier": "high",
    "confidence_score": 65.82,
    "top_contributing_factors": [
      {
        "feature": "Glucose",
        "value": 155.0,
        "importance": 0.3124,
        "impact_score": 0.3428
      },
      {
        "feature": "Age",
        "value": 51.0,
        "importance": 0.1542,
        "impact_score": 0.2327
      }
    ],
    "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
  },
  "differential_diagnosis": {
    "model_id": "symptoms_disease_v1",
    "model_version": "1.0.0",
    "top_candidates": [
      {
        "rank": 1,
        "disease": "Malaria",
        "probability": 0.9971,
        "confidence_score": 99.71
      },
      {
        "rank": 2,
        "disease": "Dengue",
        "probability": 0.0024,
        "confidence_score": 0.24
      }
    ],
    "detected_symptoms": [
      "chills",
      "headache",
      "high_fever",
      "nausea",
      "sweating"
    ],
    "unrecognized_symptoms": [],
    "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
  },
  "imputed_or_defaulted_parameters": [],
  "clinical_summary": "Patient is a 51-year-old male. Cardiovascular disease risk is evaluated at 22.5% (MODERATE risk tier, confidence 77.6%). Type 2 diabetes risk is evaluated at 65.8% (HIGH risk tier, confidence 65.8%). Primary differential diagnostic candidate from reported symptoms: Malaria (calibrated confidence 99.7%).",
  "disclaimer": "MedOracle machine learning risk predictions provide clinical decision support and do not constitute a definitive medical diagnosis. Consult a licensed physician or specialist for comprehensive clinical evaluation."
}
```
- **Postman Tests Script:**
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.user_id).to.be.a("string");
pm.expect(json.cardiovascular.probability).to.be.within(0.0, 1.0);
pm.expect(json.diabetes.probability).to.be.within(0.0, 1.0);
pm.expect(json.clinical_summary).to.be.a("string");
```

---

## 11. Future Endpoints Checklist

As subsequent roadmap steps are implemented, their specifications **must** be appended below:

- [x] **Step 5: Clinical Risk Models (`/api/v1/risk`)**
  - [x] `POST /api/v1/risk/cardiovascular` (Framingham 10-Yr CVD risk score)
  - [x] `POST /api/v1/risk/diabetes` (FINDRISC 10-Yr Type 2 diabetes score)
  - [x] `POST /api/v1/risk/kidney` (CKD-EPI 2021 eGFR & stage calculator)
- [x] **Step 8: ML Model Evaluation & Real-Time Inference (`/api/v1/predictions`)**
  - [x] `POST /api/v1/predictions/cardiovascular` (GradientBoosting 13-feature CVD risk)
  - [x] `POST /api/v1/predictions/diabetes` (RandomForest 8-feature metabolic T2D risk)
  - [x] `POST /api/v1/predictions/symptoms` (MultinomialNB 41-class differential diagnosis)
  - [x] `POST /api/v1/predictions/feedback` (Active learning feedback queue ingestion)
  - [x] `POST /api/v1/predictions/patient/me` (Unified multi-model assessment from stored records)
- [ ] **Step 14: Analysis Orchestration (`/api/v1/analysis`)**
  - [ ] `POST /api/v1/analysis/start` (Trigger async LangGraph multi-agent analysis)
  - [ ] `GET /api/v1/analysis/{session_id}/status` (Polling progress bar status)
  - [ ] `GET /api/v1/analysis/{session_id}/result` (Full multi-agent consensus results)
  - [ ] `GET /api/v1/analysis/{session_id}/debate` (Audit debate transcript)
  - [ ] `GET /api/v1/analysis/{session_id}/reasoning-graph` (GraphView node-edge payload)
- [ ] **Step 14: Doctor Recommendations (`/api/v1/doctors`)**
  - [ ] `GET /api/v1/doctors/recommendations` (Specialty referral matches)


