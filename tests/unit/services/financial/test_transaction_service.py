# tests/unit/services/financial/test_transaction_service.py
# CRITICAL: Comprehensive Transaction Service Testing Suite
# PRIORITY: Restore test coverage for payment processing and financial integrity

import pytest
import logging
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from sqlalchemy.orm import Session
from app.services.transaction_service import TransactionService, TransactionError
from app.services.commission_service import CommissionService
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType, MetodoPago
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.order import Order, OrderStatus
from app.models.user import User, UserType

logger = logging.getLogger(__name__)


@pytest.mark.financial
@pytest.mark.transaction
class TestTransactionService:
    """
    CRITICAL: Transaction Service Test Suite

    Tests all payment processing logic, financial integrity validation,
    and transaction state management for the financial system.
    """

    def test_transaction_service_initialization(self, db_session: Session):
        """Test transaction service initializes with correct configuration"""
        service = TransactionService(db_session=db_session)

        assert service.db == db_session
        assert service.environment == "test"
        assert service.audit_level == "standard"
        assert isinstance(service.max_transaction_amount, Decimal)
        assert isinstance(service.min_transaction_amount, Decimal)

    @pytest.mark.critical
    def test_create_commission_transaction_success(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        test_vendor_user: User,
        audit_logger
    ):
        """CRITICAL: Test successful transaction creation from approved commission"""
        audit_logger("transaction_creation_start", {
            "order_id": test_confirmed_order.id,
            "vendor_id": str(test_vendor_user.id)
        })

        # Create and approve commission first
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Simulate commission approval
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()
        commission.approved_at = datetime.now()

        # Create transaction from commission
        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA,
            notes="Test transaction creation"
        )

        # Validate transaction creation
        assert transaction is not None
        assert transaction.id is not None
        assert transaction.estado == EstadoTransaccion.PENDIENTE
        assert transaction.transaction_type == TransactionType.COMISION

        # Validate financial integrity
        assert transaction.monto == commission.vendor_amount
        assert transaction.monto_vendedor == commission.vendor_amount
        assert transaction.vendedor_id == commission.vendor_id
        assert transaction.comprador_id == test_confirmed_order.buyer_id

        # Validate commission linking
        assert commission.transaction_id == transaction.id

        # Validate transaction reference format
        assert transaction.referencia_externa.startswith("TXN-")
        assert len(transaction.referencia_externa) > 15

        audit_logger("transaction_creation_success", {
            "transaction_id": str(transaction.id),
            "amount": float(transaction.monto),
            "reference": transaction.referencia_externa
        })

    def test_create_transaction_for_non_approved_commission(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test error handling when creating transaction for non-approved commission"""
        # Create pending commission (not approved)
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        assert commission.status == CommissionStatus.PENDING

        # Attempt to create transaction - should fail
        with pytest.raises(TransactionError) as exc_info:
            test_transaction_service.create_commission_transaction(
                commission=commission,
                payment_method=MetodoPago.TRANSFERENCIA
            )

        assert "not approved" in str(exc_info.value)
        assert exc_info.value.details['commission_id'] == str(commission.id)

    def test_prevent_duplicate_transaction_creation(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test prevention of duplicate transactions for the same commission"""
        # Create approved commission
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        # Create first transaction
        transaction1 = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Attempt to create duplicate - should return existing
        transaction2 = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        assert transaction1.id == transaction2.id
        assert transaction1.referencia_externa == transaction2.referencia_externa

    @pytest.mark.parametrize("payment_method", [
        MetodoPago.EFECTIVO,
        MetodoPago.TARJETA_CREDITO,
        MetodoPago.TARJETA_DEBITO,
        MetodoPago.PSE
    ])
    def test_transaction_creation_with_different_payment_methods(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        payment_method: MetodoPago
    ):
        """Test transaction creation with various payment methods"""
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=payment_method
        )

        assert transaction.metodo_pago == payment_method
        assert transaction.estado == EstadoTransaccion.PENDIENTE

    @pytest.mark.critical
    def test_process_transaction_payment_success(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        audit_logger
    ):
        """CRITICAL: Test successful transaction payment processing"""
        # Create approved commission and transaction
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        audit_logger("payment_processing_start", {
            "transaction_id": str(transaction.id),
            "initial_status": transaction.estado.value
        })

        # Mock successful payment processing
        with patch.object(test_transaction_service, '_simulate_payment_processing', return_value=True):
            processed_transaction = test_transaction_service.process_transaction_payment(
                transaction_id=transaction.id,
                payment_reference="PAY-TEST-123456",
                gateway_response={"status": "success", "code": "00"}
            )

        # Validate transaction processing
        assert processed_transaction.estado == EstadoTransaccion.COMPLETADA
        assert processed_transaction.referencia_pago == "PAY-TEST-123456"
        assert "Gateway response:" in processed_transaction.observaciones

        # Validate commission was marked as paid
        assert commission.status == CommissionStatus.PAID

        audit_logger("payment_processing_success", {
            "transaction_id": str(processed_transaction.id),
            "final_status": processed_transaction.estado.value,
            "payment_reference": processed_transaction.referencia_pago
        })

    def test_process_transaction_payment_failure(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test transaction processing failure handling"""
        # Create approved commission and transaction
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Mock failed payment processing
        with patch.object(test_transaction_service, '_simulate_payment_processing', return_value=False):
            processed_transaction = test_transaction_service.process_transaction_payment(
                transaction_id=transaction.id,
                payment_reference="PAY-FAIL-123456"
            )

        # Validate failure handling
        assert processed_transaction.estado == EstadoTransaccion.FALLIDA
        assert "Payment processing failed" in processed_transaction.observaciones

    def test_process_non_existent_transaction(
        self,
        test_transaction_service: TransactionService
    ):
        """Test error handling for processing non-existent transaction"""
        fake_transaction_id = uuid4()

        with pytest.raises(TransactionError) as exc_info:
            test_transaction_service.process_transaction_payment(
                transaction_id=fake_transaction_id
            )

        assert "not found" in str(exc_info.value)

    def test_process_non_pending_transaction(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test error handling for processing transaction in wrong state"""
        # Create and process transaction to completed state
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Manually set to completed
        transaction.estado = EstadoTransaccion.COMPLETADA

        # Try to process again - should fail
        with pytest.raises(TransactionError) as exc_info:
            test_transaction_service.process_transaction_payment(
                transaction_id=transaction.id
            )

        assert "not in pending status" in str(exc_info.value)

    def test_get_transaction_history_basic(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        test_vendor_user: User
    ):
        """Test basic transaction history retrieval"""
        # Create multiple transactions
        transactions = []
        for i in range(3):
            commission = test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )
            commission.status = CommissionStatus.APPROVED
            commission.approved_by = uuid4()

            transaction = test_transaction_service.create_commission_transaction(
                commission=commission,
                payment_method=MetodoPago.TRANSFERENCIA,
                notes=f"Transaction {i+1}"
            )
            transactions.append(transaction)

        # Get transaction history
        history = test_transaction_service.get_transaction_history(
            user_id=test_vendor_user.id,
            limit=10
        )

        assert 'transactions' in history
        assert 'pagination' in history
        assert 'summary' in history
        assert len(history['transactions']) >= 3
        assert history['pagination']['total'] >= 3

    def test_get_transaction_history_with_filters(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        test_vendor_user: User
    ):
        """Test transaction history with various filters"""
        # Create commission and transaction
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Test with transaction type filter
        history_filtered = test_transaction_service.get_transaction_history(
            transaction_type=TransactionType.COMISION,
            limit=10
        )

        commission_transactions = [
            t for t in history_filtered['transactions']
            if t['transaction_type'] == TransactionType.COMISION.value
        ]
        assert len(commission_transactions) >= 1

        # Test with status filter
        history_status = test_transaction_service.get_transaction_history(
            status_filter=[EstadoTransaccion.PENDIENTE],
            limit=10
        )

        pending_transactions = [
            t for t in history_status['transactions']
            if t['estado'] == EstadoTransaccion.PENDIENTE.value
        ]
        assert len(pending_transactions) >= 1

    def test_get_transaction_history_date_range(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test transaction history with date range filtering"""
        # Create transaction
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Test date range filtering
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        history_within_range = test_transaction_service.get_transaction_history(
            start_date=yesterday,
            end_date=tomorrow,
            limit=10
        )

        assert history_within_range['pagination']['total'] >= 1

        # Test excluding date range
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=3)

        history_outside_range = test_transaction_service.get_transaction_history(
            start_date=future_start,
            end_date=future_end,
            limit=10
        )

        assert history_outside_range['pagination']['total'] == 0

    @pytest.mark.critical
    def test_validate_transaction_integrity_success(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """CRITICAL: Test transaction integrity validation for valid transactions"""
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Validate transaction integrity
        validation_result = test_transaction_service.validate_transaction_integrity(transaction)

        assert validation_result['valid'] is True
        assert len(validation_result['errors']) == 0

    @pytest.mark.parametrize("invalid_amount,expected_error", [
        (Decimal("0.00"), "must be positive"),
        (Decimal("-1000.00"), "must be positive"),
        (Decimal("50000000.00"), "exceeds maximum"),
        (Decimal("50.00"), "below minimum")
    ])
    def test_validate_transaction_integrity_invalid_amounts(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        invalid_amount: Decimal,
        expected_error: str
    ):
        """Test transaction integrity validation for invalid amounts"""
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Manipulate transaction amount to invalid value
        transaction.monto = invalid_amount
        transaction.monto_vendedor = invalid_amount

        validation_result = test_transaction_service.validate_transaction_integrity(transaction)

        assert validation_result['valid'] is False
        assert any(expected_error in error for error in validation_result['errors'])

    def test_transaction_reference_generation_uniqueness(
        self,
        test_transaction_service: TransactionService
    ):
        """Test transaction reference generation is unique and properly formatted"""
        references = set()

        for _ in range(100):
            reference = test_transaction_service._generate_transaction_reference()
            assert reference.startswith("TXN-")
            assert len(reference) > 15
            assert reference not in references
            references.add(reference)

    @patch('app.services.transaction_service.logger')
    def test_audit_logging_for_transactions(
        self,
        mock_logger: MagicMock,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test audit logging for transaction operations"""
        # Enable detailed logging
        test_transaction_service.enable_detailed_logging = True

        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        transaction = test_transaction_service.create_commission_transaction(
            commission=commission,
            payment_method=MetodoPago.TRANSFERENCIA
        )

        # Verify audit logging was called
        mock_logger.info.assert_called()
        audit_calls = [call for call in mock_logger.info.call_args_list
                      if 'audit' in str(call).lower() or 'transaction' in str(call).lower()]
        assert len(audit_calls) > 0

    def test_transaction_summary_calculation(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService
    ):
        """Test transaction summary statistics calculation"""
        # Create multiple transactions with different amounts
        test_amounts = [
            Decimal("10000.00"),
            Decimal("20000.00"),
            Decimal("30000.00")
        ]

        transactions = []
        for amount in test_amounts:
            test_confirmed_order.total_amount = amount

            commission = test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )
            commission.status = CommissionStatus.APPROVED
            commission.approved_by = uuid4()

            transaction = test_transaction_service.create_commission_transaction(
                commission=commission,
                payment_method=MetodoPago.TRANSFERENCIA
            )
            transaction.estado = EstadoTransaccion.COMPLETADA
            transactions.append(transaction)

        # Calculate summary
        summary = test_transaction_service._calculate_transaction_summary(transactions)

        expected_total = sum(commission.vendor_amount for commission in
                           [test_commission_service.calculate_commission_for_order(
                               test_confirmed_order, CommissionType.STANDARD
                           ) for amount in test_amounts])

        assert summary['total_transactions'] == 3
        assert summary['total_amount'] > 0
        assert summary['avg_amount'] > 0
        assert 'by_payment_method' in summary

    @pytest.mark.slow
    def test_transaction_processing_performance(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        performance_monitor
    ):
        """Test transaction processing performance under load"""
        import time

        # Create base commission
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        start_time = time.time()

        # Process multiple transaction operations
        for i in range(20):
            transaction = test_transaction_service.create_commission_transaction(
                commission=commission,
                payment_method=MetodoPago.TRANSFERENCIA,
                notes=f"Performance test {i}"
            )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete 20 transaction creations in under 3 seconds
        assert execution_time < 3.0, f"Transaction operations too slow: {execution_time}s"

    def test_error_handling_and_rollback(
        self,
        test_transaction_service: TransactionService,
        test_confirmed_order: Order,
        test_commission_service: CommissionService,
        db_session: Session
    ):
        """Test database rollback on transaction creation errors"""
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = uuid4()

        # Simulate database error by using invalid vendor ID
        original_vendor_id = commission.vendor_id
        commission.vendor_id = None

        with pytest.raises(TransactionError):
            test_transaction_service.create_commission_transaction(
                commission=commission,
                payment_method=MetodoPago.TRANSFERENCIA
            )

        # Verify no transaction was created due to rollback
        transactions = db_session.query(Transaction).filter(
            Transaction.id == commission.transaction_id
        ).all()
        assert len(transactions) == 0

        # Restore original data
        commission.vendor_id = original_vendor_id

    @patch('random.choice')
    def test_payment_processing_simulation(
        self,
        mock_random_choice: MagicMock,
        test_transaction_service: TransactionService
    ):
        """Test payment processing simulation logic"""
        # Test development environment simulation
        test_transaction_service.environment = 'development'

        # Mock random failure
        mock_random_choice.return_value = False
        result = test_transaction_service._simulate_payment_processing(None)
        assert result is False

        # Mock random success
        mock_random_choice.return_value = True
        result = test_transaction_service._simulate_payment_processing(None)
        assert result is True

        # Test production environment
        test_transaction_service.environment = 'production'
        result = test_transaction_service._simulate_payment_processing(None)
        assert result is True  # Always success in production simulation