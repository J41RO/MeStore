# Ruta: MeStore/app/main.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - FastAPI Main Application
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi.errors import RateLimitExceeded

import logging as stdlib_logging
import os
import inspect
import httpx

logger_early = stdlib_logging.getLogger(__name__)
logger_early.info("DEBUG: Starting imports in main.py")

# CRITICAL: Disable heavy services for fast startup
os.environ['DISABLE_SEARCH_SERVICE'] = '1'
os.environ['DISABLE_CHROMA_SERVICE'] = '1'
logger_early.info("DEBUG: Heavy services disabled for fast startup")


def _patch_httpx_delete_json_support() -> None:
    """Ensure httpx.AsyncClient.delete acepta parámetro json en entornos legacy."""
    delete_sig = inspect.signature(httpx.AsyncClient.delete)
    if "json" not in delete_sig.parameters:
        async def delete_with_json(self, url, **kwargs):  # type: ignore[override]
            json_payload = kwargs.pop("json", None)
            return await self.request("DELETE", url, json=json_payload, **kwargs)

        httpx.AsyncClient.delete = delete_with_json  # type: ignore[assignment]


_patch_httpx_delete_json_support()

from app.api.v1 import api_router
logger_early.info("DEBUG: api_router imported successfully")

from app.api.v1.handlers.exceptions import register_exception_handlers
logger_early.info("DEBUG: exception handlers imported")

from app.core.config import settings
logger_early.info("DEBUG: settings imported")

# Simplified dependencies and middleware - with fallback for production
try:
    from app.core.dependencies_simple import (
        get_service_container,
        get_health_check_services,
        service_lifespan
    )
    logger_early.info("DEBUG: dependencies_simple imported")
except Exception as e:
    logger_early.warning(f"Could not import dependencies_simple: {e}")
    # Fallback minimal health check
    async def get_health_check_services():
        return {"status": "healthy", "services": {}}

try:
    from app.core.middleware_integration_simple import setup_application_middleware
    logger_early.info("DEBUG: middleware_integration_simple imported")
except Exception as e:
    logger_early.warning(f"Could not import middleware_integration_simple: {e}")
    # Fallback minimal middleware setup
    def setup_application_middleware(app):
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Response standardization
from app.schemas.response_base import HealthResponse
from app.utils.response_utils import ResponseUtils

from app.database import get_db

# Optional imports with fallbacks
try:
    from app.core.logger import get_logger, log_error, log_shutdown_info, log_startup_info
    logger_early.info("DEBUG: Custom logger imported")
except Exception as e:
    logger_early.warning(f"Could not import custom logger: {e}, using stdlib logger")
    get_logger = lambda: logger_early
    log_error = lambda **kwargs: logger_early.error(str(kwargs))
    log_shutdown_info = lambda: logger_early.info("Shutdown")
    log_startup_info = lambda: logger_early.info("Startup")

try:
    from app.core.logging_rotation import setup_log_rotation
    logger_early.info("DEBUG: Log rotation imported")
except Exception as e:
    logger_early.warning(f"Could not import log rotation: {e}")
    setup_log_rotation = lambda: None

from app.models.user import User
from fastapi.staticfiles import StaticFiles
from pathlib import Path
logger_early.info("DEBUG: All imports completed in main.py")

# Metadata para categorización de endpoints
tags_metadata = [
    {"name": "health", "description": "Monitoreo de estado y readiness del sistema"},
    {"name": "embeddings", "description": "Gestión de búsquedas vectoriales"},
    {"name": "logs", "description": "Consulta de eventos y errores"},
    {"name": "marketplace", "description": "Interacción con productos y vendedores"},
    {"name": "agents", "description": "Gestión de agentes inteligentes IA"},
]

# Simplified lifespan for production deployment
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan management - no blocking operations"""
    logger_early.info("MeStore startup - minimal mode")

    # No initialization - just yield immediately to allow fast startup
    yield

    # Minimal cleanup
    logger_early.info("MeStore shutdown")

# Crear aplicación FastAPI
logger_early.info("DEBUG: Creating FastAPI app instance...")
app = FastAPI(
    title="MeStore API - Fulfillment & Marketplace Colombia",
    description="""Enterprise-grade API for MeStore marketplace with comprehensive security, performance optimization, and service integration.

Production-ready architecture with FastAPI + Async SQLAlchemy + PostgreSQL

Documentation:
   • Swagger UI: /docs
   • ReDoc: /redoc
   • OpenAPI Schema: /openapi.json
   • Health Check: /health
   • Service Status: /health/services""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)
