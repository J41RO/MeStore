# tests/api/test_pagos_historial.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_historial_pagos_basic(async_client: AsyncClient):
    """Test básico del endpoint de historial de pagos."""
    response = await async_client.get("/api/v1/pagos/historial")
    assert response.status_code == 200
    assert "transacciones" in response.json()
    assert "total" in response.json()
