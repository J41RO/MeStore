"""
Shipping management endpoints for order tracking and delivery management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from datetime import datetime, timedelta
import secrets

from app.api.v1.deps.auth import require_admin, get_current_user
from app.database import get_async_db
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.schemas.shipping import (
    ShippingAssignment,
    ShippingLocationUpdate,
    ShippingInfo,
    TrackingResponse,
    ShippingEvent,
    ShippingStatus
)

router = APIRouter()


def generate_tracking_number() -> str:
    """
    Generate a unique tracking number.
    Format: SHIP-YYYYMMDDHHMMSS-RANDOM
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(4).upper()
    return f"SHIP-{timestamp}-{random_suffix}"


@router.post("/orders/{order_id}/shipping", response_model=Dict[str, Any])
async def assign_shipping(
    order_id: int,
    shipping_data: ShippingAssignment,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin)
):
    """
    Assign courier and generate tracking number for an order.
    Only admin users can assign shipping.
    """
    # Fetch order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Validate order status
    if order.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign shipping to order with status: {order.status.value}"
        )

    # Check if shipping already assigned
    if order.tracking_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shipping already assigned to this order"
        )

    # Generate tracking number
    tracking_number = generate_tracking_number()

    # Calculate estimated delivery
    estimated_delivery = datetime.now() + timedelta(days=shipping_data.estimated_days)

    # Update order
    order.tracking_number = tracking_number
    order.courier = shipping_data.courier
    order.estimated_delivery = estimated_delivery
    order.status = OrderStatus.SHIPPED
    order.shipped_at = datetime.now()

    # Initialize shipping events
    initial_event = {
        "timestamp": datetime.now().isoformat(),
        "status": ShippingStatus.IN_TRANSIT.value,
        "location": "Origin warehouse",
        "description": f"Package picked up by {shipping_data.courier}"
    }
    order.shipping_events = [initial_event]

    await db.commit()
    await db.refresh(order)

    return {
        "message": "Shipping assigned successfully",
        "tracking_number": tracking_number,
        "courier": shipping_data.courier,
        "estimated_delivery": estimated_delivery.isoformat(),
        "order_status": order.status.value
    }


@router.patch("/orders/{order_id}/shipping/location", response_model=Dict[str, Any])
async def update_shipping_location(
    order_id: int,
    location_data: ShippingLocationUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin)
):
    """
    Update shipping location and status.
    Only admin users can update shipping information.
    """
    # Fetch order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Validate order has shipping assigned
    if not order.tracking_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No shipping assigned to this order"
        )

    # Create new event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "status": location_data.status.value,
        "location": location_data.current_location,
        "description": location_data.description or ""
    }

    # Update shipping events
    current_events = order.shipping_events or []
    current_events.append(new_event)
    order.shipping_events = current_events

    # If delivered, update order status
    if location_data.status == ShippingStatus.DELIVERED:
        order.status = OrderStatus.DELIVERED
        order.delivered_at = datetime.now()

    await db.commit()
    await db.refresh(order)

    return {
        "message": "Shipping location updated successfully",
        "tracking_number": order.tracking_number,
        "current_location": location_data.current_location,
        "status": location_data.status.value,
        "order_status": order.status.value,
        "total_events": len(current_events)
    }


@router.get("/orders/{order_id}/shipping/tracking", response_model=TrackingResponse)
async def get_shipping_tracking(
    order_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get shipping tracking information for an order.
    Users can only view tracking for their own orders, admins can view all.
    """
    # Fetch order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Validate user can see this order
    if not current_user.is_superuser and order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this order"
        )

    # Parse shipping events
    shipping_events = []
    current_status = None
    if order.shipping_events:
        for event in order.shipping_events:
            shipping_events.append(ShippingEvent(
                timestamp=datetime.fromisoformat(event["timestamp"]),
                status=event["status"],
                location=event["location"],
                description=event.get("description", "")
            ))
        # Get latest status
        if shipping_events:
            current_status = shipping_events[-1].status

    # Build shipping info
    shipping_info = ShippingInfo(
        tracking_number=order.tracking_number,
        courier=order.courier,
        estimated_delivery=order.estimated_delivery,
        shipping_events=shipping_events,
        current_status=current_status
    )

    # Build response
    return TrackingResponse(
        order_number=order.order_number,
        order_status=order.status.value,
        shipping_info=shipping_info,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        created_at=order.created_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )


@router.get("/tracking/{tracking_number}", response_model=TrackingResponse)
async def track_by_tracking_number(
    tracking_number: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Public endpoint to track order by tracking number.
    No authentication required.
    """
    # Fetch order by tracking number
    result = await db.execute(
        select(Order).where(Order.tracking_number == tracking_number)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking number not found"
        )

    # Parse shipping events
    shipping_events = []
    current_status = None
    if order.shipping_events:
        for event in order.shipping_events:
            shipping_events.append(ShippingEvent(
                timestamp=datetime.fromisoformat(event["timestamp"]),
                status=event["status"],
                location=event["location"],
                description=event.get("description", "")
            ))
        if shipping_events:
            current_status = shipping_events[-1].status

    # Build shipping info
    shipping_info = ShippingInfo(
        tracking_number=order.tracking_number,
        courier=order.courier,
        estimated_delivery=order.estimated_delivery,
        shipping_events=shipping_events,
        current_status=current_status
    )

    # Build response (hide sensitive buyer info for public tracking)
    return TrackingResponse(
        order_number=order.order_number,
        order_status=order.status.value,
        shipping_info=shipping_info,
        shipping_address=f"{order.shipping_city}, {order.shipping_state}",  # Partial address only
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        created_at=order.created_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at
    )
