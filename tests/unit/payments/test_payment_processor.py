import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payments.payment_processor import PaymentProcessor
from app.models.order import Order, Transaction, PaymentStatus, OrderStatus
from app.models.payment import Payment, PaymentIntent
from app.models.user import User


class TestPaymentProcessor:
    """Test PaymentProcessor functionality"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock(spec=AsyncSession)
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.refresh = AsyncMock()
        db.flush = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def mock_wompi_service(self):
        """Create mock Wompi service"""
        mock_service = AsyncMock()
        mock_service.amount_to_cents = Mock(return_value=10000)
        mock_service.generate_reference = Mock(return_value="ORDER_123_20231201120000")
        return mock_service

    @pytest.fixture
    def payment_processor(self, mock_db):
        """Create PaymentProcessor instance"""
        with patch('app.services.payments.payment_processor.get_wompi_service') as mock_get_service:
            mock_get_service.return_value = AsyncMock()
            processor = PaymentProcessor(mock_db)
            processor.wompi = AsyncMock()
            processor.wompi.amount_to_cents = Mock(return_value=10000)
            processor.wompi.generate_reference = Mock(return_value="ORDER_123_20231201120000")
            return processor

    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.total_amount = 100.0
        order.status = OrderStatus.PENDING
        order.order_number = "ORD-123"
        order.buyer_id = 456
        order.items = []
        return order

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing"""
        user = Mock(spec=User)
        user.id = 456
        user.email = "test@example.com"
        user.full_name = "John Doe"
        user.telefono = "1234567890"
        return user

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, payment_processor, mock_db, sample_order):
        """Test successful payment intent creation"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        result = await payment_processor.create_payment_intent(
            order_id=123,
            customer_email="test@example.com",
            redirect_url="https://example.com/return"
        )

        assert isinstance(result, PaymentIntent)
        assert result.order_id == 123
        assert result.customer_email == "test@example.com"
        assert result.amount_in_cents == 10000
        assert result.currency == "COP"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_payment_intent_order_not_found(self, payment_processor, mock_db):
        """Test payment intent creation with non-existent order"""
        # Mock database query result - no order found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Order 123 not found"):
            await payment_processor.create_payment_intent(
                order_id=123,
                customer_email="test@example.com",
                redirect_url="https://example.com/return"
            )

    @pytest.mark.asyncio
    async def test_create_payment_intent_invalid_order_status(self, payment_processor, mock_db, sample_order):
        """Test payment intent creation with invalid order status"""
        sample_order.status = OrderStatus.COMPLETED

        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Order 123 is not in a payable state"):
            await payment_processor.create_payment_intent(
                order_id=123,
                customer_email="test@example.com",
                redirect_url="https://example.com/return"
            )

    @pytest.mark.asyncio
    async def test_process_card_payment_success(self, payment_processor, mock_db, sample_order):
        """Test successful card payment processing"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        # Mock Wompi responses
        payment_processor.wompi.tokenize_card.return_value = {
            "data": {"id": "tok_test_12345"}
        }
        payment_processor.wompi.create_payment_source.return_value = {
            "data": {"id": 67890}
        }
        payment_processor.wompi.create_transaction.return_value = {
            "data": {
                "id": "trx_test_12345",
                "status": "PENDING",
                "payment_link_url": "https://checkout.wompi.co/p/trx_test_12345",
                "payment_method": {"type": "CARD"}
            }
        }

        card_data = {
            "number": "4111111111111111",
            "exp_month": "12",
            "exp_year": "2025",
            "cvc": "123",
            "card_holder": "John Doe",
            "installments": 1
        }

        customer_data = {
            "email": "test@example.com",
            "full_name": "John Doe",
            "phone": "1234567890",
            "redirect_url": "https://example.com/return"
        }

        result = await payment_processor.process_card_payment(
            order_id=123,
            card_data=card_data,
            customer_data=customer_data
        )

        assert result["transaction_id"] is not None
        assert result["wompi_transaction_id"] == "trx_test_12345"
        assert result["status"] == "PENDING"
        assert result["checkout_url"] == "https://checkout.wompi.co/p/trx_test_12345"
        assert result["reference"] == "ORDER_123_20231201120000"

        # Verify Wompi service calls
        payment_processor.wompi.tokenize_card.assert_called_once_with(card_data)
        payment_processor.wompi.create_payment_source.assert_called_once()
        payment_processor.wompi.create_transaction.assert_called_once()

        # Verify database operations
        assert mock_db.add.call_count == 2  # Transaction and Payment
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_card_payment_order_not_found(self, payment_processor, mock_db):
        """Test card payment processing with non-existent order"""
        # Mock database query result - no order found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        card_data = {"number": "4111111111111111"}
        customer_data = {"email": "test@example.com"}

        with pytest.raises(ValueError, match="Order 123 not found"):
            await payment_processor.process_card_payment(
                order_id=123,
                card_data=card_data,
                customer_data=customer_data
            )

    @pytest.mark.asyncio
    async def test_process_card_payment_tokenization_failure(self, payment_processor, mock_db, sample_order):
        """Test card payment processing with tokenization failure"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        # Mock Wompi tokenization failure
        payment_processor.wompi.tokenize_card.side_effect = Exception("Card tokenization failed")

        card_data = {"number": "4111111111111111"}
        customer_data = {"email": "test@example.com"}

        with pytest.raises(Exception):
            await payment_processor.process_card_payment(
                order_id=123,
                card_data=card_data,
                customer_data=customer_data
            )

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pse_payment_success(self, payment_processor, mock_db, sample_order):
        """Test successful PSE payment processing"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        # Mock Wompi responses
        payment_processor.wompi.create_payment_source.return_value = {
            "data": {
                "id": 67890,
                "redirect_url": "https://banco.com/pse"
            }
        }
        payment_processor.wompi.create_transaction.return_value = {
            "data": {
                "id": "trx_test_12345",
                "status": "PENDING",
                "payment_link_url": "https://checkout.wompi.co/p/trx_test_12345",
                "payment_method": {"type": "PSE"}
            }
        }

        pse_data = {
            "user_type": "0",
            "user_legal_id": "12345678",
            "bank_code": "1001"
        }

        customer_data = {
            "email": "test@example.com",
            "full_name": "John Doe",
            "redirect_url": "https://example.com/return"
        }

        result = await payment_processor.process_pse_payment(
            order_id=123,
            pse_data=pse_data,
            customer_data=customer_data
        )

        assert result["transaction_id"] is not None
        assert result["wompi_transaction_id"] == "trx_test_12345"
        assert result["status"] == "PENDING"
        assert result["pse_redirect_url"] == "https://banco.com/pse"
        assert result["reference"] == "ORDER_123_20231201120000"

        # Verify Wompi service calls
        payment_processor.wompi.create_payment_source.assert_called_once()
        payment_processor.wompi.create_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_transaction_status_approved(self, payment_processor, mock_db):
        """Test updating transaction status to approved"""
        # Mock transaction and order
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.order = Mock()
        mock_transaction.order.status = OrderStatus.PENDING

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        wompi_data = {
            "id": "trx_test_12345",
            "status": "APPROVED",
            "amount_in_cents": 10000
        }

        result = await payment_processor.update_transaction_status(
            transaction_id=123,
            status="APPROVED",
            wompi_data=wompi_data
        )

        assert mock_transaction.status == PaymentStatus.APPROVED
        assert mock_transaction.order.status == OrderStatus.CONFIRMED
        assert mock_transaction.confirmed_at is not None
        assert mock_transaction.order.confirmed_at is not None
        assert mock_transaction.gateway_response == wompi_data

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_transaction)

    @pytest.mark.asyncio
    async def test_update_transaction_status_declined(self, payment_processor, mock_db):
        """Test updating transaction status to declined"""
        # Mock transaction
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.order = Mock()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        wompi_data = {
            "status": "DECLINED",
            "status_message": "Insufficient funds",
            "error": {"type": "PAYMENT_DECLINED"}
        }

        result = await payment_processor.update_transaction_status(
            transaction_id=123,
            status="DECLINED",
            wompi_data=wompi_data
        )

        assert mock_transaction.status == PaymentStatus.DECLINED
        assert mock_transaction.failure_reason == "Insufficient funds"
        assert mock_transaction.failure_code == "PAYMENT_DECLINED"

    @pytest.mark.asyncio
    async def test_update_transaction_status_not_found(self, payment_processor, mock_db):
        """Test updating transaction status for non-existent transaction"""
        # Mock database query result - no transaction found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Transaction 123 not found"):
            await payment_processor.update_transaction_status(
                transaction_id=123,
                status="APPROVED"
            )

    @pytest.mark.asyncio
    async def test_get_payment_status_success(self, payment_processor, mock_db):
        """Test getting payment status successfully"""
        # Mock transaction with order
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.transaction_reference = "ORDER_123_20231201120000"
        mock_transaction.status = PaymentStatus.APPROVED
        mock_transaction.amount = 100.0
        mock_transaction.currency = "COP"
        mock_transaction.gateway_transaction_id = "trx_test_12345"
        mock_transaction.created_at = datetime.utcnow()
        mock_transaction.processed_at = datetime.utcnow()
        mock_transaction.confirmed_at = datetime.utcnow()
        mock_transaction.failure_reason = None

        mock_transaction.order = Mock()
        mock_transaction.order.order_number = "ORD-123"

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        result = await payment_processor.get_payment_status("ORDER_123_20231201120000")

        assert result["transaction_id"] == 123
        assert result["reference"] == "ORDER_123_20231201120000"
        assert result["status"] == "approved"
        assert result["amount"] == 100.0
        assert result["currency"] == "COP"
        assert result["order_number"] == "ORD-123"
        assert result["gateway_transaction_id"] == "trx_test_12345"

    @pytest.mark.asyncio
    async def test_get_payment_status_not_found(self, payment_processor, mock_db):
        """Test getting payment status for non-existent transaction"""
        # Mock database query result - no transaction found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Transaction ORDER_123_20231201120000 not found"):
            await payment_processor.get_payment_status("ORDER_123_20231201120000")

    @pytest.mark.asyncio
    async def test_get_pse_banks(self, payment_processor):
        """Test getting PSE banks"""
        expected_banks = [
            {
                "financial_institution_code": "1001",
                "financial_institution_name": "Banco de Prueba"
            }
        ]

        payment_processor.wompi.get_pse_banks.return_value = expected_banks

        result = await payment_processor.get_pse_banks()

        assert result == expected_banks
        payment_processor.wompi.get_pse_banks.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_payment_success(self, payment_processor, mock_db):
        """Test successful payment cancellation"""
        # Mock transaction
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.gateway_transaction_id = "trx_test_12345"
        mock_transaction.status = PaymentStatus.PENDING

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        # Mock Wompi void response
        payment_processor.wompi.void_transaction.return_value = {
            "data": {"status": "VOIDED"}
        }

        result = await payment_processor.cancel_payment(123)

        assert result is True
        assert mock_transaction.status == PaymentStatus.CANCELLED
        payment_processor.wompi.void_transaction.assert_called_once_with("trx_test_12345")
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_payment_transaction_not_found(self, payment_processor, mock_db):
        """Test payment cancellation for non-existent transaction"""
        # Mock database query result - no transaction found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await payment_processor.cancel_payment(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_payment_no_gateway_id(self, payment_processor, mock_db):
        """Test payment cancellation for transaction without gateway ID"""
        # Mock transaction without gateway ID
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.gateway_transaction_id = None

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        result = await payment_processor.cancel_payment(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_payment_invalid_status(self, payment_processor, mock_db):
        """Test payment cancellation for transaction with invalid status"""
        # Mock transaction with completed status
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.gateway_transaction_id = "trx_test_12345"
        mock_transaction.status = PaymentStatus.APPROVED

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        result = await payment_processor.cancel_payment(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_payment_void_failed(self, payment_processor, mock_db):
        """Test payment cancellation when void fails"""
        # Mock transaction
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.gateway_transaction_id = "trx_test_12345"
        mock_transaction.status = PaymentStatus.PENDING

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        # Mock Wompi void response - not voided
        payment_processor.wompi.void_transaction.return_value = {
            "data": {"status": "FAILED"}
        }

        result = await payment_processor.cancel_payment(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_payment_exception_handling(self, payment_processor, mock_db):
        """Test payment cancellation with exception"""
        # Mock transaction
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = 123
        mock_transaction.gateway_transaction_id = "trx_test_12345"
        mock_transaction.status = PaymentStatus.PENDING

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_db.execute.return_value = mock_result

        # Mock Wompi void exception
        payment_processor.wompi.void_transaction.side_effect = Exception("Network error")

        result = await payment_processor.cancel_payment(123)

        assert result is False


class TestPaymentProcessorEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    def payment_processor(self, mock_db):
        """Create PaymentProcessor instance"""
        with patch('app.services.payments.payment_processor.get_wompi_service') as mock_get_service:
            mock_get_service.return_value = AsyncMock()
            processor = PaymentProcessor(mock_db)
            processor.wompi = AsyncMock()
            return processor

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock(spec=AsyncSession)
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.refresh = AsyncMock()
        db.flush = AsyncMock()
        db.add = Mock()
        return db

    @pytest.mark.asyncio
    async def test_database_error_handling(self, payment_processor, mock_db):
        """Test handling of database errors"""
        # Mock database error
        mock_db.execute.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception):
            await payment_processor.create_payment_intent(
                order_id=123,
                customer_email="test@example.com",
                redirect_url="https://example.com/return"
            )

    @pytest.mark.asyncio
    async def test_commit_failure_rollback(self, payment_processor, mock_db, sample_order):
        """Test rollback on commit failure"""
        # Mock successful query but failed commit
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result
        mock_db.commit.side_effect = Exception("Commit failed")

        payment_processor.wompi.amount_to_cents = Mock(return_value=10000)

        with pytest.raises(Exception):
            await payment_processor.create_payment_intent(
                order_id=123,
                customer_email="test@example.com",
                redirect_url="https://example.com/return"
            )

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_wompi_service_timeout(self, payment_processor, mock_db, sample_order):
        """Test handling of Wompi service timeouts"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        # Mock Wompi timeout
        payment_processor.wompi.tokenize_card.side_effect = asyncio.TimeoutError("Request timeout")

        card_data = {"number": "4111111111111111"}
        customer_data = {"email": "test@example.com"}

        with pytest.raises(Exception):
            await payment_processor.process_card_payment(
                order_id=123,
                card_data=card_data,
                customer_data=customer_data
            )

    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(self, payment_processor, mock_db, sample_order):
        """Test handling of concurrent payment processing"""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_order
        mock_db.execute.return_value = mock_result

        # Mock successful Wompi responses
        payment_processor.wompi.tokenize_card.return_value = {"data": {"id": "tok_test"}}
        payment_processor.wompi.create_payment_source.return_value = {"data": {"id": 123}}
        payment_processor.wompi.create_transaction.return_value = {
            "data": {"id": "trx_test", "status": "PENDING", "payment_method": {}}
        }
        payment_processor.wompi.amount_to_cents = Mock(return_value=10000)
        payment_processor.wompi.generate_reference = Mock(return_value="ORDER_123_20231201120000")

        # Simulate concurrent calls
        tasks = []
        for i in range(3):
            task = payment_processor.process_card_payment(
                order_id=123,
                card_data={"number": "4111111111111111"},
                customer_data={"email": f"test{i}@example.com"}
            )
            tasks.append(task)

        # All should complete without deadlock
        results = await asyncio.gather(*tasks)
        assert len(results) == 3

    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.total_amount = 100.0
        order.status = OrderStatus.PENDING
        order.order_number = "ORD-123"
        order.buyer_id = 456
        order.items = []
        return order


# Import asyncio for timeout tests
import asyncio