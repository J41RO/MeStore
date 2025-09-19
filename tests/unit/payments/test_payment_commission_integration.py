import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.services.payments.payment_commission_service import PaymentCommissionService, PaymentCommissionError
from app.models.order import Order, OrderStatus, Transaction, PaymentStatus
from app.models.payment import WebhookEvent
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.user import User, UserType


class TestPaymentCommissionService:
    """Test PaymentCommissionService functionality"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.refresh = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def mock_commission_service(self):
        """Create mock commission service"""
        service = AsyncMock()
        service.calculate_order_commission = AsyncMock()
        return service

    @pytest.fixture
    def payment_commission_service(self, mock_db):
        """Create PaymentCommissionService instance"""
        service = PaymentCommissionService(mock_db)
        return service

    @pytest.fixture
    def sample_order(self):
        """Create sample order"""
        order = Mock(spec=Order)
        order.id = 123
        order.total_amount = 100.0
        order.status = OrderStatus.CONFIRMED
        order.vendor_id = 1
        order.buyer_id = 2
        order.metadata = {}
        return order

    @pytest.fixture
    def sample_transaction(self, sample_order):
        """Create sample transaction"""
        transaction = Mock(spec=Transaction)
        transaction.id = 456
        transaction.order = sample_order
        transaction.status = PaymentStatus.APPROVED
        return transaction

    @pytest.fixture
    def sample_vendor(self):
        """Create sample vendor"""
        vendor = Mock(spec=User)
        vendor.id = 1
        vendor.user_type = UserType.VENDOR
        vendor.email = "vendor@test.com"
        return vendor

    @pytest.fixture
    def sample_buyer(self):
        """Create sample buyer"""
        buyer = Mock(spec=User)
        buyer.id = 2
        buyer.user_type = UserType.BUYER
        buyer.email = "buyer@test.com"
        return buyer

    @pytest.fixture
    def sample_payment_data(self):
        """Create sample payment data"""
        return {
            "id": "trx_test_12345",
            "reference": "ORDER_123_20231201120000",
            "status": "APPROVED",
            "amount_in_cents": 10000,
            "currency": "COP",
            "payment_method": {"type": "CARD"}
        }

    @pytest.mark.asyncio
    async def test_process_payment_approval_success(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test successful payment approval commission processing"""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock commission service
        with patch.object(payment_commission_service, 'commission_service') as mock_comm_service:
            mock_comm_service.calculate_order_commission.return_value = {
                "success": True,
                "commission": {
                    "commission_rate": 0.1,
                    "commission_amount": 10.0,
                    "vendor_amount": 90.0,
                    "platform_amount": 10.0
                }
            }

            # Mock existing commission check
            with patch.object(payment_commission_service, '_check_existing_commission', return_value=None):
                result = await payment_commission_service.process_payment_approval(
                    transaction_id=456,
                    payment_data=sample_payment_data,
                    webhook_event_id=789
                )

                assert result["success"] is True
                assert result["commission_amount"] == Decimal("10.0")
                assert result["vendor_amount"] == Decimal("90.0")
                assert result["platform_amount"] == Decimal("10.0")
                assert result["commission_rate"] == Decimal("0.1")

                # Verify commission was created
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_process_payment_approval_existing_commission(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test payment approval when commission already exists"""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock existing commission
        existing_commission = Mock(spec=Commission)
        existing_commission.id = 999
        existing_commission.commission_amount = Decimal("10.0")
        existing_commission.status = CommissionStatus.PENDING

        with patch.object(payment_commission_service, '_check_existing_commission', return_value=existing_commission):
            result = await payment_commission_service.process_payment_approval(
                transaction_id=456,
                payment_data=sample_payment_data
            )

            assert result["success"] is True
            assert result["message"] == "Commission already calculated"
            assert result["commission_id"] == 999
            assert result["amount"] == Decimal("10.0")

            # Verify no new commission was created
            mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_payment_approval_transaction_not_found(
        self,
        payment_commission_service,
        mock_db,
        sample_payment_data
    ):
        """Test payment approval when transaction not found"""
        # Mock database query returning None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(PaymentCommissionError, match="Transaction 456 not found"):
            await payment_commission_service.process_payment_approval(
                transaction_id=456,
                payment_data=sample_payment_data
            )

    @pytest.mark.asyncio
    async def test_process_payment_approval_order_not_confirmed(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test payment approval when order not confirmed"""
        # Set order status to pending
        sample_transaction.order.status = OrderStatus.PENDING

        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        result = await payment_commission_service.process_payment_approval(
            transaction_id=456,
            payment_data=sample_payment_data
        )

        assert result["success"] is False
        assert "not eligible for commission calculation" in result["message"]

    @pytest.mark.asyncio
    async def test_process_payment_approval_commission_calculation_fails(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test payment approval when commission calculation fails"""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock commission service failure
        with patch.object(payment_commission_service, 'commission_service') as mock_comm_service:
            mock_comm_service.calculate_order_commission.return_value = {
                "success": False,
                "error": "Commission calculation failed"
            }

            # Mock existing commission check
            with patch.object(payment_commission_service, '_check_existing_commission', return_value=None):
                with pytest.raises(PaymentCommissionError, match="Commission calculation failed"):
                    await payment_commission_service.process_payment_approval(
                        transaction_id=456,
                        payment_data=sample_payment_data
                    )

    @pytest.mark.asyncio
    async def test_process_payment_refund_success(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction
    ):
        """Test successful payment refund commission adjustment"""
        # Create existing commission
        existing_commission = Mock(spec=Commission)
        existing_commission.id = 999
        existing_commission.order_id = 123
        existing_commission.vendor_id = 1
        existing_commission.buyer_id = 2
        existing_commission.base_amount = Decimal("100.0")
        existing_commission.commission_amount = Decimal("10.0")
        existing_commission.vendor_amount = Decimal("90.0")
        existing_commission.platform_amount = Decimal("10.0")
        existing_commission.commission_rate = Decimal("0.1")
        existing_commission.order = sample_transaction.order

        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_commission
        mock_db.execute.return_value = mock_result

        refund_data = {
            "id": "refund_12345",
            "reference": "ORDER_123_20231201120000",
            "amount_in_cents": 5000,  # 50% refund
            "currency": "COP"
        }

        result = await payment_commission_service.process_payment_refund(
            transaction_id=456,
            refund_data=refund_data,
            webhook_event_id=789
        )

        assert result["success"] is True
        assert result["original_commission_id"] == 999
        assert result["refund_amount"] == Decimal("50.0")
        assert result["commission_adjustment"] == Decimal("-5.0")  # 50% of 10.0
        assert result["vendor_adjustment"] == Decimal("-45.0")    # 50% of 90.0

        # Verify refund commission was created
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_process_payment_refund_no_commission(
        self,
        payment_commission_service,
        mock_db
    ):
        """Test payment refund when no commission exists"""
        # Mock database query returning None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        refund_data = {
            "id": "refund_12345",
            "amount_in_cents": 5000
        }

        result = await payment_commission_service.process_payment_refund(
            transaction_id=456,
            refund_data=refund_data
        )

        assert result["success"] is True
        assert result["message"] == "No commission to adjust for refund"

    @pytest.mark.asyncio
    async def test_get_commission_summary_with_filters(
        self,
        payment_commission_service,
        mock_db
    ):
        """Test commission summary generation with filters"""
        # Create mock commissions
        commission1 = Mock(spec=Commission)
        commission1.commission_amount = Decimal("10.0")
        commission1.vendor_amount = Decimal("90.0")
        commission1.platform_amount = Decimal("10.0")
        commission1.base_amount = Decimal("100.0")
        commission1.status = CommissionStatus.PENDING
        commission1.commission_type = CommissionType.SALE

        commission2 = Mock(spec=Commission)
        commission2.commission_amount = Decimal("-5.0")
        commission2.vendor_amount = Decimal("-45.0")
        commission2.platform_amount = Decimal("-5.0")
        commission2.base_amount = Decimal("-50.0")
        commission2.status = CommissionStatus.PENDING
        commission2.commission_type = CommissionType.REFUND

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [commission1, commission2]
        mock_db.execute.return_value = mock_result

        result = await payment_commission_service.get_commission_summary(
            vendor_id=1,
            date_from=datetime(2023, 1, 1),
            date_to=datetime(2023, 12, 31)
        )

        assert result["summary"]["total_commissions"] == 2
        assert result["summary"]["total_commission_amount"] == Decimal("5.0")  # 10.0 + (-5.0)
        assert result["summary"]["total_vendor_amount"] == Decimal("45.0")     # 90.0 + (-45.0)
        assert result["summary"]["total_platform_amount"] == Decimal("5.0")    # 10.0 + (-5.0)

        assert "pending" in result["by_status"]
        assert result["by_status"]["pending"]["count"] == 2

        assert "sale" in result["by_type"]
        assert "refund" in result["by_type"]

    @pytest.mark.asyncio
    async def test_commission_metadata_integration(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test that commission records include proper payment metadata"""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock commission service
        with patch.object(payment_commission_service, 'commission_service') as mock_comm_service:
            mock_comm_service.calculate_order_commission.return_value = {
                "success": True,
                "commission": {
                    "commission_rate": 0.1,
                    "commission_amount": 10.0,
                    "vendor_amount": 90.0,
                    "platform_amount": 10.0
                }
            }

            # Mock existing commission check
            with patch.object(payment_commission_service, '_check_existing_commission', return_value=None):
                await payment_commission_service.process_payment_approval(
                    transaction_id=456,
                    payment_data=sample_payment_data,
                    webhook_event_id=789
                )

                # Verify commission was created with metadata
                commission_call = mock_db.add.call_args[0][0]
                assert commission_call.metadata["payment_gateway"] == "wompi"
                assert commission_call.metadata["payment_reference"] == "ORDER_123_20231201120000"
                assert commission_call.metadata["payment_id"] == "trx_test_12345"
                assert commission_call.metadata["webhook_event_id"] == 789
                assert "processed_at" in commission_call.metadata

    @pytest.mark.asyncio
    async def test_post_commission_actions(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test post-commission creation actions"""
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result

        # Mock commission service
        with patch.object(payment_commission_service, 'commission_service') as mock_comm_service:
            mock_comm_service.calculate_order_commission.return_value = {
                "success": True,
                "commission": {
                    "commission_rate": 0.1,
                    "commission_amount": 10.0,
                    "vendor_amount": 90.0,
                    "platform_amount": 10.0
                }
            }

            # Mock existing commission check
            with patch.object(payment_commission_service, '_check_existing_commission', return_value=None):
                # Mock post-commission actions
                with patch.object(payment_commission_service, '_create_vendor_notification') as mock_notify, \
                     patch.object(payment_commission_service, '_update_vendor_metrics') as mock_metrics:

                    await payment_commission_service.process_payment_approval(
                        transaction_id=456,
                        payment_data=sample_payment_data
                    )

                    # Verify post-commission actions were called
                    mock_notify.assert_called_once()
                    mock_metrics.assert_called_once()

                    # Verify order metadata was updated
                    assert sample_transaction.order.metadata["commission_id"] is not None
                    assert "commission_calculated_at" in sample_transaction.order.metadata
                    assert "vendor_payout_amount" in sample_transaction.order.metadata


class TestPaymentCommissionErrorHandling:
    """Test error handling in payment commission service"""

    @pytest.fixture
    def payment_commission_service(self, mock_db):
        """Create PaymentCommissionService instance"""
        return PaymentCommissionService(mock_db)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.refresh = AsyncMock()
        db.add = Mock()
        return db

    @pytest.mark.asyncio
    async def test_database_error_handling(
        self,
        payment_commission_service,
        mock_db
    ):
        """Test handling of database errors"""
        # Mock database error
        mock_db.execute.side_effect = Exception("Database connection failed")

        with pytest.raises(PaymentCommissionError, match="Commission processing failed"):
            await payment_commission_service.process_payment_approval(
                transaction_id=456,
                payment_data={"id": "test"},
                webhook_event_id=789
            )

    @pytest.mark.asyncio
    async def test_commit_failure_rollback(
        self,
        payment_commission_service,
        mock_db,
        sample_transaction,
        sample_payment_data
    ):
        """Test rollback on commit failure"""
        # Mock successful query but failed commit
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_transaction
        mock_db.execute.return_value = mock_result
        mock_db.commit.side_effect = Exception("Commit failed")

        with patch.object(payment_commission_service, 'commission_service') as mock_comm_service:
            mock_comm_service.calculate_order_commission.return_value = {
                "success": True,
                "commission": {"commission_rate": 0.1, "commission_amount": 10.0, "vendor_amount": 90.0, "platform_amount": 10.0}
            }

            with patch.object(payment_commission_service, '_check_existing_commission', return_value=None):
                with pytest.raises(PaymentCommissionError):
                    await payment_commission_service.process_payment_approval(
                        transaction_id=456,
                        payment_data=sample_payment_data
                    )

                mock_db.rollback.assert_called_once()

    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction"""
        order = Mock(spec=Order)
        order.id = 123
        order.total_amount = 100.0
        order.status = OrderStatus.CONFIRMED
        order.vendor_id = 1
        order.buyer_id = 2
        order.metadata = {}

        transaction = Mock(spec=Transaction)
        transaction.id = 456
        transaction.order = order
        transaction.status = PaymentStatus.APPROVED
        return transaction

    @pytest.fixture
    def sample_payment_data(self):
        """Create sample payment data"""
        return {
            "id": "trx_test_12345",
            "reference": "ORDER_123_20231201120000",
            "status": "APPROVED",
            "amount_in_cents": 10000,
            "currency": "COP"
        }