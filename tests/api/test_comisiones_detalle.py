import pytest
from httpx import AsyncClient







@pytest.mark.asyncio
async def test_get_comision_detalle_not_found(async_client: AsyncClient):
    """Test endpoint con UUID inexistente retorna 404."""
    import uuid
    fake_uuid = str(uuid.uuid4())  # Generate a valid random UUID
    response = await async_client.get(f"/api/v1/comisiones/detalle/{fake_uuid}")
    assert response.status_code == 404
    # Updated to match actual response structure from custom error handler
    assert "Transacción no encontrada" in response.json()["error_message"]


@pytest.mark.asyncio
async def test_get_comision_detalle_invalid_uuid(async_client: AsyncClient):
    """Test endpoint con UUID inválido retorna 422."""
    invalid_uuid = "not-a-valid-uuid"
    response = await async_client.get(f"/api/v1/comisiones/detalle/{invalid_uuid}")
    assert response.status_code == 422