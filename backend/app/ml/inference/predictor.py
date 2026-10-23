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
from app.ml.model_registry import ModelMetadata, load_model_bundle

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
MODELS_DIR = WORKSPACE_ROOT / "models" / "saved"
PROCESSED_DATA_DIR = WORKSPACE_ROOT / "datasets" / "processed"

CLINICAL_DISCLAIMER = (
    "MedOracle machine learning risk predictions provide clinical decision support "
    "and do not constitute a definitive medical diagnosis. Consult a licensed physician "
    "or specialist for comprehensive clinical evaluation."
)


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
                # Impact is proportional to feature importance * magnitude of scaled value
                impact_score = float(imp * abs(scaled_v))
                feature_impacts.append({
                    "feature": col,
                    "value": raw_v,
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
                impact_score = float(imp * abs(scaled_v))
                feature_impacts.append({
                    "feature": col,
                    "value": raw_v,
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
    def predict_symptoms(self, symptoms: List[str], top_k: int = 5) -> Dict[str, Any]:
        """Predict top-k differential diagnoses based on reported symptom entities.

        Args:
            symptoms: List of symptom string identifiers.
            top_k: Number of ranked diagnostic candidates to return.
        """
        if not symptoms:
            raise ValueError("At least one clinical symptom must be provided for differential diagnosis.")

        known_symptoms = self._symptoms_prep_meta.get("symptom_features", []) if self._symptoms_prep_meta else []
        index_to_disease = self._symptoms_prep_meta.get("index_to_disease", {}) if self._symptoms_prep_meta else {}

        # Normalize symptom tokens
        detected: List[str] = []
        unrecognized: List[str] = []

        normalized_set = {
            s.strip().lower().replace(" ", "_").replace("-", "_")
            for s in symptoms
            if s and s.strip()
        }

        for sym in normalized_set:
            if sym in known_symptoms:
                detected.append(sym)
            else:
                unrecognized.append(sym)

        if not detected:
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
            "detected_symptoms": sorted(detected),
            "unrecognized_symptoms": sorted(unrecognized),
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
