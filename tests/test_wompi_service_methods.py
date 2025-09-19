"""
Comprehensive Unit Tests for WompiService Critical Methods
===========================================================

Tests for the 3 critical missing methods implemented:
- get_transaction_status()
- get_payment_methods()
- health_check()

Author: Wompi Payment Integrator Agent
Date: 2025-09-18
Coverage Target: 95%+
"""

import pytest
import httpx
import json
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

# Import the service and related classes
from app.services.payments.wompi_service import (
    WompiService,
    WompiError,
    WompiNetworkError,
    WompiAuthenticationError,
    WompiValidationError,
    WompiRateLimitError,
    WompiConfig
)


class TestWompiServiceTransactionStatus:
    """Test suite for get_transaction_status method"""

    @pytest.fixture
    def mock_wompi_service(self):
        """Create WompiService with mocked dependencies"""
        service = Mock(spec=WompiService)
        service.config = Mock()
        service.config.public_key = "pub_test_123"
        service.config.private_key = "prv_test_456"
        service.config.environment = "test"
        service.config.base_url = "https://sandbox.wompi.co/v1"
        service.config.timeout = 30.0
        service.config.retry_config = Mock()
        service.config.retry_config.max_attempts = 3
        service._request_count = 0
        service._rate_limit_window_start = time.time()
        service._circuit_breaker_failures = 0
        service._circuit_breaker_last_failure = 0
        service._circuit_breaker_threshold = 5
        service.client = AsyncMock()

        # Mock the actual methods we're testing
        service.get_transaction_status = AsyncMock()
        service.get_payment_methods = AsyncMock()
        service.health_check = AsyncMock()
        service._make_request = AsyncMock()
        service.get_pse_banks = AsyncMock()

        return service

    @pytest.mark.asyncio
    async def test_get_transaction_status_success(self, mock_wompi_service):
        """Test successful transaction status retrieval"""
        transaction_id = "trans_123456"
        mock_response_data = {
            "data": {
                "id": transaction_id,
                "status": "APPROVED",
                "status_message": "Transaction approved",
                "amount_in_cents": 50000,
                "currency": "COP",
                "reference": "ORDER_123_20250918",
                "payment_method": {"type": "CARD", "installments": 1},
                "created_at": "2025-09-18T10:00:00Z",
                "finalized_at": "2025-09-18T10:01:00Z",
                "customer_email": "test@example.com",
                "customer_data": {"name": "Test User"},
                "billing_data": {"address": "Test Address"},
                "taxes": []
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)

        result = await mock_wompi_service.get_transaction_status(transaction_id)

        # Verify API call
        mock_wompi_service._make_request.assert_called_once_with(
            "GET", f"/transactions/{transaction_id}"
        )

        # Verify response structure
        assert result["transaction_id"] == transaction_id
        assert result["status"] == "APPROVED"
        assert result["status_message"] == "Transaction approved"
        assert result["amount_in_cents"] == 50000
        assert result["currency"] == "COP"
        assert result["reference"] == "ORDER_123_20250918"
        assert result["payment_method"]["type"] == "CARD"
        assert result["customer_email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_transaction_status_invalid_id(self, mock_wompi_service):
        """Test validation error for invalid transaction ID"""

        # Test empty string
        with pytest.raises(WompiValidationError) as exc_info:
            await mock_wompi_service.get_transaction_status("")
        assert "Transaction ID must be a non-empty string" in str(exc_info.value)

        # Test None
        with pytest.raises(WompiValidationError) as exc_info:
            await mock_wompi_service.get_transaction_status(None)
        assert "Transaction ID must be a non-empty string" in str(exc_info.value)

        # Test non-string
        with pytest.raises(WompiValidationError) as exc_info:
            await mock_wompi_service.get_transaction_status(123)
        assert "Transaction ID must be a non-empty string" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_transaction_status_invalid_response(self, mock_wompi_service):
        """Test handling of invalid API response"""
        transaction_id = "trans_123456"

        # Response without data field
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Something went wrong"}
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)

        with pytest.raises(WompiValidationError) as exc_info:
            await mock_wompi_service.get_transaction_status(transaction_id)
        assert "Invalid response structure" in str(exc_info.value)
        assert transaction_id in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_transaction_status_network_error(self, mock_wompi_service):
        """Test network error handling"""
        transaction_id = "trans_123456"

        mock_wompi_service._make_request = AsyncMock(
            side_effect=WompiNetworkError("Network timeout")
        )

        with pytest.raises(WompiNetworkError) as exc_info:
            await mock_wompi_service.get_transaction_status(transaction_id)
        assert "Network timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_transaction_status_unexpected_error(self, mock_wompi_service):
        """Test unexpected error handling"""
        transaction_id = "trans_123456"

        mock_wompi_service._make_request = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )

        with pytest.raises(WompiError) as exc_info:
            await mock_wompi_service.get_transaction_status(transaction_id)
        assert "Failed to get transaction status" in str(exc_info.value)


