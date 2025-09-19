import pytest
import asyncio
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock, Mock

from app.main import app
from app.database import get_db, Base
from app.models.user import User, UserType
from app.models.order import Order, OrderStatus, Transaction, PaymentStatus
from app.models.payment import Payment, PaymentIntent, WebhookEvent
from app.services.payments.payment_processor import PaymentProcessor
from app.services.payments.webhook_handler import WebhookHandler
from app.core.security import create_access_token


class TestPaymentFlowIntegration:
    """Integration tests for complete payment flow"""

    @pytest.fixture(scope="function")
    async def async_db_session(self):
        """Create async database session for testing"""
        # Use in-memory SQLite for testing
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            yield session

        await engine.dispose()

    @pytest.fixture
    async def test_user(self, async_db_session):
        """Create test user"""
        user = User(
            email="buyer@test.com",
            full_name="Test Buyer",
            hashed_password="hashed_password",
            user_type=UserType.BUYER,
            telefono="1234567890",
            is_active=True
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_order(self, async_db_session, test_user):
        """Create test order"""
        order = Order(
            order_number="ORD-TEST-001",
            buyer_id=test_user.id,
            total_amount=100.0,
            status=OrderStatus.PENDING,
            items=[]
        )
        async_db_session.add(order)
        await async_db_session.commit()
        await async_db_session.refresh(order)
        return order

    @pytest.fixture
    def access_token(self, test_user):
        """Create access token for test user"""
        return create_access_token(data={"sub": test_user.email})

    @pytest.fixture
    def auth_headers(self, access_token):
        """Create authorization headers"""
        return {"Authorization": f"Bearer {access_token}"}

    @pytest.fixture
    def mock_wompi_responses(self):
        """Mock successful Wompi API responses"""
        return {
            "acceptance_token": {
                "data": {
                    "presigned_acceptance": {
                        "acceptance_token": "test_acceptance_token",
                        "permalink": "https://test.com/terms"
                    }
                }
            },
            "tokenize_card": {
                "data": {
                    "id": "tok_test_12345",
                    "status": "AVAILABLE"
                }
            },
            "payment_source": {
                "data": {
                    "id": 67890,
                    "status": "AVAILABLE",
                    "redirect_url": "https://banco.com/pse"
                }
            },
            "transaction": {
                "data": {
                    "id": "trx_test_12345",
                    "status": "PENDING",
                    "amount_in_cents": 10000,
                    "currency": "COP",
                    "payment_link_url": "https://checkout.wompi.co/p/trx_test_12345",
                    "payment_method": {"type": "CARD"}
                }
            },
            "pse_banks": {
                "data": [
                    {
                        "financial_institution_code": "1001",
                        "financial_institution_name": "Banco de Prueba"
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_complete_card_payment_flow(self, async_db_session, test_user, test_order, mock_wompi_responses):
        """Test complete card payment flow"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                # Configure mock Wompi service
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = mock_wompi_responses["acceptance_token"]
                mock_instance.tokenize_card.return_value = mock_wompi_responses["tokenize_card"]
                mock_instance.create_payment_source.return_value = mock_wompi_responses["payment_source"]
                mock_instance.create_transaction.return_value = mock_wompi_responses["transaction"]
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.return_value = "ORDER_1_20231201120000"
                mock_wompi.return_value = mock_instance

                # 1. Create payment intent
                processor = PaymentProcessor(async_db_session)
                payment_intent = await processor.create_payment_intent(
                    order_id=test_order.id,
                    customer_email=test_user.email,
                    redirect_url="https://test.com/return"
                )

                assert payment_intent.order_id == test_order.id
                assert payment_intent.amount_in_cents == 10000

                # 2. Process card payment
                card_data = {
                    "number": "4111111111111111",
                    "exp_month": "12",
                    "exp_year": "2025",
                    "cvc": "123",
                    "card_holder": "Test User"
                }

                customer_data = {
                    "email": test_user.email,
                    "full_name": test_user.full_name,
                    "phone": test_user.telefono,
                    "redirect_url": "https://test.com/return"
                }

                payment_result = await processor.process_card_payment(
                    order_id=test_order.id,
                    card_data=card_data,
                    customer_data=customer_data
                )

                assert payment_result["wompi_transaction_id"] == "trx_test_12345"
                assert payment_result["status"] == "PENDING"

                # 3. Simulate webhook for payment approval
                webhook_handler = WebhookHandler(async_db_session)
                webhook_payload = {
                    "id": "evt_test_12345",
                    "event": "transaction.updated",
                    "timestamp": int(datetime.utcnow().timestamp()),
                    "data": {
                        "id": "trx_test_12345",
                        "status": "APPROVED",
                        "amount_in_cents": 10000,
                        "reference": "ORDER_1_20231201120000"
                    }
                }

                # Mock webhook signature validation
                with patch.object(webhook_handler.wompi, 'validate_webhook_signature', return_value=True):
                    webhook_result = await webhook_handler.process_webhook(
                        json.dumps(webhook_payload),
                        "test_signature",
                        webhook_payload
                    )

                assert webhook_result["processed"] is True

                # 4. Verify final state
                # Check transaction status
                await async_db_session.refresh(test_order)
                assert test_order.status == OrderStatus.CONFIRMED

                # Check payment status
                payment_status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert payment_status["status"] == "approved"

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_complete_pse_payment_flow(self, async_db_session, test_user, test_order, mock_wompi_responses):
        """Test complete PSE payment flow"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                # Configure mock Wompi service
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = mock_wompi_responses["acceptance_token"]
                mock_instance.create_payment_source.return_value = mock_wompi_responses["payment_source"]
                mock_instance.create_transaction.return_value = mock_wompi_responses["transaction"]
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.return_value = "ORDER_1_20231201120000"
                mock_wompi.return_value = mock_instance

                # Process PSE payment
                processor = PaymentProcessor(async_db_session)
                pse_data = {
                    "user_type": "0",
                    "user_legal_id": "12345678",
                    "bank_code": "1001"
                }

                customer_data = {
                    "email": test_user.email,
                    "full_name": test_user.full_name,
                    "redirect_url": "https://test.com/return"
                }

                payment_result = await processor.process_pse_payment(
                    order_id=test_order.id,
                    pse_data=pse_data,
                    customer_data=customer_data
                )

                assert payment_result["wompi_transaction_id"] == "trx_test_12345"
                assert payment_result["status"] == "PENDING"
                assert "pse_redirect_url" in payment_result

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_payment_failure_flow(self, async_db_session, test_user, test_order):
        """Test payment failure handling"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                # Configure mock Wompi service for failure
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = {
                    "data": {"presigned_acceptance": {"acceptance_token": "test_token"}}
                }
                mock_instance.tokenize_card.return_value = {"data": {"id": "tok_test"}}
                mock_instance.create_payment_source.return_value = {"data": {"id": 123}}
                mock_instance.create_transaction.return_value = {
                    "data": {
                        "id": "trx_test_12345",
                        "status": "DECLINED",
                        "payment_method": {"type": "CARD"}
                    }
                }
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.return_value = "ORDER_1_20231201120000"
                mock_wompi.return_value = mock_instance

                processor = PaymentProcessor(async_db_session)
                card_data = {"number": "4111111111111111"}
                customer_data = {"email": test_user.email}

                payment_result = await processor.process_card_payment(
                    order_id=test_order.id,
                    card_data=card_data,
                    customer_data=customer_data
                )

                assert payment_result["status"] == "DECLINED"

                # Simulate webhook for failure
                webhook_handler = WebhookHandler(async_db_session)
                webhook_payload = {
                    "id": "evt_test_failure",
                    "event": "transaction.updated",
                    "data": {
                        "id": "trx_test_12345",
                        "status": "DECLINED",
                        "status_message": "Insufficient funds",
                        "reference": "ORDER_1_20231201120000"
                    }
                }

                with patch.object(webhook_handler.wompi, 'validate_webhook_signature', return_value=True):
                    webhook_result = await webhook_handler.process_webhook(
                        json.dumps(webhook_payload),
                        "test_signature",
                        webhook_payload
                    )

                assert webhook_result["processed"] is True

                # Verify payment status
                payment_status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert payment_status["status"] == "declined"

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_payment_cancellation_flow(self, async_db_session, test_user, test_order):
        """Test payment cancellation flow"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                # Configure mock Wompi service
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = {
                    "data": {"presigned_acceptance": {"acceptance_token": "test_token"}}
                }
                mock_instance.tokenize_card.return_value = {"data": {"id": "tok_test"}}
                mock_instance.create_payment_source.return_value = {"data": {"id": 123}}
                mock_instance.create_transaction.return_value = {
                    "data": {
                        "id": "trx_test_12345",
                        "status": "PENDING",
                        "payment_method": {"type": "CARD"}
                    }
                }
                mock_instance.void_transaction.return_value = {
                    "data": {"status": "VOIDED"}
                }
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.return_value = "ORDER_1_20231201120000"
                mock_wompi.return_value = mock_instance

                processor = PaymentProcessor(async_db_session)

                # Create payment
                card_data = {"number": "4111111111111111"}
                customer_data = {"email": test_user.email}

                payment_result = await processor.process_card_payment(
                    order_id=test_order.id,
                    card_data=card_data,
                    customer_data=customer_data
                )

                transaction_id = payment_result["transaction_id"]

                # Cancel payment
                cancellation_result = await processor.cancel_payment(transaction_id)
                assert cancellation_result is True

                # Verify transaction status
                payment_status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert payment_status["status"] == "cancelled"

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_webhook_retry_mechanism(self, async_db_session, test_user, test_order):
        """Test webhook retry mechanism for failed events"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            # Create a failed webhook event manually
            webhook_event = WebhookEvent(
                event_id="evt_test_failed",
                event_type="transaction.updated",
                event_status="failed",
                raw_payload={
                    "event": "transaction.updated",
                    "data": {"id": "trx_test_12345", "status": "APPROVED"}
                },
                signature="test_signature",
                signature_validated=True,
                processing_attempts=1,
                processing_error="Network timeout"
            )

            async_db_session.add(webhook_event)
            await async_db_session.commit()

            # Retry failed webhooks
            webhook_handler = WebhookHandler(async_db_session)

            with patch.object(webhook_handler, '_process_event') as mock_process:
                mock_process.return_value = {"processed": True, "message": "Success"}

                result = await webhook_handler.retry_failed_webhooks(limit=10)

                assert result["total_events"] == 1
                assert result["processed_successfully"] == 1

                # Verify webhook event status updated
                await async_db_session.refresh(webhook_event)
                assert webhook_event.event_status.value == "processed"
                assert webhook_event.processing_attempts == 2

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(self, async_db_session, test_user, test_order):
        """Test concurrent payment processing doesn't cause issues"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                # Configure mock Wompi service
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = {
                    "data": {"presigned_acceptance": {"acceptance_token": "test_token"}}
                }
                mock_instance.tokenize_card.return_value = {"data": {"id": "tok_test"}}
                mock_instance.create_payment_source.return_value = {"data": {"id": 123}}
                mock_instance.create_transaction.side_effect = [
                    {"data": {"id": "trx_test_1", "status": "PENDING", "payment_method": {}}},
                    {"data": {"id": "trx_test_2", "status": "PENDING", "payment_method": {}}}
                ]
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.side_effect = [
                    "ORDER_1_20231201120000",
                    "ORDER_1_20231201120001"
                ]
                mock_wompi.return_value = mock_instance

                processor = PaymentProcessor(async_db_session)

                # Try to process the same order concurrently
                async def process_payment(suffix):
                    card_data = {"number": "4111111111111111"}
                    customer_data = {"email": f"test{suffix}@example.com"}
                    return await processor.process_card_payment(
                        order_id=test_order.id,
                        card_data=card_data,
                        customer_data=customer_data
                    )

                # Run concurrent payments
                results = await asyncio.gather(
                    process_payment("1"),
                    process_payment("2"),
                    return_exceptions=True
                )

                # At least one should succeed (depending on business logic)
                successful_results = [r for r in results if not isinstance(r, Exception)]
                assert len(successful_results) >= 1

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_payment_status_tracking(self, async_db_session, test_user, test_order, mock_wompi_responses):
        """Test payment status tracking through complete lifecycle"""
        # Override database dependency
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
                mock_instance = AsyncMock()
                mock_instance.get_acceptance_token.return_value = mock_wompi_responses["acceptance_token"]
                mock_instance.tokenize_card.return_value = mock_wompi_responses["tokenize_card"]
                mock_instance.create_payment_source.return_value = mock_wompi_responses["payment_source"]
                mock_instance.create_transaction.return_value = mock_wompi_responses["transaction"]
                mock_instance.amount_to_cents.return_value = 10000
                mock_instance.generate_reference.return_value = "ORDER_1_20231201120000"
                mock_wompi.return_value = mock_instance

                processor = PaymentProcessor(async_db_session)

                # 1. Initial payment processing
                card_data = {"number": "4111111111111111"}
                customer_data = {"email": test_user.email}

                payment_result = await processor.process_card_payment(
                    order_id=test_order.id,
                    card_data=card_data,
                    customer_data=customer_data
                )

                # Check initial status
                status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert status["status"] == "processing"

                # 2. Simulate processing webhook
                webhook_handler = WebhookHandler(async_db_session)
                processing_payload = {
                    "id": "evt_processing",
                    "event": "transaction.updated",
                    "data": {
                        "id": "trx_test_12345",
                        "status": "PENDING",
                        "reference": "ORDER_1_20231201120000"
                    }
                }

                with patch.object(webhook_handler.wompi, 'validate_webhook_signature', return_value=True):
                    await webhook_handler.process_webhook(
                        json.dumps(processing_payload),
                        "test_signature",
                        processing_payload
                    )

                # Check processing status
                status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert status["status"] == "pending"

                # 3. Simulate approval webhook
                approval_payload = {
                    "id": "evt_approval",
                    "event": "transaction.updated",
                    "data": {
                        "id": "trx_test_12345",
                        "status": "APPROVED",
                        "reference": "ORDER_1_20231201120000"
                    }
                }

                with patch.object(webhook_handler.wompi, 'validate_webhook_signature', return_value=True):
                    await webhook_handler.process_webhook(
                        json.dumps(approval_payload),
                        "test_signature",
                        approval_payload
                    )

                # Check final approved status
                status = await processor.get_payment_status("ORDER_1_20231201120000")
                assert status["status"] == "approved"

                # Verify order status updated
                await async_db_session.refresh(test_order)
                assert test_order.status == OrderStatus.CONFIRMED

        finally:
            app.dependency_overrides.clear()


class TestPaymentAPIIntegration:
    """Integration tests for payment API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_dependency(self, async_db_session):
        """Mock database dependency"""
        async def override_get_db():
            yield async_db_session

        app.dependency_overrides[get_db] = override_get_db
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_payment_methods_endpoint(self, client, mock_db_dependency):
        """Test payment methods API endpoint"""
        with patch('app.services.payments.wompi_service.WompiService') as mock_wompi:
            mock_instance = AsyncMock()
            mock_instance.config.public_key = "pub_test_12345"
            mock_wompi.return_value = mock_instance

            with patch('app.services.payments.payment_processor.PaymentProcessor') as mock_processor:
                mock_proc_instance = AsyncMock()
                mock_proc_instance.get_pse_banks.return_value = [
                    {
                        "financial_institution_code": "1001",
                        "financial_institution_name": "Banco de Prueba"
                    }
                ]
                mock_processor.return_value = mock_proc_instance

                response = client.get("/api/v1/payments/methods")

                assert response.status_code == 200
                data = response.json()
                assert data["card_enabled"] is True
                assert data["pse_enabled"] is True
                assert len(data["pse_banks"]) == 1
                assert data["wompi_public_key"] == "pub_test_12345"

    def test_webhook_endpoint_invalid_signature(self, client, mock_db_dependency):
        """Test webhook endpoint with invalid signature"""
        payload = {
            "event": "transaction.updated",
            "data": {"id": "trx_test", "status": "APPROVED"}
        }

        response = client.post(
            "/api/v1/payments/webhook",
            json=payload
        )

        assert response.status_code == 400
        assert "Missing signature" in response.json()["detail"]

    def test_webhook_endpoint_invalid_json(self, client, mock_db_dependency):
        """Test webhook endpoint with invalid JSON"""
        response = client.post(
            "/api/v1/payments/webhook",
            data="invalid json",
            headers={
                "X-Signature": "test_signature",
                "Content-Type": "application/json"
            }
        )

        assert response.status_code == 400
        assert "Invalid JSON payload" in response.json()["detail"]