# ~/tests/test_schemas_inventory.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests para Schemas Inventory
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_schemas_inventory.py
# Ruta: ~/tests/test_schemas_inventory.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Tests unitarios para schemas Pydantic de Inventory,
#            validando business rules, computed fields y MovimientoStock
#
# Modificaciones:
# 2025-07-28 - Implementación inicial con tests completos
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para schemas Inventory y MovimientoStock.

Valida:
- Schemas básicos (InventoryBase, InventoryCreate, InventoryUpdate, InventoryRead)
- Validaciones de negocio (zona, estante, cantidades coherentes)
- Schemas MovimientoStock (Create, Read, TipoMovimiento)
- Compatibilidad con enums del modelo
- Serialización JSON y from_attributes
"""

import pytest
import uuid
from datetime import datetime
from typing import Dict, Any

from app.schemas.inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryUpdate,
    InventoryRead,
    InventoryResponse,
    MovimientoStockBase,
    MovimientoStockCreate,
    MovimientoStockRead,
    TipoMovimiento,
)
from app.models.inventory import InventoryStatus, CondicionProducto


class TestInventoryBase:
    """Tests para InventoryBase schema"""

    def test_inventory_base_valid_data(self):
        """Test creación válida de InventoryBase"""
        data = {
            "product_id": uuid.uuid4(),
            "zona": "A",
            "estante": "001",
            "posicion": "01",
            "cantidad": 100,
            "cantidad_reservada": 20,
            "status": InventoryStatus.DISPONIBLE,
            "condicion_producto": CondicionProducto.NUEVO,
            "notas_almacen": "Test notes"
        }

        inventory = InventoryBase(**data)

        assert inventory.product_id == data["product_id"]
        assert inventory.zona == "A"  # Uppercase conversion
        assert inventory.estante == "001"
        assert inventory.cantidad == 100
        assert inventory.cantidad_reservada == 20
        assert inventory.status == InventoryStatus.DISPONIBLE
        assert inventory.condicion_producto == CondicionProducto.NUEVO

    def test_zona_validation_alphanumeric(self):
        """Test validación zona alfanumérica"""
        base_data = {
            "product_id": uuid.uuid4(),
            "estante": "001",
            "posicion": "01",
            "cantidad": 100,
        }

        # Zona válida
        valid_inventory = InventoryBase(zona="A1", **base_data)
        assert valid_inventory.zona == "A1"

        # Zona inválida con caracteres especiales
        with pytest.raises(ValueError, match="Zona debe ser alfanumérica"):
            InventoryBase(zona="A-1!", **base_data)

    def test_estante_validation_format(self):
        """Test validación formato estante"""
        base_data = {
            "product_id": uuid.uuid4(),
            "zona": "A",
            "posicion": "01",
            "cantidad": 100,
        }

        # Estante válido
        valid_inventory = InventoryBase(estante="A01-B", **base_data)
        assert valid_inventory.estante == "A01-B"

        # Estante inválido con caracteres especiales
        with pytest.raises(ValueError, match="Estante debe contener solo números, letras y guiones"):
            InventoryBase(estante="A01@B", **base_data)

    def test_cantidad_coherencia_validation(self):
        """Test validación coherencia de cantidades"""
        base_data = {
            "product_id": uuid.uuid4(),
            "zona": "A",
            "estante": "001",
            "posicion": "01",
        }

        # Cantidades válidas
        valid_inventory = InventoryBase(cantidad=100, cantidad_reservada=50, **base_data)
        assert valid_inventory.cantidad == 100
        assert valid_inventory.cantidad_reservada == 50

        # Cantidad reservada mayor que total
        with pytest.raises(ValueError, match="Cantidad reservada no puede ser mayor que cantidad total"):
            InventoryBase(cantidad=50, cantidad_reservada=100, **base_data)

    def test_status_disponible_cantidad_cero_validation(self):
        """Test validación status DISPONIBLE con cantidad cero"""
        base_data = {
            "product_id": uuid.uuid4(),
            "zona": "A",
            "estante": "001",
            "posicion": "01",
            "cantidad": 0,
            "status": InventoryStatus.DISPONIBLE
        }

        with pytest.raises(ValueError, match="Inventario DISPONIBLE debe tener cantidad > 0"):
            InventoryBase(**base_data)

    def test_notas_almacen_cleaning(self):
        """Test limpieza y validación de notas_almacen"""
        base_data = {
            "product_id": uuid.uuid4(),
            "zona": "A",
            "estante": "001",
            "posicion": "01",
            "cantidad": 100,
        }

        # Notas válidas
        inventory_with_notes = InventoryBase(notas_almacen="  Test notes  ", **base_data)
        assert inventory_with_notes.notas_almacen == "Test notes"

        # Notas vacías se convierten a None
        inventory_empty_notes = InventoryBase(notas_almacen="   ", **base_data)
        assert inventory_empty_notes.notas_almacen is None


class TestInventoryCreate:
    """Tests para InventoryCreate schema"""

    def test_inventory_create_inherits_base_validations(self):
        """Test que InventoryCreate hereda validaciones de InventoryBase"""
        # Test herencia de validación de zona
        with pytest.raises(ValueError, match="Zona debe ser alfanumérica"):
            InventoryCreate(
                product_id=uuid.uuid4(),
                zona="A@1",
                estante="001",
                posicion="01",
                cantidad=100
            )

    def test_inventory_create_config_example(self):
        """Test que InventoryCreate tiene Config con ejemplo"""
        config = InventoryCreate.model_config
        assert 'json_schema_extra' in config
        assert 'example' in config['json_schema_extra']

        example = config['json_schema_extra']['example']
        assert 'product_id' in example
        assert 'zona' in example
        assert example['cantidad'] == 100


class TestInventoryUpdate:
    """Tests para InventoryUpdate schema"""

    def test_inventory_update_optional_fields(self):
        """Test que todos los campos son opcionales en InventoryUpdate"""
        # Update solo con zona
        update_zona = InventoryUpdate(zona="B")
        assert update_zona.zona == "B"
        assert update_zona.cantidad is None

        # Update solo con cantidad
        update_cantidad = InventoryUpdate(cantidad=200)
        assert update_cantidad.cantidad == 200
        assert update_cantidad.zona is None

    def test_inventory_update_validation_coherencia_parcial(self):
        """Test validación coherencia solo cuando ambos campos están presentes"""
        # Solo cantidad - válido
        update_valid = InventoryUpdate(cantidad=100)
        assert update_valid.cantidad == 100

        # Solo cantidad_reservada - válido
        update_valid2 = InventoryUpdate(cantidad_reservada=50)
        assert update_valid2.cantidad_reservada == 50

        # Ambos campos incoherentes - inválido
        with pytest.raises(ValueError, match="Cantidad reservada no puede ser mayor que cantidad total"):
            InventoryUpdate(cantidad=50, cantidad_reservada=100)

    def test_inventory_update_zona_validation(self):
        """Test validación zona en updates"""
        # Zona válida
        update_valid = InventoryUpdate(zona="c1")
        assert update_valid.zona == "C1"  # Uppercase conversion

        # Zona inválida
        with pytest.raises(ValueError, match="Zona debe ser alfanumérica"):
            InventoryUpdate(zona="C@1")


class TestTipoMovimiento:
    """Tests para TipoMovimiento enum"""

    def test_tipo_movimiento_values(self):
        """Test valores disponibles en TipoMovimiento"""
        expected_values = [
            "INGRESO", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO",
            "RESERVA", "LIBERACION_RESERVA", "PICKING",
            "CAMBIO_STATUS", "CAMBIO_CONDICION"
        ]

        actual_values = [t.value for t in TipoMovimiento]
        assert set(actual_values) == set(expected_values)

    def test_tipo_movimiento_enum_usage(self):
        """Test uso del enum en schemas"""
        movimiento = MovimientoStockCreate(
            inventory_id=uuid.uuid4(),
            tipo_movimiento=TipoMovimiento.INGRESO,
            cantidad_anterior=50,
            cantidad_nueva=100
        )
        assert movimiento.tipo_movimiento == TipoMovimiento.INGRESO


class TestMovimientoStockBase:
    """Tests para MovimientoStockBase schema"""

    def test_movimiento_stock_base_valid_data(self):
        """Test creación válida de MovimientoStockBase"""
        data = {
            "inventory_id": uuid.uuid4(),
            "tipo_movimiento": TipoMovimiento.INGRESO,
            "cantidad_anterior": 50,
            "cantidad_nueva": 100,
            "observaciones": "Test movement"
        }

        movimiento = MovimientoStockBase(**data)

        assert movimiento.inventory_id == data["inventory_id"]
        assert movimiento.tipo_movimiento == TipoMovimiento.INGRESO
        assert movimiento.cantidad_anterior == 50
        assert movimiento.cantidad_nueva == 100
        assert movimiento.observaciones == "Test movement"

    def test_movimiento_stock_cantidad_validation(self):
        """Test validación cantidades >= 0"""
        base_data = {
            "inventory_id": uuid.uuid4(),
            "tipo_movimiento": TipoMovimiento.AJUSTE_POSITIVO,
            "cantidad_nueva": 100
        }

        # Cantidad anterior válida
        valid_movimiento = MovimientoStockBase(cantidad_anterior=50, **base_data)
        assert valid_movimiento.cantidad_anterior == 50

        # Cantidad anterior inválida
        with pytest.raises(ValueError):
            MovimientoStockBase(cantidad_anterior=-10, **base_data)


class TestMovimientoStockCreate:
    """Tests para MovimientoStockCreate schema"""

    def test_movimiento_stock_create_with_user(self):
        """Test MovimientoStockCreate con user_id"""
        user_id = uuid.uuid4()
        movimiento = MovimientoStockCreate(
            inventory_id=uuid.uuid4(),
            tipo_movimiento=TipoMovimiento.PICKING,
            cantidad_anterior=100,
            cantidad_nueva=80,
            user_id=user_id
        )

        assert movimiento.user_id == user_id
        assert movimiento.tipo_movimiento == TipoMovimiento.PICKING

    def test_movimiento_stock_create_config_example(self):
        """Test que MovimientoStockCreate tiene Config con ejemplo"""
        config = MovimientoStockCreate.model_config
        assert 'json_schema_extra' in config
        assert 'example' in config['json_schema_extra']


class TestMovimientoStockRead:
    """Tests para MovimientoStockRead schema"""

    def test_movimiento_stock_read_structure(self):
        """Test estructura completa de MovimientoStockRead"""
        # Verificar campos base (no computed)
        field_names = list(MovimientoStockRead.model_fields.keys())
        
        expected_base_fields = [
            'inventory_id', 'tipo_movimiento', 'cantidad_anterior', 'cantidad_nueva',
            'observaciones', 'id', 'user_id', 'fecha_movimiento', 'created_at'
        ]
        
        for field in expected_base_fields:
            assert field in field_names, f"Campo base {field} faltante en MovimientoStockRead"
        
        # Verificar computed fields funcionalmente
        import uuid
        from datetime import datetime
        
        mock_data = {
            'id': uuid.uuid4(),
            'inventory_id': uuid.uuid4(),
            'tipo_movimiento': TipoMovimiento.INGRESO,
            'cantidad_anterior': 50,
            'cantidad_nueva': 100,
            'observaciones': 'Test',
            'user_id': uuid.uuid4(),
            'fecha_movimiento': datetime.now(),
            'created_at': datetime.now()
        }
        
        instance = MovimientoStockRead(**mock_data)
        
        # Verificar computed fields funcionan
        assert hasattr(instance, 'diferencia_cantidad'), "Computed field diferencia_cantidad faltante"
        assert hasattr(instance, 'tipo_descripcion'), "Computed field tipo_descripcion faltante"
        assert instance.diferencia_cantidad == 50, "Computed field diferencia_cantidad no calcula correctamente"
        assert instance.tipo_descripcion == 'Ingreso de stock', "Computed field tipo_descripcion no funciona"

    def test_movimiento_stock_read_config_example(self):
        """Test que MovimientoStockRead tiene Config con ejemplo"""
        config = MovimientoStockRead.model_config
        assert 'json_schema_extra' in config
        assert 'example' in config['json_schema_extra']

        example = config['json_schema_extra']['example']
        assert 'diferencia_cantidad' in example
        assert 'tipo_descripcion' in example


class TestInventoryRead:
    """Tests para InventoryRead schema"""

    def test_inventory_read_structure_complete(self):
        """Test estructura completa de InventoryRead"""
        field_names = list(InventoryRead.model_fields.keys())
        
        # Campos base (heredados de InventoryBase)
        base_fields = [
            'product_id', 'zona', 'estante', 'posicion', 'cantidad',
            'cantidad_reservada', 'status', 'condicion_producto', 'notas_almacen'
        ]
        
        # Campos metadatos
        metadata_fields = [
            'id', 'updated_by_id', 'fecha_ingreso', 'fecha_ultimo_movimiento',
            'created_at', 'updated_at', 'deleted_at'
        ]
        
        # Verificar campos base y metadatos (no computed)
        expected_non_computed = base_fields + metadata_fields
        
        for field in expected_non_computed:
            assert field in field_names, f"Campo {field} faltante en InventoryRead"
        
        # Verificar computed fields funcionalmente
        import uuid
        from datetime import datetime
        
        mock_data = {
            'id': uuid.uuid4(),
            'product_id': uuid.uuid4(),
            'zona': 'A',
            'estante': '001',
            'posicion': '01',
            'cantidad': 100,
            'cantidad_reservada': 20,
            'status': InventoryStatus.DISPONIBLE,
            'condicion_producto': CondicionProducto.NUEVO,
            'notas_almacen': 'Test',
            'updated_by_id': uuid.uuid4(),
            'fecha_ingreso': datetime.now(),
            'fecha_ultimo_movimiento': datetime.now(),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'deleted_at': None
        }
        
        instance = InventoryRead(**mock_data)
        
        # Verificar computed fields funcionan
        computed_fields = [
            'ubicacion_completa', 'cantidad_disponible', 'condicion_descripcion',
            'nivel_calidad', 'es_nuevo', 'es_vendible', 'requiere_inspeccion',
            'tiene_notas', 'transiciones_disponibles', 'dias_desde_ingreso',
            'dias_desde_ultimo_movimiento'
        ]
        
        for field in computed_fields:
            assert hasattr(instance, field), f"Computed field {field} faltante en InventoryRead"
        
        # Verificar algunos valores específicos
        assert instance.ubicacion_completa == "A-001-01"
        assert instance.cantidad_disponible == 80
        assert instance.es_nuevo == True

    def test_inventory_read_config_example(self):
        """Test que InventoryRead tiene Config con ejemplo completo"""
        config = InventoryRead.model_config
        assert 'json_schema_extra' in config
        assert 'example' in config['json_schema_extra']

        example = config['json_schema_extra']['example']

        # Verificar campos computed en el ejemplo
        computed_fields = [
            'ubicacion_completa', 'cantidad_disponible', 'es_nuevo',
            'es_vendible', 'dias_desde_ingreso'
        ]

        for field in computed_fields:
            assert field in example, f"Campo computed {field} faltante en ejemplo"


class TestInventoryResponse:
    """Tests para InventoryResponse schema"""

    def test_inventory_response_is_alias(self):
        """Test que InventoryResponse es alias de InventoryRead"""
        # Verificar que tienen los mismos campos
        read_fields = set(InventoryRead.model_fields.keys())
        response_fields = set(InventoryResponse.model_fields.keys())

        assert read_fields == response_fields

        # Verificar que InventoryResponse hereda de InventoryRead
        assert issubclass(InventoryResponse, InventoryRead)


class TestSchemasIntegration:
    """Tests de integración entre schemas"""

    def test_all_schemas_have_from_attributes(self):
        """Test que todos los schemas tienen from_attributes = True"""
        schemas_to_test = [
            InventoryCreate, InventoryUpdate, InventoryRead,
            MovimientoStockCreate, MovimientoStockRead
        ]

        for schema in schemas_to_test:
            config = schema.model_config
            assert config.get('from_attributes') is True, f"{schema.__name__} falta from_attributes = True"

    def test_schemas_compatibility_with_enums(self):
        """Test compatibilidad de schemas con enums del modelo"""
        # Test todos los valores de InventoryStatus
        for status in InventoryStatus:
            inventory = InventoryCreate(
                product_id=uuid.uuid4(),
                zona="A",
                estante="001",
                posicion="01",
                cantidad=100 if status == InventoryStatus.DISPONIBLE else 0,
                status=status
            )
            assert inventory.status == status

        # Test todos los valores de CondicionProducto
        for condicion in CondicionProducto:
            inventory = InventoryCreate(
                product_id=uuid.uuid4(),
                zona="A",
                estante="001",
                posicion="01",
                cantidad=100,
                condicion_producto=condicion
            )
            assert inventory.condicion_producto == condicion

    def test_json_serialization(self):
        """Test serialización JSON de schemas"""
        # Test InventoryCreate
        inventory_data = {
            "product_id": str(uuid.uuid4()),
            "zona": "A",
            "estante": "001",
            "posicion": "01",
            "cantidad": 100,
            "cantidad_reservada": 20,
            "status": "DISPONIBLE",
            "condicion_producto": "NUEVO"
        }

        inventory = InventoryCreate(**inventory_data)
        json_data = inventory.model_dump()

        assert json_data['zona'] == "A"
        assert json_data['cantidad'] == 100
        assert isinstance(json_data['product_id'], (str, uuid.UUID))  # Pydantic puede serializar como UUID object

        # Test MovimientoStockCreate
        movimiento_data = {
            "inventory_id": str(uuid.uuid4()),
            "tipo_movimiento": "INGRESO",
            "cantidad_anterior": 50,
            "cantidad_nueva": 100
        }

        movimiento = MovimientoStockCreate(**movimiento_data)
        json_data = movimiento.model_dump()

        assert json_data['tipo_movimiento'] == "INGRESO"
        assert json_data['cantidad_nueva'] == 100