"""
VENDOR ORDERS ENDPOINT - Quick functional implementation
Allows vendors to view and manage their orders
Author: backend-framework-ai
Date: 2025-10-03
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.api.v1.deps.auth import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# SCHEMAS (Simple dict-based responses for speed)
# ============================================================================

def order_item_to_dict(item: OrderItem) -> dict:
    """Convert OrderItem to dict with vendor-relevant info"""
    return {
        "id": item.id,
        "product_id": item.product_id,
        "product_name": item.product_name,
        "product_sku": item.product_sku,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price),
        "total_price": float(item.total_price),
        "variant_attributes": item.variant_attributes,
        "created_at": item.created_at.isoformat() if item.created_at else None
    }


def order_to_dict(order: Order, vendor_items: List[OrderItem]) -> dict:
    """Convert Order to dict with only vendor's items"""
    vendor_total = sum(float(item.total_price) for item in vendor_items)

    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
        "total_amount": float(order.total_amount),
        "vendor_items_total": vendor_total,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
        "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "shipping_address": order.shipping_address,
        "shipping_city": order.shipping_city,
        "shipping_state": order.shipping_state,
        "shipping_name": order.shipping_name,
        "shipping_phone": order.shipping_phone,
        "items": [order_item_to_dict(item) for item in vendor_items],
        "items_count": len(vendor_items)
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/orders")
async def get_vendor_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    skip: int = Query(0, ge=0, description="Skip records for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Limit records"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders containing products from the authenticated vendor.

    Returns orders with vendor's items only, not all items in the order.
    """
    try:
        # Build query - get orders that have items from vendor's products
        query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .where(Product.vendedor_id == current_user.id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product),
                selectinload(Order.buyer)
            )
            .distinct()
        )

        # Apply status filter if provided
        if status:
            try:
                status_enum = OrderStatus[status.upper()]
                query = query.where(Order.status == status_enum)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}. Valid values: {', '.join([s.name for s in OrderStatus])}"
                )

        # Order by most recent first
        query = query.order_by(Order.created_at.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        orders = result.unique().scalars().all()

        # Filter items to show only vendor's products
        response_orders = []
        for order in orders:
            vendor_items = [
                item for item in order.items
                if item.product and item.product.vendedor_id == current_user.id
            ]
            if vendor_items:  # Only include orders with vendor items
                response_orders.append(order_to_dict(order, vendor_items))

        return {
            "total": len(response_orders),
            "skip": skip,
            "limit": limit,
            "orders": response_orders
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vendor orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )


@router.get("/orders/{order_id}")
async def get_vendor_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific order (vendor's items only).
    """
    try:
        # Get order with items
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product),
                selectinload(Order.buyer)
            )
        )

        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )

        # Filter to vendor's items only
        vendor_items = [
            item for item in order.items
            if item.product and item.product.vendedor_id == current_user.id
        ]

        if not vendor_items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this order"
            )

        return order_to_dict(order, vendor_items)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order: {str(e)}"
        )


@router.patch("/orders/{order_id}/items/{item_id}/status")
async def update_vendor_item_status(
    order_id: int,
    item_id: int,
    status_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update preparation status of a specific order item.

    Request body: {"status": "preparing" | "ready_to_ship"}

    Note: This is a simplified implementation. For production, add:
    - Dedicated status field in OrderItem model
    - More granular status options
    - Validation rules
    """
    try:
        # Validate status value
        new_status = status_update.get("status")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'status' field in request body"
            )

        allowed_statuses = ["preparing", "ready_to_ship"]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed: {', '.join(allowed_statuses)}"
            )

        # Get order item with product
        query = (
            select(OrderItem)
            .where(
                and_(
                    OrderItem.id == item_id,
                    OrderItem.order_id == order_id
                )
            )
            .options(joinedload(OrderItem.product))
        )

        result = await db.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order item {item_id} not found in order {order_id}"
            )

        # Verify vendor ownership
        if not item.product or item.product.vendedor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this item"
            )

        # Store status in variant_attributes as JSON (temporary solution)
        # For production: add dedicated status field to OrderItem model
        import json
        current_attrs = json.loads(item.variant_attributes) if item.variant_attributes else {}
        current_attrs["vendor_status"] = new_status
        current_attrs["vendor_status_updated_at"] = datetime.utcnow().isoformat()
        item.variant_attributes = json.dumps(current_attrs)

        await db.commit()
        await db.refresh(item)

        return {
            "success": True,
            "item_id": item.id,
            "order_id": order_id,
            "new_status": new_status,
            "updated_at": datetime.utcnow().isoformat(),
            "message": f"Item status updated to {new_status}"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating item status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating status: {str(e)}"
        )


@router.get("/orders/stats/summary")
async def get_vendor_orders_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics of vendor's orders.
    Quick aggregation for dashboard display.
    """
    try:
        # Get all orders with vendor's products
        query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .where(Product.vendedor_id == current_user.id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product)
            )
            .distinct()
        )

        result = await db.execute(query)
        orders = result.unique().scalars().all()

        # Calculate stats
        stats = {
            "total_orders": 0,
            "total_items": 0,
            "total_revenue": 0.0,
            "by_status": {},
            "recent_orders": []
        }

        for order in orders:
            vendor_items = [
                item for item in order.items
                if item.product and item.product.vendedor_id == current_user.id
            ]

            if vendor_items:
                stats["total_orders"] += 1
                stats["total_items"] += len(vendor_items)
                vendor_total = sum(float(item.total_price) for item in vendor_items)
                stats["total_revenue"] += vendor_total

                # Count by status
                status_key = order.status.value if hasattr(order.status, 'value') else str(order.status)
                stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

        # Get 5 most recent orders
        recent = sorted(orders, key=lambda x: x.created_at, reverse=True)[:5]
        for order in recent:
            vendor_items = [
                item for item in order.items
                if item.product and item.product.vendedor_id == current_user.id
            ]
            if vendor_items:
                stats["recent_orders"].append({
                    "order_number": order.order_number,
                    "created_at": order.created_at.isoformat(),
                    "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
                    "items_count": len(vendor_items),
                    "total": sum(float(item.total_price) for item in vendor_items)
                })

        return stats

    except Exception as e:
        logger.error(f"Error getting vendor stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statistics: {str(e)}"
        )
