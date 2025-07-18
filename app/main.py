from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User, UserType
from app.api.v1.health import router as health_router
from app.api.v1.embeddings import router as embeddings_router
from app.core.logger import get_logger, log_startup_info, log_shutdown_info, log_error

app = FastAPI(
    title="MeStore API",
    description="API para gestión de tienda online",
    version="1.0.0",
)

# Registrar routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(embeddings_router, prefix="/api/v1")


# Event handlers para logging
@app.on_event("startup")
async def startup_event():
    """Log información de startup de la aplicación."""
    log_startup_info()

@app.on_event("shutdown")
async def shutdown_event():
    """Log información de shutdown de la aplicación."""
    log_shutdown_info()


# Exception handler global para logging de errores
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para capturar y loggear todas las excepciones."""
    log_error(
        exc,
        context={
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
        },
        logger_name="app.exceptions"
    )
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred",
        "status_code": 500
    }

@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {"message": "Bienvenido a MeStore API", "status": "running"}

@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    """Test de conexión async a PostgreSQL"""
    try:
        # Test básico de conexión
        result = await db.execute(text("SELECT 1 as test_value"))
        test_value = result.scalar()
        
        # Test de acceso a tabla users
        users_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        users_count = users_result.scalar()
        
        return {
            "status": "success",
            "database": "connected",
            "test_query": test_value,
            "users_table": "accessible",
            "users_count": users_count,
            "message": "PostgreSQL async connection working"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "connection_failed",
            "error": str(e),
            "message": "PostgreSQL async connection failed"
        }

@app.get("/users/test")
async def get_users_test(db: AsyncSession = Depends(get_db)):
    """Obtener todos los usuarios para testing"""
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return {
            "status": "success",
            "count": len(users),
            "users": [user.to_dict() for user in users]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)