"""API v1 router package for MedOracle."""

from fastapi import APIRouter

v1_router = APIRouter()


@v1_router.get("/", tags=["API v1"])
def v1_root():
    """API v1 status checkpoint."""
    return {
        "version": "v1",
        "status": "active",
        "description": "MedOracle API v1 root",
    }
