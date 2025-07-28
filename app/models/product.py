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
# Última Actualización: 2025-07-28
# Versión: 1.2.0
# Propósito: Modelo SQLAlchemy para entidad Product con campos básicos, pricing y fulfillment
#            Gestión de productos del marketplace (sku, name, description, pricing, logística)
#
# Modificaciones:
# 2025-07-27 - Creación inicial del modelo Product básico
# 2025-07-28 - Añadidos campos de pricing (precio_venta, precio_costo, comision_mestocker)
# 2025-07-28 - Añadidos campos de fulfillment (peso, dimensiones, categoria, tags)
#
# ---------------------------------------------------------------------------------------------

"""
Modelo Product para MeStore.

Este módulo contiene el modelo SQLAlchemy para la entidad Product:
- Product: Modelo principal con campos básicos (sku, name, description)
- Campos de pricing: precio_venta, precio_costo, comision_mestocker
- Campos de fulfillment: peso, dimensiones, categoria, tags
- Herencia de BaseModel: UUID, timestamps automáticos y soft delete
- Métodos personalizados: __repr__, __str__, to_dict()
- Métodos de negocio: calcular_margen(), calcular_porcentaje_margen()
- Métodos de fulfillment: calcular_volumen(), tiene_tag()
- Índices para optimización: sku (unique), name (búsquedas), categoria
"""

from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import DECIMAL
from sqlalchemy import Enum
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.models.base import BaseModel


