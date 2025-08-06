# ~/app/schemas/product_image.py
# ---------------------------------------------------------------------------------------------
# MeStore - Product Image Schemas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Schemas para gestión de imágenes de productos.

Define los schemas de validación y respuesta para el upload
y gestión de imágenes de productos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.utils.url_helper import build_public_url


class ProductImageBase(BaseModel):
    """Schema base para imágenes de productos."""
    
    filename: str = Field(..., description="Nombre único del archivo")
    original_filename: str = Field(..., description="Nombre original del archivo subido")
    file_size: int = Field(..., gt=0, description="Tamaño del archivo en bytes")
    mime_type: str = Field(..., description="Tipo MIME del archivo")
    width: Optional[int] = Field(None, ge=1, description="Ancho en píxeles")
    height: Optional[int] = Field(None, ge=1, description="Alto en píxeles")
    order_index: int = Field(0, ge=0, description="Orden de visualización (0 = principal)")


class ProductImageCreate(ProductImageBase):
    """Schema para crear una nueva imagen."""
    
    product_id: UUID = Field(..., description="ID del producto asociado")
    file_path: str = Field(..., description="Ruta relativa del archivo")


class ProductImageResponse(ProductImageBase):
    """Schema para respuestas de imágenes."""
    
    id: UUID
    product_id: UUID
    file_path: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def public_url(self) -> str:
        """URL pública para acceder a la imagen."""
        return build_public_url(self.file_path)


class ProductImageUploadResponse(BaseModel):
    resolutions_created: List[str] = Field(default_factory=list, description="Resoluciones creadas automáticamente")
    """Schema para respuesta de upload múltiple."""
    
    success: bool = Field(..., description="Indica si el upload fue exitoso")
    uploaded_count: int = Field(..., ge=0, description="Cantidad de imágenes subidas exitosamente")
    total_files: int = Field(..., ge=0, description="Total de archivos procesados")
    images: List[ProductImageResponse] = Field(
        default_factory=list,
        description="Lista de imágenes subidas exitosamente"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Lista de errores encontrados durante el upload"
    )
    
    model_config = ConfigDict(from_attributes=True)


class ProductImagesListResponse(BaseModel):
    """Schema para listar todas las imágenes de un producto."""
    
    product_id: UUID
    total_images: int = Field(..., ge=0, description="Total de imágenes del producto")
    images: List[ProductImageResponse] = Field(
        default_factory=list,
        description="Lista de imágenes del producto ordenadas por order_index"
    )
    
    model_config = ConfigDict(from_attributes=True)