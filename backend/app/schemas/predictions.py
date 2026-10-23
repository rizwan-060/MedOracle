"""Pydantic v2 schemas for real-time ML inference and prediction feedback."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_DISCLAIMER = (
    "MedOracle machine learning risk predictions provide clinical decision support "
    "and do not constitute a definitive medical diagnosis. Consult a licensed physician "
    "or specialist for comprehensive clinical evaluation."
)


class FeatureFactor(BaseModel):
    """Quantitative feature contribution factor for model explainability."""

    feature: str = Field(..., description="Feature name")
    value: float = Field(..., description="Observed/normalized feature value")
    importance: float = Field(..., description="Global model feature importance weight")
    impact_score: float = Field(..., description="Product of importance and deviation magnitude")


# -----------------------------------------------------------------------------
# Cardiovascular Risk Schemas
# -----------------------------------------------------------------------------
class CardiovascularPredictionRequest(BaseModel):
    """Input payload for ML cardiovascular disease risk classification."""

    age: int = Field(..., ge=18, le=120, description="Age in years", examples=[63])
    sex: int = Field(..., ge=0, le=1, description="Biological sex (0 = female, 1 = male)", examples=[1])
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0: typical angina, 1: atypical angina, 2: non-anginal pain, 3: asymptomatic)", examples=[3])
    trestbps: float = Field(..., ge=60.0, le=300.0, description="Resting blood pressure in mm Hg", examples=[145.0])
    chol: float = Field(..., ge=80.0, le=700.0, description="Serum cholesterol in mg/dl", examples=[233.0])
    fbs: int = Field(0, ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)", examples=[1])
    restecg: int = Field(0, ge=0, le=2, description="Resting ECG results (0: normal, 1: ST-T wave abnormality, 2: LV hypertrophy)", examples=[0])
    thalach: float = Field(..., ge=50.0, le=250.0, description="Maximum heart rate achieved during exercise", examples=[150.0])
    exang: int = Field(0, ge=0, le=1, description="Exercise induced angina (1 = yes, 0 = no)", examples=[0])
    oldpeak: float = Field(0.0, ge=0.0, le=10.0, description="ST depression induced by exercise relative to rest", examples=[2.3])
    slope: int = Field(1, ge=0, le=2, description="Slope of peak exercise ST segment (0: upsloping, 1: flat, 2: downsloping)", examples=[0])
    ca: Optional[int] = Field(0, ge=0, le=3, description="Number of major vessels (0-3) colored by fluoroscopy", examples=[0])
    thal: Optional[int] = Field(3, ge=1, le=3, description="Thallium stress scintigraphy (1: normal, 2: fixed defect, 3: reversible defect)", examples=[1])

    model_config = ConfigDict(extra="ignore")


class CardiovascularPredictionResponse(BaseModel):
    """Calibrated output payload for cardiovascular disease prediction."""

    model_id: str
    model_version: str
    probability: float = Field(..., ge=0.0, le=1.0, description="Estimated posterior risk probability [0.0, 1.0]")
    predicted_class: int = Field(..., description="Binary class assignment (0 = low/normal, 1 = elevated risk)")
    risk_tier: Literal["low", "moderate", "high"] = Field(..., description="Categorical clinical risk tier")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Model prediction confidence score [0, 100]")
    top_contributing_factors: List[FeatureFactor] = Field(default_factory=list, description="Top influential features")
    disclaimer: str = DEFAULT_DISCLAIMER


# -----------------------------------------------------------------------------
# Diabetes Risk Schemas
# -----------------------------------------------------------------------------
class DiabetesPredictionRequest(BaseModel):
    """Input payload for ML Type 2 Diabetes risk classification."""

    pregnancies: int = Field(0, ge=0, le=25, description="Number of pregnancies", examples=[6])
    glucose: float = Field(..., ge=0.0, le=500.0, description="Fasting plasma glucose (mg/dL)", examples=[148.0])
    blood_pressure: float = Field(..., ge=0.0, le=250.0, description="Diastolic blood pressure (mm Hg)", examples=[72.0])
    skin_thickness: float = Field(0.0, ge=0.0, le=120.0, description="Triceps skin fold thickness (mm)", examples=[35.0])
    insulin: float = Field(0.0, ge=0.0, le=1000.0, description="2-Hour serum insulin (mu U/ml)", examples=[0.0])
    bmi: float = Field(..., ge=10.0, le=80.0, description="Body Mass Index (kg/m^2)", examples=[33.6])
    diabetes_pedigree: float = Field(..., ge=0.0, le=3.0, description="Diabetes pedigree function genetic score", examples=[0.627])
    age: int = Field(..., ge=18, le=120, description="Age in years", examples=[50])

    model_config = ConfigDict(extra="ignore")


class DiabetesPredictionResponse(BaseModel):
    """Calibrated output payload for Type 2 Diabetes prediction."""

    model_id: str
    model_version: str
    probability: float = Field(..., ge=0.0, le=1.0, description="Estimated diabetes risk probability [0.0, 1.0]")
    predicted_class: int = Field(..., description="Binary class assignment (0 = low/normal, 1 = elevated risk)")
    risk_tier: Literal["low", "moderate", "high"] = Field(..., description="Categorical clinical risk tier")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Model prediction confidence score [0, 100]")
    top_contributing_factors: List[FeatureFactor] = Field(default_factory=list, description="Top influential features")
    disclaimer: str = DEFAULT_DISCLAIMER


# -----------------------------------------------------------------------------
# Symptoms Diagnostic Schemas
# -----------------------------------------------------------------------------
class SymptomPredictionRequest(BaseModel):
    """Input payload for multi-class differential diagnostic prediction."""

    symptoms: List[str] = Field(
        ...,
        min_length=1,
        description="List of clinical symptom identifiers (e.g. ['chills', 'high_fever', 'headache'])",
        examples=[["chills", "high_fever", "sweating", "headache", "nausea"]],
    )
    top_k: int = Field(5, ge=1, le=20, description="Number of differential candidates to return", examples=[5])

    model_config = ConfigDict(extra="ignore")


class DifferentialCandidate(BaseModel):
    """Ranked diagnostic candidate from differential classification."""

    rank: int = Field(..., description="Ranking position (1 = primary suspected condition)")
    disease: str = Field(..., description="Standardized clinical disease entity")
    probability: float = Field(..., ge=0.0, le=1.0, description="Posterior probability score")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence percentage [0, 100]")


class SymptomPredictionResponse(BaseModel):
    """Differential diagnostic output ranking and symptom recognition report."""

    model_id: str
    model_version: str
    top_candidates: List[DifferentialCandidate] = Field(..., description="Ranked candidate diagnoses")
    detected_symptoms: List[str] = Field(..., description="Symptoms successfully matched to clinical ontology")
    unrecognized_symptoms: List[str] = Field(default_factory=list, description="Unmatched symptom tokens")
    disclaimer: str = DEFAULT_DISCLAIMER


# -----------------------------------------------------------------------------
# Active Learning Feedback Schemas
# -----------------------------------------------------------------------------
class PredictionFeedbackRequest(BaseModel):
    """Input payload for reporting clinician-verified ground truth."""

    target_disease: Literal["cardio", "diabetes", "symptoms"] = Field(
        ..., description="Target model family ('cardio', 'diabetes', 'symptoms')", examples=["cardio"]
    )
    features: Dict[str, Any] = Field(..., description="Feature key-value map at the time of prediction")
    ground_truth_label: Union[int, str] = Field(..., description="Confirmed clinical diagnosis (0/1 or disease name)")
    confidence_at_prediction: Optional[float] = Field(None, ge=0.0, le=100.0, description="Prior confidence score")
    notes: Optional[str] = Field(None, description="Clinician observations or audit notes")


class PredictionFeedbackResponse(BaseModel):
    """Acknowledgment payload confirming feedback ingestion into active learning queue."""

    sample_id: str = Field(..., description="Unique UUID assigned to feedback record")
    target_disease: str
    status: str = Field("recorded", description="Ingestion status")
    message: str = Field("Feedback queued successfully for model retraining.")
