# Ruta: MeStore/app/main.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - FastAPI Main Application
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import redis

from app.api.v1 import api_router
from app.api.v1.handlers.exceptions import register_exception_handlers
from app.core.auth import auth_service
from app.core.config import settings

# Procesar configuración CORS
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
cors_methods = [method.strip() for method in settings.CORS_ALLOW_METHODS.split(",")]
cors_headers = [header.strip() for header in settings.CORS_ALLOW_HEADERS.split(",")]
from app.core.database import get_db
from app.core.logger import get_logger, log_error, log_shutdown_info, log_startup_info
from app.core.logging_rotation import setup_log_rotation
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware, UserAgentValidatorMiddleware
from app.core.middleware.ip_detection import SuspiciousIPMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
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

# Configuración Redis para Rate Limiting
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

# Crear aplicación FastAPI
app = FastAPI(
    title="MeStore API - Fulfillment & Marketplace Colombia",
    description="""API pública de MeStore para gestión de productos, IA, salud del sistema y agentes autónomos.

🏗️ ENTORNOS CONFIGURADOS:
   🐍 Backend: Python 3.11 + FastAPI (http://192.168.1.137:8000) ✅
   ⚛️ Frontend: Node.js 20 + React+TS (http://192.168.1.137:5173) ✅

📚 Documentación disponible en:
   • Swagger UI: http://192.168.1.137:8000/docs
   • ReDoc: http://192.168.1.137:8000/redoc
   • OpenAPI Schema: http://192.168.1.137:8000/openapi.json""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Agregar después de crear app:
app.mount("/media", StaticFiles(directory="uploads"), name="media")

# Registrar exception handlers
register_exception_handlers(app)

# CONFIGURACIÓN DE MIDDLEWARES EN ORDEN CORRECTO:

# 1. HTTPS Redirect (solo en producción)
if settings.ENVIRONMENT.lower() == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# 2. Security Headers (solo en producción)
if settings.ENVIRONMENT.lower() == "production":
    app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate Limiting Middleware
# 4. Suspicious IP Detection Middleware
app.add_middleware(
    SuspiciousIPMiddleware,
    suspicious_ips=settings.SUSPICIOUS_IPS,
    enable_blacklist=settings.ENABLE_IP_BLACKLIST
)

app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    authenticated_limit=settings.RATE_LIMIT_AUTHENTICATED_PER_MINUTE,
    anonymous_limit=settings.RATE_LIMIT_ANONYMOUS_PER_MINUTE,
    window_seconds=60
)

# 5. User-Agent Validator Middleware
app.add_middleware(UserAgentValidatorMiddleware)

# 6. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 5. CORS Middleware (al final)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

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


@app.on_event("startup")
async def startup_event():
    # Validar migraciones al startup
    await validate_migrations_on_startup()
    """Inicialización del sistema."""
    # Configurar sistema de rotación de logs
    setup_log_rotation()
    log_startup_info()

    # Inicializar sistema de autenticación
    logger = get_logger()
    logger.info(
        "Sistema de autenticación inicializado",
        extra={"auth_service": "ready", "jwt_algorithm": "HS256"},
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación."""
    log_shutdown_info()


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
    """Endpoint raíz de la API."""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint - excluido de rate limiting."""
    return {"status": "healthy", "service": "MeStore API"}


@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    """Test de conexión a la base de datos."""
    try:
        # Test básico de conexión
        await db.execute(text("SELECT 1"))

        # Test de conteo de usuarios
        users_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = users_result.scalar()

        return {
            "status": "success",
            "database": {
                "status": "connected",
                "message": "Conexión a base de datos exitosa",
                "user_count": user_count,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "database": {"status": "error", "message": f"Error de conexión: {str(e)}"},
        }


@app.get("/users/test")
async def get_users_test(db: AsyncSession = Depends(get_db)):
    """Test de lectura de usuarios."""
    try:
        stmt = select(User).limit(5)
        result = await db.execute(stmt)
        users = result.scalars().all()

        return {
            "status": "success",
            "count": len(users),
            "users": [
                {"id": u.id, "email": u.email, "user_type": u.user_type.value}
                for u in users
            ],
        }
    except Exception as e:
        return {"status": "error", "message": f"Error consultando usuarios: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)