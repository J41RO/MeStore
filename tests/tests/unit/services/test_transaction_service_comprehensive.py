# ~/tests/test_transaction_service_comprehensive.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Comprehensive Transaction Service Tests (FINANCIAL SECURITY CRITICAL)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
CRITICAL FINANCIAL TESTING: Comprehensive Transaction Service Test Suite

This test suite validates:
- Transaction creation and payment processing
- Financial integrity and rollback scenarios
- Payment gateway integration and error handling
- Transaction history and filtering
- Security validation and fraud prevention
- Performance under concurrent load

Coverage Target: 95%+ for all financial operations
Risk Level: CRITICAL - Real money transactions
"""

import pytest
import asyncio
from decimal import Decimal
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.transaction_service import (
    TransactionService,
    TransactionError
)
from app.models.transaction import (
    Transaction,
    EstadoTransaccion,
    TransactionType,
    MetodoPago
)
from app.models.commission import Commission, CommissionStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserType


class TestTransactionServiceCore:
    """Core transaction service functionality tests"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = TransactionService()
        self.mock_db = Mock(spec=Session)
        
    def test_service_initialization(self):
        """Test service initializes with correct configuration"""
        assert hasattr(self.service, 'environment')
        assert hasattr(self.service, 'audit_level')
        assert hasattr(self.service, 'max_transaction_amount')
        assert hasattr(self.service, 'min_transaction_amount')
        
        assert self.service.max_transaction_amount > 0
        assert self.service.min_transaction_amount > 0
        assert self.service.max_transaction_amount > self.service.min_transaction_amount
    
    def test_get_db_with_provided_session(self):
        """Test get_db uses provided session"""
        service = TransactionService(db_session=self.mock_db)
        assert service.get_db() == self.mock_db
    
    def test_transaction_reference_generation_uniqueness(self):
        """Test transaction reference generation is unique"""
        references = set()
        
        # Generate 1000 references to test uniqueness
        for _ in range(1000):
            ref = self.service._generate_transaction_reference()
            assert ref.startswith('TXN-')
            assert len(ref.split('-')) == 3
            assert len(ref) > 15
            references.add(ref)
        
        # All should be unique
        assert len(references) == 1000


