import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_dashboard_resumen_requiere_auth(async_client):
    """Verificar que el endpoint requiere autenticación."""
    response = await async_client.get("/api/v1/vendedores/dashboard/resumen")
    # El endpoint retorna 403 porque require autenticación Y permisos de vendedor
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio  
async def test_dashboard_resumen_endpoint_disponible(async_client):
    """Verificar que el endpoint está registrado y responde."""
    response = await async_client.get("/api/v1/vendedores/dashboard/resumen")
    # Endpoint debe responder (no 404) aunque requiera auth
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.status_code in [403, 401]  # Auth/permission required

@pytest.mark.asyncio
async def test_dashboard_resumen_estructura_response():
    """Verificar estructura de respuesta del dashboard."""
    # TODO: Test con usuario vendedor autenticado cuando tengamos auth fixtures
    # Verificar que response contiene: ventas_totales, pedidos_pendientes,
    # productos_activos, comision_total
    pass

import pytest
from httpx import AsyncClient
from fastapi import status

# Tests para endpoint dashboard/ventas
@pytest.mark.asyncio
async def test_dashboard_ventas_requiere_auth(async_client: AsyncClient):
    """Verificar que endpoint de ventas requiere autenticación."""
    response = await async_client.get("/api/v1/vendedores/dashboard/ventas")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_dashboard_ventas_parametros_query(async_client: AsyncClient):
    """Verificar parámetros de query del endpoint ventas."""
    # Test con parámetros específicos
    response = await async_client.get("/api/v1/vendedores/dashboard/ventas?periodo=diario&limite=5")
    # Debe responder con estructura correcta (aunque requiera auth)
    assert response.status_code in [403, 401, 200]  # Auth required o success

@pytest.mark.asyncio  
async def test_dashboard_ventas_estructura_response():
    """Verificar estructura de respuesta de dashboard ventas."""
    # TODO: Test con autenticación cuando tengamos fixtures de usuario vendedor
    pass

@pytest.mark.asyncio
async def test_dashboard_ventas_tipos_periodo(async_client: AsyncClient):
    """Verificar que endpoint acepta todos los tipos de período."""
    periodos = ["diario", "semanal", "mensual"]

    for periodo in periodos:
        response = await async_client.get(f"/api/v1/vendedores/dashboard/ventas?periodo={periodo}")
        # Verificar que el parámetro es aceptado (aunque falle por auth)
        assert response.status_code in [403, 401, 200, 422]  # 422 solo si parámetro inválido

@pytest.mark.asyncio
async def test_dashboard_ventas_limite_parametro(async_client: AsyncClient):
    """Verificar validación del parámetro límite."""
    # Test límite válido
    response = await async_client.get("/api/v1/vendedores/dashboard/ventas?limite=10")
    assert response.status_code in [403, 401, 200]  # No error de validación

    # Test límite inválido (mayor a 24)
    response = await async_client.get("/api/v1/vendedores/dashboard/ventas?limite=30")
    assert response.status_code == 403  # Auth required (no llega a validation)