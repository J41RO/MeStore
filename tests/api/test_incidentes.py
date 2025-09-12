import pytest
from app.models.incidente_inventario import IncidenteInventario, TipoIncidente, EstadoIncidente
from app.schemas.inventory import IncidenteCreate, IncidenteResponse


def test_incidente_modelo_existe():
    """Test que el modelo IncidenteInventario existe y es construible."""
    assert IncidenteInventario is not None
    print("✅ Modelo IncidenteInventario existe")


def test_tipo_incidente_enum():
    """Test que el enum TipoIncidente está completo."""
    assert TipoIncidente.PERDIDO == "PERDIDO"
    assert TipoIncidente.DAÑADO == "DAÑADO"
    print("✅ Enum TipoIncidente completo con PERDIDO y DAÑADO")


def test_estado_incidente_enum():
    """Test que el enum EstadoIncidente está completo."""
    assert EstadoIncidente.REPORTADO == "REPORTADO"
    assert EstadoIncidente.EN_INVESTIGACION == "EN_INVESTIGACION"
    assert EstadoIncidente.RESUELTO == "RESUELTO"
    assert EstadoIncidente.CERRADO == "CERRADO"
    print("✅ Enum EstadoIncidente completo con 4 estados")


def test_incidente_schemas_exist():
    """Test que los schemas de incidentes existen."""
    # Test IncidenteCreate schema
    incidente_create = IncidenteCreate(
        inventory_id="550e8400-e29b-41d4-a716-446655440000",
        tipo_incidente=TipoIncidente.PERDIDO,
        descripcion="Producto perdido durante inventario"
    )
    assert str(incidente_create.inventory_id) == "550e8400-e29b-41d4-a716-446655440000"
    assert incidente_create.tipo_incidente == TipoIncidente.PERDIDO
    print("✅ Schema IncidenteCreate funcional")
    
    # Test que IncidenteResponse schema existe
    assert IncidenteResponse is not None
    print("✅ Schema IncidenteResponse existe")


def test_incidente_relationship():
    """Test que las relaciones del modelo están definidas."""
    from app.models.inventory import Inventory
    
    # Verificar que el modelo Inventory tiene la relación con incidentes
    inventory_relationships = [rel.key for rel in Inventory.__mapper__.relationships]
    assert "incidentes" in inventory_relationships
    print("✅ Relación Inventory -> IncidenteInventario definida")


def test_incidente_model_construction():
    """Test construcción básica del modelo IncidenteInventario."""
    # Test que se puede crear un incidente con los campos mínimos requeridos
    incidente_data = {
        "inventory_id": "550e8400-e29b-41d4-a716-446655440001",
        "tipo_incidente": TipoIncidente.PERDIDO,
        "descripcion": "Producto no encontrado en ubicación A-1-1",
        "reportado_por": "admin@test.com",
        "estado": EstadoIncidente.REPORTADO
    }
    
    # Verificar que se puede instanciar (sin persistir en BD)
    try:
        incidente = IncidenteInventario(**incidente_data)
        assert incidente.inventory_id == "550e8400-e29b-41d4-a716-446655440001"
        assert incidente.tipo_incidente == TipoIncidente.PERDIDO
        assert incidente.estado == EstadoIncidente.REPORTADO
        print("✅ Modelo IncidenteInventario se puede construir correctamente")
    except Exception as e:
        pytest.fail(f"Error construyendo IncidenteInventario: {e}")


def test_endpoints_imports():
    """Test que los endpoints de incidentes se pueden importar."""
    from app.api.v1.endpoints.inventory import reportar_incidente, listar_incidentes
    
    assert callable(reportar_incidente)
    assert callable(listar_incidentes)
    print("✅ Endpoints de incidentes existen y son callable")


def test_tipos_disponibles():
    """Test que todos los tipos de incidente están disponibles."""
    tipos_disponibles = [tipo.value for tipo in TipoIncidente]
    assert "PERDIDO" in tipos_disponibles
    assert "DAÑADO" in tipos_disponibles
    assert len(tipos_disponibles) == 2
    print("✅ Tipos de incidente disponibles: PERDIDO, DAÑADO")


def test_estados_workflow():
    """Test que el workflow de estados está completo."""
    estados_disponibles = [estado.value for estado in EstadoIncidente]
    expected_estados = ["REPORTADO", "EN_INVESTIGACION", "RESUELTO", "CERRADO"]
    
    for estado in expected_estados:
        assert estado in estados_disponibles
    
    print("✅ Workflow de estados completo: REPORTADO -> EN_INVESTIGACION -> RESUELTO -> CERRADO")


if __name__ == "__main__":
    test_incidente_modelo_existe()
    test_tipo_incidente_enum()
    test_estado_incidente_enum() 
    test_incidente_schemas_exist()
    test_incidente_relationship()
    test_incidente_model_construction()
    test_endpoints_imports()
    test_tipos_disponibles()
    test_estados_workflow()
    print("🎉 TODOS LOS TESTS DE INCIDENTES PASARON")