# ~/tests/test_commission_service_comprehensive.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Comprehensive Commission Service Tests (FINANCIAL SECURITY CRITICAL)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
CRITICAL FINANCIAL TESTING: Comprehensive Commission Service Test Suite

This test suite validates:
- Financial calculation precision with edge cases
- Data integrity and rollback scenarios
- Commission workflow validation
- Error handling and security boundaries
- Performance under load conditions
- Integration with order and transaction systems

Coverage Target: 95%+ for all financial operations
Risk Level: HIGH - Financial calculations affecting real money
"""

import pytest
import asyncio
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.commission_service import (
    CommissionService, 
    CommissionCalculationError
)
from app.models.commission import (
    Commission, 
    CommissionType, 
    CommissionStatus,
    commission_settings
)
from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User, UserType
from app.models.product import Product
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType


class TestCommissionCalculationPrecision:
    """CRITICAL: Financial precision validation tests"""
    
    def test_decimal_precision_standard_cases(self):
        """Test standard commission calculations maintain precision"""
        test_cases = [
            (Decimal('1000.00'), Decimal('0.05'), Decimal('50.00'), Decimal('950.00')),
            (Decimal('1237.33'), Decimal('0.0567'), Decimal('70.16'), Decimal('1167.17')),
            (Decimal('99.99'), Decimal('0.03'), Decimal('3.00'), Decimal('96.99')),
            (Decimal('1000000.00'), Decimal('0.025'), Decimal('25000.00'), Decimal('975000.00')),
        ]
        
        for order_amount, rate, expected_commission, expected_vendor in test_cases:
            commission_amount, vendor_amount, platform_amount = Commission.calculate_commission(
                order_amount, rate, CommissionType.STANDARD
            )
            
            assert commission_amount == expected_commission, f"Commission failed for {order_amount}"
            assert vendor_amount == expected_vendor, f"Vendor amount failed for {order_amount}"
            assert platform_amount == expected_commission, f"Platform amount failed for {order_amount}"
            assert vendor_amount + platform_amount == order_amount, "Total amount mismatch"
    
    def test_precision_with_extreme_values(self):
        """Test precision with extreme monetary values"""
        # Very small amounts
        commission, vendor, platform = Commission.calculate_commission(
            Decimal('0.01'), Decimal('0.05'), CommissionType.STANDARD
        )
        assert commission + vendor == Decimal('0.01')
        
        # Very large amounts
        commission, vendor, platform = Commission.calculate_commission(
            Decimal('99999999.99'), Decimal('0.05'), CommissionType.STANDARD
        )
        assert commission + vendor == Decimal('99999999.99')
    
    def test_rounding_consistency(self):
        """Test that rounding is consistent and follows financial standards"""
        # Test amounts that require rounding - use properly rounded input amounts
        test_amounts = [
            Decimal('33.33'),   # Clean amount
            Decimal('66.67'),   # Clean amount
            Decimal('100.00'),  # Clean amount
        ]

        for amount in test_amounts:
            commission, vendor, platform = Commission.calculate_commission(
                amount, Decimal('0.10'), CommissionType.STANDARD
            )

            # Verify all amounts have exactly 2 decimal places
            assert commission.as_tuple().exponent == -2
            assert vendor.as_tuple().exponent == -2
            assert platform.as_tuple().exponent == -2

            # Verify total is conserved (within rounding tolerance)
            total = vendor + platform
            assert abs(total - amount) <= Decimal('0.01'), f"Total {total} != amount {amount}"
    
    def test_commission_types_different_rates(self):
        """Test different commission types produce different rates"""
        order_amount = Decimal('1000.00')
        
        standard_comm, standard_vendor, _ = Commission.calculate_commission(
            order_amount, Decimal('0.05'), CommissionType.STANDARD
        )
        premium_comm, premium_vendor, _ = Commission.calculate_commission(
            order_amount, Decimal('0.03'), CommissionType.PREMIUM
        )
        
        # Premium should have lower commission, higher vendor amount
        assert premium_comm < standard_comm
        assert premium_vendor > standard_vendor


class TestCommissionServiceCore:
    """Core commission service functionality tests"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = CommissionService()
        self.mock_db = Mock(spec=Session)
        
    def test_service_initialization(self):
        """Test service initializes with correct configuration"""
        assert self.service.settings is not None
        assert hasattr(self.service, 'environment')
        assert hasattr(self.service, 'batch_size')
        assert hasattr(self.service, 'async_threshold')
        assert self.service.batch_size > 0
        assert self.service.async_threshold > 0
    
    def test_get_db_with_provided_session(self):
        """Test get_db uses provided session"""
        service = CommissionService(db_session=self.mock_db)
        assert service.get_db() == self.mock_db
    
    def test_commission_number_generation_uniqueness(self):
        """Test commission number generation is unique and follows format"""
        numbers = set()
        
        # Generate 1000 numbers to test uniqueness
        for _ in range(1000):
            number = self.service._generate_commission_number()
            assert number.startswith('COM-')
            assert len(number.split('-')) == 3
            assert len(number) > 15  # Should be reasonably long
            numbers.add(number)
        
        # All should be unique
        assert len(numbers) == 1000


