# ~/app/schemas/embeddings_schemas.py
# ---------------------------------------------------------------------------------------------
# MeStore - Embeddings Pydantic Schemas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embeddings_schemas.py
# Ruta: ~/app/schemas/embeddings_schemas.py
# Autor: Jairo
# Fecha de Creación: 2025-07-24
# Última Actualización: 2025-07-24
# Versión: 1.0.0
# Propósito: Pydantic models para embeddings API endpoints
#            Extracted from app/api/v1/endpoints/embeddings.py for better organization
#
# Modificaciones:
# 2025-07-24 - Schemas extracted from embeddings.py endpoint
#
# ---------------------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Modelos Pydantic para requests/responses
class AddItemsRequest(BaseModel):
    """Request para agregar items a colección."""
    ids: List[str] = Field(..., description="IDs únicos para cada item")
    texts: List[str] = Field(..., description="Textos para generar embeddings")
    metadatas: Optional[List[Dict[str, Any]]] = Field(
        None, description="Metadatos opcionales para cada item"
    )


class QueryRequest(BaseModel):
    """Request para búsqueda semántica."""
    query_text: str = Field(..., description="Texto de consulta")
    n_results: int = Field(5, description="Número de resultados", ge=1, le=50)
    where: Optional[Dict[str, Any]] = Field(None, description="Filtros de metadatos")


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
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales de la operación")


# Export all schemas
__all__ = [
    "AddItemsRequest",
    "QueryRequest", 
    "UpdateItemRequest",
    "DeleteItemsRequest",
    "StandardResponse"
]
