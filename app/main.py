from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.embeddings import router as embeddings_router
from app.api.v1.health import router as health_router
from app.core.database import get_db
from app.core.logger import (get_logger, log_error, log_shutdown_info,
                             log_startup_info)
from app.middleware import RequestLoggingMiddleware
from app.models.user import User

app = FastAPI(
    title="MeStore API",
    description="API para gestión de tienda online",
    version="1.0.0",
)

# Configurar middleware de logging CORRECTAMENTE
app.add_middleware(RequestLoggingMiddleware)

# Registrar routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(embeddings_router, prefix="/api/v1")


# Event handlers para logging
@app.on_event("startup")
async def startup_event():
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
    return {"message": "Bienvenido a MeStore API", "status": "running"}


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