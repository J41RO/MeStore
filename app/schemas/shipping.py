"""
Pydantic schemas for shipping management.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ShippingStatus(str, Enum):
    """Status of shipping events."""
    IN_TRANSIT = "in_transit"
    AT_WAREHOUSE = "at_warehouse"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"
    FAILED = "failed"


class ShippingEventCreate(BaseModel):
    """Schema for creating a shipping event."""
    status: ShippingStatus
    location: str = Field(..., min_length=1, max_length=200, description="Current location of the package")
    description: Optional[str] = Field(None, max_length=500, description="Additional details about the event")


class ShippingEvent(ShippingEventCreate):
    """Schema for shipping event response."""
    timestamp: datetime

    class Config:
        from_attributes = True


class ShippingAssignment(BaseModel):
    """Schema for assigning shipping to an order."""
    courier: str = Field(..., min_length=1, max_length=100, description="Courier company name")
    estimated_days: int = Field(..., ge=1, le=30, description="Estimated delivery days")

    @validator('courier')
    def validate_courier(cls, v):
        """Validate courier name."""
        valid_couriers = [
            'Rappi', 'Coordinadora', 'Servientrega',
            'Interrapidisimo', 'Envia', 'Otro'
        ]
        if v not in valid_couriers:
            # Allow custom courier but log it
            pass
        return v


class ShippingLocationUpdate(BaseModel):
    """Schema for updating shipping location."""
    current_location: str = Field(..., min_length=1, max_length=200)
    status: ShippingStatus
    description: Optional[str] = Field(None, max_length=500)


class ShippingInfo(BaseModel):
    """Schema for shipping information response."""
    tracking_number: Optional[str] = None
    courier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    shipping_events: List[ShippingEvent] = []
    current_status: Optional[ShippingStatus] = None

    class Config:
        from_attributes = True


class TrackingResponse(BaseModel):
    """Schema for tracking response."""
    order_number: str
    order_status: str
    shipping_info: ShippingInfo
    shipping_address: str
    shipping_city: str
    shipping_state: str
    created_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
