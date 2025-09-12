from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import logging
import uuid
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, Transaction
from app.models.product import Product
from app.core.auth import get_current_user
from app.services.order_tracking_service import order_tracking_service
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int
    variant_attributes: Optional[Dict[str, str]] = None

class CreateOrderRequest(BaseModel):
    items: List[OrderItemRequest]
    shipping_name: str
    shipping_phone: str
    shipping_email: Optional[EmailStr] = None
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: Optional[str] = None
    notes: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    product_image_url: Optional[str]
    unit_price: float
    quantity: int
    total_price: float
    variant_attributes: Optional[Dict[str, str]]

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    subtotal: float
    tax_amount: float
    shipping_cost: float
    discount_amount: float
    total_amount: float
    shipping_address: str
    shipping_city: str
    shipping_state: str
    notes: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]
    is_paid: bool
    payment_status: Optional[str]

class OrderSummary(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float
    created_at: datetime
    items_count: int
    is_paid: bool

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order"""
    try:
        # Validate that we have items
        if not order_request.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must contain at least one item"
            )
        
        # Get all products and validate availability
        product_ids = [item.product_id for item in order_request.items]
        result = await db.execute(
            select(Product).where(
                Product.id.in_(product_ids),
                Product.estado == "aprobado"
            )
        )
        products = {p.id: p for p in result.scalars().all()}
        
        # Validate all products exist and are available
        missing_products = set(product_ids) - set(products.keys())
        if missing_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Products not found or unavailable: {missing_products}"
            )
        
        # Calculate totals
        subtotal = Decimal('0')
        order_items = []
        
        for item_request in order_request.items:
            product = products[item_request.product_id]
            
            if item_request.quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid quantity for product {product.id}"
                )
            
            unit_price = Decimal(str(product.precio_venta))
            total_price = unit_price * item_request.quantity
            subtotal += total_price
            
            # Get primary image
            primary_image = None
            if product.images:
                primary_images = [img for img in product.images if img.is_primary]
                if primary_images:
                    primary_image = primary_images[0].image_url
                elif product.images:
                    primary_image = product.images[0].image_url
            
            order_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "product_image_url": primary_image,
                "unit_price": float(unit_price),
                "quantity": item_request.quantity,
                "total_price": float(total_price),
                "variant_attributes": item_request.variant_attributes
            })
        
        # Calculate taxes and shipping (placeholder logic)
        tax_amount = subtotal * Decimal('0.19')  # 19% IVA in Colombia
        shipping_cost = Decimal('0')  # Free shipping for now
        if subtotal < Decimal('100000'):  # Less than 100,000 COP
            shipping_cost = Decimal('15000')  # 15,000 COP shipping
        
        discount_amount = Decimal('0')  # No discount for now
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount
        
        # Generate unique order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            buyer_id=current_user.id,
            subtotal=float(subtotal),
            tax_amount=float(tax_amount),
            shipping_cost=float(shipping_cost),
            discount_amount=float(discount_amount),
            total_amount=float(total_amount),
            status=OrderStatus.PENDING,
            shipping_name=order_request.shipping_name,
            shipping_phone=order_request.shipping_phone,
            shipping_email=order_request.shipping_email or current_user.email,
            shipping_address=order_request.shipping_address,
            shipping_city=order_request.shipping_city,
            shipping_state=order_request.shipping_state,
            shipping_postal_code=order_request.shipping_postal_code,
            notes=order_request.notes
        )
        
        db.add(order)
        await db.flush()  # Get order ID
        
        # Create order items
        db_order_items = []
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(order_item)
            db_order_items.append(order_item)
        
        await db.commit()
        
        # Refresh to get all relationships
        await db.refresh(order)
        
        # Build response
        response_items = [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_sku=item.product_sku,
                product_image_url=item.product_image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price,
                variant_attributes=item.variant_attributes
            )
            for item in db_order_items
        ]
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status.value,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            shipping_cost=order.shipping_cost,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_state=order.shipping_state,
            notes=order.notes,
            created_at=order.created_at,
            items=response_items,
            is_paid=order.is_paid,
            payment_status=order.payment_status.value if order.payment_status else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )

@router.get("/", response_model=List[OrderSummary])
async def get_user_orders(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's orders"""
    try:
        query = select(Order).where(Order.buyer_id == current_user.id)
        
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter)
                query = query.where(Order.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # Get item counts for each order
        order_ids = [order.id for order in orders]
        if order_ids:
            count_result = await db.execute(
                select(
                    OrderItem.order_id,
                    func.count(OrderItem.id).label('items_count')
                )
                .where(OrderItem.order_id.in_(order_ids))
                .group_by(OrderItem.order_id)
            )
            item_counts = {row.order_id: row.items_count for row in count_result}
        else:
            item_counts = {}
        
        return [
            OrderSummary(
                id=order.id,
                order_number=order.order_number,
                status=order.status.value,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items_count=item_counts.get(order.id, 0),
                is_paid=order.is_paid
            )
            for order in orders
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get orders"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific order details"""
    try:
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.transactions)
            )
            .where(
                Order.id == order_id,
                Order.buyer_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        response_items = [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_sku=item.product_sku,
                product_image_url=item.product_image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price,
                variant_attributes=item.variant_attributes
            )
            for item in order.items
        ]
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status.value,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            shipping_cost=order.shipping_cost,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_state=order.shipping_state,
            notes=order.notes,
            created_at=order.created_at,
            items=response_items,
            is_paid=order.is_paid,
            payment_status=order.payment_status.value if order.payment_status else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order"
        )

