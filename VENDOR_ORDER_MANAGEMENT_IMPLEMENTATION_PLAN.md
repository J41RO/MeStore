# Vendor Order Management System - Complete Implementation Plan

**Date**: 2025-10-03
**Agent**: enterprise-product-manager
**Status**: In Development
**Priority**: High
**Architecture**: FastAPI + React 19 + PostgreSQL + TDD

---

## Executive Summary

Implementation of a complete Vendor Order Management System allowing vendors to view, manage, and update orders containing their products. This multi-vendor order management system enables vendors to track order fulfillment, update preparation status, and view sales analytics while maintaining security isolation between vendors.

---

## Current System Analysis

### Existing Architecture

**Database Models:**
- `Order` model with `buyer_id`, status tracking, shipping information
- `OrderItem` model with `product_id` relationship
- `Product` model with `vendedor_id` (vendor ownership)
- `OrderStatus` enum: pending, confirmed, processing, shipped, delivered, cancelled, refunded

**Current Capabilities:**
- Buyers can create orders via `/api/v1/orders/` endpoint
- Order tracking and cancellation for buyers
- Complete order lifecycle management
- Stock validation and IVA calculations

**Gap Identified:**
- **No vendor-specific order endpoints** - Vendors cannot view orders containing their products
- **No item-level status tracking** - Cannot track preparation status per item
- **No vendor order filtering** - Cannot filter orders by vendor products
- **No vendor analytics** - No sales stats for individual vendors

---

## Requirements Specification

### Functional Requirements

#### FR-1: Vendor Order Visibility
- Vendors can view ONLY orders that contain their products
- Multi-vendor orders show only vendor's items
- Pagination and filtering by order status
- Real-time order updates

#### FR-2: Item Preparation Tracking
- New `preparation_status` field on `OrderItem`
- Status flow: pending → preparing → ready_to_ship → shipped
- Vendor can update only their items
- Timestamp tracking for status changes

#### FR-3: Vendor Order Analytics
- Total sales (daily/weekly/monthly)
- Orders pending preparation
- Top selling products
- Revenue breakdown

