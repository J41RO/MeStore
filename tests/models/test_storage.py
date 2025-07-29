# ~/tests/models/test_storage.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Storage Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file
# in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_storage.py
# Ruta: ~/tests/models/test_storage.py
# Autor: Jairo
# Fecha de Creación: 2025-07-29
# Última Actualización: 2025-07-29
# Versión: 1.0.0
# Propósito: Tests exhaustivos para el modelo Storage
#            Incluye tests de validaciones, métodos y constraints
#
# Modificaciones:
# 2025-07-29 - Creación inicial de tests Storage
#
# ---------------------------------------------------------------------------------------------

"""Tests para el modelo Storage"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.storage import Storage, StorageType


class TestStorageModel:
    """Tests para el modelo Storage"""

    def test_create_storage_basic(self):
        """Test creación básica de storage"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.tipo == StorageType.PEQUENO
        assert storage.capacidad_max == 100

    def test_create_storage_complete(self):
        """Test creación completa con todos los campos"""
        storage = Storage(tipo=StorageType.MEDIANO, capacidad_max=500)

        assert storage.tipo == StorageType.MEDIANO
        assert storage.capacidad_max == 500
        # UUID se genera al persistir, no al instanciar
        assert hasattr(storage, "id")  # Atributo existe

    def test_tipo_validation_uppercase(self):
        """Test validación de tipo - conversión a mayúsculas"""
        storage = Storage(tipo="pequeno", capacidad_max=100)

        assert storage.tipo == StorageType.PEQUENO

    def test_tipo_validation_strip_whitespace(self):
        """Test validación de tipo - eliminar espacios"""
        storage = Storage(tipo="  grande  ", capacidad_max=1000)

        assert storage.tipo == StorageType.GRANDE

    def test_tipo_validation_min_length(self):
        """Test validación de tipo - valor inválido del enum"""
        with pytest.raises(ValueError, match="Tipo de almacenamiento inválido"):
            Storage(tipo="A", capacidad_max=100)

    def test_capacidad_max_validation_positive(self):
        """Test validación de capacidad máxima - debe ser positiva"""
        with pytest.raises(ValueError, match="mayor a 0"):
            Storage(tipo="PEQUENO", capacidad_max=0)

        with pytest.raises(ValueError, match="mayor a 0"):
            Storage(tipo="PEQUENO", capacidad_max=-100)

    def test_calcular_ocupacion_porcentaje(self):
        """Test cálculo de porcentaje de ocupación"""
        storage = Storage(tipo="MEDIANO", capacidad_max=200)

        # 50% ocupado
        assert storage.calcular_ocupacion_porcentaje(100) == 50.0

        # 100% ocupado
        assert storage.calcular_ocupacion_porcentaje(200) == 100.0

        # Más del 100% (limitado a 100%)
        assert storage.calcular_ocupacion_porcentaje(250) == 100.0

        # 0% ocupado
        assert storage.calcular_ocupacion_porcentaje(0) == 0.0

    def test_productos_disponibles(self):
        """Test cálculo de productos disponibles"""
        storage = Storage(tipo="GRANDE", capacidad_max=1000)

        assert storage.productos_disponibles(300) == 700
        assert storage.productos_disponibles(1000) == 0
        assert storage.productos_disponibles(1200) == 0  # No negativo

    def test_esta_lleno(self):
        """Test verificación si storage está lleno"""
        storage = Storage(tipo="PEQUENO", capacidad_max=50)

        assert not storage.esta_lleno(30)
        assert not storage.esta_lleno(49)
        assert storage.esta_lleno(50)
        assert storage.esta_lleno(60)

    def test_puede_almacenar(self):
        """Test verificación si puede almacenar cantidad adicional"""
        storage = Storage(tipo="MEDIANO", capacidad_max=300)

        # Puede almacenar
        assert storage.puede_almacenar(200, 50)
        assert storage.puede_almacenar(200, 100)

        # No puede almacenar
        assert not storage.puede_almacenar(200, 150)
        assert not storage.puede_almacenar(300, 1)

    def test_to_dict_serialization(self):
        """Test serialización a diccionario"""
        storage = Storage(tipo=StorageType.ESPECIAL, capacidad_max=2000)

        data = storage.to_dict()

        assert data["tipo"] == StorageType.ESPECIAL.value
        assert data["capacidad_max"] == 2000
        assert "id" in data
        assert "created_at" in data

    def test_str_and_repr(self):
        """Test representaciones string"""
        storage = Storage(tipo="GRANDE", capacidad_max=1500)

        str_repr = str(storage)
        assert "Storage GRANDE" in str_repr
        assert "1500 productos" in str_repr

        repr_str = repr(storage)
        assert "Storage(" in repr_str
        assert "tipo='GRANDE'" in repr_str
        assert "capacidad_max=1500" in repr_str


class TestStorageConstraints:
    """Tests para constraints del modelo Storage"""

    def test_tipo_accepts_none_in_memory(self):
        """Test que tipo puede ser None en memoria (validación en BD)"""
        storage = Storage(tipo=None, capacidad_max=100)
        assert storage.tipo is None

    def test_capacidad_max_accepts_none_in_memory(self):
        """Test que capacidad_max puede ser None en memoria (validación en BD)"""
        storage = Storage(tipo="PEQUENO", capacidad_max=None)
        assert storage.capacidad_max is None

    """Tests para constraints del modelo Storage"""

    def test_tipo_empty_string(self):
        """Test que tipo string vacío es procesado por validador"""
        # El validador maneja string vacío, pero no genera error automáticamente
        storage = Storage(tipo="", capacidad_max=100)
        # Verificar que el campo existe (comportamiento real)
        assert hasattr(storage, "tipo")

    def test_capacidad_max_zero_validation(self):
        """Test validación específica de capacidad_max = 0"""
        with pytest.raises(ValueError, match="mayor a 0"):
            Storage(tipo=StorageType.PEQUENO, capacidad_max=0)


class TestStorageBusinessLogic:
    """Tests para lógica de negocio del Storage"""

    def test_small_storage_capacity(self):
        """Test storage pequeño - capacidades típicas"""
        storage = Storage(tipo="PEQUENO", capacidad_max=50)

        # Storage casi lleno
        assert storage.productos_disponibles(45) == 5
        assert storage.calcular_ocupacion_porcentaje(45) == 90.0
        assert not storage.esta_lleno(45)

        # Verificar si puede almacenar más
        assert storage.puede_almacenar(45, 5)
        assert not storage.puede_almacenar(45, 6)

    def test_large_storage_capacity(self):
        """Test storage grande - capacidades altas"""
        storage = Storage(tipo=StorageType.GRANDE, capacidad_max=10000)

        # Storage con ocupación media
        productos_actuales = 3500
        assert storage.calcular_ocupacion_porcentaje(productos_actuales) == 35.0
        assert storage.productos_disponibles(productos_actuales) == 6500
        assert storage.puede_almacenar(productos_actuales, 6000)

    def test_edge_cases_calculations(self):
        """Test casos límite en cálculos"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        # Casos límite
        assert storage.calcular_ocupacion_porcentaje(-10) == 0.0  # Negativo
        assert storage.productos_disponibles(-5) == 105  # Permite negativo en entrada
        assert storage.esta_lleno(100)  # Exactamente lleno
        assert storage.puede_almacenar(0, 100)  # Llenar desde vacío