@router.patch("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order"""
    try:
        result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.buyer_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled in current status"
            )
        
        if order.is_paid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel paid order. Request refund instead."
            )
        
        order.status = OrderStatus.CANCELLED
        await db.commit()
        
        return {
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "order_number": order.order_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        )

# Admin endpoints
@router.get("/admin/all")
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        query = select(Order).options(
            selectinload(Order.buyer),
            selectinload(Order.items)
        )
        
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter)
                query = query.where(Order.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        orders = result.scalars().all()
        
        return [
            {
                "id": order.id,
                "order_number": order.order_number,
                "buyer_email": order.buyer.email,
                "buyer_name": order.buyer.full_name,
                "status": order.status.value,
                "total_amount": order.total_amount,
                "created_at": order.created_at,
                "items_count": len(order.items),
                "is_paid": order.is_paid,
                "payment_status": order.payment_status.value if order.payment_status else None
            }
            for order in orders
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get orders"
        )

@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order status (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Validate status
        try:
            status_enum = OrderStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {new_status}"
            )
        
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        old_status = order.status
        order.status = status_enum
        
        # Update relevant timestamps
        if status_enum == OrderStatus.SHIPPED and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif status_enum == OrderStatus.DELIVERED and not order.delivered_at:
            order.delivered_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "message": "Order status updated successfully",
            "order_id": order.id,
            "old_status": old_status.value,
            "new_status": status_enum.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )


# ===== ENDPOINTS DE TRACKING PÚBLICO ENTERPRISE =====

@router.get("/track/{order_number}", summary="Tracking público de orden", tags=["Public Tracking"])
async def track_order_public(
    order_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint público para tracking de órdenes.
    
    No requiere autenticación - acceso mediante número de orden únicamente.
    Información filtrada para seguridad pública.
    """
    try:
        tracking_info = await order_tracking_service.get_public_tracking(db, order_number)
        return {
            "success": True,
            "data": tracking_info,
            "message": f"Tracking information for order {order_number}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in public tracking for {order_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tracking information"
        )


@router.get("/track/{order_number}/detailed", summary="Tracking detallado con autenticación")
async def track_order_detailed(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para tracking detallado con autenticación.
    
    Incluye información completa y sensible de la orden.
    Solo para el comprador o administradores.
    """
    try:
        # Verificar que el usuario tenga acceso a esta orden
        result = await db.execute(
            select(Order).where(Order.order_number == order_number)
        )
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Verificar permisos
        if order.buyer_id != current_user.id and current_user.user_type not in ["ADMIN", "SUPERUSER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this order"
            )
        
        tracking_info = await order_tracking_service.get_order_tracking_info(db, order_number)
        
        return {
            "success": True,
            "data": tracking_info,
            "message": f"Detailed tracking information for order {order_number}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in detailed tracking for {order_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving detailed tracking information"
        )


@router.get("/tracking/config", summary="Configuración de tracking")
async def get_tracking_config():
    """
    Endpoint para obtener configuración de tracking.
    
    Información pública sobre URLs y configuraciones de tracking.
    """
    try:
        config = order_tracking_service.get_tracking_config()
        return {
            "success": True,
            "data": config,
            "message": "Tracking configuration retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting tracking config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tracking configuration"
        )


class TrackingTokenRequest(BaseModel):
    """Request model para generar token de tracking"""
    order_number: str
    email: str  # Email del comprador para validación


@router.post("/tracking/generate-token", summary="Generar token de tracking público")
async def generate_tracking_token(
    request: TrackingTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Genera token seguro para tracking público.
    
    Permite acceso a tracking sin autenticación mediante token seguro.
    Validación por email del comprador.
    """
    try:
        # Verificar que la orden existe y el email coincide
        result = await db.execute(
            select(Order).options(selectinload(Order.buyer))
            .where(Order.order_number == request.order_number)
        )
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Verificar email del comprador
        if order.buyer.email != request.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email does not match order buyer"
            )
        
        # Generar token público
        token = order_tracking_service._generate_public_token(order)
        
        # URL de tracking con token
        tracking_url = f"{order_tracking_service.config.TRACKING_PUBLIC_URL}/{request.order_number}?token={token}"
        
        return {
            "success": True,
            "data": {
                "tracking_token": token,
                "tracking_url": tracking_url,
                "expires_in": "30 days",
                "order_number": request.order_number
            },
            "message": "Tracking token generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tracking token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating tracking token"
        )