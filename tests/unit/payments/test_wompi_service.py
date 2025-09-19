import pytest
import httpx
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from app.services.payments.wompi_service import WompiService, WompiConfig
from app.services.payments.wompi_service import PaymentSourceCard, PaymentSourcePSE, PaymentRequest


class TestWompiConfig:
    """Test WompiConfig initialization and validation"""

    @pytest.fixture
    def clean_env(self, monkeypatch):
        """Clean environment for testing"""
        env_vars = ["WOMPI_PUBLIC_KEY", "WOMPI_PRIVATE_KEY", "WOMPI_ENVIRONMENT",
                   "WOMPI_WEBHOOK_SECRET", "WOMPI_BASE_URL", "PYTEST_CURRENT_TEST", "TESTING"]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

    def test_config_with_valid_environment(self, monkeypatch):
        """Test config initialization with valid environment variables"""
        monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_12345")
        monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_12345")
        monkeypatch.setenv("WOMPI_WEBHOOK_SECRET", "test_secret")

        config = WompiConfig()

        assert config.public_key == "pub_test_12345"
        assert config.private_key == "prv_test_12345"
        assert config.webhook_secret == "test_secret"
        assert config.environment == "test"
        assert config.base_url == "https://sandbox.wompi.co/v1"

    def test_config_missing_keys_production(self, monkeypatch):
        """Test config fails when missing keys in production"""
        # Clear all environment variables
        env_vars = ["WOMPI_PUBLIC_KEY", "WOMPI_PRIVATE_KEY", "WOMPI_ENVIRONMENT",
                   "WOMPI_WEBHOOK_SECRET", "WOMPI_BASE_URL", "PYTEST_CURRENT_TEST",
                   "TESTING", "_"]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        # Set production environment
        monkeypatch.setenv("WOMPI_ENVIRONMENT", "production")

        with pytest.raises(ValueError, match="WOMPI_PUBLIC_KEY and WOMPI_PRIVATE_KEY must be set"):
            WompiConfig()

    def test_config_missing_keys_test_environment(self, monkeypatch):
        """Test config uses defaults in test environment"""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_something")

        config = WompiConfig()

        assert config.public_key == "pub_test_default"
        assert config.private_key == "prv_test_default"

    def test_config_custom_base_url(self, monkeypatch):
        """Test config uses custom base URL"""
        monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_12345")
        monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_12345")
        monkeypatch.setenv("WOMPI_BASE_URL", "https://production.wompi.co/v1")

        config = WompiConfig()

        assert config.base_url == "https://production.wompi.co/v1"