class TestWompiServicePaymentMethods:
    """Test suite for get_payment_methods method"""

    @pytest.fixture
    def mock_wompi_service(self):
        """Create WompiService with mocked dependencies"""
        with patch.object(WompiConfig, '__init__', return_value=None):
            service = WompiService()
            service.config = Mock()
            service.config.public_key = "pub_test_123"
            service.config.private_key = "prv_test_456"
            service.config.environment = "test"
            service.config.base_url = "https://sandbox.wompi.co/v1"
            service.config.timeout = 30.0
            service._request_count = 0
            service._rate_limit_window_start = time.time()
            service._circuit_breaker_failures = 0
            service._circuit_breaker_last_failure = 0
            service._circuit_breaker_threshold = 5
            service.client = AsyncMock()
            return service

    @pytest.mark.asyncio
    async def test_get_payment_methods_success_with_card_and_pse(self, mock_wompi_service):
        """Test successful payment methods retrieval with both card and PSE"""
        mock_merchant_data = {
            "data": {
                "id": "merchant_123",
                "name": "Test Merchant",
                "payment_methods": {
                    "card": ["VISA", "MASTERCARD"],
                    "pse": True
                }
            }
        }

        mock_pse_banks = [
            {"financial_institution_code": "1007", "financial_institution_name": "Bancolombia"},
            {"financial_institution_code": "1019", "financial_institution_name": "Scotiabank"}
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_pse_banks = AsyncMock(return_value=mock_pse_banks)

        result = await mock_wompi_service.get_payment_methods()

        # Verify API call
        mock_wompi_service._make_request.assert_called_once_with(
            "GET", f"/merchants/{mock_wompi_service.config.public_key}"
        )

        # Should have card methods (2) + PSE (1) = 3 methods
        assert len(result) == 3

        # Check card methods
        card_methods = [pm for pm in result if pm["type"] == "CARD"]
        assert len(card_methods) == 2

        visa_method = next(pm for pm in card_methods if pm["processor"] == "VISA")
        assert visa_method["name"] == "Credit/Debit Card"
        assert visa_method["supported_currencies"] == ["COP"]
        assert visa_method["installments_available"] is True
        assert visa_method["max_installments"] == 36

        # Check PSE method
        pse_methods = [pm for pm in result if pm["type"] == "PSE"]
        assert len(pse_methods) == 1

        pse_method = pse_methods[0]
        assert pse_method["name"] == "PSE (Pagos Seguros en Línea)"
        assert pse_method["requires_user_type"] is True
        assert pse_method["requires_legal_id"] is True
        assert pse_method["available_banks"] == mock_pse_banks

    @pytest.mark.asyncio
    async def test_get_payment_methods_pse_bank_failure(self, mock_wompi_service):
        """Test PSE method when bank retrieval fails"""
        mock_merchant_data = {
            "data": {
                "payment_methods": {
                    "pse": True
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_pse_banks = AsyncMock(side_effect=Exception("Bank API failed"))

        result = await mock_wompi_service.get_payment_methods()

        pse_method = next(pm for pm in result if pm["type"] == "PSE")
        assert pse_method["available_banks"] == []

    @pytest.mark.asyncio
    async def test_get_payment_methods_no_methods_configured(self, mock_wompi_service):
        """Test fallback when no payment methods are configured"""
        mock_merchant_data = {
            "data": {
                "payment_methods": {}
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)

        result = await mock_wompi_service.get_payment_methods()

        # Should return default card method
        assert len(result) == 1
        assert result[0]["type"] == "CARD"
        assert result[0]["name"] == "Credit/Debit Card"

    @pytest.mark.asyncio
    async def test_get_payment_methods_invalid_response(self, mock_wompi_service):
        """Test handling of invalid merchant response"""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)

        with pytest.raises(WompiValidationError) as exc_info:
            await mock_wompi_service.get_payment_methods()
        assert "No merchant data in response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_payment_methods_network_error(self, mock_wompi_service):
        """Test network error handling"""
        mock_wompi_service._make_request = AsyncMock(
            side_effect=WompiNetworkError("Connection failed")
        )

        with pytest.raises(WompiNetworkError):
            await mock_wompi_service.get_payment_methods()

    @pytest.mark.asyncio
    async def test_get_payment_methods_other_methods(self, mock_wompi_service):
        """Test handling of additional payment methods"""
        mock_merchant_data = {
            "data": {
                "payment_methods": {
                    "bancolombia_transfer": {"enabled": True},
                    "cash_payment": {"enabled": True}
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)

        result = await mock_wompi_service.get_payment_methods()

        # Should have 2 additional methods
        assert len(result) == 2

        bancolombia_method = next(pm for pm in result if pm["type"] == "BANCOLOMBIA_TRANSFER")
        assert bancolombia_method["name"] == "Bancolombia Transfer"


class TestWompiServiceHealthCheck:
    """Test suite for health_check method"""

    @pytest.fixture
    def mock_wompi_service(self):
        """Create WompiService with mocked dependencies"""
        with patch.object(WompiConfig, '__init__', return_value=None):
            service = WompiService()
            service.config = Mock()
            service.config.public_key = "pub_test_123"
            service.config.private_key = "prv_test_456"
            service.config.environment = "test"
            service.config.base_url = "https://sandbox.wompi.co/v1"
            service.config.timeout = 30.0
            service.config.rate_limit_requests = 100
            service.config.rate_limit_window = 60
            service._request_count = 10
            service._rate_limit_window_start = time.time()
            service._circuit_breaker_failures = 0
            service._circuit_breaker_last_failure = 0
            service._circuit_breaker_threshold = 5
            service.client = AsyncMock()
            return service

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, mock_wompi_service):
        """Test health check when all components are healthy"""
        mock_merchant_data = {
            "data": {
                "id": "merchant_123",
                "name": "Test Merchant"
            }
        }

        mock_payment_methods = [
            {"type": "CARD", "name": "Credit Card"},
            {"type": "PSE", "name": "PSE"}
        ]

        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_response.headers = {"X-API-Version": "1.0"}

        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_payment_methods = AsyncMock(return_value=mock_payment_methods)

        with patch('time.time', return_value=1000.0):
            result = await mock_wompi_service.health_check()

        # Overall status should be healthy
        assert result["status"] == "healthy"
        assert result["service"] == "WompiService"
        assert result["environment"] == "test"
        assert "timestamp" in result

        # Check individual components
        checks = result["checks"]

        # Connectivity check
        assert checks["connectivity"]["status"] == "healthy"
        assert "response_time_ms" in checks["connectivity"]
        assert checks["connectivity"]["api_version"] == "1.0"

        # Authentication check
        assert checks["authentication"]["status"] == "healthy"
        assert checks["authentication"]["merchant_id"] == "merchant_123"
        assert checks["authentication"]["merchant_name"] == "Test Merchant"

        # Configuration check
        assert checks["configuration"]["status"] == "healthy"
        assert checks["configuration"]["environment"] == "test"

        # Payment methods check
        assert checks["payment_methods"]["status"] == "healthy"
        assert checks["payment_methods"]["available_methods"] == 2
        assert checks["payment_methods"]["method_types"] == ["CARD", "PSE"]

        # Rate limiting check
        assert checks["rate_limiting"]["status"] == "healthy"
        assert checks["rate_limiting"]["current_requests"] == 10
        assert checks["rate_limiting"]["limit"] == 100

        # Circuit breaker check
        assert checks["circuit_breaker"]["status"] == "closed"
        assert checks["circuit_breaker"]["failure_count"] == 0

    @pytest.mark.asyncio
    async def test_health_check_authentication_failure(self, mock_wompi_service):
        """Test health check with authentication failure"""
        mock_wompi_service._make_request = AsyncMock(
            side_effect=WompiAuthenticationError("Invalid API key")
        )

        with pytest.raises(WompiAuthenticationError):
            await mock_wompi_service.health_check()

    @pytest.mark.asyncio
    async def test_health_check_network_failure(self, mock_wompi_service):
        """Test health check with network failure"""
        mock_wompi_service._make_request = AsyncMock(
            side_effect=WompiNetworkError("Connection timeout")
        )

        with pytest.raises(WompiNetworkError):
            await mock_wompi_service.health_check()

    @pytest.mark.asyncio
    async def test_health_check_invalid_configuration(self, mock_wompi_service):
        """Test health check with configuration issues"""
        # Set invalid configuration
        mock_wompi_service.config.public_key = "invalid_key"
        mock_wompi_service.config.private_key = "invalid_key"
        mock_wompi_service.config.environment = "invalid_env"

        mock_merchant_data = {"data": {"id": "merchant_123", "name": "Test"}}
        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_response.headers = {}

        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_payment_methods = AsyncMock(return_value=[])

        result = await mock_wompi_service.health_check()

        # Should be degraded due to configuration issues
        assert result["status"] == "degraded"

        config_check = result["checks"]["configuration"]
        assert config_check["status"] == "unhealthy"
        assert len(config_check["issues"]) == 3  # All 3 config issues

    @pytest.mark.asyncio
    async def test_health_check_payment_methods_failure(self, mock_wompi_service):
        """Test health check when payment methods retrieval fails"""
        mock_merchant_data = {"data": {"id": "merchant_123", "name": "Test"}}
        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_response.headers = {}

        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_payment_methods = AsyncMock(
            side_effect=Exception("Payment methods API failed")
        )

        result = await mock_wompi_service.health_check()

        # Should be degraded due to payment methods failure
        assert result["status"] == "degraded"

        pm_check = result["checks"]["payment_methods"]
        assert pm_check["status"] == "unhealthy"
        assert "Failed to retrieve payment methods" in pm_check["error"]

    @pytest.mark.asyncio
    async def test_health_check_circuit_breaker_open(self, mock_wompi_service):
        """Test health check with circuit breaker open"""
        # Set circuit breaker to open state
        mock_wompi_service._circuit_breaker_failures = 5
        mock_wompi_service._circuit_breaker_last_failure = time.time()

        mock_merchant_data = {"data": {"id": "merchant_123", "name": "Test"}}
        mock_response = Mock()
        mock_response.json.return_value = mock_merchant_data
        mock_response.headers = {}

        mock_wompi_service._make_request = AsyncMock(return_value=mock_response)
        mock_wompi_service.get_payment_methods = AsyncMock(return_value=[])

        result = await mock_wompi_service.health_check()

        # Should be unhealthy due to circuit breaker
        assert result["status"] == "unhealthy"

        cb_check = result["checks"]["circuit_breaker"]
        assert cb_check["status"] == "open"
        assert cb_check["failure_count"] == 5

    @pytest.mark.asyncio
    async def test_health_check_unexpected_error(self, mock_wompi_service):
        """Test health check with unexpected error"""
        mock_wompi_service._make_request = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )

        with pytest.raises(WompiError) as exc_info:
            await mock_wompi_service.health_check()
        assert "Health check failed" in str(exc_info.value)


# Integration test class
class TestWompiServiceIntegration:
    """Integration tests for the three methods working together"""

    @pytest.fixture
    def mock_wompi_service(self):
        """Create WompiService with mocked dependencies"""
        with patch.object(WompiConfig, '__init__', return_value=None):
            service = WompiService()
            service.config = Mock()
            service.config.public_key = "pub_test_123"
            service.config.private_key = "prv_test_456"
            service.config.environment = "test"
            service.config.base_url = "https://sandbox.wompi.co/v1"
            service.config.timeout = 30.0
            service.config.rate_limit_requests = 100
            service.config.rate_limit_window = 60
            service._request_count = 0
            service._rate_limit_window_start = time.time()
            service._circuit_breaker_failures = 0
            service._circuit_breaker_last_failure = 0
            service._circuit_breaker_threshold = 5
            service.client = AsyncMock()
            return service

    @pytest.mark.asyncio
    async def test_all_methods_work_together(self, mock_wompi_service):
        """Test that all three methods can be called successfully"""
        # Mock responses for health check and payment methods
        mock_merchant_data = {
            "data": {
                "id": "merchant_123",
                "name": "Test Merchant",
                "payment_methods": {"card": ["VISA"]}
            }
        }

        # Mock transaction status response
        mock_transaction_data = {
            "data": {
                "id": "trans_123",
                "status": "APPROVED",
                "amount_in_cents": 10000,
                "currency": "COP"
            }
        }

        mock_responses = [
            Mock(json=lambda: mock_merchant_data, headers={}),  # For health_check
            Mock(json=lambda: mock_merchant_data, headers={}),  # For get_payment_methods
            Mock(json=lambda: mock_transaction_data, headers={})  # For get_transaction_status
        ]

        mock_wompi_service._make_request = AsyncMock(side_effect=mock_responses)
        mock_wompi_service.get_pse_banks = AsyncMock(return_value=[])

        # Test health check
        health_result = await mock_wompi_service.health_check()
        assert health_result["status"] in ["healthy", "degraded"]

        # Test payment methods
        payment_methods = await mock_wompi_service.get_payment_methods()
        assert len(payment_methods) >= 1

        # Test transaction status
        transaction_status = await mock_wompi_service.get_transaction_status("trans_123")
        assert transaction_status["transaction_id"] == "trans_123"
        assert transaction_status["status"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_error_propagation_consistency(self, mock_wompi_service):
        """Test that all methods handle errors consistently"""
        # Test that all methods properly propagate WompiNetworkError
        mock_wompi_service._make_request = AsyncMock(
            side_effect=WompiNetworkError("Network error")
        )

        # All methods should raise WompiNetworkError
        with pytest.raises(WompiNetworkError):
            await mock_wompi_service.get_transaction_status("test_id")

        with pytest.raises(WompiNetworkError):
            await mock_wompi_service.get_payment_methods()

        with pytest.raises(WompiNetworkError):
            await mock_wompi_service.health_check()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])