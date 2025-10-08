#!/usr/bin/env python3
"""
Script de migración manual para agregar columna account_status.

Este script es un backup por si Alembic falla en producción.
Es idempotente - se puede ejecutar múltiples veces sin problemas.

Uso:
    python scripts/add_account_status.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_account_status_column():
    """
    Agrega columna account_status a la tabla users.

    Pasos:
    1. Verifica si la columna ya existe
    2. Crea el enum type AccountStatus (solo PostgreSQL)
    3. Agrega la columna si no existe
    4. Actualiza usuarios existentes:
       - SUPERUSER → 'active'
       - email_verified=True → 'active'
       - Otros → 'pending'
    """
    try:
        logger.info("🚀 Iniciando migración de account_status...")

        # Crear engine
        engine = create_engine(settings.DATABASE_URL)
        db_type = engine.dialect.name
        logger.info(f"📊 Database type: {db_type}")

        # Verificar si la columna ya existe
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'account_status' in columns:
            logger.info("✅ La columna account_status ya existe")

            # Actualizar usuarios existentes
            with engine.connect() as conn:
                result = conn.execute(text("""
                    UPDATE users
                    SET account_status = 'active'
                    WHERE (email_verified = 1 OR user_type = 'SUPERUSER')
                    AND account_status = 'pending'
                """))
                conn.commit()
                logger.info(f"✅ {result.rowcount} usuarios actualizados a 'active'")

            return True

        logger.info("📝 La columna account_status no existe, agregándola...")

        with engine.connect() as conn:
            if db_type == 'postgresql':
                # PostgreSQL: Crear ENUM type
                logger.info("🔧 PostgreSQL: Creando ENUM type...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE accountstatus AS ENUM ('pending', 'active', 'suspended', 'deleted');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))

                # Agregar columna con ENUM
                conn.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS account_status accountstatus
                    NOT NULL DEFAULT 'pending';
                """))

            elif db_type == 'sqlite':
                # SQLite: Usar VARCHAR con CHECK constraint
                logger.info("🔧 SQLite: Creando columna VARCHAR...")
                conn.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN account_status VARCHAR(9)
                    NOT NULL DEFAULT 'pending'
                    CHECK (account_status IN ('pending', 'active', 'suspended', 'deleted'));
                """))

            else:
                # MySQL u otros: Usar VARCHAR
                logger.info(f"🔧 {db_type}: Creando columna VARCHAR...")
                conn.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN account_status VARCHAR(9)
                    NOT NULL DEFAULT 'pending';
                """))

            # Actualizar usuarios existentes
            logger.info("📊 Actualizando usuarios existentes...")

            # SUPERUSER y usuarios verificados → 'active'
            result = conn.execute(text("""
                UPDATE users
                SET account_status = 'active'
                WHERE email_verified = 1 OR user_type = 'SUPERUSER'
            """))

            conn.commit()
            logger.info(f"✅ {result.rowcount} usuarios actualizados a 'active'")

        logger.info("✅ Migración completada exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error en migración: {str(e)}")
        raise


if __name__ == '__main__':
    try:
        add_account_status_column()
        logger.info("🎉 Script ejecutado exitosamente")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Fallo en ejecución: {str(e)}")
        sys.exit(1)
