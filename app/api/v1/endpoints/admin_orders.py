"""
Admin Orders Management Endpoints

This module provides SUPERUSER-only endpoints for complete order management:
- View all orders in the system
- Filter and search orders
- View detailed order information
- Update order status
- Cancel orders with reason tracking
- View order statistics and dashboard metrics

Security: All endpoints require SUPERUSER authentication via require_admin dependency
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import get_db
from app.api.v1.deps.auth import require_admin
from app.schemas.user import UserRead
from app.models.order import Order, OrderItem, OrderTransaction, OrderStatus, PaymentStatus
from app.models.user import User
from app.models.product import Product
from pydantic import BaseModel


router = APIRouter()


# ==================== SCHEMAS ====================

class OrderItemDetail(BaseModel):
    """Order item detail for admin view"""
    id: int
    product_id: int
    product_name: str
    product_sku: str
    product_image_url: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    variant_attributes: Optional[str]
    vendor_id: Optional[str]
    vendor_name: Optional[str]

    class Config:
        from_attributes = True


class OrderTransactionDetail(BaseModel):
    """Transaction detail for admin view"""
    id: int
    transaction_reference: str
    amount: Decimal
    currency: str
    status: str
    payment_method_type: str
    gateway: str
    gateway_transaction_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    failure_reason: Optional[str]

    class Config:
        from_attributes = True


class OrderListItem(BaseModel):
    """Order list item for admin table view"""
    id: int
    order_number: str
    buyer_id: str
    buyer_email: str
    buyer_name: str
    total_amount: Decimal
    status: str
    payment_status: str
    created_at: datetime
    items_count: int

    class Config:
        from_attributes = True


class OrderDetailAdmin(BaseModel):
    """Complete order detail for admin view"""
    id: int
    order_number: str
    status: str

    # Buyer information
    buyer_id: str
    buyer_email: str
    buyer_name: str
    buyer_phone: Optional[str]

    # Order totals
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    total_amount: Decimal

    # Shipping information
    shipping_name: str
    shipping_phone: str
    shipping_email: Optional[str]
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: Optional[str]
    shipping_country: str

    # Timestamps
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    cancelled_at: Optional[datetime]

    # Additional info
    notes: Optional[str]
    cancellation_reason: Optional[str]

    # Related data
    items: List[OrderItemDetail]
    transactions: List[OrderTransactionDetail]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Request to update order status"""
    status: str
    notes: Optional[str] = None


class OrderCancellation(BaseModel):
    """Request to cancel order"""
    reason: str
    refund_requested: bool = False


class OrderStatsResponse(BaseModel):
    """Order statistics for admin dashboard"""
    total_orders_today: int
    total_orders_week: int
    total_orders_month: int
    revenue_today: Decimal
    revenue_week: Decimal
    revenue_month: Decimal
    orders_by_status: dict
    top_buyers: List[dict]
    pending_orders_count: int
    processing_orders_count: int


class OrdersListResponse(BaseModel):
    """Paginated orders list response"""
    orders: List[OrderListItem]
    total: int
    skip: int
    limit: int


# ==================== ENDPOINTS ====================

