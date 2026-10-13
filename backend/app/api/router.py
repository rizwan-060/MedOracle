"""Top-level API router mounting all versioned sub-routers."""

from fastapi import APIRouter
from app.api.v1 import v1_router
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(v1_router, prefix=settings.api_v1_prefix)
