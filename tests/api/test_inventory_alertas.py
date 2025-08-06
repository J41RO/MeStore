import pytest
from app.api.v1.endpoints.inventory import get_alertas_inventario, TipoAlerta
from app.schemas.inventory import AlertasResponse, AlertasMetadata

def test_get_alertas_endpoint_exists():
    """Test que el endpoint get_alertas_inventario existe y es callable."""
    assert callable(get_alertas_inventario)
    print("✅ Endpoint get_alertas_inventario existe y es callable")

def test_alertas_schemas_exist():
    """Test que los schemas de alertas existen y son construibles."""
    # Test AlertasMetadata
    metadata = AlertasMetadata(
        total_alertas=5,
        stock_bajo=2,
        sin_movimiento=1,
        stock_agotado=1,
        criticos=1
    )
    assert metadata.total_alertas == 5
    print("✅ AlertasMetadata construible y funcional")
    
    # Test AlertasResponse (con data mock)
    mock_alertas = []
    response = AlertasResponse(alertas=mock_alertas, metadata=metadata)
    assert response.metadata.total_alertas == 5
    print("✅ AlertasResponse construible y funcional")

def test_tipo_alerta_enum():
    """Test que el enum TipoAlerta está completo."""
    assert TipoAlerta.STOCK_BAJO == "STOCK_BAJO"
    assert TipoAlerta.SIN_MOVIMIENTO == "SIN_MOVIMIENTO"
    assert TipoAlerta.STOCK_AGOTADO == "STOCK_AGOTADO"
    assert TipoAlerta.CRITICO == "CRITICO"
    print("✅ Enum TipoAlerta completo con 4 tipos")

def test_import_compatibility():
    """Test que todos los imports necesarios funcionan."""
    from sqlalchemy import or_, and_
    from datetime import datetime, timedelta
    from app.models.inventory import Inventory
    
    # Test de sintaxis básica
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    assert isinstance(fecha_limite, datetime)
    print("✅ Imports y sintaxis básica funcional")

if __name__ == "__main__":
    test_get_alertas_endpoint_exists()
    test_alertas_schemas_exist()
    test_tipo_alerta_enum()
    test_import_compatibility()
    print("🎉 TODOS LOS TESTS BÁSICOS PASARON")