class ProductStatus(PyEnum):
    """
    Enumeración para estados del producto en el marketplace.

    Estados del flujo de vida del producto:
        TRANSITO: Producto en tránsito hacia almacén
        VERIFICADO: Producto verificado y en proceso de catalogación
        DISPONIBLE: Producto disponible para venta
        VENDIDO: Producto vendido y no disponible
    """
    TRANSITO = "TRANSITO"
    VERIFICADO = "VERIFICADO"
    DISPONIBLE = "DISPONIBLE"
    VENDIDO = "VENDIDO"


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
    - status: Estado del producto (Enum ProductStatus)
    
    Campos de pricing:
    - precio_venta: Precio de venta al público (DECIMAL 10,2)
    - precio_costo: Precio de costo/compra (DECIMAL 10,2)
    - comision_mestocker: Comisión de MeStore (DECIMAL 10,2)
    
    Campos de fulfillment:
    - peso: Peso del producto en kilogramos (DECIMAL 8,3)
    - dimensiones: Dimensiones del producto en JSON {largo, ancho, alto} cm
    - categoria: Categoría del producto (String 100 chars, indexed)
    - tags: Tags del producto como array JSON para búsquedas
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

    # Relationship con User (vendedor)
    vendedor_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="ID del usuario vendedor que registró el producto"
    )

    # Tracking de cambios
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=True,
        comment="ID del usuario que creó el producto"
    )

    updated_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=True,
        comment="ID del usuario que actualizó por última vez"
    )

    version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Versión del producto para control de cambios"
    )
    # Relationships
    vendedor = relationship(
        "User",
        foreign_keys=[vendedor_id],
        back_populates="productos_vendidos"
    )

    created_by = relationship(
        "User", 
        foreign_keys=[created_by_id],
        backref="productos_creados"
    )

    updated_by = relationship(
        "User",
        foreign_keys=[updated_by_id],
        backref="productos_actualizados"
    )

    # Inventory relationship
    ubicaciones_inventario = relationship(
        "Inventory",
        back_populates="product"
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

    status = Column(
        Enum(ProductStatus),
        nullable=False,
        default=ProductStatus.TRANSITO,
        comment="Estado actual del producto en el marketplace"
    )

    # Campos de pricing
    precio_venta = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Precio de venta al público (COP)"
    )

    precio_costo = Column(
        DECIMAL(10, 2), 
        nullable=True,
        comment="Precio de costo/compra del producto (COP)"
    )

    comision_mestocker = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Comisión de MeStore por venta del producto (COP)"
    )

    # Campos de fulfillment
    peso = Column(
        DECIMAL(8, 3),
        nullable=True,
        comment="Peso del producto en kilogramos"
    )

    dimensiones = Column(
        JSON,
        nullable=True,
        comment="Dimensiones del producto: {largo, ancho, alto} en cm"
    )

    categoria = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Categoría del producto para organización"
    )

    tags = Column(
        JSON,
        nullable=True,
        comment="Tags del producto como array JSON para búsquedas"
    )

    # Índices adicionales para optimización
    __table_args__ = (
        Index('ix_product_name_sku', 'name', 'sku'),  # Índice compuesto
        Index('ix_product_created_at', 'created_at'),  # Para ordenamiento temporal
    )

    def __init__(self, **kwargs):
        """
        Inicializar Product con default status si no se especifica.

        Args:
            **kwargs: Argumentos para crear el producto
        """
        # Si no se especifica status, aplicar default
        if 'status' not in kwargs:
            kwargs['status'] = ProductStatus.TRANSITO

        # Llamar al __init__ de BaseModel
        super().__init__(**kwargs)

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

    def set_vendedor(self, user_id: UUID) -> None:
        """Asignar vendedor al producto"""
        self.vendedor_id = user_id
        self.increment_version()

    def increment_version(self) -> None:
        """Incrementar versión para tracking"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1

    def update_tracking(self, user_id: UUID) -> None:
        """Actualizar tracking de cambios"""
        self.updated_by_id = user_id
        self.increment_version()

    def is_vendido_por(self, user_id: UUID) -> bool:
        """Verificar si producto es vendido por usuario específico"""
        return self.vendedor_id == user_id

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
            dict: Representación completa del producto incluyendo fulfillment
        """
        # Usar método base y extender con campos específicos
        base_dict = super().to_dict()
        product_dict = {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "precio_venta": float(self.precio_venta) if self.precio_venta else None,
            "precio_costo": float(self.precio_costo) if self.precio_costo else None,
            "comision_mestocker": float(self.comision_mestocker) if self.comision_mestocker else None,
            "peso": float(self.peso) if self.peso else None,
            "dimensiones": self.dimensiones,
            "categoria": self.categoria,
            "tags": self.tags,
            "vendedor_id": str(self.vendedor_id) if self.vendedor_id else None,
            "created_by_id": str(self.created_by_id) if self.created_by_id else None,
            "updated_by_id": str(self.updated_by_id) if self.updated_by_id else None,
            "version": self.version,
        }
        return {**base_dict, **product_dict}

    def calcular_margen(self) -> float:
        """
        Calcular margen de ganancia.
        
        Returns:
            float: Margen en COP (precio_venta - precio_costo)
        """
        if self.precio_venta and self.precio_costo:
            return float(self.precio_venta - self.precio_costo)
        return 0.0

    def calcular_porcentaje_margen(self) -> float:
        """
        Calcular porcentaje de margen.
        
        Returns:
            float: Porcentaje de margen sobre precio_costo
        """
        if self.precio_venta and self.precio_costo and self.precio_costo > 0:
            return float((self.precio_venta - self.precio_costo) / self.precio_costo * 100)
        return 0.0

    def calcular_volumen(self) -> float:
        """
        Calcular volumen en cm³ desde dimensiones.
        
        Returns:
            float: Volumen en cm³ o 0.0 si no hay dimensiones válidas
        """
        if self.dimensiones and all(k in self.dimensiones for k in ['largo', 'ancho', 'alto']):
            return float(self.dimensiones['largo'] * self.dimensiones['ancho'] * self.dimensiones['alto'])
        return 0.0

    def tiene_tag(self, tag: str) -> bool:
        """
        Verificar si producto tiene un tag específico.
        
        Args:
            tag: Tag a buscar (case insensitive)
            
        Returns:
            bool: True si el producto tiene el tag especificado
        """
        if self.tags and isinstance(self.tags, list):
            return tag.lower() in [t.lower() for t in self.tags]
        return False

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