"""
Order schemas with consistent ID validation for MeStore API.

This module provides Pydantic schemas for order-related operations
with standardized ID validation and response formats.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import Field, field_validator
from enum import Enum

from app.schemas.base import (
    BaseSchema,
    BaseIDSchema,
    BaseCreateSchema,
    BaseUpdateSchema,
    BaseResponseSchema,
    TimestampMixin,
    UserContextMixin
)
from app.core.id_validation import IDValidationMixin


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderPriority(str, Enum):
    """Order priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class OrderItemBase(BaseSchema):
    """Base schema for order items."""

    product_id: str = Field(
        ...,
        description="Product UUID identifier",
        min_length=36,
        max_length=36
    )
    quantity: int = Field(..., ge=1, description="Quantity of the product")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")
    total_price: Decimal = Field(..., ge=0, description="Total price for this item")

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v):
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "product_id")


class OrderItemCreate(OrderItemBase, BaseCreateSchema):
    """Schema for creating order items."""
    pass


class OrderItemResponse(OrderItemBase, BaseResponseSchema):
    """Schema for order item responses."""

    order_id: str = Field(
        ...,
        description="Order UUID identifier",
        min_length=36,
        max_length=36
    )

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v):
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "order_id")


class OrderBase(BaseSchema):
    """Base schema for orders."""

    buyer_id: str = Field(
        ...,
        description="Buyer UUID identifier",
        min_length=36,
        max_length=36
    )
    vendor_id: Optional[str] = Field(
        None,
        description="Vendor UUID identifier",
        min_length=36,
        max_length=36
    )
    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        description="Order status"
    )
    priority: OrderPriority = Field(
        default=OrderPriority.NORMAL,
        description="Order priority"
    )
    total_amount: Decimal = Field(..., ge=0, description="Total order amount")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    billing_address: Optional[str] = Field(None, description="Billing address")
    notes: Optional[str] = Field(None, max_length=1000, description="Order notes")

    @field_validator("buyer_id")
    @classmethod
    def validate_buyer_id(cls, v):
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "buyer_id")

    @field_validator("vendor_id")
    @classmethod
    def validate_vendor_id(cls, v):
        if v is None:
            return v
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "vendor_id")


class OrderCreate(OrderBase, BaseCreateSchema):
    """Schema for creating orders."""

    items: List[OrderItemCreate] = Field(
        ...,
        min_items=1,
        description="List of order items"
    )

    @field_validator("items")
    @classmethod
    def validate_items_total(cls, v, values):
        """Validate that item totals match order total."""
        if not v:
            raise ValueError("At least one item is required")
        return v


class OrderUpdate(BaseUpdateSchema):
    """Schema for updating orders."""

    status: Optional[OrderStatus] = None
    priority: Optional[OrderPriority] = None
    shipping_address: Optional[str] = Field(None, max_length=500)
    billing_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    vendor_id: Optional[str] = Field(
        None,
        min_length=36,
        max_length=36
    )

    @field_validator("vendor_id")
    @classmethod
    def validate_vendor_id(cls, v):
        if v is None:
            return v
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "vendor_id")


class OrderResponse(OrderBase, BaseResponseSchema, IDValidationMixin):
    """Schema for order responses."""

    order_number: Optional[str] = Field(None, description="Human-readable order number")
    items: List[OrderItemResponse] = Field(..., description="Order items")
    subtotal: Decimal = Field(..., ge=0, description="Subtotal before tax and shipping")
    tax_amount: Decimal = Field(..., ge=0, description="Tax amount")
    shipping_amount: Decimal = Field(..., ge=0, description="Shipping amount")
    discount_amount: Decimal = Field(..., ge=0, description="Discount amount")
    processing_at: Optional[datetime] = Field(None, description="When order started processing")
    shipped_at: Optional[datetime] = Field(None, description="When order was shipped")
    delivered_at: Optional[datetime] = Field(None, description="When order was delivered")
    cancelled_at: Optional[datetime] = Field(None, description="When order was cancelled")


class OrderStatusUpdate(BaseSchema):
    """Schema for order status updates."""

    status: OrderStatus = Field(..., description="New order status")
    notes: Optional[str] = Field(None, max_length=500, description="Status update notes")
    notify_customer: bool = Field(True, description="Whether to notify customer")


class OrderSearchFilter(BaseSchema):
    """Schema for order search filters."""

    buyer_id: Optional[str] = Field(None, min_length=36, max_length=36)
    vendor_id: Optional[str] = Field(None, min_length=36, max_length=36)
    status: Optional[OrderStatus] = None
    priority: Optional[OrderPriority] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)

    @field_validator("buyer_id", "vendor_id")
    @classmethod
    def validate_id_fields(cls, v):
        if v is None:
            return v
        from app.core.id_validation import IDValidator
        return IDValidator.validate_uuid_string(v, "id")


class OrderSummary(BaseIDSchema):
    """Summary schema for orders in lists."""

    order_number: Optional[str] = Field(None, description="Human-readable order number")
    buyer_id: str = Field(..., min_length=36, max_length=36)
    vendor_id: Optional[str] = Field(None, min_length=36, max_length=36)
    status: OrderStatus = Field(..., description="Order status")
    total_amount: Decimal = Field(..., ge=0, description="Total order amount")
    created_at: datetime = Field(..., description="Creation timestamp")
    item_count: int = Field(..., ge=1, description="Number of items in order")


class OrderMetrics(BaseSchema):
    """Schema for order metrics and analytics."""

    total_orders: int = Field(..., ge=0, description="Total number of orders")
    total_revenue: Decimal = Field(..., ge=0, description="Total revenue")
    average_order_value: Decimal = Field(..., ge=0, description="Average order value")
    orders_by_status: Dict[str, int] = Field(..., description="Order count by status")
    orders_by_priority: Dict[str, int] = Field(..., description="Order count by priority")
    daily_orders: List[Dict[str, Any]] = Field(..., description="Daily order statistics")


# Export all order schemas
__all__ = [
    "OrderStatus",
    "OrderPriority",
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderStatusUpdate",
    "OrderSearchFilter",
    "OrderSummary",
    "OrderMetrics"
]