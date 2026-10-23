"""MedOracle FastAPI Application Entrypoint.

Provides the FastAPI application factory, middleware (CORS, request logging),
standardized error handlers, health check, and mounts versioned routers.
"""

import logging
import time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("medoracle")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Backend API for the MedOracle multi-agent disease forecasting platform.",
        version=settings.version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000.0

        logger.info(
            "%s %s -> status=%d duration=%.2fms",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
        )
        return response

    # Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Format request validation errors consistently."""
        sanitized_errors = []
        for err in exc.errors():
            err_dict = dict(err)
            if "ctx" in err_dict and isinstance(err_dict["ctx"], dict):
                err_dict["ctx"] = {k: str(v) for k, v in err_dict["ctx"].items()}
            sanitized_errors.append(err_dict)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": sanitized_errors,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Format HTTP exceptions consistently."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": "HTTP_ERROR",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Catch-all for unhandled exceptions."""
        logger.exception("Unhandled server exception on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred",
                "error_code": "INTERNAL_SERVER_ERROR",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    # Root & Health Endpoints
    @app.get("/", tags=["System"])
    def root():
        """Root welcome endpoint."""
        return {
            "project": settings.app_name,
            "message": "MedOracle API is running",
            "version": settings.version,
            "environment": settings.app_env,
        }

    @app.get("/health", tags=["System"])
    def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "medoracle-backend",
            "version": settings.version,
            "environment": settings.app_env,
        }

    # Mount API routers
    app.include_router(api_router)

    return app


app = create_app()
