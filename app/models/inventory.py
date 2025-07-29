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
# Versión: 1.2.0
# Propósito: Modelo Inventory para gestión de ubicación física de productos en almacén
#            Incluye campos de zona, estante, posición, control de cantidades y calidad
#
# Modificaciones:
# 2025-07-28 - Creación inicial del modelo con campos de ubicación
# 2025-07-28 - Agregado enum InventoryStatus y métodos de transición
# 2025-07-28 - Agregado enum CondicionProducto y campos de calidad
#
# ---------------------------------------------------------------------------------------------

"""
Modelo Inventory para gestión de ubicación física de productos.

Este módulo contiene:
- Clase Inventory: Modelo principal para tracking de ubicación física
- Enum InventoryStatus: Estados del proceso de fulfillment
- Enum CondicionProducto: Estados de calidad del producto
- Campos de ubicación: zona, estante, posición para localización precisa
- Control de inventario: cantidad total y cantidad reservada
- Campos de calidad: condicion_producto y notas_almacen
- Relationships: Conexiones con Product y User para integridad referencial
- Métodos de utilidad: Cálculos de disponibilidad y gestión de reservas
- Métodos de transición: Control de estados del proceso de fulfillment
- Métodos de calidad: Business logic para condición del producto
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Index, UniqueConstraint, DateTime, Enum, Text
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Optional, List

from .base import BaseModel
from datetime import datetime


class InventoryStatus(PyEnum):
    """
    Enumeración para estados del inventario en el proceso de fulfillment.

    Estados del flujo de fulfillment:
        DISPONIBLE: Inventario disponible para reservar
        RESERVADO: Inventario reservado para una orden
        EN_PICKING: Inventario en proceso de picking
        DESPACHADO: Inventario despachado y fuera del almacén
    """
    DISPONIBLE = "DISPONIBLE"
    RESERVADO = "RESERVADO"
    EN_PICKING = "EN_PICKING"
    DESPACHADO = "DESPACHADO"


class CondicionProducto(PyEnum):
    """
    Enumeración para condición física del producto en inventario.
    
    Estados de calidad del producto:
        NUEVO: Producto completamente nuevo, sin uso
        USADO_EXCELENTE: Producto usado en excelente estado
        USADO_BUENO: Producto usado en buen estado
        USADO_REGULAR: Producto usado con desgaste visible
        DAÑADO: Producto con daños significativos
    """
    NUEVO = "NUEVO"
    USADO_EXCELENTE = "USADO_EXCELENTE"
    USADO_BUENO = "USADO_BUENO"
    USADO_REGULAR = "USADO_REGULAR"
    DAÑADO = "DAÑADO"


class Inventory(BaseModel):
    """
    Modelo Inventory para gestión de ubicación física de productos.

    Gestiona la ubicación física de productos en el almacén con campos específicos
    para zona, estante y posición. Incluye control de cantidades disponibles y reservadas,
    así como sistema de calidad para tracking de condición del producto.

    Campos de ubicación:
    - zona: Zona del almacén (A, B, C, etc.)
    - estante: Número de estante dentro de la zona
    - posicion: Posición específica dentro del estante
    - product_id: Relación con Product (ForeignKey)
    - cantidad: Cantidad disponible en esa ubicación
    - cantidad_reservada: Cantidad reservada para órdenes
    - updated_by_id: Usuario que realizó la última actualización
    - status: Estado en el proceso de fulfillment
    - condicion_producto: Estado de calidad del producto
    - notas_almacen: Observaciones del personal de almacén
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

    # Estado del inventario en el proceso de fulfillment
    status = Column(
        Enum(InventoryStatus),
        nullable=False,
        default=InventoryStatus.DISPONIBLE,
        comment="Estado del inventario en el proceso de fulfillment"
    )

    # Campos de calidad del producto
    condicion_producto = Column(
        Enum(CondicionProducto),
        nullable=False,
        default=CondicionProducto.NUEVO,
        comment="Condición física del producto en inventario"
    )

    notas_almacen = Column(
        Text,
        nullable=True,
        comment="Observaciones y notas del personal de almacén"
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

    user = relationship(
        "User",
        back_populates="ubicaciones_inventario"
    )
    # Constraints e índices
    __table_args__ = (
        Index('ix_inventory_location', 'zona', 'estante', 'posicion'),
        Index('ix_inventory_product_location', 'product_id', 'zona', 'estante'),
        UniqueConstraint('product_id', 'zona', 'estante', 'posicion', name='uq_product_location'),
    )

    def __init__(self, **kwargs):
        """Inicializar inventario con defaults automáticos"""
        # Asegurar valores por defecto para campos numéricos
        kwargs.setdefault('cantidad', 0)
        kwargs.setdefault('cantidad_reservada', 0)
        
        # CRÍTICO: Asegurar status por defecto
        kwargs.setdefault('status', InventoryStatus.DISPONIBLE)
        kwargs.setdefault('condicion_producto', CondicionProducto.NUEVO)
        
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

    # Métodos de transición de estado
    def reservar_inventario(self, user_id: Optional[UUID] = None) -> bool:
        """Transición a estado RESERVADO"""
        if self.status == InventoryStatus.DISPONIBLE and self.cantidad_disponible() > 0:
            self.status = InventoryStatus.RESERVADO
            self.actualizar_fecha_movimiento(user_id)
            return True
        return False

    def iniciar_picking(self, user_id: Optional[UUID] = None) -> bool:
        """Transición a estado EN_PICKING"""
        if self.status == InventoryStatus.RESERVADO:
            self.status = InventoryStatus.EN_PICKING
            self.actualizar_fecha_movimiento(user_id)
            return True
        return False

    def completar_despacho(self, user_id: Optional[UUID] = None) -> bool:
        """Transición a estado DESPACHADO"""
        if self.status == InventoryStatus.EN_PICKING:
            self.status = InventoryStatus.DESPACHADO
            self.actualizar_fecha_movimiento(user_id)
            return True
        return False

    def liberar_a_disponible(self, user_id: Optional[UUID] = None) -> bool:
        """Volver a estado DISPONIBLE (cancelación)"""
        if self.status in [InventoryStatus.RESERVADO, InventoryStatus.EN_PICKING]:
            self.status = InventoryStatus.DISPONIBLE
            self.actualizar_fecha_movimiento(user_id)
            return True
        return False

    # Métodos de validación de transiciones
    def puede_transicionar_a(self, nuevo_status: InventoryStatus) -> bool:
        """Verificar si puede transicionar a un estado específico"""
        transiciones_validas = {
            InventoryStatus.DISPONIBLE: [InventoryStatus.RESERVADO],
            InventoryStatus.RESERVADO: [InventoryStatus.EN_PICKING, InventoryStatus.DISPONIBLE],
            InventoryStatus.EN_PICKING: [InventoryStatus.DESPACHADO, InventoryStatus.DISPONIBLE],
            InventoryStatus.DESPACHADO: []  # Estado final
        }
        return nuevo_status in transiciones_validas.get(self.status, [])

    def obtener_transiciones_disponibles(self) -> List[InventoryStatus]:
        """Obtener lista de estados a los que puede transicionar"""
        transiciones = {
            InventoryStatus.DISPONIBLE: [InventoryStatus.RESERVADO],
            InventoryStatus.RESERVADO: [InventoryStatus.EN_PICKING, InventoryStatus.DISPONIBLE],
            InventoryStatus.EN_PICKING: [InventoryStatus.DESPACHADO, InventoryStatus.DISPONIBLE],
            InventoryStatus.DESPACHADO: []
        }
        return transiciones.get(self.status, [])

    # Métodos de consulta de estado
    def esta_disponible(self) -> bool:
        """Verificar si está en estado DISPONIBLE"""
        return self.status == InventoryStatus.DISPONIBLE

    def esta_reservado(self) -> bool:
        """Verificar si está en estado RESERVADO"""
        return self.status == InventoryStatus.RESERVADO

    def esta_en_picking(self) -> bool:
        """Verificar si está en estado EN_PICKING"""
        return self.status == InventoryStatus.EN_PICKING

    def esta_despachado(self) -> bool:
        """Verificar si está en estado DESPACHADO"""
        return self.status == InventoryStatus.DESPACHADO

    # Métodos de calidad del producto
    def es_producto_nuevo(self) -> bool:
        """Verificar si el producto está en condición nueva"""
        return self.condicion_producto == CondicionProducto.NUEVO

    def es_producto_usado(self) -> bool:
        """Verificar si el producto está usado (cualquier condición)"""
        return self.condicion_producto in [
            CondicionProducto.USADO_EXCELENTE,
            CondicionProducto.USADO_BUENO,
            CondicionProducto.USADO_REGULAR
        ]

    def requiere_inspeccion(self) -> bool:
        """Verificar si requiere inspección especial"""
        return self.condicion_producto in [
            CondicionProducto.USADO_REGULAR,
            CondicionProducto.DAÑADO
        ]

    def es_vendible(self) -> bool:
        """Verificar si está en condición vendible"""
        return self.condicion_producto != CondicionProducto.DAÑADO

    def tiene_notas(self) -> bool:
        """Verificar si tiene notas del almacén"""
        return self.notas_almacen is not None and len(self.notas_almacen.strip()) > 0

    def obtener_condicion_descripcion(self) -> str:
        """Obtener descripción legible de la condición"""
        descripciones = {
            CondicionProducto.NUEVO: "Producto nuevo",
            CondicionProducto.USADO_EXCELENTE: "Usado - Excelente estado",
            CondicionProducto.USADO_BUENO: "Usado - Buen estado",
            CondicionProducto.USADO_REGULAR: "Usado - Estado regular",
            CondicionProducto.DAÑADO: "Producto dañado"
        }
        return descripciones.get(self.condicion_producto, "Condición desconocida")

    def obtener_nivel_calidad(self) -> int:
        """Obtener nivel numérico de calidad (1-5, donde 5 es mejor)"""
        niveles = {
            CondicionProducto.DAÑADO: 1,
            CondicionProducto.USADO_REGULAR: 2,
            CondicionProducto.USADO_BUENO: 3,
            CondicionProducto.USADO_EXCELENTE: 4,
            CondicionProducto.NUEVO: 5
        }
        return niveles.get(self.condicion_producto, 0)

    def agregar_nota_almacen(self, nota: str, user_id: Optional[UUID] = None) -> None:
        """Agregar o actualizar nota del almacén"""
        fecha_actual = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        nueva_nota = f"[{fecha_actual}] {nota}"
        
        if self.notas_almacen:
            self.notas_almacen = f"{self.notas_almacen}\n{nueva_nota}"
        else:
            self.notas_almacen = nueva_nota
        
        self.actualizar_fecha_movimiento(user_id)

    def esta_en_proceso(self) -> bool:
        """Verificar si está en algún proceso (no disponible ni despachado)"""
        return self.status in [InventoryStatus.RESERVADO, InventoryStatus.EN_PICKING]

    # Métodos de utilidad de tiempo
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

    # Métodos de ubicación y stock
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
        self.actualizar_fecha_movimiento(user_id)

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

    def reservar_cantidad(self, cantidad: int, user_id: Optional[UUID] = None) -> bool:
        """
        Reservar cantidad específica.

        Args:
            cantidad: Cantidad a reservar
            user_id: ID del usuario que realiza la reserva

        Returns:
            True si se pudo reservar, False si no hay suficiente stock
        """
        # Asegurar que tenga status inicializado
        if self.status is None:
            self.status = InventoryStatus.DISPONIBLE
        
        if self.cantidad_disponible() >= cantidad and self.esta_disponible():
            self.cantidad_reservada += cantidad
            if self.cantidad_reservada > 0:
                self.reservar_inventario(user_id)
            else:
                self.actualizar_fecha_movimiento(user_id)
            return True
        return False

    def liberar_reserva(self, cantidad: int, user_id: Optional[UUID] = None) -> None:
        """
        Liberar cantidad reservada.

        Args:
            cantidad: Cantidad a liberar de la reserva
            user_id: ID del usuario que libera la reserva
        """
        cantidad_anterior = self.cantidad_reservada
        self.cantidad_reservada = max(0, self.cantidad_reservada - cantidad)
        
        # Si se libera toda la reserva y está en RESERVADO, volver a DISPONIBLE
        if cantidad_anterior > 0 and self.cantidad_reservada == 0 and self.esta_reservado():
            self.liberar_a_disponible(user_id)
        else:
            self.actualizar_fecha_movimiento(user_id)

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
            "status": self.status.value if self.status else None,
            "status_descripcion": self.status.value.replace("_", " ").title() if self.status else None,
            # Campos de calidad del producto
            "condicion_producto": self.condicion_producto.value if self.condicion_producto else None,
            "condicion_descripcion": self.obtener_condicion_descripcion(),
            "nivel_calidad": self.obtener_nivel_calidad(),
            "notas_almacen": self.notas_almacen,
            "es_nuevo": self.es_producto_nuevo(),
            "es_vendible": self.es_vendible(),
            "requiere_inspeccion": self.requiere_inspeccion(),
            "tiene_notas": self.tiene_notas(),
            "puede_reservar": self.esta_disponible() and self.cantidad_disponible() > 0,
            "transiciones_disponibles": [s.value for s in self.obtener_transiciones_disponibles()],
            "es_reciente": self.es_reciente(),
            "tiempo_sin_movimiento": self.tiempo_sin_movimiento(),
        }
        return {**base_dict, **inventory_dict}

    def __repr__(self) -> str:
        """Representación string del objeto Inventory."""
        return f"<Inventory {self.get_ubicacion_completa()}: {self.cantidad_disponible()}/{self.cantidad} [{self.status.value}] [{self.condicion_producto.value}]>"