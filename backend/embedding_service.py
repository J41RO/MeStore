# ~/backend/embedding_service.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Servicio de Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embedding_service.py
# Ruta: ~/backend/embedding_service.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Wrapper sobre ChromaDB para operaciones CRUD de embeddings
#            en colecciones products, docs y chat
#
# Modificaciones:
# 2025-07-17 - Implementación inicial con funciones add/query/update
#
# ---------------------------------------------------------------------------------------------

"""
Servicio de Embeddings para MeStore.

Este módulo proporciona un wrapper sobre ChromaDB que simplifica las operaciones
de agregar, consultar y actualizar documentos embebidos en las colecciones
products, docs y chat.

Funciones principales:
- add_embeddings: Agregar documentos con verificación de duplicados
- query_embedding: Buscar documentos similares por embedding
- update_embedding: Actualizar contenido de documento existente
"""

import logging
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings

from embedding_model import get_embedding

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Colecciones válidas
VALID_COLLECTIONS = {'products', 'docs', 'chat'}

class EmbeddingService:
    """Servicio singleton para manejo de embeddings en ChromaDB."""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """Inicializar cliente ChromaDB con persistencia."""
        try:
            self._client = chromadb.PersistentClient(path='./backend/chroma_db')
            logger.info("✅ ChromaDB client inicializado con persistencia")
        except Exception as e:
            logger.error(f"❌ Error inicializando ChromaDB: {e}")
            raise

    @property
    def client(self):
        """Getter para cliente ChromaDB."""
        if self._client is None:
            self._initialize_client()
        return self._client

    def _validate_collection(self, collection: str) -> None:
        """Validar que la colección sea válida."""
        if collection not in VALID_COLLECTIONS:
            raise ValueError(f"Colección '{collection}' no válida. Usar: {VALID_COLLECTIONS}")

    def _get_collection(self, collection_name: str):
        """Obtener o crear colección ChromaDB."""
        try:
            return self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            logger.error(f"❌ Error accediendo colección '{collection_name}': {e}")
            raise

