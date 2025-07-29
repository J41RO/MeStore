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

from sqlalchemy import CheckConstraint, Column, Enum, Index, Integer, String
from sqlalchemy.orm import validates
from enum import Enum as PyEnum

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
        index=True,
        comment="Tipo de espacio de almacenamiento",
    )

    capacidad_max = Column(
        Integer, nullable=False, comment="Capacidad máxima en número de productos"
    )

    # Constraints e índices
    __table_args__ = (
        Index("ix_storage_tipo_capacidad", "tipo", "capacidad_max"),
        CheckConstraint("capacidad_max > 0", name="ck_storage_capacidad_positive"),
    )

    @validates("capacidad_max")
    def validate_capacidad_max(self, key, value):
        """Validar que la capacidad máxima sea positiva"""
        if value is not None and value <= 0:
            raise ValueError("La capacidad máxima debe ser mayor a 0")
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
            if len(value) < 2:
                raise ValueError("El tipo debe tener al menos 2 caracteres")
        return value

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

    def to_dict(self) -> dict:
        """Serializar storage a diccionario"""
        base_dict = super().to_dict()
        storage_dict = {
            "tipo": self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo,
            "capacidad_max": self.capacidad_max,
        }
        return {**base_dict, **storage_dict}

    def __repr__(self) -> str:
        tipo_display = self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo
        return f"<Storage(id={self.id}, tipo='{tipo_display}', capacidad_max={self.capacidad_max})>"

    def __str__(self) -> str:
        tipo_display = self.tipo.value if isinstance(self.tipo, StorageType) else self.tipo
        return f"Storage {tipo_display} (Capacidad: {self.capacidad_max} productos)"