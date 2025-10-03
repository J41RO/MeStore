"""
Integration Tests for Payment System
=====================================

Comprehensive integration testing covering:
- PayU service integration with database
- Efecty service integration with database
- Webhook processing with database transactions
- API endpoints with payment services
- Database transaction integrity
- Race condition testing
- Idempotency protection

Author: Integration Testing AI
Date: 2025-10-01
Purpose: Validate complete payment system integration
"""

import pytest
import asyncio
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status

# Import models
from app.models.order import Order, OrderTransaction, OrderStatus, PaymentStatus
from app.models.payment import WebhookEvent, WebhookEventType, WebhookEventStatus
from app.models.user import User

# Import services
from app.services.payments.payu_service import PayUService, PayUError, PayUConfig
from app.services.payments.efecty_service import EfectyService, EfectyError

# Import endpoints
from app.api.v1.endpoints.webhooks import (
    verify_wompi_signature,
    map_wompi_status_to_order_status,
    update_order_from_webhook
)


# ===== FIXTURES =====

@pytest.fixture
async def test_order(db_session: AsyncSession, test_buyer: User):
    """Create test order for payment integration tests"""
    order = Order(
        order_number=f"ORD-TEST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        buyer_id=test_buyer.id,
        subtotal=100000.0,
        tax_amount=19000.0,
        shipping_cost=10000.0,
        discount_amount=0.0,
        total_amount=129000.0,
        status=OrderStatus.PENDING,
        shipping_name="Test Customer",
        shipping_phone="+573001234567",
        shipping_email="test@example.com",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_postal_code="110111",
        shipping_country="CO"
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest.fixture
def payu_transaction_data():
    """Sample PayU transaction data"""
    return {
        "amount_in_cents": 12900000,  # 129,000 COP
        "customer_email": "test@example.com",
        "payment_method": "VISA",
        "reference": "ORD-TEST-12345",
        "description": "Test Order Payment",
        "customer_id": 1,
        "customer_data": {
            "full_name": "Test Customer",
            "phone": "+573001234567",
            "document": "1234567890"
        },
        "payment_data": {
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiration_date": "2025/12",
            "card_holder": "Test Customer",
            "installments": 1
        },
        "notify_url": "https://example.com/webhooks/payu",
        "ip_address": "127.0.0.1",
        "device_session_id": "test-device-123"
    }


@pytest.fixture
def wompi_webhook_payload():
    """Sample Wompi webhook payload"""
    return {
        "event": "transaction.updated",
        "data": {
            "id": "wompi-txn-12345",
            "reference": "ORD-TEST-12345",
            "status": "APPROVED",
            "amount_in_cents": 12900000,
            "currency": "COP",
            "payment_method_type": "CARD",
            "status_message": "Transaction approved",
            "created_at": datetime.utcnow().isoformat(),
            "finalized_at": datetime.utcnow().isoformat()
        },
        "sent_at": datetime.utcnow().isoformat(),
        "timestamp": int(datetime.utcnow().timestamp())
    }


@pytest.fixture
def payu_webhook_payload():
    """Sample PayU webhook payload"""
    return {
        "merchant_id": "508029",
        "reference_sale": "ORD-TEST-12345",
        "value": "129000.00",
        "currency": "COP",
        "state_pol": "4",  # APPROVED
        "transaction_id": "payu-txn-67890",
        "payment_method_name": "VISA",
        "response_message_pol": "APPROVED",
        "sign": "",  # Will be calculated
    }


# ===== PAYU SERVICE INTEGRATION TESTS =====

class TestPayUServiceIntegration:
    """Test PayU service integration with database"""

    @pytest.mark.asyncio
    async def test_payu_signature_generation(self):
        """Test PayU signature generation algorithm"""
        service = PayUService()

        # Test signature with known values
        reference = "TEST-ORDER-123"
        amount = "50000.0"
        currency = "COP"

        signature = service._generate_signature(reference, amount, currency)

        # Signature should be MD5 hash (32 chars)
        assert len(signature) == 32
        assert signature.isalnum()

        # Same inputs should generate same signature (deterministic)
        signature2 = service._generate_signature(reference, amount, currency)
        assert signature == signature2

    @pytest.mark.asyncio
    async def test_payu_transaction_creation_with_db(
        self,
        db_session: AsyncSession,
        test_order: Order,
        payu_transaction_data: Dict[str, Any]
    ):
        """Test PayU transaction creation and database storage"""
        service = PayUService()

        # Mock the HTTP request to PayU
        mock_response = {
            "code": "SUCCESS",
            "transactionResponse": {
                "state": "APPROVED",
                "transactionId": "payu-12345",
                "orderId": "order-67890",
                "responseCode": "APPROVED",
                "responseMessage": "Transaction approved",
                "authorizationCode": "AUTH-123",
                "trazabilityCode": "TRACE-456"
            }
        }

        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            # Update transaction data with test order reference
            payu_transaction_data["reference"] = test_order.order_number

            # Create transaction
            result = await service.create_transaction(payu_transaction_data)

            # Validate result
            assert result["status"] == "approved"
            assert result["transaction_id"] == "payu-12345"
            assert result["order_id"] == "order-67890"
            assert result["authorization_code"] == "AUTH-123"

            # Create database transaction record
            transaction = OrderTransaction(
                transaction_reference=f"TXN-{test_order.order_number}-{result['transaction_id'][:10]}",
                order_id=test_order.id,
                amount=payu_transaction_data["amount_in_cents"] / 100.0,
                currency="COP",
                status=PaymentStatus.APPROVED,
                payment_method_type="VISA",
                gateway="payu",
                gateway_transaction_id=result["transaction_id"],
                gateway_response=json.dumps(result["raw_response"]),
                processed_at=datetime.utcnow()
            )
            db_session.add(transaction)

            # Update order status
            test_order.status = OrderStatus.CONFIRMED
            test_order.confirmed_at = datetime.utcnow()

            await db_session.commit()
            await db_session.refresh(test_order)

            # Validate database state
            assert test_order.status == OrderStatus.CONFIRMED
            assert test_order.confirmed_at is not None
            assert len(test_order.transactions) == 1
            assert test_order.transactions[0].status == PaymentStatus.APPROVED

    @pytest.mark.asyncio
    async def test_payu_webhook_signature_validation(self):
        """Test PayU webhook signature verification"""
        service = PayUService()

        payload = {
            "reference_sale": "TEST-ORDER-123",
            "value": "50000.0",
            "currency": "COP",
            "state_pol": "4"
        }

        # Generate signature
        api_key = service.config.api_key
        merchant_id = service.config.merchant_id
        signature_string = f"{api_key}~{merchant_id}~{payload['reference_sale']}~{payload['value']}~{payload['currency']}~{payload['state_pol']}"
        expected_signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

        # Validate signature
        is_valid = service.validate_webhook_signature(payload, expected_signature)
        assert is_valid is True

        # Test with invalid signature
        is_valid = service.validate_webhook_signature(payload, "invalid-signature")
        assert is_valid is False


# ===== EFECTY SERVICE INTEGRATION TESTS =====

class TestEfectyServiceIntegration:
    """Test Efecty service integration with database"""

    @pytest.mark.asyncio
    async def test_efecty_code_generation(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test Efecty payment code generation and validation"""
        service = EfectyService()

        # Generate payment code
        code_data = service.generate_payment_code(
            order_id=test_order.id,
            amount=129000,  # COP
            customer_email="test@example.com",
            customer_name="Test Customer",
            customer_phone="+573001234567"
        )

        # Validate code structure
        assert "payment_code" in code_data
        assert "barcode_data" in code_data
        assert "expiration_date" in code_data
        assert code_data["amount"] == 129000
        assert code_data["currency"] == "COP"

        # Validate code format (PREFIX-ORDERID-RANDOM)
        parts = code_data["payment_code"].split("-")
        assert len(parts) == 3
        assert parts[0] == service.config.code_prefix
        assert parts[1] == str(test_order.id)
        assert len(parts[2]) == 6

        # Store in database
        transaction = OrderTransaction(
            transaction_reference=f"TXN-EFECTY-{test_order.order_number}",
            order_id=test_order.id,
            amount=129000.0,
            currency="COP",
            status=PaymentStatus.PENDING,
            payment_method_type="EFECTY",
            gateway="efecty",
            gateway_reference=code_data["payment_code"],
            gateway_response=json.dumps(code_data),
            created_at=datetime.utcnow()
        )
        db_session.add(transaction)
        await db_session.commit()

        # Validate database storage
        result = await db_session.execute(
            select(OrderTransaction).where(
                OrderTransaction.gateway_reference == code_data["payment_code"]
            )
        )
        stored_transaction = result.scalar_one()
        assert stored_transaction is not None
        assert stored_transaction.payment_method_type == "EFECTY"

    @pytest.mark.asyncio
    async def test_efecty_code_validation_and_expiration(self):
        """Test Efecty code validation and expiration logic"""
        service = EfectyService()

        # Valid code
        code_data = service.generate_payment_code(
            order_id=12345,
            amount=50000,
            customer_email="test@example.com",
            customer_name="Test Customer"
        )

        payment_code = code_data["payment_code"]

        # Validate code
        validation = service.validate_payment_code(payment_code)
        assert validation["valid"] is True
        assert validation["order_id"] == 12345

        # Test expiration check
        created_at = datetime.utcnow() - timedelta(hours=service.config.payment_timeout_hours + 1)
        is_expired = service.is_code_expired(created_at)
        assert is_expired is True

        # Not expired
        created_at = datetime.utcnow()
        is_expired = service.is_code_expired(created_at)
        assert is_expired is False

    @pytest.mark.asyncio
    async def test_efecty_payment_confirmation(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test Efecty payment confirmation flow"""
        service = EfectyService()

        # Generate code
        code_data = service.generate_payment_code(
            order_id=test_order.id,
            amount=129000,
            customer_email="test@example.com",
            customer_name="Test Customer"
        )

        payment_code = code_data["payment_code"]

        # Simulate confirmation
        confirmation_data = service.generate_payment_confirmation_data(
            payment_code=payment_code,
            amount=129000,
            paid_at=datetime.utcnow(),
            efecty_transaction_id="EFY-TEST-123"
        )

        # Validate confirmation
        assert confirmation_data["payment_code"] == payment_code
        assert confirmation_data["order_id"] == test_order.id
        assert confirmation_data["amount"] == 129000
        assert confirmation_data["status"] == "confirmed"
        assert confirmation_data["payment_method"] == "EFECTY"


# ===== WEBHOOK INTEGRATION TESTS =====

class TestWebhookIntegration:
    """Test webhook processing with database transactions"""

    @pytest.mark.asyncio
    async def test_wompi_signature_verification(self):
        """Test Wompi HMAC SHA256 signature verification"""
        payload = b'{"event":"transaction.updated","data":{"id":"123"}}'
        secret = "test-secret-key"

        # Generate signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Verify signature
        is_valid = verify_wompi_signature(payload, signature, secret)
        assert is_valid is True

        # Invalid signature
        is_valid = verify_wompi_signature(payload, "invalid", secret)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_wompi_webhook_order_update(
        self,
        db_session: AsyncSession,
        test_order: Order,
        wompi_webhook_payload: Dict[str, Any]
    ):
        """Test Wompi webhook updates order status correctly"""
        # Update payload with test order reference
        wompi_webhook_payload["data"]["reference"] = test_order.order_number

        # Process webhook
        result = await update_order_from_webhook(
            db=db_session,
            transaction_data=wompi_webhook_payload["data"],
            wompi_transaction_id=wompi_webhook_payload["data"]["id"]
        )

        # Validate result
        assert result.success is True
        assert result.order_id == test_order.id
        assert result.status == "processed"

        # Refresh order from database
        await db_session.refresh(test_order)

        # Validate order status updated
        assert test_order.status == OrderStatus.CONFIRMED
        assert test_order.confirmed_at is not None

        # Validate transaction created
        assert len(test_order.transactions) == 1
        transaction = test_order.transactions[0]
        assert transaction.status == PaymentStatus.APPROVED
        assert transaction.gateway == "wompi"
        assert transaction.gateway_transaction_id == wompi_webhook_payload["data"]["id"]

    @pytest.mark.asyncio
    async def test_webhook_idempotency_protection(
        self,
        db_session: AsyncSession,
        test_order: Order,
        wompi_webhook_payload: Dict[str, Any]
    ):
        """Test webhook idempotency prevents duplicate processing"""
        wompi_webhook_payload["data"]["reference"] = test_order.order_number
        transaction_id = wompi_webhook_payload["data"]["id"]

        # Process webhook first time
        result1 = await update_order_from_webhook(
            db=db_session,
            transaction_data=wompi_webhook_payload["data"],
            wompi_transaction_id=transaction_id
        )
        assert result1.success is True

        # Create webhook event
        webhook_event = WebhookEvent(
            event_id=transaction_id,
            event_type=WebhookEventType.TRANSACTION_UPDATED,
            event_status=WebhookEventStatus.PROCESSED,
            raw_payload=wompi_webhook_payload,
            signature_validated=True,
            processed_at=datetime.utcnow()
        )
        db_session.add(webhook_event)
        await db_session.commit()

        # Check idempotency
        from app.api.v1.endpoints.webhooks import check_event_already_processed
        already_processed = await check_event_already_processed(db_session, transaction_id)
        assert already_processed is True

        # Attempting to process again should be detected
        result2 = await db_session.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == transaction_id)
        )
        existing_event = result2.scalar_one()
        assert existing_event.event_status == WebhookEventStatus.PROCESSED

    @pytest.mark.asyncio
    async def test_wompi_status_mapping(self):
        """Test Wompi status mapping to internal statuses"""
        # Test all status mappings
        test_cases = [
            ("APPROVED", OrderStatus.CONFIRMED, PaymentStatus.APPROVED),
            ("DECLINED", OrderStatus.PENDING, PaymentStatus.DECLINED),
            ("PENDING", OrderStatus.PENDING, PaymentStatus.PENDING),
            ("ERROR", OrderStatus.PENDING, PaymentStatus.ERROR),
            ("VOIDED", OrderStatus.CANCELLED, PaymentStatus.CANCELLED),
        ]

        for wompi_status, expected_order_status, expected_payment_status in test_cases:
            order_status, payment_status = map_wompi_status_to_order_status(wompi_status)
            assert order_status == expected_order_status
            assert payment_status == expected_payment_status