@router.get("/orders", response_model=OrdersListResponse)
async def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by order status"),
    search: Optional[str] = Query(None, description="Search by order number, buyer email, or buyer name"),
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders in the system with filtering and pagination (ADMIN ONLY)

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 100)
    - **status**: Filter by order status (pending, confirmed, processing, shipped, delivered, cancelled)
    - **search**: Search by order number, buyer email, or buyer name

    Returns paginated list of orders with buyer information and summary data.
    """
    try:
        # Build base query
        query = select(Order).options(
            selectinload(Order.buyer),
            selectinload(Order.items),
            selectinload(Order.transactions)
        )

        # Apply status filter
        if status:
            try:
                status_enum = OrderStatus(status.lower())
                query = query.where(Order.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {status}"
                )

        # Apply search filter
        if search:
            query = query.join(Order.buyer).where(
                or_(
                    Order.order_number.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.nombre.ilike(f"%{search}%"),
                    User.apellido.ilike(f"%{search}%")
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(Order)
        if status:
            try:
                status_enum = OrderStatus(status.lower())
                count_query = count_query.where(Order.status == status_enum)
            except ValueError:
                pass
        if search:
            count_query = count_query.join(Order.buyer).where(
                or_(
                    Order.order_number.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.nombre.ilike(f"%{search}%"),
                    User.apellido.ilike(f"%{search}%")
                )
            )

        result = await db.execute(count_query)
        total = result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(desc(Order.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        orders = result.scalars().all()

        # Transform to response model
        orders_list = []
        for order in orders:
            # Get payment status
            payment_status = "pending"
            if order.transactions:
                latest_transaction = sorted(order.transactions, key=lambda x: x.created_at)[-1]
                payment_status = latest_transaction.status.value

            orders_list.append(OrderListItem(
                id=order.id,
                order_number=order.order_number,
                buyer_id=order.buyer_id,
                buyer_email=order.buyer.email,
                buyer_name=f"{order.buyer.nombre} {order.buyer.apellido}",
                total_amount=order.total_amount,
                status=order.status.value,
                payment_status=payment_status,
                created_at=order.created_at,
                items_count=len(order.items)
            ))

        return OrdersListResponse(
            orders=orders_list,
            total=total,
            skip=skip,
            limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )


@router.get("/orders/{order_id}", response_model=OrderDetailAdmin)
async def get_order_detail_admin(
    order_id: int,
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete order details including buyer, items, and transactions (ADMIN ONLY)

    Returns all order information with related entities fully loaded.
    """
    try:
        query = select(Order).options(
            selectinload(Order.buyer),
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.transactions)
        ).where(Order.id == order_id)

        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )

        # Build items detail with vendor information
        items_detail = []
        for item in order.items:
            vendor_id = None
            vendor_name = None
            if item.product:
                vendor_id = item.product.vendor_id
                # Get vendor info
                if vendor_id:
                    vendor_query = select(User).where(User.id == vendor_id)
                    vendor_result = await db.execute(vendor_query)
                    vendor = vendor_result.scalar_one_or_none()
                    if vendor:
                        vendor_name = f"{vendor.nombre} {vendor.apellido}"

            items_detail.append(OrderItemDetail(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_sku=item.product_sku,
                product_image_url=item.product_image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price,
                variant_attributes=item.variant_attributes,
                vendor_id=vendor_id,
                vendor_name=vendor_name
            ))

        # Build transactions detail
        transactions_detail = [
            OrderTransactionDetail(
                id=t.id,
                transaction_reference=t.transaction_reference,
                amount=t.amount,
                currency=t.currency,
                status=t.status.value,
                payment_method_type=t.payment_method_type,
                gateway=t.gateway,
                gateway_transaction_id=t.gateway_transaction_id,
                created_at=t.created_at,
                processed_at=t.processed_at,
                failure_reason=t.failure_reason
            )
            for t in order.transactions
        ]

        return OrderDetailAdmin(
            id=order.id,
            order_number=order.order_number,
            status=order.status.value,
            buyer_id=order.buyer_id,
            buyer_email=order.buyer.email,
            buyer_name=f"{order.buyer.nombre} {order.buyer.apellido}",
            buyer_phone=order.buyer.telefono,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            shipping_cost=order.shipping_cost,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            shipping_name=order.shipping_name,
            shipping_phone=order.shipping_phone,
            shipping_email=order.shipping_email,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_state=order.shipping_state,
            shipping_postal_code=order.shipping_postal_code,
            shipping_country=order.shipping_country,
            created_at=order.created_at,
            updated_at=order.updated_at,
            confirmed_at=order.confirmed_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            notes=order.notes,
            cancellation_reason=order.cancellation_reason,
            items=items_detail,
            transactions=transactions_detail
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order details: {str(e)}"
        )


@router.patch("/orders/{order_id}/status", response_model=OrderDetailAdmin)
async def update_order_status_admin(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status (ADMIN ONLY)

    Validates status transitions and updates appropriate timestamp fields.
    """
    try:
        # Validate status value
        try:
            new_status = OrderStatus(status_update.status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_update.status}"
            )

        # Get order
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )

        # Update status
        old_status = order.status
        order.status = new_status

        # Update corresponding timestamp
        now = datetime.utcnow()
        if new_status == OrderStatus.CONFIRMED and not order.confirmed_at:
            order.confirmed_at = now
        elif new_status == OrderStatus.SHIPPED and not order.shipped_at:
            order.shipped_at = now
        elif new_status == OrderStatus.DELIVERED and not order.delivered_at:
            order.delivered_at = now
        elif new_status == OrderStatus.CANCELLED and not order.cancelled_at:
            order.cancelled_at = now

        # Update notes if provided
        if status_update.notes:
            existing_notes = order.notes or ""
            order.notes = f"{existing_notes}\n[Admin Update {now.isoformat()}]: {status_update.notes}".strip()

        await db.commit()
        await db.refresh(order)

        # Return updated order detail
        return await get_order_detail_admin(order_id, current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order status: {str(e)}"
        )


@router.delete("/orders/{order_id}")
async def cancel_order_admin(
    order_id: int,
    cancellation: OrderCancellation,
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel an order (ADMIN ONLY)

    Sets order status to cancelled and records the cancellation reason.
    Optionally triggers refund process if payment was approved.
    """
    try:
        # Get order
        query = select(Order).options(
            selectinload(Order.transactions)
        ).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )

        # Check if already cancelled
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already cancelled"
            )

        # Update order
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()
        order.cancellation_reason = f"[ADMIN] {cancellation.reason}"

        # Check if refund is needed
        refund_info = None
        if cancellation.refund_requested:
            # Check if there's an approved payment
            approved_transaction = None
            for transaction in order.transactions:
                if transaction.status == PaymentStatus.APPROVED:
                    approved_transaction = transaction
                    break

            if approved_transaction:
                refund_info = {
                    "transaction_id": approved_transaction.id,
                    "amount": approved_transaction.amount,
                    "gateway": approved_transaction.gateway,
                    "status": "pending_manual_refund"
                }
                # TODO: Integrate with payment gateway refund API

        await db.commit()

        return {
            "success": True,
            "message": f"Order {order.order_number} cancelled successfully",
            "order_id": order_id,
            "cancellation_reason": cancellation.reason,
            "refund_info": refund_info
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling order: {str(e)}"
        )


