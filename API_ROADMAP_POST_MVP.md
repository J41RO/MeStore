# API ROADMAP POST-MVP
**MeStore - Backend API Enhancement Plan**

**Current Status**: MVP Complete (35/40)
**Target**: Full Production (40/40)

---

## 🎯 PHASE 1: IMMEDIATE ENHANCEMENTS (Week 1)
**Priority**: CRITICAL
**Timeline**: 1 week
**Effort**: 8-12 hours total

### 1.1 Global Rate Limiting ⚡
**Status**: Missing
**Priority**: HIGH
**Effort**: 2-4 hours

**Implementation**:
```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.post("/products/")
@limiter.limit("100/hour")  # 100 requests per hour per IP
async def create_product(...):
    ...

@router.post("/orders/")
@limiter.limit("50/hour")  # 50 orders per hour
async def create_order(...):
    ...

@router.post("/payments/process")
@limiter.limit("20/hour")  # 20 payments per hour
async def process_payment(...):
    ...
```

**Rate Limits Recommended**:
- Products: 100/hour (create), 1000/hour (read)
- Orders: 50/hour (create), 200/hour (read)
- Payments: 20/hour (process), 100/hour (status)
- Auth: 10/hour (login), 5/hour (register)

---

### 1.2 Order Update Endpoints 📝
**Status**: Missing
**Priority**: MEDIUM
**Effort**: 3-5 hours

**New Endpoints**:

#### 1.2.1 Update Order Status (Admin/Vendor)
```python
@router.put("/{order_id}/status", status_code=200)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    notes: Optional[str] = None,
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status (admin/vendor only).

    Allowed transitions:
    - PENDING → CONFIRMED (payment approved)
    - CONFIRMED → PROCESSING (vendor starts preparing)
    - PROCESSING → SHIPPED (order shipped)
    - SHIPPED → DELIVERED (customer received)
    - Any → CANCELLED (with refund if paid)
    """
    # Validate order exists
    order = await get_order_or_404(order_id, db)

    # Validate status transition
    if not is_valid_transition(order.status, new_status):
        raise HTTPException(400, "Invalid status transition")

    # Update order
    order.status = new_status
    if notes:
        order.notes = (order.notes or "") + f"\n[{datetime.now()}] {notes}"

    # Trigger side effects
    if new_status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
        await send_shipping_notification(order)
    elif new_status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()
        await send_delivery_confirmation(order)

    await db.commit()

    return {"success": True, "order": OrderResponse.from_orm(order)}
```

#### 1.2.2 Quick Status Update (PATCH)
```python
@router.patch("/{order_id}", status_code=200)
async def quick_order_update(
    order_id: int,
    status: Optional[OrderStatus] = None,
    tracking_number: Optional[str] = None,
    current_user: UserRead = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Quick update for specific fields without full validation."""
    order = await get_order_or_404(order_id, db)

    if status:
        order.status = status
    if tracking_number:
        order.tracking_number = tracking_number

    await db.commit()
    return {"success": True, "updated_fields": [...]}
```

---

### 1.3 Environment Audit 🔐
**Status**: Required
**Priority**: HIGH
**Effort**: 1 hour

**Checklist**:
```bash
# .env file verification
✅ DATABASE_URL - PostgreSQL connection
✅ REDIS_URL - Redis connection
✅ SECRET_KEY - JWT signing (min 32 chars)
✅ ALGORITHM - "HS256"
✅ WOMPI_PUBLIC_KEY - Payment gateway
✅ WOMPI_PRIVATE_KEY - Webhook signature
✅ PAYU_MERCHANT_ID - PayU merchant
✅ PAYU_API_KEY - PayU API key
✅ PAYU_ACCOUNT_ID - PayU account
✅ SMTP_HOST - Email delivery
✅ SMTP_PORT - Email port
✅ SMTP_USER - Email credentials
✅ SMTP_PASSWORD - Email password
✅ TWILIO_ACCOUNT_SID - SMS service (optional)
✅ TWILIO_AUTH_TOKEN - SMS auth (optional)
```

**Automated Check Script**:
```python
# scripts/check_env.py
import os
from typing import List, Tuple

REQUIRED_VARS = [
    "DATABASE_URL", "REDIS_URL", "SECRET_KEY",
    "WOMPI_PUBLIC_KEY", "WOMPI_PRIVATE_KEY",
    "PAYU_MERCHANT_ID", "PAYU_API_KEY"
]

def check_environment() -> Tuple[bool, List[str]]:
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)

    return len(missing) == 0, missing

if __name__ == "__main__":
    success, missing = check_environment()
    if not success:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        exit(1)
    print("✅ All required environment variables present")
```

---

### 1.4 Load Testing 📊
**Status**: Required
**Priority**: HIGH
**Effort**: 4-8 hours

