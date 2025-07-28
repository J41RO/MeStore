# ~/tests/test_models_inventory.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Modelo Inventory con Ubicación Física
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_models_inventory.py
# Ruta: ~/tests/test_models_inventory.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Tests completos para modelo Inventory con campos de ubicación física
#            Incluye tests de creación, validación, relationships y métodos de utilidad
#
# Modificaciones:
# 2025-07-28 - Tests iniciales para modelo Inventory completado
#
# ---------------------------------------------------------------------------------------------

"""
Tests para modelo Inventory - Sistema de ubicación física de productos.

Este módulo contiene tests para:
- Creación y validación básica del modelo Inventory
- Campos de ubicación física (zona, estante, posicion)
- Control de inventario (cantidad, cantidad_reservada)
- Relationships con Product y User
- Métodos de utilidad (ubicacion_completa, cantidad_disponible, reservas)
- Constraints únicos y foreign keys
- Serialización y funcionalidad warehouse management
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User


class TestInventoryModel:
    """Tests básicos del modelo Inventory."""

    def test_create_inventory_with_minimal_data(self):
        """Test creación de Inventory con datos mínimos requeridos."""
        product_id = uuid.uuid4()

        inventory = Inventory(
            product_id=product_id,
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100
        )

        # Verificar campos obligatorios
        assert inventory.product_id == product_id
        assert inventory.zona == 'A'
        assert inventory.estante == '001'
        assert inventory.posicion == '01'
        assert inventory.cantidad == 100
        assert inventory.cantidad_reservada == 0  # Default value

        # Verificar herencia BaseModel
        assert hasattr(inventory, "id")
        assert hasattr(inventory, "created_at")
        assert hasattr(inventory, "updated_at")
        assert inventory.deleted_at is None

    def test_create_inventory_with_all_fields(self):
        """Test creación de Inventory con todos los campos."""
        product_id = uuid.uuid4()
        user_id = uuid.uuid4()

        inventory = Inventory(
            product_id=product_id,
            zona='B',
            estante='025',
            posicion='03',
            cantidad=250,
            cantidad_reservada=50,
            updated_by_id=user_id
        )

        assert inventory.product_id == product_id
        assert inventory.zona == 'B'
        assert inventory.estante == '025'
        assert inventory.posicion == '03'
        assert inventory.cantidad == 250
        assert inventory.cantidad_reservada == 50
        assert inventory.updated_by_id == user_id

    def test_inventory_init_with_defaults(self):
        """Test que __init__ establece valores por defecto seguros."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='C',
            estante='100',
            posicion='05'
        )

        # Verificar defaults del __init__
        assert inventory.cantidad == 0
        assert inventory.cantidad_reservada == 0


