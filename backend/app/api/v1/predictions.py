"""FastAPI endpoints for real-time machine learning inference and active learning feedback."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.database.models import User
from app.ml.inference.predictor import RealtimePredictor
from app.schemas.predictions import (
    CardiovascularPredictionRequest,
    CardiovascularPredictionResponse,
    DiabetesPredictionRequest,
    DiabetesPredictionResponse,
    PredictionFeedbackRequest,
    PredictionFeedbackResponse,
    SymptomPredictionRequest,
    SymptomPredictionResponse,
)

router = APIRouter(prefix="/predictions", tags=["ML Predictions & Inference"])


@router.post(
    "/cardiovascular",
    response_model=CardiovascularPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Real-time Cardiovascular Disease Risk Prediction",
)
def predict_cardiovascular_risk(
    payload: CardiovascularPredictionRequest,
    current_user: User = Depends(get_current_user),
) -> CardiovascularPredictionResponse:
    """Predict cardiovascular disease risk probability and top contributing factors using the champion GradientBoosting model."""
    try:
        predictor = RealtimePredictor.get_instance()
        result = predictor.predict_cardiovascular(payload.model_dump())
        return CardiovascularPredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failure: {str(e)}",
        )


@router.post(
    "/diabetes",
    response_model=DiabetesPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Real-time Type 2 Diabetes Risk Prediction",
)
def predict_diabetes_risk(
    payload: DiabetesPredictionRequest,
    current_user: User = Depends(get_current_user),
) -> DiabetesPredictionResponse:
    """Predict Type 2 diabetes risk probability and contributing biomarkers using the champion RandomForest model."""
    try:
        predictor = RealtimePredictor.get_instance()
        result = predictor.predict_diabetes(payload.model_dump())
        return DiabetesPredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failure: {str(e)}",
        )


@router.post(
    "/symptoms",
    response_model=SymptomPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Real-time 41-Class Symptom Differential Diagnosis",
)
def predict_symptom_differential(
    payload: SymptomPredictionRequest,
    current_user: User = Depends(get_current_user),
) -> SymptomPredictionResponse:
    """Evaluate reported symptoms and return top-k ranked differential diagnostic possibilities with calibrated posterior probabilities."""
    try:
        predictor = RealtimePredictor.get_instance()
        result = predictor.predict_symptoms(symptoms=payload.symptoms, top_k=payload.top_k)
        return SymptomPredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failure: {str(e)}",
        )


@router.post(
    "/feedback",
    response_model=PredictionFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Clinician-Verified Diagnostic Feedback",
)
def submit_prediction_feedback(
    payload: PredictionFeedbackRequest,
    current_user: User = Depends(get_current_user),
) -> PredictionFeedbackResponse:
    """Ingest clinician-verified ground truth into the active learning queue for continuous model retraining."""
    try:
        predictor = RealtimePredictor.get_instance()
        sample_id = predictor.submit_feedback(
            target_disease=payload.target_disease,
            features=payload.features,
            ground_truth_label=payload.ground_truth_label,
            confidence_at_prediction=payload.confidence_at_prediction,
            notes=payload.notes,
        )
        return PredictionFeedbackResponse(
            sample_id=sample_id,
            target_disease=payload.target_disease,
            status="recorded",
            message=f"Verified feedback queued successfully for {payload.target_disease} retraining queue.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback queue failure: {str(e)}",
        )
