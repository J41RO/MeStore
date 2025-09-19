"""
Payment Commission Integration Service

This service integrates the payment processing system with commission calculations.
When a payment is approved, it automatically triggers commission calculations
for the associated order, ensuring vendor commissions are properly tracked.
"""

import logging
import asyncio
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus, Transaction
from app.models.payment import Payment, WebhookEvent
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.user import User
from app.services.commission_service import CommissionService

logger = logging.getLogger(__name__)
commission_logger = logging.getLogger(f"{__name__}.commission")
audit_logger = logging.getLogger(f"{__name__}.audit")


class PaymentCommissionError(Exception):
    """Exception raised for payment commission processing errors"""
    pass


class PaymentCommissionService:
    """Service to handle commission calculations triggered by payment events"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.commission_service = CommissionService()

    async def process_payment_approval(
        self,
        transaction_id: int,
        payment_data: Dict[str, Any],
        webhook_event_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process commission calculations when a payment is approved

        Args:
            transaction_id: The transaction that was approved
            payment_data: Payment data from the webhook
            webhook_event_id: Associated webhook event ID for audit trail

        Returns:
            Dict containing commission processing results
        """
        try:
            # Get transaction with order and related info
            result = await self.db.execute(
                select(Transaction)
                .options(
                    selectinload(Transaction.order).selectinload(Order.items),
                    selectinload(Transaction.order).selectinload(Order.buyer)
                )
                .where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()

            if not transaction:
                raise PaymentCommissionError(f"Transaction {transaction_id} not found")

            order = transaction.order
            if not order:
                raise PaymentCommissionError(f"No order associated with transaction {transaction_id}")

            # Validate order state for commission calculation
            if order.status != OrderStatus.CONFIRMED:
                commission_logger.warning(
                    f"Order {order.id} not in confirmed state for commission calculation",
                    extra={
                        "order_id": order.id,
                        "order_status": order.status.value,
                        "transaction_id": transaction_id
                    }
                )
                return {
                    "success": False,
                    "message": f"Order status {order.status.value} not eligible for commission calculation"
                }

            # Check if commission already exists
            existing_commission = await self._check_existing_commission(order.id)
            if existing_commission:
                commission_logger.info(
                    f"Commission already exists for order {order.id}",
                    extra={
                        "order_id": order.id,
                        "commission_id": existing_commission.id,
                        "commission_status": existing_commission.status.value
                    }
                )
                return {
                    "success": True,
                    "message": "Commission already calculated",
                    "commission_id": existing_commission.id,
                    "amount": existing_commission.commission_amount
                }

            # Calculate and create commission
            commission_result = await self._calculate_and_create_commission(
                order=order,
                transaction=transaction,
                payment_data=payment_data,
                webhook_event_id=webhook_event_id
            )

            audit_logger.info(
                "Payment commission processing completed",
                extra={
                    "order_id": order.id,
                    "transaction_id": transaction_id,
                    "commission_id": commission_result.get("commission_id"),
                    "vendor_amount": commission_result.get("vendor_amount"),
                    "platform_amount": commission_result.get("platform_amount"),
                    "webhook_event_id": webhook_event_id
                }
            )

            return commission_result

        except Exception as e:
            logger.error(
                f"Error processing payment commission for transaction {transaction_id}: {e}",
                extra={
                    "transaction_id": transaction_id,
                    "webhook_event_id": webhook_event_id,
                    "error": str(e)
                }
            )
            raise PaymentCommissionError(f"Commission processing failed: {e}")

    async def _check_existing_commission(self, order_id: int) -> Optional[Commission]:
        """Check if commission already exists for the order"""
        result = await self.db.execute(
            select(Commission).where(Commission.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def _calculate_and_create_commission(
        self,
        order: Order,
        transaction: Transaction,
        payment_data: Dict[str, Any],
        webhook_event_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate and create commission for the approved payment"""
        try:
            # Use the existing commission service to calculate commission
            # Note: This is a placeholder - we'll implement a simpler calculation for now
            # In a real system, integrate with the actual commission service
            commission_calculation = self._calculate_simple_commission(order)

            if not commission_calculation.get("success"):
                raise PaymentCommissionError(
                    f"Commission calculation failed: {commission_calculation.get('error')}"
                )

            commission_data = commission_calculation.get("commission", {})

            # Get vendor_id - for now, use a placeholder since Order model doesn't have direct vendor relationship
            # In a real system, this would be determined from the order items or business logic
            vendor_id = getattr(order, 'vendor_id', None)
            if not vendor_id and hasattr(order, 'items') and order.items:
                # Try to get vendor from first item if available
                vendor_id = getattr(order.items[0], 'vendor_id', None) if order.items else None

            # Create commission record with payment integration metadata
            commission = Commission(
                order_id=order.id,
                vendor_id=vendor_id,
                buyer_id=order.buyer_id,
                transaction_id=transaction.id,
                commission_type=CommissionType.STANDARD,
                base_amount=Decimal(str(order.total_amount)),
                commission_rate=Decimal(str(commission_data.get("commission_rate", "0.0"))),
                commission_amount=Decimal(str(commission_data.get("commission_amount", "0.0"))),
                vendor_amount=Decimal(str(commission_data.get("vendor_amount", "0.0"))),
                platform_amount=Decimal(str(commission_data.get("platform_amount", "0.0"))),
                status=CommissionStatus.PENDING,
                metadata={
                    "payment_gateway": "wompi",
                    "payment_reference": payment_data.get("reference"),
                    "payment_id": payment_data.get("id"),
                    "payment_amount_cents": payment_data.get("amount_in_cents"),
                    "payment_currency": payment_data.get("currency", "COP"),
                    "payment_method": payment_data.get("payment_method", {}),
                    "webhook_event_id": webhook_event_id,
                    "processed_at": datetime.utcnow().isoformat(),
                    "calculation_details": commission_data
                }
            )

            self.db.add(commission)
            await self.db.commit()
            await self.db.refresh(commission)

            commission_logger.info(
                "Commission created for approved payment",
                extra={
                    "commission_id": commission.id,
                    "order_id": order.id,
                    "vendor_id": order.vendor_id,
                    "commission_amount": float(commission.commission_amount),
                    "vendor_amount": float(commission.vendor_amount),
                    "platform_amount": float(commission.platform_amount),
                    "commission_rate": float(commission.commission_rate)
                }
            )

            # Trigger additional processing if needed
            await self._trigger_post_commission_actions(commission, order, transaction)

            return {
                "success": True,
                "commission_id": commission.id,
                "commission_amount": commission.commission_amount,
                "vendor_amount": commission.vendor_amount,
                "platform_amount": commission.platform_amount,
                "commission_rate": commission.commission_rate,
                "status": commission.status.value
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating commission for order {order.id}: {e}")
            raise PaymentCommissionError(f"Commission creation failed: {e}")

    async def _trigger_post_commission_actions(
        self,
        commission: Commission,
        order: Order,
        transaction: Transaction
    ) -> None:
        """Trigger any post-commission creation actions"""
        try:
            # 1. Update order metadata with commission info
            if order.metadata:
                order.metadata.update({
                    "commission_id": commission.id,
                    "commission_calculated_at": datetime.utcnow().isoformat(),
                    "vendor_payout_amount": float(commission.vendor_amount),
                    "platform_fee": float(commission.platform_amount)
                })
            else:
                order.metadata = {
                    "commission_id": commission.id,
                    "commission_calculated_at": datetime.utcnow().isoformat(),
                    "vendor_payout_amount": float(commission.vendor_amount),
                    "platform_fee": float(commission.platform_amount)
                }

            # 2. Create vendor notification (placeholder for notification service)
            await self._create_vendor_notification(commission, order)

            # 3. Update vendor metrics (placeholder for analytics service)
            await self._update_vendor_metrics(commission, order)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error in post-commission actions: {e}")
            # Don't fail the main commission creation for notification errors

    async def _create_vendor_notification(self, commission: Commission, order: Order) -> None:
        """Create notification for vendor about commission"""
        # This would integrate with the notification service
        commission_logger.info(
            "Vendor commission notification triggered",
            extra={
                "commission_id": commission.id,
                "vendor_id": commission.vendor_id,
                "order_id": order.id,
                "commission_amount": float(commission.commission_amount)
            }
        )

    async def _update_vendor_metrics(self, commission: Commission, order: Order) -> None:
        """Update vendor performance metrics"""
        # This would integrate with analytics/metrics service
        commission_logger.info(
            "Vendor metrics update triggered",
            extra={
                "commission_id": commission.id,
                "vendor_id": commission.vendor_id,
                "order_value": float(order.total_amount),
                "commission_earned": float(commission.vendor_amount)
            }
        )

    async def process_payment_refund(
        self,
        transaction_id: int,
        refund_data: Dict[str, Any],
        webhook_event_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process commission adjustments when a payment is refunded

        Args:
            transaction_id: The transaction that was refunded
            refund_data: Refund data from the webhook
            webhook_event_id: Associated webhook event ID for audit trail

        Returns:
            Dict containing commission adjustment results
        """
        try:
            # Get commission associated with the transaction
            result = await self.db.execute(
                select(Commission)
                .options(selectinload(Commission.order))
                .where(Commission.transaction_id == transaction_id)
            )
            commission = result.scalar_one_or_none()

            if not commission:
                commission_logger.warning(
                    f"No commission found for refunded transaction {transaction_id}",
                    extra={"transaction_id": transaction_id, "webhook_event_id": webhook_event_id}
                )
                return {
                    "success": True,
                    "message": "No commission to adjust for refund"
                }

            # Create refund commission entry or adjust existing
            refund_amount = Decimal(str(refund_data.get("amount_in_cents", 0))) / 100

            # Calculate proportional commission adjustment
            refund_ratio = refund_amount / commission.base_amount if commission.base_amount > 0 else Decimal("0")
            adjusted_commission_amount = commission.commission_amount * refund_ratio
            adjusted_vendor_amount = commission.vendor_amount * refund_ratio
            adjusted_platform_amount = commission.platform_amount * refund_ratio

            # Create adjustment commission record
            refund_commission = Commission(
                order_id=commission.order_id,
                vendor_id=commission.vendor_id,
                buyer_id=commission.buyer_id,
                transaction_id=transaction_id,
                commission_type=CommissionType.STANDARD,  # Use STANDARD for refund adjustments
                base_amount=-refund_amount,  # Negative for refund
                commission_rate=commission.commission_rate,
                commission_amount=-adjusted_commission_amount,
                vendor_amount=-adjusted_vendor_amount,
                platform_amount=-adjusted_platform_amount,
                status=CommissionStatus.PENDING,
                parent_commission_id=commission.id,
                metadata={
                    "refund_gateway": "wompi",
                    "refund_reference": refund_data.get("reference"),
                    "refund_id": refund_data.get("id"),
                    "refund_amount_cents": refund_data.get("amount_in_cents"),
                    "original_commission_id": commission.id,
                    "webhook_event_id": webhook_event_id,
                    "processed_at": datetime.utcnow().isoformat(),
                    "refund_ratio": float(refund_ratio)
                }
            )

            self.db.add(refund_commission)
            await self.db.commit()
            await self.db.refresh(refund_commission)

            audit_logger.info(
                "Commission refund adjustment created",
                extra={
                    "refund_commission_id": refund_commission.id,
                    "original_commission_id": commission.id,
                    "transaction_id": transaction_id,
                    "refund_amount": float(refund_amount),
                    "commission_adjustment": float(adjusted_commission_amount),
                    "vendor_adjustment": float(adjusted_vendor_amount)
                }
            )

            return {
                "success": True,
                "refund_commission_id": refund_commission.id,
                "original_commission_id": commission.id,
                "refund_amount": refund_amount,
                "commission_adjustment": adjusted_commission_amount,
                "vendor_adjustment": adjusted_vendor_amount,
                "platform_adjustment": adjusted_platform_amount
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing commission refund for transaction {transaction_id}: {e}")
            raise PaymentCommissionError(f"Commission refund processing failed: {e}")

    async def get_commission_summary(
        self,
        vendor_id: Optional[int] = None,
        order_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get commission summary for reporting and analytics

        Args:
            vendor_id: Filter by vendor ID
            order_id: Filter by specific order ID
            date_from: Start date for the summary period
            date_to: End date for the summary period

        Returns:
            Dict containing commission summary data
        """
        try:
            query = select(Commission)
            filters = []

            if vendor_id:
                filters.append(Commission.vendor_id == vendor_id)
            if order_id:
                filters.append(Commission.order_id == order_id)
            if date_from:
                filters.append(Commission.created_at >= date_from)
            if date_to:
                filters.append(Commission.created_at <= date_to)

            if filters:
                query = query.where(*filters)

            result = await self.db.execute(query)
            commissions = result.scalars().all()

            # Calculate summary statistics
            total_commission = sum(c.commission_amount for c in commissions if c.commission_amount)
            total_vendor_amount = sum(c.vendor_amount for c in commissions if c.vendor_amount)
            total_platform_amount = sum(c.platform_amount for c in commissions if c.platform_amount)
            total_base_amount = sum(c.base_amount for c in commissions if c.base_amount)

            commission_by_status = {}
            commission_by_type = {}

            for commission in commissions:
                # By status
                status = commission.status.value
                if status not in commission_by_status:
                    commission_by_status[status] = {"count": 0, "amount": Decimal("0")}
                commission_by_status[status]["count"] += 1
                commission_by_status[status]["amount"] += commission.commission_amount or Decimal("0")

                # By type
                comm_type = commission.commission_type.value if commission.commission_type else "unknown"
                if comm_type not in commission_by_type:
                    commission_by_type[comm_type] = {"count": 0, "amount": Decimal("0")}
                commission_by_type[comm_type]["count"] += 1
                commission_by_type[comm_type]["amount"] += commission.commission_amount or Decimal("0")

            return {
                "summary": {
                    "total_commissions": len(commissions),
                    "total_commission_amount": total_commission,
                    "total_vendor_amount": total_vendor_amount,
                    "total_platform_amount": total_platform_amount,
                    "total_base_amount": total_base_amount,
                    "average_commission_rate": total_commission / total_base_amount if total_base_amount > 0 else Decimal("0")
                },
                "by_status": {
                    status: {
                        "count": data["count"],
                        "amount": float(data["amount"])
                    }
                    for status, data in commission_by_status.items()
                },
                "by_type": {
                    comm_type: {
                        "count": data["count"],
                        "amount": float(data["amount"])
                    }
                    for comm_type, data in commission_by_type.items()
                },
                "filters_applied": {
                    "vendor_id": vendor_id,
                    "order_id": order_id,
                    "date_from": date_from.isoformat() if date_from else None,
                    "date_to": date_to.isoformat() if date_to else None
                }
            }

        except Exception as e:
            logger.error(f"Error generating commission summary: {e}")
            raise PaymentCommissionError(f"Commission summary generation failed: {e}")

    def _calculate_simple_commission(self, order: Order) -> Dict[str, Any]:
        """
        Simple commission calculation for payment integration

        This is a placeholder implementation. In production, this would
        integrate with the full commission service or business rules engine.
        """
        try:
            # Default commission rate (10%)
            commission_rate = Decimal("0.1")
            base_amount = Decimal(str(order.total_amount))

            # Calculate commission amounts
            commission_amount = base_amount * commission_rate
            platform_amount = commission_amount
            vendor_amount = base_amount - commission_amount

            return {
                "success": True,
                "commission": {
                    "commission_rate": float(commission_rate),
                    "commission_amount": float(commission_amount),
                    "vendor_amount": float(vendor_amount),
                    "platform_amount": float(platform_amount),
                    "base_amount": float(base_amount),
                    "calculation_method": "simple_payment_integration"
                }
            }

        except Exception as e:
            logger.error(f"Error in simple commission calculation: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def get_payment_commission_service(db: AsyncSession) -> PaymentCommissionService:
    """Factory function to create PaymentCommissionService instance"""
    return PaymentCommissionService(db)