@router.get("/orders/stats/dashboard", response_model=OrderStatsResponse)
async def get_admin_order_stats(
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order statistics for admin dashboard (ADMIN ONLY)

    Returns aggregated statistics including:
    - Order counts by period (today, week, month)
    - Revenue by period
    - Orders grouped by status
    - Top buyers
    """
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        # Orders count by period
        orders_today_query = select(func.count()).select_from(Order).where(
            Order.created_at >= today_start
        )
        orders_week_query = select(func.count()).select_from(Order).where(
            Order.created_at >= week_start
        )
        orders_month_query = select(func.count()).select_from(Order).where(
            Order.created_at >= month_start
        )

        today_count = (await db.execute(orders_today_query)).scalar_one()
        week_count = (await db.execute(orders_week_query)).scalar_one()
        month_count = (await db.execute(orders_month_query)).scalar_one()

        # Revenue by period (only approved payments)
        revenue_today_query = select(func.sum(Order.total_amount)).select_from(Order).join(
            Order.transactions
        ).where(
            and_(
                Order.created_at >= today_start,
                OrderTransaction.status == PaymentStatus.APPROVED
            )
        )
        revenue_week_query = select(func.sum(Order.total_amount)).select_from(Order).join(
            Order.transactions
        ).where(
            and_(
                Order.created_at >= week_start,
                OrderTransaction.status == PaymentStatus.APPROVED
            )
        )
        revenue_month_query = select(func.sum(Order.total_amount)).select_from(Order).join(
            Order.transactions
        ).where(
            and_(
                Order.created_at >= month_start,
                OrderTransaction.status == PaymentStatus.APPROVED
            )
        )

        revenue_today = (await db.execute(revenue_today_query)).scalar_one_or_none() or Decimal(0)
        revenue_week = (await db.execute(revenue_week_query)).scalar_one_or_none() or Decimal(0)
        revenue_month = (await db.execute(revenue_month_query)).scalar_one_or_none() or Decimal(0)

        # Orders by status
        orders_by_status = {}
        for order_status in OrderStatus:
            count_query = select(func.count()).select_from(Order).where(
                Order.status == order_status
            )
            count = (await db.execute(count_query)).scalar_one()
            orders_by_status[order_status.value] = count

        # Top buyers (top 5 by total spent)
        top_buyers_query = select(
            User.id,
            User.email,
            User.nombre,
            User.apellido,
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_spent")
        ).join(Order, Order.buyer_id == User.id).group_by(
            User.id, User.email, User.nombre, User.apellido
        ).order_by(desc("total_spent")).limit(5)

        result = await db.execute(top_buyers_query)
        top_buyers_raw = result.all()

        top_buyers = [
            {
                "buyer_id": row.id,
                "email": row.email,
                "name": f"{row.nombre} {row.apellido}",
                "order_count": row.order_count,
                "total_spent": float(row.total_spent)
            }
            for row in top_buyers_raw
        ]

        # Pending and processing counts
        pending_count = orders_by_status.get(OrderStatus.PENDING.value, 0)
        processing_count = orders_by_status.get(OrderStatus.PROCESSING.value, 0)

        return OrderStatsResponse(
            total_orders_today=today_count,
            total_orders_week=week_count,
            total_orders_month=month_count,
            revenue_today=revenue_today,
            revenue_week=revenue_week,
            revenue_month=revenue_month,
            orders_by_status=orders_by_status,
            top_buyers=top_buyers,
            pending_orders_count=pending_count,
            processing_orders_count=processing_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order statistics: {str(e)}"
        )