# ===== API ENDPOINT INTEGRATION TESTS =====

class TestPaymentAPIIntegration:
    """Test payment API endpoints with service integration"""

    @pytest.mark.asyncio
    async def test_payment_config_endpoint(self, async_client: AsyncClient):
        """Test payment configuration endpoint"""
        response = await async_client.get("/api/v1/payments/config")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "wompi_public_key" in data
        assert "environment" in data
        assert "accepted_methods" in data
        assert "currency" in data
        assert data["currency"] == "COP"

    @pytest.mark.asyncio
    async def test_payment_methods_endpoint(self, async_client: AsyncClient):
        """Test payment methods endpoint with PSE banks"""
        response = await async_client.get("/api/v1/payments/methods")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["card_enabled"] is True
        assert data["pse_enabled"] is True
        assert "pse_banks" in data
        assert len(data["pse_banks"]) > 0
        assert data["currency"] == "COP"

    @pytest.mark.asyncio
    async def test_webhook_endpoint_with_signature(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_order: Order,
        wompi_webhook_payload: Dict[str, Any]
    ):
        """Test webhook endpoint with signature verification"""
        from app.core.config import settings

        # Update payload with test order
        wompi_webhook_payload["data"]["reference"] = test_order.order_number

        # Generate signature
        payload_bytes = json.dumps(wompi_webhook_payload).encode('utf-8')
        signature = hmac.new(
            settings.WOMPI_WEBHOOK_SECRET.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

        # Send webhook request
        response = await async_client.post(
            "/api/v1/webhooks/wompi",
            json=wompi_webhook_payload,
            headers={"X-Event-Signature": signature}
        )

        # Should always return 200 OK per Wompi spec
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"


# ===== RACE CONDITION TESTS =====

class TestRaceConditions:
    """Test concurrent webhook processing and race conditions"""

    @pytest.mark.asyncio
    async def test_concurrent_webhook_processing(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test that concurrent webhook processing is handled correctly"""
        # Create two identical webhooks
        webhook_data = {
            "id": "wompi-concurrent-test",
            "reference": test_order.order_number,
            "status": "APPROVED",
            "amount_in_cents": 12900000,
            "payment_method_type": "CARD"
        }

        # Process concurrently (simulating race condition)
        results = await asyncio.gather(
            update_order_from_webhook(db_session, webhook_data, "wompi-concurrent-test"),
            update_order_from_webhook(db_session, webhook_data, "wompi-concurrent-test"),
            return_exceptions=True
        )

        # One should succeed, one might fail or be idempotent
        successful_results = [r for r in results if not isinstance(r, Exception) and r.success]
        assert len(successful_results) >= 1

        # Verify database consistency
        await db_session.refresh(test_order)
        assert test_order.status == OrderStatus.CONFIRMED

        # Should only have one transaction
        assert len(test_order.transactions) == 1

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test that database transaction rolls back on error"""
        initial_status = test_order.status

        # Create invalid webhook data (missing required fields)
        webhook_data = {
            "id": "wompi-error-test",
            # Missing reference - should cause error
            "status": "APPROVED"
        }

        # Process webhook (should fail)
        result = await update_order_from_webhook(
            db=db_session,
            transaction_data=webhook_data,
            wompi_transaction_id="wompi-error-test"
        )

        assert result.success is False

        # Order status should not change
        await db_session.refresh(test_order)
        assert test_order.status == initial_status

        # No transaction should be created
        assert len(test_order.transactions) == 0


# ===== DATA INTEGRITY TESTS =====

class TestDataIntegrity:
    """Test data integrity and consistency across payment flow"""

    @pytest.mark.asyncio
    async def test_payment_amount_consistency(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test amount consistency between order and transaction"""
        # Create transaction
        transaction = OrderTransaction(
            transaction_reference=f"TXN-{test_order.order_number}",
            order_id=test_order.id,
            amount=test_order.total_amount,
            currency="COP",
            status=PaymentStatus.APPROVED,
            payment_method_type="CARD",
            gateway="wompi",
            gateway_transaction_id="wompi-amount-test",
            processed_at=datetime.utcnow()
        )
        db_session.add(transaction)
        await db_session.commit()

        # Validate amounts match
        assert transaction.amount == test_order.total_amount

        # Validate in cents conversion
        amount_in_cents = int(Decimal(str(transaction.amount)) * 100)
        assert amount_in_cents == 12900000

    @pytest.mark.asyncio
    async def test_order_status_transitions(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test valid order status transitions"""
        # PENDING → CONFIRMED
        assert test_order.status == OrderStatus.PENDING

        test_order.status = OrderStatus.CONFIRMED
        test_order.confirmed_at = datetime.utcnow()
        await db_session.commit()

        assert test_order.status == OrderStatus.CONFIRMED
        assert test_order.confirmed_at is not None

        # CONFIRMED → PROCESSING
        test_order.status = OrderStatus.PROCESSING
        await db_session.commit()

        assert test_order.status == OrderStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_webhook_audit_trail(
        self,
        db_session: AsyncSession,
        test_order: Order,
        wompi_webhook_payload: Dict[str, Any]
    ):
        """Test webhook events are properly logged for audit"""
        wompi_webhook_payload["data"]["reference"] = test_order.order_number
        transaction_id = wompi_webhook_payload["data"]["id"]

        # Create webhook event
        webhook_event = WebhookEvent(
            event_id=transaction_id,
            event_type=WebhookEventType.TRANSACTION_UPDATED,
            event_status=WebhookEventStatus.PROCESSED,
            raw_payload=wompi_webhook_payload,
            signature="test-signature",
            signature_validated=True,
            processed_at=datetime.utcnow(),
            processing_attempts=1,
            gateway_timestamp=datetime.utcnow()
        )
        db_session.add(webhook_event)
        await db_session.commit()

        # Verify audit trail
        result = await db_session.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == transaction_id)
        )
        stored_event = result.scalar_one()

        assert stored_event.event_type == WebhookEventType.TRANSACTION_UPDATED
        assert stored_event.event_status == WebhookEventStatus.PROCESSED
        assert stored_event.signature_validated is True
        assert stored_event.raw_payload == wompi_webhook_payload


# ===== PERFORMANCE TESTS =====

class TestPaymentPerformance:
    """Test performance characteristics of payment integration"""

    @pytest.mark.asyncio
    async def test_webhook_processing_performance(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test webhook processing completes within acceptable time"""
        import time

        webhook_data = {
            "id": "wompi-perf-test",
            "reference": test_order.order_number,
            "status": "APPROVED",
            "amount_in_cents": 12900000,
            "payment_method_type": "CARD"
        }

        start_time = time.time()
        result = await update_order_from_webhook(
            db=db_session,
            transaction_data=webhook_data,
            wompi_transaction_id="wompi-perf-test"
        )
        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # ms

        assert result.success is True
        # Webhook should process in under 500ms
        assert processing_time < 500

    @pytest.mark.asyncio
    async def test_bulk_transaction_creation(
        self,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test creating multiple transactions efficiently"""
        import time

        start_time = time.time()

        # Create 10 transactions
        transactions = []
        for i in range(10):
            transaction = OrderTransaction(
                transaction_reference=f"TXN-BULK-{i}",
                order_id=test_order.id,
                amount=test_order.total_amount,
                currency="COP",
                status=PaymentStatus.PENDING,
                payment_method_type="CARD",
                gateway="wompi",
                gateway_transaction_id=f"wompi-bulk-{i}",
                created_at=datetime.utcnow()
            )
            transactions.append(transaction)

        db_session.add_all(transactions)
        await db_session.commit()

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # ms

        # Should complete in under 1 second
        assert processing_time < 1000

        # Verify all created
        result = await db_session.execute(
            select(OrderTransaction).where(OrderTransaction.order_id == test_order.id)
        )
        all_transactions = result.scalars().all()
        assert len(all_transactions) == 10
