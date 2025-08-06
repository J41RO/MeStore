import pytest
from uuid import uuid4
from app.api.v1.endpoints.inventory import get_ubicaciones

def test_get_ubicaciones_endpoint_exists():
    """Test que el endpoint get_ubicaciones existe y es callable."""
    assert callable(get_ubicaciones)
    print("✅ Endpoint get_ubicaciones existe y es callable")

def test_get_ubicaciones_has_correct_parameters():
    """Test que el endpoint tiene los parámetros esperados."""
    import inspect
    signature = inspect.signature(get_ubicaciones)
    params = list(signature.parameters.keys())
    
    expected_params = ['zona', 'disponible_solo', 'limit', 'offset', 'db']
    assert all(param in params for param in expected_params), f"Parámetros esperados: {expected_params}, encontrados: {params}"
    print(f"✅ Parámetros correctos: {params}")

def test_get_ubicaciones_return_annotation():
    """Test que el endpoint tiene la anotación de retorno correcta."""
    import inspect
    from typing import get_type_hints
    
    hints = get_type_hints(get_ubicaciones)
    return_type = hints.get('return')
    
    assert return_type is not None, "Endpoint debe tener anotación de retorno"
    print(f"✅ Tipo de retorno anotado: {return_type}")

if __name__ == "__main__":
    test_get_ubicaciones_endpoint_exists()
    test_get_ubicaciones_has_correct_parameters() 
    test_get_ubicaciones_return_annotation()
    print("🎉 TODOS LOS TESTS BÁSICOS PASARON")
