# tests/unit/services/financial/test_commission_service.py
# CRITICAL: Comprehensive Commission Service Testing Suite
# PRIORITY: Restore test coverage for financial calculations with >90% coverage

import pytest
import logging
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from sqlalchemy.orm import Session
from app.services.commission_service import CommissionService, CommissionCalculationError
from app.models.commission import Commission, CommissionStatus, CommissionType, commission_settings
from app.models.order import Order, OrderStatus
from app.models.user import User, UserType
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType

logger = logging.getLogger(__name__)


@pytest.mark.financial
@pytest.mark.commission
class TestCommissionService:
    """
    CRITICAL: Commission Service Test Suite

    Tests all financial calculation logic, edge cases, and error conditions
    for the commission service that handles vendor/platform revenue splits.
    """

    def test_commission_service_initialization(self, db_session: Session, monkeypatch):
        """Test commission service initializes correctly with all dependencies"""
        # Set test environment
        monkeypatch.setenv('ENVIRONMENT', 'test')
        monkeypatch.setenv('COMMISSION_AUDIT_LEVEL', 'standard')
        monkeypatch.setenv('COMMISSION_BATCH_SIZE', '50')
        monkeypatch.setenv('COMMISSION_ASYNC_THRESHOLD', '25')

        service = CommissionService(db_session=db_session)

        assert service.db == db_session
        assert service.settings == commission_settings
        assert service.environment == "test"
        assert isinstance(service.batch_size, int)
        assert isinstance(service.async_threshold, int)

    @pytest.mark.critical
    def test_calculate_commission_for_valid_confirmed_order(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        sample_commission_data: dict,
        audit_logger
    ):
        """CRITICAL: Test commission calculation for confirmed order - core financial logic"""
        audit_logger("commission_calculation_start", {
            "order_id": test_confirmed_order.id,
            "order_amount": float(test_confirmed_order.total_amount)
        })

        # Execute commission calculation
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Validate commission creation
        assert commission is not None
        assert commission.id is not None
        assert commission.order_id == test_confirmed_order.id
        assert commission.status == CommissionStatus.PENDING

        # Validate financial calculations - CRITICAL for revenue integrity
        expected_rate = Decimal("0.05")  # 5% standard rate
        expected_commission = test_confirmed_order.total_amount * expected_rate
        expected_vendor_amount = test_confirmed_order.total_amount - expected_commission

        assert commission.commission_rate == expected_rate
        assert commission.commission_amount == expected_commission
        assert commission.vendor_amount == expected_vendor_amount
        assert commission.platform_amount == expected_commission

        # Validate totals integrity - MUST balance
        calculated_total = commission.vendor_amount + commission.platform_amount
        assert calculated_total == test_confirmed_order.total_amount

        # Validate metadata
        assert commission.currency == "COP"
        assert commission.calculation_method == "automatic"
        assert commission.commission_number.startswith("COM-")

        audit_logger("commission_calculation_success", {
            "commission_id": str(commission.id),
            "commission_amount": float(commission.commission_amount),
            "vendor_amount": float(commission.vendor_amount)
        })

    def test_calculate_commission_different_rates(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """Test commission calculation with different commission types and rates"""
        test_cases = [
            (CommissionType.STANDARD, Decimal("0.05")),  # 5%
            (CommissionType.PREMIUM, Decimal("0.03")),   # 3%
            (CommissionType.ENTERPRISE, Decimal("0.02")) # 2%
        ]

        order_amount = test_confirmed_order.total_amount

        for commission_type, expected_rate in test_cases:
            commission = test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=commission_type
            )

            expected_commission_amount = order_amount * expected_rate
            expected_vendor_amount = order_amount - expected_commission_amount

            assert commission.commission_rate == expected_rate
            assert commission.commission_amount == expected_commission_amount
            assert commission.vendor_amount == expected_vendor_amount

            # Verify financial integrity
            total_check = commission.vendor_amount + commission.platform_amount
            assert total_check == order_amount

    def test_calculate_commission_with_custom_rate(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """Test commission calculation with custom override rate"""
        custom_rate = Decimal("0.08")  # 8% custom rate

        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD,
            custom_rate=custom_rate
        )

        expected_commission = test_confirmed_order.total_amount * custom_rate
        expected_vendor = test_confirmed_order.total_amount - expected_commission

        assert commission.commission_rate == custom_rate
        assert commission.commission_amount == expected_commission
        assert commission.vendor_amount == expected_vendor

    @pytest.mark.critical
    def test_calculate_commission_precision_handling(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """CRITICAL: Test decimal precision handling for financial calculations"""
        # Test with amounts that require precise decimal handling
        precision_test_amounts = [
            Decimal("99.99"),      # Edge case small amount
            Decimal("33333.33"),   # Repeating decimals
            Decimal("100000.01"),  # Large amount with cents
            Decimal("999999.99")   # Maximum precision test
        ]

        for amount in precision_test_amounts:
            test_confirmed_order.total_amount = amount

            commission = test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )

            # Verify precision is maintained
            assert isinstance(commission.commission_amount, Decimal)
            assert isinstance(commission.vendor_amount, Decimal)
            assert isinstance(commission.platform_amount, Decimal)

            # Verify totals still balance with precision
            total = commission.vendor_amount + commission.platform_amount
            assert abs(total - amount) < Decimal('0.01')  # Allow 1 cent tolerance

    def test_prevent_duplicate_commission_creation(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """Test that duplicate commissions cannot be created for the same order"""
        # Create first commission
        commission1 = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Attempt to create duplicate - should return existing
        commission2 = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        assert commission1.id == commission2.id
        assert commission1.commission_number == commission2.commission_number

    @pytest.mark.parametrize("invalid_status", [
        OrderStatus.PENDING,
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED
    ])
    def test_reject_commission_for_invalid_order_status(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        invalid_status: OrderStatus
    ):
        """Test commission calculation rejection for orders in invalid states"""
        test_confirmed_order.status = invalid_status

        with pytest.raises(CommissionCalculationError) as exc_info:
            test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )

        assert "not in valid status" in str(exc_info.value)
        assert exc_info.value.order_id == test_confirmed_order.id

    def test_handle_order_without_items(
        self,
        test_commission_service: CommissionService,
        test_buyer_user: User,
        db_session: Session
    ):
        """Test error handling for orders without items"""
        # Create order without items
        empty_order = Order(
            id=uuid4(),
            order_number="ORD-EMPTY-001",
            buyer_id=test_buyer_user.id,
            total_amount=Decimal("100000.00"),
            status=OrderStatus.CONFIRMED,
            payment_method="credit_card",
            shipping_address="Test Address"
        )
        db_session.add(empty_order)
        db_session.commit()

        with pytest.raises(CommissionCalculationError) as exc_info:
            test_commission_service.calculate_commission_for_order(
                order=empty_order,
                commission_type=CommissionType.STANDARD
            )

        assert "has no items" in str(exc_info.value)
        assert exc_info.value.order_id == empty_order.id

    def test_commission_approval_workflow(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        test_admin_user: User
    ):
        """Test commission approval workflow"""
        # Create pending commission
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        assert commission.status == CommissionStatus.PENDING

        # Approve commission
        approved_commission = test_commission_service.approve_commission(
            commission_id=commission.id,
            approver_user_id=test_admin_user.id,
            notes="Approved for testing"
        )

        assert approved_commission.status == CommissionStatus.APPROVED
        assert approved_commission.approved_by == test_admin_user.id
        assert approved_commission.approved_at is not None

    def test_approve_non_existent_commission(
        self,
        test_commission_service: CommissionService,
        test_admin_user: User
    ):
        """Test error handling for approving non-existent commission"""
        fake_commission_id = uuid4()

        with pytest.raises(CommissionCalculationError) as exc_info:
            test_commission_service.approve_commission(
                commission_id=fake_commission_id,
                approver_user_id=test_admin_user.id
            )

        assert "not found" in str(exc_info.value)

    def test_approve_already_approved_commission(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        test_admin_user: User
    ):
        """Test error handling for approving already approved commission"""
        # Create and approve commission
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        test_commission_service.approve_commission(
            commission_id=commission.id,
            approver_user_id=test_admin_user.id
        )

        # Try to approve again
        with pytest.raises(CommissionCalculationError) as exc_info:
            test_commission_service.approve_commission(
                commission_id=commission.id,
                approver_user_id=test_admin_user.id
            )

        assert "cannot be approved" in str(exc_info.value)

    def test_get_vendor_earnings_summary(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        test_vendor_user: User
    ):
        """Test vendor earnings summary generation"""
        # Create commission for vendor
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Get earnings summary
        earnings = test_commission_service.get_vendor_earnings(
            vendor_id=test_vendor_user.id
        )

        assert earnings['vendor_id'] == str(test_vendor_user.id)
        assert earnings['summary']['total_commissions'] == 1
        assert earnings['summary']['total_order_amount'] == float(test_confirmed_order.total_amount)
        assert earnings['summary']['pending_earnings'] == float(commission.vendor_amount)
        assert earnings['currency'] == 'COP'

    def test_vendor_earnings_with_date_filter(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        test_vendor_user: User
    ):
        """Test vendor earnings with date range filtering"""
        # Create commission
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Test with date ranges
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        # Should include commission (within range)
        earnings_within = test_commission_service.get_vendor_earnings(
            vendor_id=test_vendor_user.id,
            start_date=yesterday,
            end_date=tomorrow
        )
        assert earnings_within['summary']['total_commissions'] == 1

        # Should exclude commission (before range)
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=3)

        earnings_outside = test_commission_service.get_vendor_earnings(
            vendor_id=test_vendor_user.id,
            start_date=future_start,
            end_date=future_end
        )
        assert earnings_outside['summary']['total_commissions'] == 0

    def test_batch_order_processing(
        self,
        test_commission_service: CommissionService,
        commission_test_setup: dict
    ):
        """Test batch processing of multiple orders for commission calculation"""
        db_session = commission_test_setup['db']
        buyer = commission_test_setup['buyer']
        vendor = commission_test_setup['vendor']

        # Create multiple test orders
        order_ids = []
        for i in range(5):
            order = Order(
                id=uuid4(),
                order_number=f"ORD-BATCH-{i:03d}",
                buyer_id=buyer.id,
                total_amount=Decimal(f"{(i+1)*10000}.00"),
                status=OrderStatus.CONFIRMED,
                payment_method="credit_card",
                shipping_address=f"Test Address {i}"
            )
            db_session.add(order)
            order_ids.append(order.id)

        db_session.commit()

        # Process batch
        results = test_commission_service.process_orders_batch(
            order_ids=order_ids,
            commission_type=CommissionType.STANDARD
        )

        assert len(results['success']) == 5
        assert len(results['failed']) == 0

    @patch('app.services.commission_service.logger')
    def test_audit_logging_integration(
        self,
        mock_logger: MagicMock,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """Test audit logging for commission operations"""
        # Enable detailed logging
        test_commission_service.enable_detailed_logging = True

        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Verify audit logging was called
        mock_logger.info.assert_called()
        log_calls = [call for call in mock_logger.info.call_args_list
                    if 'Commission calculation audit:' in str(call)]
        assert len(log_calls) > 0

    def test_commission_number_generation_uniqueness(
        self,
        test_commission_service: CommissionService
    ):
        """Test that commission numbers are unique and properly formatted"""
        numbers = set()

        for _ in range(100):
            number = test_commission_service._generate_commission_number()
            assert number.startswith("COM-")
            assert len(number) > 15  # Timestamp + random suffix
            assert number not in numbers  # Unique
            numbers.add(number)

    @pytest.mark.slow
    def test_commission_calculation_performance(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        performance_monitor
    ):
        """Test commission calculation performance under load"""
        import time

        start_time = time.time()

        # Perform multiple calculations
        for _ in range(50):
            test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete 50 calculations in under 5 seconds
        assert execution_time < 5.0, f"Commission calculations too slow: {execution_time}s"

    def test_commission_integrity_validation(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order
    ):
        """Test commission calculation integrity validation"""
        commission = test_commission_service.calculate_commission_for_order(
            order=test_confirmed_order,
            commission_type=CommissionType.STANDARD
        )

        # Validate integrity
        is_valid = test_commission_service.validate_commission_integrity(commission)
        assert is_valid is True

    def test_error_handling_and_rollback(
        self,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        db_session: Session
    ):
        """Test database rollback on commission calculation errors"""
        # Force an error by manipulating order data
        original_total = test_confirmed_order.total_amount
        test_confirmed_order.total_amount = None  # This should cause an error

        with pytest.raises(CommissionCalculationError):
            test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )

        # Verify no commission was created due to rollback
        commissions = db_session.query(Commission).filter(
            Commission.order_id == test_confirmed_order.id
        ).all()
        assert len(commissions) == 0

        # Restore original data
        test_confirmed_order.total_amount = original_total

    @pytest.mark.parametrize("environment,webhook_enabled", [
        ("production", True),
        ("development", False),
        ("test", False)
    ])
    @patch('app.services.commission_service.logger')
    def test_webhook_integration(
        self,
        mock_logger: MagicMock,
        test_commission_service: CommissionService,
        test_confirmed_order: Order,
        environment: str,
        webhook_enabled: bool
    ):
        """Test webhook integration for different environments"""
        test_commission_service.environment = environment

        with patch.object(test_commission_service.settings, 'WEBHOOK_URLS', {'commission_calculated': 'http://test.com/webhook'}):
            commission = test_commission_service.calculate_commission_for_order(
                order=test_confirmed_order,
                commission_type=CommissionType.STANDARD
            )

            # Verify appropriate webhook logging based on environment
            webhook_calls = [call for call in mock_logger.info.call_args_list
                            if 'webhook' in str(call).lower()]

            if webhook_enabled:
                assert len(webhook_calls) > 0
            # Note: In test environment, webhooks are disabled so no calls expected