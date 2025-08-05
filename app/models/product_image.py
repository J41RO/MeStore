# ~/app/models/product_image.py
# ---------------------------------------------------------------------------------------------
# MeStore - Product Image Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Modelo para imágenes de productos.

Este módulo define el modelo ProductImage que gestiona las imágenes
asociadas a los productos con relación 1:N.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProductImage(BaseModel):
    """
    Modelo para imágenes de productos.
    
    Relación 1:N con Product (un producto puede tener múltiples imágenes).
    Gestiona metadatos de archivos y orden de visualización.
    """
    
    __tablename__ = "product_images"
    
    # Relación con producto
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del producto asociado"
    )
    
    # Información del archivo
    filename = Column(String(255), nullable=False, comment="Nombre único del archivo")
    original_filename = Column(String(255), nullable=False, comment="Nombre original del upload")
    file_path = Column(Text, nullable=False, comment="Ruta relativa del archivo")
    file_size = Column(Integer, nullable=False, comment="Tamaño en bytes")
    mime_type = Column(String(100), nullable=False, comment="Tipo MIME del archivo")
    
    # Metadatos de imagen
    width = Column(Integer, comment="Ancho en píxeles")
    height = Column(Integer, comment="Alto en píxeles")
    order_index = Column(Integer, default=0, comment="Orden de visualización (0 = principal)")
    
    # Relación inversa con Product
    product = relationship("Product", back_populates="images")
    
    # Índices para optimización
    __table_args__ = (
        Index('ix_product_image_product_order', 'product_id', 'order_index'),
        Index('ix_product_image_filename', 'filename'),
    )
    
    def __repr__(self) -> str:
        """Representación legible del modelo."""
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, filename={self.filename})>"
