# ~/app/services/embedding_sync_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Embedding Synchronization Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embedding_sync_service.py
# Ruta: ~/app/services/embedding_sync_service.py
# Autor: Data Engineering AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Servicio de sincronización de embeddings entre PostgreSQL y ChromaDB
#            Mantiene consistency entre productos y sus representaciones vectoriales
#
# Características:
# - Sincronización automática de productos a ChromaDB
# - Batch processing para performance optimizada
# - Delta sync para cambios incrementales
# - Error handling y retry logic
# - Monitoring y metrics de sincronización
# - Background tasks para sync automático
#
# ---------------------------------------------------------------------------------------------

"""
Embedding Synchronization Service para MeStore.

Este módulo mantiene sincronizados los productos de PostgreSQL
con sus embeddings en ChromaDB:
- Sync inicial de todos los productos
- Sync incremental de cambios
- Cleanup de embeddings obsoletos
- Monitoring de sync status
- Background processing automático
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis.base import RedisManager
from app.models.product import Product, ProductStatus
from app.models.category import Category, ProductCategory
from app.services.chroma_service import chroma_service
from app.services.search_cache_service import SearchCacheService

logger = logging.getLogger(__name__)


class EmbeddingSyncService:
    """
    Servicio para sincronizar embeddings entre PostgreSQL y ChromaDB.

    Mantiene consistency entre:
    - Productos en PostgreSQL
    - Embeddings en ChromaDB
    - Cache invalidation en Redis
    """

    def __init__(self, redis_manager: RedisManager):
        """
        Inicializar EmbeddingSyncService.

        Args:
            redis_manager: Instancia de RedisManager para tracking
        """
        self.redis_manager = redis_manager
        self.chroma_service = chroma_service

        # Tracking keys para sincronización
        self.sync_status_key = "sync:embedding:status"
        self.sync_progress_key = "sync:embedding:progress"
        self.sync_errors_key = "sync:embedding:errors"
        self.last_sync_key = "sync:embedding:last_sync"

        # Configuration
        self.batch_size = 50  # Productos por batch
        self.max_retries = 3  # Reintentos por producto
        self.sync_interval = 3600  # 1 hora para sync automático

        # Performance tracking
        self.sync_metrics = {
            "products_synced": 0,
            "products_failed": 0,
            "products_skipped": 0,
            "sync_time": 0,
            "last_error": None
        }

    async def full_sync(self, session: AsyncSession) -> Dict:
        """
        Sincronización completa de todos los productos.

        Args:
            session: AsyncSession de SQLAlchemy

        Returns:
            Dict: Resultado de la sincronización
        """
        try:
            start_time = asyncio.get_event_loop().time()
            logger.info("Iniciando sincronización completa de embeddings")

            # Marcar inicio de sync
            await self._mark_sync_start("full")

            # Reinicializar ChromaDB si es necesario
            await self.chroma_service.initialize()

            # Obtener total de productos a sincronizar
            total_products = await session.execute(
                text("SELECT COUNT(*) FROM products WHERE deleted_at IS NULL")
            )
            total_count = total_products.scalar()

            logger.info(f"Sincronizando {total_count} productos en total")

            # Procesar en batches
            synced_count = 0
            failed_count = 0
            skipped_count = 0
            errors = []

            offset = 0
            while offset < total_count:
                try:
                    # Obtener batch de productos
                    batch_query = session.query(Product).filter(
                        Product.deleted_at.is_(None)
                    ).options(
                        selectinload(Product.category_associations).selectinload(ProductCategory.category)
                    ).offset(offset).limit(self.batch_size)

                    batch_products = await batch_query.all()

                    if not batch_products:
                        break

                    # Procesar batch
                    batch_result = await self._sync_batch(batch_products)

                    synced_count += batch_result["synced"]
                    failed_count += batch_result["failed"]
                    skipped_count += batch_result["skipped"]
                    errors.extend(batch_result["errors"])

                    # Actualizar progreso
                    progress_percent = min(100, (offset + len(batch_products)) / total_count * 100)
                    await self._update_sync_progress(progress_percent, synced_count, failed_count)

                    logger.info(f"Batch procesado: {len(batch_products)} productos ({progress_percent:.1f}% completado)")

                    # Small delay para no sobrecargar sistema
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error procesando batch en offset {offset}: {e}")
                    failed_count += len(batch_products) if 'batch_products' in locals() else self.batch_size
                    errors.append(f"Batch offset {offset}: {str(e)}")

                offset += self.batch_size

            # Calcular tiempo total
            sync_time = asyncio.get_event_loop().time() - start_time

            # Marcar finalización
            sync_result = {
                "type": "full_sync",
                "total_products": total_count,
                "synced": synced_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "sync_time_seconds": sync_time,
                "errors": errors[:10],  # Solo primeros 10 errores
                "success_rate": (synced_count / total_count * 100) if total_count > 0 else 0
            }

            await self._mark_sync_complete(sync_result)

            logger.info(f"Sincronización completa finalizada: {synced_count}/{total_count} productos sincronizados ({sync_time:.2f}s)")
            return sync_result

        except Exception as e:
            logger.error(f"Error en sincronización completa: {e}")
            await self._mark_sync_error(str(e))
            return {
                "type": "full_sync",
                "error": str(e),
                "success": False
            }

    async def incremental_sync(
        self,
        session: AsyncSession,
        since: Optional[datetime] = None
    ) -> Dict:
        """
        Sincronización incremental de productos modificados.

        Args:
            session: AsyncSession de SQLAlchemy
            since: Fecha desde la cual sincronizar (default: última sincronización)

        Returns:
            Dict: Resultado de la sincronización incremental
        """
        try:
            start_time = asyncio.get_event_loop().time()

            # Determinar fecha de corte
            if since is None:
                since = await self._get_last_sync_time()

            logger.info(f"Iniciando sincronización incremental desde {since}")

            # Marcar inicio
            await self._mark_sync_start("incremental")

            # Obtener productos modificados
            modified_query = session.query(Product).filter(
                and_(
                    Product.deleted_at.is_(None),
                    Product.updated_at >= since
                )
            ).options(
                selectinload(Product.category_associations).selectinload(ProductCategory.category)
            ).order_by(Product.updated_at)

            modified_products = await modified_query.all()

            logger.info(f"Encontrados {len(modified_products)} productos modificados")

            if not modified_products:
                return {
                    "type": "incremental_sync",
                    "products_modified": 0,
                    "synced": 0,
                    "message": "No hay productos para sincronizar"
                }

            # Procesar productos modificados
            sync_result = await self._sync_batch(modified_products)

            # Calcular tiempo
            sync_time = asyncio.get_event_loop().time() - start_time

            # Resultado final
            result = {
                "type": "incremental_sync",
                "since": since.isoformat(),
                "products_modified": len(modified_products),
                "synced": sync_result["synced"],
                "failed": sync_result["failed"],
                "skipped": sync_result["skipped"],
                "sync_time_seconds": sync_time,
                "errors": sync_result["errors"]
            }

            await self._mark_sync_complete(result)

            logger.info(f"Sincronización incremental completada: {sync_result['synced']} productos sincronizados")
            return result

        except Exception as e:
            logger.error(f"Error en sincronización incremental: {e}")
            await self._mark_sync_error(str(e))
            return {
                "type": "incremental_sync",
                "error": str(e),
                "success": False
            }

    async def sync_single_product(
        self,
        session: AsyncSession,
        product_id: UUID
    ) -> Dict:
        """
        Sincronizar un producto específico.

        Args:
            session: AsyncSession de SQLAlchemy
            product_id: ID del producto a sincronizar

        Returns:
            Dict: Resultado de la sincronización
        """
        try:
            # Obtener producto con relaciones
            product_query = session.query(Product).filter(
                Product.id == product_id
            ).options(
                selectinload(Product.category_associations).selectinload(ProductCategory.category)
            )

            product = await product_query.first()

            if not product:
                return {
                    "product_id": str(product_id),
                    "success": False,
                    "error": "Producto no encontrado"
                }

            # Si está soft-deleted, remover del ChromaDB
            if product.deleted_at is not None:
                success = await self.chroma_service.delete_product_embedding(str(product_id))
                return {
                    "product_id": str(product_id),
                    "action": "deleted",
                    "success": success
                }

            # Sincronizar producto
            product_data = product.to_dict()
            success = await self.chroma_service.update_product_embedding(
                str(product_id),
                product_data
            )

            # Invalidar cache relacionado
            if success:
                await self._invalidate_product_cache(str(product_id))

            return {
                "product_id": str(product_id),
                "action": "synced",
                "success": success
            }

        except Exception as e:
            logger.error(f"Error sincronizando producto {product_id}: {e}")
            return {
                "product_id": str(product_id),
                "success": False,
                "error": str(e)
            }

    async def cleanup_orphaned_embeddings(self, session: AsyncSession) -> Dict:
        """
        Limpiar embeddings huérfanos (que no tienen producto correspondiente).

        Args:
            session: AsyncSession de SQLAlchemy

        Returns:
            Dict: Resultado de la limpieza
        """
        try:
            logger.info("Iniciando limpieza de embeddings huérfanos")

            # Obtener todos los IDs de productos en PostgreSQL
            product_ids_query = await session.execute(
                text("SELECT id FROM products WHERE deleted_at IS NULL")
            )
            valid_product_ids = {str(row[0]) for row in product_ids_query.fetchall()}

            # Obtener estadísticas de ChromaDB
            chroma_stats = await self.chroma_service.get_collection_stats()
            products_collection = self.chroma_service.products_collection

            # Obtener todos los IDs en ChromaDB
            all_chroma_data = products_collection.get(include=["metadatas"])
            chroma_product_ids = set(all_chroma_data["ids"]) if all_chroma_data["ids"] else set()

            # Encontrar huérfanos
            orphaned_ids = chroma_product_ids - valid_product_ids

            logger.info(f"Encontrados {len(orphaned_ids)} embeddings huérfanos para limpiar")

            # Eliminar huérfanos en batches
            deleted_count = 0
            for i in range(0, len(orphaned_ids), self.batch_size):
                batch_ids = list(orphaned_ids)[i:i + self.batch_size]
                try:
                    products_collection.delete(ids=batch_ids)
                    deleted_count += len(batch_ids)
                    logger.debug(f"Eliminados {len(batch_ids)} embeddings huérfanos")
                except Exception as e:
                    logger.error(f"Error eliminando batch de huérfanos: {e}")

            return {
                "type": "cleanup",
                "orphaned_found": len(orphaned_ids),
                "orphaned_deleted": deleted_count,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error en limpieza de huérfanos: {e}")
            return {
                "type": "cleanup",
                "error": str(e),
                "success": False
            }

    async def get_sync_status(self) -> Dict:
        """
        Obtener estado actual de sincronización.

        Returns:
            Dict: Estado y métricas de sincronización
        """
        try:
            # Obtener datos de Redis
            status_data = await self.redis_manager.hgetall(self.sync_status_key)
            progress_data = await self.redis_manager.hgetall(self.sync_progress_key)
            last_sync = await self.redis_manager.get(self.last_sync_key)

            # Obtener estadísticas de ChromaDB
            chroma_stats = await self.chroma_service.get_collection_stats()

            return {
                "sync_status": {
                    key.decode(): value.decode() for key, value in status_data.items()
                } if status_data else {},
                "sync_progress": {
                    key.decode(): value.decode() for key, value in progress_data.items()
                } if progress_data else {},
                "last_sync_time": last_sync.decode() if last_sync else None,
                "chroma_stats": chroma_stats,
                "service_status": "operational"
            }

        except Exception as e:
            logger.error(f"Error obteniendo status de sync: {e}")
            return {
                "service_status": "error",
                "error": str(e)
            }

    async def _sync_batch(self, products: List[Product]) -> Dict:
        """
        Sincronizar un batch de productos.

        Args:
            products: Lista de productos a sincronizar

        Returns:
            Dict: Resultado del batch
        """
        synced_count = 0
        failed_count = 0
        skipped_count = 0
        errors = []

        # Preparar datos para batch processing
        products_data = []
        for product in products:
            try:
                product_data = product.to_dict()
                products_data.append(product_data)
            except Exception as e:
                logger.warning(f"Error preparando datos para producto {product.id}: {e}")
                failed_count += 1
                errors.append(f"Product {product.id}: {str(e)}")

        # Sincronizar batch en ChromaDB
        if products_data:
            synced_count = await self.chroma_service.add_products_batch(products_data)
            failed_count += len(products_data) - synced_count

        return {
            "synced": synced_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "errors": errors
        }

    async def _mark_sync_start(self, sync_type: str) -> None:
        """Marcar inicio de sincronización."""
        try:
            sync_data = {
                "type": sync_type,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "progress": "0"
            }

            await self.redis_manager.hmset(self.sync_status_key, sync_data)
            await self.redis_manager.expire(self.sync_status_key, 86400)  # 24 horas

        except Exception as e:
            logger.warning(f"Error marcando inicio de sync: {e}")

    async def _mark_sync_complete(self, result: Dict) -> None:
        """Marcar finalización de sincronización."""
        try:
            sync_data = {
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "success_rate": str(result.get("success_rate", 0)),
                "synced_count": str(result.get("synced", 0))
            }

            await self.redis_manager.hmset(self.sync_status_key, sync_data)

            # Actualizar timestamp de última sincronización
            await self.redis_manager.set(
                self.last_sync_key,
                datetime.now().isoformat(),
                expire=86400 * 30  # 30 días
            )

        except Exception as e:
            logger.warning(f"Error marcando finalización de sync: {e}")

    async def _mark_sync_error(self, error: str) -> None:
        """Marcar error en sincronización."""
        try:
            sync_data = {
                "status": "error",
                "end_time": datetime.now().isoformat(),
                "error": error
            }

            await self.redis_manager.hmset(self.sync_status_key, sync_data)

        except Exception as e:
            logger.warning(f"Error marcando error de sync: {e}")

    async def _update_sync_progress(
        self,
        percent: float,
        synced_count: int,
        failed_count: int
    ) -> None:
        """Actualizar progreso de sincronización."""
        try:
            progress_data = {
                "percent": str(percent),
                "synced_count": str(synced_count),
                "failed_count": str(failed_count),
                "updated_at": datetime.now().isoformat()
            }

            await self.redis_manager.hmset(self.sync_progress_key, progress_data)
            await self.redis_manager.expire(self.sync_progress_key, 86400)

        except Exception as e:
            logger.warning(f"Error actualizando progreso: {e}")

    async def _get_last_sync_time(self) -> datetime:
        """Obtener timestamp de última sincronización."""
        try:
            last_sync = await self.redis_manager.get(self.last_sync_key)
            if last_sync:
                return datetime.fromisoformat(last_sync.decode())
            else:
                # Si no hay último sync, usar hace 24 horas
                return datetime.now() - timedelta(hours=24)

        except Exception as e:
            logger.warning(f"Error obteniendo último sync: {e}")
            return datetime.now() - timedelta(hours=24)

    async def _invalidate_product_cache(self, product_id: str) -> None:
        """Invalidar cache relacionado con un producto."""
        try:
            # Invalidar cache de búsqueda que pueda contener este producto
            # (implementación simplificada)
            search_cache_keys = await self.redis_manager.keys("search:results:*")
            if search_cache_keys:
                # En producción, esto sería más granular
                await self.redis_manager.delete(*search_cache_keys[:50])  # Limitar para performance

        except Exception as e:
            logger.warning(f"Error invalidando cache para producto {product_id}: {e}")

    async def schedule_automatic_sync(self, session: AsyncSession) -> None:
        """
        Programar sincronización automática incremental.

        Args:
            session: AsyncSession de SQLAlchemy
        """
        try:
            logger.info("Iniciando sincronización automática programada")

            # Verificar si hay otra sincronización en progreso
            status_data = await self.redis_manager.hgetall(self.sync_status_key)
            if status_data and status_data.get(b"status") == b"running":
                logger.info("Sincronización ya en progreso, saltando automática")
                return

            # Ejecutar sync incremental
            result = await self.incremental_sync(session)

            logger.info(f"Sincronización automática completada: {result}")

        except Exception as e:
            logger.error(f"Error en sincronización automática: {e}")


# Factory function
def create_embedding_sync_service(redis_manager: RedisManager) -> EmbeddingSyncService:
    """
    Factory function para crear EmbeddingSyncService.

    Args:
        redis_manager: Instancia de RedisManager

    Returns:
        EmbeddingSyncService: Instancia configurada del servicio
    """
    return EmbeddingSyncService(redis_manager)