**Tool**: Locust
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class MeStoreUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def browse_products(self):
        self.client.get("/api/v1/products/", headers=self.headers)

    @task(2)
    def view_product(self):
        self.client.get("/api/v1/products/1", headers=self.headers)

    @task(1)
    def create_order(self):
        self.client.post("/api/v1/orders/", headers=self.headers, json={
            "items": [{"product_id": "uuid", "quantity": 1}],
            "shipping_name": "Test User",
            "shipping_phone": "+57 300 1234567",
            "shipping_address": "Calle 123",
            "shipping_city": "Bogotá",
            "shipping_state": "Cundinamarca"
        })
```

**Run Load Test**:
```bash
# Install
pip install locust

# Run with 100 concurrent users
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10 --host http://localhost:8000
```

**Success Criteria**:
- ✅ 100 concurrent users sustained
- ✅ < 500ms average response time
- ✅ < 1% error rate
- ✅ Database connections stable

---

## 🚀 PHASE 2: BACKEND CART (Week 2-3)
**Priority**: MEDIUM
**Timeline**: 1-2 weeks
**Effort**: 8-12 hours

### 2.1 Cart Endpoints 🛒

**New Model**:
```python
# app/models/cart.py
class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=True)  # For guest carts

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Snapshot at add time

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
```

**New Endpoints**:

#### 2.1.1 Get Current Cart
```python
@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current cart with items.
    Creates empty cart if none exists.
    """
    cart = await get_or_create_cart(current_user.id, db)
    return CartResponse.from_orm(cart)
```

#### 2.1.2 Add Item to Cart
```python
@router.post("/items", status_code=201)
async def add_to_cart(
    item: AddToCartRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add product to cart.
    - Validates product exists and is available
    - Checks stock availability
    - Updates quantity if item already in cart
    """
    # Get cart
    cart = await get_or_create_cart(current_user.id, db)

    # Validate product
    product = await get_product_or_404(item.product_id, db)
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(400, "Product not available")

    # Check stock
    if product.get_stock_disponible() < item.quantity:
        raise HTTPException(400, "Insufficient stock")

    # Add or update item
    existing_item = next(
        (i for i in cart.items if i.product_id == item.product_id),
        None
    )

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.precio_venta
        )
        db.add(cart_item)

    await db.commit()

    return {"success": True, "cart": CartResponse.from_orm(cart)}
```

#### 2.1.3 Update Cart Item
```python
@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update item quantity in cart."""
    cart = await get_user_cart(current_user.id, db)
    item = next((i for i in cart.items if i.id == item_id), None)

    if not item:
        raise HTTPException(404, "Item not in cart")

    # Validate stock
    if item.product.get_stock_disponible() < quantity:
        raise HTTPException(400, "Insufficient stock")

    item.quantity = quantity
    await db.commit()

    return {"success": True, "cart": CartResponse.from_orm(cart)}
```

#### 2.1.4 Remove Item
```python
@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart."""
    cart = await get_user_cart(current_user.id, db)
    item = next((i for i in cart.items if i.id == item_id), None)

    if not item:
        raise HTTPException(404, "Item not in cart")

    await db.delete(item)
    await db.commit()

    return {"success": True, "cart": CartResponse.from_orm(cart)}
```

#### 2.1.5 Clear Cart
```python
@router.delete("/")
async def clear_cart(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from cart."""
    cart = await get_user_cart(current_user.id, db)

    for item in cart.items:
        await db.delete(item)

    await db.commit()

    return {"success": True, "message": "Cart cleared"}
```

**Migration**:
```bash
alembic revision --autogenerate -m "Add cart and cart_items tables"
alembic upgrade head
```

---

## 📦 PHASE 3: VENDOR ENHANCEMENTS (Week 3-4)
**Priority**: MEDIUM
**Timeline**: 1 week
**Effort**: 6-8 hours

### 3.1 Vendor Profile Endpoints 👤

#### 3.1.1 Get Vendor Profile
```python
@router.get("/{vendor_id}", response_model=VendorProfileResponse)
async def get_vendor_profile(
    vendor_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get vendor public profile.
    Includes: business info, product count, rating, since date.
    """
    vendor = await get_user_or_404(vendor_id, db)

    if vendor.user_type != UserType.VENDOR:
        raise HTTPException(404, "Vendor not found")

    # Get vendor stats
    product_count = await get_vendor_product_count(vendor_id, db)
    avg_rating = await get_vendor_avg_rating(vendor_id, db)

    return VendorProfileResponse(
        id=vendor.id,
        business_name=vendor.business_name,
        city=vendor.city,
        primary_category=vendor.primary_category,
        product_count=product_count,
        avg_rating=avg_rating,
        member_since=vendor.created_at
    )
```

#### 3.1.2 Update Vendor Profile
```python
@router.put("/profile", status_code=200)
async def update_vendor_profile(
    profile_data: VendorProfileUpdate,
    current_user: UserRead = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Update vendor profile (own profile only).
    Allows updating: business_name, description, phone, city.
    """
    vendor = await get_user_or_404(current_user.id, db)

    # Update allowed fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(vendor, field, value)

    await db.commit()

    return {"success": True, "vendor": VendorProfileResponse.from_orm(vendor)}
```

#### 3.1.3 Vendor Analytics
```python
@router.get("/analytics/dashboard")
async def get_vendor_analytics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: UserRead = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive vendor analytics.

    Returns:
    - Total sales (revenue)
    - Number of orders
    - Top products
    - Pending commissions
    - Customer reviews
    """
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Query vendor orders
    orders = await get_vendor_orders(current_user.id, date_from, date_to, db)

    # Calculate metrics
    total_revenue = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    avg_order_value = total_revenue / total_orders if total_orders else 0

    # Top products
    top_products = await get_top_products(current_user.id, date_from, date_to, db)

    # Pending commissions
    pending_commissions = await get_pending_commissions(current_user.id, db)

    return {
        "period": {"from": date_from, "to": date_to},
        "revenue": {
            "total": total_revenue,
            "avg_order_value": avg_order_value
        },
        "orders": {
            "total": total_orders,
            "by_status": await count_orders_by_status(current_user.id, db)
        },
        "top_products": top_products,
        "commissions": {
            "pending": pending_commissions,
            "total_pending_amount": sum(c.amount for c in pending_commissions)
        }
    }
```

---

## 🎨 PHASE 4: ADVANCED FEATURES (Month 2)
**Priority**: LOW
**Timeline**: 2-4 weeks
**Effort**: 20-40 hours

### 4.1 Product Reviews 📝

**New Model**:
```python
class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)

    verified_purchase = Column(Boolean, default=True)
    helpful_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="reviews")
    user = relationship("User")
    order = relationship("Order")
