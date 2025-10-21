#!/usr/bin/env python3
"""
Auto DB Initialization for Integration Tests
--------------------------------------------
Crea la base de datos de prueba (SQLite) si no existe, asegurando que
todas las tablas estén disponibles antes de ejecutar los tests.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test_mestore.db")

async def init_test_database():
    print(f"🔧 Inicializando base de datos de prueba: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Tablas creadas correctamente para entorno de test.")

if __name__ == "__main__":
    asyncio.run(init_test_database())
