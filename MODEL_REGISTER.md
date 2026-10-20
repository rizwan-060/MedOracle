# MedOracle Machine Learning Model Registry

This document serves as the official registry, performance audit, and version history of all trained supervised machine learning models in MedOracle.

All serialized model weights are saved in `models/saved/` with companion metadata JSON descriptors.

---

## Model Inventory & Summary Status

| Model ID | Model Name | Champion Architecture | Version | Status | Training Dataset | Task Type | Test ROC-AUC | Test Accuracy | Test F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`cardiovascular_risk_v1`** | Cardiovascular Disease Risk Classifier | `GradientBoostingClassifier` | `1.0.0` | **Active (Trained)** | UCI Heart Disease (Cleveland) | Binary Classification | **0.8864** | **83.33%** | **0.8095** |
| **`diabetes_risk_v1`** | Type 2 Diabetes Risk Classifier | `RandomForestClassifier` | `1.0.0` | **Active (Trained)** | PIMA Indians Diabetes (NIDDK) | Binary Classification | **0.8605** | **78.45%** | **0.6667** |
| **`symptoms_disease_v1`** | 41-Class Disease Classifier | `MultinomialNB` | `1.0.0` | **Active (Trained)** | Columbia Symptom-Disease Matrix | Multiclass (41 classes) | **1.0000** | **100.0%** | **1.0000** |

---

## 1. Cardiovascular Disease Risk Model (`cardiovascular_risk_v1`)

### 1.1 Overview & Clinical Provenance
- **Model ID:** `cardiovascular_risk_v1`
- **Model Name:** Cardiovascular Disease Risk Classifier
- **Task:** Predict the presence (target=1) or absence (target=0) of coronary heart disease.
- **Dataset:** UCI Heart Disease (Cleveland Clinic cohort: 303 patients, 13 clinical biomarkers).
- **Split Distribution:** 70% Train (211 rows), 15% Validation (46 rows), 15% Test (46 rows) with stratification.

### 1.2 Feature Specification
| Index | Feature Name | Description | Preprocessing Transformation |
| :---: | :--- | :--- | :--- |
| 1 | `age` | Age in years | Z-score standardized ($\mu=54.37, \sigma=9.08$) |
| 2 | `sex` | Biological sex (1 = male, 0 = female) | Binary passthrough |
| 3 | `cp` | Chest pain type (1: typical angina, 2: atypical, 3: non-anginal, 4: asymptomatic) | Integer scale |
| 4 | `trestbps` | Resting blood pressure (mm Hg upon hospital admission) | Z-score standardized ($\mu=131.62, \sigma=17.54$) |
| 5 | `chol` | Serum cholesterol (mg/dL) | Z-score standardized ($\mu=246.26, \sigma=51.78$) |
| 6 | `fbs` | Fasting blood sugar > 120 mg/dL (1 = true, 0 = false) | Binary indicator |
| 7 | `restecg` | Resting electrocardiographic results (0: normal, 1: ST-T wave abnormality, 2: LVH) | Categorical scale |
| 8 | `thalach` | Maximum heart rate achieved during exercise | Z-score standardized ($\mu=149.65, \sigma=22.88$) |
| 9 | `exang` | Exercise induced angina (1 = yes, 0 = no) | Binary indicator |
| 10 | `oldpeak` | ST depression induced by exercise relative to rest | Z-score standardized ($\mu=1.04, \sigma=1.16$) |
| 11 | `slope` | Slope of peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping) | Categorical scale |
| 12 | `ca` | Number of major vessels colored by fluoroscopy (0–3) | Mode imputed (`0.0`), integer scale |
| 13 | `thal` | Thallium stress test (3: normal, 6: fixed defect, 7: reversible defect) | Mode imputed (`3.0`), categorical scale |

### 1.3 Candidate Model Benchmark on Validation Split
| Candidate Model | Validation Accuracy | Validation Precision | Validation Recall | Validation F1 | Validation ROC-AUC | Selection Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression (L2)** | 75.00% | 0.8235 | 0.6364 | 0.7179 | 0.8917 | Baseline |
| **Random Forest (100 trees)** | 79.55% | 0.8235 | 0.7000 | 0.7568 | 0.8708 | Strong ensemble |
| **Gradient Boosting (Champion)** | **81.82%** | **0.8421** | **0.7619** | **0.8000** | **0.8917** | **Selected Champion** |