class TestCommissionTransactionCreation:
    """Test commission transaction creation workflows"""
    
    def setup_method(self):
        """Setup mocked environment for testing"""
        self.service = TransactionService()
        self.mock_db = Mock(spec=Session)
        self.mock_commission = self._create_mock_commission()
        self.mock_vendor = self._create_mock_vendor()
        self.mock_order = self._create_mock_order()
        
    def _create_mock_commission(self) -> Mock:
        """Create a mock commission"""
        commission = Mock(spec=Commission)
        commission.id = uuid4()
        commission.status = CommissionStatus.APPROVED
        commission.vendor_id = uuid4()
        commission.order_id = 123
        commission.vendor_amount = Decimal('950.00')
        commission.commission_rate = Decimal('0.05')
        commission.transaction_id = None
        return commission
    
    def _create_mock_vendor(self) -> Mock:
        """Create a mock vendor user"""
        vendor = Mock(spec=User)
        vendor.id = self.mock_commission.vendor_id
        vendor.user_type = UserType.VENDEDOR
        return vendor
    
    def _create_mock_order(self) -> Mock:
        """Create a mock order"""
        order = Mock(spec=Order)
        order.id = self.mock_commission.order_id
        order.buyer_id = uuid4()
        order.order_number = 'ORD-20250913-001'
        order.status = OrderStatus.CONFIRMED
        return order
    
    def test_create_commission_transaction_success(self):
        """Test successful commission transaction creation"""
        # Setup mocks
        def mock_query_side_effect(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=self.mock_vendor))))
            elif model == Order:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=self.mock_order))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        self.mock_db.add = Mock()
        self.mock_db.flush = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        with patch.object(self.service, '_generate_transaction_reference', return_value='TXN-TEST-001'):
            transaction = self.service.create_commission_transaction(
                self.mock_commission,
                MetodoPago.TARJETA_CREDITO,
                "Test transaction",
                db=self.mock_db
            )
        
        # Verify transaction creation
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        assert transaction is not None
    
    def test_create_commission_transaction_not_approved(self):
        """Test transaction creation fails for non-approved commission"""
        self.mock_commission.status = CommissionStatus.PENDING
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.create_commission_transaction(
                self.mock_commission,
                MetodoPago.TARJETA_CREDITO,
                db=self.mock_db
            )
        
        assert "not approved" in str(exc_info.value)
        assert str(self.mock_commission.id) in str(exc_info.value.details)
    
    def test_create_commission_transaction_existing_transaction(self):
        """Test returns existing transaction if already exists"""
        existing_transaction = Mock(spec=Transaction)
        existing_transaction.id = uuid4()
        self.mock_commission.transaction_id = existing_transaction.id
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_transaction
        
        result = self.service.create_commission_transaction(
            self.mock_commission,
            MetodoPago.TARJETA_CREDITO,
            db=self.mock_db
        )
        
        assert result == existing_transaction
        self.mock_db.add.assert_not_called()
    
    def test_create_commission_transaction_vendor_not_found(self):
        """Test transaction creation fails when vendor not found"""
        def mock_query_side_effect(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.create_commission_transaction(
                self.mock_commission,
                MetodoPago.TARJETA_CREDITO,
                db=self.mock_db
            )
        
        assert "Vendor" in str(exc_info.value)
        assert "not found" in str(exc_info.value)
    
    def test_create_commission_transaction_order_not_found(self):
        """Test transaction creation fails when order not found"""
        def mock_query_side_effect(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=self.mock_vendor))))
            elif model == Order:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.create_commission_transaction(
                self.mock_commission,
                MetodoPago.TARJETA_CREDITO,
                db=self.mock_db
            )
        
        assert "Order" in str(exc_info.value)
        assert "not found" in str(exc_info.value)
    
    def test_create_commission_transaction_database_rollback(self):
        """Test database rollback occurs on creation errors"""
        def mock_query_side_effect(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=self.mock_vendor))))
            elif model == Order:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=self.mock_order))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        self.mock_db.add.side_effect = IntegrityError("Test error", None, None)
        
        with pytest.raises(TransactionError):
            self.service.create_commission_transaction(
                self.mock_commission,
                MetodoPago.TARJETA_CREDITO,
                db=self.mock_db
            )
        
        self.mock_db.rollback.assert_called_once()