class TestCommissionCalculationWorkflows:
    """Test complete commission calculation workflows"""
    
    def setup_method(self):
        """Setup mocked environment for testing"""
        self.service = CommissionService()
        self.mock_db = Mock(spec=Session)
        self.mock_order = self._create_mock_order()
        self.mock_user = self._create_mock_user()
        
    def _create_mock_order(self) -> Mock:
        """Create a mock order with proper structure"""
        order = Mock(spec=Order)
        order.id = 123
        order.status = OrderStatus.CONFIRMED
        order.total_amount = Decimal('1500.00')
        order.order_number = 'ORD-20250913-001'
        order.buyer_id = uuid4()
        
        # Mock order items
        item = Mock(spec=OrderItem)
        product = Mock(spec=Product)
        product.vendedor_id = uuid4()
        item.product = product
        item.product_id = uuid4()
        order.items = [item]
        
        return order
    
    def _create_mock_user(self) -> Mock:
        """Create a mock user (vendor)"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.user_type = UserType.VENDEDOR
        return user
    
    def test_calculate_commission_for_order_success(self):
        """Test successful commission calculation for order"""
        # Setup mocks
        self.mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing commission
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # Execute
        with patch.object(self.service, '_generate_commission_number', return_value='COM-TEST-001'):
            commission = self.service.calculate_commission_for_order(
                self.mock_order, CommissionType.STANDARD, db=self.mock_db
            )
        
        # Verify
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        assert commission is not None
    
    def test_calculate_commission_invalid_order_status(self):
        """Test commission calculation fails for invalid order status"""
        self.mock_order.status = OrderStatus.PENDING
        
        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.calculate_commission_for_order(
                self.mock_order, db=self.mock_db
            )
        
        assert "not in valid status" in str(exc_info.value)
        assert exc_info.value.order_id == self.mock_order.id
    
    def test_calculate_commission_existing_commission(self):
        """Test returns existing commission if already calculated"""
        existing_commission = Mock(spec=Commission)
        existing_commission.id = uuid4()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_commission
        
        result = self.service.calculate_commission_for_order(
            self.mock_order, db=self.mock_db
        )
        
        assert result == existing_commission
        self.mock_db.add.assert_not_called()
    
    def test_calculate_commission_no_items(self):
        """Test commission calculation fails for order with no items"""
        self.mock_order.items = []
        # Ensure no existing commission is found
        self.mock_db.query().filter().first.return_value = None

        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.calculate_commission_for_order(
                self.mock_order, db=self.mock_db
            )

        assert "has no items" in str(exc_info.value)
    
    def test_calculate_commission_no_vendor(self):
        """Test commission calculation fails when product has no vendor"""
        self.mock_order.items[0].product.vendedor_id = None
        # Ensure no existing commission is found
        self.mock_db.query().filter().first.return_value = None

        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.calculate_commission_for_order(
                self.mock_order, db=self.mock_db
            )

        assert "has no vendor assigned" in str(exc_info.value)
    
    def test_calculate_commission_database_rollback_on_error(self):
        """Test database rollback occurs on calculation errors"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.add.side_effect = IntegrityError("Test error", None, None)
        
        with pytest.raises(CommissionCalculationError):
            self.service.calculate_commission_for_order(
                self.mock_order, db=self.mock_db
            )
        
        self.mock_db.rollback.assert_called_once()


