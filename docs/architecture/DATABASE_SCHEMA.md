# MedOracle Database Schema Specification

**Document Version:** 1.0.0  
**Last Updated:** 2026-10-14  
**Target RDBMS:** PostgreSQL 15+ (Production / Supabase), SQLite 3.35+ (Testing Harness)  
**ORM:** SQLAlchemy 2.0 (Sync Engine via `psycopg` 3)  
**Migration Engine:** Alembic  

---

## 1. Schema Architecture Overview

MedOracle employs a normalized relational core with flexible document payloads (`JSON` column types) to accommodate multi-agent reasoning traces, clinical biomarker panels, dynamic debate transcripts, and counterfactual simulation scenarios.

### Core Design Principles
1. **Cryptographic Identification**: All primary keys are RFC 4122 v4 UUID strings (`String(36)`), eliminating incremental identifier enumeration attacks.
2. **Temporal Traceability**: Every table enforces timezone-aware UTC timestamps (`created_at`, `updated_at`).
3. **Tenant Boundary Isolation**: All personal health records (biometrics, symptoms, medical history, lab results, risk scores, analysis sessions) are bound to `user_id` with foreign key indexes and cascading deletion.
4. **Dialect Portability**: Dynamic payloads use SQLAlchemy's generic `JSON` type, guaranteeing seamless local testing on SQLite and native `JSONB` performance in production PostgreSQL.

---

## 2. Complete Table Inventory

| # | Table Name | Domain | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `users` | Identity & Auth | `id` (UUID) | User accounts, credentials, and account activation states. |
| 2 | `patient_profiles` | Demographics & Biometrics | `id` (UUID) | Height, weight, waist circumference, smoking status, and baseline health. |
| 3 | `medical_histories` | Longitudinal Records | `id` (UUID) | Chronic conditions, surgical history, active medications, and family hereditary risk. |
| 4 | `symptom_reports` | Clinical Intake | `id` (UUID) | Patient-reported natural language symptoms, perceived severity, and contextual triggers. |
| 5 | `lab_results` | Diagnostic Biomarkers | `id` (UUID) | Metabolic panel values, lipid profiles, renal function markers, and panel dates. |
| 6 | `analysis_sessions` | Multi-Agent Orchestration | `id` (UUID) | Lifecycle of multi-agent debate, progress tracking, consensus verdict, and trajectories. |
| 7 | `agent_outputs` | Agent Traceability | `id` (UUID) | Structured findings, confidence scores, reasoning chains, and challenges per agent. |
| 8 | `risk_results` | Quantitative Stratification | `id` (UUID) | Quantified risk outputs from clinical equations (Framingham, FINDRISC, CKD-EPI) and ML. |
| 9 | `doctors` | Clinical Referral Directory | `id` (UUID) | Registered specialists, clinics, hospital affiliations, geographic coordinates, and ratings. |
| 10 | `trained_models` | ML Model Registry | `id` (UUID) | Catalog of serialized machine learning models, training datasets, performance metrics, and paths. |

---

## 3. Entity-Relationship (ER) Mapping

| Parent Table | Child Table | Foreign Key Column | Parent Ref Column | Cardinality | On Delete Action | Relationship Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `users` | `patient_profiles` | `user_id` | `id` | 1 : 1 | `CASCADE` | User's demographic and physical profile. |
| `users` | `medical_histories` | `user_id` | `id` | 1 : N | `CASCADE` | User's historical medical and family conditions. |
| `users` | `symptom_reports` | `user_id` | `id` | 1 : N | `CASCADE` | User's self-reported symptom intake records. |
| `users` | `lab_results` | `user_id` | `id` | 1 : N | `CASCADE` | User's diagnostic laboratory panels. |
| `users` | `analysis_sessions` | `user_id` | `id` | 1 : N | `CASCADE` | User's multi-agent analysis sessions. |
| `users` | `risk_results` | `user_id` | `id` | 1 : N | `CASCADE` | User's direct clinical and ML risk records. |
| `symptom_reports` | `analysis_sessions` | `symptom_report_id` | `id` | 1 : N | `SET NULL` | Associates an analysis session with the triggering symptom report. |
| `analysis_sessions` | `agent_outputs` | `analysis_session_id` | `id` | 1 : N | `CASCADE` | Individual agent contributions within a session. |
| `analysis_sessions` | `risk_results` | `analysis_session_id` | `id` | 1 : N | `SET NULL` | Calculated risk scores produced during a session. |

---

## 4. Table Specifications and Concrete Example Data

