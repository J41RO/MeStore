# ~/app/utils/database_utils.py
# ---------------------------------------------------------------------------------------------
# MeStore - Database Utilities (Async Optimizado)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Database Utilities - Utilidades para inicialización y testing de base de datos

Características:
- Inicialización completa de DB con creación de tablas
- Testing de conectividad async
- Validación de schema y estructura
- Health checks robustos para monitoring
- Support para diferentes entornos (dev/test/prod)
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine, AsyncSessionLocal, Base
from app.models import user  # Import para registrar modelos


logger = logging.getLogger(__name__)


async def init_database() -> Dict[str, Any]:
    """
    Inicializar base de datos creando todas las tablas.

    Returns:
        Dict con status de inicialización y detalles
    """
    try:
        logger.info('Iniciando creación de tablas de base de datos')

        async with engine.begin() as conn:
            # Crear todas las tablas definidas en los modelos
            await conn.run_sync(Base.metadata.create_all)

            # Obtener lista de tablas creadas
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]

        logger.info(f'Base de datos inicializada exitosamente. Tablas: {tables}')

        return {
            'status': 'success',
            'message': 'Base de datos inicializada correctamente',
            'tables_created': tables,
            'total_tables': len(tables)
        }

    except Exception as e:
        logger.error(f'Error inicializando base de datos: {e}')
        return {
            'status': 'error',
            'message': f'Error en inicialización: {str(e)}',
            'tables_created': [],
            'total_tables': 0
        }


async def test_connection() -> Dict[str, Any]:
    """
    Probar conectividad async con la base de datos.

    Returns:
        Dict con resultado del test de conexión
    """
    start_time = asyncio.get_event_loop().time()

    try:
        async with AsyncSessionLocal() as session:
            # Test básico de conectividad
            result = await session.execute(text('SELECT 1 as test_connection'))
            test_value = result.scalar()

            # Test de version de PostgreSQL
            version_result = await session.execute(text('SELECT version()'))
            db_version = version_result.scalar()

            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)  # ms

            logger.info(f'Test de conexión exitoso en {response_time}ms')

            return {
                'status': 'success',
                'connection_active': test_value == 1,
                'response_time_ms': response_time,
                'database_version': db_version.split(' ')[1] if db_version else 'unknown',
                'engine_info': str(engine.url).replace(engine.url.password or '', '***')
            }

    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        response_time = round((end_time - start_time) * 1000, 2)

        logger.error(f'Error en test de conexión: {e}')

        return {
            'status': 'error',
            'connection_active': False,
            'response_time_ms': response_time,
            'error_message': str(e),
            'error_type': type(e).__name__
        }


async def validate_schema() -> Dict[str, Any]:
    """
    Validar estructura del schema de base de datos.

    Returns:
        Dict con resultado de validación de schema
    """
    try:
        async with engine.begin() as conn:
            # Obtener información de tablas
            tables_result = await conn.execute(text("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """))

            schema_info = {}
            for row in tables_result.fetchall():
                table_name, column_name, data_type, is_nullable = row
                if table_name not in schema_info:
                    schema_info[table_name] = []
                schema_info[table_name].append({
                    'column': column_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                })

            # Validar que existan tablas esperadas
            expected_tables = ['users']  # Agregar más según modelos
            missing_tables = [t for t in expected_tables if t not in schema_info]

            logger.info(f'Validación de schema completada. Tablas: {list(schema_info.keys())}')

            return {
                'status': 'success',
                'tables_found': list(schema_info.keys()),
                'schema_details': schema_info,
                'missing_tables': missing_tables,
                'validation_passed': len(missing_tables) == 0
            }

    except Exception as e:
        logger.error(f'Error validando schema: {e}')
        return {
            'status': 'error',
            'error_message': str(e),
            'validation_passed': False
        }


