# Ruta: MeStore/app/main.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - FastAPI Main Application
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import redis

from app.api.v1 import api_router
from app.api.v1.handlers.exceptions import register_exception_handlers
from app.core.config import settings

# Simplified dependencies and middleware
from app.core.dependencies_simple import (
    get_service_container,
    get_health_check_services,
    service_lifespan
)
from app.core.middleware_integration_simple import setup_application_middleware

# Response standardization
from app.schemas.response_base import HealthResponse
from app.utils.response_utils import ResponseUtils

from app.database import get_db
from app.core.logger import get_logger, log_error, log_shutdown_info, log_startup_info
from app.core.logging_rotation import setup_log_rotation
from app.models.user import User
from fastapi.staticfiles import StaticFiles
# Metadata para categorización de endpoints
tags_metadata = [
    {"name": "health", "description": "Monitoreo de estado y readiness del sistema"},
    {"name": "embeddings", "description": "Gestión de búsquedas vectoriales"},
    {"name": "logs", "description": "Consulta de eventos y errores"},
    {"name": "marketplace", "description": "Interacción con productos y vendedores"},
    {"name": "agents", "description": "Gestión de agentes inteligentes IA"},
]

# Application lifespan management with service container
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with service initialization"""
    logger = get_logger()
    logger.info("🚀 Starting MeStore application...")

    try:
        # Initialize service container
        await get_service_container()
        logger.info("✅ Service container initialized")

        # Validate migrations
        await validate_migrations_on_startup()

        # Setup log rotation
        setup_log_rotation()

        # Warm up cache if needed
        # await warm_up_application_cache()

        logger.info("🎉 Application startup completed successfully")
        yield

    except Exception as e:
        logger.error(f"💥 Application startup failed: {e}")
        raise
    finally:
        # Cleanup during shutdown
        logger.info("🔄 Starting application shutdown...")
        try:
            container = await get_service_container()
            await container.cleanup()
            logger.info("✅ Application shutdown completed")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Crear aplicación FastAPI con integrated service container
app = FastAPI(
    title="MeStore API - Fulfillment & Marketplace Colombia",
    description="""Enterprise-grade API for MeStore marketplace with comprehensive security, performance optimization, and service integration.

🏗️ PRODUCTION-READY ARCHITECTURE:
   🐍 Backend: Python 3.11 + FastAPI + Async SQLAlchemy (http://192.168.1.137:8000) ✅
   ⚛️ Frontend: Node.js 20 + React+TS (http://192.168.1.137:5173) ✅
   🔒 Security: Comprehensive security middleware with rate limiting and audit logging ✅
   ⚡ Performance: Redis caching, compression, and performance monitoring ✅
   🏪 Services: Integrated auth, payment, search, and commission services ✅

📚 Documentación disponible en:
   • Swagger UI: http://192.168.1.137:8000/docs
   • ReDoc: http://192.168.1.137:8000/redoc
   • OpenAPI Schema: http://192.168.1.137:8000/openapi.json
   • Health Check: http://192.168.1.137:8000/health
   • Service Status: http://192.168.1.137:8000/health/services""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Agregar después de crear app:
app.mount("/media", StaticFiles(directory="uploads"), name="media")

# Registrar exception handlers
register_exception_handlers(app)

# Setup integrated middleware chain with optimal ordering
setup_application_middleware(app)

# Registrar routers
app.include_router(api_router, prefix="/api/v1")


# Event handlers para logging
# Función para validar estado de migraciones al startup
async def validate_migrations_on_startup():
    """
    Validar que la base de datos esté migrada a la versión más reciente.
    En producción, la aplicación no debe iniciar si hay migraciones pendientes.
    """
    logger = get_logger()

    try:
        # Obtener environment actual
        current_env = settings.ENVIRONMENT.lower()
        logger.info(f"Validando migraciones para environment: {current_env}")

        # Comando para obtener revisión actual y head
        import subprocess
        import os

        # Cambiar al directorio del proyecto para ejecutar alembic
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Obtener revisión actual
        current_result = subprocess.run(
            ["alembic", "-x", f"env={current_env}", "current", "--head-only"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Obtener revisión head
        head_result = subprocess.run(
            ["alembic", "-x", f"env={current_env}", "heads", "--head-only"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        if current_result.returncode != 0 or head_result.returncode != 0:
            logger.error("Error ejecutando comandos alembic para validación de migraciones")
            if current_env == "production":
                raise RuntimeError("No se puede validar migraciones en producción")
            else:
                logger.warning("Continuando sin validación de migraciones en development")
                return

        current_rev = current_result.stdout.strip()
        head_rev = head_result.stdout.strip()

        logger.info(f"Revisión actual: {current_rev}")
        logger.info(f"Revisión esperada: {head_rev}")

        if current_rev != head_rev:
            error_msg = f"Base de datos no está actualizada. Actual: {current_rev}, Esperada: {head_rev}"
            logger.error(error_msg)

            if current_env == "production":
                raise RuntimeError(f"CRÍTICO: {error_msg}. La aplicación no puede iniciar en producción con migraciones pendientes.")
            else:
                logger.warning(f"Migraciones pendientes en {current_env}. Considere ejecutar: alembic -x env={current_env} upgrade head")
        else:
            logger.info("✅ Base de datos está actualizada - No hay migraciones pendientes")

    except subprocess.TimeoutExpired:
        logger.error("Timeout validando migraciones")
        if current_env == "production":
            raise RuntimeError("Timeout validando migraciones en producción")
    except Exception as e:
        logger.error(f"Error validando migraciones: {str(e)}")
        if current_env == "production":
            raise RuntimeError(f"Error crítico validando migraciones en producción: {str(e)}")
        else:
            logger.warning(f"Continuando sin validación completa de migraciones: {str(e)}")


# Note: Startup and shutdown events are now handled by the lifespan context manager


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

    return {
        "error": "Internal server error",
        "message": "Ha ocurrido un error interno del servidor",
    }


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
    """Test de conexión a la base de datos con response standardization."""
    try:
        # Test básico de conexión
        await db.execute(text("SELECT 1"))

        # Test de conteo de usuarios
        users_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = users_result.scalar()

        database_info = {
            "status": "connected",
            "message": "Conexión a base de datos exitosa",
            "user_count": user_count,
            "connection_test": "passed"
        }

        return ResponseUtils.success(
            data=database_info,
            message="Database connection test completed successfully"
        )

    except Exception as e:
        return ResponseUtils.error(
            error_code="DATABASE_CONNECTION_ERROR",
            message=f"Database connection failed: {str(e)}",
            status_code=503
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)