# MedOracle Machine Learning Dataset Register

> **Status:** Acquired & Verified (Sub-Step 6.1)  
> **Storage Root:** `datasets/raw/`  
> **Downstream Pipelines:** Preprocessing & Scaling (`app/ml/preprocessing/`), Model Training (`backend/scripts/train_models.py`)

---

## 1. Executive Summary & Dataset Inventory

To provide quantitative machine learning forecasting alongside MedOracle's deterministic clinical formulas (Framingham, FINDRISC, CKD-EPI), three benchmark clinical datasets have been ingested and verified:

| Dataset ID | Canonical Name | Clinical Domain | Instances | Features | Target Column | Source |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `DS-CVD-01` | **UCI Heart Disease (Cleveland)** | Cardiovascular Disease | 303 | 13 + 1 target | `target` (0 = No, 1 = Yes) | UCI Machine Learning Repository (Cleveland Clinic Foundation) |
| `DS-DIA-01` | **PIMA Indians Diabetes** | Type 2 Diabetes | 768 | 8 + 1 target | `Outcome` (0 = No, 1 = Yes) | National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) |
| `DS-SYM-01` | **Disease-to-Symptom Matrix** | Multi-Pathology Diagnostic Mapping | 4,920 | 132 + 1 target | `prognosis` (41 disease classes) | Columbia University / Kaggle Benchmark Diagnostic Corpus |

---

## 2. Dataset `DS-CVD-01`: UCI Heart Disease (Cleveland)

