import pytest
from httpx import AsyncClient







@pytest.mark.asyncio
async def test_get_comision_detalle_not_found(async_client: AsyncClient):
    """Test endpoint con UUID inexistente retorna 404."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = await async_client.get(f"/api/v1/comisiones/detalle/{fake_uuid}")
    assert response.status_code == 404
    assert "Transacción no encontrada" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_comision_detalle_invalid_uuid(async_client: AsyncClient):
    """Test endpoint con UUID inválido retorna 422."""
    invalid_uuid = "not-a-valid-uuid"
    response = await async_client.get(f"/api/v1/comisiones/detalle/{invalid_uuid}")
    assert response.status_code == 422