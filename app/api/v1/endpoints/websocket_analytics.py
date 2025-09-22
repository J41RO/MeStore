# app/api/v1/endpoints/websocket_analytics.py
# REAL-TIME ANALYTICS WEBSOCKET ENDPOINT
# Target: <150ms latency with auto-reconnection and JWT auth

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order
from app.models.commission import Commission
from app.utils.response_utils import ResponseUtils

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Note: Background task startup will be handled by main application lifespan
# Router-level events are deprecated in FastAPI and may not work reliably

# Security scheme for WebSocket
security = HTTPBearer(auto_error=False)

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, vendor_id: str, user_id: str):
        """Accept WebSocket connection and store vendor association"""
        await websocket.accept()

        if vendor_id not in self.active_connections:
            self.active_connections[vendor_id] = []

        self.active_connections[vendor_id].append(websocket)
        self.connection_metadata[id(websocket)] = {
            "vendor_id": vendor_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }

        logger.info(f"WebSocket connected for vendor {vendor_id}, user {user_id}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        metadata = self.connection_metadata.get(id(websocket))
        if metadata:
            vendor_id = metadata["vendor_id"]
            if vendor_id in self.active_connections:
                try:
                    self.active_connections[vendor_id].remove(websocket)
                    if not self.active_connections[vendor_id]:
                        del self.active_connections[vendor_id]
                except ValueError:
                    pass
            del self.connection_metadata[id(websocket)]
            logger.info(f"WebSocket disconnected for vendor {vendor_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_vendor(self, message: dict, vendor_id: str):
        """Send message to all connections for a specific vendor"""
        if vendor_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[vendor_id]:
                try:
                    await connection.send_text(json.dumps({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Error broadcasting to vendor {vendor_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

    async def broadcast_to_all(self, message: dict):
        """Send message to all active connections"""
        for vendor_id in list(self.active_connections.keys()):
            await self.broadcast_to_vendor(message, vendor_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_vendor_connections(self, vendor_id: str) -> int:
        """Get number of connections for specific vendor"""
        return len(self.active_connections.get(vendor_id, []))

# Global connection manager
manager = ConnectionManager()

async def authenticate_websocket_token(
    websocket: WebSocket,
    token: Optional[str],
    db: AsyncSession
) -> Optional[User]:
    """Authenticate WebSocket connection using JWT token"""
    if not token:
        await websocket.close(code=4001, reason="Authentication token required")
        return None

    try:
        # Import decode_access_token for direct token validation
        from app.core.security import decode_access_token
        from sqlalchemy import select

        # Decode JWT token directly
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=4001, reason="Invalid token payload")
            return None

        # Get user from database
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close(code=4001, reason="User not found")
            return None

        # Verify user is vendor
        if user.user_type != UserType.VENDOR:
            await websocket.close(code=4003, reason="Access denied: vendor account required")
            return None

        logger.info(f"WebSocket authentication successful for vendor {user.id}")
        return user

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return None

async def get_vendor_analytics_data(vendor_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get real-time analytics data for vendor"""
    try:
        # Get date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Revenue metrics (current and previous period)
        current_revenue_query = select(func.coalesce(func.sum(Commission.commission_amount), 0)).where(
            and_(
                Commission.vendor_id == vendor_id,
                Commission.created_at >= month_ago,
                Commission.status == 'APPROVED'
            )
        )
        current_revenue_result = await db.execute(current_revenue_query)
        current_revenue = float(current_revenue_result.scalar() or 0)

        # Previous month revenue for comparison
        previous_month = month_ago - timedelta(days=30)
        previous_revenue_query = select(func.coalesce(func.sum(Commission.commission_amount), 0)).where(
            and_(
                Commission.vendor_id == vendor_id,
                Commission.created_at >= previous_month,
                Commission.created_at < month_ago,
                Commission.status == 'APPROVED'
            )
        )
        previous_revenue_result = await db.execute(previous_revenue_query)
        previous_revenue = float(previous_revenue_result.scalar() or 0)

        # Calculate revenue trend
        revenue_percentage = 0
        revenue_trend = 'stable'
        if previous_revenue > 0:
            revenue_percentage = ((current_revenue - previous_revenue) / previous_revenue) * 100
            revenue_trend = 'up' if revenue_percentage > 0 else 'down' if revenue_percentage < 0 else 'stable'
        elif current_revenue > 0:
            revenue_trend = 'up'
            revenue_percentage = 100.0

        # Order metrics
        current_orders_query = select(func.count(Order.id)).where(
            and_(
                Order.vendor_id == vendor_id,
                Order.created_at >= month_ago
            )
        )
        current_orders_result = await db.execute(current_orders_query)
        current_orders = int(current_orders_result.scalar() or 0)

        previous_orders_query = select(func.count(Order.id)).where(
            and_(
                Order.vendor_id == vendor_id,
                Order.created_at >= previous_month,
                Order.created_at < month_ago
            )
        )
        previous_orders_result = await db.execute(previous_orders_query)
        previous_orders = int(previous_orders_result.scalar() or 0)

        # Calculate order trend
        orders_percentage = 0
        orders_trend = 'stable'
        if previous_orders > 0:
            orders_percentage = ((current_orders - previous_orders) / previous_orders) * 100
            orders_trend = 'up' if orders_percentage > 0 else 'down' if orders_percentage < 0 else 'stable'
        elif current_orders > 0:
            orders_trend = 'up'
            orders_percentage = 100.0

        # Product metrics
        total_products_query = select(func.count(Product.id)).where(Product.vendor_id == vendor_id)
        total_products_result = await db.execute(total_products_query)
        total_products = int(total_products_result.scalar() or 0)

        active_products_query = select(func.count(Product.id)).where(
            and_(Product.vendor_id == vendor_id, Product.is_active == True)
        )
        active_products_result = await db.execute(active_products_query)
        active_products = int(active_products_result.scalar() or 0)

        low_stock_products_query = select(func.count(Product.id)).where(
            and_(
                Product.vendor_id == vendor_id,
                Product.is_active == True,
                Product.stock_quantity <= 10,
                Product.stock_quantity > 0
            )
        )
        low_stock_result = await db.execute(low_stock_products_query)
        low_stock = int(low_stock_result.scalar() or 0)

        out_of_stock_query = select(func.count(Product.id)).where(
            and_(
                Product.vendor_id == vendor_id,
                Product.is_active == True,
                Product.stock_quantity <= 0
            )
        )
        out_of_stock_result = await db.execute(out_of_stock_query)
        out_of_stock = int(out_of_stock_result.scalar() or 0)

        # Top products (last 30 days)
        top_products_query = select(
            Product.id,
            Product.name,
            Product.price,
            func.count(Order.id).label('sales_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).select_from(
            Product.__table__.join(Order.__table__, Product.id == Order.product_id)
        ).where(
            and_(
                Product.vendor_id == vendor_id,
                Order.created_at >= month_ago
            )
        ).group_by(Product.id, Product.name, Product.price).order_by(desc('sales_count')).limit(5)

        top_products_result = await db.execute(top_products_query)
        top_products = [
            {
                "id": str(row.id),
                "name": row.name,
                "sales": int(row.sales_count),
                "revenue": float(row.total_revenue or 0),
                "image": "/api/placeholder/60/60",
                "trend": "up"  # Could be calculated based on historical data
            }
            for row in top_products_result.fetchall()
        ]

        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(5, -1, -1):
            start_date = today - timedelta(days=30 * (i + 1))
            end_date = today - timedelta(days=30 * i)

            month_revenue_query = select(func.coalesce(func.sum(Commission.commission_amount), 0)).where(
                and_(
                    Commission.vendor_id == vendor_id,
                    Commission.created_at >= start_date,
                    Commission.created_at < end_date,
                    Commission.status == 'APPROVED'
                )
            )
            month_revenue_result = await db.execute(month_revenue_query)
            month_revenue = float(month_revenue_result.scalar() or 0)

            month_orders_query = select(func.count(Order.id)).where(
                and_(
                    Order.vendor_id == vendor_id,
                    Order.created_at >= start_date,
                    Order.created_at < end_date
                )
            )
            month_orders_result = await db.execute(month_orders_query)
            month_orders = int(month_orders_result.scalar() or 0)

            monthly_trends.append({
                "month": start_date.strftime("%b"),
                "revenue": month_revenue,
                "orders": month_orders,
                "customers": month_orders,  # Simplified - could be unique customer count
                "timestamp": start_date.isoformat()
            })

        # Sales by category (mock data for now)
        sales_by_category = [
            {"category": "Electrónicos", "sales": current_orders // 3, "revenue": current_revenue * 0.4, "color": "#3b82f6", "percentage": 40},
            {"category": "Ropa", "sales": current_orders // 4, "revenue": current_revenue * 0.3, "color": "#10b981", "percentage": 30},
            {"category": "Hogar", "sales": current_orders // 5, "revenue": current_revenue * 0.2, "color": "#f97316", "percentage": 20},
            {"category": "Deportes", "sales": current_orders // 6, "revenue": current_revenue * 0.1, "color": "#8b5cf6", "percentage": 10}
        ]

        return {
            "metrics": {
                "revenue": {
                    "current": current_revenue,
                    "previous": previous_revenue,
                    "trend": revenue_trend,
                    "percentage": abs(revenue_percentage)
                },
                "orders": {
                    "current": current_orders,
                    "previous": previous_orders,
                    "trend": orders_trend,
                    "percentage": abs(orders_percentage)
                },
                "products": {
                    "total": total_products,
                    "active": active_products,
                    "lowStock": low_stock,
                    "outOfStock": out_of_stock
                },
                "customers": {
                    "total": current_orders,  # Simplified
                    "new": max(0, current_orders - previous_orders),
                    "returning": min(current_orders, previous_orders)
                }
            },
            "topProducts": top_products,
            "salesByCategory": sales_by_category,
            "monthlyTrends": monthly_trends
        }

    except Exception as e:
        logger.error(f"Error getting vendor analytics data: {e}")
        return {
            "metrics": None,
            "topProducts": [],
            "salesByCategory": [],
            "monthlyTrends": []
        }

@router.websocket("/ws/vendor/analytics")
async def websocket_vendor_analytics(
    websocket: WebSocket,
    vendor_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time vendor analytics

    Features:
    - JWT authentication with query parameter
    - Real-time metrics updates
    - Auto-reconnection support
    - <150ms latency target
    - Heartbeat monitoring
    """
    start_time = datetime.utcnow()

    # Get database session using dependency
    db_generator = get_db()
    db = await db_generator.__anext__()

    try:
        # Authenticate user
        user = await authenticate_websocket_token(websocket, token, db)
        if not user:
            return

        # Use user's vendor ID if not provided
        if not vendor_id:
            vendor_id = str(user.id)

        # Verify user can access this vendor data
        if str(user.id) != vendor_id:
            await websocket.close(code=4003, reason="Access denied: can only access own analytics")
            return

        # Connect to manager
        await manager.connect(websocket, vendor_id, str(user.id))

        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection_status",
            "data": {
                "status": "connected",
                "vendor_id": vendor_id,
                "connection_time": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
        }, websocket)

        # Send initial analytics data
        analytics_data = await get_vendor_analytics_data(vendor_id, db)
        await manager.send_personal_message({
            "type": "analytics_update",
            "data": analytics_data
        }, websocket)

        try:
            # Main message loop
            while True:
                try:
                    # Wait for message with timeout for heartbeat
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    message_data = json.loads(message)

                    # Handle different message types
                    message_type = message_data.get("type")

                    if message_type == "ping":
                        # Respond to ping with pong
                        await manager.send_personal_message({
                            "type": "connection_status",
                            "data": {"type": "pong"}
                        }, websocket)

                    elif message_type == "refresh_analytics":
                        # Force refresh analytics data - use fresh db session
                        async with AsyncSessionLocal() as fresh_db:
                            analytics_data = await get_vendor_analytics_data(vendor_id, fresh_db)
                            await manager.send_personal_message({
                                "type": "analytics_update",
                                "data": analytics_data
                            }, websocket)

                    elif message_type == "subscribe_notifications":
                        # Subscribe to real-time notifications
                        await manager.send_personal_message({
                            "type": "connection_status",
                            "data": {"status": "subscribed_to_notifications"}
                        }, websocket)

                    # Update last ping time
                    if id(websocket) in manager.connection_metadata:
                        manager.connection_metadata[id(websocket)]["last_ping"] = datetime.utcnow()

                except asyncio.TimeoutError:
                    # Send heartbeat ping
                    await manager.send_personal_message({
                        "type": "connection_status",
                        "data": {"type": "heartbeat"}
                    }, websocket)

                except json.JSONDecodeError:
                    # Invalid JSON received
                    await manager.send_personal_message({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    }, websocket)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for vendor {vendor_id}")
        except Exception as e:
            logger.error(f"WebSocket error for vendor {vendor_id}: {e}")
        finally:
            manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket setup error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
    finally:
        # Close database session
        try:
            await db_generator.aclose()
        except:
            pass

# Background task to send periodic analytics updates (optimized for <150ms)
async def periodic_analytics_update():
    """Send periodic analytics updates to all connected vendors with performance optimization"""
    while True:
        try:
            await asyncio.sleep(30)  # Update every 30 seconds for more real-time feel

            if manager.get_connection_count() > 0:
                update_start_time = datetime.utcnow()
                logger.info(f"Sending periodic updates to {manager.get_connection_count()} connections")

                # Get unique vendor IDs from active connections
                vendor_ids = list(manager.active_connections.keys())

                # Process vendors in parallel for better performance
                async def update_vendor(vendor_id: str):
                    try:
                        vendor_start_time = datetime.utcnow()

                        # Get fresh analytics data with timeout
                        try:
                            await asyncio.wait_for(update_single_vendor(vendor_id), timeout=5.0)
                        except asyncio.TimeoutError:
                            logger.error(f"Timeout updating vendor {vendor_id}")

                    except Exception as e:
                        logger.error(f"Error sending periodic update to vendor {vendor_id}: {e}")

                # Run vendor updates concurrently for better performance
                await asyncio.gather(*[update_vendor(vid) for vid in vendor_ids], return_exceptions=True)

                # Track total update time
                total_duration = (datetime.utcnow() - update_start_time).total_seconds() * 1000
                logger.info(f"Periodic update completed in {total_duration:.2f}ms")

        except Exception as e:
            logger.error(f"Error in periodic analytics update: {e}")
            await asyncio.sleep(5)  # Wait before retrying

async def update_single_vendor(vendor_id: str):
    """Update analytics for a single vendor"""
    vendor_start_time = datetime.utcnow()

    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        analytics_data = await get_vendor_analytics_data(vendor_id, db)

        # Send update to all connections for this vendor
        await manager.broadcast_to_vendor({
            "type": "analytics_update",
            "data": analytics_data
        }, vendor_id)

    # Track processing time per vendor
    vendor_duration = (datetime.utcnow() - vendor_start_time).total_seconds() * 1000
    if vendor_duration > 100:
        logger.warning(f"Slow vendor update: {vendor_id} took {vendor_duration:.2f}ms")

# Background task will be started by startup event handler
# Note: Don't start background tasks at module import time

# Global variable to store background task
background_task = None

async def start_periodic_analytics_task():
    """Start the periodic analytics update background task"""
    global background_task
    if background_task is None:
        background_task = asyncio.create_task(periodic_analytics_update())
        logger.info("Periodic analytics update task started")

async def stop_periodic_analytics_task():
    """Stop the periodic analytics update background task"""
    global background_task
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
        background_task = None
        logger.info("Periodic analytics update task stopped")

# Utility endpoint to broadcast test message
@router.post("/websocket/test-broadcast")
async def test_broadcast(message: dict, vendor_id: Optional[str] = None):
    """Test endpoint to broadcast messages to WebSocket connections"""
    if vendor_id:
        await manager.broadcast_to_vendor({
            "type": "test_message",
            "data": message
        }, vendor_id)
        return {"status": "sent_to_vendor", "vendor_id": vendor_id}
    else:
        await manager.broadcast_to_all({
            "type": "test_message",
            "data": message
        })
        return {"status": "sent_to_all", "connections": manager.get_connection_count()}

# Connection status endpoint
@router.get("/websocket/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_vendors": len(manager.active_connections),
        "vendor_connections": {
            vendor_id: len(connections)
            for vendor_id, connections in manager.active_connections.items()
        }
    }