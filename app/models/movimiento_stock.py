# ~/app/models/movimiento_stock.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Movimientos de Stock
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: movimiento_stock.py
# Ruta: ~/app/models/movimiento_stock.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Modelo MovimientoStock para tracking de movimientos de inventario
#            Incluye historial completo y trazabilidad de cambios
#
# ---------------------------------------------------------------------------------------------

"""
Modelo MovimientoStock para tracking de movimientos de inventario.

Este módulo contiene:
- Clase MovimientoStock: Modelo principal para movimientos de stock
- Enum TipoMovimiento: Tipos de movimientos posibles
- Relationships: Conexiones con Inventory y User
- Campos de tracking: usuario, fecha, observaciones
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum
from enum import Enum as PyEnum
# UUID import removed for SQLite compatibility
from sqlalchemy.orm import relationship
from typing import Optional
from datetime import datetime

from .base import BaseModel


class TipoMovimiento(PyEnum):
    """
    Enumeración para tipos de movimientos de stock.
    
    Tipos de movimientos:
        INGRESO: Entrada de mercancía al inventario
        SALIDA: Salida de mercancía del inventario
        AJUSTE_POSITIVO: Ajuste positivo por corrección
        AJUSTE_NEGATIVO: Ajuste negativo por corrección
        TRANSFERENCIA: Transferencia entre ubicaciones
        DEVOLUCION: Devolución de mercancía
        MERMA: Pérdida por deterioro/robo
        RESERVA: Reserva para orden
        LIBERACION: Liberación de reserva
    """
    INGRESO = "INGRESO"
    SALIDA = "SALIDA"
    AJUSTE_POSITIVO = "AJUSTE_POSITIVO"
    AJUSTE_NEGATIVO = "AJUSTE_NEGATIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    DEVOLUCION = "DEVOLUCION"
    MERMA = "MERMA"
    RESERVA = "RESERVA"
    LIBERACION = "LIBERACION"


class MovimientoStock(BaseModel):
    """
    Modelo MovimientoStock para tracking de movimientos de inventario.
    
    Registra todos los movimientos de stock con información detallada
    para trazabilidad y control de inventario.
    
    Campos principales:
    - inventory_id: Referencia al item de inventario
    - tipo_movimiento: Tipo de movimiento realizado
    - cantidad_anterior: Cantidad antes del movimiento
    - cantidad_nueva: Cantidad después del movimiento
    - user_id: Usuario que realizó el movimiento
    - observaciones: Notas adicionales del movimiento
    """
    
    __tablename__ = "movimientos_stock"
    
    # Relación con Inventory
    inventory_id = Column(
        String(36),
        ForeignKey('inventory.id'),
        nullable=False,
        index=True,
        comment="ID del item de inventario afectado"
    )
    
    # Tipo de movimiento
    tipo_movimiento = Column(
        Enum(TipoMovimiento),
        nullable=False,
        index=True,
        comment="Tipo de movimiento realizado"
    )
    
    # Cantidades
    cantidad_anterior = Column(
        Integer,
        nullable=False,
        comment="Cantidad antes del movimiento"
    )
    
    cantidad_nueva = Column(
        Integer,
        nullable=False,
        comment="Cantidad después del movimiento"
    )
    
    # Usuario que realizó el movimiento
    user_id = Column(
        String(36),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="Usuario que realizó el movimiento"
    )
    
    # Observaciones del movimiento
    observaciones = Column(
        Text,
        nullable=True,
        comment="Observaciones y notas del movimiento"
    )
    
    # Fecha del movimiento
    fecha_movimiento = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Fecha y hora del movimiento"
    )
    
    # Campos adicionales para tracking
    referencia_externa = Column(
        String(100),
        nullable=True,
        comment="Referencia externa (factura, orden, etc.)"
    )
    
    lote = Column(
        String(50),
        nullable=True,
        comment="Número de lote si aplica"
    )
    
    ubicacion_origen = Column(
        String(100),
        nullable=True,
        comment="Ubicación origen para transferencias"
    )
    
    ubicacion_destino = Column(
        String(100),
        nullable=True,
        comment="Ubicación destino para transferencias"
    )
    
    # Relationships
    inventory = relationship("Inventory", back_populates="movimientos")
    user = relationship("User", backref="movimientos_realizados")
    
    def __init__(self, **kwargs):
        """Inicializar movimiento con defaults automáticos"""
        # Asegurar fecha de movimiento si no se proporciona
        if 'fecha_movimiento' not in kwargs:
            kwargs['fecha_movimiento'] = datetime.utcnow()
        
        # Llamar al constructor padre
        super().__init__(**kwargs)
    
    @property
    def diferencia_cantidad(self) -> int:
        """Calcular la diferencia de cantidad del movimiento"""
        return self.cantidad_nueva - self.cantidad_anterior
    
    @property
    def es_incremento(self) -> bool:
        """Verificar si el movimiento incrementa el stock"""
        return self.cantidad_nueva > self.cantidad_anterior
    
    @property
    def es_decremento(self) -> bool:
        """Verificar si el movimiento decrementa el stock"""
        return self.cantidad_nueva < self.cantidad_anterior
    
    def to_dict(self) -> dict:
        """Serializar movimiento a diccionario."""
        base_dict = super().to_dict()
        movimiento_dict = {
            "inventory_id": str(self.inventory_id) if self.inventory_id else None,
            "tipo_movimiento": self.tipo_movimiento.value if self.tipo_movimiento else None,
            "cantidad_anterior": self.cantidad_anterior,
            "cantidad_nueva": self.cantidad_nueva,
            "diferencia_cantidad": self.diferencia_cantidad,
            "user_id": str(self.user_id) if self.user_id else None,
            "observaciones": self.observaciones,
            "fecha_movimiento": self.fecha_movimiento.isoformat() if self.fecha_movimiento else None,
            "referencia_externa": self.referencia_externa,
            "lote": self.lote,
            "ubicacion_origen": self.ubicacion_origen,
            "ubicacion_destino": self.ubicacion_destino,
            "es_incremento": self.es_incremento,
            "es_decremento": self.es_decremento,
        }
        return {**base_dict, **movimiento_dict}
    
    def __repr__(self) -> str:
        """Representación string del objeto MovimientoStock."""
        return f"<MovimientoStock {self.tipo_movimiento.value}: {self.cantidad_anterior} → {self.cantidad_nueva}>"