from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.health import router as health_router
from app.api.v1.endpoints.health import router as health_simple_router
from app.api.v1.logs import router as logs_router
from app.api.v1.endpoints.fulfillment import router as fulfillment_router
from app.api.v1.endpoints.marketplace import router as marketplace_router
from app.api.v1.endpoints.agents import router as agents_router
from app.core.database import get_db
from app.core.logger import (get_logger, log_error, log_shutdown_info,

                             log_startup_info)
from app.middleware import RequestLoggingMiddleware
from app.models.user import User
from app.core.logging_rotation import setup_log_rotation

app = FastAPI(
    title="MeStore API",
    description="API para gestión de tienda online",
    version="1.0.0",
)

# Configurar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.137:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar middleware de logging CORRECTAMENTE
app.add_middleware(RequestLoggingMiddleware)

# Registrar routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(health_simple_router)
app.include_router(logs_router, prefix="/api/v1")
app.include_router(embeddings_router, prefix="/api/v1")
app.include_router(fulfillment_router, prefix="/api/v1/fulfillment")
app.include_router(marketplace_router, prefix="/marketplace")
app.include_router(agents_router, prefix="/agents")


# Event handlers para logging
@app.on_event("startup")
async def startup_event():
    # Configurar sistema de rotación de logs
    setup_log_rotation()
    log_startup_info()


@app.on_event("shutdown")
async def shutdown_event():
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
            "user_count": user_count
            }
        }
    except Exception as e:
        return {
            "status": "error", 
            "database": {
                "status": "error",
                "message": f"Error de conexión: {str(e)}"
            }
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)