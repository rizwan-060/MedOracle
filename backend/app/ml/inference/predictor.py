"""Real-time Clinical Machine Learning Inference Engine.

Provides low-latency, calibrated predictions for:
1. Cardiovascular Disease Risk (GradientBoostingClassifier on 13 clinical biomarkers)
2. Type 2 Diabetes Risk (RandomForestClassifier on 8 metabolic/demographic indicators)
3. 41-Class Disease-Symptom Differential Diagnosis (MultinomialNB on 132 symptoms)

Also acts as the integration gateway to the active learning FeedbackBuffer.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from app.ml.feedback.buffer import FeedbackBuffer, FeedbackRecord
from app.ml.inference.nlp_extractor import ClinicalSymptomExtractor
from app.ml.model_registry import ModelMetadata, load_model_bundle

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
MODELS_DIR = WORKSPACE_ROOT / "models" / "saved"
PROCESSED_DATA_DIR = WORKSPACE_ROOT / "datasets" / "processed"

CLINICAL_DISCLAIMER = (
    "MedOracle machine learning risk predictions provide clinical decision support "
    "and do not constitute a definitive medical diagnosis. Consult a licensed physician "
    "or specialist for comprehensive clinical evaluation."
)

CARDIO_FEATURE_METADATA = {
    "cp": {
        "name": "Chest Pain Type",
        "interpret": lambda v: (
            "Typical Angina (severe exertional substernal pain)" if v == 0
            else "Atypical Angina (non-classical chest discomfort)" if v == 1
            else "Non-anginal Chest Pain" if v == 2
            else "Asymptomatic (no typical ischemic chest pain reported)"
        ),
        "direction": lambda v: "increases_risk" if v in [0, 1] else "decreases_risk",
    },
    "thal": {
        "name": "Thallium Stress Scintigraphy",
        "interpret": lambda v: (
            "Normal myocardial perfusion" if v == 1
            else "Fixed defect (prior myocardial infarction / scar tissue)" if v == 2
            else "Reversible defect (active inducible myocardial ischemia)"
        ),
        "direction": lambda v: "decreases_risk" if v == 1 else "increases_risk",
    },
    "age": {
        "name": "Patient Age",
        "interpret": lambda v: f"{int(v)} years old",
        "direction": lambda v: "increases_risk" if v >= 55 else "decreases_risk",
    },
    "oldpeak": {
        "name": "Exercise ST Depression (Oldpeak)",
        "interpret": lambda v: f"{v:.1f} mm ({'Marked ischemic depression' if v >= 2.0 else 'Moderate depression' if v >= 1.0 else 'Normal/minimal'})",
        "direction": lambda v: "increases_risk" if v >= 1.0 else "decreases_risk",
    },
    "trestbps": {
        "name": "Resting Blood Pressure",
        "interpret": lambda v: f"{v:.0f} mmHg ({'Stage 2 Hypertension' if v >= 140 else 'Stage 1 Hypertension' if v >= 130 else 'Elevated' if v >= 120 else 'Optimal'})",
        "direction": lambda v: "increases_risk" if v >= 130 else "decreases_risk",
    },
    "chol": {
        "name": "Total Serum Cholesterol",
        "interpret": lambda v: f"{v:.0f} mg/dL ({'High' if v >= 240 else 'Borderline High' if v >= 200 else 'Desirable'})",
        "direction": lambda v: "increases_risk" if v >= 200 else "decreases_risk",
    },
    "thalach": {
        "name": "Maximum Exercise Heart Rate",
        "interpret": lambda v: f"{v:.0f} bpm (cardiac exercise reserve)",
        "direction": lambda v: "decreases_risk" if v >= 145 else "increases_risk",
    },
    "ca": {
        "name": "Major Vessels Colored by Fluoroscopy",
        "interpret": lambda v: f"{int(v)} vessels ({'Significant calcification/stenosis' if v > 0 else 'Clear fluoroscopy'})",
        "direction": lambda v: "increases_risk" if v > 0 else "decreases_risk",
    },
    "exang": {
        "name": "Exercise Induced Angina",
        "interpret": lambda v: "Yes (angina provoked by exertion)" if v == 1 else "No (exercise tolerated without angina)",
        "direction": lambda v: "increases_risk" if v == 1 else "decreases_risk",
    },
    "slope": {
        "name": "ST Segment Slope",
        "interpret": lambda v: "Upsloping (normal)" if v == 0 else "Flat (ischemic)" if v == 1 else "Downsloping (severe ischemia)",
        "direction": lambda v: "increases_risk" if v in [1, 2] else "decreases_risk",
    },
    "fbs": {
        "name": "Fasting Blood Sugar > 120 mg/dL",
        "interpret": lambda v: "Elevated (>120 mg/dL)" if v == 1 else "Normal (<=120 mg/dL)",
        "direction": lambda v: "increases_risk" if v == 1 else "decreases_risk",
    },
    "restecg": {
        "name": "Resting ECG Results",
        "interpret": lambda v: "Normal" if v == 0 else "ST-T wave abnormality" if v == 1 else "Left ventricular hypertrophy",
        "direction": lambda v: "increases_risk" if v > 0 else "decreases_risk",
    },
    "sex": {
        "name": "Biological Sex",
        "interpret": lambda v: "Male" if v == 1 else "Female",
        "direction": lambda v: "increases_risk" if v == 1 else "decreases_risk",
    },
}

DIABETES_FEATURE_METADATA = {
    "Glucose": {
        "name": "Fasting Blood Glucose",
        "interpret": lambda v: f"{v:.0f} mg/dL ({'Diabetic range (>126)' if v >= 126 else 'Impaired fasting glucose (100-125)' if v >= 100 else 'Normal (<100)'})",
        "direction": lambda v: "increases_risk" if v >= 100 else "decreases_risk",
    },
    "BMI": {
        "name": "Body Mass Index (BMI)",
        "interpret": lambda v: f"{v:.1f} kg/m² ({'Obese (>=30)' if v >= 30 else 'Overweight (25-29.9)' if v >= 25 else 'Normal weight'})",
        "direction": lambda v: "increases_risk" if v >= 25 else "decreases_risk",
    },
    "Age": {
        "name": "Patient Age",
        "interpret": lambda v: f"{int(v)} years old",
        "direction": lambda v: "increases_risk" if v >= 45 else "decreases_risk",
    },
    "DiabetesPedigreeFunction": {
        "name": "Genetic Diabetes Pedigree",
        "interpret": lambda v: f"{v:.3f} ({'High familial genetic risk' if v >= 0.50 else 'Moderate/low genetic risk'})",
        "direction": lambda v: "increases_risk" if v >= 0.50 else "decreases_risk",
    },
    "BloodPressure": {
        "name": "Diastolic Blood Pressure",
        "interpret": lambda v: f"{v:.0f} mmHg ({'Elevated (>=80)' if v >= 80 else 'Normal'})",
        "direction": lambda v: "increases_risk" if v >= 80 else "decreases_risk",
    },
    "Insulin": {
        "name": "2-Hour Serum Insulin",
        "interpret": lambda v: f"{v:.0f} µU/mL ({'Hyperinsulinemia (insulin resistance)' if v >= 166 else 'Normal physiological range'})",
        "direction": lambda v: "increases_risk" if v >= 166 else "decreases_risk",
    },
    "SkinThickness": {
        "name": "Triceps Skinfold Thickness",
        "interpret": lambda v: f"{v:.0f} mm (subcutaneous adiposity)",
        "direction": lambda v: "increases_risk" if v >= 30 else "decreases_risk",
    },
    "Pregnancies": {
        "name": "Number of Pregnancies",
        "interpret": lambda v: f"{int(v)} pregnancies ({'Gestational metabolic stress factor' if v >= 3 else 'Low parity'})",
        "direction": lambda v: "increases_risk" if v >= 3 else "decreases_risk",
    },
}


class RealtimePredictor:
    """Singleton inference service for all registered MedOracle ML models."""

    _instance: Optional["RealtimePredictor"] = None

    def __init__(self, models_dir: Optional[Path] = None, data_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.data_dir = Path(data_dir) if data_dir else PROCESSED_DATA_DIR

        # Model bundles and metadata
        self._cardio_model: Optional[Any] = None
        self._cardio_meta: Optional[ModelMetadata] = None
        self._diabetes_model: Optional[Any] = None
        self._diabetes_meta: Optional[ModelMetadata] = None
        self._symptoms_model: Optional[Any] = None
        self._symptoms_meta: Optional[ModelMetadata] = None

        # Preprocessing metadata
        self._heart_prep_meta: Optional[Dict[str, Any]] = None
        self._diabetes_prep_meta: Optional[Dict[str, Any]] = None
        self._symptoms_prep_meta: Optional[Dict[str, Any]] = None

        # Clinical NLP extractor
        self._nlp_extractor: Optional[ClinicalSymptomExtractor] = None

        # Feedback buffer
        self._feedback_buffer = FeedbackBuffer()

        # Warm-up / load models
        self._load_models()

    @classmethod
    def get_instance(cls, models_dir: Optional[Path] = None, data_dir: Optional[Path] = None) -> "RealtimePredictor":
        """Return singleton instance of RealtimePredictor."""
        if cls._instance is None:
            cls._instance = cls(models_dir=models_dir, data_dir=data_dir)
        return cls._instance

    def _load_models(self) -> None:
        """Load and cache trained model estimators and preprocessing metadata."""
        # 1. Cardiovascular model
        self._cardio_model, self._cardio_meta = load_model_bundle("cardiovascular_risk_v1", models_dir=self.models_dir)
        heart_meta_path = self.data_dir / "heart" / "metadata.json"
        if heart_meta_path.exists():
            with open(heart_meta_path, "r", encoding="utf-8") as f:
                self._heart_prep_meta = json.load(f)

        # 2. Diabetes model
        self._diabetes_model, self._diabetes_meta = load_model_bundle("diabetes_risk_v1", models_dir=self.models_dir)
        diabetes_meta_path = self.data_dir / "diabetes" / "metadata.json"
        if diabetes_meta_path.exists():
            with open(diabetes_meta_path, "r", encoding="utf-8") as f:
                self._diabetes_prep_meta = json.load(f)

        # 3. Symptoms model
        self._symptoms_model, self._symptoms_meta = load_model_bundle("symptoms_disease_v1", models_dir=self.models_dir)
        symptoms_meta_path = self.data_dir / "symptoms" / "metadata.json"
        if symptoms_meta_path.exists():
            with open(symptoms_meta_path, "r", encoding="utf-8") as f:
                self._symptoms_prep_meta = json.load(f)

        # 4. Clinical NLP Symptom Extractor
        known_symptoms = self._symptoms_prep_meta.get("symptom_features", []) if self._symptoms_prep_meta else []
        self._nlp_extractor = ClinicalSymptomExtractor(known_symptoms=known_symptoms)

    # -------------------------------------------------------------------------
    # Cardiovascular Risk Prediction
    # -------------------------------------------------------------------------
    def predict_cardiovascular(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cardiovascular disease risk prediction and feature contributions.

        Expected feature keys:
            age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
        """
        required_cols = [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ]

        # Extract features and handle missing values
        features: Dict[str, float] = {}
        modes = self._heart_prep_meta.get("imputed_modes", {"ca": 0.0, "thal": 3.0}) if self._heart_prep_meta else {"ca": 0.0, "thal": 3.0}

        for col in required_cols:
            val = data.get(col)
            if val is None or val == "":
                if col in modes:
                    val = modes[col]
                else:
                    raise ValueError(f"Missing required cardiovascular feature: '{col}'")
            features[col] = float(val)

        # Apply z-score scaling for continuous features
        scaler = self._heart_prep_meta.get("scaler_params", {}) if self._heart_prep_meta else {}
        scaled_row: List[float] = []
        for col in required_cols:
            raw_val = features[col]
            if col in scaler:
                m = scaler[col]["mean"]
                s = scaler[col]["std"]
                scaled_val = (raw_val - m) / s if s > 1e-9 else 0.0
            else:
                scaled_val = raw_val
            scaled_row.append(scaled_val)

        # Predict probability
        x_input = np.array([scaled_row], dtype=np.float64)
        prob_arr = self._cardio_model.predict_proba(x_input)[0]
        prob_positive = float(prob_arr[1])
        predicted_class = 1 if prob_positive >= 0.50 else 0

        # Risk tiering
        if prob_positive < 0.20:
            risk_tier = "low"
        elif prob_positive < 0.50:
            risk_tier = "moderate"
        else:
            risk_tier = "high"

        # Calibrated confidence score (50% to 100% based on distance from boundary)
        confidence = round(abs(prob_positive - 0.50) * 2 * 50 + 50, 2)

        # Feature contribution analysis
        factors = []
        if hasattr(self._cardio_model, "feature_importances_"):
            importances = self._cardio_model.feature_importances_
            feature_impacts = []
            for col, imp, scaled_v, raw_v in zip(required_cols, importances, scaled_row, [features[c] for c in required_cols]):
                meta = CARDIO_FEATURE_METADATA.get(col, {})
                display_name = meta.get("name", col)
                interpretation = meta["interpret"](raw_v) if "interpret" in meta else f"{raw_v}"
                direction = meta["direction"](raw_v) if "direction" in meta else "neutral"
                impact_score = float(imp * abs(scaled_v))
                feature_impacts.append({
                    "feature": col,
                    "display_name": display_name,
                    "value": raw_v,
                    "interpretation": interpretation,
                    "direction": direction,
                    "importance": round(float(imp), 4),
                    "impact_score": round(impact_score, 4),
                })
            feature_impacts.sort(key=lambda x: x["impact_score"], reverse=True)
            factors = feature_impacts[:4]

        return {
            "model_id": self._cardio_meta.model_id if self._cardio_meta else "cardiovascular_risk_v1",
            "model_version": self._cardio_meta.version if self._cardio_meta else "1.0.0",
            "probability": round(prob_positive, 4),
            "predicted_class": predicted_class,
            "risk_tier": risk_tier,
            "confidence_score": confidence,
            "top_contributing_factors": factors,
            "disclaimer": CLINICAL_DISCLAIMER,
        }

    # -------------------------------------------------------------------------
    # Diabetes Risk Prediction
    # -------------------------------------------------------------------------
    def predict_diabetes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Type 2 Diabetes risk prediction and feature contributions.

        Expected feature keys (case-insensitive):
            Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
        """
        canonical_cols = [
            "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
            "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
        ]
        alias_map = {
            "pregnancies": "Pregnancies",
            "glucose": "Glucose",
            "bloodpressure": "BloodPressure",
            "blood_pressure": "BloodPressure",
            "skinthickness": "SkinThickness",
            "skin_thickness": "SkinThickness",
            "insulin": "Insulin",
            "bmi": "BMI",
            "diabetespedigree": "DiabetesPedigreeFunction",
            "diabetes_pedigree": "DiabetesPedigreeFunction",
            "diabetespedigreefunction": "DiabetesPedigreeFunction",
            "age": "Age",
        }

        # Normalize incoming data dictionary keys
        normalized_data = {}
        for k, v in data.items():
            k_lower = k.strip().lower()
            k_clean = k_lower.replace("_", "")
            if k in canonical_cols:
                normalized_data[k] = v
            elif k_clean in alias_map:
                normalized_data[alias_map[k_clean]] = v
            elif k_lower in alias_map:
                normalized_data[alias_map[k_lower]] = v

        # Validate gender and enforce biological plausibility rules
        gender = data.get("gender")
        if gender is not None:
            gender = str(gender).strip().lower()

        raw_preg = normalized_data.get("Pregnancies")
        if gender == "male":
            if raw_preg is not None:
                raise ValueError(
                    "Biological contradiction: Male patients must not provide a pregnancies field. "
                    "Omit this field entirely for male patients."
                )
            normalized_data["Pregnancies"] = 0.0
        elif raw_preg is None:
            normalized_data["Pregnancies"] = 0.0

        # Validate required columns
        medians = self._diabetes_prep_meta.get("imputed_medians", {}) if self._diabetes_prep_meta else {}
        scaler = self._diabetes_prep_meta.get("scaler_params", {}) if self._diabetes_prep_meta else {}

        features: Dict[str, float] = {}
        for col in canonical_cols:
            val = normalized_data.get(col)
            if val is None or val == "":
                raise ValueError(f"Missing required diabetes feature: '{col}'")
            val_float = float(val)
            # Biologically impossible 0 imputation
            if val_float == 0.0 and col in medians:
                val_float = float(medians[col])
            features[col] = val_float

        # Scale features
        scaled_row: List[float] = []
        for col in canonical_cols:
            raw_val = features[col]
            if col in scaler:
                m = scaler[col]["mean"]
                s = scaler[col]["std"]
                scaled_val = (raw_val - m) / s if s > 1e-9 else 0.0
            else:
                scaled_val = raw_val
            scaled_row.append(scaled_val)

        # Predict probability
        x_input = np.array([scaled_row], dtype=np.float64)
        prob_arr = self._diabetes_model.predict_proba(x_input)[0]
        prob_positive = float(prob_arr[1])
        predicted_class = 1 if prob_positive >= 0.50 else 0

        # Risk tiering
        if prob_positive < 0.25:
            risk_tier = "low"
        elif prob_positive < 0.55:
            risk_tier = "moderate"
        else:
            risk_tier = "high"

        # Calibrated confidence score
        confidence = round(abs(prob_positive - 0.50) * 2 * 50 + 50, 2)

        # Feature contribution analysis
        factors = []
        if hasattr(self._diabetes_model, "feature_importances_"):
            importances = self._diabetes_model.feature_importances_
            feature_impacts = []
            for col, imp, scaled_v, raw_v in zip(canonical_cols, importances, scaled_row, [features[c] for c in canonical_cols]):
                # Clinical rule: exclude Pregnancies from male patient contributing factors
                if gender == "male" and col == "Pregnancies":
                    continue
                meta = DIABETES_FEATURE_METADATA.get(col, {})
                display_name = meta.get("name", col)
                interpretation = meta["interpret"](raw_v) if "interpret" in meta else f"{raw_v}"
                direction = meta["direction"](raw_v) if "direction" in meta else "neutral"
                impact_score = float(imp * abs(scaled_v))
                feature_impacts.append({
                    "feature": col,
                    "display_name": display_name,
                    "value": raw_v,
                    "interpretation": interpretation,
                    "direction": direction,
                    "importance": round(float(imp), 4),
                    "impact_score": round(impact_score, 4),
                })
            feature_impacts.sort(key=lambda x: x["impact_score"], reverse=True)
            factors = feature_impacts[:4]

        return {
            "model_id": self._diabetes_meta.model_id if self._diabetes_meta else "diabetes_risk_v1",
            "model_version": self._diabetes_meta.version if self._diabetes_meta else "1.0.0",
            "probability": round(prob_positive, 4),
            "predicted_class": predicted_class,
            "risk_tier": risk_tier,
            "confidence_score": confidence,
            "top_contributing_factors": factors,
            "disclaimer": CLINICAL_DISCLAIMER,
        }

    # -------------------------------------------------------------------------
    # Symptom-Based Differential Diagnosis
    # -------------------------------------------------------------------------
    def predict_symptoms(
        self,
        symptoms: Optional[List[str]] = None,
        text: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Predict top-k differential diagnoses based on reported symptom entities or free-text narrative.

        Args:
            symptoms: Optional list of symptom string identifiers.
            text: Optional natural language narrative describing symptoms.
            top_k: Number of ranked diagnostic candidates to return.
        """
        extracted_entities = []
        negated_symptoms = []
        detected: List[str] = []
        unrecognized: List[str] = []

        # 1. If narrative text provided, invoke ClinicalSymptomExtractor
        if text and text.strip():
            nlp_result = self._nlp_extractor.extract(text)
            detected.extend(nlp_result["detected_symptoms"])
            extracted_entities.extend(nlp_result["extracted_entities"])
            negated_symptoms.extend(nlp_result["negated_symptoms"])
            unrecognized.extend(nlp_result["unrecognized_spans"])

        # 2. If structured symptoms list provided, normalize and merge
        known_symptoms = self._symptoms_prep_meta.get("symptom_features", []) if self._symptoms_prep_meta else []
        index_to_disease = self._symptoms_prep_meta.get("index_to_disease", {}) if self._symptoms_prep_meta else {}

        if symptoms:
            for s in symptoms:
                if not s or not s.strip():
                    continue
                clean_s = s.strip().lower().replace(" ", "_").replace("-", "_")
                if clean_s in known_symptoms:
                    if clean_s not in detected:
                        detected.append(clean_s)
                else:
                    # Synonym lookup
                    matched_canonical = self._nlp_extractor._synonym_lookup.get(s.strip().lower())
                    if matched_canonical and matched_canonical in known_symptoms:
                        if matched_canonical not in detected:
                            detected.append(matched_canonical)
                    else:
                        unrecognized.append(s)

        # Exclude symptoms ruled out by clinical negation
        detected = [sym for sym in detected if sym not in negated_symptoms]

        if not detected:
            if negated_symptoms:
                raise ValueError(
                    f"All mentioned symptoms were clinically ruled out/negated: {negated_symptoms}"
                )
            raise ValueError(
                f"None of the provided symptoms could be recognized. Unrecognized: {unrecognized}"
            )

        # Construct 132-element binary input vector
        input_vector = [1.0 if sym in detected else 0.0 for sym in known_symptoms]
        x_input = np.array([input_vector], dtype=np.float64)

        # Predict probability distribution across all 41 diseases
        probs = self._symptoms_model.predict_proba(x_input)[0]

        # Retrieve top-k sorted candidate indices
        sorted_indices = np.argsort(probs)[::-1][:top_k]

        candidates = []
        for rank, idx in enumerate(sorted_indices, start=1):
            disease_name = index_to_disease.get(str(idx), f"Unknown Condition (Class {idx})")
            p = float(probs[idx])
            candidates.append({
                "rank": rank,
                "disease": disease_name,
                "probability": round(p, 4),
                "confidence_score": round(p * 100, 2),
            })

        return {
            "model_id": self._symptoms_meta.model_id if self._symptoms_meta else "symptoms_disease_v1",
            "model_version": self._symptoms_meta.version if self._symptoms_meta else "1.0.0",
            "top_candidates": candidates,
            "detected_symptoms": sorted(list(set(detected))),
            "extracted_entities": extracted_entities,
            "negated_symptoms": sorted(list(set(negated_symptoms))),
            "unrecognized_symptoms": sorted(list(set(unrecognized))),
            "disclaimer": CLINICAL_DISCLAIMER,
        }

    # -------------------------------------------------------------------------
    # Active Learning Feedback Queue
    # -------------------------------------------------------------------------
    def submit_feedback(
        self,
        target_disease: str,
        features: Dict[str, Any],
        ground_truth_label: Union[int, str],
        confidence_at_prediction: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Route verified clinician diagnosis into the active learning queue."""
        if target_disease not in ["cardio", "diabetes", "symptoms"]:
            raise ValueError(
                f"Invalid target_disease: '{target_disease}'. Must be 'cardio', 'diabetes', or 'symptoms'."
            )

        record = FeedbackRecord(
            target_disease=target_disease,
            features=features,
            ground_truth_label=ground_truth_label,
            confidence_at_prediction=confidence_at_prediction,
            notes=notes,
        )

        sample_id = self._feedback_buffer.add_record(record)
        return sample_id

    # -------------------------------------------------------------------------
    # Programmatic Hook for Patient Risk Assessment & Multi-Agent Pipeline
    # -------------------------------------------------------------------------
    def predict_patient_assessment(self, user_id: str, db: Any) -> Dict[str, Any]:
        """Ingests patient demographics, laboratory biomarkers, and symptom reports from the database.

        Transforms features, applies stored preprocessing scalers, runs multi-model inference,
        and returns unified predictions. Primary programmatic hook for the Risk Prediction Agent.
        """
        from datetime import date
        from app.database.repositories import (
            LabResultRepository,
            PatientProfileRepository,
            SymptomReportRepository,
        )

        profile_repo = PatientProfileRepository(db)
        lab_repo = LabResultRepository(db)
        symptom_repo = SymptomReportRepository(db)

        profile = profile_repo.get_by_user_id(user_id)
        latest_lab = lab_repo.get_latest_by_user_id(user_id)
        symptom_reports = symptom_repo.list_by_user_id(user_id, limit=5)

        imputed_or_defaulted = []

        # 1. Age extraction
        if profile and profile.date_of_birth:
            today = date.today()
            dob = profile.date_of_birth
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        else:
            age = 50
            imputed_or_defaulted.append("age (defaulted to 50)")

        # 2. Gender extraction
        gender_raw = profile.gender.lower() if profile and profile.gender else "male"
        sex = 1 if gender_raw == "male" else 0
        if not profile or not profile.gender:
            imputed_or_defaulted.append("gender (defaulted to male)")

        # 3. BMI extraction
        if profile and profile.height_cm and profile.weight_kg and profile.height_cm > 0:
            bmi = round(profile.weight_kg / ((profile.height_cm / 100.0) ** 2), 2)
        else:
            bmi = 27.5
            imputed_or_defaulted.append("bmi (defaulted to 27.5)")

        # 4. Lab biomarkers extraction
        biomarkers: Dict[str, Any] = {}
        if latest_lab and latest_lab.biomarkers:
            for k, v in latest_lab.biomarkers.items():
                clean_k = k.strip().lower().replace(" ", "").replace("_", "")
                biomarkers[clean_k] = v

        def _get_bio(keys: List[str], default_val: float, param_name: str) -> float:
            for k in keys:
                clean_k = k.lower().replace(" ", "").replace("_", "")
                if clean_k in biomarkers:
                    try:
                        return float(biomarkers[clean_k])
                    except (ValueError, TypeError):
                        pass
            imputed_or_defaulted.append(param_name)
            return default_val

        trestbps = _get_bio(["resting_blood_pressure", "trestbps", "systolic_bp", "blood_pressure_systolic"], 125.0, "resting_blood_pressure (defaulted 125 mmHg)")
        diastolic_bp = _get_bio(["diastolic_bp", "blood_pressure_diastolic", "blood_pressure"], 75.0, "diastolic_blood_pressure (defaulted 75 mmHg)")
        chol = _get_bio(["total_cholesterol", "cholesterol", "chol"], 210.0, "total_cholesterol (defaulted 210 mg/dL)")
        glucose = _get_bio(["fasting_glucose", "blood_glucose", "glucose"], 105.0, "fasting_glucose (defaulted 105 mg/dL)")
        fbs = 1 if glucose > 120.0 else 0
        thalach = _get_bio(["max_heart_rate", "thalach", "heart_rate"], 150.0, "max_heart_rate (defaulted 150 bpm)")
        oldpeak = _get_bio(["st_depression", "oldpeak"], 0.8, "st_depression (defaulted 0.8)")
        restecg = int(_get_bio(["restecg", "resting_ecg"], 0.0, "resting_ecg (defaulted 0)"))
        exang = int(_get_bio(["exang", "exercise_angina"], 0.0, "exercise_angina (defaulted 0)"))
        slope = int(_get_bio(["slope", "st_slope"], 1.0, "st_slope (defaulted 1)"))
        ca = int(_get_bio(["ca", "vessels_colored"], 0.0, "major_vessels_ca (defaulted 0)"))
        thal = int(_get_bio(["thal", "thallium_stress"], 1.0, "thallium_stress (defaulted 1)"))

        # Diabetes specific
        if gender_raw == "male":
            pregnancies = None
        else:
            pregnancies = int(_get_bio(["pregnancies"], 0.0, "pregnancies (defaulted 0)"))
        skin_thickness = _get_bio(["skin_thickness", "skinthickness"], 29.0, "skin_thickness (imputed median 29 mm)")
        insulin = _get_bio(["insulin", "serum_insulin"], 125.0, "insulin (imputed median 125 mu U/ml)")
        diabetes_pedigree = _get_bio(["diabetes_pedigree", "diabetespedigreefunction", "pedigree"], 0.47, "diabetes_pedigree (defaulted 0.47)")

        # 5. Cardiovascular ML prediction
        cardio_input = {
            "age": age,
            "sex": sex,
            "cp": 0,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal,
        }
        cardio_res = self.predict_cardiovascular(cardio_input)

        # 6. Diabetes ML prediction
        diabetes_input = {
            "gender": gender_raw,
            "glucose": glucose,
            "blood_pressure": diastolic_bp,
            "skin_thickness": skin_thickness,
            "insulin": insulin,
            "bmi": bmi,
            "diabetes_pedigree": diabetes_pedigree,
            "age": age,
        }
        if gender_raw != "male":
            diabetes_input["pregnancies"] = pregnancies
        diabetes_res = self.predict_diabetes(diabetes_input)

        # 7. Symptoms differential diagnosis
        collected_symptoms: List[str] = []
        for rep in symptom_reports:
            if rep.structured_symptoms:
                for s in rep.structured_symptoms:
                    if isinstance(s, str) and s.strip():
                        collected_symptoms.append(s.strip())

        symptoms_res = None
        if collected_symptoms:
            try:
                symptoms_res = self.predict_symptoms(collected_symptoms, top_k=5)
            except Exception:
                symptoms_res = None

        # 8. Clinical synthesis
        top_diff = (
            symptoms_res["top_candidates"][0]["disease"]
            if symptoms_res and symptoms_res.get("top_candidates")
            else None
        )
        summary_parts = [
            f"Patient is a {age}-year-old {gender_raw}.",
            f"Cardiovascular disease risk is evaluated at {cardio_res['probability']*100:.1f}% ({cardio_res['risk_tier'].upper()} risk tier, confidence {cardio_res['confidence_score']:.1f}%).",
            f"Type 2 diabetes risk is evaluated at {diabetes_res['probability']*100:.1f}% ({diabetes_res['risk_tier'].upper()} risk tier, confidence {diabetes_res['confidence_score']:.1f}%).",
        ]
        if top_diff:
            summary_parts.append(
                f"Primary differential diagnostic candidate from reported symptoms: {top_diff} (calibrated confidence {symptoms_res['top_candidates'][0]['confidence_score']:.1f}%)."
            )
        else:
            summary_parts.append("No active acute symptom reports on file for differential ranking.")

        clinical_summary = " ".join(summary_parts)

        return {
            "user_id": user_id,
            "patient_age": age,
            "patient_gender": gender_raw,
            "cardiovascular": cardio_res,
            "diabetes": diabetes_res,
            "differential_diagnosis": symptoms_res,
            "imputed_or_defaulted_parameters": imputed_or_defaulted,
            "clinical_summary": clinical_summary,
            "disclaimer": CLINICAL_DISCLAIMER,
        }