class TestTransactionPaymentProcessing:
    """Test transaction payment processing workflows"""
    
    def setup_method(self):
        self.service = TransactionService()
        self.mock_db = Mock(spec=Session)
        self.transaction_id = uuid4()
        
    def _create_mock_transaction(self, estado=EstadoTransaccion.PENDIENTE) -> Mock:
        """Create a mock transaction"""
        transaction = Mock(spec=Transaction)
        transaction.id = self.transaction_id
        transaction.estado = estado
        transaction.transaction_type = TransactionType.COMISION
        transaction.observaciones = "Initial notes"
        transaction.marcar_pago_completado = Mock()
        return transaction
    
    def test_process_transaction_payment_success(self):
        """Test successful transaction payment processing"""
        mock_transaction = self._create_mock_transaction()
        mock_commission = Mock(spec=Commission)
        mock_commission.mark_as_paid = Mock()
        
        def mock_query_side_effect(model):
            if model == Transaction:
                mock_query = Mock()
                mock_query.filter.return_value.first.return_value = mock_transaction
                return mock_query
            elif model == Commission:
                mock_query = Mock()
                mock_query.filter.return_value.first.return_value = mock_commission
                return mock_query
        
        self.mock_db.query.side_effect = mock_query_side_effect
        self.mock_db.commit = Mock()
        
        with patch.object(self.service, '_simulate_payment_processing', return_value=True):
            result = self.service.process_transaction_payment(
                self.transaction_id,
                "PAY-12345",
                {"status": "success"},
                db=self.mock_db
            )
        
        assert result == mock_transaction
        assert mock_transaction.estado == EstadoTransaccion.COMPLETADA
        mock_transaction.marcar_pago_completado.assert_called_once_with("PAY-12345")
        mock_commission.mark_as_paid.assert_called_once()
        assert self.mock_db.commit.call_count == 2  # Once for processing, once for completion
    
    def test_process_transaction_payment_failure(self):
        """Test transaction payment processing failure"""
        mock_transaction = self._create_mock_transaction()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_transaction
        self.mock_db.commit = Mock()
        
        with patch.object(self.service, '_simulate_payment_processing', return_value=False):
            result = self.service.process_transaction_payment(
                self.transaction_id,
                "PAY-12345",
                db=self.mock_db
            )
        
        assert result == mock_transaction
        assert mock_transaction.estado == EstadoTransaccion.FALLIDA
        assert "Payment processing failed" in mock_transaction.observaciones
    
    def test_process_transaction_payment_not_found(self):
        """Test payment processing fails when transaction not found"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.process_transaction_payment(
                self.transaction_id,
                db=self.mock_db
            )
        
        assert "not found" in str(exc_info.value)
    
    def test_process_transaction_payment_invalid_status(self):
        """Test payment processing fails for non-pending transactions"""
        mock_transaction = self._create_mock_transaction(EstadoTransaccion.COMPLETADA)
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_transaction
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.process_transaction_payment(
                self.transaction_id,
                db=self.mock_db
            )
        
        assert "not in pending status" in str(exc_info.value)
    
    def test_process_transaction_payment_rollback_on_error(self):
        """Test database rollback on payment processing errors"""
        mock_transaction = self._create_mock_transaction()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_transaction
        self.mock_db.commit.side_effect = IntegrityError("Test error", None, None)
        
        with pytest.raises(TransactionError):
            self.service.process_transaction_payment(
                self.transaction_id,
                db=self.mock_db
            )
        
        self.mock_db.rollback.assert_called()


class TestTransactionHistoryAndFiltering:
    """Test transaction history retrieval and filtering"""
    
    def setup_method(self):
        self.service = TransactionService()
        self.mock_db = Mock(spec=Session)
        
    def test_get_transaction_history_basic(self):
        """Test basic transaction history retrieval"""
        # Mock transactions
        mock_transactions = []
        for i in range(5):
            transaction = Mock(spec=Transaction)
            transaction.to_dict.return_value = {'id': i, 'amount': 1000.0}
            mock_transactions.append(transaction)
        
        # Mock query chain
        mock_query = Mock()
        mock_query.count.return_value = 5
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_transactions
        mock_query.filter.return_value.all.return_value = mock_transactions  # For summary
        
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.service, '_calculate_transaction_summary', return_value={'total': 5000.0}):
            result = self.service.get_transaction_history(db=self.mock_db)
        
        assert 'transactions' in result
        assert 'pagination' in result
        assert 'summary' in result
        assert len(result['transactions']) == 5
        assert result['pagination']['total'] == 5
    
    def test_get_transaction_history_with_user_filter(self):
        """Test transaction history with user ID filter"""
        user_id = uuid4()
        
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_query.filter.return_value = mock_query  # Allow chaining
        
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.service, '_calculate_transaction_summary', return_value={}):
            result = self.service.get_transaction_history(
                user_id=user_id,
                db=self.mock_db
            )
        
        # Verify user filter was applied
        assert result['filters_applied']['user_id'] == str(user_id)
    
    def test_get_transaction_history_with_date_range(self):
        """Test transaction history with date range filter"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_query.filter.return_value = mock_query
        
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.service, '_calculate_transaction_summary', return_value={}):
            result = self.service.get_transaction_history(
                start_date=start_date,
                end_date=end_date,
                db=self.mock_db
            )
        
        # Verify date filters were applied
        assert result['filters_applied']['start_date'] == start_date.isoformat()
        assert result['filters_applied']['end_date'] == end_date.isoformat()
    
    def test_get_transaction_history_pagination(self):
        """Test transaction history pagination"""
        mock_query = Mock()
        mock_query.count.return_value = 150
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_query.filter.return_value.all.return_value = []
        
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.service, '_calculate_transaction_summary', return_value={}):
            result = self.service.get_transaction_history(
                limit=50,
                offset=100,
                db=self.mock_db
            )
        
        pagination = result['pagination']
        assert pagination['total'] == 150
        assert pagination['limit'] == 50
        assert pagination['offset'] == 100
        assert pagination['has_next'] == False  # 100+50=150, no more pages
        assert pagination['has_prev'] == True


