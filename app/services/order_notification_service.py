"""
Order Notification Service for MeStore.

This service handles notifications for order status changes,
including email notifications to buyers and vendors.
"""

import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User
from app.models.product import Product

logger = logging.getLogger(__name__)


class OrderNotificationService:
    """Service for handling order status change notifications"""

    @staticmethod
    async def notify_status_change(
        db: AsyncSession,
        order_id: int,
        old_status: OrderStatus,
        new_status: OrderStatus,
        updated_by_user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Send notifications when order status changes.

        Args:
            db: Database session
            order_id: ID of the order
            old_status: Previous order status
            new_status: New order status
            updated_by_user_id: ID of user who made the change
            notes: Optional notes about the change

        Returns:
            bool: True if notifications were sent successfully
        """
        try:
            # Get order with related data
            result = await db.execute(
                select(Order)
                .options(
                    selectinload(Order.buyer),
                    selectinload(Order.items).selectinload(OrderItem.product)
                )
                .where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()

            if not order:
                logger.error(f"Order {order_id} not found for notification")
                return False

            # Send notification to buyer
            await OrderNotificationService._notify_buyer(
                order, old_status, new_status, notes
            )

            # Send notification to vendors (for orders containing their products)
            await OrderNotificationService._notify_vendors(
                db, order, old_status, new_status, notes
            )

            # Log the notification
            logger.info(
                f"Notifications sent for order {order.order_number} "
                f"status change: {old_status.value} -> {new_status.value}"
            )

            return True

        except Exception as e:
            logger.error(f"Error sending order notifications: {e}")
            return False

    @staticmethod
    async def _notify_buyer(
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus,
        notes: Optional[str] = None
    ):
        """Send notification to the buyer about order status change"""
        try:
            # Get status-specific message
            message = OrderNotificationService._get_buyer_message(
                order, old_status, new_status
            )

            # In a real implementation, this would send an email
            # For now, we'll just log the notification
            logger.info(
                f"BUYER NOTIFICATION - Order {order.order_number}:\n"
                f"To: {order.buyer.email}\n"
                f"Subject: Order Update - {order.order_number}\n"
                f"Message: {message}\n"
                f"Notes: {notes or 'None'}"
            )

            # TODO: Implement actual email sending using FastAPI-Mail or similar
            # await email_service.send_order_update_email(
            #     to_email=order.buyer.email,
            #     order=order,
            #     message=message,
            #     notes=notes
            # )

        except Exception as e:
            logger.error(f"Error notifying buyer for order {order.id}: {e}")

    @staticmethod
    async def _notify_vendors(
        db: AsyncSession,
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus,
        notes: Optional[str] = None
    ):
        """Send notifications to vendors with products in the order"""
        try:
            # Get unique vendors from order items
            vendor_ids = set()
            for item in order.items:
                if hasattr(item, 'product') and item.product.vendedor_id:
                    vendor_ids.add(item.product.vendedor_id)

            if not vendor_ids:
                return

            # Get vendor details
            result = await db.execute(
                select(User).where(User.id.in_(vendor_ids))
            )
            vendors = result.scalars().all()

            for vendor in vendors:
                # Get vendor-specific items
                vendor_items = [
                    item for item in order.items
                    if hasattr(item, 'product') and item.product.vendedor_id == vendor.id
                ]

                message = OrderNotificationService._get_vendor_message(
                    order, old_status, new_status, vendor_items
                )

                # Log notification (replace with actual email service)
                logger.info(
                    f"VENDOR NOTIFICATION - Order {order.order_number}:\n"
                    f"To: {vendor.email}\n"
                    f"Subject: Order Update - {order.order_number}\n"
                    f"Message: {message}\n"
                    f"Vendor Items: {len(vendor_items)}\n"
                    f"Notes: {notes or 'None'}"
                )

        except Exception as e:
            logger.error(f"Error notifying vendors for order {order.id}: {e}")

    @staticmethod
    def _get_buyer_message(
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus
    ) -> str:
        """Generate buyer-specific message based on status change"""
        messages = {
            OrderStatus.CONFIRMED: (
                f"Great news! Your order {order.order_number} has been confirmed "
                f"and payment has been processed. Your order is now being prepared."
            ),
            OrderStatus.PROCESSING: (
                f"Your order {order.order_number} is now being processed by our vendors. "
                f"We'll notify you when it ships."
            ),
            OrderStatus.SHIPPED: (
                f"Your order {order.order_number} has been shipped! "
                f"You can track its progress and expect delivery within 7 business days."
            ),
            OrderStatus.DELIVERED: (
                f"Your order {order.order_number} has been delivered. "
                f"Thank you for shopping with MeStore!"
            ),
            OrderStatus.CANCELLED: (
                f"Your order {order.order_number} has been cancelled. "
                f"If you have any questions, please contact customer support."
            )
        }

        return messages.get(
            new_status,
            f"Your order {order.order_number} status has been updated to {new_status.value}."
        )

    @staticmethod
    def _get_vendor_message(
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus,
        vendor_items: list
    ) -> str:
        """Generate vendor-specific message based on status change"""
        item_count = len(vendor_items)
        total_value = sum(item.total_price for item in vendor_items)

        messages = {
            OrderStatus.CONFIRMED: (
                f"New order received! Order {order.order_number} with {item_count} "
                f"of your items (${total_value:.2f}) has been confirmed and paid. "
                f"Please begin processing."
            ),
            OrderStatus.PROCESSING: (
                f"Order {order.order_number} is now being processed. "
                f"Please update the status when ready to ship."
            ),
            OrderStatus.SHIPPED: (
                f"Order {order.order_number} has been marked as shipped. "
                f"Thank you for fulfilling this order."
            ),
            OrderStatus.DELIVERED: (
                f"Order {order.order_number} has been delivered successfully. "
                f"Commission will be processed shortly."
            ),
            OrderStatus.CANCELLED: (
                f"Order {order.order_number} has been cancelled. "
                f"No further action is required."
            )
        }

        return messages.get(
            new_status,
            f"Order {order.order_number} status updated to {new_status.value}."
        )


# Service instance
order_notification_service = OrderNotificationService()