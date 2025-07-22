# ~/app/main.py
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
from app.core.database import get_db
from app.core.logger import get_logger, log_error, log_shutdown_info, log_startup_info
from app.core.logging_rotation import setup_log_rotation
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware, UserAgentValidatorMiddleware
from app.core.middleware.ip_detection import SuspiciousIPMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.models.user import User

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
    allow_origins=["http://192.168.1.137:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(api_router, prefix="/api/v1")


# Event handlers para logging
@app.on_event("startup")
async def startup_event():
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