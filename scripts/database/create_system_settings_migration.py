#!/usr/bin/env python3
"""
Script para crear la migración de system_settings manualmente
===========================================================
Crea la tabla system_settings directamente usando SQLAlchemy
"""

import asyncio
from app.database import engine, Base
from app.models.system_setting import SystemSetting
from sqlalchemy import text


async def create_system_settings_table():
    """Crear la tabla system_settings directamente"""
    conn = None
    try:
        print("🔧 Creando tabla system_settings...")
        
        conn = await engine.begin()
        
        # Verificar si la tabla ya existe
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'system_settings'
            );
        """))
        
        table_exists = result.scalar()
        
        if table_exists:
            print("✅ La tabla system_settings ya existe")
            await conn.commit()
            return True
        
        # Crear todas las tablas desde Base.metadata
        await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tabla system_settings creada exitosamente")
        
        # Verificar que se creó correctamente
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'system_settings'
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        print(f"📋 Columnas creadas ({len(columns)}):")
        for col_name, data_type, is_nullable in columns:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"   • {col_name}: {data_type} {nullable}")
        
        await conn.commit()
        return True
            
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        if conn:
            await conn.rollback()
        return False
    finally:
        if conn:
            await conn.close()


async def main():
    """Función principal"""
    try:
        success = await create_system_settings_table()
        
        if success:
            print(f"\n✅ Tabla system_settings lista para usar")
            print(f"🚀 Ahora puede ejecutar el script de población")
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)