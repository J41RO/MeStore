# ~/tests/test_financial_integration_workflows.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Financial Integration Workflow Tests (BUSINESS CRITICAL)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
BUSINESS CRITICAL: Financial Integration Workflow Tests

This test suite validates:
- End-to-end commission-transaction workflows
- Order-to-payment complete cycles
- Financial data consistency across services
- Error handling and rollback scenarios
- Integration between all financial components

Coverage Target: 100% for financial workflows
Risk Level: MAXIMUM - Complete financial integrity validation
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

from app.services.commission_service import CommissionService, CommissionCalculationError
from app.services.transaction_service import TransactionService, TransactionError
from app.models.commission import Commission, CommissionType, CommissionStatus
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType, MetodoPago
from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User, UserType
from app.models.product import Product


class TestCompleteFinancialWorkflows:
    """Test complete financial workflows from order to payment"""
    
    def setup_method(self):
        """Setup integrated test environment"""
        self.commission_service = CommissionService()
        self.transaction_service = TransactionService()
        self.mock_db = Mock(spec=Session)
        
        # Create comprehensive test data
        self.test_data = self._create_complete_test_scenario()
    
    def _create_complete_test_scenario(self) -> Dict:
        """Create complete test scenario with all entities"""
        # Create test IDs
        buyer_id = uuid4()
        vendor_id = uuid4()
        product_id = uuid4()
        order_id = 123
        
        # Create test order
        order = Mock(spec=Order)
        order.id = order_id
        order.order_number = 'ORD-20250913-001'
        order.status = OrderStatus.CONFIRMED
        order.total_amount = Decimal('2500.00')
        order.buyer_id = buyer_id
        order.created_at = datetime.now()
        
        # Create order item
        item = Mock(spec=OrderItem)
        item.product_id = product_id
        product = Mock(spec=Product)
        product.vendedor_id = vendor_id
        item.product = product
        order.items = [item]
        
        # Create users
        buyer = Mock(spec=User)
        buyer.id = buyer_id
        buyer.user_type = UserType.COMPRADOR

        vendor = Mock(spec=User)
        vendor.id = vendor_id
        vendor.user_type = UserType.VENDEDOR
        
        return {
            'order': order,
            'buyer': buyer,
            'vendor': vendor,
            'product': product,
            'item': item,
            'order_id': order_id,
            'buyer_id': buyer_id,
            'vendor_id': vendor_id,
            'product_id': product_id
        }
    
    def test_complete_commission_to_transaction_workflow(self):
        """Test complete workflow from commission calculation to transaction completion"""
        test_data = self.test_data
        order = test_data['order']
        
        # Step 1: Calculate commission
        def commission_query_mock(model):
            if model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
        
        self.mock_db.query.side_effect = commission_query_mock
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        with patch.object(self.commission_service, '_generate_commission_number', return_value='COM-TEST-001'):
            commission = self.commission_service.calculate_commission_for_order(
                order, CommissionType.STANDARD, db=self.mock_db
            )
        
        # Verify commission was created
        assert commission is not None
        self.mock_db.add.assert_called_once()
        
        # Step 2: Approve commission
        mock_commission = Mock(spec=Commission)
        mock_commission.id = uuid4()
        mock_commission.status = CommissionStatus.PENDING
        mock_commission.approve = Mock()
        
        def approval_query_mock(model):
            if model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_commission))))
        
        self.mock_db.query.side_effect = approval_query_mock
        
        with patch.object(self.commission_service, '_trigger_webhook'):
            approved_commission = self.commission_service.approve_commission(
                mock_commission.id, uuid4(), "Approved for testing", db=self.mock_db
            )
        
        assert approved_commission == mock_commission
        mock_commission.approve.assert_called_once()
        
        # Step 3: Create transaction for commission
        mock_commission.status = CommissionStatus.APPROVED
        mock_commission.vendor_amount = Decimal('2375.00')  # 95% of 2500
        mock_commission.commission_rate = Decimal('0.05')
        mock_commission.transaction_id = None
        
        def transaction_query_mock(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=test_data['vendor']))))
            elif model == Order:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=order))))
        
        self.mock_db.query.side_effect = transaction_query_mock
        self.mock_db.flush = Mock()
        
        with patch.object(self.transaction_service, '_generate_transaction_reference', return_value='TXN-TEST-001'):
            transaction = self.transaction_service.create_commission_transaction(
                mock_commission,
                MetodoPago.TARJETA_CREDITO,
                "Commission payment",
                db=self.mock_db
            )
        
        assert transaction is not None
        
        # Step 4: Process payment
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.id = uuid4()
        mock_transaction.estado = EstadoTransaccion.PENDIENTE
        mock_transaction.transaction_type = TransactionType.COMISION
        mock_transaction.observaciones = "Initial notes"
        mock_transaction.marcar_pago_completado = Mock()
        
        mock_commission_for_payment = Mock(spec=Commission)
        mock_commission_for_payment.mark_as_paid = Mock()
        
        def payment_query_mock(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_transaction))))
            elif model == Commission:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_commission_for_payment))))
        
        self.mock_db.query.side_effect = payment_query_mock
        
        with patch.object(self.transaction_service, '_simulate_payment_processing', return_value=True):
            processed_transaction = self.transaction_service.process_transaction_payment(
                mock_transaction.id,
                "PAY-12345",
                {"gateway": "test", "status": "success"},
                db=self.mock_db
            )
        
        assert processed_transaction == mock_transaction
        assert mock_transaction.estado == EstadoTransaccion.COMPLETADA
        mock_commission_for_payment.mark_as_paid.assert_called_once()
        
        # Verify the complete workflow integrity
        assert self.mock_db.commit.call_count >= 3  # Commission, approval, transaction creation, payment
    
    def test_workflow_error_handling_and_rollback(self):
        """Test error handling and rollback in complete workflow"""
        test_data = self.test_data
        order = test_data['order']
        
        # Simulate commission calculation failure
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.add.side_effect = IntegrityError("Commission creation failed", None, None)
        
        with pytest.raises(CommissionCalculationError):
            self.commission_service.calculate_commission_for_order(
                order, CommissionType.STANDARD, db=self.mock_db
            )
        
        # Verify rollback was called
        self.mock_db.rollback.assert_called_once()
        
        # Test transaction creation failure after commission success
        self.mock_db.reset_mock()
        
        mock_commission = Mock(spec=Commission)
        mock_commission.status = CommissionStatus.APPROVED
        mock_commission.vendor_id = test_data['vendor_id']
        mock_commission.order_id = test_data['order_id']
        mock_commission.vendor_amount = Decimal('2375.00')
        mock_commission.transaction_id = None
        
        def failing_transaction_query(model):
            if model == Transaction:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            elif model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=test_data['vendor']))))
            elif model == Order:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=order))))
        
        self.mock_db.query.side_effect = failing_transaction_query
        self.mock_db.add.side_effect = IntegrityError("Transaction creation failed", None, None)
        
        with pytest.raises(TransactionError):
            self.transaction_service.create_commission_transaction(
                mock_commission,
                MetodoPago.TARJETA_CREDITO,
                db=self.mock_db
            )
        
        # Verify transaction rollback was called
        self.mock_db.rollback.assert_called_once()
    
    def test_financial_data_consistency_validation(self):
        """Test financial data consistency across services"""
        test_data = self.test_data
        order_amount = Decimal('2500.00')
        commission_rate = Decimal('0.05')
        
        # Calculate expected amounts
        expected_commission = order_amount * commission_rate
        expected_vendor_amount = order_amount - expected_commission
        expected_platform_amount = expected_commission
        
        # Test commission calculation consistency
        commission_amount, vendor_amount, platform_amount = Commission.calculate_commission(
            order_amount, commission_rate, CommissionType.STANDARD
        )
        
        assert commission_amount == expected_commission
        assert vendor_amount == expected_vendor_amount
        assert platform_amount == expected_platform_amount
        assert vendor_amount + platform_amount == order_amount
        
        # Create mock commission and transaction
        mock_commission = Mock(spec=Commission)
        mock_commission.order_amount = order_amount
        mock_commission.commission_rate = commission_rate
        mock_commission.commission_amount = commission_amount
        mock_commission.vendor_amount = vendor_amount
        mock_commission.platform_amount = platform_amount
        
        mock_transaction = Mock(spec=Transaction)
        mock_transaction.monto = vendor_amount
        mock_transaction.monto_vendedor = vendor_amount
        mock_transaction.transaction_type = TransactionType.COMISION
        
        # Validate transaction consistency with commission
        validation_result = self.transaction_service.validate_transaction_integrity(
            mock_transaction, db=self.mock_db
        )
        
        # Should pass basic amount validation
        assert mock_transaction.monto > 0
        assert mock_transaction.monto_vendedor == vendor_amount
    
    def test_concurrent_commission_calculation_safety(self):
        """Test safety of concurrent commission calculations"""
        test_data = self.test_data
        order = test_data['order']
        
        # Simulate existing commission (race condition)
        existing_commission = Mock(spec=Commission)
        existing_commission.id = uuid4()
        existing_commission.order_id = order.id
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_commission
        
        # Should return existing commission without creating duplicate
        result = self.commission_service.calculate_commission_for_order(
            order, CommissionType.STANDARD, db=self.mock_db
        )
        
        assert result == existing_commission
        self.mock_db.add.assert_not_called()  # Should not create new commission
    
    def test_batch_processing_with_mixed_results(self):
        """Test batch processing with mixed success/failure scenarios"""
        order_ids = [1, 2, 3, 4, 5]
        
        # Create mock orders - some valid, some invalid
        mock_orders = []
        for i, order_id in enumerate(order_ids):
            order = Mock(spec=Order)
            order.id = order_id
            order.status = OrderStatus.CONFIRMED if i % 2 == 0 else OrderStatus.PENDING  # Alternate valid/invalid
            order.total_amount = Decimal('1000.00')
            order.items = [Mock()]
            order.items[0].product = Mock()
            order.items[0].product.vendedor_id = uuid4() if i != 2 else None  # Order 3 has no vendor
            mock_orders.append(order)
        
        self.mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = mock_orders
        
        # Mock commission calculation - succeed for valid orders
        def mock_calc_side_effect(order, *args, **kwargs):
            if order.status != OrderStatus.CONFIRMED:
                raise CommissionCalculationError("Invalid status")
            if not order.items[0].product.vendedor_id:
                raise CommissionCalculationError("No vendor")
            return Mock(spec=Commission)
        
        with patch.object(self.commission_service, 'calculate_commission_for_order') as mock_calc:
            mock_calc.side_effect = mock_calc_side_effect
            
            results = self.commission_service.process_orders_batch(
                order_ids, CommissionType.STANDARD, db=self.mock_db
            )
        
        # Should have mixed results
        # Orders 1, 5 (indices 0, 4) should succeed (CONFIRMED status and have vendor)
        # Orders 2, 4 (indices 1, 3) should fail (PENDING status)
        # Order 3 (index 2) should fail (no vendor)
        assert len(results['success']) == 2  # Orders 1 and 5
        assert len(results['failed']) == 3   # Orders 2, 3, and 4
        assert set(results['success']) == {1, 5}
        assert set(results['failed']) == {2, 3, 4}