#### FR-4: Security & Access Control
- Vendor-level isolation (cannot see other vendors' data)
- Item-level validation (can only update own items)
- Read-only access to buyer information (name/contact only)
- 403 Forbidden for unauthorized access attempts

### Non-Functional Requirements

#### NFR-1: Performance
- P95 latency < 200ms for order list endpoint
- Support pagination (100 orders per page)
- Database query optimization with eager loading
- Indexed queries on vendor_id and order status

#### NFR-2: Security
- JWT authentication required for all endpoints
- Vendor role validation via `get_current_active_vendor` dependency
- SQL injection prevention via SQLAlchemy ORM
- Rate limiting: 100 requests per minute per vendor

#### NFR-3: Testing
- TDD approach with tests written BEFORE implementation
- Minimum 80% code coverage
- Integration tests for multi-vendor scenarios
- E2E tests for complete order workflow

#### NFR-4: Mobile Optimization
- Mobile-first responsive design
- Touch-optimized UI components
- Offline capability (view cached orders)
- PWA-ready architecture

---

## Database Schema Changes

### New Migration: Add OrderItem Preparation Status

```python
# alembic/versions/YYYY_MM_DD_HHMM_add_order_item_preparation_status.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Preparation status enum
preparation_status = postgresql.ENUM(
    'pending', 'preparing', 'ready_to_ship', 'shipped',
    name='preparationstatus',
    create_type=True
)

def upgrade():
    # Create enum type
    preparation_status.create(op.get_bind(), checkfirst=True)

    # Add preparation_status column
    op.add_column('order_items',
        sa.Column('preparation_status',
                  sa.Enum('pending', 'preparing', 'ready_to_ship', 'shipped',
                          name='preparationstatus'),
                  nullable=False,
                  server_default='pending'))

    # Add timestamps for tracking
    op.add_column('order_items',
        sa.Column('preparation_started_at', sa.DateTime(timezone=True), nullable=True))

    op.add_column('order_items',
        sa.Column('ready_at', sa.DateTime(timezone=True), nullable=True))

    op.add_column('order_items',
        sa.Column('shipped_at', sa.DateTime(timezone=True), nullable=True))

    # Add index for vendor queries
    op.create_index('ix_order_items_preparation_status', 'order_items', ['preparation_status'])

def downgrade():
    op.drop_index('ix_order_items_preparation_status', table_name='order_items')
    op.drop_column('order_items', 'shipped_at')
    op.drop_column('order_items', 'ready_at')
    op.drop_column('order_items', 'preparation_started_at')
    op.drop_column('order_items', 'preparation_status')
    preparation_status.drop(op.get_bind(), checkfirst=True)
```

### Updated OrderItem Model

```python
# app/models/order.py

class PreparationStatus(PyEnum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY_TO_SHIP = "ready_to_ship"
    SHIPPED = "shipped"

class OrderItem(Base):
    __tablename__ = "order_items"

    # ... existing fields ...

    # NEW: Vendor preparation tracking
    preparation_status = Column(
        Enum(PreparationStatus),
        nullable=False,
        default=PreparationStatus.PENDING,
        index=True
    )
    preparation_started_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
```

---

## Backend API Design

### Endpoint Structure

```
BASE: /api/v1/vendor/orders

GET    /api/v1/vendor/orders                    # List vendor's orders
GET    /api/v1/vendor/orders/{order_id}         # Get order details
PATCH  /api/v1/vendor/orders/{order_id}/items/{item_id}/status  # Update item status
GET    /api/v1/vendor/orders/stats              # Vendor sales stats
GET    /api/v1/vendor/orders/stats/products     # Top products
```

### Endpoint Specifications

#### 1. GET /api/v1/vendor/orders

**Purpose**: List all orders containing vendor's products

**Query Parameters:**
- `skip: int = 0` - Pagination offset
- `limit: int = 100` - Maximum records (max: 100)
- `status: Optional[str]` - Filter by order status
- `preparation_status: Optional[str]` - Filter by item preparation status
- `start_date: Optional[datetime]` - Orders from date
- `end_date: Optional[datetime]` - Orders until date

**Response Schema:**
```python
class VendorOrderListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    orders: List[VendorOrderSummary]

class VendorOrderSummary(BaseModel):
    order_id: int
    order_number: str
    buyer_name: str
    buyer_email: str
    order_status: OrderStatus
    order_created_at: datetime
    vendor_items_count: int
    vendor_items_total: Decimal
    pending_items: int
    ready_items: int
    items: List[VendorOrderItemSummary]

class VendorOrderItemSummary(BaseModel):
    item_id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    preparation_status: PreparationStatus
    can_update_status: bool
```

**Business Logic:**
1. Extract vendor_id from JWT token
2. Query orders with INNER JOIN on order_items → products WHERE product.vendedor_id = vendor_id
3. Apply filters (status, date range, preparation_status)
4. Eager load relationships (items, product, buyer)
5. Calculate vendor-specific totals
6. Return paginated results

**Security:**
- JWT authentication required
- User must have VENDOR role
- Returns 403 if user is not a vendor
- Only shows orders with vendor's products

---

#### 2. GET /api/v1/vendor/orders/{order_id}

**Purpose**: Get detailed information for specific order

**Path Parameters:**
- `order_id: int` - Order ID

**Response Schema:**
```python
class VendorOrderDetailResponse(BaseModel):
    order_id: int
    order_number: str
    order_status: OrderStatus
    order_created_at: datetime
    order_confirmed_at: Optional[datetime]

    # Buyer information (limited)
    buyer_name: str
    buyer_email: str
    buyer_phone: Optional[str]

    # Shipping information
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: Optional[str]

    # Vendor's items only
    items: List[VendorOrderItemDetail]

    # Vendor-specific totals
    vendor_subtotal: Decimal
    vendor_item_count: int

class VendorOrderItemDetail(BaseModel):
    item_id: int
    product_id: int
    product_name: str
    product_sku: str
    product_image_url: Optional[str]
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    # Preparation tracking
    preparation_status: PreparationStatus
    preparation_started_at: Optional[datetime]
    ready_at: Optional[datetime]
    shipped_at: Optional[datetime]

    # Actions
    can_mark_preparing: bool
    can_mark_ready: bool
    can_mark_shipped: bool

class PreparationTimeline(BaseModel):
    status: str
    timestamp: datetime
    description: str
```

**Business Logic:**
1. Validate order exists
2. Verify vendor has items in this order (security check)
3. Load order with vendor's items only
4. Calculate allowed actions based on current status
5. Return detailed information

**Validation:**
- Order must exist (404 if not found)
- Vendor must have products in order (403 if not)
- Returns only vendor's items, not other vendors' items

---

#### 3. PATCH /api/v1/vendor/orders/{order_id}/items/{item_id}/status

**Purpose**: Update preparation status of specific order item

**Path Parameters:**
- `order_id: int` - Order ID
- `item_id: int` - Order Item ID

**Request Body:**
```python
class UpdateItemStatusRequest(BaseModel):
    new_status: PreparationStatus
    notes: Optional[str] = None
```

**Response:**
```python
class UpdateItemStatusResponse(BaseModel):
    item_id: int
    order_id: int
    previous_status: PreparationStatus
    new_status: PreparationStatus
    updated_at: datetime
    message: str
```

**Business Logic:**
1. Validate order and item exist
2. Verify item belongs to vendor's product (security)
3. Validate status transition is allowed
4. Update preparation_status and corresponding timestamp
5. Log status change event
6. Trigger notification to buyer (optional)
7. Update order status if all items ready

**Status Transition Rules:**
```
pending → preparing (vendor starts prep)
preparing → ready_to_ship (vendor finished prep)
ready_to_ship → shipped (admin/system marks shipped)
```

**Validation:**
- Item must belong to vendor's product (403)
- Status transition must be valid (400)
- Cannot update already shipped items (400)
- Cannot downgrade status (400)

---

#### 4. GET /api/v1/vendor/orders/stats

**Purpose**: Get vendor sales statistics and analytics

**Query Parameters:**
- `period: str = 'month'` - Time period: day, week, month, year
- `start_date: Optional[datetime]` - Custom period start
- `end_date: Optional[datetime]` - Custom period end

**Response Schema:**
```python
class VendorOrderStatsResponse(BaseModel):
    period: str
    start_date: datetime
    end_date: datetime

    # Sales metrics
    total_orders: int
    total_revenue: Decimal
    average_order_value: Decimal

    # Item metrics
    total_items_sold: int
    pending_items: int
    preparing_items: int
    ready_items: int
    shipped_items: int

    # Top products
    top_products: List[TopProductStat]

    # Daily breakdown
    daily_sales: List[DailySalesStat]

class TopProductStat(BaseModel):
    product_id: int
    product_name: str
    product_sku: str
    units_sold: int
    revenue: Decimal

class DailySalesStat(BaseModel):
    date: date
    orders: int
    items: int
    revenue: Decimal
```

**Business Logic:**
1. Extract vendor_id from token
2. Calculate date range based on period
3. Query orders with vendor's items
4. Aggregate statistics (COUNT, SUM, AVG)
5. Calculate top products by revenue
6. Group by date for daily breakdown
7. Return comprehensive stats

---

## Frontend Implementation

### Component Structure

```
frontend/src/
├── pages/vendor/
│   ├── VendorOrderManagement.tsx      # Main order list page
│   ├── VendorOrderDetail.tsx          # Single order detail page
│   └── VendorOrderStats.tsx           # Analytics dashboard
├── components/vendor/orders/
│   ├── OrderCard.tsx                  # Order summary card
│   ├── OrderItemCard.tsx              # Order item with status
│   ├── StatusUpdateButton.tsx         # Quick status update
│   ├── PreparationTimeline.tsx        # Visual timeline
│   ├── OrderFilters.tsx               # Filter controls
│   └── StatsWidget.tsx                # Stats card component
├── services/
│   └── vendorOrderService.ts          # API client
└── types/
    └── vendorOrder.ts                 # TypeScript interfaces
```

### 1. VendorOrderManagement.tsx

**Purpose**: Main page showing list of vendor's orders

**Features:**
- Responsive grid of order cards
- Filter by order status and preparation status
- Search by order number
- Pagination controls
- Quick actions (mark as preparing/ready)
- Pull-to-refresh on mobile

**UI Design:**
```typescript
interface OrderCardProps {
  order: VendorOrderSummary;
  onStatusUpdate: (itemId: number, newStatus: string) => Promise<void>;
  onViewDetails: (orderId: number) => void;
}

const OrderCard: React.FC<OrderCardProps> = ({ order, onStatusUpdate, onViewDetails }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      {/* Order Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold">#{order.order_number}</h3>
          <p className="text-sm text-gray-600">{order.buyer_name}</p>
        </div>
        <StatusBadge status={order.order_status} />
      </div>

      {/* Items Summary */}
      <div className="space-y-2 mb-4">
        {order.items.map(item => (
          <OrderItemCard
            key={item.item_id}
            item={item}
            onStatusUpdate={onStatusUpdate}
          />
        ))}
      </div>

      {/* Order Totals */}
      <div className="border-t pt-3 flex justify-between items-center">
        <span className="text-sm text-gray-600">
          {order.vendor_items_count} productos
        </span>
        <span className="text-lg font-bold">
          ${order.vendor_items_total.toLocaleString()}
        </span>
      </div>

      {/* Actions */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={() => onViewDetails(order.order_id)}
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
        >
          Ver Detalles
        </button>
      </div>
    </div>
  );
};
```

**State Management:**
```typescript
const VendorOrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<VendorOrderSummary[]>([]);
  const [filters, setFilters] = useState({
    status: '',
    preparation_status: '',
    search: ''
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  });
  const [loading, setLoading] = useState(false);

  // Fetch orders with filters
  const fetchOrders = async () => {
    setLoading(true);
    try {
      const response = await vendorOrderService.getOrders(filters, pagination);
      setOrders(response.orders);
      setPagination(prev => ({ ...prev, total: response.total }));
    } catch (error) {
      toast.error('Error loading orders');
    } finally {
      setLoading(false);
    }
  };

  // Quick status update
  const handleStatusUpdate = async (itemId: number, newStatus: string) => {
    try {
      await vendorOrderService.updateItemStatus(itemId, newStatus);
      toast.success('Status updated successfully');
      fetchOrders(); // Refresh list
    } catch (error) {
      toast.error('Error updating status');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Gestión de Órdenes</h1>
        <p className="text-gray-600">Administra las órdenes de tus productos</p>
      </div>

      {/* Filters */}
      <OrderFilters filters={filters} onFilterChange={setFilters} />

      {/* Orders Grid */}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {orders.map(order => (
            <OrderCard
              key={order.order_id}
              order={order}
              onStatusUpdate={handleStatusUpdate}
              onViewDetails={(id) => navigate(`/vendor/orders/${id}`)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      <Pagination pagination={pagination} onPageChange={setPagination} />
    </div>
  );
};
```

---

### 2. VendorOrderDetail.tsx

**Purpose**: Detailed view of single order with full information

**Features:**
- Complete order information
- Buyer contact details
- Shipping address
- Item-by-item status management
- Preparation timeline
- Action buttons for status updates

**UI Components:**
```typescript
const VendorOrderDetail: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<VendorOrderDetailResponse | null>(null);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Order Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Orden #{order?.order_number}
            </h1>
            <p className="text-gray-600">
              Creada el {formatDate(order?.order_created_at)}
            </p>
          </div>
          <StatusBadge status={order?.order_status} />
        </div>
      </div>

      {/* Customer & Shipping Info */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <CustomerInfo buyer={order?.buyer} />
        <ShippingInfo address={order?.shipping} />
      </div>

      {/* Order Items */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Tus Productos en esta Orden</h2>
        <div className="space-y-4">
          {order?.items.map(item => (
            <OrderItemDetailCard
              key={item.item_id}
              item={item}
              onStatusUpdate={handleStatusUpdate}
            />
          ))}
        </div>
      </div>

      {/* Preparation Timeline */}
      <PreparationTimeline items={order?.items} />
    </div>
  );
};
```

---

### 3. VendorOrderStats.tsx

**Purpose**: Analytics dashboard with sales metrics

**Features:**
- Key metrics cards (total sales, pending orders, etc.)
- Top products chart
- Daily sales graph
- Time period selector

---

## Service Layer

### Backend Service: VendorOrderService

```python
# app/services/vendor_order_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from decimal import Decimal
from datetime import datetime, date

from app.models.order import Order, OrderItem, OrderStatus, PreparationStatus
from app.models.product import Product
from app.schemas.vendor_order import (
    VendorOrderListResponse,
    VendorOrderDetailResponse,
    VendorOrderStatsResponse
)

class VendorOrderService:
    """Service for vendor order management operations"""

    @staticmethod
    async def get_vendor_orders(
        db: AsyncSession,
        vendor_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        preparation_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> VendorOrderListResponse:
        """Get list of orders containing vendor's products"""

        # Build query
        query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .where(Product.vendedor_id == vendor_id)
        )

        # Apply filters
        if status:
            query = query.where(Order.status == OrderStatus(status))

        if preparation_status:
            query = query.where(
                OrderItem.preparation_status == PreparationStatus(preparation_status)
            )

        if start_date:
            query = query.where(Order.created_at >= start_date)

        if end_date:
            query = query.where(Order.created_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and eager loading
        query = (
            query
            .distinct()
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.buyer)
            )
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        orders = result.scalars().unique().all()

        # Format response
        return VendorOrderListResponse(
            total=total,
            skip=skip,
            limit=limit,
            orders=[
                VendorOrderService._format_order_summary(order, vendor_id)
                for order in orders
            ]
        )

    @staticmethod
    async def get_vendor_order_detail(
        db: AsyncSession,
        order_id: int,
        vendor_id: str
    ) -> VendorOrderDetailResponse:
        """Get detailed order information for vendor"""

        # Query order
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.buyer)
            )
        )

        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Verify vendor has items in this order
        vendor_items = [
            item for item in order.items
            if item.product.vendedor_id == vendor_id
        ]

        if not vendor_items:
            raise HTTPException(
                status_code=403,
                detail="You don't have items in this order"
            )

        # Format response
        return VendorOrderService._format_order_detail(order, vendor_items)

    @staticmethod
    async def update_item_status(
        db: AsyncSession,
        order_id: int,
        item_id: int,
        vendor_id: str,
        new_status: PreparationStatus,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update preparation status of order item"""

        # Get item with product
        query = (
            select(OrderItem)
            .where(OrderItem.id == item_id, OrderItem.order_id == order_id)
            .options(selectinload(OrderItem.product))
        )

        result = await db.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Verify item belongs to vendor
        if item.product.vendedor_id != vendor_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own items"
            )

        # Validate status transition
        VendorOrderService._validate_status_transition(
            item.preparation_status, new_status
        )

        # Update status and timestamp
        previous_status = item.preparation_status
        item.preparation_status = new_status

        if new_status == PreparationStatus.PREPARING:
            item.preparation_started_at = datetime.now()
        elif new_status == PreparationStatus.READY_TO_SHIP:
            item.ready_at = datetime.now()
        elif new_status == PreparationStatus.SHIPPED:
            item.shipped_at = datetime.now()

        await db.commit()
        await db.refresh(item)

        return {
            "item_id": item.id,
            "order_id": order_id,
            "previous_status": previous_status.value,
            "new_status": new_status.value,
            "updated_at": datetime.now(),
            "message": f"Item status updated to {new_status.value}"
        }

    @staticmethod
    def _validate_status_transition(
        current: PreparationStatus,
        new: PreparationStatus
    ):
        """Validate status transition is allowed"""

        allowed_transitions = {
            PreparationStatus.PENDING: [PreparationStatus.PREPARING],
            PreparationStatus.PREPARING: [PreparationStatus.READY_TO_SHIP],
            PreparationStatus.READY_TO_SHIP: [PreparationStatus.SHIPPED],
            PreparationStatus.SHIPPED: []
        }

        if new not in allowed_transitions.get(current, []):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from {current.value} to {new.value}"
            )
```

---

## Testing Strategy

### Backend Tests (TDD Approach)

**Test File**: `tests/test_vendor_order_endpoints.py`

```python
import pytest
from fastapi import status

@pytest.mark.asyncio
@pytest.mark.tdd
class TestVendorOrderEndpoints:

    async def test_get_vendor_orders_success(
        self, async_client, vendor_user, vendor_product, test_order
    ):
        """Test vendor can view orders with their products"""

        # Arrange
        headers = {"Authorization": f"Bearer {vendor_user.token}"}

        # Act
        response = await async_client.get(
            "/api/v1/vendor/orders",
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] > 0
        assert len(data["orders"]) > 0
        assert data["orders"][0]["vendor_items_count"] > 0

    async def test_vendor_cannot_see_other_vendor_orders(
        self, async_client, vendor_user, other_vendor_order
    ):
        """Test vendor isolation - cannot see other vendors' orders"""

        # Arrange
        headers = {"Authorization": f"Bearer {vendor_user.token}"}

        # Act
        response = await async_client.get(
            f"/api/v1/vendor/orders/{other_vendor_order.id}",
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_item_status_success(
        self, async_client, vendor_user, vendor_order_item
    ):
        """Test vendor can update their item status"""

        # Arrange
        headers = {"Authorization": f"Bearer {vendor_user.token}"}
        payload = {"new_status": "preparing"}

        # Act
        response = await async_client.patch(
            f"/api/v1/vendor/orders/{vendor_order_item.order_id}/items/{vendor_order_item.id}/status",
            headers=headers,
            json=payload
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["new_status"] == "preparing"
        assert data["previous_status"] == "pending"

    async def test_update_item_invalid_transition(
        self, async_client, vendor_user, shipped_item
    ):
        """Test invalid status transition is rejected"""

        # Arrange
        headers = {"Authorization": f"Bearer {vendor_user.token}"}
        payload = {"new_status": "pending"}

        # Act
        response = await async_client.patch(
            f"/api/v1/vendor/orders/{shipped_item.order_id}/items/{shipped_item.id}/status",
            headers=headers,
            json=payload
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

### Frontend Tests (Vitest + React Testing Library)

```typescript
// tests/VendorOrderManagement.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VendorOrderManagement } from '@/pages/vendor/VendorOrderManagement';

describe('VendorOrderManagement', () => {
  it('displays list of vendor orders', async () => {
    render(<VendorOrderManagement />);

    await waitFor(() => {
      expect(screen.getByText(/Gestión de Órdenes/i)).toBeInTheDocument();
    });

    expect(screen.getAllByRole('article')).toHaveLength(3);
  });

  it('updates item status when button clicked', async () => {
    const user = userEvent.setup();
    render(<VendorOrderManagement />);

    const markPreparingButton = screen.getByText('Marcar como Preparando');
    await user.click(markPreparingButton);

    await waitFor(() => {
      expect(screen.getByText('Status updated successfully')).toBeInTheDocument();
    });
  });

  it('filters orders by status', async () => {
    const user = userEvent.setup();
    render(<VendorOrderManagement />);

    const filterSelect = screen.getByLabelText('Estado de Orden');
    await user.selectOptions(filterSelect, 'pending');

    await waitFor(() => {
      const orders = screen.getAllByRole('article');
      orders.forEach(order => {
        expect(order).toHaveTextContent('Pendiente');
      });
    });
  });
});
```

---

## Deployment Plan

### Phase 1: Database Migration (Week 1)
1. Create and test migration locally
2. Run migration on staging database
3. Verify data integrity
4. Backup production database
5. Run migration on production

### Phase 2: Backend API (Week 1-2)
1. Implement vendor order service
2. Create API endpoints
3. Write and run TDD tests
4. Code review and security audit
5. Deploy to staging
6. Integration testing
7. Deploy to production

### Phase 3: Frontend Implementation (Week 2-3)
1. Create TypeScript interfaces
2. Implement service layer
3. Build UI components
4. Implement pages
5. Add routing
6. Write frontend tests
7. Deploy to staging
8. User acceptance testing
9. Deploy to production

### Phase 4: Testing & Validation (Week 3)
1. E2E testing
2. Performance testing
3. Security penetration testing
4. Load testing
5. Mobile responsiveness testing
6. Cross-browser testing

### Phase 5: Documentation & Training (Week 4)
1. API documentation
2. User guide for vendors
3. Admin documentation
4. Video tutorials
5. Support team training

---

## Success Metrics

### Technical Metrics
- API response time P95 < 200ms
- Zero SQL injection vulnerabilities
- Test coverage > 80%
- Zero critical security issues

### Business Metrics
- Vendor adoption rate > 80% within 1 month
- Order preparation time reduced by 30%
- Vendor satisfaction score > 4.5/5
- Support tickets related to orders reduced by 50%

### User Experience Metrics
- Mobile page load time < 2 seconds
- Task completion rate > 95%
- Error rate < 1%
- Time to update order status < 10 seconds

---

## Risk Management

### Technical Risks

**Risk**: Migration fails on production database
**Mitigation**: Full database backup before migration, tested rollback script, staging environment testing

**Risk**: Performance degradation with large order volumes
**Mitigation**: Database indexing, query optimization, pagination, caching layer

**Risk**: Security vulnerability in vendor isolation
**Mitigation**: Comprehensive security testing, code review, penetration testing

### Business Risks

**Risk**: Vendors don't adopt new system
**Mitigation**: User training, video tutorials, support hotline, gradual rollout

**Risk**: System bugs affect order fulfillment
**Mitigation**: Extensive testing, phased rollout, quick rollback capability

---

## Future Enhancements

### Phase 2 Features (3-6 months)
- Email notifications on order status changes
- WhatsApp integration for buyer communication
- Bulk status updates for multiple items
- Export orders to CSV/Excel
- Advanced filtering and search
- Saved filter presets

### Phase 3 Features (6-12 months)
- Mobile native app (React Native)
- Push notifications
- Barcode scanning for item tracking
- Integration with shipping carriers
- Automated status updates via courier APIs
- Vendor performance dashboard
- AI-powered order prediction
- Inventory sync with order status

---

## Appendix

### A. Database Indexes

```sql
-- Optimize vendor order queries
CREATE INDEX idx_order_items_product_vendor ON order_items(product_id);
CREATE INDEX idx_order_items_prep_status ON order_items(preparation_status);
CREATE INDEX idx_orders_created_status ON orders(created_at, status);
CREATE INDEX idx_products_vendor_status ON products(vendedor_id, status);
```

### B. API Rate Limits

```
/api/v1/vendor/orders: 100 requests/minute
/api/v1/vendor/orders/{id}: 200 requests/minute
/api/v1/vendor/orders/stats: 20 requests/minute
```

### C. Mobile Breakpoints

```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-03
**Next Review**: 2025-10-10
**Status**: Ready for Implementation

---

## Implementation Checklist

- [ ] Database migration created and tested
- [ ] OrderItem model updated with preparation_status
- [ ] Vendor order service implemented
- [ ] API endpoints created and documented
- [ ] TDD tests written and passing
- [ ] Frontend TypeScript interfaces defined
- [ ] vendorOrderService.ts implemented
- [ ] VendorOrderManagement page created
- [ ] VendorOrderDetail page created
- [ ] VendorOrderStats dashboard created
- [ ] Routing configured
- [ ] Frontend tests written and passing
- [ ] Integration tests complete
- [ ] Security audit passed
- [ ] Performance testing passed
- [ ] Documentation complete
- [ ] Deployed to staging
- [ ] User acceptance testing
- [ ] Deployed to production

