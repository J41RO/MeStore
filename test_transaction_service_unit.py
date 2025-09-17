#!/usr/bin/env python3
# Test Transaction Service Methods - Unit Testing
# Focus: Validate all transaction service methods work independently

import pytest
import logging
from decimal import Decimal
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.services.transaction_service import TransactionService, TransactionError
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType, MetodoPago
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.user import User, UserType
from app.models.order import Order, OrderStatus

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTransactionServiceUnit:
    """Unit tests for TransactionService methods"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        session = MagicMock(spec=Session)
        session.query.return_value.filter.return_value.first.return_value = None
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.flush = Mock()
        session.refresh = Mock()
        return session

    @pytest.fixture
    def transaction_service(self, mock_session):
        """Transaction service instance with mock session"""
        return TransactionService(db_session=mock_session)

    @pytest.fixture
    def mock_commission(self):
        """Mock commission for testing"""
        commission = Mock(spec=Commission)
        commission.id = uuid4()
        commission.vendor_id = uuid4()
        commission.order_id = 123
        commission.vendor_amount = Decimal('85000.00')
        commission.commission_rate = Decimal('0.15')
        commission.commission_amount = Decimal('15000.00')
        commission.status = CommissionStatus.APPROVED
        commission.transaction_id = None
        return commission

    @pytest.fixture
    def mock_user(self):
        """Mock user for testing"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.nombre = "Test"
        user.apellido = "User"
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def mock_order(self):
        """Mock order for testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.order_number = "ORDER-123"
        order.buyer_id = uuid4()
        order.total_amount = Decimal('100000.00')
        order.status = OrderStatus.CONFIRMED
        return order

    def test_create_transaction_basic(self, transaction_service, mock_session):
        """Test basic transaction creation"""
        # Setup
        buyer_id = uuid4()
        vendor_id = uuid4()

        # Mock user queries - simplified approach
        mock_buyer = Mock(spec=User)
        mock_vendor = Mock(spec=User)

        # Create a proper query chain mock
        query_mock = Mock()
        filter_mock = Mock()

        # Setup the query chain: session.query().filter().first()
        filter_mock.first.return_value = mock_buyer  # Default to buyer, we'll override for vendor
        query_mock.filter.return_value = filter_mock
        mock_session.query.return_value = query_mock

        # Setup side effect to return appropriate user based on query
        call_count = [0]  # Use list to make it mutable in closure
        def first_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:  # First call - buyer
                return mock_buyer
            else:  # Second call - vendor
                return mock_vendor

        filter_mock.first.side_effect = first_side_effect

        # Test transaction creation
        transaction = transaction_service.create_transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.TARJETA_CREDITO,
            transaction_type=TransactionType.VENTA,
            comprador_id=buyer_id,
            vendedor_id=vendor_id,
            porcentaje_mestocker=Decimal('15.0')
        )

        # Assertions
        assert transaction is not None
        assert transaction.monto == Decimal('100000.00')
        assert transaction.metodo_pago == MetodoPago.TARJETA_CREDITO
        assert transaction.transaction_type == TransactionType.VENTA
        assert transaction.comprador_id == buyer_id
        assert transaction.vendedor_id == vendor_id
        assert transaction.estado == EstadoTransaccion.PENDIENTE

        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_transaction_validation_errors(self, transaction_service):
        """Test transaction creation validation errors"""
        buyer_id = uuid4()

        # Test negative amount
        with pytest.raises(TransactionError, match="Transaction amount must be positive"):
            transaction_service.create_transaction(
                monto=Decimal('-100.00'),
                metodo_pago=MetodoPago.TARJETA_CREDITO,
                transaction_type=TransactionType.VENTA,
                comprador_id=buyer_id
            )

        # Test zero amount
        with pytest.raises(TransactionError, match="Transaction amount must be positive"):
            transaction_service.create_transaction(
                monto=Decimal('0.00'),
                metodo_pago=MetodoPago.TARJETA_CREDITO,
                transaction_type=TransactionType.VENTA,
                comprador_id=buyer_id
            )

    def test_update_transaction_status(self, transaction_service, mock_session):
        """Test transaction status update"""
        # Setup
        transaction_id = uuid4()
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = transaction_id
        mock_transaction.estado = EstadoTransaccion.PENDIENTE
        mock_transaction.observaciones = "Initial notes"

        mock_session.query.return_value.filter.return_value.first.return_value = mock_transaction

        # Test status update
        updated_transaction = transaction_service.update_transaction_status(
            transaction_id=transaction_id,
            new_status=EstadoTransaccion.PROCESANDO,
            notes="Processing payment",
            payment_reference="PAY-123"
        )

        # Assertions
        assert updated_transaction.estado == EstadoTransaccion.PROCESANDO
        assert updated_transaction.referencia_pago == "PAY-123"
        assert "Processing payment" in updated_transaction.observaciones
        mock_session.commit.assert_called_once()

    def test_update_transaction_invalid_transition(self, transaction_service, mock_session):
        """Test invalid transaction status transitions"""
        # Setup
        transaction_id = uuid4()
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = transaction_id
        mock_transaction.estado = EstadoTransaccion.COMPLETADA  # Final state

        mock_session.query.return_value.filter.return_value.first.return_value = mock_transaction

        # Test invalid transition
        with pytest.raises(TransactionError, match="Invalid state transition"):
            transaction_service.update_transaction_status(
                transaction_id=transaction_id,
                new_status=EstadoTransaccion.PENDIENTE
            )

    def test_calculate_fees(self, transaction_service):
        """Test fee calculation"""
        base_amount = Decimal('100000.00')
        commission_rate = Decimal('0.15')  # 15%

        # Test standard transaction
        fees = transaction_service.calculate_fees(
            base_amount=base_amount,
            commission_rate=commission_rate,
            transaction_type=TransactionType.VENTA
        )

        assert fees['base_amount'] == base_amount
        assert fees['platform_fee'] == Decimal('15000.00')  # 15% of 100k
        assert fees['vendor_amount'] == Decimal('85000.00')  # 100k - 15k
        assert fees['commission_rate'] == commission_rate

        # Test commission transaction (with processing fee)
        fees_commission = transaction_service.calculate_fees(
            base_amount=base_amount,
            commission_rate=commission_rate,
            transaction_type=TransactionType.COMISION
        )

        assert fees_commission['processing_fee'] == Decimal('100.00')  # 0.1% of 100k

        # Test refund transaction (no platform fee)
        fees_refund = transaction_service.calculate_fees(
            base_amount=base_amount,
            commission_rate=commission_rate,
            transaction_type=TransactionType.DEVOLUCION
        )

        assert fees_refund['platform_fee'] == Decimal('0')
        assert fees_refund['vendor_amount'] == base_amount

    def test_calculate_fees_validation(self, transaction_service):
        """Test fee calculation validation"""
        # Test negative amount
        with pytest.raises(TransactionError, match="Base amount must be positive"):
            transaction_service.calculate_fees(
                base_amount=Decimal('-100.00'),
                commission_rate=Decimal('0.15')
            )

        # Test invalid commission rate
        with pytest.raises(TransactionError, match="Commission rate must be between 0 and 1"):
            transaction_service.calculate_fees(
                base_amount=Decimal('100000.00'),
                commission_rate=Decimal('1.5')  # 150% - invalid
            )

    def test_process_refund(self, transaction_service, mock_session):
        """Test refund processing"""
        # Setup
        original_tx_id = uuid4()
        mock_original_tx = Mock(spec=Transaction)
        mock_original_tx.id = original_tx_id
        mock_original_tx.monto = Decimal('100000.00')
        mock_original_tx.estado = EstadoTransaccion.COMPLETADA
        mock_original_tx.metodo_pago = MetodoPago.TARJETA_CREDITO
        mock_original_tx.comprador_id = uuid4()
        mock_original_tx.vendedor_id = uuid4()
        mock_original_tx.referencia_externa = "TXN-ORIGINAL"
        mock_original_tx.inventory_id = None

        mock_session.query.return_value.filter.return_value.first.return_value = mock_original_tx

        # Test full refund
        refund_tx = transaction_service.process_refund(
            original_transaction_id=original_tx_id,
            reason="Customer request"
        )

        # Assertions
        assert refund_tx.monto == Decimal('100000.00')  # Full amount
        assert refund_tx.transaction_type == TransactionType.DEVOLUCION
        assert refund_tx.porcentaje_mestocker == 0.0  # No commission on refunds
        assert refund_tx.estado == EstadoTransaccion.COMPLETADA
        assert "Customer request" in refund_tx.observaciones

        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_process_partial_refund(self, transaction_service, mock_session):
        """Test partial refund processing"""
        # Setup
        original_tx_id = uuid4()
        mock_original_tx = Mock(spec=Transaction)
        mock_original_tx.id = original_tx_id
        mock_original_tx.monto = Decimal('100000.00')
        mock_original_tx.estado = EstadoTransaccion.COMPLETADA
        mock_original_tx.metodo_pago = MetodoPago.TARJETA_CREDITO
        mock_original_tx.comprador_id = uuid4()
        mock_original_tx.vendedor_id = uuid4()
        mock_original_tx.referencia_externa = "TXN-ORIGINAL"
        mock_original_tx.inventory_id = None

        mock_session.query.return_value.filter.return_value.first.return_value = mock_original_tx

        # Test partial refund
        partial_amount = Decimal('30000.00')
        refund_tx = transaction_service.process_refund(
            original_transaction_id=original_tx_id,
            refund_amount=partial_amount,
            reason="Partial return"
        )

        # Assertions
        assert refund_tx.monto == partial_amount
        assert refund_tx.transaction_type == TransactionType.DEVOLUCION

    def test_process_refund_validation(self, transaction_service, mock_session):
        """Test refund validation errors"""
        # Test non-existent transaction
        non_existent_id = uuid4()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(TransactionError, match="Original transaction .* not found"):
            transaction_service.process_refund(original_transaction_id=non_existent_id)

        # Test transaction not completed
        pending_tx = Mock(spec=Transaction)
        pending_tx.estado = EstadoTransaccion.PENDIENTE
        mock_session.query.return_value.filter.return_value.first.return_value = pending_tx

        with pytest.raises(TransactionError, match="Original transaction must be completed"):
            transaction_service.process_refund(original_transaction_id=uuid4())

    def test_get_transaction_history(self, transaction_service, mock_session):
        """Test transaction history retrieval"""
        user_id = uuid4()

        # Mock query chain
        mock_transactions = [Mock(spec=Transaction) for _ in range(3)]
        for i, tx in enumerate(mock_transactions):
            tx.to_dict.return_value = {'id': str(uuid4()), 'amount': float(1000 * (i+1))}
            tx.estado = EstadoTransaccion.COMPLETADA
            tx.monto = Decimal(str(1000 * (i+1)))
            tx.transaction_type = TransactionType.VENTA
            tx.metodo_pago = MetodoPago.TARJETA_CREDITO

        # Setup query chain mocking
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 3
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = mock_transactions

        mock_session.query.return_value = query_mock

        # Test transaction history
        result = transaction_service.get_transaction_history(
            user_id=user_id,
            limit=10,
            offset=0
        )

        # Assertions
        assert 'transactions' in result
        assert 'pagination' in result
        assert 'summary' in result
        assert result['pagination']['total'] == 3
        assert len(result['transactions']) == 3

    @patch('app.services.transaction_service.logger')
    def test_transaction_logging(self, mock_logger, transaction_service, mock_session):
        """Test transaction logging"""
        buyer_id = uuid4()

        # Mock user query
        mock_buyer = Mock(spec=User)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_buyer

        # Create transaction
        transaction_service.create_transaction(
            monto=Decimal('50000.00'),
            metodo_pago=MetodoPago.PSE,
            transaction_type=TransactionType.VENTA,
            comprador_id=buyer_id
        )

        # Verify logging was called
        mock_logger.info.assert_called()
        log_calls = mock_logger.info.call_args_list
        assert any("Transaction created" in str(call) for call in log_calls)

def test_run_all():
    """Run all transaction service unit tests"""
    pytest.main([__file__, "-v", "--tb=short"])

if __name__ == "__main__":
    print("🧪 TRANSACTION SERVICE UNIT TESTS")
    print("==================================")
    test_run_all()