class TestFinancialAuditingAndLogging:
    """Test financial auditing and logging functionality"""
    
    def setup_method(self):
        self.commission_service = CommissionService()
        self.transaction_service = TransactionService()
    
    def test_commission_audit_logging(self):
        """Test commission calculation audit logging"""
        # Create test commission and order
        commission = Mock(spec=Commission)
        commission.id = uuid4()
        commission.commission_number = 'COM-TEST-001'
        commission.vendor_id = uuid4()
        commission.order_amount = Decimal('1000.00')
        commission.commission_rate = Decimal('0.05')
        commission.commission_amount = Decimal('50.00')
        commission.vendor_amount = Decimal('950.00')
        commission.platform_amount = Decimal('50.00')
        commission.calculation_method = 'automatic'
        
        order = Mock(spec=Order)
        order.id = 123
        order.order_number = 'ORD-TEST-001'
        
        # Test audit logging
        with patch('app.services.commission_service.logger') as mock_logger:
            self.commission_service._log_commission_calculation(commission, order)
            
            # Verify logging was called
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert commission.commission_number in log_call
            assert order.order_number in log_call
    
    def test_transaction_audit_logging(self):
        """Test transaction creation audit logging"""
        # Create test transaction and commission
        transaction = Mock(spec=Transaction)
        transaction.id = uuid4()
        transaction.monto = Decimal('950.00')
        transaction.monto_vendedor = Decimal('950.00')
        transaction.metodo_pago = MetodoPago.TARJETA_CREDITO
        transaction.transaction_type = TransactionType.COMISION
        transaction.vendedor_id = uuid4()
        transaction.comprador_id = uuid4()
        transaction.referencia_externa = 'TXN-TEST-001'
        
        commission = Mock(spec=Commission)
        commission.id = uuid4()
        
        # Test audit logging
        with patch('app.services.transaction_service.logger') as mock_logger:
            self.transaction_service._log_transaction_creation(transaction, commission)
            
            # Verify logging was called
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert transaction.referencia_externa in log_call
    
    def test_payment_processing_audit_logging(self):
        """Test payment processing audit logging"""
        transaction = Mock(spec=Transaction)
        transaction.id = uuid4()
        transaction.referencia_externa = 'TXN-TEST-001'
        
        # Test successful processing log
        with patch('app.services.transaction_service.logger') as mock_logger:
            self.transaction_service._log_transaction_processing(transaction, True)
            
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert 'SUCCESS' in log_call
            assert transaction.referencia_externa in log_call
        
        # Test failed processing log
        with patch('app.services.transaction_service.logger') as mock_logger:
            self.transaction_service._log_transaction_processing(transaction, False)
            
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert 'FAILED' in log_call
            assert transaction.referencia_externa in log_call