logger_early.info("DEBUG: FastAPI app created successfully")

# Create uploads directory if it doesn't exist and mount StaticFiles
logger_early.info("DEBUG: Setting up uploads directory...")
try:
    BASE_DIR = Path(__file__).parent.parent
    UPLOADS_DIR = BASE_DIR / "uploads"
    UPLOADS_DIR.mkdir(exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(UPLOADS_DIR)), name="media")
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
    logger_early.info("DEBUG: Uploads directory configured")
except Exception as e:
    logger_early.warning(f"Could not setup uploads directory: {e} - skipping static files")

# Registrar exception handlers
logger_early.info("DEBUG: Registering exception handlers...")
register_exception_handlers(app)
logger_early.info("DEBUG: Exception handlers registered")

# Setup integrated middleware chain with optimal ordering
logger_early.info("DEBUG: Setting up application middleware...")
setup_application_middleware(app)
logger_early.info("DEBUG: Application middleware setup completed")

# Registrar routers
logger_early.info("DEBUG: Including API router...")
app.include_router(api_router, prefix="/api/v1")
logger_early.info("DEBUG: API router included - main.py initialization complete")


@app.get("/", tags=["health"])
async def root_status() -> dict:
    """Simplified root endpoint used by integration tests and uptime checks."""
    return {"status": "ok"}


# Exception handler for rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error_code": "RATE_LIMIT_EXCEEDED",
            "error_message": "Demasiadas solicitudes. Por favor intenta de nuevo más tarde.",
            "retry_after": exc.detail
        }
    )


# Exception handler global para logging de errores
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para capturar y loggear todas las excepciones."""
    log_error(
        error=exc,
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
        },
    )

    return ResponseUtils.error(
        error_code="INTERNAL_SERVER_ERROR",
        message="Ha ocurrido un error interno del servidor",
        status_code=500
    )


@app.get("/")
async def root():
    """Endpoint raíz de la API con response standardization."""
    return ResponseUtils.success(
        data={"message": "MeStore API is running", "docs": "/docs"},
        message="API root endpoint accessed successfully"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Basic health check endpoint - excluido de rate limiting."""
    health_data = {
        "service": "MeStore API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "healthy"
    }
    return ResponseUtils.success(
        data=health_data,
        message="Health check completed successfully"
    )


@app.get("/health/services", response_model=HealthResponse)
async def health_services(health_data = Depends(get_health_check_services)):
    """Comprehensive health check for all integrated services."""
    is_healthy = all("unhealthy" not in str(v) for v in health_data.values())

    complete_health_data = {
        "service": "MeStore API - Service Health Check",
        "status": "healthy" if is_healthy else "degraded",
        "services": health_data,
        "overall_status": "operational" if is_healthy else "degraded"
    }

    return ResponseUtils.success(
        data=complete_health_data,
        message="Service health check completed successfully"
    )


@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    """Test de conexión a la base de datos con respuesta simplificada para testing."""
    try:
        await db.execute(text("SELECT 1"))
        users_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = users_result.scalar()

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "database": {
                    "connection": "ok",
                    "message": "Conexión a base de datos exitosa",
                    "user_count": user_count,
                    "connection_test": "passed"
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "database": {
                    "connection": "failed",
                    "message": "Database connection failed",
                    "error": str(e)
                }
            }
        )


@app.get("/users/test")
async def get_users_test(db: AsyncSession = Depends(get_db)):
    """Test de lectura de usuarios con response standardization."""
    try:
        stmt = select(User).limit(5)
        result = await db.execute(stmt)
        users = result.scalars().all()

        users_data = {
            "count": len(users),
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "user_type": u.user_type.value,
                    "created_at": u.created_at.isoformat() if u.created_at else None
                }
                for u in users
            ],
        }

        return ResponseUtils.success(
            data=users_data,
            message=f"Retrieved {len(users)} test users successfully"
        )

    except Exception as e:
        return ResponseUtils.error(
            error_code="USER_QUERY_ERROR",
            message=f"Error querying users: {str(e)}",
            status_code=500
        )


@app.get("/test-token")
async def get_test_token():
    """Generar token de prueba para testing de endpoints."""
    from app.core.security import create_access_token
    from datetime import timedelta

    token_data = {
        "sub": "test@example.com",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_type": "BUYER",
        "exp": timedelta(hours=24)
    }

    access_token = create_access_token(data=token_data)

    return ResponseUtils.success(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {
                "email": "test@example.com",
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_type": "BUYER"
            }
        },
        message="Test token generated successfully"
    )
