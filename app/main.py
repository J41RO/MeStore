from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserType

app = FastAPI(
    title="MeStore API",
    description="API para gestión de tienda online",
    version="1.0.0",
)


@app.get("/")
async def root():


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
            "message": "PostgreSQL async connection working```
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
    """Endpoint de prueba"""
    return {"message": "Bienvenido a MeStore API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)