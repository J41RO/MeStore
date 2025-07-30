# ~/app/models/storage.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo Storage para Espacios de Almacenamiento
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: storage.py
# Ruta: ~/app/models/storage.py
# Autor: Jairo
# Fecha de Creación: 2025-07-29
# Última Actualización: 2025-07-29
# Versión: 1.0.0
# Propósito: Modelo SQLAlchemy Storage para gestión de espacios de almacenamiento
#            Incluye campos tipo y capacidad_max con validaciones
#
# Modificaciones:
# 2025-07-29 - Creación inicial del modelo Storage
#
# ---------------------------------------------------------------------------------------------

"""
Storage Model para MeStore Marketplace.

Este módulo contiene:
- Storage: Modelo principal para espacios de almacenamiento
- Campos de espacio: tipo y capacidad_max
- Herencia de BaseModel: UUID, timestamps automáticos y soft delete
- Métodos personalizados para gestión de espacios
"""

from sqlalchemy import Boolean, CheckConstraint, Column, DECIMAL, Enum, ForeignKey, Index, Integer, String, DateTime
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import relationship, validates
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as PyEnum
from datetime import datetime

from app.models.base import BaseModel


class StorageType(PyEnum):
   """
   Enumeración para tipos de espacios de almacenamiento.

   Tipos disponibles:
       PEQUENO: Espacio pequeño para pocos productos
       MEDIANO: Espacio mediano para cantidades moderadas
       GRANDE: Espacio grande para alto volumen
       ESPECIAL: Espacio especial para productos únicos
   """
   PEQUENO = "PEQUENO"
   MEDIANO = "MEDIANO"
   GRANDE = "GRANDE"
   ESPECIAL = "ESPECIAL"


