# ~/app/services/chroma_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - ChromaDB Vector Search Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: chroma_service.py
# Ruta: ~/app/services/chroma_service.py
# Autor: Data Engineering AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Servicio para gestión de embeddings y búsqueda vectorial con ChromaDB
#            Soporte para búsqueda semántica de productos del marketplace
#
# Características:
# - Gestión de embeddings con sentence-transformers optimizados para español
# - ChromaDB collection management para productos
# - Búsqueda por similitud semántica con scoring
# - Batch processing para embedding generation
# - Integration con sistema de categorías jerárquicas
# - Performance optimization con caching y indexing
#
# ---------------------------------------------------------------------------------------------

"""
ChromaDB Vector Search Service para MeStore.

Este módulo proporciona funcionalidades de búsqueda semántica:
- Generación de embeddings para productos (nombre + descripción)
- Búsqueda por similitud en espacio vectorial
- Gestión de colecciones ChromaDB
- Sincronización de datos con PostgreSQL
- Performance optimization y caching
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models.product import Product
from app.models.category import Category

logger = logging.getLogger(__name__)


class ChromaDBService:
    """
    Servicio para gestión de embeddings y búsqueda vectorial con ChromaDB.

    Proporciona funcionalidades de:
    - Embedding generation con modelos optimizados para español
    - Vector similarity search para productos
    - Collection management y data synchronization
    - Performance optimization con batch processing
    """

    def __init__(self):
        """
        Inicializar ChromaDB service con configuración optimizada.
        """
        # ChromaDB client configuration
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Sentence transformer model optimizado para español
        self.embedding_model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.embedding_model = None
        self.embedding_dimension = 768  # Dimension del modelo mpnet

        # Collection names
        self.products_collection_name = "products_embeddings"
        self.categories_collection_name = "categories_embeddings"

        # Collections
        self.products_collection = None
        self.categories_collection = None

        # Performance settings
        self.batch_size = 50  # Batch size para embedding generation
        self.max_results = 20  # Máximo resultados por búsqueda

        # Cache para embeddings frecuentes
        self._embedding_cache = {}
        self._cache_max_size = 1000

    async def initialize(self) -> None:
        """
        Inicializar service: cargar modelo y crear collections.
        """
        try:
            logger.info("Inicializando ChromaDB service...")

            # Cargar modelo de embeddings
            await self._load_embedding_model()

            # Inicializar collections
            await self._initialize_collections()

            logger.info("ChromaDB service inicializado correctamente")

        except Exception as e:
            logger.error(f"Error inicializando ChromaDB service: {e}")
            raise

    async def _load_embedding_model(self) -> None:
        """
        Cargar modelo de sentence transformers para embeddings.
        """
        try:
            logger.info(f"Cargando modelo de embeddings: {self.embedding_model_name}")

            # Cargar en thread separado para no bloquear
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(
                None,
                lambda: SentenceTransformer(self.embedding_model_name)
            )

            logger.info("Modelo de embeddings cargado correctamente")

        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {e}")
            raise

    async def _initialize_collections(self) -> None:
        """
        Inicializar collections de ChromaDB para productos y categorías.
        """
        try:
            # Products collection
            self.products_collection = self.client.get_or_create_collection(
                name=self.products_collection_name,
                metadata={
                    "description": "Embeddings de productos para búsqueda semántica",
                    "model": self.embedding_model_name,
                    "dimension": self.embedding_dimension,
                    "created_at": str(asyncio.get_event_loop().time())
                }
            )

            # Categories collection
            self.categories_collection = self.client.get_or_create_collection(
                name=self.categories_collection_name,
                metadata={
                    "description": "Embeddings de categorías para búsqueda jerárquica",
                    "model": self.embedding_model_name,
                    "dimension": self.embedding_dimension,
                    "created_at": str(asyncio.get_event_loop().time())
                }
            )

            logger.info(f"Collections inicializadas: {self.products_collection_name}, {self.categories_collection_name}")

        except Exception as e:
            logger.error(f"Error inicializando collections: {e}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generar embeddings para lista de textos.

        Args:
            texts: Lista de textos para convertir a embeddings

        Returns:
            List[List[float]]: Lista de embeddings como vectores
        """
        try:
            if not texts:
                return []

            # Check cache primero
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []

            for i, text in enumerate(texts):
                text_hash = hash(text)
                if text_hash in self._embedding_cache:
                    cached_embeddings.append((i, self._embedding_cache[text_hash]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)

            # Generar embeddings para textos no cacheados
            new_embeddings = []
            if uncached_texts:
                loop = asyncio.get_event_loop()
                new_embeddings = await loop.run_in_executor(
                    None,
                    lambda: self.embedding_model.encode(
                        uncached_texts,
                        convert_to_tensor=False,
                        show_progress_bar=False
                    ).tolist()
                )

                # Cache nuevos embeddings
                for text, embedding in zip(uncached_texts, new_embeddings):
                    text_hash = hash(text)
                    if len(self._embedding_cache) < self._cache_max_size:
                        self._embedding_cache[text_hash] = embedding

            # Combinar cached y new embeddings en orden correcto
            all_embeddings = [None] * len(texts)

            # Agregar cached embeddings
            for original_index, embedding in cached_embeddings:
                all_embeddings[original_index] = embedding

            # Agregar new embeddings
            for i, original_index in enumerate(uncached_indices):
                all_embeddings[original_index] = new_embeddings[i]

            return all_embeddings

        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            raise

    async def add_product_embedding(
        self,
        product_id: str,
        product_data: Dict
    ) -> bool:
        """
        Agregar embedding de producto a ChromaDB.

        Args:
            product_id: ID único del producto
            product_data: Datos del producto (name, description, category, etc.)

        Returns:
            bool: True si se agregó correctamente
        """
        try:
            # Generar texto combinado para embedding
            combined_text = self._create_product_text(product_data)

            # Generar embedding
            embeddings = await self.generate_embeddings([combined_text])
            if not embeddings:
                return False

            # Metadata para filtros y búsqueda
            metadata = {
                "product_id": product_id,
                "name": product_data.get("name", ""),
                "category": product_data.get("categoria", ""),
                "primary_category_id": product_data.get("primary_category_id", ""),
                "price": float(product_data.get("precio_venta", 0)) if product_data.get("precio_venta") else 0,
                "vendor_id": product_data.get("vendedor_id", ""),
                "status": product_data.get("status", ""),
                "has_stock": product_data.get("tiene_stock", False),
                "created_at": product_data.get("created_at", ""),
                "tags": json.dumps(product_data.get("tags", []) if product_data.get("tags") else [])
            }

            # Agregar a collection
            self.products_collection.upsert(
                ids=[product_id],
                embeddings=embeddings,
                documents=[combined_text],
                metadatas=[metadata]
            )

            logger.debug(f"Embedding agregado para producto {product_id}")
            return True

        except Exception as e:
            logger.error(f"Error agregando embedding para producto {product_id}: {e}")
            return False

    async def add_products_batch(self, products_data: List[Dict]) -> int:
        """
        Agregar múltiples productos en batch para performance.

        Args:
            products_data: Lista de datos de productos

        Returns:
            int: Número de productos agregados exitosamente
        """
        try:
            if not products_data:
                return 0

            # Preparar datos para batch processing
            ids = []
            texts = []
            metadatas = []

            for product_data in products_data:
                product_id = str(product_data.get("id", ""))
                if not product_id:
                    continue

                combined_text = self._create_product_text(product_data)

                metadata = {
                    "product_id": product_id,
                    "name": product_data.get("name", ""),
                    "category": product_data.get("categoria", ""),
                    "primary_category_id": product_data.get("primary_category_id", ""),
                    "price": float(product_data.get("precio_venta", 0)) if product_data.get("precio_venta") else 0,
                    "vendor_id": product_data.get("vendedor_id", ""),
                    "status": product_data.get("status", ""),
                    "has_stock": product_data.get("tiene_stock", False),
                    "created_at": product_data.get("created_at", ""),
                    "tags": json.dumps(product_data.get("tags", []) if product_data.get("tags") else [])
                }

                ids.append(product_id)
                texts.append(combined_text)
                metadatas.append(metadata)

            if not ids:
                return 0

            # Generar embeddings en batch
            embeddings = await self.generate_embeddings(texts)

            # Agregar en batches para evitar memory issues
            added_count = 0
            for i in range(0, len(ids), self.batch_size):
                batch_end = min(i + self.batch_size, len(ids))

                batch_ids = ids[i:batch_end]
                batch_embeddings = embeddings[i:batch_end]
                batch_texts = texts[i:batch_end]
                batch_metadatas = metadatas[i:batch_end]

                self.products_collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )

                added_count += len(batch_ids)
                logger.debug(f"Batch procesado: {len(batch_ids)} productos")

            logger.info(f"Batch embedding completado: {added_count} productos procesados")
            return added_count

        except Exception as e:
            logger.error(f"Error en batch processing: {e}")
            return 0

    async def search_products(
        self,
        query: str,
        max_results: int = 10,
        category_filter: Optional[str] = None,
        price_range: Optional[Tuple[float, float]] = None,
        vendor_filter: Optional[str] = None,
        stock_available_only: bool = True
    ) -> List[Dict]:
        """
        Búsqueda semántica de productos.

        Args:
            query: Texto de búsqueda
            max_results: Número máximo de resultados
            category_filter: Filtro por categoría
            price_range: Rango de precios (min, max)
            vendor_filter: Filtro por vendor ID
            stock_available_only: Solo productos con stock

        Returns:
            List[Dict]: Lista de productos con scores de similitud
        """
        try:
            if not query.strip():
                return []

            # Generar embedding para query
            query_embeddings = await self.generate_embeddings([query])
            if not query_embeddings:
                return []

            # Construir filtros
            where_filter = {}
            if category_filter:
                where_filter["category"] = {"$eq": category_filter}
            if vendor_filter:
                where_filter["vendor_id"] = {"$eq": vendor_filter}
            if stock_available_only:
                where_filter["has_stock"] = {"$eq": True}
            if price_range:
                min_price, max_price = price_range
                where_filter["price"] = {"$gte": min_price, "$lte": max_price}

            # Realizar búsqueda
            results = self.products_collection.query(
                query_embeddings=query_embeddings,
                n_results=min(max_results, self.max_results),
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )

            # Procesar resultados
            search_results = []
            if results and results["ids"] and results["ids"][0]:
                for i, product_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    document = results["documents"][0][i]

                    # Convertir distance a similarity score (0-1)
                    similarity_score = max(0, 1 - distance)

                    search_result = {
                        "product_id": product_id,
                        "similarity_score": similarity_score,
                        "distance": distance,
                        "matched_text": document,
                        "metadata": metadata
                    }

                    search_results.append(search_result)

            logger.debug(f"Búsqueda semántica completada: {len(search_results)} resultados para '{query}'")
            return search_results

        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []

    async def search_similar_products(
        self,
        product_id: str,
        max_results: int = 5,
        exclude_same_vendor: bool = True
    ) -> List[Dict]:
        """
        Encontrar productos similares a uno dado.

        Args:
            product_id: ID del producto base
            max_results: Número máximo de resultados
            exclude_same_vendor: Excluir productos del mismo vendor

        Returns:
            List[Dict]: Lista de productos similares
        """
        try:
            # Obtener embedding del producto base
            base_product = self.products_collection.get(
                ids=[product_id],
                include=["embeddings", "metadatas"]
            )

            if not base_product["embeddings"] or not base_product["embeddings"][0]:
                return []

            base_embedding = base_product["embeddings"][0]
            base_metadata = base_product["metadatas"][0]

            # Construir filtros
            where_filter = {"has_stock": {"$eq": True}}
            if exclude_same_vendor and base_metadata.get("vendor_id"):
                where_filter["vendor_id"] = {"$ne": base_metadata["vendor_id"]}

            # Búsqueda por embedding
            results = self.products_collection.query(
                query_embeddings=[base_embedding],
                n_results=max_results + 1,  # +1 para excluir el producto mismo
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            # Procesar y filtrar resultados
            similar_products = []
            if results and results["ids"] and results["ids"][0]:
                for i, similar_id in enumerate(results["ids"][0]):
                    # Excluir el producto base
                    if similar_id == product_id:
                        continue

                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]

                    similarity_score = max(0, 1 - distance)

                    similar_product = {
                        "product_id": similar_id,
                        "similarity_score": similarity_score,
                        "distance": distance,
                        "metadata": metadata
                    }

                    similar_products.append(similar_product)

                    if len(similar_products) >= max_results:
                        break

            logger.debug(f"Productos similares encontrados: {len(similar_products)} para producto {product_id}")
            return similar_products

        except Exception as e:
            logger.error(f"Error buscando productos similares: {e}")
            return []

    async def delete_product_embedding(self, product_id: str) -> bool:
        """
        Eliminar embedding de producto.

        Args:
            product_id: ID del producto a eliminar

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            self.products_collection.delete(ids=[product_id])
            logger.debug(f"Embedding eliminado para producto {product_id}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando embedding: {e}")
            return False

    async def update_product_embedding(
        self,
        product_id: str,
        product_data: Dict
    ) -> bool:
        """
        Actualizar embedding de producto existente.

        Args:
            product_id: ID del producto
            product_data: Nuevos datos del producto

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Simplemente usar upsert que actualiza si existe
            return await self.add_product_embedding(product_id, product_data)

        except Exception as e:
            logger.error(f"Error actualizando embedding: {e}")
            return False

    async def get_collection_stats(self) -> Dict:
        """
        Obtener estadísticas de las collections.

        Returns:
            Dict: Estadísticas de uso y performance
        """
        try:
            products_count = self.products_collection.count()
            categories_count = self.categories_collection.count()

            stats = {
                "products_collection": {
                    "name": self.products_collection_name,
                    "count": products_count,
                    "embedding_model": self.embedding_model_name,
                    "dimension": self.embedding_dimension
                },
                "categories_collection": {
                    "name": self.categories_collection_name,
                    "count": categories_count,
                    "embedding_model": self.embedding_model_name,
                    "dimension": self.embedding_dimension
                },
                "cache_stats": {
                    "cached_embeddings": len(self._embedding_cache),
                    "cache_max_size": self._cache_max_size
                }
            }

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def _create_product_text(self, product_data: Dict) -> str:
        """
        Crear texto combinado para embedding de producto.

        Args:
            product_data: Datos del producto

        Returns:
            str: Texto optimizado para embedding
        """
        components = []

        # Nombre del producto (peso alto)
        name = product_data.get("name", "").strip()
        if name:
            components.append(name)
            components.append(name)  # Duplicar para mayor peso

        # Descripción
        description = product_data.get("description", "").strip()
        if description:
            components.append(description)

        # Categoría
        categoria = product_data.get("categoria", "").strip()
        if categoria:
            components.append(f"Categoría: {categoria}")

        # Tags
        tags = product_data.get("tags", [])
        if tags and isinstance(tags, list):
            components.append(f"Tags: {' '.join(tags)}")

        # Información de categoría principal si está disponible
        primary_category = product_data.get("primary_category")
        if primary_category and isinstance(primary_category, dict):
            cat_name = primary_category.get("name", "")
            if cat_name:
                components.append(f"Categoría principal: {cat_name}")

        return " ".join(components) if components else name or "Producto sin descripción"

    async def reset_collections(self) -> bool:
        """
        Resetear todas las collections (usar con cuidado).

        Returns:
            bool: True si se reseteó correctamente
        """
        try:
            logger.warning("Reseteando collections de ChromaDB...")

            # Eliminar collections existentes
            try:
                self.client.delete_collection(self.products_collection_name)
            except:
                pass

            try:
                self.client.delete_collection(self.categories_collection_name)
            except:
                pass

            # Reinicializar
            await self._initialize_collections()

            # Limpiar cache
            self._embedding_cache.clear()

            logger.info("Collections reseteadas exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error reseteando collections: {e}")
            return False


# Singleton instance
chroma_service = ChromaDBService()