class TestInventoryUbicacion:
    """Tests para funcionalidad de ubicación física."""

    def test_get_ubicacion_completa(self):
        """Test método get_ubicacion_completa()."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100
        )

        ubicacion = inventory.get_ubicacion_completa()
        assert ubicacion == 'A-001-01'

    def test_get_ubicacion_completa_various_formats(self):
        """Test ubicación completa con diferentes formatos."""
        test_cases = [
            ('A', '001', '01', 'A-001-01'),
            ('B', '100', '05', 'B-100-05'),
            ('C', '025', '10', 'C-025-10'),
            ('Z', '999', '99', 'Z-999-99'),
        ]

        for zona, estante, posicion, expected in test_cases:
            inventory = Inventory(
                product_id=uuid.uuid4(),
                zona=zona,
                estante=estante,
                posicion=posicion,
                cantidad=50
            )
            assert inventory.get_ubicacion_completa() == expected


class TestInventoryCantidades:
    """Tests para funcionalidad de cantidades e inventario."""

    def test_cantidad_disponible_basic(self):
        """Test cálculo básico de cantidad disponible."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=20
        )

        assert inventory.cantidad_disponible() == 80

    def test_cantidad_disponible_sin_reservas(self):
        """Test cantidad disponible sin reservas."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=0
        )

        assert inventory.cantidad_disponible() == 100

    def test_cantidad_disponible_totalmente_reservado(self):
        """Test cantidad disponible cuando está totalmente reservado."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=100
        )

        assert inventory.cantidad_disponible() == 0

    def test_cantidad_disponible_over_reserved(self):
        """Test que cantidad disponible nunca sea negativa."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=150  # Más reservado que disponible
        )

        assert inventory.cantidad_disponible() == 0  # max(0, 100-150) = 0


class TestInventoryReservas:
    """Tests para funcionalidad de reservas."""

    def test_reservar_cantidad_exitoso(self):
        """Test reserva exitosa de cantidad."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=0
        )

        resultado = inventory.reservar_cantidad(30)

        assert resultado is True
        assert inventory.cantidad_reservada == 30
        assert inventory.cantidad_disponible() == 70

    def test_reservar_cantidad_insuficiente(self):
        """Test reserva cuando no hay cantidad suficiente."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=80
        )

        # Solo 20 disponibles, intentar reservar 30
        resultado = inventory.reservar_cantidad(30)

        assert resultado is False
        assert inventory.cantidad_reservada == 80  # No cambió
        assert inventory.cantidad_disponible() == 20

    def test_reservar_cantidad_exacta_disponible(self):
        """Test reservar exactamente la cantidad disponible."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=70
        )

        # 30 disponibles, reservar exactamente 30
        resultado = inventory.reservar_cantidad(30)

        assert resultado is True
        assert inventory.cantidad_reservada == 100
        assert inventory.cantidad_disponible() == 0

    def test_liberar_reserva_basic(self):
        """Test liberación básica de reserva."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=50
        )

        inventory.liberar_reserva(20)

        assert inventory.cantidad_reservada == 30
        assert inventory.cantidad_disponible() == 70

    def test_liberar_reserva_mas_que_reservado(self):
        """Test liberar más cantidad de la que está reservada."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=20
        )

        inventory.liberar_reserva(50)  # Liberar más de lo reservado

        assert inventory.cantidad_reservada == 0  # No puede ser negativo
        assert inventory.cantidad_disponible() == 100

    def test_liberar_reserva_total(self):
        """Test liberar toda la reserva."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=40
        )

        inventory.liberar_reserva(40)

        assert inventory.cantidad_reservada == 0
        assert inventory.cantidad_disponible() == 100


class TestInventorySerializacion:
    """Tests para serialización y to_dict()."""

    def test_to_dict_campos_basicos(self):
        """Test serialización con campos básicos."""
        product_id = uuid.uuid4()
        user_id = uuid.uuid4()

        inventory = Inventory(
            product_id=product_id,
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=20,
            updated_by_id=user_id
        )

        data = inventory.to_dict()

        # Verificar campos base
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'deleted_at' in data

        # Verificar campos específicos
        assert data['product_id'] == str(product_id)
        assert data['zona'] == 'A'
        assert data['estante'] == '001'
        assert data['posicion'] == '01'
        assert data['cantidad'] == 100
        assert data['cantidad_reservada'] == 20
        assert data['updated_by_id'] == str(user_id)

        # Verificar campos calculados
        assert data['ubicacion_completa'] == 'A-001-01'
        assert data['cantidad_disponible'] == 80

    def test_to_dict_campos_calculados(self):
        """Test que campos calculados se incluyen correctamente."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='B',
            estante='100',
            posicion='05',
            cantidad=200,
            cantidad_reservada=75
        )

        data = inventory.to_dict()

        assert data['ubicacion_completa'] == 'B-100-05'
        assert data['cantidad_disponible'] == 125

    def test_to_dict_campos_opcional_none(self):
        """Test serialización cuando campos opcionales son None."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='C',
            estante='050',
            posicion='02',
            cantidad=50
            # updated_by_id no proporcionado (None)
        )

        data = inventory.to_dict()

        assert data['updated_by_id'] is None


class TestInventoryRelationships:
    """Tests para relationships con otros modelos."""

    def test_inventory_has_product_relationship(self):
        """Test que Inventory tiene relationship con Product."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100
        )

        # Verificar que el relationship existe
        assert hasattr(inventory, 'product')
        assert hasattr(inventory, 'updated_by')

    def test_product_has_inventory_relationship(self):
        """Test que Product tiene relationship con Inventory."""
        # Verificar que Product tiene el relationship inverso
        assert hasattr(Product, 'ubicaciones_inventario')