### 4.1. Table: `users`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Unique user identifier. |
| `email` | `VARCHAR(255)` | No | None | Unique, Index (`ix_users_email`) | User email address for login. |
| `hashed_password` | `VARCHAR(255)` | No | None | None | Bcrypt hashed password string. |
| `full_name` | `VARCHAR(255)` | No | None | None | Full legal or preferred name. |
| `is_active` | `BOOLEAN` | No | `TRUE` | None | Account operational status. |
| `is_verified` | `BOOLEAN` | No | `FALSE` | None | Email verification status. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Account creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | email | hashed_password | full_name | is_active | is_verified | created_at | updated_at |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `ahmed.khan@example.com` | `$2b$12$K8y4nU...` | `Ahmed Khan` | `true` | `true` | `2026-10-14 08:30:00+00` | `2026-10-14 08:30:00+00` |
| `b2c3d4e5-f6a1-4b2c-9d3e-222222222222` | `fatima.noor@example.com` | `$2b$12$P9z5mV...` | `Fatima Noor` | `true` | `true` | `2026-10-14 09:15:00+00` | `2026-10-14 09:15:00+00` |

---

### 4.2. Table: `patient_profiles`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Profile identifier. |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Unique, Index | User owning this profile (1:1). |
| `date_of_birth` | `DATE` | Yes | None | None | Patient date of birth. |
| `gender` | `VARCHAR(20)` | Yes | None | `male`, `female`, `other` | Biological sex / gender. |
| `height_cm` | `FLOAT` | Yes | None | None | Standing height in centimeters. |
| `weight_kg` | `FLOAT` | Yes | None | None | Body weight in kilograms. |
| `waist_circumference_cm`| `FLOAT` | Yes | None | None | Waist circumference in centimeters. |
| `smoking_status` | `VARCHAR(30)` | Yes | None | `never`, `former`, `current_smoker` | Tobacco smoking history. |
| `activity_level` | `VARCHAR(30)` | Yes | None | `sedentary`, `low`, `moderate`, `high` | Habitual physical activity. |
| `blood_group` | `VARCHAR(10)` | Yes | None | `A+`, `B+`, `O-`, etc. | ABO/Rh blood classification. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | user_id | date_of_birth | gender | height_cm | weight_kg | waist_circumference_cm | smoking_status | activity_level | blood_group |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `11111111-2222-3333-4444-555555555555` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `1972-04-18` | `male` | `175.0` | `86.5` | `98.0` | `current_smoker` | `low` | `B+` |
| `22222222-3333-4444-5555-666666666666` | `b2c3d4e5-f6a1-4b2c-9d3e-222222222222` | `1985-11-25` | `female` | `162.0` | `68.0` | `82.0` | `never` | `moderate` | `O+` |

---

### 4.3. Table: `medical_histories`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Record identifier. |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Index | User owning this history. |
| `chronic_conditions` | `JSON` | No | `[]` | None | List of diagnosed long-term conditions. |
| `past_surgeries` | `JSON` | No | `[]` | None | List of surgical procedures. |
| `current_medications` | `JSON` | No | `[]` | None | List of active medication objects. |
| `allergies` | `JSON` | No | `[]` | None | List of documented adverse drug/food reactions. |
| `family_history` | `JSON` | No | `[]` | None | Structured hereditary disease history. |
| `notes` | `TEXT` | Yes | None | None | Clinician / patient contextual notes. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Record timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | user_id | chronic_conditions | current_medications | family_history | notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `33333333-4444-5555-6666-777777777777` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `["hypertension", "dyslipidemia"]` | `[{"name": "Amlodipine", "dosage": "5mg", "freq": "once_daily"}]` | `[{"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 52}]` | `Patient complies with antihypertensive therapy.` |
| `44444444-5555-6666-7777-888888888888` | `b2c3d4e5-f6a1-4b2c-9d3e-222222222222` | `["gestational_diabetes_history"]` | `[]` | `[{"relative": "mother", "condition": "type_2_diabetes", "age_at_onset": 58}]` | `Annual screening recommended.` |

---