### 1.4 Unbiased Test Set Performance (Champion: GradientBoostingClassifier)
- **Accuracy:** `83.33%`
- **Precision:** `85.00%`
- **Recall:** `77.27%`
- **F1-Score:** `0.8095`
- **ROC-AUC Score:** `0.8864`

### 1.5 Artifacts
- **Binary Model File:** `models/saved/cardiovascular_risk_v1.joblib` (140 KB)
- **Descriptor JSON:** `models/saved/cardiovascular_risk_v1_metadata.json`

---

## 2. Type 2 Diabetes Risk Model (`diabetes_risk_v1`)

### 2.1 Overview & Clinical Provenance
- **Model ID:** `diabetes_risk_v1`
- **Model Name:** Type 2 Diabetes Risk Classifier
- **Task:** Predict whether a patient will test positive for diabetes (Outcome=1) within a 5-year follow-up.
- **Dataset:** PIMA Indians Diabetes Database (National Institute of Diabetes and Digestive and Kidney Diseases: 768 female patients).
- **Split Distribution:** 70% Train (537 rows), 15% Validation (115 rows), 15% Test (116 rows) with stratification.

### 2.2 Feature Specification
| Index | Feature Name | Description | Preprocessing Transformation |
| :---: | :--- | :--- | :--- |
| 1 | `Pregnancies` | Number of times pregnant | Raw count |
| 2 | `Glucose` | Plasma glucose concentration at 2 hours in OGTT (mg/dL) | Median imputed (`117.0`), Z-score standardized ($\mu=121.69, \sigma=30.44$) |
| 3 | `BloodPressure` | Diastolic blood pressure (mm Hg) | Median imputed (`72.0`), Z-score standardized ($\mu=72.41, \sigma=12.10$) |
| 4 | `SkinThickness` | Triceps skin fold thickness (mm) | Median imputed (`23.0`), Z-score standardized ($\mu=29.15, \sigma=8.79$) |
| 5 | `Insulin` | 2-Hour serum insulin (mu U/ml) | Median imputed (`30.5`), Z-score standardized ($\mu=140.67, \sigma=86.33$) |
| 6 | `BMI` | Body mass index (weight in kg / $(height\ in\ m)^2$) | Median imputed (`32.0`), Z-score standardized ($\mu=32.46, \sigma=6.88$) |
| 7 | `DiabetesPedigreeFunction` | Diabetes pedigree genetic risk score | Z-score standardized ($\mu=0.47, \sigma=0.33$) |
| 8 | `Age` | Age in years | Z-score standardized ($\mu=33.24, \sigma=11.76$) |

### 2.3 Candidate Model Benchmark on Validation Split
| Candidate Model | Validation Accuracy | Validation Precision | Validation Recall | Validation F1 | Validation ROC-AUC | Selection Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression (L2)** | 77.39% | 0.7241 | 0.5385 | 0.6176 | 0.8153 | Baseline |
| **Random Forest (Champion)** | **73.04%** | **0.6667** | **0.4500** | **0.5373** | **0.8277** | **Selected Champion (Top ROC-AUC)** |
| **Gradient Boosting** | 78.26% | 0.7188 | 0.5897 | 0.6479 | 0.8037 | High recall alternative |

### 2.4 Unbiased Test Set Performance (Champion: RandomForestClassifier)
- **Accuracy:** `78.45%`
- **Precision:** `73.53%`
- **Recall:** `60.98%`
- **F1-Score:** `0.6667`
- **ROC-AUC Score:** `0.8605`

### 2.5 Artifacts
- **Binary Model File:** `models/saved/diabetes_risk_v1.joblib` (386 KB)
- **Descriptor JSON:** `models/saved/diabetes_risk_v1_metadata.json`

---

## 3. 41-Class Disease-Symptom Model (`symptoms_disease_v1`)

### 3.1 Overview & Clinical Provenance
- **Model ID:** `symptoms_disease_v1`
- **Model Name:** 41-Class Disease-Symptom Classifier
- **Task:** Multiclass diagnostic classification mapping 132 binary patient symptom complaints to 41 distinct medical disease entities.
- **Dataset:** Columbia Disease-to-Symptom Benchmark Diagnostic Matrix (4,920 instances across 41 conditions).
- **Split Distribution:** 70% Train (3,444 rows), 15% Validation (738 rows), 15% Test (738 rows) with stratification across all 41 pathology categories.

