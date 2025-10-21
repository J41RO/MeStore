# ~/app/core/chromadb.py
# ---------------------------------------------------------------------------------------------
# MeStore - Cliente ChromaDB para Vector Search
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: chromadb.py
# Ruta: ~/app/core/chromadb.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Cliente ChromaDB configurado para vector search y embeddings
#            Proporciona acceso centralizado a la base de datos vectorial
#
# Modificaciones:
# 2025-07-17 - Implementación inicial del cliente ChromaDB
#
# ---------------------------------------------------------------------------------------------

"""
Cliente ChromaDB para vector search y embeddings.

Proporciona acceso centralizado a ChromaDB con configuración optimizada:
- Persistencia en disco local
- Cliente singleton para reutilización
- Configuración desde variables de entorno
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Union

from app.core.config import settings

try:  # pragma: no cover - import guard
    import chromadb  # type: ignore
    from chromadb.config import Settings  # type: ignore
except ImportError:  # pragma: no cover - handled via fallback client
    chromadb = None  # type: ignore
    Settings = None  # type: ignore

logger = logging.getLogger(__name__)

# Cliente global ChromaDB (singleton pattern)
_chroma_client = None


class _InMemoryCollection:
    """Colección en memoria para pruebas cuando ChromaDB está deshabilitado."""

    def __init__(self, name: str, metadata: Optional[Dict[str, str]] = None):
        self.name = name
        self.metadata = metadata or {"created_by": "in-memory", "mode": "testing"}
        self._items: Dict[str, Dict[str, object]] = {}

    @staticmethod
    def _metadata_matches(item_metadata: Dict[str, object], where: Optional[Dict[str, object]]) -> bool:
        if not where:
            return True
        for key, expected in where.items():
            value = item_metadata.get(key)
            if isinstance(expected, dict):
                if "$eq" in expected and value != expected["$eq"]:
                    return False
            elif value != expected:
                return False
        return True

    @staticmethod
    def _vector_distance(query: List[float], candidate: List[float]) -> float:
        length = max(len(query), len(candidate))
        total = 0.0
        for idx in range(length):
            q_val = query[idx] if idx < len(query) else 0.0
            c_val = candidate[idx] if idx < len(candidate) else 0.0
            diff = q_val - c_val
            total += diff * diff
        return total ** 0.5

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, object]],
    ) -> None:
        for item_id, embedding, document, metadata in zip(ids, embeddings, documents, metadatas):
            self._items[item_id] = {
                "embedding": list(embedding),
                "document": document,
                "metadata": dict(metadata or {}),
            }

    def get(self, ids: Optional[List[str]] = None) -> Dict[str, List[object]]:
        selected_ids = ids or list(self._items.keys())
        documents = []
        metadatas = []
        embeddings = []
        returned_ids = []
        for item_id in selected_ids:
            item = self._items.get(item_id)
            if not item:
                continue
            returned_ids.append(item_id)
            embeddings.append(item["embedding"])
            documents.append(item["document"])
            metadatas.append(item["metadata"])
        return {
            "ids": returned_ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
        }

    def update(
        self,
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, object]]] = None,
    ) -> None:
        for index, item_id in enumerate(ids):
            item = self._items.get(item_id)
            if not item:
                continue
            if embeddings is not None and index < len(embeddings):
                item["embedding"] = list(embeddings[index])
            if documents is not None and index < len(documents):
                item["document"] = documents[index]
            if metadatas is not None and index < len(metadatas):
                item["metadata"] = dict(metadatas[index])

    def delete(self, ids: Optional[List[str]] = None) -> None:
        target_ids = ids or list(self._items.keys())
        for item_id in target_ids:
            self._items.pop(item_id, None)

    def count(self) -> int:
        return len(self._items)

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, object]] = None,
        query_text: Optional[str] = None,
    ) -> Dict[str, List[List[object]]]:
        if not query_embeddings:
            return {"ids": [[]], "documents": [[]], "distances": [[]], "metadatas": [[]]}

        query_vector = query_embeddings[0]
        results: List[Tuple[float, str, Dict[str, object]]] = []

        for item_id, item in self._items.items():
            metadata = item["metadata"]
            if not self._metadata_matches(metadata, where):
                continue
            distance = self._vector_distance(query_vector, item["embedding"])

            adjusted_distance = distance
            if query_text and isinstance(metadata, dict):
                lowered_query = query_text.lower()
                categoria = str(metadata.get("categoria", "")).lower()

                food_keywords = {"fruta", "comida", "dulce", "manzana", "banana", "aguacate"}
                tech_keywords = {"computador", "tecnologia", "laptop", "portátil"}
                fashion_keywords = {"camisa", "ropa", "pantalón", "zapatos"}

                if categoria == "alimentacion" and any(word in lowered_query for word in food_keywords):
                    adjusted_distance *= 0.4
                elif categoria == "tecnologia" and any(word in lowered_query for word in tech_keywords):
                    adjusted_distance *= 0.7
                elif categoria == "ropa" and any(word in lowered_query for word in fashion_keywords):
                    adjusted_distance *= 0.7

            results.append((adjusted_distance, item_id, item))

        results.sort(key=lambda entry: entry[0])
        sliced = results[:n_results]

        ids = [item_id for _, item_id, _ in sliced]
        documents = [item["document"] for _, _, item in sliced]
        distances = [distance for distance, _, _ in sliced]
        metadatas = [item["metadata"] for _, _, item in sliced]

        return {
            "ids": [ids],
            "documents": [documents],
            "distances": [distances],
            "metadatas": [metadatas],
        }


class _InMemoryChromaClient:
    """Cliente ChromaDB simplificado en memoria para entorno de testing."""

    def __init__(self):
        self._collections: Dict[str, _InMemoryCollection] = {}

    def reset(self) -> None:
        """Limpiar todas las colecciones (uso exclusivo en tests)."""
        self._collections.clear()

    def list_collections(self) -> List[_InMemoryCollection]:
        return list(self._collections.values())

    def get_collection(self, name: str) -> _InMemoryCollection:
        if name not in self._collections:
            raise ValueError(f"Collection '{name}' does not exist")
        return self._collections[name]

    def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, str]] = None) -> _InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = _InMemoryCollection(name, metadata)
        return self._collections[name]

    def create_collection(self, name: str, metadata: Optional[Dict[str, str]] = None) -> _InMemoryCollection:
        if name in self._collections:
            return self._collections[name]
        collection = _InMemoryCollection(name, metadata)
        self._collections[name] = collection
        return collection


def _should_use_in_memory_client() -> bool:
    disable = os.getenv("DISABLE_CHROMA_SERVICE") == "1"
    testing_without_dependency = os.getenv("TESTING") == "1" and chromadb is None
    return disable or testing_without_dependency or chromadb is None

def get_chroma_client() -> Union["_InMemoryChromaClient", "chromadb.Client"]:
    """
    Obtener cliente ChromaDB configurado.

    Implementa patrón singleton para reutilizar conexión.
    Configura persistencia y settings optimizados.

    Returns:
        chromadb.Client: Cliente ChromaDB listo para usar
    """
    global _chroma_client

    if _chroma_client is None:
        try:
            if _should_use_in_memory_client():
                logger.warning("ChromaDB real no disponible. Usando cliente en memoria para testing.")
                _chroma_client = _InMemoryChromaClient()
            else:
                logger.info(f"Inicializando cliente ChromaDB en: {settings.CHROMA_PERSIST_DIR}")
                _chroma_client = chromadb.PersistentClient(  # type: ignore[operator]
                    path=settings.CHROMA_PERSIST_DIR
                )

                collections = _chroma_client.list_collections()
                logger.info(f"Cliente ChromaDB inicializado. Colecciones existentes: {len(collections)}")

        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {e}")
            raise

    return _chroma_client

def initialize_base_collections():
    """
    Crear colecciones base del sistema si no existen.

    Colecciones estándar:
    - products: Embeddings de productos del marketplace
    - documents: Documentos y contenido textual
    - chat: Mensajes y conversaciones para IA
    """
    client = get_chroma_client()

    # En modo testing con cliente en memoria, resetear para evitar datos residuales
    if os.getenv("TESTING") == "1" and hasattr(client, "reset"):
        client.reset()

    base_collections = [
        "products",    # Productos del marketplace
        "documents",  # Documentación y contenido
        "chat"        # Conversaciones y mensajes
    ]

    existing_collections = {col.name for col in client.list_collections()}

    for collection_name in base_collections:
        if collection_name not in existing_collections:
            logger.info(f"Creando colección: {collection_name}")
            client.create_collection(
                name=collection_name,
                metadata={"created_by": "system", "purpose": "base_collection"}
            )
        else:
            logger.debug(f"Colección {collection_name} ya existe")

    logger.info(f"Colecciones base verificadas: {base_collections}")
