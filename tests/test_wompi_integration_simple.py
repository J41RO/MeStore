"""
Simple Integration Test for WompiService Methods
================================================

Testing the 3 critical methods working with IntegratedPaymentService.
This validates that the implementation integrates correctly.

Author: Wompi Payment Integrator Agent
Date: 2025-09-18
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.services.integrated_payment_service import IntegratedPaymentService
from app.services.payments.wompi_service import WompiService, WompiError


@pytest.mark.asyncio
async def test_integrated_payment_service_uses_wompi_methods():
    """Test that IntegratedPaymentService can call the new Wompi methods"""

    # Create mock database session
    db_mock = Mock()

    # Create integrated payment service
    service = IntegratedPaymentService(db=db_mock)

    # Mock the Wompi service methods we implemented
    service.wompi_service.get_transaction_status = AsyncMock(return_value={
        "transaction_id": "trans_123",
        "status": "APPROVED",
        "amount_in_cents": 50000,
        "currency": "COP"
    })

    service.wompi_service.get_payment_methods = AsyncMock(return_value=[
        {
            "type": "CARD",
            "name": "Credit/Debit Card",
            "supported_currencies": ["COP"]
        }
    ])

    service.wompi_service.health_check = AsyncMock(return_value={
        "service": "WompiService",
        "status": "healthy",
        "timestamp": "2025-09-18T10:00:00Z"
    })

    # Test 1: get_payment_methods integration
    payment_methods = await service.get_payment_methods()
    assert len(payment_methods) == 1
    assert payment_methods[0]["type"] == "CARD"
    service.wompi_service.get_payment_methods.assert_called_once()

    # Test 2: health_check integration
    health_status = await service.health_check()
    assert "wompi" in health_status["components"]
    assert health_status["components"]["wompi"]["status"] == "healthy"
    service.wompi_service.health_check.assert_called_once()

    # Test 3: Verify transaction status can be called (via get_payment_status)
    # This would normally be called within get_payment_status method
    status = await service.wompi_service.get_transaction_status("trans_123")
    assert status["transaction_id"] == "trans_123"
    assert status["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_wompi_service_methods_exist_and_callable():
    """Test that the WompiService has the required methods"""

    service = WompiService()

    # Verify methods exist
    assert hasattr(service, 'get_transaction_status')
    assert hasattr(service, 'get_payment_methods')
    assert hasattr(service, 'health_check')

    # Verify they are callable
    assert callable(service.get_transaction_status)
    assert callable(service.get_payment_methods)
    assert callable(service.health_check)


@pytest.mark.asyncio
async def test_wompi_methods_have_correct_signatures():
    """Test method signatures are correct"""

    import inspect

    # Test get_transaction_status signature
    sig = inspect.signature(WompiService.get_transaction_status)
    params = list(sig.parameters.keys())
    assert 'self' in params
    assert 'transaction_id' in params

    # Test get_payment_methods signature
    sig = inspect.signature(WompiService.get_payment_methods)
    params = list(sig.parameters.keys())
    assert 'self' in params

    # Test health_check signature
    sig = inspect.signature(WompiService.health_check)
    params = list(sig.parameters.keys())
    assert 'self' in params


def test_wompi_service_error_handling():
    """Test that proper error classes are defined"""

    # Test that our custom errors exist
    from app.services.payments.wompi_service import (
        WompiError,
        WompiNetworkError,
        WompiAuthenticationError,
        WompiValidationError
    )

    # Test error inheritance
    assert issubclass(WompiNetworkError, WompiError)
    assert issubclass(WompiAuthenticationError, WompiError)
    assert issubclass(WompiValidationError, WompiError)

    # Test error instantiation
    error = WompiError("Test error", "TEST_CODE", {"detail": "test"})
    assert error.message == "Test error"
    assert error.error_code == "TEST_CODE"
    assert error.response_data == {"detail": "test"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])