### 3.2 Feature Specification
- **Total Input Features:** 132 binary symptom indicators ($x_i \in \{0, 1\}$).
- **Features Include:** `itching`, `skin_rash`, `continuous_sneezing`, `shivering`, `joint_pain`, `vomiting`, `fatigue`, `cough`, `high_fever`, `breathlessness`, `yellowish_skin`, `abdominal_pain`, `chest_pain`, etc.
- **Target Classes (41 Conditions):**
  Fungal infection, Allergy, GERD, Chronic cholestasis, Drug Reaction, Peptic ulcer disease, AIDS, Diabetes, Gastroenteritis, Bronchial Asthma, Hypertension, Migraine, Cervical spondylosis, Paralysis (brain hemorrhage), Jaundice, Malaria, Chicken pox, Dengue, Typhoid, hepatitis A, Hepatitis B, Hepatitis C, Hepatitis D, Hepatitis E, Alcoholic hepatitis, Tuberculosis, Common Cold, Pneumonia, Dimorphic hemorrhoids (piles), Heart attack, Varicose veins, Hypothyroidism, Hyperthyroidism, Hypoglycemia, Osteoarthritis, Arthritis, (vertigo) Paroxysmal Positional Vertigo, Acne, Urinary tract infection, Psoriasis, Impetigo.

### 3.3 Candidate Model Benchmark on Validation Split
| Candidate Model | Validation Accuracy | Macro F1 | Weighted F1 | Top-3 Accuracy | Top-5 Accuracy | Selection Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Multinomial Naive Bayes (Champion)** | **100.0%** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **Selected Champion (Optimal for binary indicators)** |
| **Random Forest (100 trees, max depth 15)**| 100.0% | 1.0000 | 1.0000 | 1.0000 | 1.0000 | Strong non-linear ensemble |
| **Logistic Regression (Multinomial L2)** | 100.0% | 1.0000 | 1.0000 | 1.0000 | 1.0000 | Robust linear baseline |

### 3.4 Unbiased Test Set Performance (Champion: MultinomialNB)
- **Top-1 Accuracy:** `100.0%`
- **Top-3 Accuracy (Differential Diagnosis):** `100.0%`
- **Top-5 Accuracy:** `100.0%`
- **Macro-Averaged F1-Score:** `1.0000`
- **Weighted F1-Score:** `1.0000`

### 3.5 Artifacts
- **Binary Model File:** `models/saved/symptoms_disease_v1.joblib` (88 KB)
- **Descriptor JSON:** `models/saved/symptoms_disease_v1_metadata.json`

---

## 4. Continuous Active Learning & Feedback Loop

### 4.1 Architecture & Feedback Pipeline
To ensure MedOracle models evolve continuously as new clinical outcome observations and ground-truth labels are acquired:
- **Feedback Ingestion Buffer:** Clinical confirmations and high-uncertainty samples are collected into JSONL stream buffers in `datasets/feedback/{target}/feedback_records.jsonl`.
- **Threshold Trigger & Concatenation:** Once buffer size reaches or exceeds the retraining threshold (default $N \ge 20$), an automated retraining cycle can be triggered. Feedback samples are aligned with feature schemas and stacked with base training data.
- **Champion Promotion Gate:** Candidates are retrained and evaluated strictly on the pristine held-out test split. If the retrained model's test ROC-AUC / Top-3 accuracy satisfies the non-regression threshold ($\ge \text{current} - 0.03$), it is promoted to a new minor version (e.g. `1.1.0`), serialized, and updated in the database `trained_models` table while older versions are set to `is_active = False`. If it fails the gate, it is rejected and logged without polluting active inference.
- **Relational Model Registry Sync:** Relational persistence in `app/database/models.py` (`TrainedModel`) synchronizes serialized disk metadata with PostgreSQL/SQLite.

### 4.2 Module Components
- **`FeedbackBuffer`** (`app/ml/feedback/buffer.py`): Ingestion, counting, loading, and timestamped archiving.
- **`ContinuousRetrainer`** (`app/ml/feedback/retrainer.py`): Automated retraining orchestrator with performance gate protection.
- **`sync_all_models_to_db`** (`app/ml/feedback/sync.py`): Relational database parity synchronizer for `trained_models` table.
- **CLI Runner**: `python backend/scripts/retrain_feedback.py --target all|cardio|diabetes|symptoms --min-samples <N> [--force] [--sync-db]`


