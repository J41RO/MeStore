# ~/app/api/v1/embeddings.py
# ---------------------------------------------------------------------------------------------
# MeStore - API Endpoints para ChromaDB y Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embeddings.py
# Ruta: ~/app/api/v1/embeddings.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: API REST para operaciones de vector search y embeddings
#            Expone funcionalidades ChromaDB via HTTP endpoints
#
# Modificaciones:
# 2025-07-17 - API inicial para embeddings y vector search
#
# ---------------------------------------------------------------------------------------------

"""
API REST para sistema de embeddings y vector search.

Endpoints disponibles:
- POST /embeddings/{collection}/add: Agregar items con embeddings
- GET /embeddings/{collection}/query: Buscar items similares
- PUT /embeddings/{collection}/update: Actualizar item existente
- DELETE /embeddings/{collection}/delete: Eliminar items
- GET /embeddings/{collection}/stats: Estadísticas de colección
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.embeddings import (
    add_items,
    query_similar, 
    update_item,
    delete_items,
    get_collection_stats
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embeddings", tags=["Vector Search"])

# Modelos Pydantic para requests/responses

class AddItemsRequest(BaseModel):
    """Request para agregar items a colección."""
    ids: List[str] = Field(..., description="IDs únicos para cada item")
    texts: List[str] = Field(..., description="Textos para generar embeddings")
    metadatas: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Metadatos opcionales para cada item"
    )

class QueryRequest(BaseModel):
    """Request para búsqueda semántica."""
    query_text: str = Field(..., description="Texto de consulta")
    n_results: int = Field(5, description="Número de resultados", ge=1, le=50)
    where: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filtros de metadatos"
    )

class UpdateItemRequest(BaseModel):
    """Request para actualizar item."""
    item_id: str = Field(..., description="ID del item a actualizar")
    new_text: Optional[str] = Field(None, description="Nuevo texto")
    new_metadata: Optional[Dict[str, Any]] = Field(None, description="Nuevos metadatos")

class DeleteItemsRequest(BaseModel):
    """Request para eliminar items."""
    ids: List[str] = Field(..., description="IDs de items a eliminar")

class StandardResponse(BaseModel):
    """Response estándar para operaciones."""
    success: bool = Field(..., description="Indica si operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")

# Endpoints de la API

@router.post("/{collection}/add", response_model=StandardResponse)
async def add_items_to_collection(
    collection: str,
    request: AddItemsRequest
):
    """
    Agregar items con embeddings a una colección.

    Args:
        collection: Nombre de la colección ChromaDB
        request: Datos de los items a agregar

    Returns:
        Confirmación de operación exitosa
    """
    try:
        logger.info(f"Agregando {len(request.texts)} items a colección '{collection}'")

        # Validar longitudes
        if len(request.ids) != len(request.texts):
            raise HTTPException(
                status_code=400,
                detail="IDs y textos deben tener la misma longitud"
            )

        # Validar metadatos si se proporcionan
        if request.metadatas and len(request.metadatas) != len(request.texts):
            raise HTTPException(
                status_code=400,
                detail="Metadatos deben tener la misma longitud que textos"
            )

        # Agregar items
        success = add_items(
            collection_name=collection,
            ids=request.ids,
            texts=request.texts,
            metadatas=request.metadatas
        )

        if success:
            return StandardResponse(
                success=True,
                message=f"Agregados {len(request.texts)} items a '{collection}'",
                data={"collection": collection, "items_added": len(request.texts)}
            )
        else:
            raise HTTPException(status_code=500, detail="Error agregando items")

    except Exception as e:
        logger.error(f"Error en add_items_to_collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/query")
async def query_collection(
    collection: str,
    request: QueryRequest
):
    """
    Buscar items similares por contenido semántico.

    Args:
        collection: Nombre de la colección a consultar
        request: Parámetros de búsqueda

    Returns:
        Resultados de búsqueda con similitud
    """
    try:
        logger.info(f"Consultando '{collection}' con: '{request.query_text}'")

        results = query_similar(
            collection_name=collection,
            query_text=request.query_text,
            n_results=request.n_results,
            where=request.where
        )

        # Formatear resultados para respuesta
        formatted_results = []

        if results['ids'][0]:  # Si hay resultados
            for i, (doc_id, document, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0], 
                results['distances'][0]
            )):
                result_item = {
                    "rank": i + 1,
                    "id": doc_id,
                    "document": document,
                    "similarity_score": 1.0 - distance,  # Convertir distancia a similitud
                    "distance": distance
                }

                # Agregar metadatos si existen
                if results['metadatas'][0] and i < len(results['metadatas'][0]):
                    result_item["metadata"] = results['metadatas'][0][i]

                formatted_results.append(result_item)

        return {
            "success": True,
            "query": request.query_text,
            "collection": collection,
            "total_results": len(formatted_results),
            "results": formatted_results
        }

    except Exception as e:
        logger.error(f"Error en query_collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{collection}/update", response_model=StandardResponse)
async def update_collection_item(
    collection: str,
    request: UpdateItemRequest
):
    """
    Actualizar un item existente en la colección.

    Args:
        collection: Nombre de la colección
        request: Datos de actualización

    Returns:
        Confirmación de actualización
    """
    try:
        logger.info(f"Actualizando item {request.item_id} en '{collection}'")

        success = update_item(
            collection_name=collection,
            item_id=request.item_id,
            new_text=request.new_text,
            new_metadata=request.new_metadata
        )

        if success:
            return StandardResponse(
                success=True,
                message=f"Item {request.item_id} actualizado en '{collection}'",
                data={"collection": collection, "updated_id": request.item_id}
            )
        else:
            raise HTTPException(status_code=500, detail="Error actualizando item")

    except Exception as e:
        logger.error(f"Error en update_collection_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{collection}/delete", response_model=StandardResponse)
async def delete_collection_items(
    collection: str,
    request: DeleteItemsRequest
):
    """
    Eliminar items de una colección.

    Args:
        collection: Nombre de la colección
        request: IDs de items a eliminar

    Returns:
        Confirmación de eliminación
    """
    try:
        logger.info(f"Eliminando {len(request.ids)} items de '{collection}'")

        success = delete_items(
            collection_name=collection,
            ids=request.ids
        )

        if success:
            return StandardResponse(
                success=True,
                message=f"Eliminados {len(request.ids)} items de '{collection}'",
                data={"collection": collection, "deleted_count": len(request.ids)}
            )
        else:
            raise HTTPException(status_code=500, detail="Error eliminando items")

    except Exception as e:
        logger.error(f"Error en delete_collection_items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection}/stats")
async def get_collection_statistics(collection: str):
    """
    Obtener estadísticas de una colección.

    Args:
        collection: Nombre de la colección

    Returns:
        Estadísticas de la colección
    """
    try:
        logger.info(f"Obteniendo estadísticas de '{collection}'")

        stats = get_collection_stats(collection_name=collection)

        return {
            "success": True,
            "collection": collection,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error en get_collection_statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint adicional para listar colecciones disponibles
@router.get("/collections")
async def list_collections():
    """
    Listar todas las colecciones disponibles.

    Returns:
        Lista de colecciones y sus estadísticas básicas
    """
    try:
        from app.core.chromadb import get_chroma_client

        client = get_chroma_client()
        collections = client.list_collections()

        collection_info = []
        for col in collections:
            try:
                stats = get_collection_stats(col.name)
                collection_info.append({
                    "name": col.name,
                    "count": stats["count"],
                    "metadata": col.metadata
                })
            except Exception as e:
                logger.warning(f"Error obteniendo stats de {col.name}: {e}")
                collection_info.append({
                    "name": col.name,
                    "count": "unknown",
                    "metadata": col.metadata
                })

        return {
            "success": True,
            "total_collections": len(collection_info),
            "collections": collection_info
        }

    except Exception as e:
        logger.error(f"Error en list_collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))