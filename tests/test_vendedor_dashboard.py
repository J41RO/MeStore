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