class TestInventoryConstraints:
    """Tests para constraints y validaciones."""

    def test_inventory_tablename(self):
        """Test que el tablename es correcto."""
        assert Inventory.__tablename__ == 'inventory'

    def test_inventory_table_constraints(self):
        """Test que la tabla tiene los constraints esperados."""
        table = Inventory.__table__

        # Verificar que tiene constraints
        assert len(table.constraints) >= 3  # PK + FK + Unique

        # Verificar que tiene foreign keys
        foreign_keys = [fk for fk in table.foreign_keys]
        assert len(foreign_keys) >= 2  # product_id, updated_by_id

        fk_columns = [fk.parent.name for fk in foreign_keys]
        assert 'product_id' in fk_columns
        assert 'updated_by_id' in fk_columns

    def test_inventory_indexes(self):
        """Test que la tabla tiene los índices esperados."""
        table = Inventory.__table__

        # Verificar que tiene índices
        assert len(table.indexes) >= 5

        # Verificar índices específicos por nombre
        index_names = [idx.name for idx in table.indexes]
        expected_indexes = [
            'ix_inventory_location',
            'ix_inventory_product_location',
            'ix_inventory_zona',
            'ix_inventory_estante',
            'ix_inventory_product_id'
        ]

        for expected_idx in expected_indexes:
            assert expected_idx in index_names


class TestInventoryRepr:
    """Tests para representación string del modelo."""

    def test_inventory_repr(self):
        """Test método __repr__ del modelo."""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona='A',
            estante='001',
            posicion='01',
            cantidad=100,
            cantidad_reservada=20
        )

        repr_str = repr(inventory)

        # Verificar que contiene información clave
        assert 'Inventory' in repr_str
        assert 'A-001-01' in repr_str  # ubicacion_completa
        assert '80/100' in repr_str     # disponible/total


# Tests de integración
class TestInventoryIntegration:
    """Tests de integración con otros componentes."""

    def test_inventory_workflow_completo(self):
        """Test workflow completo de inventory management."""
        product_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # 1. Crear inventory inicial
        inventory = Inventory(
            product_id=product_id,
            zona='A',
            estante='001',
            posicion='01',
            cantidad=1000,
            updated_by_id=user_id
        )

        assert inventory.cantidad_disponible() == 1000
        assert inventory.get_ubicacion_completa() == 'A-001-01'

        # 2. Reservar cantidad para orden
        reserva_exitosa = inventory.reservar_cantidad(300)
        assert reserva_exitosa is True
        assert inventory.cantidad_disponible() == 700
        assert inventory.cantidad_reservada == 300

        # 3. Intentar reservar más de lo disponible
        reserva_fallida = inventory.reservar_cantidad(800)
        assert reserva_fallida is False
        assert inventory.cantidad_disponible() == 700  # No cambió

        # 4. Liberar parte de la reserva
        inventory.liberar_reserva(100)
        assert inventory.cantidad_disponible() == 800
        assert inventory.cantidad_reservada == 200

        # 5. Verificar serialización final
        data = inventory.to_dict()
        assert data['cantidad'] == 1000
        assert data['cantidad_reservada'] == 200
        assert data['cantidad_disponible'] == 800
        assert data['ubicacion_completa'] == 'A-001-01'

        # 6. Verificar que puede ser actualizado
        inventory.zona = 'B'
        inventory.estante = '200'
        assert inventory.get_ubicacion_completa() == 'B-200-01'
