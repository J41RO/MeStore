# Orders Endpoint Restoration Plan

**Date**: 2025-10-01
**Agent**: backend-framework-ai
**Priority**: CRITICAL
**Status**: PLANNING COMPLETED

---

## Current State Analysis

### Temporary Implementation Review
**File**: `app/api/v1/endpoints/orders.py` (165 lines)

**What Works:**
- ✅ Basic endpoint structure with FastAPI router
- ✅ Authentication integration with `get_current_user_for_orders`
- ✅ Health check endpoint functional
- ✅ Mock order creation returns valid response structure
- ✅ No timeout issues (simplified version)

**Critical Missing Features:**
- ❌ NO database persistence - orders not saved
- ❌ NO stock validation - accepts any quantity
- ❌ NO order_items creation - items only in response JSON
- ❌ NO real payment processing integration
- ❌ NO totals calculation (IVA, shipping)
- ❌ Returns empty array for GET /orders
- ❌ Only mock data for POST /orders

**Reason for Temporary Implementation:**
According to header comment: "timeout issue resolved" by simplifying. Original version backed up as `orders.py.broken.backup` (not found in codebase).

---

## Database Schema Analysis

### Available Models

#### 1. Order Model (`app/models/order.py`)
```python
class Order(Base):
    __tablename__ = "orders"

    # Core fields
    id: Integer (primary key)
    order_number: String(50) (unique, indexed)
    buyer_id: String(36) (FK to users.id)

    # Totals
    subtotal: Float
    tax_amount: Float
    shipping_cost: Float
    discount_amount: Float
    total_amount: Float

    # Status & Dates
    status: Enum(OrderStatus) - PENDING, CONFIRMED, PROCESSING, etc.
    created_at, updated_at, confirmed_at, shipped_at, delivered_at

    # Shipping info
    shipping_name, shipping_phone, shipping_email
    shipping_address, shipping_city, shipping_state
    shipping_postal_code, shipping_country (default: "CO")
    notes: Text

    # Relationships
    buyer: relationship(User)
    items: relationship(OrderItem) - CASCADE delete
    transactions: relationship(OrderTransaction)
    commissions: relationship(Commission) - CASCADE delete
```

#### 2. OrderItem Model (`app/models/order.py`)
```python
class OrderItem(Base):
    __tablename__ = "order_items"

    # Core fields
    id: Integer (primary key)
    order_id: Integer (FK to orders.id)
    product_id: Integer (FK to products.id)

    # Snapshot of product at purchase time
    product_name: String(500)
    product_sku: String(100)
    product_image_url: String(1000)

    # Pricing
    unit_price: Float
    quantity: Integer
    total_price: Float
    variant_attributes: Text (JSON string)

    # Relationships
    order: relationship(Order)
    product: relationship(Product)
```

#### 3. Product Model (`app/models/product.py`)
```python
class Product(BaseModel):
    __tablename__ = "products"

    # Core fields
    id: String(36) (UUID primary key)
    sku: String(50) (unique, indexed)
    name: String(200)
    description: Text
    status: Enum(ProductStatus)

    # Pricing
    precio_venta: DECIMAL(10, 2)
    precio_costo: DECIMAL(10, 2)
    comision_mestocker: DECIMAL(10, 2)

    # Stock methods
    get_stock_total() -> int
    get_stock_disponible() -> int
    get_stock_reservado() -> int
    tiene_stock_disponible() -> bool
    buscar_ubicacion_disponible(cantidad) -> Optional[Inventory]

    # Relationships
    ubicaciones_inventario: relationship(Inventory)
    vendedor: relationship(User)
```

### Schema Compatibility Issues

**CRITICAL DISCREPANCY FOUND:**
- Order model uses `Integer` primary key
- Product model uses `String(36)` UUID primary key
- OrderItem.product_id is `Integer` but Product.id is `String(36)`

**Resolution**: Use `product_sku` or adapt query to handle UUID strings correctly.

---

## Proposed Solution

### Strategy: **REWRITE with Performance Optimizations**

**Justification:**
1. No backup file found (`orders.py.broken.backup` missing)
2. Current implementation is minimal placeholder
3. Need to build complete solution from scratch
4. Focus on performance to avoid timeout issues
5. Leverage existing database models and relationships