```

**Endpoints**:
```
POST   /api/v1/products/{id}/reviews    # Create review
GET    /api/v1/products/{id}/reviews    # List reviews
PUT    /api/v1/reviews/{id}             # Update review
DELETE /api/v1/reviews/{id}             # Delete review
POST   /api/v1/reviews/{id}/helpful     # Mark helpful
```

---

### 4.2 Admin Order Management 🔧

**Endpoints**:
```
GET  /api/v1/admin/orders              # All orders (paginated)
GET  /api/v1/admin/orders/stats        # Order statistics
PUT  /api/v1/admin/orders/{id}/status  # Update status
POST /api/v1/admin/orders/{id}/refund  # Process refund
GET  /api/v1/admin/vendors             # All vendors
PUT  /api/v1/admin/vendors/{id}/status # Approve/suspend vendor
```

---

### 4.3 Advanced Search & Filters 🔍

**Features**:
- Faceted search (category, price, rating)
- Auto-complete suggestions
- Search history
- Saved searches
- Price alerts

---

### 4.4 Notification System 🔔

**Channels**:
- Email notifications
- SMS notifications
- In-app notifications
- Push notifications (mobile)

**Events**:
- Order status updates
- Payment confirmations
- Product price drops
- Low stock alerts (vendors)
- Commission payouts

---

## 📊 IMPLEMENTATION PRIORITY MATRIX

| Feature | Priority | Effort | Impact | Timeline |
|---------|----------|--------|--------|----------|
| Global Rate Limiting | HIGH | 2-4h | HIGH | Week 1 |
| Order Updates | MEDIUM | 3-5h | MEDIUM | Week 1 |
| Environment Audit | HIGH | 1h | HIGH | Week 1 |
| Load Testing | HIGH | 4-8h | HIGH | Week 1 |
| Backend Cart | MEDIUM | 8-12h | MEDIUM | Week 2-3 |
| Vendor Profile | MEDIUM | 6-8h | MEDIUM | Week 3-4 |
| Product Reviews | LOW | 12-16h | MEDIUM | Month 2 |
| Admin Management | LOW | 8-12h | LOW | Month 2 |
| Advanced Search | LOW | 16-24h | MEDIUM | Month 2 |
| Notifications | LOW | 20-30h | HIGH | Month 2 |

---

## 🎯 SUCCESS METRICS

### Phase 1 (Week 1) - Critical Fixes
- ✅ Rate limiting implemented (100% endpoints)
- ✅ Load test passed (100 users, <500ms)
- ✅ All env vars validated
- ✅ Order updates working

### Phase 2 (Week 2-3) - Cart Enhancement
- ✅ Cart endpoints operational
- ✅ Session persistence working
- ✅ Stock validation in cart
- ✅ Abandoned cart tracking

### Phase 3 (Week 3-4) - Vendor Features
- ✅ Vendor profiles public
- ✅ Analytics dashboard functional
- ✅ Commission tracking accurate

### Phase 4 (Month 2) - Advanced
- ✅ Review system live
- ✅ Admin tools operational
- ✅ Notifications sending
- ✅ Advanced search working

---

**Document Version**: 1.0
**Last Updated**: 2025-10-03
**Next Review**: After Phase 1 completion
