#!/usr/bin/env python3
"""
Script para crear la tabla incoming_product_queue en la base de datos.
Este script crea la tabla directamente sin usar migraciones de Alembic.
"""

import sys
import os
import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import de modelos
from app.models.base import BaseModel
from app.models.incoming_product_queue import IncomingProductQueue
from app.core.database import get_async_database_url

def create_table():
    """Crear la tabla incoming_product_queue en la base de datos."""
    
    # Obtener URL de conexión
    database_url = get_async_database_url()
    
    # Crear conexión síncrona para DDL operations
    sync_database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"🔗 Conectando a: {sync_database_url}")
    
    # Crear engine síncrono
    engine = create_engine(sync_database_url)
    
    try:
        print("📋 Verificando si la tabla ya existe...")
        
        # Verificar si la tabla existe
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'incoming_product_queue' in existing_tables:
            print("✅ La tabla 'incoming_product_queue' ya existe.")
            return True
        
        print("🛠️  Creando tabla 'incoming_product_queue'...")
        
        # Crear solo la tabla IncomingProductQueue
        IncomingProductQueue.__table__.create(engine, checkfirst=True)
        
        print("✅ Tabla 'incoming_product_queue' creada exitosamente!")
        
        # Verificar que se creó correctamente
        inspector = inspect(engine)
        if 'incoming_product_queue' in inspector.get_table_names():
            columns = inspector.get_columns('incoming_product_queue')
            print(f"📊 Tabla creada con {len(columns)} columnas:")
            for col in columns[:5]:  # Mostrar las primeras 5 columnas
                print(f"   - {col['name']}: {col['type']}")
            if len(columns) > 5:
                print(f"   ... y {len(columns) - 5} columnas más")
            return True
        else:
            print("❌ Error: La tabla no se creó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear la tabla: {str(e)}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("🚀 Iniciando creación de tabla incoming_product_queue...")
    success = create_table()
    
    if success:
        print("✅ Proceso completado exitosamente!")
        sys.exit(0)
    else:
        print("❌ Proceso fallido!")
        sys.exit(1)