- **File Path:** `datasets/raw/heart_disease_uci.csv`
- **Origin:** Cleveland Clinic Foundation (Dr. Robert Detrano)
- **Primary Source:** [UCI Machine Learning Repository: Heart Disease](https://archive.ics.uci.edu/ml/datasets/heart+disease)
- **Citation:**
  > Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, J., Sandhu, S., Guppy, K., Lee, S., & Froelicher, V. (1989). *International application of a new probability algorithm for the diagnosis of coronary artery disease.* The American Journal of Cardiology, 64(5), 304–310.

### Variable Dictionary

| Column | Type | Permissible Range / Values | Clinical Description | Imputation / Preprocessing Rule |
| :--- | :--- | :--- | :--- | :--- |
| `age` | Integer | 29 – 77 years | Age of patient in years | None (no missing values) |
| `sex` | Binary | `1` = Male; `0` = Female | Biological sex | None |
| `cp` | Categorical | `1`: Typical angina<br>`2`: Atypical angina<br>`3`: Non-anginal pain<br>`4`: Asymptomatic | Chest pain type reported by patient | One-Hot / Categorical encoding |
| `trestbps` | Continuous | 94 – 200 mmHg | Resting systolic blood pressure on hospital admission | Robust scaling |
| `chol` | Continuous | 126 – 564 mg/dL | Serum cholesterol in mg/dL | StandardScaler |
| `fbs` | Binary | `1`: FBS > 120 mg/dL<br>`0`: FBS ≤ 120 mg/dL | Fasting blood sugar elevation indicator | Binary passthrough |
| `restecg` | Categorical | `0`: Normal<br>`1`: ST-T wave abnormality<br>`2`: Left ventricular hypertrophy (Estes' criteria) | Resting electrocardiogram findings | One-Hot encoding |
| `thalach` | Continuous | 71 – 202 bpm | Maximum heart rate achieved during exercise | StandardScaler |
| `exang` | Binary | `1`: Yes; `0`: No | Exercise-induced angina | Binary passthrough |
| `oldpeak` | Continuous | 0.0 – 6.2 mm | ST depression induced by exercise relative to rest | Robust scaling |
| `slope` | Categorical | `1`: Upsloping<br>`2`: Flat<br>`3`: Downsloping | Slope of the peak exercise ST segment | One-Hot encoding |
| `ca` | Discrete | 0, 1, 2, 3 major vessels | Number of major coronary vessels colored by fluoroscopy | 4 records contain missing values (`?`): mode imputation (0) |
| `thal` | Categorical | `3`: Normal<br>`6`: Fixed defect<br>`7`: Reversible defect | Thallium-201 scintigraphy myocardial perfusion | 2 records contain missing values (`?`): mode imputation (3) |
| `target` | Integer / Binary | Original: `0` (absence) to `1, 2, 3, 4` (presence of CAD) | Angiographic disease status (>50% coronary stenosis) | Binarized: `0` = healthy ($N=164$), `1` = coronary artery disease ($N=139$) |

---

## 3. Dataset `DS-DIA-01`: PIMA Indians Diabetes Database

- **File Path:** `datasets/raw/diabetes_pima.csv`
- **Origin:** National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)
- **Primary Source:** [NIDDK PIMA Indians Diabetes Dataset](https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv)
- **Citation:**
  > Smith, J.W., Everhart, J.E., Dickson, W.C., Knowler, W.C., & Johannes, R.S. (1988). *Using the ADAP learning algorithm to forecast the onset of diabetes mellitus.* In Proceedings of the Symposium on Computer Applications and Medical Care (pp. 261–265). IEEE Computer Society Press.

### Variable Dictionary

| Column | Type | Biological Units | Clinical Meaning | Physiologically Impossible Zeroes & Imputation Rule |
| :--- | :--- | :--- | :--- | :--- |
| `Pregnancies` | Integer | Count | Number of pregnancies | `0` is biologically valid (nulliparous women). No imputation. |
| `Glucose` | Continuous | mg/dL | 2-hour plasma glucose concentration in an oral GTT | `0` is physiologically fatal ($N=5$). Impute with median (117 mg/dL). |
| `BloodPressure`| Continuous | mmHg | Diastolic blood pressure | `0` is physiologically impossible ($N=35$). Impute with median (72 mmHg). |
| `SkinThickness`| Continuous | mm | Triceps skin fold thickness | `0` indicates missing sensor read ($N=227$). Impute with median (23 mm). |
| `Insulin` | Continuous | $\mu\text{U/mL}$ | 2-hour serum insulin level | `0` indicates missing test ($N=374$). Impute with median (30.5 $\mu\text{U/mL}$). |
| `BMI` | Continuous | $\text{kg/m}^2$ | Body mass index | `0` is physiologically impossible ($N=11$). Impute with median (32.0 $\text{kg/m}^2$). |
| `DiabetesPedigreeFunction` | Continuous | Score | Genetic diabetes risk scoring function | Complete data (0.078 to 2.42). Log transformation applied. |
| `Age` | Integer | Years | Patient age (range 21 – 81) | Complete data. |
| `Outcome` | Binary | 0 or 1 | Class variable: `1` = Diabetic ($N=268$), `0` = Non-diabetic ($N=500$) | Target outcome. |

---

## 4. Dataset `DS-SYM-01`: Disease-to-Symptom Benchmark Matrix

- **File Path:** `datasets/raw/symptoms_disease.csv`
- **Origin:** Columbia University Medical Diagnostic Corpus / Kaggle Healthcare Repository
- **Instances:** 4,920 clinical presentations across 41 distinct acute and chronic pathologies (120 balanced presentations per condition).
- **Features:** 132 binary symptom indicators + 1 target column (`prognosis`).

### Pathologies Covered (41 Disease Targets)
```text
1. Fungal infection
2. Allergy
3. GERD (Gastroesophageal Reflux)
4. Chronic cholestasis
5. Drug Reaction
6. Peptic ulcer disease
7. AIDS
8. Diabetes
9. Gastroenteritis
10. Bronchial Asthma
11. Hypertension
12. Migraine
13. Cervical spondylosis
14. Paralysis (brain hemorrhage)
15. Jaundice
16. Malaria
17. Chicken pox
18. Dengue
19. Typhoid
20. Hepatitis A
21. Hepatitis B
22. Hepatitis C
23. Hepatitis D
24. Hepatitis E
25. Alcoholic hepatitis
26. Tuberculosis
27. Common Cold
28. Pneumonia
29. Dimorphic hemorrhoids (piles)
30. Heart attack (Myocardial infarction)
31. Varicose veins
32. Hypothyroidism
33. Hyperthyroidism
34. Hypoglycemia
35. Osteoarthritis
36. Arthritis
37. (vertigo) Paroxysmal Positional Vertigo
38. Acne
39. Urinary tract infection
40. Psoriasis
41. Impetigo
```

### Feature Architecture
- **Binary Matrix:** Each feature represents the presence (`1`) or absence (`0`) of a specific symptom reported by the patient (e.g. `chest_pain`, `breathlessness`, `sweating`, `high_fever`, `joint_pain`).
- **Clinical Relevance:** Maps directly into the **Symptom Analysis Agent** (Step 10) to compute preliminary disease differential distributions.

---

## 5. Downstream Integration Workflow

```
[Raw Ingestion (Step 6.1)]
   ├── datasets/raw/heart_disease_uci.csv  (303 rows)
   ├── datasets/raw/diabetes_pima.csv      (768 rows)
   └── datasets/raw/symptoms_disease.csv   (4,920 rows)
        │
[Preprocessing Pipelines (Step 6.2)]
   ├── app/ml/preprocessing/heart.py       (ca/thal imputation, One-Hot cp/slope, 70/15/15 split)
   ├── app/ml/preprocessing/diabetes.py    (0-value median imputation, RobustScaler, 70/15/15 split)
   └── app/ml/preprocessing/symptoms.py    (Symptom vectorizer, label encoder, 70/15/15 split)
        │
[Serialized Processed Splits]
   ├── datasets/processed/heart/    (train.csv, val.csv, test.csv, scaler.joblib)
   ├── datasets/processed/diabetes/ (train.csv, val.csv, test.csv, scaler.joblib)
   └── datasets/processed/symptoms/ (train.csv, val.csv, test.csv, label_encoder.joblib)
        │
[Model Training & Registry (Step 7)]
   └── backend/scripts/train_models.py (RandomForest, LightGBM, LogisticRegression)
```
