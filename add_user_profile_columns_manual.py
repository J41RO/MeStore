#!/usr/bin/env python3
"""
Migración manual para agregar columnas faltantes al modelo User.
"""

import asyncpg
import asyncio
from app.core.config import settings

async def add_missing_user_columns():
    """Agregar columnas faltantes a la tabla users."""
    
    # Conectar a la base de datos
    conn = await asyncpg.connect(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
    
    try:
        # Lista de columnas que faltan según el test
        missing_columns = [
            "business_description TEXT",
            "business_name VARCHAR(200)",
            "notification_preferences JSON DEFAULT '{}'::json",
            "business_hours JSON DEFAULT '{}'::json",
            "shipping_policy TEXT",
            "bank_name VARCHAR(100)",
            "social_media_links JSON DEFAULT '{}'::json",
            "website_url VARCHAR(500)",
            "avatar_url VARCHAR(500)",
            "account_holder_name VARCHAR(200)",
            "return_policy TEXT",
            "account_number VARCHAR(50)"
        ]
        
        print("🔧 Verificando columnas existentes...")
        
        # Verificar qué columnas ya existen
        existing_columns = await conn.fetch('''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND table_schema = 'public'
        ''')
        existing_column_names = {row['column_name'] for row in existing_columns}
        
        print(f"✅ Columnas existentes: {len(existing_column_names)}")
        
        # Agregar solo las columnas que realmente faltan
        for column_def in missing_columns:
            column_name = column_def.split()[0]
            
            if column_name not in existing_column_names:
                print(f"➕ Agregando columna: {column_name}")
                try:
                    await conn.execute(f'ALTER TABLE users ADD COLUMN {column_def}')
                    print(f"✅ Columna {column_name} agregada exitosamente")
                except Exception as e:
                    print(f"❌ Error agregando {column_name}: {e}")
            else:
                print(f"⏩ Columna {column_name} ya existe")
        
        print("\n🎉 Migración completada!")
        
        # Verificar resultado final
        final_columns = await conn.fetch('''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND table_schema = 'public'
        ''')
        print(f"✅ Total columnas después: {len(final_columns)}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_missing_user_columns())