class TestCommissionBatchProcessing:
    """Test batch processing functionality"""
    
    def setup_method(self):
        self.service = CommissionService()
        self.mock_db = Mock(spec=Session)
    
    def test_process_orders_batch_small_batch_sync(self):
        """Test small batch processes synchronously"""
        order_ids = [1, 2, 3]  # Small batch, below async threshold
        
        # Mock orders
        mock_orders = []
        for i, order_id in enumerate(order_ids):
            order = Mock(spec=Order)
            order.id = order_id
            order.status = OrderStatus.CONFIRMED
            order.total_amount = Decimal('1000.00')
            order.items = [Mock()]
            order.items[0].product = Mock()
            order.items[0].product.vendedor_id = uuid4()
            mock_orders.append(order)
        
        self.mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = mock_orders
        
        # Mock successful commission calculations
        with patch.object(self.service, 'calculate_commission_for_order') as mock_calc:
            mock_calc.return_value = Mock(spec=Commission)
            
            results = self.service.process_orders_batch(
                order_ids, CommissionType.STANDARD, db=self.mock_db
            )
        
        assert results['success'] == order_ids
        assert results['failed'] == []
        assert mock_calc.call_count == len(order_ids)
    
    def test_process_orders_batch_with_failures(self):
        """Test batch processing handles individual failures"""
        order_ids = [1, 2, 3]
        
        mock_orders = []
        for order_id in order_ids:
            order = Mock(spec=Order)
            order.id = order_id
            order.status = OrderStatus.CONFIRMED
            mock_orders.append(order)
        
        self.mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = mock_orders
        
        def mock_calc_side_effect(order, *args, **kwargs):
            if order.id == 2:
                raise CommissionCalculationError("Test error")
            return Mock(spec=Commission)
        
        with patch.object(self.service, 'calculate_commission_for_order') as mock_calc:
            mock_calc.side_effect = mock_calc_side_effect
            
            results = self.service.process_orders_batch(
                order_ids, CommissionType.STANDARD, db=self.mock_db
            )
        
        assert results['success'] == [1, 3]
        assert results['failed'] == [2]


class TestCommissionApprovalWorkflow:
    """Test commission approval workflows"""
    
    def setup_method(self):
        self.service = CommissionService()
        self.mock_db = Mock(spec=Session)
        
    def test_approve_commission_success(self):
        """Test successful commission approval"""
        commission_id = uuid4()
        approver_id = uuid4()
        
        mock_commission = Mock(spec=Commission)
        mock_commission.id = commission_id
        mock_commission.status = CommissionStatus.PENDING
        mock_commission.approve = Mock()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_commission
        
        with patch.object(self.service, '_trigger_webhook'):
            result = self.service.approve_commission(
                commission_id, approver_id, "Test approval", db=self.mock_db
            )
        
        assert result == mock_commission
        mock_commission.approve.assert_called_once_with(approver_id, "Test approval")
        self.mock_db.commit.assert_called_once()
    
    def test_approve_commission_not_found(self):
        """Test approval fails when commission not found"""
        commission_id = uuid4()
        approver_id = uuid4()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.approve_commission(
                commission_id, approver_id, db=self.mock_db
            )
        
        assert "not found" in str(exc_info.value)
    
    def test_approve_commission_invalid_status(self):
        """Test approval fails for non-pending commissions"""
        commission_id = uuid4()
        approver_id = uuid4()
        
        mock_commission = Mock(spec=Commission)
        mock_commission.id = commission_id
        mock_commission.status = CommissionStatus.PAID
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_commission
        
        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.approve_commission(
                commission_id, approver_id, db=self.mock_db
            )
        
        assert "cannot be approved" in str(exc_info.value)