### 4.4. Table: `symptom_reports`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Symptom report identifier. |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Index | User reporting symptoms. |
| `reported_text` | `TEXT` | No | None | None | Raw patient narrative description. |
| `duration_days` | `INTEGER` | Yes | None | None | Duration in elapsed days. |
| `severity_self_rating` | `INTEGER` | Yes | None | 1 to 10 | Subjective rating on 1-10 pain/discomfort scale. |
| `body_locations` | `JSON` | No | `[]` | None | Anatomical locations involved. |
| `triggers` | `JSON` | No | `[]` | None | Aggravating triggers reported. |
| `structured_symptoms`| `JSON` | No | `[]` | None | Standardized symptoms extracted. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Submission timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | user_id | reported_text | duration_days | severity_self_rating | body_locations | triggers | structured_symptoms |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `55555555-6666-7777-8888-999999999999` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `Tight squeezing chest sensation radiating to left shoulder and jaw during morning brisk walking.` | `4` | `8` | `["chest", "left_shoulder", "jaw"]` | `["brisk_walking", "cold_air"]` | `["chest_tightness", "radiating_pain", "exertional_dyspnea"]` |
| `66666666-7777-8888-9999-000000000000` | `b2c3d4e5-f6a1-4b2c-9d3e-222222222222` | `Unusual fatigue, increased thirst, and frequent nighttime urination over past month.` | `30` | `5` | `["systemic"]` | `["none"]` | `["polydipsia", "polyuria", "fatigue"]` |

---

### 4.5. Table: `lab_results`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Lab record identifier. |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Index | User owning test panel. |
| `test_date` | `DATE` | No | None | None | Specimen collection date. |
| `lab_name` | `VARCHAR(255)` | Yes | None | None | Diagnostic center / hospital laboratory name. |
| `biomarkers` | `JSON` | No | None | None | Key-value panel of clinical biomarker values. |
| `notes` | `TEXT` | Yes | None | None | Pathologist remarks. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Entry creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | user_id | test_date | lab_name | biomarkers (JSON payload) | notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `77777777-8888-9999-0000-111111111111` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `2026-10-10` | `Chughtai Lab, Lahore` | `{"systolic_bp": 146, "diastolic_bp": 92, "total_cholesterol_mg_dl": 242, "hdl_cholesterol_mg_dl": 37, "ldl_cholesterol_mg_dl": 164, "fasting_blood_glucose_mg_dl": 118, "serum_creatinine_mg_dl": 1.12, "hba1c_percent": 6.2}` | `Lipid panel indicates atherogenic dyslipidemia.` |
| `88888888-9999-0000-1111-222222222222` | `b2c3d4e5-f6a1-4b2c-9d3e-222222222222` | `2026-10-08` | `Shaukat Khanum Diagnostics` | `{"systolic_bp": 122, "diastolic_bp": 78, "total_cholesterol_mg_dl": 185, "hdl_cholesterol_mg_dl": 52, "fasting_blood_glucose_mg_dl": 134, "serum_creatinine_mg_dl": 0.85, "hba1c_percent": 6.9}` | `Fasting glucose and HbA1c suggest impaired glycemic control.` |

---