class TestWompiService:
    """Test WompiService functionality"""

    @pytest.fixture
    def wompi_service(self, monkeypatch):
        """Create WompiService instance for testing"""
        monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_12345")
        monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_12345")
        monkeypatch.setenv("WOMPI_WEBHOOK_SECRET", "test_secret")
        return WompiService()

    @pytest.fixture
    def mock_response(self):
        """Create mock HTTP response"""
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock()
        return response

    @pytest.mark.asyncio
    async def test_get_acceptance_token_success(self, wompi_service, mock_response):
        """Test successful acceptance token retrieval"""
        mock_response.json.return_value = {
            "data": {
                "presigned_acceptance": {
                    "acceptance_token": "test_acceptance_token",
                    "permalink": "https://test.com/terms"
                }
            }
        }

        with patch.object(wompi_service, '_make_request', return_value=mock_response) as mock_request:
            result = await wompi_service.get_acceptance_token()

            assert result["acceptance_token"] == "test_acceptance_token"
            assert result["permalink"] == "https://test.com/terms"
            mock_request.assert_called_once_with("GET", "/merchants/pub_test_12345")

    @pytest.mark.asyncio
    async def test_get_acceptance_token_http_error(self, wompi_service):
        """Test acceptance token retrieval with HTTP error"""
        from app.services.payments.wompi_service import WompiError
        with patch.object(wompi_service, '_make_request', side_effect=WompiError("Network error")):
            with pytest.raises(WompiError, match="Network error"):
                await wompi_service.get_acceptance_token()

    @pytest.mark.asyncio
    async def test_tokenize_card_success(self, wompi_service, mock_response):
        """Test successful card tokenization"""
        card_data = {
            "number": "4111111111111111",
            "exp_month": "12",
            "exp_year": "2025",
            "cvc": "123",
            "card_holder": "John Doe"
        }

        mock_response.json.return_value = {
            "data": {
                "id": "tok_test_12345",
                "status": "AVAILABLE"
            }
        }

        with patch.object(wompi_service, '_make_request', return_value=mock_response) as mock_request:
            result = await wompi_service.tokenize_card(card_data)

            assert result["data"]["id"] == "tok_test_12345"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_tokenize_card_http_error(self, wompi_service):
        """Test card tokenization with HTTP error"""
        card_data = {
            "number": "4111111111111111",
            "exp_month": "12",
            "exp_year": "2025",
            "cvc": "123",
            "card_holder": "John Doe"
        }

        with patch.object(wompi_service.client, 'post', side_effect=httpx.HTTPError("Invalid card")):
            with pytest.raises(Exception, match="Card tokenization failed"):
                await wompi_service.tokenize_card(card_data)

    @pytest.mark.asyncio
    async def test_create_payment_source_card(self, wompi_service, mock_response):
        """Test creating card payment source"""
        # Mock acceptance token call
        acceptance_token_response = Mock()
        acceptance_token_response.raise_for_status = Mock()
        acceptance_token_response.json.return_value = {
            "data": {
                "presigned_acceptance": {
                    "acceptance_token": "test_acceptance_token"
                }
            }
        }

        # Mock payment source creation
        payment_source_response = Mock()
        payment_source_response.raise_for_status = Mock()
        payment_source_response.json.return_value = {
            "data": {
                "id": 12345,
                "status": "AVAILABLE"
            }
        }

        payment_data = {
            "type": "CARD",
            "token": "tok_test_12345",
            "customer_email": "test@example.com",
            "phone_number": "1234567890",
            "full_name": "John Doe"
        }

        with patch.object(wompi_service.client, 'get', return_value=acceptance_token_response), \
             patch.object(wompi_service.client, 'post', return_value=payment_source_response) as mock_post:

            result = await wompi_service.create_payment_source(payment_data)

            assert result["data"]["id"] == 12345

            # Verify the payload structure
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["type"] == "CARD"
            assert payload["token"] == "tok_test_12345"
            assert payload["acceptance_token"] == "test_acceptance_token"
            assert payload["customer_email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_payment_source_pse(self, wompi_service, mock_response):
        """Test creating PSE payment source"""
        # Mock acceptance token call
        acceptance_token_response = Mock()
        acceptance_token_response.raise_for_status = Mock()
        acceptance_token_response.json.return_value = {
            "data": {
                "presigned_acceptance": {
                    "acceptance_token": "test_acceptance_token"
                }
            }
        }

        # Mock payment source creation
        payment_source_response = Mock()
        payment_source_response.raise_for_status = Mock()
        payment_source_response.json.return_value = {
            "data": {
                "id": 12345,
                "redirect_url": "https://banco.com/pse"
            }
        }

        payment_data = {
            "type": "PSE",
            "user_type": "0",
            "user_legal_id": "12345678",
            "financial_institution_code": "1001",
            "payment_description": "Test payment",
            "customer_email": "test@example.com"
        }

        with patch.object(wompi_service.client, 'get', return_value=acceptance_token_response), \
             patch.object(wompi_service.client, 'post', return_value=payment_source_response) as mock_post:

            result = await wompi_service.create_payment_source(payment_data)

            assert result["data"]["id"] == 12345

            # Verify the payload structure
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["type"] == "PSE"
            assert payload["user_type"] == "0"
            assert payload["user_legal_id"] == "12345678"
            assert payload["financial_institution_code"] == "1001"

    @pytest.mark.asyncio
    async def test_create_transaction_success(self, wompi_service, mock_response):
        """Test successful transaction creation"""
        transaction_data = {
            "amount_in_cents": 10000,
            "currency": "COP",
            "customer_email": "test@example.com",
            "payment_method": {"type": "CARD"},
            "reference": "TEST_12345",
            "redirect_url": "https://example.com/return",
            "payment_source_id": 12345
        }

        mock_response.json.return_value = {
            "data": {
                "id": "trx_test_12345",
                "status": "PENDING",
                "payment_link_url": "https://checkout.wompi.co/p/trx_test_12345"
            }
        }

        with patch.object(wompi_service.client, 'post', return_value=mock_response) as mock_post:
            result = await wompi_service.create_transaction(transaction_data)

            assert result["data"]["id"] == "trx_test_12345"
            assert result["data"]["status"] == "PENDING"
            mock_post.assert_called_once_with("/transactions", json=transaction_data)

    @pytest.mark.asyncio
    async def test_get_transaction_success(self, wompi_service, mock_response):
        """Test successful transaction retrieval"""
        transaction_id = "trx_test_12345"

        mock_response.json.return_value = {
            "data": {
                "id": transaction_id,
                "status": "APPROVED",
                "amount_in_cents": 10000
            }
        }

        with patch.object(wompi_service.client, 'get', return_value=mock_response) as mock_get:
            result = await wompi_service.get_transaction(transaction_id)

            assert result["data"]["id"] == transaction_id
            assert result["data"]["status"] == "APPROVED"
            mock_get.assert_called_once_with(f"/transactions/{transaction_id}")

    @pytest.mark.asyncio
    async def test_get_pse_banks_success(self, wompi_service, mock_response):
        """Test successful PSE banks retrieval"""
        mock_response.json.return_value = {
            "data": [
                {
                    "financial_institution_code": "1001",
                    "financial_institution_name": "Banco de Prueba"
                },
                {
                    "financial_institution_code": "1002",
                    "financial_institution_name": "Banco Ejemplo"
                }
            ]
        }

        with patch.object(wompi_service.client, 'get', return_value=mock_response):
            result = await wompi_service.get_pse_banks()

            assert len(result) == 2
            assert result[0]["financial_institution_code"] == "1001"
            assert result[1]["financial_institution_name"] == "Banco Ejemplo"

    @pytest.mark.asyncio
    async def test_get_pse_banks_error(self, wompi_service):
        """Test PSE banks retrieval with error"""
        with patch.object(wompi_service.client, 'get', side_effect=httpx.HTTPError("Network error")):
            result = await wompi_service.get_pse_banks()

            assert result == []  # Should return empty list on error

    def test_validate_webhook_signature_valid(self, wompi_service):
        """Test webhook signature validation with valid signature"""
        payload = '{"event": "transaction.updated", "data": {"id": "123"}}'
        # Generate expected signature
        expected_signature = wompi_service._generate_signature(payload)

        result = wompi_service.validate_webhook_signature(payload, expected_signature)

        assert result is True

    def test_validate_webhook_signature_invalid(self, wompi_service):
        """Test webhook signature validation with invalid signature"""
        payload = '{"event": "transaction.updated", "data": {"id": "123"}}'
        invalid_signature = "invalid_signature"

        result = wompi_service.validate_webhook_signature(payload, invalid_signature)

        assert result is False

    @pytest.mark.asyncio
    async def test_process_webhook_transaction_updated(self, wompi_service, mock_response):
        """Test webhook processing for transaction.updated event"""
        payload = {
            "event": "transaction.updated",
            "data": {
                "id": "trx_test_12345",
                "status": "APPROVED"
            }
        }

        mock_response.json.return_value = {
            "data": {
                "id": "trx_test_12345",
                "status": "APPROVED",
                "amount_in_cents": 10000
            }
        }

        with patch.object(wompi_service.client, 'get', return_value=mock_response):
            result = await wompi_service.process_webhook(payload)

            assert result["event"] == "transaction.updated"
            assert result["processed"] is True
            assert result["transaction"]["data"]["status"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_process_webhook_unknown_event(self, wompi_service):
        """Test webhook processing for unknown event type"""
        payload = {
            "event": "unknown.event",
            "data": {}
        }

        result = await wompi_service.process_webhook(payload)

        assert result["event"] == "unknown.event"
        assert result["processed"] is False

    @pytest.mark.asyncio
    async def test_void_transaction_success(self, wompi_service, mock_response):
        """Test successful transaction voiding"""
        transaction_id = "trx_test_12345"

        mock_response.json.return_value = {
            "data": {
                "id": transaction_id,
                "status": "VOIDED"
            }
        }

        with patch.object(wompi_service.client, 'post', return_value=mock_response) as mock_post:
            result = await wompi_service.void_transaction(transaction_id)

            assert result["data"]["status"] == "VOIDED"
            mock_post.assert_called_once_with(f"/transactions/{transaction_id}/void")

    def test_amount_conversion_to_cents(self, wompi_service):
        """Test amount conversion to cents"""
        assert wompi_service.amount_to_cents(100.0) == 10000
        assert wompi_service.amount_to_cents(50.75) == 5075
        assert wompi_service.amount_to_cents(0.01) == 1

    def test_amount_conversion_from_cents(self, wompi_service):
        """Test amount conversion from cents"""
        assert wompi_service.cents_to_amount(10000) == 100.0
        assert wompi_service.cents_to_amount(5075) == 50.75
        assert wompi_service.cents_to_amount(1) == 0.01

    def test_generate_reference(self, wompi_service):
        """Test reference generation"""
        order_id = 12345
        reference = wompi_service.generate_reference(order_id)

        assert reference.startswith("ORDER_12345_")
        assert len(reference) > len("ORDER_12345_")

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, wompi_service):
        """Test WompiService as async context manager"""
        async with wompi_service as service:
            assert service is wompi_service

        # Verify client is closed (this would need to be mocked in real tests)
        # For now just verify the context manager works


class TestPaymentModels:
    """Test payment request/response models"""

    def test_payment_source_card_model(self):
        """Test PaymentSourceCard model validation"""
        card = PaymentSourceCard(
            token="tok_test_12345",
            installments=3
        )

        assert card.type == "CARD"
        assert card.token == "tok_test_12345"
        assert card.installments == 3

    def test_payment_source_pse_model(self):
        """Test PaymentSourcePSE model validation"""
        pse = PaymentSourcePSE(
            user_type="0",
            user_legal_id="12345678",
            financial_institution_code="1001",
            payment_description="Test payment"
        )

        assert pse.type == "PSE"
        assert pse.user_type == "0"
        assert pse.user_legal_id == "12345678"
        assert pse.financial_institution_code == "1001"

    def test_payment_request_model(self):
        """Test PaymentRequest model validation"""
        request = PaymentRequest(
            amount_in_cents=10000,
            customer_email="test@example.com",
            payment_method={"type": "CARD"},
            redirect_url="https://example.com/return",
            reference="TEST_12345"
        )

        assert request.amount_in_cents == 10000
        assert request.currency == "COP"
        assert request.customer_email == "test@example.com"
        assert request.reference == "TEST_12345"

    def test_payment_request_model_with_optional_fields(self):
        """Test PaymentRequest model with optional fields"""
        request = PaymentRequest(
            amount_in_cents=10000,
            currency="USD",
            customer_email="test@example.com",
            payment_method={"type": "CARD"},
            redirect_url="https://example.com/return",
            reference="TEST_12345",
            payment_source_id=12345
        )

        assert request.currency == "USD"
        assert request.payment_source_id == 12345


class TestWompiServiceEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    def wompi_service(self, monkeypatch):
        """Create WompiService instance for testing"""
        monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_12345")
        monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_12345")
        monkeypatch.setenv("WOMPI_WEBHOOK_SECRET", "test_secret")
        return WompiService()

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, wompi_service):
        """Test handling of network timeouts"""
        with patch.object(wompi_service.client, 'get', side_effect=httpx.TimeoutException("Request timeout")):
            with pytest.raises(Exception):
                await wompi_service.get_acceptance_token()

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, wompi_service):
        """Test handling of invalid JSON responses"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with patch.object(wompi_service.client, 'get', return_value=mock_response):
            with pytest.raises(Exception):
                await wompi_service.get_acceptance_token()

    @pytest.mark.asyncio
    async def test_api_rate_limiting(self, wompi_service):
        """Test handling of API rate limiting"""
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limit exceeded",
            request=Mock(),
            response=rate_limit_response
        )

        with patch.object(wompi_service.client, 'get', return_value=rate_limit_response):
            with pytest.raises(Exception):
                await wompi_service.get_acceptance_token()

    def test_webhook_signature_with_empty_payload(self, wompi_service):
        """Test webhook signature validation with empty payload"""
        result = wompi_service.validate_webhook_signature("", "signature")
        assert result is False

    def test_webhook_signature_with_none_secret(self, monkeypatch):
        """Test webhook signature validation when secret is None"""
        monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_12345")
        monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_12345")
        # Don't set webhook secret

        service = WompiService()
        # This should handle the case where webhook_secret is None
        result = service.validate_webhook_signature("payload", "signature")
        assert result is False