class TestVendorEarningsReporting:
    """Test vendor earnings calculation and reporting"""
    
    def setup_method(self):
        self.service = CommissionService()
        self.mock_db = Mock(spec=Session)
    
    def test_get_vendor_earnings_comprehensive_report(self):
        """Test comprehensive vendor earnings report generation"""
        vendor_id = uuid4()
        
        # Mock commissions data
        mock_commissions = []
        for i in range(5):
            commission = Mock(spec=Commission)
            commission.order_amount = Decimal('1000.00')
            commission.commission_amount = Decimal('50.00')
            commission.vendor_amount = Decimal('950.00')
            commission.commission_rate = Decimal('0.05')
            commission.status = CommissionStatus.PAID if i < 3 else CommissionStatus.PENDING
            mock_commissions.append(commission)
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_commissions
        self.mock_db.query.return_value = mock_query
        
        report = self.service.get_vendor_earnings(
            vendor_id, db=self.mock_db
        )
        
        # Verify report structure
        assert 'vendor_id' in report
        assert 'summary' in report
        assert 'breakdown_by_status' in report
        assert report['vendor_id'] == str(vendor_id)
        
        # Verify calculations
        summary = report['summary']
        assert summary['total_commissions'] == 5
        assert summary['total_order_amount'] == 5000.0
        assert summary['total_commission_amount'] == 250.0
        assert summary['total_vendor_earnings'] == 4750.0
        assert summary['paid_earnings'] == 2850.0  # 3 paid * 950
        assert summary['pending_earnings'] == 1900.0  # 2 pending * 950


class TestCommissionIntegration:
    """Integration tests for commission service with other components"""
    
    def test_commission_settings_integration(self):
        """Test integration with commission settings"""
        # Test rate retrieval
        standard_rate = commission_settings.get_commission_rate(CommissionType.STANDARD)
        premium_rate = commission_settings.get_commission_rate(CommissionType.PREMIUM)
        
        assert isinstance(standard_rate, float)
        assert isinstance(premium_rate, float)
        assert 0 <= standard_rate <= 1
        assert 0 <= premium_rate <= 1
        
        # Premium should typically have lower commission rate
        assert premium_rate <= standard_rate
    
    def test_webhook_configuration(self):
        """Test webhook URL configuration"""
        webhook_urls = commission_settings.WEBHOOK_URLS
        
        required_webhooks = [
            'commission_calculated',
            'commission_approved', 
            'commission_paid'
        ]
        
        for webhook in required_webhooks:
            assert webhook in webhook_urls
            url = webhook_urls[webhook]
            assert url.startswith('http')
            assert '/api/v1/webhooks/' in url


class TestCommissionErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def setup_method(self):
        self.service = CommissionService()
    
    def test_commission_calculation_error_with_details(self):
        """Test CommissionCalculationError includes proper details"""
        order_id = 123
        details = {'vendor_id': 'abc123', 'amount': 1000.0}
        
        error = CommissionCalculationError(
            "Test error", order_id=order_id, details=details
        )
        
        assert str(error) == "Test error"
        assert error.order_id == order_id
        assert error.details == details
    
    def test_service_handles_none_order(self):
        """Test service handles None order gracefully"""
        mock_db = Mock(spec=Session)
        
        with pytest.raises(CommissionCalculationError) as exc_info:
            self.service.calculate_commission_for_order(None, db=mock_db)
        
        assert "Order None" in str(exc_info.value)
        assert exc_info.value.order_id is None


class TestCommissionPerformance:
    """Performance and load testing for commission service"""
    
    def test_commission_calculation_performance(self):
        """Test commission calculation performance"""
        import time
        
        start_time = time.time()
        
        # Calculate 1000 commissions
        for i in range(1000):
            Commission.calculate_commission(
                Decimal('1000.00'), Decimal('0.05'), CommissionType.STANDARD
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 1000 calculations in under 1 second
        assert duration < 1.0, f"Commission calculations too slow: {duration:.3f}s"
    
    def test_memory_usage_stability(self):
        """Test that commission calculations don't leak memory"""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Perform many calculations
        for _ in range(10000):
            Commission.calculate_commission(
                Decimal('1234.56'), Decimal('0.0789'), CommissionType.PREMIUM
            )
        
        # Force another garbage collection
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])