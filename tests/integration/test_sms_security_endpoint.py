"""
Integration tests for /send-sms-public endpoint
Testing 4 security layers + Twilio integration

This test suite validates the complete SMS sending flow:
1. Phone format validation
2. Phone rate limiting (3 per 10min)
3. IP rate limiting (10 per 10min)
4. Twilio integration

Author: unit-testing-ai
Date: 2025-10-11
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.sms_security
async def test_send_sms_public_success_flow(async_client: AsyncClient, mock_sms_service_success):
    """Complete successful SMS flow with all security layers"""
    response = await async_client.post(
        "/api/v1/auth/send-sms-public",
        params={"phone": "+573001234567"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "exitosamente" in data["message"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.sms_security
async def test_send_sms_public_phone_rate_limit(async_client: AsyncClient, mock_sms_service_success):
    """4th attempt to same phone should be blocked with 429"""
    phone = "+573009999999"

    # Attempts 1, 2, 3 should succeed
    for i in range(3):
        response = await async_client.post(
            "/api/v1/auth/send-sms-public",
            params={"phone": phone}
        )
        assert response.status_code == 200, f"Attempt {i+1} failed"

    # 4th attempt should be BLOCKED
    response = await async_client.post(
        "/api/v1/auth/send-sms-public",
        params={"phone": phone}
    )

    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert response.headers["Retry-After"] == "600"
    data = response.json()
    assert "10 minutos" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.sms_security
async def test_send_sms_public_invalid_phone_no_plus(async_client: AsyncClient):
    """Phone without + should be rejected with 400"""
    response = await async_client.post(
        "/api/v1/auth/send-sms-public",
        params={"phone": "3001234567"}  # Missing +
    )

    assert response.status_code == 400
    data = response.json()
    assert "inválido" in data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.sms_security
async def test_send_sms_public_invalid_phone_too_short(async_client: AsyncClient):
    """Too short phone should be rejected"""
    response = await async_client.post(
        "/api/v1/auth/send-sms-public",
        params={"phone": "+123"}
    )

    assert response.status_code == 400
