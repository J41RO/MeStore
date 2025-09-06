#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.models.user import UserType
from sqlalchemy import text

async def create_test_user():
    auth_service = AuthService()
    
    async with AsyncSessionLocal() as db:
        try:
            print("Verificando usuario test@mestore.com...")
            
            result = await db.execute(
                text("SELECT email FROM users WHERE email='test@mestore.com'")
            )
            existing = result.fetchone()
            
            if existing:
                print("Usuario ya existe. Eliminando...")
                await db.execute(
                    text("DELETE FROM users WHERE email='test@mestore.com'")
                )
                await db.commit()
            
            print("Creando usuario test@mestore.com...")
            
            user = await auth_service.create_user(
                db=db,
                email="test@mestore.com",
                password="123456",
                user_type=UserType.SUPERUSER,
                is_active=True
            )
            
            print(f"Usuario creado: {user.email}")
            return True
                
        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
            return False

if __name__ == "__main__":
    success = asyncio.run(create_test_user())
    sys.exit(0 if success else 1)