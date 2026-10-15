"""API v1 router package for MedOracle."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.laboratory import router as laboratory_router
from app.api.v1.medical_history import router as medical_history_router
from app.api.v1.patient import router as patient_router
from app.api.v1.symptoms import router as symptoms_router

v1_router = APIRouter()

# Mount sub-routers
v1_router.include_router(auth_router)
v1_router.include_router(patient_router)
v1_router.include_router(medical_history_router)
v1_router.include_router(symptoms_router)
v1_router.include_router(laboratory_router)


@v1_router.get("/", tags=["API v1"])
def v1_root():
    """API v1 status checkpoint."""
    return {
        "version": "v1",
        "status": "active",
        "description": "MedOracle API v1 root",
    }