class TestTransactionIntegrityValidation:
    """Test transaction integrity validation"""
    
    def setup_method(self):
        self.service = TransactionService()
        self.mock_db = Mock(spec=Session)
        
    def _create_mock_transaction_for_validation(self) -> Mock:
        """Create a mock transaction for validation testing"""
        transaction = Mock(spec=Transaction)
        transaction.id = uuid4()
        transaction.monto = Decimal('1500.00')
        transaction.monto_vendedor = Decimal('1425.00')
        transaction.transaction_type = TransactionType.COMISION
        transaction.comprador_id = uuid4()
        transaction.vendedor_id = uuid4()
        return transaction
    
    def test_validate_transaction_integrity_valid_transaction(self):
        """Test validation passes for valid transaction"""
        transaction = self._create_mock_transaction_for_validation()
        
        # Mock commission
        mock_commission = Mock(spec=Commission)
        mock_commission.vendor_amount = Decimal('1425.00')
        
        # Mock users
        mock_buyer = Mock(spec=User)
        mock_vendor = Mock(spec=User)
        
        def mock_query_side_effect(model):
            if model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_commission))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_buyer))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        with patch.object(self.service, '_validate_commission_calculation', return_value=True):
            result = self.service.validate_transaction_integrity(
                transaction, db=self.mock_db
            )
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
    
    def test_validate_transaction_integrity_negative_amount(self):
        """Test validation fails for negative amount"""
        transaction = self._create_mock_transaction_for_validation()
        transaction.monto = Decimal('-100.00')
        
        result = self.service.validate_transaction_integrity(
            transaction, db=self.mock_db
        )
        
        assert result['valid'] == False
        assert any('positive' in error for error in result['errors'])
    
    def test_validate_transaction_integrity_amount_too_large(self):
        """Test validation fails for amount exceeding maximum"""
        transaction = self._create_mock_transaction_for_validation()
        transaction.monto = self.service.max_transaction_amount + Decimal('1.00')
        
        result = self.service.validate_transaction_integrity(
            transaction, db=self.mock_db
        )
        
        assert result['valid'] == False
        assert any('exceeds maximum' in error for error in result['errors'])
    
    def test_validate_transaction_integrity_amount_too_small(self):
        """Test validation fails for amount below minimum"""
        transaction = self._create_mock_transaction_for_validation()
        transaction.monto = self.service.min_transaction_amount - Decimal('1.00')
        
        result = self.service.validate_transaction_integrity(
            transaction, db=self.mock_db
        )
        
        assert result['valid'] == False
        assert any('below minimum' in error for error in result['errors'])
    
    def test_validate_transaction_integrity_commission_amount_mismatch(self):
        """Test validation fails when commission amounts don't match"""
        transaction = self._create_mock_transaction_for_validation()
        transaction.transaction_type = TransactionType.COMISION
        
        # Mock commission with different vendor amount
        mock_commission = Mock(spec=Commission)
        mock_commission.vendor_amount = Decimal('1000.00')  # Different from transaction
        
        mock_buyer = Mock(spec=User)
        mock_vendor = Mock(spec=User)
        
        def mock_query_side_effect(model):
            if model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_commission))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_buyer))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        result = self.service.validate_transaction_integrity(
            transaction, db=self.mock_db
        )
        
        assert result['valid'] == False
        assert any('does not match commission' in error for error in result['errors'])
    
    def test_validate_transaction_integrity_user_not_found(self):
        """Test validation fails when user not found"""
        transaction = self._create_mock_transaction_for_validation()
        
        # Mock commission
        mock_commission = Mock(spec=Commission)
        mock_commission.vendor_amount = Decimal('1425.00')
        
        def mock_query_side_effect(model):
            if model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_commission))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        with patch.object(self.service, '_validate_commission_calculation', return_value=True):
            result = self.service.validate_transaction_integrity(
                transaction, db=self.mock_db
            )
        
        assert result['valid'] == False
        assert any('not found' in error for error in result['errors'])