### Performance Optimizations

**Timeout Prevention Strategy:**
1. **Eager Loading**: Use `selectinload` for relationships
2. **Batch Operations**: Insert all order_items in single transaction
3. **Minimal Queries**: Fetch all products in one query
4. **Transaction Optimization**: Use `begin()` context manager
5. **Connection Pooling**: Leverage existing async SQLAlchemy setup
6. **Query Optimization**: Avoid N+1 queries with proper joins

---

## API Endpoint Specification

### POST /api/v1/orders
**Purpose**: Create new order with full database persistence

**Request Body:**
```json
{
  "items": [
    {
      "product_id": "uuid-string-36-chars",
      "quantity": 2
    }
  ],
  "shipping_name": "Juan Pérez",
  "shipping_phone": "+57 300 1234567",
  "shipping_email": "juan@example.com",
  "shipping_address": "Calle 123 #45-67, Apto 401",
  "shipping_city": "Bogotá",
  "shipping_state": "Cundinamarca",
  "shipping_postal_code": "110111",
  "notes": "Entregar en la mañana"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "order_number": "ORD-20251001-ABC12345",
    "buyer_id": "user-uuid",
    "status": "pending",
    "subtotal": 100000.00,
    "tax_amount": 19000.00,
    "shipping_cost": 15000.00,
    "discount_amount": 0.00,
    "total_amount": 134000.00,
    "created_at": "2025-10-01T10:30:00Z",
    "shipping_info": {
      "name": "Juan Pérez",
      "phone": "+57 300 1234567",
      "address": "Calle 123 #45-67, Apto 401",
      "city": "Bogotá",
      "state": "Cundinamarca"
    },
    "items": [
      {
        "product_id": "uuid",
        "product_name": "Producto Ejemplo",
        "product_sku": "SKU-001",
        "quantity": 2,
        "unit_price": 50000.00,
        "total_price": 100000.00
      }
    ]
  },
  "message": "Order created successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data, insufficient stock
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Database error

---

## Implementation Steps

### Phase 1: Core Order Creation Logic

1. **Validate Authentication**
   - Use existing `get_current_user_for_orders` dependency
   - Extract buyer_id from current_user

2. **Validate Request Data**
   - Items list not empty
   - All product_ids are valid UUIDs
   - Quantities > 0

3. **Fetch Products with Stock**
   - Query all product_ids in single query
   - Eager load `ubicaciones_inventario` for stock info
   - Validate all products exist

4. **Stock Validation**
   - For each item, check `product.get_stock_disponible() >= quantity`
   - Collect all stock errors before failing
   - Return clear error message with product names

### Phase 2: Total Calculations

5. **Calculate Subtotal**
   ```python
   subtotal = sum(product.precio_venta * item.quantity for item in items)
   ```

6. **Calculate Tax (IVA 19%)**
   ```python
   tax_amount = subtotal * Decimal('0.19')
   ```

7. **Calculate Shipping**
   ```python
   # Free shipping for orders >= 200,000 COP
   shipping_cost = Decimal('0.00') if subtotal >= 200000 else Decimal('15000.00')
   ```

8. **Calculate Total**
   ```python
   total_amount = subtotal + tax_amount + shipping_cost
   ```

### Phase 3: Database Persistence

9. **Generate Order Number**
   ```python
   import uuid
   from datetime import datetime

   order_id = uuid.uuid4()
   order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{order_id.hex[:8].upper()}"
   ```

10. **Create Order in Transaction**
    ```python
    async with db.begin():
        # Create Order
        new_order = Order(
            order_number=order_number,
            buyer_id=current_user.id,
            subtotal=float(subtotal),
            tax_amount=float(tax_amount),
            shipping_cost=float(shipping_cost),
            discount_amount=0.0,
            total_amount=float(total_amount),
            status=OrderStatus.PENDING,
            shipping_name=order_data.shipping_name,
            shipping_phone=order_data.shipping_phone,
            shipping_email=order_data.get('shipping_email'),
            shipping_address=order_data.shipping_address,
            shipping_city=order_data.shipping_city,
            shipping_state=order_data.shipping_state,
            shipping_postal_code=order_data.get('shipping_postal_code'),
            shipping_country="CO",
            notes=order_data.get('notes')
        )
        db.add(new_order)
        await db.flush()  # Get order.id

        # Create OrderItems
        for item in items:
            product = products_dict[item.product_id]
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,  # Handle UUID/Integer conversion
                product_name=product.name,
                product_sku=product.sku,
                product_image_url=None,  # TODO: Add from product.images
                unit_price=float(product.precio_venta),
                quantity=item.quantity,
                total_price=float(product.precio_venta * item.quantity),
                variant_attributes=None
            )
            db.add(order_item)

        await db.commit()
        await db.refresh(new_order)
    ```

### Phase 4: Response Formatting

11. **Eager Load Relationships**
    ```python
    await db.refresh(new_order, ['items', 'buyer'])
    ```

12. **Format Response**
    - Include all order details
    - Format items with product info
    - Return shipping info structured

---

## Error Handling Strategy

### Validation Errors (400)
```python
# Product not found
if missing_products:
    raise HTTPException(
        status_code=400,
        detail=f"Products not found: {', '.join(missing_products)}"
    )

