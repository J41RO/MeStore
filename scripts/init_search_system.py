#!/usr/bin/env python3
# ~/scripts/init_search_system.py
# ---------------------------------------------------------------------------------------------
# MeStore - Search System Initialization Script
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: init_search_system.py
# Ruta: ~/scripts/init_search_system.py
# Autor: Data Engineering AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Script de inicialización del sistema de búsqueda avanzada
#            Configura ChromaDB, sincroniza embeddings iniciales y ejecuta tests
#
# Uso: python scripts/init_search_system.py [--full-sync] [--reset-chroma] [--test]
#
# ---------------------------------------------------------------------------------------------

"""
Script de inicialización del sistema de búsqueda avanzada.

Este script:
- Inicializa ChromaDB y carga modelos de embeddings
- Ejecuta sincronización inicial de productos
- Configura índices de base de datos
- Realiza tests básicos del sistema
- Genera reporte de estado
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.redis.base import RedisManager
from app.services.chroma_service import chroma_service
from app.services.search_service import create_search_service, SearchFilters
from app.services.search_cache_service import create_search_cache_service
from app.services.embedding_sync_service import create_embedding_sync_service
from app.services.search_analytics_service import create_search_analytics_service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchSystemInitializer:
    """
    Inicializador del sistema de búsqueda avanzada.
    """

    def __init__(self):
        """Inicializar configuración."""
        self.engine = None
        self.async_session = None
        self.redis_manager = None

    async def setup_connections(self):
        """Configurar conexiones a base de datos y Redis."""
        try:
            logger.info("🔌 Configurando conexiones...")

            # PostgreSQL/SQLite connection
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                future=True
            )

            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Redis connection
            self.redis_manager = RedisManager(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_CACHE_DB,
                password=None  # Update if needed
            )

            await self.redis_manager.connect()

            logger.info("✅ Conexiones configuradas correctamente")

        except Exception as e:
            logger.error(f"❌ Error configurando conexiones: {e}")
            raise

    async def initialize_chromadb(self, reset: bool = False):
        """
        Inicializar ChromaDB con modelos de embeddings.

        Args:
            reset: Si resetear collections existentes
        """
        try:
            logger.info("🧠 Inicializando ChromaDB...")

            if reset:
                logger.warning("⚠️  Reseteando collections de ChromaDB")
                await chroma_service.reset_collections()

            # Inicializar service
            await chroma_service.initialize()

            # Verificar estadísticas
            stats = await chroma_service.get_collection_stats()
            logger.info(f"📊 ChromaDB stats: {stats}")

            logger.info("✅ ChromaDB inicializado correctamente")

        except Exception as e:
            logger.error(f"❌ Error inicializando ChromaDB: {e}")
            raise

    async def sync_products_to_embeddings(self, full_sync: bool = False):
        """
        Sincronizar productos a embeddings.

        Args:
            full_sync: Si hacer sincronización completa o incremental
        """
        try:
            logger.info("🔄 Iniciando sincronización de productos...")

            sync_service = create_embedding_sync_service(self.redis_manager)

            async with self.async_session() as session:
                if full_sync:
                    result = await sync_service.full_sync(session)
                else:
                    result = await sync_service.incremental_sync(session)

                logger.info(f"📈 Resultado de sincronización: {result}")

                # Cleanup de embeddings huérfanos
                cleanup_result = await sync_service.cleanup_orphaned_embeddings(session)
                logger.info(f"🧹 Cleanup result: {cleanup_result}")

        except Exception as e:
            logger.error(f"❌ Error en sincronización: {e}")
            raise

    async def run_search_tests(self):
        """Ejecutar tests básicos del sistema de búsqueda."""
        try:
            logger.info("🧪 Ejecutando tests del sistema de búsqueda...")

            search_service = create_search_service(self.redis_manager)
            cache_service = create_search_cache_service(self.redis_manager)

            async with self.async_session() as session:
                # Test 1: Búsqueda básica
                logger.info("Test 1: Búsqueda básica")
                filters = SearchFilters(query="laptop")
                results = await search_service.search_products(session, filters, page=1, page_size=5)
                logger.info(f"✅ Búsqueda básica: {results['pagination']['total_count']} resultados")

                # Test 2: Búsqueda con filtros
                logger.info("Test 2: Búsqueda con filtros")
                filters = SearchFilters(
                    query="celular",
                    price_max=1000,
                    has_stock=True
                )
                results = await search_service.search_products(session, filters, page=1, page_size=5)
                logger.info(f"✅ Búsqueda con filtros: {results['pagination']['total_count']} resultados")

                # Test 3: Autocomplete
                logger.info("Test 3: Autocomplete")
                suggestions = await search_service.get_autocomplete_suggestions(
                    session, "lap", limit=5
                )
                logger.info(f"✅ Autocomplete: {len(suggestions)} sugerencias")

                # Test 4: Analytics
                logger.info("Test 4: Analytics")
                analytics = await search_service.get_search_analytics(days=7)
                logger.info(f"✅ Analytics: {analytics.get('total_searches', 0)} búsquedas en 7 días")

                # Test 5: Cache
                logger.info("Test 5: Cache")
                cache_metrics = await cache_service.get_cache_metrics()
                logger.info(f"✅ Cache metrics: {cache_metrics}")

            logger.info("✅ Todos los tests completados exitosamente")

        except Exception as e:
            logger.error(f"❌ Error en tests: {e}")
            raise

    async def generate_status_report(self):
        """Generar reporte de estado del sistema."""
        try:
            logger.info("📋 Generando reporte de estado...")

            # ChromaDB stats
            chroma_stats = await chroma_service.get_collection_stats()

            # Search service status
            search_service = create_search_service(self.redis_manager)
            cache_service = create_search_cache_service(self.redis_manager)
            sync_service = create_embedding_sync_service(self.redis_manager)

            cache_metrics = await cache_service.get_cache_metrics()
            sync_status = await sync_service.get_sync_status()

            # Generar reporte
            report = {
                "system_status": "operational",
                "timestamp": str(asyncio.get_event_loop().time()),
                "chromadb": chroma_stats,
                "cache_metrics": cache_metrics,
                "sync_status": sync_status,
                "components": {
                    "postgresql": "connected",
                    "redis": "connected",
                    "chromadb": "initialized",
                    "embeddings_model": "loaded"
                }
            }

            logger.info("📊 Reporte de estado:")
            for key, value in report.items():
                if isinstance(value, dict):
                    logger.info(f"  {key}:")
                    for subkey, subvalue in value.items():
                        logger.info(f"    {subkey}: {subvalue}")
                else:
                    logger.info(f"  {key}: {value}")

            return report

        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return {"system_status": "error", "error": str(e)}

    async def cleanup_connections(self):
        """Limpiar conexiones."""
        try:
            if self.redis_manager:
                await self.redis_manager.disconnect()

            if self.engine:
                await self.engine.dispose()

            logger.info("🧹 Conexiones limpiadas")

        except Exception as e:
            logger.warning(f"⚠️ Error limpiando conexiones: {e}")


async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Inicializar sistema de búsqueda avanzada")
    parser.add_argument("--full-sync", action="store_true", help="Ejecutar sincronización completa")
    parser.add_argument("--reset-chroma", action="store_true", help="Resetear collections de ChromaDB")
    parser.add_argument("--test", action="store_true", help="Ejecutar tests del sistema")
    parser.add_argument("--skip-sync", action="store_true", help="Saltar sincronización de productos")

    args = parser.parse_args()

    initializer = SearchSystemInitializer()

    try:
        logger.info("🚀 Iniciando configuración del sistema de búsqueda avanzada...")

        # 1. Configurar conexiones
        await initializer.setup_connections()

        # 2. Inicializar ChromaDB
        await initializer.initialize_chromadb(reset=args.reset_chroma)

        # 3. Sincronizar productos (opcional)
        if not args.skip_sync:
            await initializer.sync_products_to_embeddings(full_sync=args.full_sync)

        # 4. Ejecutar tests (opcional)
        if args.test:
            await initializer.run_search_tests()

        # 5. Generar reporte de estado
        report = await initializer.generate_status_report()

        logger.info("🎉 Inicialización completada exitosamente!")
        logger.info("🔍 Sistema de búsqueda avanzada listo para usar")

        return 0

    except Exception as e:
        logger.error(f"💥 Error en inicialización: {e}")
        return 1

    finally:
        await initializer.cleanup_connections()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)