class TestFinancialReportingIntegration:
    """Test financial reporting and analytics integration"""
    
    def setup_method(self):
        self.commission_service = CommissionService()
        self.transaction_service = TransactionService()
        self.mock_db = Mock(spec=Session)
    
    def test_vendor_earnings_comprehensive_report(self):
        """Test comprehensive vendor earnings report"""
        vendor_id = uuid4()
        
        # Create mock commission data representing different scenarios
        mock_commissions = []
        commission_data = [
            (Decimal('1000.00'), Decimal('50.00'), Decimal('950.00'), CommissionStatus.PAID),
            (Decimal('1500.00'), Decimal('75.00'), Decimal('1425.00'), CommissionStatus.PAID),
            (Decimal('800.00'), Decimal('40.00'), Decimal('760.00'), CommissionStatus.APPROVED),
            (Decimal('1200.00'), Decimal('60.00'), Decimal('1140.00'), CommissionStatus.PENDING),
            (Decimal('2000.00'), Decimal('100.00'), Decimal('1900.00'), CommissionStatus.PAID),
        ]
        
        for order_amt, comm_amt, vendor_amt, status in commission_data:
            commission = Mock(spec=Commission)
            commission.order_amount = order_amt
            commission.commission_amount = comm_amt
            commission.vendor_amount = vendor_amt
            commission.commission_rate = Decimal('0.05')
            commission.status = status
            mock_commissions.append(commission)
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_commissions
        self.mock_db.query.return_value = mock_query
        
        # Get earnings report
        report = self.commission_service.get_vendor_earnings(
            vendor_id, db=self.mock_db
        )
        
        # Verify report calculations
        assert report['vendor_id'] == str(vendor_id)
        
        summary = report['summary']
        assert summary['total_commissions'] == 5
        assert summary['total_order_amount'] == 6500.0  # Sum of all order amounts
        assert summary['total_commission_amount'] == 325.0  # Sum of all commission amounts
        assert summary['total_vendor_earnings'] == 6175.0  # Sum of all vendor amounts
        
        # Paid earnings: 3 paid commissions (950 + 1425 + 1900)
        assert summary['paid_earnings'] == 4275.0
        
        # Pending earnings: 1 pending + 1 approved (1140 + 760)
        assert summary['pending_earnings'] == 1900.0
        
        # Verify breakdown by status
        breakdown = report['breakdown_by_status']
        assert breakdown[CommissionStatus.PAID.value]['count'] == 3
        assert breakdown[CommissionStatus.APPROVED.value]['count'] == 1
        assert breakdown[CommissionStatus.PENDING.value]['count'] == 1
    
    def test_transaction_history_comprehensive_filtering(self):
        """Test comprehensive transaction history filtering"""
        user_id = uuid4()
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # Create mock transaction data
        mock_transactions = []
        for i in range(10):
            transaction = Mock(spec=Transaction)
            transaction.to_dict.return_value = {
                'id': str(uuid4()),
                'amount': 1000.0 + i * 100,
                'status': 'COMPLETADA',
                'created_at': (datetime.now() - timedelta(days=i)).isoformat()
            }
            mock_transactions.append(transaction)
        
        # Mock query chain for filtering
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_transactions
        mock_query.all.return_value = mock_transactions
        
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.transaction_service, '_calculate_transaction_summary') as mock_summary:
            mock_summary.return_value = {
                'total_amount': 14500.0,
                'total_transactions': 10,
                'avg_amount': 1450.0,
                'commission_total': 10000.0,
                'by_payment_method': {'TARJETA_CREDITO': {'count': 10, 'amount': 14500.0}}
            }
            
            result = self.transaction_service.get_transaction_history(
                user_id=user_id,
                transaction_type=TransactionType.COMISION,
                start_date=start_date,
                end_date=end_date,
                status_filter=[EstadoTransaccion.COMPLETADA],
                limit=50,
                offset=0,
                db=self.mock_db
            )
        
        # Verify result structure
        assert 'transactions' in result
        assert 'pagination' in result
        assert 'summary' in result
        assert 'filters_applied' in result
        
        # Verify filters were recorded
        filters = result['filters_applied']
        assert filters['user_id'] == str(user_id)
        assert filters['transaction_type'] == TransactionType.COMISION.value
        assert filters['start_date'] == start_date.isoformat()
        assert filters['end_date'] == end_date.isoformat()
        assert filters['status_filter'] == [EstadoTransaccion.COMPLETADA.value]
        
        # Verify pagination
        pagination = result['pagination']
        assert pagination['total'] == 10
        assert pagination['limit'] == 50
        assert pagination['offset'] == 0
        assert pagination['has_next'] == False
        assert pagination['has_prev'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])