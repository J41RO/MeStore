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

from sqlalchemy import Column, String, Integer, ForeignKey, Index, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel
from datetime import datetime
from typing import Optional


class Inventory(BaseModel):

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

    # Campos de fechas específicos del inventario
    fecha_ingreso = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha de ingreso del producto al inventario"
    )

    fecha_ultimo_movimiento = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Fecha del último movimiento de stock"
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

    def __init__(self, **kwargs):
        """Inicializar inventario con defaults automáticos"""
        # Asegurar valores por defecto para campos numéricos
        kwargs.setdefault('cantidad', 0)
        kwargs.setdefault('cantidad_reservada', 0)
        
        # Inicializar campos fecha si no se proporcionan
        if 'fecha_ingreso' not in kwargs:
            kwargs['fecha_ingreso'] = datetime.utcnow()
        if 'fecha_ultimo_movimiento' not in kwargs:
            kwargs['fecha_ultimo_movimiento'] = datetime.utcnow()
        
        # Llamar al constructor padre
        super().__init__(**kwargs)


    # Métodos de utilidad para fechas
    def dias_desde_ingreso(self) -> int:
        """Calcular días desde el ingreso del producto"""
        if not self.fecha_ingreso:
            return 0
        delta = datetime.utcnow() - self.fecha_ingreso
        return delta.days

    def dias_desde_ultimo_movimiento(self) -> int:
        """Calcular días desde el último movimiento"""
        if not self.fecha_ultimo_movimiento:
            return 0
        delta = datetime.utcnow() - self.fecha_ultimo_movimiento
        return delta.days

    def actualizar_fecha_movimiento(self, user_id: Optional[UUID] = None) -> None:
        """Actualizar fecha del último movimiento"""
        self.fecha_ultimo_movimiento = datetime.utcnow()
        if user_id:
            self.updated_by_id = user_id
        
    def es_reciente(self, dias: int = 7) -> bool:
        """Verificar si el ingreso es reciente (por defecto 7 días)"""
        return self.dias_desde_ingreso() <= dias

    def es_movimiento_reciente(self, dias: int = 30) -> bool:
        """Verificar si el último movimiento es reciente (por defecto 30 días)"""
        return self.dias_desde_ultimo_movimiento() <= dias

    def tiempo_sin_movimiento(self) -> str:
        """Obtener descripción del tiempo sin movimiento"""
        dias = self.dias_desde_ultimo_movimiento()
        if dias == 0:
            return "Hoy"
        elif dias == 1:
            return "1 día"
        elif dias < 7:
            return f"{dias} días"
        elif dias < 30:
            semanas = dias // 7
            return f"{semanas} semana{'s' if semanas > 1 else ''}"
        elif dias < 365:
            meses = dias // 30
            return f"{meses} mes{'es' if meses > 1 else ''}"
        else:
            años = dias // 365
            return f"{años} año{'s' if años > 1 else ''}"


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

    def actualizar_stock(self, nueva_cantidad: int, user_id: Optional[UUID] = None) -> None:
        """
        Actualizar stock total manteniendo reservas

        Args:
            nueva_cantidad: Nueva cantidad total
            user_id: ID del usuario que realiza la actualización
        """
        if nueva_cantidad < self.cantidad_reservada:
            raise ValueError(f"Nueva cantidad ({nueva_cantidad}) no puede ser menor que cantidad reservada ({self.cantidad_reservada})")

        self.cantidad = nueva_cantidad
        if user_id:
            # Auto-actualizar fecha de último movimiento
            self.actualizar_fecha_movimiento(user_id)
            self.updated_by_id = user_id

    def ajustar_stock(self, diferencia: int, user_id: Optional[UUID] = None) -> None:
        """
        Ajustar stock con diferencia (+/-)

        Args:
            diferencia: Cantidad a sumar/restar
            user_id: ID del usuario que realiza el ajuste
        """
        nueva_cantidad = self.cantidad + diferencia
        if nueva_cantidad < 0:
            raise ValueError(f"El ajuste resulta en cantidad negativa: {nueva_cantidad}")

        self.actualizar_stock(nueva_cantidad, user_id)

    def esta_sin_stock(self) -> bool:
        """Verificar si la ubicación está sin stock"""
        return self.cantidad_disponible() == 0

    def puede_satisfacer(self, cantidad_requerida: int) -> bool:
        """Verificar si puede satisfacer una cantidad requerida"""
        return self.cantidad_disponible() >= cantidad_requerida

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
            self.actualizar_fecha_movimiento()  # Auto-update fecha
            return True
        return False

    def liberar_reserva(self, cantidad: int) -> None:
        """
        Liberar cantidad reservada.

        Args:
            cantidad: Cantidad a liberar de la reserva
        """
        self.cantidad_reservada = max(0, self.cantidad_reservada - cantidad)
        self.actualizar_fecha_movimiento()  # Auto-update fecha

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
            "fecha_ingreso": self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            "fecha_ultimo_movimiento": self.fecha_ultimo_movimiento.isoformat() if self.fecha_ultimo_movimiento else None,
            "dias_desde_ingreso": self.dias_desde_ingreso(),
            "dias_desde_ultimo_movimiento": self.dias_desde_ultimo_movimiento(),
            "es_reciente": self.es_reciente(),
            "tiempo_sin_movimiento": self.tiempo_sin_movimiento(),
        }
        return {**base_dict, **inventory_dict}

    def __repr__(self) -> str:
        """Representación string del objeto Inventory."""
        return f"<Inventory {self.get_ubicacion_completa()}: {self.cantidad_disponible()}/{self.cantidad}>"