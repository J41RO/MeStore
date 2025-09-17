"""
Test simple para verificar que el endpoint de vendedores funciona.
Sin fixtures complicadas, solo verificación básica.
"""

def test_vendedores_health_simple():
    """Test simple de health check sin fixtures"""
    # Este test siempre pasa porque solo verifica que el módulo existe
    from app.api.v1.endpoints.vendedores import router
    assert router is not None
    assert hasattr(router, 'routes')
    print("✅ Router vendedores importado correctamente")

def test_vendedores_schema_simple():
    """Test simple del schema sin BD"""
    from app.schemas.vendedor import VendedorCreate
    
    # Test de validación básica
    try:
        vendedor = VendedorCreate(
            email="test@test.com",
            password="Password123", 
            nombre="Test",
            apellido="User",
            cedula="12345678",
            telefono="300 123 4567"
        )
        assert vendedor.email == "test@test.com"
        assert vendedor.cedula == "12345678"
        assert vendedor.telefono == "+57 3001234567"  # Normalizado
        print("✅ Schema VendedorCreate funciona correctamente")
    except Exception as e:
        assert False, f"Schema validation failed: {e}"

def test_endpoint_registration():
    """Verificar que el endpoint está registrado"""
    from app.main import app
    
    # Verificar que las rutas de vendedores existen
    vendedor_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'vendedores' in route.path:
            vendedor_routes.append(route.path)
    
    assert len(vendedor_routes) >= 2, "Deben existir al menos 2 rutas de vendedores"
    assert any('/registro' in route for route in vendedor_routes), "Debe existir ruta de registro"
    assert any('/health' in route for route in vendedor_routes), "Debe existir ruta de health"
    print(f"✅ Rutas vendedores registradas: {vendedor_routes}")
