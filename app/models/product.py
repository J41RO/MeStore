# ~/app/models/product.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo Product para gestión de productos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: product.py
# Ruta: ~/app/models/product.py
# Autor: Jairo
# Fecha de Creación: 2025-07-27
# Última Actualización: 2025-07-27
# Versión: 1.0.0
# Propósito: Modelo SQLAlchemy para entidad Product con campos básicos
#            Gestión de productos del marketplace (sku, name, description)
#
# Modificaciones:
# 2025-07-27 - Creación inicial del modelo Product básico
#
# ---------------------------------------------------------------------------------------------

"""
Modelo Product para MeStore.

Este módulo contiene el modelo SQLAlchemy para la entidad Product:
- Product: Modelo principal con campos básicos (sku, name, description)
- Herencia de BaseModel: UUID, timestamps automáticos y soft delete
- Métodos personalizados: __repr__, __str__, to_dict()
- Índices para optimización: sku (unique), name (búsquedas)
"""

from sqlalchemy import Column, String, Text, Index
from sqlalchemy.orm import validates

from app.models.base import BaseModel


class Product(BaseModel):
    """
    Modelo Product para gestión de productos del marketplace.

    Hereda de BaseModel los campos:
    - id: UUID primary key
    - created_at: Timestamp de creación
    - updated_at: Timestamp de última actualización  
    - deleted_at: Timestamp de soft delete (nullable)

    Campos específicos:
    - sku: Código único del producto (String 50 chars, unique, indexed)
    - name: Nombre del producto (String 200 chars, indexed)
    - description: Descripción detallada (Text, optional)
    """

    __tablename__ = "products"

    # Campos específicos del producto
    sku = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Código único del producto para identificación"
    )

    name = Column(
        String(200), 
        nullable=False, 
        index=True,
        comment="Nombre del producto para búsquedas"
    )

    description = Column(
        Text, 
        nullable=True,
        comment="Descripción detallada del producto"
    )

    # Índices adicionales para optimización
    __table_args__ = (
        Index('ix_product_name_sku', 'name', 'sku'),  # Índice compuesto
        Index('ix_product_created_at', 'created_at'),  # Para ordenamiento temporal
    )

    @validates('sku')
    def validate_sku(self, key, sku):
        """Validar formato de SKU."""
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU no puede estar vacío")
        if len(sku) > 50:
            raise ValueError("SKU no puede exceder 50 caracteres")
        return sku.strip().upper()  # Normalizar a mayúsculas

    @validates('name')
    def validate_name(self, key, name):
        """Validar nombre del producto."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Nombre del producto no puede estar vacío")
        if len(name) > 200:
            raise ValueError("Nombre no puede exceder 200 caracteres")
        return name.strip()

    def __repr__(self) -> str:
        """
        Representación técnica del objeto Product.

        Returns:
            str: Representación técnica con SKU y name
        """
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"

    def __str__(self) -> str:
        """
        Representación amigable del producto.

        Returns:
            str: String amigable del producto
        """
        return f"Producto {self.sku}: {self.name}"

    def to_dict(self) -> dict:
        """
        Serializar producto a diccionario.

        Returns:
            dict: Representación completa del producto
        """
        # Usar método base y extender con campos específicos
        base_dict = super().to_dict()
        product_dict = {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
        }
        return {**base_dict, **product_dict}

    def has_description(self) -> bool:
        """
        Verificar si el producto tiene descripción.

        Returns:
            bool: True si tiene descripción no vacía
        """
        return self.description is not None and len(self.description.strip()) > 0

    def get_display_name(self) -> str:
        """
        Obtener nombre para mostrar con SKU.

        Returns:
            str: Formato 'SKU - Name' para displays
        """
        return f"{self.sku} - {self.name}"