### 4.6. Table: `analysis_sessions`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Analysis session identifier. |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Index | User initiating analysis. |
| `symptom_report_id` | `VARCHAR(36)` | Yes | None | FK (`symptom_reports.id`), Index | Linked symptom report. |
| `status` | `VARCHAR(30)` | No | `pending` | Index (`ix_analysis_sessions_status`) | `pending`, `running`, `completed`, `failed`. |
| `current_phase` | `VARCHAR(50)` | No | `queued` | None | Pipeline execution stage. |
| `progress_percent` | `INTEGER` | No | `0` | None | 0 to 100 client progress value. |
| `consensus_verdict` | `JSON` | Yes | None | None | Multi-agent consensus summary object. |
| `debate_summary` | `JSON` | Yes | None | None | Contradictions and resolution record. |
| `disease_trajectory`| `JSON` | Yes | None | None | 30-day, 6-month, 1-year forecasted risks. |
| `counterfactuals` | `JSON` | Yes | None | None | Quantified lifestyle intervention deltas. |
| `reasoning_graph` | `JSON` | Yes | None | None | Nodes and edges payload for Flutter `graphview`. |
| `recommended_specialty` | `VARCHAR(100)` | Yes | None | None | Matched medical discipline (e.g. Cardiology). |
| `error_message` | `TEXT` | Yes | None | None | Error trace if failed. |
| `completed_at` | `TIMESTAMP WITH TZ`| Yes | None | None | Execution completion timestamp. |
| `created_at` | `TIMESTAMP WITH TZ`| No | UTC Now | None | Session initiation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ`| No | UTC Now | None | Last state transition timestamp. |

#### Example Data
| id | user_id | status | current_phase | progress_percent | consensus_verdict (JSON snippet) | recommended_specialty | completed_at |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `99999999-0000-1111-2222-333333333333` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `completed` | `completed` | `100` | `{"primary_risk_category": "Coronary Artery Disease Risk", "overall_urgency": "high", "consensus_confidence": 88.5, "summary": "Exertional angina supported by dyslipidemia and hereditary premature CAD history."}` | `Cardiology` | `2026-10-14 09:35:12+00` |

---

### 4.7. Table: `agent_outputs`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Agent output record identifier. |
| `analysis_session_id` | `VARCHAR(36)` | No | None | FK (`analysis_sessions.id`), Index | Parent session identifier. |
| `agent_role` | `VARCHAR(50)` | No | None | Index (`ix_agent_outputs_agent_role`) | Role: `symptom_agent`, `laboratory_agent`, etc. |
| `findings` | `TEXT` | No | None | None | Structured findings narrative. |
| `confidence` | `FLOAT` | No | None | 0.0 to 100.0 | Quantified agent confidence percentage. |
| `reasoning_chain` | `JSON` | No | `[]` | None | Step-by-step logical inferences. |
| `evidence` | `JSON` | No | `[]` | None | Grounded empirical data points used. |
| `challenges` | `JSON` | No | `[]` | None | Formal challenges raised against other agents. |
| `metadata_payload` | `JSON` | No | `{}` | None | Token counts, latency, model ID metadata. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Output creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | analysis_session_id | agent_role | findings | confidence | reasoning_chain | evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `aaaa1111-bbbb-2222-cccc-333333333333` | `99999999-0000-1111-2222-333333333333` | `symptom_agent` | `Symptom profile indicates probable exertional angina pectoris.` | `86.0` | `["Exertional tightness triggered by brisk walking", "Radiation to jaw and shoulder", "Short relief duration with rest"]` | `["Severity rating 8/10", "Duration 4 days"]` |
| `bbbb2222-cccc-3333-dddd-444444444444` | `99999999-0000-1111-2222-333333333333` | `medical_history_agent` | `Significant hereditary risk multiplier from first-degree premature CAD.` | `91.0` | `["Paternal myocardial infarction at age 52 (< 55 threshold)", "Active tobacco smoking adds compounding endothelial injury"]` | `["Father MI at age 52", "Current smoker status"]` |

---

### 4.8. Table: `risk_results`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Risk calculation identifier. |
| `analysis_session_id` | `VARCHAR(36)` | Yes | None | FK (`analysis_sessions.id`), Index | Associated session (if orchestrated). |
| `user_id` | `VARCHAR(36)` | No | None | FK (`users.id`), Index | User owning risk evaluation. |
| `model_name` | `VARCHAR(100)` | No | None | None | E.g. `Framingham 10-Year General CVD`. |
| `model_type` | `VARCHAR(30)` | No | None | None | `clinical_formula`, `machine_learning`, `ensemble`. |
| `risk_score` | `FLOAT` | No | None | None | Numerical percentage score (e.g. 22.4). |
| `risk_category` | `VARCHAR(50)` | No | None | None | `low`, `moderate`, `high`, `very_high`. |
| `horizon` | `VARCHAR(30)` | Yes | None | None | Projection timeframe: `10_year`, `1_year`, etc. |
| `input_parameters` | `JSON` | No | None | None | Parameter values supplied to model. |
| `missing_or_assumed` | `JSON` | No | `[]` | None | Imputed or assumed variables documented. |
| `disclaimer` | `TEXT` | No | None | None | Non-diagnostic legal medical disclaimer. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Calculation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | user_id | model_name | model_type | risk_score | risk_category | horizon | input_parameters | disclaimer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cccc3333-dddd-4444-eeee-555555555555` | `a1b2c3d4-e5f6-4a1b-8c2d-111111111111` | `Framingham 10-Year General CVD` | `clinical_formula` | `23.8` | `high` | `10_year` | `{"age": 54, "total_chol": 242, "hdl": 37, "sbp": 146, "treated_bp": true, "smoker": true}` | `MedOracle decision support only; does not provide diagnosis.` |

---

