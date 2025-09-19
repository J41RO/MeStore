import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payments.webhook_handler import WebhookHandler
from app.models.order import Transaction, OrderStatus
from app.models.payment import WebhookEvent, WebhookEventType, WebhookEventStatus, Payment
from app.models.order import PaymentStatus


class TestWebhookHandler:
    """Test WebhookHandler functionality"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock(spec=AsyncSession)
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.flush = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def mock_wompi_service(self):
        """Create mock Wompi service"""
        service = AsyncMock()
        service.validate_webhook_signature = Mock(return_value=True)
        return service

    @pytest.fixture
    def mock_payment_processor(self):
        """Create mock payment processor"""
        processor = AsyncMock()
        processor.update_transaction_status = AsyncMock()
        return processor

    @pytest.fixture
    def webhook_handler(self, mock_db):
        """Create WebhookHandler instance"""
        with patch('app.services.payments.webhook_handler.WompiService') as mock_wompi_class, \
             patch('app.services.payments.webhook_handler.PaymentProcessor') as mock_processor_class:

            mock_wompi_instance = AsyncMock()
            mock_wompi_instance.validate_webhook_signature = Mock(return_value=True)
            mock_wompi_class.return_value = mock_wompi_instance

            mock_processor_instance = AsyncMock()
            mock_processor_class.return_value = mock_processor_instance

            handler = WebhookHandler(mock_db)
            handler.wompi = mock_wompi_instance
            handler.payment_processor = mock_processor_instance
            return handler

    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction for testing"""
        transaction = Mock(spec=Transaction)
        transaction.id = 123
        transaction.transaction_reference = "ORDER_123_20231201120000"
        transaction.gateway_transaction_id = "trx_test_12345"
        transaction.order = Mock()
        transaction.order.id = 456
        return transaction

    @pytest.fixture
    def sample_webhook_event_data(self):
        """Create sample webhook event data"""
        return {
            "id": "evt_test_12345",
            "event": "transaction.updated",
            "timestamp": 1703184000,  # 2023-12-21 16:00:00 UTC
            "data": {
                "id": "trx_test_12345",
                "status": "APPROVED",
                "amount_in_cents": 10000,
                "currency": "COP",
                "reference": "ORDER_123_20231201120000"
            }
        }

    @pytest.mark.asyncio
    async def test_process_webhook_success(self, webhook_handler, mock_db, sample_webhook_event_data):
        """Test successful webhook processing"""
        payload = json.dumps(sample_webhook_event_data)
        signature = "valid_signature"

        # Mock no existing event
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Mock successful event processing
        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler.process_webhook(payload, signature, sample_webhook_event_data)

        assert result["processed"] is True
        assert "message" in result
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_webhook_invalid_signature(self, webhook_handler, sample_webhook_event_data):
        """Test webhook processing with invalid signature"""
        payload = json.dumps(sample_webhook_event_data)
        signature = "invalid_signature"

        # Mock invalid signature
        webhook_handler.wompi.validate_webhook_signature.return_value = False

        result = await webhook_handler.process_webhook(payload, signature, sample_webhook_event_data)

        assert result["processed"] is False
        assert result["error"] == "Invalid signature"

    @pytest.mark.asyncio
    async def test_process_webhook_duplicate_event(self, webhook_handler, mock_db, sample_webhook_event_data):
        """Test webhook processing with duplicate event"""
        payload = json.dumps(sample_webhook_event_data)
        signature = "valid_signature"

        # Mock existing event
        existing_event = Mock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_event
        mock_db.execute.return_value = mock_result

        result = await webhook_handler.process_webhook(payload, signature, sample_webhook_event_data)

        assert result["processed"] is True
        assert result["message"] == "Event already processed"

    @pytest.mark.asyncio
    async def test_map_event_type(self, webhook_handler):
        """Test event type mapping"""
        assert webhook_handler._map_event_type("transaction.updated") == WebhookEventType.TRANSACTION_UPDATED
        assert webhook_handler._map_event_type("payment.created") == WebhookEventType.PAYMENT_CREATED
        assert webhook_handler._map_event_type("payment.approved") == WebhookEventType.PAYMENT_APPROVED
        assert webhook_handler._map_event_type("payment.declined") == WebhookEventType.PAYMENT_DECLINED
        assert webhook_handler._map_event_type("unknown.event") == WebhookEventType.TRANSACTION_UPDATED

    @pytest.mark.asyncio
    async def test_handle_transaction_updated_success(self, webhook_handler, mock_db, sample_transaction):
        """Test successful transaction update handling"""
        webhook_event = Mock(spec=WebhookEvent)
        webhook_event.id = 789

        data = {
            "id": "trx_test_12345",
            "status": "APPROVED",
            "reference": "ORDER_123_20231201120000"
        }

        # Mock finding transaction by gateway ID
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock successful transaction update
        updated_transaction = Mock()
        webhook_handler.payment_processor.update_transaction_status.return_value = updated_transaction

        result = await webhook_handler._handle_transaction_updated(webhook_event, data)

        assert result["processed"] is True
        assert result["transaction_id"] == 123
        assert result["new_status"] == "APPROVED"
        assert webhook_event.transaction_id == 123

        webhook_handler.payment_processor.update_transaction_status.assert_called_once_with(
            123, "APPROVED", data
        )

    @pytest.mark.asyncio
    async def test_handle_transaction_updated_not_found(self, webhook_handler, mock_db):
        """Test transaction update handling when transaction not found"""
        webhook_event = Mock(spec=WebhookEvent)

        data = {
            "id": "trx_test_12345",
            "status": "APPROVED",
            "reference": "ORDER_123_20231201120000"
        }

        # Mock no transaction found by gateway ID or reference
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await webhook_handler._handle_transaction_updated(webhook_event, data)

        assert result["processed"] is False
        assert result["error"] == "Transaction not found"

    @pytest.mark.asyncio
    async def test_handle_transaction_updated_missing_data(self, webhook_handler, mock_db):
        """Test transaction update handling with missing data"""
        webhook_event = Mock(spec=WebhookEvent)

        # Missing transaction ID
        data = {
            "status": "APPROVED",
            "reference": "ORDER_123_20231201120000"
        }

        result = await webhook_handler._handle_transaction_updated(webhook_event, data)

        assert result["processed"] is False
        assert result["error"] == "Missing transaction ID or status"

    @pytest.mark.asyncio
    async def test_handle_transaction_updated_find_by_reference(self, webhook_handler, mock_db, sample_transaction):
        """Test transaction update handling when found by reference"""
        webhook_event = Mock(spec=WebhookEvent)

        data = {
            "id": "trx_test_12345",
            "status": "APPROVED",
            "reference": "ORDER_123_20231201120000"
        }

        # Mock not found by gateway ID, but found by reference
        mock_db.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=None)),  # First query - by gateway ID
            Mock(scalar_one_or_none=Mock(return_value=sample_transaction))  # Second query - by reference
        ]

        # Mock successful transaction update
        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_transaction_updated(webhook_event, data)

        assert result["processed"] is True
        assert result["transaction_id"] == 123

    @pytest.mark.asyncio
    async def test_handle_payment_updated_existing_payment(self, webhook_handler, mock_db):
        """Test payment update handling for existing payment"""
        webhook_event = Mock(spec=WebhookEvent)

        data = {
            "id": "pay_test_12345",
            "status": "APPROVED",
            "amount_in_cents": 10000,
            "reference": "ORDER_123_20231201120000"
        }

        # Mock existing payment
        existing_payment = Mock(spec=Payment)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_payment
        mock_db.execute.return_value = mock_result

        result = await webhook_handler._handle_payment_updated(webhook_event, data)

        assert result["processed"] is True
        assert existing_payment.status == "APPROVED"
        assert existing_payment.gateway_response == data

    @pytest.mark.asyncio
    async def test_handle_payment_updated_new_payment(self, webhook_handler, mock_db, sample_transaction):
        """Test payment update handling for new payment"""
        webhook_event = Mock(spec=WebhookEvent)

        data = {
            "id": "pay_test_12345",
            "status": "APPROVED",
            "amount_in_cents": 10000,
            "reference": "ORDER_123_20231201120000",
            "payment_method": {"type": "CARD"}
        }

        # Mock no existing payment, but found transaction
        mock_db.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=None)),  # Payment query
            Mock(scalar_one_or_none=Mock(return_value=sample_transaction))  # Transaction query
        ]

        result = await webhook_handler._handle_payment_updated(webhook_event, data)

        assert result["processed"] is True
        mock_db.add.assert_called_once()
        assert webhook_event.transaction_id == 123

    @pytest.mark.asyncio
    async def test_handle_payment_approved(self, webhook_handler, mock_db, sample_transaction):
        """Test payment approved handling"""
        webhook_event = Mock(spec=WebhookEvent)
        data = {"id": "trx_test_12345", "status": "APPROVED"}

        # Mock finding transaction
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_payment_approved(webhook_event, data)

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_handle_payment_declined(self, webhook_handler, mock_db, sample_transaction):
        """Test payment declined handling"""
        webhook_event = Mock(spec=WebhookEvent)
        data = {"id": "trx_test_12345", "status": "DECLINED"}

        # Mock finding transaction
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_payment_declined(webhook_event, data)

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_handle_payment_failed(self, webhook_handler, mock_db, sample_transaction):
        """Test payment failed handling"""
        webhook_event = Mock(spec=WebhookEvent)
        data = {"id": "trx_test_12345", "status": "ERROR"}

        # Mock finding transaction
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_payment_failed(webhook_event, data)

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_handle_payment_voided(self, webhook_handler, mock_db, sample_transaction):
        """Test payment voided handling"""
        webhook_event = Mock(spec=WebhookEvent)
        data = {"id": "trx_test_12345", "status": "VOIDED"}

        # Mock finding transaction
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_payment_voided(webhook_event, data)

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_handle_payment_refunded(self, webhook_handler, mock_db, sample_transaction):
        """Test payment refunded handling"""
        webhook_event = Mock(spec=WebhookEvent)
        data = {"id": "trx_test_12345", "status": "REFUNDED"}

        # Mock finding transaction
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        result = await webhook_handler._handle_payment_refunded(webhook_event, data)

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_process_event_unknown_type(self, webhook_handler):
        """Test processing unknown event type"""
        webhook_event = Mock(spec=WebhookEvent)
        event_type = "unknown.event"
        data = {}

        result = await webhook_handler._process_event(webhook_event, event_type, data)

        assert result["processed"] is False
        assert "Unknown event type" in result["message"]

    @pytest.mark.asyncio
    async def test_retry_failed_webhooks_success(self, webhook_handler, mock_db):
        """Test successful retry of failed webhooks"""
        # Mock failed webhook events
        failed_event1 = Mock(spec=WebhookEvent)
        failed_event1.id = 1
        failed_event1.event_type = WebhookEventType.TRANSACTION_UPDATED
        failed_event1.raw_payload = {"event": "transaction.updated", "data": {"id": "trx_1"}}
        failed_event1.processing_attempts = 1

        failed_event2 = Mock(spec=WebhookEvent)
        failed_event2.id = 2
        failed_event2.event_type = WebhookEventType.PAYMENT_APPROVED
        failed_event2.raw_payload = {"event": "payment.approved", "data": {"id": "trx_2"}}
        failed_event2.processing_attempts = 2

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [failed_event1, failed_event2]
        mock_db.execute.return_value = mock_result

        # Mock successful retry processing
        with patch.object(webhook_handler, '_process_event') as mock_process:
            mock_process.side_effect = [
                {"processed": True, "message": "Success"},
                {"processed": False, "error": "Still failed"}
            ]

            result = await webhook_handler.retry_failed_webhooks(limit=10)

            assert result["total_events"] == 2
            assert result["processed_successfully"] == 1
            assert "Retried 2 events, 1 successful" in result["message"]

            # Verify status updates
            assert failed_event1.event_status == WebhookEventStatus.PROCESSED
            assert failed_event2.event_status == WebhookEventStatus.FAILED
            assert failed_event1.processing_attempts == 2
            assert failed_event2.processing_attempts == 3

            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_failed_webhooks_exception_handling(self, webhook_handler, mock_db):
        """Test retry failed webhooks with exception handling"""
        # Mock failed webhook event
        failed_event = Mock(spec=WebhookEvent)
        failed_event.id = 1
        failed_event.event_type = WebhookEventType.TRANSACTION_UPDATED
        failed_event.raw_payload = {"event": "transaction.updated", "data": {"id": "trx_1"}}
        failed_event.processing_attempts = 1

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [failed_event]
        mock_db.execute.return_value = mock_result

        # Mock processing exception
        with patch.object(webhook_handler, '_process_event') as mock_process:
            mock_process.side_effect = Exception("Processing error")

            result = await webhook_handler.retry_failed_webhooks(limit=10)

            assert result["total_events"] == 1
            assert result["processed_successfully"] == 0
            assert failed_event.processing_attempts == 2

    @pytest.mark.asyncio
    async def test_process_webhook_exception_handling(self, webhook_handler, mock_db):
        """Test webhook processing with exception handling"""
        payload = "invalid json"
        signature = "valid_signature"
        event_data = {}

        # Mock database exception
        mock_db.execute.side_effect = Exception("Database error")

        result = await webhook_handler.process_webhook(payload, signature, event_data)

        assert result["processed"] is False
        assert "error" in result
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_event_creation_with_timestamp(self, webhook_handler, mock_db, sample_webhook_event_data):
        """Test webhook event creation with proper timestamp handling"""
        payload = json.dumps(sample_webhook_event_data)
        signature = "valid_signature"

        # Mock no existing event
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Mock successful event processing
        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        await webhook_handler.process_webhook(payload, signature, sample_webhook_event_data)

        # Verify webhook event was created with proper timestamp
        mock_db.add.assert_called_once()
        webhook_event = mock_db.add.call_args[0][0]

        assert webhook_event.event_id == "evt_test_12345"
        assert webhook_event.event_type == WebhookEventType.TRANSACTION_UPDATED
        assert webhook_event.signature_validated is True
        assert webhook_event.gateway_timestamp is not None

    @pytest.mark.asyncio
    async def test_webhook_event_without_timestamp(self, webhook_handler, mock_db):
        """Test webhook event creation without timestamp"""
        event_data = {
            "id": "evt_test_12345",
            "event": "transaction.updated",
            "data": {"id": "trx_test_12345", "status": "APPROVED"}
        }

        payload = json.dumps(event_data)
        signature = "valid_signature"

        # Mock no existing event
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Mock successful event processing
        webhook_handler.payment_processor.update_transaction_status.return_value = Mock()

        await webhook_handler.process_webhook(payload, signature, event_data)

        # Verify webhook event was created without timestamp
        webhook_event = mock_db.add.call_args[0][0]
        assert webhook_event.gateway_timestamp is None


class TestWebhookHandlerEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    def webhook_handler(self, mock_db):
        """Create WebhookHandler instance"""
        with patch('app.services.payments.webhook_handler.WompiService') as mock_wompi_class, \
             patch('app.services.payments.webhook_handler.PaymentProcessor') as mock_processor_class:

            mock_wompi_instance = AsyncMock()
            mock_wompi_class.return_value = mock_wompi_instance

            mock_processor_instance = AsyncMock()
            mock_processor_class.return_value = mock_processor_instance

            handler = WebhookHandler(mock_db)
            handler.wompi = mock_wompi_instance
            handler.payment_processor = mock_processor_instance
            return handler

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock(spec=AsyncSession)
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.flush = AsyncMock()
        db.add = Mock()
        return db

    @pytest.mark.asyncio
    async def test_malformed_event_data(self, webhook_handler, mock_db):
        """Test handling of malformed event data"""
        event_data = {
            "event": "transaction.updated"
            # Missing data field
        }

        payload = json.dumps(event_data)
        signature = "valid_signature"

        webhook_handler.wompi.validate_webhook_signature.return_value = True

        # Mock no existing event
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await webhook_handler.process_webhook(payload, signature, event_data)

        # Should still process but may fail at event handling level
        assert "error" in result or result.get("processed") is False

    @pytest.mark.asyncio
    async def test_database_constraint_violation(self, webhook_handler, mock_db):
        """Test handling of database constraint violations"""
        event_data = {
            "id": "evt_test_12345",
            "event": "transaction.updated",
            "data": {"id": "trx_test_12345", "status": "APPROVED"}
        }

        payload = json.dumps(event_data)
        signature = "valid_signature"

        webhook_handler.wompi.validate_webhook_signature.return_value = True

        # Mock constraint violation during commit
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.commit.side_effect = Exception("UNIQUE constraint failed")

        result = await webhook_handler.process_webhook(payload, signature, event_data)

        assert result["processed"] is False
        assert "error" in result
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_webhook_processing(self, webhook_handler, mock_db):
        """Test concurrent processing of the same webhook"""
        event_data = {
            "id": "evt_test_12345",
            "event": "transaction.updated",
            "data": {"id": "trx_test_12345", "status": "APPROVED"}
        }

        payload = json.dumps(event_data)
        signature = "valid_signature"

        webhook_handler.wompi.validate_webhook_signature.return_value = True

        # First call - no existing event
        # Second call - event already exists
        mock_db.execute.side_effect = [
            Mock(scalar_one_or_none=Mock(return_value=None)),
            Mock(scalar_one_or_none=Mock(return_value=Mock()))  # Existing event
        ]

        # Process the same webhook twice
        result1 = await webhook_handler.process_webhook(payload, signature, event_data)
        result2 = await webhook_handler.process_webhook(payload, signature, event_data)

        # First should process, second should detect duplicate
        assert result2["message"] == "Event already processed"
        assert result2["processed"] is True