"""API v1 router package for MedOracle."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

v1_router = APIRouter()

# Mount sub-routers
v1_router.include_router(auth_router)


@v1_router.get("/", tags=["API v1"])
def v1_root():
    """API v1 status checkpoint."""
    return {
        "version": "v1",
        "status": "active",
        "description": "MedOracle API v1 root",
    }