def add_embeddings(
    docs: List[str], 
    ids: List[str], 
    collection: str,
    metadatas: Optional[List[dict]] = None
) -> Dict[str, Any]:
    """
    Agregar documentos con embeddings a una colección.

    Args:
        docs: Lista de documentos de texto a embebir
        ids: Lista de IDs únicos para los documentos
        collection: Nombre de la colección ('products', 'docs', 'chat')
        metadatas: Metadatos opcionales para cada documento

    Returns:
        Dict con resultado de la operación

    Raises:
        ValueError: Si la colección no es válida o hay inconsistencias en datos
        Exception: Si hay errores en ChromaDB o generación de embeddings
    """
    service = EmbeddingService()
    service._validate_collection(collection)

    # Validar consistencia de datos
    if len(docs) != len(ids):
        raise ValueError(f"Inconsistencia: {len(docs)} docs vs {len(ids)} ids")

    if metadatas and len(metadatas) != len(docs):
        raise ValueError(f"Inconsistencia: {len(docs)} docs vs {len(metadatas)} metadatas")

    if not docs:
        raise ValueError("Lista de documentos no puede estar vacía")

    logger.info(f"🔧 Agregando {len(docs)} documentos a colección '{collection}'")

    try:
        # Obtener colección
        chroma_collection = service._get_collection(collection)

        # Verificar IDs existentes para evitar duplicados
        existing_ids = []
        for doc_id in ids:
            try:
                existing = chroma_collection.get(ids=[doc_id])
                if existing['ids']:
                    existing_ids.append(doc_id)
            except Exception:
                # ID no existe, está bien
                pass

        if existing_ids:
            logger.warning(f"⚠️ IDs ya existentes (se omitirán): {existing_ids}")
            # Filtrar documentos con IDs duplicados
            filtered_docs = []
            filtered_ids = []
            filtered_metadatas = []

            for i, doc_id in enumerate(ids):
                if doc_id not in existing_ids:
                    filtered_docs.append(docs[i])
                    filtered_ids.append(doc_id)
                    if metadatas:
                        filtered_metadatas.append(metadatas[i])

            docs = filtered_docs
            ids = filtered_ids
            metadatas = filtered_metadatas if metadatas else None

        if not docs:
            return {
                'success': True,
                'message': 'Todos los IDs ya existían - no se agregó nada',
                'added_count': 0,
                'skipped_count': len(existing_ids),
                'collection': collection
            }

        # Generar embeddings
        logger.info(f"🧠 Generando embeddings para {len(docs)} documentos...")
        embeddings = []
        for doc in docs:
            embedding = get_embedding(doc)
            embeddings.append(embedding)

        # Preparar metadatas por defecto si no se proporcionan
        if metadatas is None:
            metadatas = [{'source': 'embedding_service', 'collection': collection} for _ in docs]

        # Agregar a ChromaDB
        chroma_collection.add(
            documents=docs,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        logger.info(f"✅ Agregados {len(docs)} documentos a '{collection}'")

        return {
            'success': True,
            'message': f'Documentos agregados exitosamente a {collection}',
            'added_count': len(docs),
            'skipped_count': len(existing_ids),
            'collection': collection,
            'embedding_dimensions': len(embeddings[0]) if embeddings else 0
        }

    except Exception as e:
        logger.error(f"❌ Error en add_embeddings: {e}")
        return {
            'success': False,
            'message': f'Error agregando documentos: {str(e)}',
            'added_count': 0,
            'collection': collection
        }

def query_embedding(
    query: str, 
    collection: str, 
    n_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Buscar documentos similares por embedding en una colección.

    Args:
        query: Texto de consulta para buscar similitudes
        collection: Nombre de la colección a consultar
        n_results: Número máximo de resultados a retornar

    Returns:
        Lista de documentos ordenados por similitud (mayor a menor)

    Raises:
        ValueError: Si la colección no es válida
        Exception: Si hay errores en ChromaDB o generación de embeddings
    """
    service = EmbeddingService()
    service._validate_collection(collection)

    if not query.strip():
        raise ValueError("Query no puede estar vacía")

    if n_results <= 0:
        raise ValueError("n_results debe ser mayor a 0")

    logger.info(f"🔍 Consultando '{collection}' con query: '{query[:50]}...'")

    try:
        # Obtener colección
        chroma_collection = service._get_collection(collection)

        # Verificar que la colección tenga documentos
        collection_count = chroma_collection.count()
        if collection_count == 0:
            logger.warning(f"⚠️ Colección '{collection}' está vacía")
            return []

        # Generar embedding de la consulta
        query_embedding = get_embedding(query)
        logger.info(f"🧠 Embedding de consulta generado: {len(query_embedding)} dimensiones")

        # Realizar búsqueda por similitud
        results = chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection_count)
        )

        # Formatear resultados
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                'similarity_score': 1 - results['distances'][0][i]  # Convertir distancia a score
            }
            formatted_results.append(result)

        logger.info(f"✅ Encontrados {len(formatted_results)} resultados en '{collection}'")

        return formatted_results

    except Exception as e:
        logger.error(f"❌ Error en query_embedding: {e}")
        raise

def update_embedding(
    id: str, 
    new_doc: str, 
    collection: str,
    new_metadata: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Actualizar el contenido de un documento existente en una colección.

    Args:
        id: ID del documento a actualizar
        new_doc: Nuevo contenido del documento
        collection: Nombre de la colección
        new_metadata: Nuevos metadatos opcionales

    Returns:
        Dict con resultado de la operación

    Raises:
        ValueError: Si la colección no es válida o el documento no existe
        Exception: Si hay errores en ChromaDB o generación de embeddings
    """
    service = EmbeddingService()
    service._validate_collection(collection)

    if not id.strip():
        raise ValueError("ID no puede estar vacío")

    if not new_doc.strip():
        raise ValueError("Nuevo documento no puede estar vacío")

    logger.info(f"🔄 Actualizando documento '{id}' en colección '{collection}'")

    try:
        # Obtener colección
        chroma_collection = service._get_collection(collection)

        # Verificar que el documento existe
        existing = chroma_collection.get(ids=[id])
        if not existing['ids']:
            raise ValueError(f"Documento con ID '{id}' no existe en colección '{collection}'")

        # Obtener metadatos existentes si no se proporcionan nuevos
        if new_metadata is None:
            existing_metadata = existing['metadatas'][0] if existing['metadatas'][0] else {}
            new_metadata = {
                **existing_metadata,
                'updated_by': 'embedding_service',
                'last_update': str(chromadb.utils.embedding_functions.DefaultEmbeddingFunction())  # Timestamp simple
            }

        # Generar nuevo embedding
        logger.info(f"🧠 Generando nuevo embedding para documento '{id}'...")
        new_embedding = get_embedding(new_doc)

        # Actualizar en ChromaDB
        chroma_collection.update(
            ids=[id],
            documents=[new_doc],
            embeddings=[new_embedding],
            metadatas=[new_metadata]
        )

        logger.info(f"✅ Documento '{id}' actualizado en '{collection}'")

        return {
            'success': True,
            'message': f'Documento {id} actualizado exitosamente',
            'id': id,
            'collection': collection,
            'new_doc_length': len(new_doc),
            'embedding_dimensions': len(new_embedding)
        }

    except Exception as e:
        logger.error(f"❌ Error en update_embedding: {e}")
        return {
            'success': False,
            'message': f'Error actualizando documento: {str(e)}',
            'id': id,
            'collection': collection
        }

# Funciones de utilidad adicionales
def get_collection_stats(collection: str) -> Dict[str, Any]:
    """Obtener estadísticas de una colección."""
    service = EmbeddingService()
    service._validate_collection(collection)

    try:
        chroma_collection = service._get_collection(collection)
        count = chroma_collection.count()

        # Obtener algunos documentos de muestra si existen
        sample_data = None
        if count > 0:
            sample = chroma_collection.peek(limit=min(3, count))
            sample_data = sample

        return {
            'collection': collection,
            'document_count': count,
            'sample_documents': sample_data,
            'status': 'active' if count > 0 else 'empty'
        }
    except Exception as e:
        return {
            'collection': collection,
            'error': str(e),
            'status': 'error'
        }

def list_all_collections() -> List[Dict[str, Any]]:
    """Listar todas las colecciones con sus estadísticas."""
    service = EmbeddingService()

    try:
        collections = service.client.list_collections()
        stats = []

        for col in collections:
            col_stats = {
                'name': col.name,
                'count': col.count(),
                'is_valid': col.name in VALID_COLLECTIONS
            }
            stats.append(col_stats)

        return stats
    except Exception as e:
        logger.error(f"❌ Error listando colecciones: {e}")
        return []

if __name__ == '__main__':
    # Ejemplo de uso básico
    print("🧪 EMBEDDING SERVICE - EJEMPLO DE USO")

    # Listar colecciones
    collections = list_all_collections()
    print(f"📋 Colecciones disponibles: {collections}")

    # Obtener estadísticas
    for col_name in VALID_COLLECTIONS:
        stats = get_collection_stats(col_name)
        print(f"📊 {col_name}: {stats}")