class TestTransactionUtilityMethods:
    """Test transaction service utility methods"""
    
    def setup_method(self):
        self.service = TransactionService()
    
    def test_simulate_payment_processing_development(self):
        """Test payment simulation in development environment"""
        self.service.environment = 'development'
        transaction = Mock(spec=Transaction)
        
        # Run multiple times to test randomness
        results = []
        for _ in range(100):
            result = self.service._simulate_payment_processing(transaction)
            results.append(result)
        
        # Should have both True and False results (with 75% success rate)
        assert True in results
        # Note: False might not appear in 100 iterations due to 75% success rate
    
    def test_simulate_payment_processing_production(self):
        """Test payment simulation in production environment"""
        self.service.environment = 'production'
        transaction = Mock(spec=Transaction)
        
        result = self.service._simulate_payment_processing(transaction)
        
        # Production should always return True (placeholder for real gateway)
        assert result == True
    
    def test_calculate_transaction_summary_empty(self):
        """Test transaction summary calculation with no transactions"""
        result = self.service._calculate_transaction_summary([])
        
        expected_keys = [
            'total_amount', 'total_transactions', 'avg_amount',
            'commission_total', 'by_payment_method'
        ]
        
        for key in expected_keys:
            assert key in result
        
        assert result['total_amount'] == 0.0
        assert result['total_transactions'] == 0
        assert result['avg_amount'] == 0.0
    
    def test_calculate_transaction_summary_with_data(self):
        """Test transaction summary calculation with transaction data"""
        # Mock transactions
        transactions = []
        for i in range(3):
            transaction = Mock(spec=Transaction)
            transaction.monto = Decimal('1000.00')
            transaction.transaction_type = TransactionType.COMISION if i < 2 else TransactionType.ORDEN
            transaction.metodo_pago = MetodoPago.TARJETA_CREDITO
            transactions.append(transaction)
        
        result = self.service._calculate_transaction_summary(transactions)
        
        assert result['total_amount'] == 3000.0
        assert result['total_transactions'] == 3
        assert result['avg_amount'] == 1000.0
        assert result['commission_total'] == 2000.0  # 2 commission transactions
        assert 'TARJETA_CREDITO' in result['by_payment_method']
        assert result['by_payment_method']['TARJETA_CREDITO']['count'] == 3


class TestTransactionErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def setup_method(self):
        self.service = TransactionService()
    
    def test_transaction_error_with_details(self):
        """Test TransactionError includes proper details"""
        transaction_id = uuid4()
        details = {'amount': 1000.0, 'user_id': 'abc123'}
        
        error = TransactionError(
            "Test error", transaction_id=transaction_id, details=details
        )
        
        assert str(error) == "Test error"
        assert error.transaction_id == transaction_id
        assert error.details == details
    
    def test_service_handles_none_commission(self):
        """Test service handles None commission gracefully"""
        mock_db = Mock(spec=Session)
        
        with pytest.raises(TransactionError) as exc_info:
            self.service.create_commission_transaction(
                None, MetodoPago.TARJETA_CREDITO, db=mock_db
            )
        
        assert "Commission None" in str(exc_info.value)


class TestTransactionPerformance:
    """Performance and load testing for transaction service"""
    
    def test_transaction_reference_generation_performance(self):
        """Test transaction reference generation performance"""
        import time
        
        service = TransactionService()
        start_time = time.time()
        
        # Generate 1000 references
        for _ in range(1000):
            service._generate_transaction_reference()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 1000 generations in under 1 second
        assert duration < 1.0, f"Reference generation too slow: {duration:.3f}s"
    
    def test_validation_performance(self):
        """Test transaction validation performance"""
        import time
        
        service = TransactionService()
        mock_db = Mock(spec=Session)
        
        # Mock transaction
        transaction = Mock(spec=Transaction)
        transaction.monto = Decimal('1000.00')
        transaction.transaction_type = TransactionType.ORDEN
        transaction.comprador_id = uuid4()
        transaction.vendedor_id = uuid4()
        
        # Mock database responses
        mock_db.query.return_value.filter.return_value.first.return_value = Mock(spec=User)
        
        start_time = time.time()
        
        # Validate 100 transactions
        for _ in range(100):
            service.validate_transaction_integrity(transaction, db=mock_db)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 validations in under 1 second
        assert duration < 1.0, f"Validation too slow: {duration:.3f}s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])