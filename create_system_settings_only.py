#!/usr/bin/env python3
"""
Script para crear SOLO la tabla system_settings
=============================================
Crea únicamente la tabla system_settings evitando conflictos con otras tablas
"""

from app.core.config import settings
from sqlalchemy import create_engine, text


def create_system_settings_table():
    """Crear SOLO la tabla system_settings"""
    try:
        print("🔧 Creando tabla system_settings...")
        
        # Crear engine sincrónico
        sync_engine = create_engine(
            settings.DATABASE_URL.replace('asyncpg', 'psycopg2')
        )
        
        with sync_engine.connect() as conn:
            # Verificar si la tabla ya existe
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
            
            # Crear la tabla system_settings directamente con SQL
            conn.execute(text("""
                CREATE TABLE system_settings (
                    id SERIAL NOT NULL PRIMARY KEY,
                    key VARCHAR(100) NOT NULL UNIQUE,
                    value TEXT,
                    category VARCHAR(50) NOT NULL,
                    data_type VARCHAR(20) NOT NULL DEFAULT 'string',
                    description TEXT,
                    default_value TEXT,
                    is_public BOOLEAN NOT NULL DEFAULT false,
                    is_editable BOOLEAN NOT NULL DEFAULT true,
                    last_modified_by INTEGER,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    CONSTRAINT ck_system_settings_category 
                        CHECK (category IN ('general', 'email', 'business', 'security')),
                    CONSTRAINT ck_system_settings_data_type 
                        CHECK (data_type IN ('string', 'integer', 'float', 'boolean', 'json'))
                );
            """))
            
            # Crear índices para mejorar performance
            conn.execute(text("""
                CREATE INDEX ix_system_settings_category ON system_settings (category);
            """))
            
            conn.execute(text("""
                CREATE INDEX ix_system_settings_is_public ON system_settings (is_public);
            """))
            
            conn.commit()
            
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
            
            # Verificar constraints
            result = conn.execute(text("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints
                WHERE table_name = 'system_settings'
                ORDER BY constraint_type, constraint_name;
            """))
            
            constraints = result.fetchall()
            print(f"\n🔒 Constraints creados ({len(constraints)}):")
            for constraint_name, constraint_type in constraints:
                print(f"   • {constraint_name}: {constraint_type}")
            
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