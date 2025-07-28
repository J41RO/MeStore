# ~/app/models/inventory.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Inventario con Ubicación Física
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: inventory.py
# Ruta: ~/app/models/inventory.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Modelo Inventory para gestión de ubicación física de productos en almacén
#            Incluye campos de zona, estante, posición y control de cantidades
#
# Modificaciones:
# 2025-07-28 - Creación inicial del modelo con campos de ubicación
#
# ---------------------------------------------------------------------------------------------

"""
Modelo Inventory para gestión de ubicación física de productos.

Este módulo contiene:
- Clase Inventory: Modelo principal para tracking de ubicación física
- Campos de ubicación: zona, estante, posición para localización precisa
- Control de inventario: cantidad total y cantidad reservada
- Relationships: Conexiones con Product y User para integridad referencial
- Métodos de utilidad: Cálculos de disponibilidad y gestión de reservas
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class Inventory(BaseModel):

    def __init__(self, **kwargs):
        """Inicializar Inventory con valores por defecto seguros."""
        # Asegurar valores por defecto para campos numéricos
        kwargs.setdefault('cantidad', 0)
        kwargs.setdefault('cantidad_reservada', 0)
        super().__init__(**kwargs)
    """
    Modelo Inventory para gestión de ubicación física de productos.

    Gestiona la ubicación física de productos en el almacén con campos específicos
    para zona, estante y posición. Incluye control de cantidades disponibles y reservadas.

    Campos de ubicación:
    - zona: Zona del almacén (A, B, C, etc.)
    - estante: Número de estante dentro de la zona
    - posicion: Posición específica dentro del estante
    - product_id: Relación con Product (ForeignKey)
    - cantidad: Cantidad disponible en esa ubicación
    - cantidad_reservada: Cantidad reservada para órdenes
    - updated_by_id: Usuario que realizó la última actualización
    """

    __tablename__ = "inventory"

    # Relationship con Product
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey('products.id'),
        nullable=False,
        index=True,
        comment="ID del producto en inventario"
    )

    # Campos de ubicación física
    zona = Column(
        String(10),
        nullable=False,
        index=True,
        comment="Zona del almacén (A, B, C, etc.)"
    )

    estante = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Número de estante dentro de la zona"
    )

    posicion = Column(
        String(20),
        nullable=False,
        comment="Posición específica dentro del estante"
    )

    # Información de inventario
    cantidad = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Cantidad disponible en esta ubicación"
    )

    cantidad_reservada = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Cantidad reservada para órdenes"
    )

    # Tracking de cambios
    updated_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=True,
        comment="ID del usuario que actualizó el inventario"
    )

    # Relationships
    product = relationship(
        "Product",
        back_populates="ubicaciones_inventario"
    )

    updated_by = relationship(
        "User",
        backref="inventarios_actualizados"
    )

    # Constraints e índices
    __table_args__ = (
        Index('ix_inventory_location', 'zona', 'estante', 'posicion'),  # Búsqueda por ubicación
        Index('ix_inventory_product_location', 'product_id', 'zona', 'estante'),  # Producto + ubicación
        UniqueConstraint('product_id', 'zona', 'estante', 'posicion', name='uq_product_location'),  # Ubicación única por producto
    )

    def get_ubicacion_completa(self) -> str:
        """Obtener ubicación completa como string."""
        return f"{self.zona}-{self.estante}-{self.posicion}"

    def cantidad_disponible(self) -> int:
        """Calcular cantidad disponible (total - reservada)."""
        return max(0, self.cantidad - self.cantidad_reservada)

    def reservar_cantidad(self, cantidad: int) -> bool:
        """
        Reservar cantidad específica.

        Args:
            cantidad: Cantidad a reservar

        Returns:
            True si se pudo reservar, False si no hay suficiente stock
        """
        if self.cantidad_disponible() >= cantidad:
            self.cantidad_reservada += cantidad
            return True
        return False

    def liberar_reserva(self, cantidad: int) -> None:
        """
        Liberar cantidad reservada.

        Args:
            cantidad: Cantidad a liberar de la reserva
        """
        self.cantidad_reservada = max(0, self.cantidad_reservada - cantidad)

    def to_dict(self) -> dict:
        """Serializar inventario a diccionario."""
        base_dict = super().to_dict()
        inventory_dict = {
            "product_id": str(self.product_id) if self.product_id else None,
            "zona": self.zona,
            "estante": self.estante,
            "posicion": self.posicion,
            "ubicacion_completa": self.get_ubicacion_completa(),
            "cantidad": self.cantidad,
            "cantidad_reservada": self.cantidad_reservada,
            "cantidad_disponible": self.cantidad_disponible(),
            "updated_by_id": str(self.updated_by_id) if self.updated_by_id else None,
        }
        return {**base_dict, **inventory_dict}

    def __repr__(self) -> str:
        """Representación string del objeto Inventory."""
        return f"<Inventory {self.get_ubicacion_completa()}: {self.cantidad_disponible()}/{self.cantidad}>"