### 4.9. Table: `doctors`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Doctor identifier. |
| `name` | `VARCHAR(255)` | No | None | None | Professional title and name. |
| `specialty` | `VARCHAR(100)` | No | None | Index (`ix_doctors_specialty`) | Clinical discipline (e.g. `Cardiology`). |
| `sub_specialty` | `VARCHAR(100)` | Yes | None | None | Sub-specialization area. |
| `hospital_clinic` | `VARCHAR(255)` | No | None | None | Hospital or clinical practice name. |
| `city` | `VARCHAR(100)` | No | None | Index (`ix_doctors_city`) | City of practice (e.g. Lahore, Karachi). |
| `area` | `VARCHAR(150)` | No | None | None | Neighborhood or district area. |
| `address` | `TEXT` | Yes | None | None | Complete street address. |
| `contact_phone` | `VARCHAR(50)` | Yes | None | None | Clinic appointment telephone number. |
| `contact_email` | `VARCHAR(100)` | Yes | None | None | Professional email address. |
| `latitude` | `FLOAT` | Yes | None | None | WGS84 GPS latitude for proximity sorting. |
| `longitude` | `FLOAT` | Yes | None | None | WGS84 GPS longitude for proximity sorting. |
| `rating` | `FLOAT` | No | `5.0` | 0.0 to 5.0 | Average patient satisfaction rating. |
| `is_available` | `BOOLEAN` | No | `TRUE` | None | Active consultation availability flag. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Record creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | name | specialty | hospital_clinic | city | area | contact_phone | rating | is_available |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dddd4444-eeee-5555-ffff-666666666666` | `Dr. Sarah Khan, FCPS` | `Cardiology` | `Punjab Institute of Cardiology` | `Lahore` | `Jail Road` | `+92-42-99203051` | `4.9` | `true` |
| `eeee5555-ffff-6666-aaaa-777777777777` | `Dr. Tariq Mahmood, MRCP` | `Endocrinology` | `Shaukat Khanum Memorial Hospital` | `Lahore` | `Johar Town` | `+92-42-35905000` | `4.85` | `true` |

---

### 4.10. Table: `trained_models`

#### Column Specifications
| Column Name | Data Type | Nullable | Default | Constraints / Indexes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | UUID v4 | Primary Key | Registered model identifier. |
| `name` | `VARCHAR(100)` | No | None | Index (`ix_trained_models_name`) | Model identifier name. |
| `version` | `VARCHAR(30)` | No | None | None | Semantic version string (e.g. `v1.0.0`). |
| `target_disease` | `VARCHAR(100)` | No | None | None | Target condition predicted. |
| `algorithm` | `VARCHAR(100)` | No | None | None | Classifier algorithm utilized. |
| `dataset_source` | `VARCHAR(100)` | No | None | None | Training data benchmark source. |
| `artifact_path` | `VARCHAR(255)` | No | None | None | Relative file system path to serialized joblib/pickle. |
| `metrics` | `JSON` | No | None | None | Benchmark performance evaluation metrics. |
| `feature_names` | `JSON` | No | None | None | Ordered list of expected input feature names. |
| `is_active` | `BOOLEAN` | No | `TRUE` | None | Serving status flag. |
| `created_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Registration timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ` | No | UTC Now | None | Last update timestamp. |

#### Example Data
| id | name | version | target_disease | algorithm | dataset_source | metrics (JSON payload) | artifact_path | is_active |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ffff6666-aaaa-7777-bbbb-888888888888` | `cardiovascular_rf_classifier` | `v1.0.0` | `Cardiovascular Disease` | `RandomForestClassifier` | `UCI Heart Disease` | `{"roc_auc": 0.884, "f1_score": 0.821, "accuracy": 0.845, "precision": 0.835, "recall": 0.808}` | `backend/app/ml/models/cardio_rf_v1.joblib` | `true` |
| `00007777-bbbb-8888-cccc-999999999999` | `diabetes_lightgbm_classifier` | `v1.0.0` | `Type 2 Diabetes` | `LGBMClassifier` | `PIMA Indians Diabetes` | `{"roc_auc": 0.852, "f1_score": 0.774, "accuracy": 0.812, "precision": 0.791, "recall": 0.758}` | `backend/app/ml/models/diabetes_lgbm_v1.joblib` | `true` |

---

## 5. Security & Data Protection Guarantees

1. **Password Protection**:
   - `hashed_password` in `users` stores cryptographically strong bcrypt hashes with a work factor $\ge 12$. Plaintext passwords never enter the persistence layer.
2. **Preventing ID Enumeration**:
   - Every entity generates a v4 UUID at instantiation. Sequential enumeration attacks are impossible.
3. **Strict Multi-Tenant Isolation**:
   - In `repositories.py`, queries for sensitive clinical assets (`symptom_reports`, `lab_results`, `medical_histories`, `analysis_sessions`) enforce `where(user_id == current_user.id)` scoping.
4. **SQL Injection Immunity**:
   - All queries are executed using SQLAlchemy 2.0 object-relational mapping and parameterized expression trees. Raw SQL string concatenation is forbidden.
5. **No Secret Infiltration**:
   - Database connection strings and credentials reside strictly in `backend/.env` (git-ignored) with dummy representations in `.env.example`.
