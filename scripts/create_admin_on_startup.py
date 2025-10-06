#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.password import hash_password
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime

async def create_admin_if_not_exists():
    async with AsyncSessionLocal() as db:
        try:
            # Verificar si existe admin
            result = await db.execute(
                select(User).where(User.email == "admin@mestocker.com")
            )
            existing = result.scalar_one_or_none()

            if existing:
                print("✅ Admin user already exists")
                return

            # Crear superusuario
            admin = User(
                id=str(uuid4()),
                email="admin@mestocker.com",
                password_hash=hash_password("Admin123456"),
                nombre="Admin",
                apellido="MeStocker",
                user_type="SUPERUSER",
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin)
            await db.commit()
            print("✅ Admin user created: admin@mestocker.com / Admin123456")
        except Exception as e:
            print(f"❌ Error creating admin: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin_if_not_exists())