class Storage(BaseModel):
    """
    Modelo Storage para gestión de espacios de almacenamiento del marketplace.

    Campos principales:
    - tipo: Tipo de espacio de almacenamiento (string)
    - capacidad_max: Capacidad máxima en número de productos

    Hereda de BaseModel:
    - id (UUID): Identificador único
    - created_at (DateTime): Fecha de creación
    - updated_at (DateTime): Fecha de última actualización
    - deleted_at (DateTime): Fecha de eliminación lógica
    """

    __tablename__ = "storages"

    # Campos de espacio básicos
    tipo = Column(
        Enum(StorageType),
        nullable=False,
        default=0,
        index=True,
        comment="Tipo de espacio de almacenamiento",
    )

    capacidad_max = Column(
        Integer, 
        nullable=False, 
        comment="Capacidad máxima en número de productos"
    )

    # Relationship con User (vendedor)
    vendedor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="ID del usuario vendedor propietario del espacio"
    )

    # Campos de tracking de ocupación
    productos_actuales = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Número actual de productos almacenados"
    )

    ocupacion_actual = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=0.00,
        comment="Porcentaje actual de ocupación (0.00 a 100.00)"
    )

    ultima_actualizacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha de última actualización del tracking"
    )

    # Campos de pricing
    tarifa_mensual = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Tarifa mensual del espacio de almacenamiento (COP)"
    )

    tarifa_por_producto = Column(
        DECIMAL(12, 2), 
        nullable=True,
        comment="Tarifa por producto almacenado (COP)"
    )

    # Relationships (DESPUÉS de todos los campos)

    def __init__(self, **kwargs):
        """Constructor con defaults Python para campos de tracking"""
        # Establecer defaults antes de llamar super().__init__
        if 'productos_actuales' not in kwargs:
            kwargs['productos_actuales'] = 0
        if 'ocupacion_actual' not in kwargs:
            kwargs['ocupacion_actual'] = Decimal('0.00')

        super().__init__(**kwargs)
    vendedor = relationship(
        "User",
        foreign_keys=[vendedor_id],
        back_populates="espacios_storage"
    )

    # Campos de contrato
    fecha_inicio = Column(
        DateTime,
        nullable=True,
        comment="Fecha de inicio del contrato de almacenamiento"
    )

    fecha_fin = Column(
        DateTime,
        nullable=True,
        comment="Fecha de finalización del contrato de almacenamiento"
    )

    renovacion_automatica = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indica si el contrato se renueva automáticamente"
    )

    # Constraints e índices
    __table_args__ = (
        Index("ix_storage_tipo_capacidad", "tipo", "capacidad_max"),
        CheckConstraint("capacidad_max > 0", name="ck_storage_capacidad_positive"),
        CheckConstraint("productos_actuales >= 0", name="ck_storage_productos_actuales_positive"),
        CheckConstraint("ocupacion_actual >= 0 AND ocupacion_actual <= 100", name="ck_storage_ocupacion_valid"),
        CheckConstraint("tarifa_mensual >= 0", name="ck_storage_tarifa_mensual_positive"),
        CheckConstraint("tarifa_por_producto >= 0", name="ck_storage_tarifa_por_producto_positive"),
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin > fecha_inicio", 
            name="ck_storage_fechas_validas"
        ),
    )

    @validates("capacidad_max")
    def validate_capacidad_max(self, key, value):
        """Validar que la capacidad máxima sea positiva"""
        if value is not None and value <= 0:
            raise ValueError("La capacidad máxima debe ser mayor a 0")
        return value

    @validates('fecha_fin')
    def validate_fecha_fin(self, key, value):
        """Validar que fecha_fin sea posterior a fecha_inicio"""
        if value and self.fecha_inicio and value <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        return value

    @validates('fecha_inicio')
    def validate_fecha_inicio(self, key, value):
        """Validar fecha_inicio"""
        if value and self.fecha_fin and value >= self.fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        return value

    @validates('tarifa_mensual')
    def validate_tarifa_mensual(self, key, value):
        """Validar que la tarifa mensual sea positiva o None"""
        if value is not None and value < 0:
            raise ValueError("La tarifa mensual debe ser mayor o igual a 0")
        return value

    @validates('tarifa_por_producto') 
    def validate_tarifa_por_producto(self, key, value):
        """Validar que la tarifa por producto sea positiva o None"""
        if value is not None and value < 0:
            raise ValueError("La tarifa por producto debe ser mayor o igual a 0")
        return value

    @validates("tipo")
    def validate_tipo(self, key, value):
        """Validar que el tipo sea un StorageType válido."""
        if value:
            # Si recibimos enum, obtener su valor
            if isinstance(value, StorageType):
                return value
            # Si es string, normalizar y convertir a enum
            value = value.strip().upper()
            try:
                return StorageType(value)
            except ValueError:
                allowed_tipos = [t.value for t in StorageType]
                raise ValueError(
                    f"Tipo de almacenamiento inválido. Debe ser uno de: {', '.join(allowed_tipos)}"
                )
        return value

    # Métodos de tracking de ocupación
    def actualizar_ocupacion(self) -> None:
        """Actualizar porcentaje de ocupación basado en productos actuales"""
        if self.capacidad_max > 0:
            self.ocupacion_actual = Decimal(str(min((self.productos_actuales / self.capacidad_max) * 100, 100.0)))
            self.ultima_actualizacion = datetime.utcnow()

    def agregar_productos(self, cantidad: int) -> bool:
        """Agregar productos y actualizar tracking"""
        if cantidad <= 0:
            return False
        
        if self.productos_actuales + cantidad <= self.capacidad_max:
            self.productos_actuales += cantidad
            self.actualizar_ocupacion()
            return True
        return False

    def remover_productos(self, cantidad: int) -> bool:
        """Remover productos y actualizar tracking"""
        if cantidad <= 0:
            return False
        
        if self.productos_actuales >= cantidad:
            self.productos_actuales -= cantidad
            self.actualizar_ocupacion()
            return True
        return False

    def get_espacio_disponible(self) -> int:
        """Obtener espacio disponible en número de productos"""
        return max(0, self.capacidad_max - self.productos_actuales)

    def calcular_ocupacion_porcentaje(self, productos_actuales: int) -> float:
        """Calcular porcentaje de ocupación del storage"""
        if self.capacidad_max <= 0 or productos_actuales < 0:
            return 0.0
        return min((productos_actuales / self.capacidad_max) * 100, 100.0)

    def productos_disponibles(self, productos_actuales: int) -> int:
        """Calcular cuántos productos más se pueden almacenar"""
        return max(0, self.capacidad_max - productos_actuales)

    def esta_lleno(self, productos_actuales: int) -> bool:
        """Verificar si el storage está lleno"""
        return productos_actuales >= self.capacidad_max

    def puede_almacenar(self, productos_actuales: int, cantidad_nueva: int) -> bool:
        """Verificar si se puede almacenar una cantidad adicional"""
        return (productos_actuales + cantidad_nueva) <= self.capacidad_max

    def calcular_costo_mensual(self, productos_actuales: int) -> Decimal:
        """Calcular costo mensual total (tarifa base + tarifa por productos)"""
        costo_total = Decimal('0.00')

        # Agregar tarifa mensual base si existe
        if self.tarifa_mensual is not None:
            costo_total += self.tarifa_mensual

        # Agregar tarifa por productos si existe
        if self.tarifa_por_producto is not None and productos_actuales > 0:
            costo_total += self.tarifa_por_producto * Decimal(str(productos_actuales))

        return costo_total

    def es_gratis(self) -> bool:
        """Verificar si el storage es gratuito"""
        return (self.tarifa_mensual is None or self.tarifa_mensual == 0) and \
               (self.tarifa_por_producto is None or self.tarifa_por_producto == 0)

    def get_tarifa_mensual_formateada(self) -> str:
        """Obtener tarifa mensual formateada en COP"""
        if self.tarifa_mensual is None:
            return "Gratis"
        return f"${self.tarifa_mensual:,.2f} COP"

    def get_tarifa_producto_formateada(self) -> str:
        """Obtener tarifa por producto formateada en COP"""
        if self.tarifa_por_producto is None:
            return "Gratis"
        return f"${self.tarifa_por_producto:,.2f} COP por producto"

    def esta_vigente(self) -> bool:
        """Verificar si el contrato está vigente actualmente"""
        now = datetime.utcnow()
        if not self.fecha_inicio:
            return False
        if self.fecha_fin and now > self.fecha_fin:
            return False
        return now >= self.fecha_inicio

    def dias_restantes(self) -> Optional[int]:
        """Calcular días restantes del contrato"""
        if not self.fecha_fin or not self.esta_vigente():
            return None
        return (self.fecha_fin - datetime.utcnow()).days

    def requiere_renovacion(self, dias_aviso: int = 30) -> bool:
        """Verificar si el contrato requiere renovación pronto"""
        if not self.esta_vigente() or self.renovacion_automatica:
            return False
        dias = self.dias_restantes()
        return dias is not None and dias <= dias_aviso

    def renovar_contrato(self, duracion_meses: int = 12) -> None:
        """Renovar contrato por duración especificada"""
        if self.fecha_fin:
            from dateutil.relativedelta import relativedelta
            self.fecha_fin = self.fecha_fin + relativedelta(months=duracion_meses)
            self.ultima_actualizacion = datetime.utcnow()

    def to_dict(self) -> dict:
        """Serializar storage a diccionario"""
        base_dict = super().to_dict()
        storage_dict = {
            "tipo": self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo,
            "capacidad_max": self.capacidad_max,
            "vendedor_id": str(self.vendedor_id) if self.vendedor_id else None,
            "productos_actuales": self.productos_actuales,
            "ocupacion_actual": float(self.ocupacion_actual) if self.ocupacion_actual is not None else None,
            "ultima_actualizacion": self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None,
            "tarifa_mensual": float(self.tarifa_mensual) if self.tarifa_mensual is not None else None,
            "tarifa_por_producto": float(self.tarifa_por_producto) if self.tarifa_por_producto is not None else None,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "renovacion_automatica": self.renovacion_automatica,
        }
        return {**base_dict, **storage_dict}

    def __repr__(self) -> str:
        tipo_display = self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo
        return f"<Storage(id={self.id}, tipo='{tipo_display}', capacidad_max={self.capacidad_max})>"

    def __str__(self) -> str:
        tipo_display = self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo
        return f"Storage {tipo_display} (Capacidad: {self.capacidad_max} productos)"