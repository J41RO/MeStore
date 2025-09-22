#!/usr/bin/env python3
"""
Script sincrónico para crear la tabla system_settings
===================================================
Crea la tabla system_settings usando SQLAlchemy sincrónico
"""

from app.models.system_setting import SystemSetting
from app.database import Base
from app.core.config import settings
from sqlalchemy import create_engine, text


def create_system_settings_table():
    """Crear la tabla system_settings usando SQLAlchemy sincrónico"""
    try:
        print("🔧 Creando tabla system_settings...")
        
        # Crear engine sincrónico
        sync_engine = create_engine(
            settings.DATABASE_URL.replace('asyncpg', 'psycopg2')
        )
        
        # Verificar si la tabla ya existe
        with sync_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'system_settings'
                );
            """))
            
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ La tabla system_settings ya existe")
                return True
            
            # Crear todas las tablas desde Base.metadata
            Base.metadata.create_all(sync_engine)
            
            print("✅ Tabla system_settings creada exitosamente")
            
            # Verificar que se creó correctamente
            result = conn.execute(text("""
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
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        return False


def main():
    """Función principal"""
    try:
        success = create_system_settings_table()
        
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
    exit_code = main()
    exit(exit_code)