# Insufficient stock
if stock_errors:
    raise HTTPException(
        status_code=400,
        detail=f"Insufficient stock: {', '.join(stock_errors)}"
    )

# Empty cart
if not items:
    raise HTTPException(
        status_code=400,
        detail="Cart is empty. Add at least one item."
    )
```

### Database Errors (500)
```python
try:
    async with db.begin():
        # Order creation logic
        pass
except IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Order creation failed. Please try again."
    )
except Exception as e:
    logger.error(f"Unexpected error creating order: {e}")
    raise HTTPException(
        status_code=500,
        detail="An unexpected error occurred."
    )
```

---

## Testing Strategy

### Unit Tests
```python
# Test stock validation
def test_create_order_insufficient_stock()

# Test total calculations
def test_calculate_totals_with_iva()

# Test shipping cost logic
def test_free_shipping_over_threshold()
```

### Integration Tests
```python
# Test full order creation flow
async def test_create_order_complete_flow()

# Test database persistence
async def test_order_persisted_in_database()

# Test order items creation
async def test_order_items_created_correctly()
```

### Manual Testing
```bash
# Test with real token
curl -X POST "http://192.168.1.137:8000/api/v1/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_order.json
```

---

## Migration Considerations

### Frontend Compatibility
- Maintain existing request format
- Keep response structure compatible
- Add new fields as optional

### Database Migrations
- No new tables needed (all exist)
- Verify foreign key constraints
- Check indexes on orders table

### Rollback Plan
- Keep temporary implementation as backup
- Document all changes
- Easy revert with git

---

## Risk Assessment

### High Risk Items
1. **Product ID Type Mismatch**: OrderItem expects Integer, Product uses UUID
   - **Mitigation**: Store product_sku instead, or adapt FK

2. **Timeout on Large Orders**: Multiple products could cause slow query
   - **Mitigation**: Use eager loading, batch operations, limit items per order

3. **Concurrent Order Creation**: Race condition on stock
   - **Mitigation**: Database transaction isolation, stock locking

### Medium Risk Items
1. **Price Changes**: Product price could change between cart and order
   - **Mitigation**: Snapshot current price in order_items

2. **Stock Validation**: Stock could change during order creation
   - **Mitigation**: Use SELECT FOR UPDATE on inventory

---

## Success Criteria

- ✅ Orders persist in `orders` table with all fields
- ✅ OrderItems created in `order_items` table with relationships
- ✅ Stock validation against real inventory working
- ✅ Total calculations accurate (subtotal + IVA 19% + shipping)
- ✅ Transaction handling ensures atomicity
- ✅ No timeout issues (response < 2 seconds)
- ✅ Frontend continues working without changes
- ✅ Manual testing with curl succeeds
- ✅ Database verification shows correct data

---

## Next Phase: Implementation

**Ready to proceed with implementation using this plan.**

---

**Plan Approval**: ✅ READY FOR IMPLEMENTATION
**Estimated Implementation Time**: 2-3 hours
**Estimated Testing Time**: 1 hour
**Total Timeline**: 3-4 hours

