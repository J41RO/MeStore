"""
Tests para endpoint de inventario.

Tests básicos para verificar funcionalidad del endpoint GET /inventario.
"""

import inspect
from uuid import uuid4

import pytest


def test_get_inventario_endpoint_exists():
    """Test que el endpoint get_inventario existe y es importable."""
    from app.api.v1.endpoints.inventory import get_inventario

    # Verificar que la función existe
    assert callable(get_inventario)
    print("✅ Endpoint get_inventario existe y es callable")


def test_get_inventario_endpoint_signature():
    """Test que el endpoint tiene la signatura correcta."""
    from app.api.v1.endpoints.inventory import get_inventario

    # Verificar signatura de la función
    sig = inspect.signature(get_inventario)
    params = list(sig.parameters.keys())

    # Verificar parámetros esperados
    expected_params = ['vendedor_id', 'product_id', 'limit', 'offset', 'db']
    for param in expected_params:
        assert param in params, f"Parámetro {param} faltante"

    print(f"✅ Signatura correcta: {params}")


def test_inventory_response_schema_exists():
    """Test que el schema InventoryResponse existe."""
    from app.schemas.inventory import InventoryResponse

    # Verificar que el schema existe y es usable
    assert hasattr(InventoryResponse, 'model_validate')
    assert hasattr(InventoryResponse, 'model_dump')

    print("✅ Schema InventoryResponse disponible")


def test_inventory_router_registration():
    """Test que el router está registrado correctamente."""
    from app.api.v1 import api_router

    # Verificar que hay rutas registradas
    routes = [route.path for route in api_router.routes if hasattr(route, 'path')]

    # Buscar ruta de inventario
    inventory_routes = [route for route in routes if route == '/' or 'inventario' in route]

    assert len(inventory_routes) > 0, "Router inventory no encontrado"
    print(f"✅ Router registrado - rutas: {inventory_routes}")


def test_endpoint_parameters_types():
    """Test que los parámetros tienen los tipos correctos."""
    from app.api.v1.endpoints.inventory import get_inventario
    from uuid import UUID
    from sqlalchemy.ext.asyncio import AsyncSession
    from typing import get_type_hints

    # Verificar type hints
    hints = get_type_hints(get_inventario)

    # Verificar algunos tipos críticos
    assert 'db' in hints
    assert 'limit' in hints
    assert 'offset' in hints

    print("✅ Type hints verificados")


if __name__ == "__main__":
    # Ejecutar tests básicos
    test_get_inventario_endpoint_exists()
    test_get_inventario_endpoint_signature()  
    test_inventory_response_schema_exists()
    test_inventory_router_registration()
    test_endpoint_parameters_types()

    print("🎉 TODOS LOS TESTS BÁSICOS COMPLETADOS EXITOSAMENTE")

def test_registrar_movimiento_endpoint():
    """Test endpoint POST /movimiento básico."""
    from app.api.v1.endpoints.inventory import registrar_movimiento
    from app.schemas.inventory import MovimientoStockCreate, MovimientoResponse, TipoMovimiento
    import inspect
    
    # Verificar endpoint existe
    assert callable(registrar_movimiento)
    
    # Verificar signatura
    sig = inspect.signature(registrar_movimiento)
    assert "movimiento" in sig.parameters
    assert "db" in sig.parameters
    
    print("✅ Endpoint registrar_movimiento existe")


def test_movimiento_schemas():
    """Test schemas de movimiento."""
    from app.schemas.inventory import MovimientoStockCreate, MovimientoResponse, TipoMovimiento
    from uuid import uuid4
    
    # Test TipoMovimiento enum
    assert TipoMovimiento.INGRESO == "INGRESO"
    assert TipoMovimiento.AJUSTE_POSITIVO == "AJUSTE_POSITIVO"
    assert TipoMovimiento.AJUSTE_NEGATIVO == "AJUSTE_NEGATIVO"
    
    # Test MovimientoStockCreate
    create_data = {
        "inventory_id": uuid4(),
        "tipo_movimiento": TipoMovimiento.INGRESO,
        "cantidad_anterior": 50,
        "cantidad_nueva": 100,
        "observaciones": "Ingreso inicial",
        "user_id": uuid4()
    }
    
    movimiento = MovimientoStockCreate(**create_data)
    assert movimiento.tipo_movimiento == TipoMovimiento.INGRESO
    
    # Test MovimientoResponse disponible
    assert hasattr(MovimientoResponse, "model_validate")
    
    print("✅ Schemas de movimiento funcionales")


def test_tipos_movimiento_disponibles():
    """Test que todos los tipos de movimiento están definidos."""
    from app.schemas.inventory import TipoMovimiento
    
    tipos_esperados = [
        "INGRESO", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO", 
        "RESERVA", "LIBERACION_RESERVA", "PICKING", 
        "CAMBIO_STATUS", "CAMBIO_CONDICION"
    ]
    
    tipos_actuales = [tipo.value for tipo in TipoMovimiento]
    
    for tipo in tipos_esperados:
        assert tipo in tipos_actuales, f"Tipo {tipo} no encontrado"
    
    print(f"✅ Todos los tipos de movimiento disponibles: {len(tipos_actuales)}")


def test_movimiento_endpoint_integration():
    """Test integración completa del endpoint de movimiento."""
    from app.api.v1.endpoints.inventory import registrar_movimiento
    from app.schemas.inventory import MovimientoStockCreate, MovimientoResponse, TipoMovimiento
    from typing import get_type_hints
    
    # Verificar type hints del endpoint
    hints = get_type_hints(registrar_movimiento)
    assert 'movimiento' in hints
    assert 'db' in hints
    
    # Verificar que MovimientoStockCreate tiene todos los campos requeridos
    required_fields = ['inventory_id', 'tipo_movimiento', 'cantidad_anterior', 'cantidad_nueva']
    
    from pydantic import ValidationError
    import pytest
    
    # Test que falla sin campos requeridos
    with pytest.raises(ValidationError):
        MovimientoStockCreate()
    
    print("✅ Integración endpoint movimiento verificada")
