# ~/app/services/embeddings.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio de Embeddings y Vector Search
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embeddings.py
# Ruta: ~/app/services/embeddings.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Servicio de embeddings para vector search y similitud semántica
#            Integra SentenceTransformers con ChromaDB para búsqueda inteligente
#
# Modificaciones:
# 2025-07-17 - Implementación inicial del servicio de embeddings
#
# ---------------------------------------------------------------------------------------------

"""
Servicio de Embeddings para Vector Search.

Proporciona funcionalidades de embeddings y búsqueda semántica:
- Generación de embeddings con SentenceTransformers
- Operaciones CRUD en ChromaDB
- Búsqueda por similitud semántica
- Gestión de colecciones por categoría
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from app.core.chromadb import get_chroma_client, initialize_base_collections
import logging

logger = logging.getLogger(__name__)

# Modelo global de embeddings (singleton pattern)
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    """
    # Early return si no hay cambios que hacer
    if new_text is None and new_metadata is None:
        logger.info(f"No hay cambios para actualizar en item {item_id}")
        return True


    Returns:
        bool: True si se actualizó exitosamente

    Raises:
        Exception: Si ocurre error durante la actualización
        SentenceTransformer: Modelo listo para generar embeddings
    """
    global _embedding_model

    if _embedding_model is None:
        logger.info("Cargando modelo de embeddings: all-MiniLM-L6-v2")
        try:
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Modelo de embeddings cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {e}")
            raise

    return _embedding_model

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generar embeddings para lista de textos.

    Args:
        texts: Lista de textos para procesar

    Returns:
        Lista de vectores (embeddings) como listas de floats
    """
    if not texts:
        return []

    model = get_embedding_model()

    try:
        # Generar embeddings y convertir a lista de listas
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error generando embeddings: {e}")
        raise

def add_items(
    collection_name: str, 
    ids: List[str], 
    texts: List[str], 
    metadatas: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Agregar items con embeddings a una colección.

    Args:
        collection_name: Nombre de la colección ChromaDB
        ids: IDs únicos para cada item
        texts: Textos para generar embeddings
        metadatas: Metadatos opcionales para cada item

    Returns:
        bool: True si se agregaron exitosamente
    """
    if not texts or not ids or len(texts) != len(ids):
        raise ValueError("texts e ids deben tener la misma longitud y no estar vacíos")

    try:
        # Inicializar colecciones base si es necesario
        initialize_base_collections()

        # Obtener cliente y colección
        client = get_chroma_client()
        collection = client.get_or_create_collection(name=collection_name)

        # Generar embeddings
        embeddings = embed_texts(texts)

        # Preparar metadatos
        if metadatas is None:
            metadatas = [{}] * len(texts)
        elif len(metadatas) != len(texts):
            raise ValueError("metadatas debe tener la misma longitud que texts")

        # Agregar a ChromaDB
        collection.add(
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
            documents=texts
        )

        logger.info(f"Agregados {len(texts)} items a colección '{collection_name}'")
        return True

    except Exception as e:
        logger.error(f"Error agregando items a {collection_name}: {e}")
        raise

def query_similar(
    collection_name: str, 
    query_text: str, 
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Buscar items similares por contenido semántico.

    Args:
        collection_name: Nombre de la colección a consultar
        query_text: Texto de consulta para buscar similares
        n_results: Número máximo de resultados a retornar
        where: Filtros de metadatos opcionales

    Returns:
        Diccionario con resultados de la búsqueda
    """
    try:
        # Obtener cliente y colección
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        # Generar embedding de la consulta
        query_embedding = embed_texts([query_text])[0]

        # Realizar búsqueda
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        logger.info(f"Consulta en '{collection_name}': {len(results['ids'][0] if results['ids'] and results['ids'][0] else [])} resultados")
        # Aplanar resultados para facilitar uso
        return {
            'ids': results['ids'][0] if results['ids'] and results['ids'][0] else [],
            'documents': results['documents'][0] if results['documents'] and results['documents'][0] else [],
            'distances': results['distances'][0] if results['distances'] and results['distances'][0] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] and results['metadatas'][0] else []
        }

    except Exception as e:
        logger.error(f"Error en consulta a {collection_name}: {e}")
        raise

def update_item(
    collection_name: str,
    item_id: str,
    new_text: Optional[str] = None,
    new_metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Actualizar un item existente en la colección.

    Args:
        collection_name: Nombre de la colección
        item_id: ID del item a actualizar
        new_text: Nuevo texto (regenerará embedding)
        new_metadata: Nuevos metadatos

    Returns:
        bool: True si se actualizó exitosamente
    """
    # Early return si no hay cambios que hacer
    if new_text is None and new_metadata is None:
        logger.info(f"No hay cambios para actualizar en item {item_id}")
        return True
    
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        update_data = {"ids": [item_id]}

        if new_text is not None:
            # Regenerar embedding para nuevo texto
            new_embedding = embed_texts([new_text])[0]
            update_data["embeddings"] = [new_embedding]
            update_data["documents"] = [new_text]

        if new_metadata is not None:
            update_data["metadatas"] = [new_metadata]

        collection.update(**update_data)

        logger.info(f"Item {item_id} actualizado en '{collection_name}'")
        return True

    except Exception as e:
        logger.error(f"Error actualizando item {item_id}: {e}")
        raise

def delete_items(collection_name: str, ids: List[str]) -> bool:
    """
    Eliminar items de una colección.

    Args:
        collection_name: Nombre de la colección
        ids: Lista de IDs a eliminar

    Returns:
        bool: True si se eliminaron exitosamente
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        collection.delete(ids=ids)

        logger.info(f"Eliminados {len(ids)} items de '{collection_name}'")
        return True

    except Exception as e:
        logger.error(f"Error eliminando items de {collection_name}: {e}")
        raise

def get_collection_stats(collection_name: str) -> Dict[str, Any]:
    """
    Obtener estadísticas de una colección.

    Args:
        collection_name: Nombre de la colección

    Returns:
        Diccionario con estadísticas de la colección
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        count = collection.count()

        return {
            "name": collection_name,
            "count": count,
            "metadata": collection.metadata
        }

    except Exception as e:
        logger.error(f"Error obteniendo stats de {collection_name}: {e}")
        raise