async def health_check_database() -> Dict[str, Any]:
    """
    Health check completo de base de datos para monitoring.

    Returns:
        Dict con status completo de salud de la DB
    """
    health_data = {
        'timestamp': asyncio.get_event_loop().time(),
        'checks': {}
    }

    # Check 1: Conectividad básica
    connection_result = await test_connection()
    health_data['checks']['connection'] = {
        'status': connection_result['status'],
        'response_time_ms': connection_result.get('response_time_ms', 0)
    }

    # Check 2: Validación de schema
    schema_result = await validate_schema()
    health_data['checks']['schema'] = {
        'status': schema_result['status'],
        'tables_count': len(schema_result.get('tables_found', []))
    }

    # Check 3: Test de escritura (crear y eliminar registro temporal)
    try:
        async with AsyncSessionLocal() as session:
            # Test simple de escritura en una tabla temporal
            await session.execute(text('CREATE TEMP TABLE health_test (id INTEGER)'))
            await session.execute(text('INSERT INTO health_test (id) VALUES (1)'))
            result = await session.execute(text('SELECT id FROM health_test WHERE id = 1'))
            test_success = result.scalar() == 1
            await session.commit()

            health_data['checks']['write_operations'] = {
                'status': 'success' if test_success else 'error',
                'can_write': test_success
            }

    except Exception as e:
        health_data['checks']['write_operations'] = {
            'status': 'error',
            'error_message': str(e)
        }

    # Determinar status general
    all_checks_passed = all(
        check.get('status') == 'success' 
        for check in health_data['checks'].values()
    )

    health_data['overall_status'] = 'healthy' if all_checks_passed else 'unhealthy'

    logger.info(f'Health check completado. Status: {health_data["overall_status"]}')

    return health_data


async def validate_schema() -> Dict[str, Any]:
    """
    Validar estructura del schema de base de datos.

    Returns:
        Dict con resultado de validación de schema
    """
    try:
        async with engine.begin() as conn:
            # Obtener información de tablas
            tables_result = await conn.execute(text("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """))

            schema_info = {}
            for row in tables_result.fetchall():
                table_name, column_name, data_type, is_nullable = row
                if table_name not in schema_info:
                    schema_info[table_name] = []
                schema_info[table_name].append({
                    'column': column_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                })

            # Validar que existan tablas esperadas
            expected_tables = ['users']  # Agregar más según modelos
            missing_tables = [t for t in expected_tables if t not in schema_info]

            logger.info(f'Validación de schema completada. Tablas: {list(schema_info.keys())}')

            return {
                'status': 'success',
                'tables_found': list(schema_info.keys()),
                'schema_details': schema_info,
                'missing_tables': missing_tables,
                'validation_passed': len(missing_tables) == 0
            }

    except Exception as e:
        logger.error(f'Error validando schema: {e}')
        return {
            'status': 'error',
            'error_message': str(e),
            'validation_passed': False
        }


async def health_check_database() -> Dict[str, Any]:
    """
    Health check completo de base de datos para monitoring.

    Returns:
        Dict con status completo de salud de la DB
    """
    health_data = {
        'timestamp': asyncio.get_event_loop().time(),
        'checks': {}
    }

    # Check 1: Conectividad básica
    connection_result = await test_connection()
    health_data['checks']['connection'] = {
        'status': connection_result['status'],
        'response_time_ms': connection_result.get('response_time_ms', 0)
    }

    # Check 2: Validación de schema
    schema_result = await validate_schema()
    health_data['checks']['schema'] = {
        'status': schema_result['status'],
        'tables_count': len(schema_result.get('tables_found', []))
    }

    # Check 3: Test de escritura (crear y eliminar registro temporal)
    try:
        async with AsyncSessionLocal() as session:
            # Test simple de escritura en una tabla temporal
            await session.execute(text('CREATE TEMP TABLE health_test (id INTEGER)'))
            await session.execute(text('INSERT INTO health_test (id) VALUES (1)'))
            result = await session.execute(text('SELECT id FROM health_test WHERE id = 1'))
            test_success = result.scalar() == 1
            await session.commit()

            health_data['checks']['write_operations'] = {
                'status': 'success' if test_success else 'error',
                'can_write': test_success
            }

    except Exception as e:
        health_data['checks']['write_operations'] = {
            'status': 'error',
            'error_message': str(e)
        }

    # Determinar status general
    all_checks_passed = all(
        check.get('status') == 'success' 
        for check in health_data['checks'].values()
    )

    health_data['overall_status'] = 'healthy' if all_checks_passed else 'unhealthy'

    logger.info(f'Health check completado. Status: {health_data["overall_status"]}')

    return health_data