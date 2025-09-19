#!/usr/bin/env python3
"""
Script para verificar credenciales de usuarios en la base de datos
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User, UserType


async def check_users():
    """Verificar usuarios disponibles en la base de datos"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()

            print("=== CREDENCIALES DISPONIBLES EN BD ===")
            if not users:
                print("❌ No hay usuarios en la base de datos")
                return

            for user in users:
                print(f"📧 Email: {user.email}")
                print(
                    f'👤 Tipo: {user.user_type.value if user.user_type else "No definido"}'
                )
                print(f"🆔 ID: {user.id}")
                if hasattr(user, "nombre") and user.nombre:
                    apellido = getattr(user, "apellido", "") or ""
                    print(f"📝 Nombre: {user.nombre} {apellido}".strip())
                if hasattr(user, "is_active"):
                    print(f'✅ Activo: {"Sí" if user.is_active else "No"}')
                print("---")

            print(f"📊 Total usuarios: {len(users)}")

            # Mostrar distribución por tipo
            by_type = {}
            for user in users:
                user_type = user.user_type.value if user.user_type else "Sin tipo"
                by_type[user_type] = by_type.get(user_type, 0) + 1

            print("\n=== DISTRIBUCIÓN POR TIPO ===")
            for user_type, count in by_type.items():
                print(f"{user_type}: {count} usuarios")

        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")


if __name__ == "__main__":
    asyncio.run(check_users())
