# STOCK FIX - POST-EXECUTION VALIDATION PLAN
**Agent**: backend-framework-ai
**Date**: 2025-10-02
**Purpose**: Comprehensive validation checklist after applying stock fix

---

## PRE-EXECUTION CHECKLIST

Before running the fix script:

- [ ] Backend server is running: `http://192.168.1.137:8000`
- [ ] Frontend server is running: `http://192.168.1.137:5173`
- [ ] Database is accessible and healthy
- [ ] Admin credentials available: `admin@mestocker.com / Admin123456`

---

## EXECUTION STEPS

### Step 1: Run Fix Script
```bash
cd /home/admin-jairo/MeStore
python scripts/fix_pending_products_status.py
```

Expected output:
```
ANALYZING PENDING PRODUCTS
Found 6 PENDING products to update

DRY RUN MODE - No changes will be committed
Run with dry_run=False to apply changes

Do you want to apply these changes? (yes/no): yes

✅ SUCCESS
  Updated: 6 products
  APPROVED products now: 25
  PENDING products remaining: 0
```

---

## POST-EXECUTION VALIDATION

### 1. Database Verification (Backend)

#### Test A: Product Count by Status
```bash
python -c "
import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus

async def verify():
    async with AsyncSessionLocal() as session:
        for status in [ProductStatus.PENDING, ProductStatus.APPROVED]:
            result = await session.execute(
                select(func.count(Product.id)).where(Product.status == status)
            )
            print(f'{status.value}: {result.scalar()} products')

asyncio.run(verify())
"
```

**Expected**:
```
PENDING: 0 products
APPROVED: 25 products
```

#### Test B: Stock Availability
```bash
python -c "
import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.inventory import Inventory

async def verify():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.sum(Inventory.cantidad)))
        total = result.scalar()
        result = await session.execute(
            select(func.sum(Inventory.cantidad - Inventory.cantidad_reservada))
        )
        available = result.scalar()
        print(f'Total Stock: {total}')
        print(f'Available Stock: {available}')

asyncio.run(verify())
"
```

**Expected**:
```
Total Stock: 1250
Available Stock: 1250
```

---

### 2. API Verification (Backend Endpoints)

#### Test C: Public Product Listing (Unauthenticated)
```bash
curl -X GET "http://192.168.1.137:8000/api/v1/products/?page=1&limit=100" \
  -H "Content-Type: application/json" | jq '.pagination.total'
```

**Expected**: `25` (all products visible)

#### Test D: Product Detail with Stock
```bash
# Get first product ID
PRODUCT_ID=$(curl -s "http://192.168.1.137:8000/api/v1/products/?limit=1" | jq -r '.data[0].id')

# Get product details
curl -X GET "http://192.168.1.137:8000/api/v1/products/${PRODUCT_ID}" \
  -H "Content-Type: application/json" | jq '{id, sku, name, status, stock_quantity}'
```

**Expected**:
```json
{
  "id": "...",
  "sku": "PROD-001",
  "name": "iPhone 14 Pro Max",
  "status": "APPROVED",
  "stock_quantity": 50
}
```

---

### 3. Frontend Verification (User Interface)

#### Test E: Product Listing Page
1. Open browser: `http://192.168.1.137:5173`
2. Navigate to Products page
3. **Verify**:
   - [ ] 25 products displayed (not 19)
   - [ ] Stock quantities show correctly (e.g., "50 in stock")
   - [ ] All products have "Add to Cart" button enabled
   - [ ] No "Out of Stock" messages

#### Test F: Product Detail Page
1. Click on any product
2. **Verify**:
   - [ ] Product details load
   - [ ] Stock quantity displayed
   - [ ] Price displayed correctly
   - [ ] "Add to Cart" button enabled
   - [ ] No stock errors in console

---

### 4. Cart & Checkout Verification

#### Test G: Add to Cart
1. Click "Add to Cart" on product with stock
2. **Verify**:
   - [ ] Success notification appears
   - [ ] Cart badge updates with item count
   - [ ] Cart sidebar shows product
   - [ ] Stock quantity displayed in cart

#### Test H: Checkout Flow (CRITICAL)
1. Open cart with products
2. Click "Proceed to Checkout"
3. **Verify**:
   - [ ] Checkout page loads
   - [ ] Products display with stock
   - [ ] Quantity selector works
   - [ ] Total price calculates correctly
   - [ ] No stock errors in console

#### Test I: Complete Order (Full E2E)
1. Fill shipping information
2. Select payment method (PSE or Efecty)
3. Submit order
4. **Verify**:
   - [ ] Order created successfully
   - [ ] Order ID received
   - [ ] Confirmation page displays
   - [ ] Stock reserved in database
   - [ ] No 400/403 errors

---

### 5. Stock Reservation Verification

#### Test J: Check Stock After Order
```bash
# Check if stock was reserved after order creation
python -c "
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.inventory import Inventory

async def verify():
    async with AsyncSessionLocal() as session:
        stmt = select(Inventory).limit(5)
        result = await session.execute(stmt)
        inventories = result.scalars().all()

        for inv in inventories:
            print(f'{inv.get_ubicacion_completa()}: Total={inv.cantidad}, Reserved={inv.cantidad_reservada}, Available={inv.cantidad_disponible()}')

asyncio.run(verify())
"
```

**Expected**: Some inventory should show `cantidad_reservada > 0` after order

---

### 6. Error Scenarios (Negative Testing)

#### Test K: Out of Stock Behavior
1. Try to add 1000 units of a product with only 50 in stock
2. **Verify**:
   - [ ] Error message: "Insufficient stock"
   - [ ] Cart does not update
   - [ ] Stock reservation does not occur

#### Test L: Deleted Products
```bash
# Soft-deleted products should not appear
curl -X GET "http://192.168.1.137:8000/api/v1/products/" \
  -H "Content-Type: application/json" | jq '.data[] | select(.deleted_at != null)'
```

**Expected**: Empty array (no deleted products in listing)

---

## SUCCESS CRITERIA

All of the following must be TRUE:

✅ **Database Level**
- [ ] 0 PENDING products
- [ ] 25 APPROVED products
- [ ] 1,250 total stock units
- [ ] 1,250 available stock units (before orders)

✅ **API Level**
- [ ] GET /products/ returns 25 products for public users
- [ ] Individual product endpoints return stock_quantity
- [ ] No 404/403 errors for APPROVED products

✅ **Frontend Level**
- [ ] Product listing shows 25 products
- [ ] Stock quantities display correctly
- [ ] Cart functionality works
- [ ] Checkout page loads with products

✅ **E2E Flow**
- [ ] Complete checkout flow succeeds
- [ ] Order creation works
- [ ] Stock reservation occurs
- [ ] No errors in browser console

---

## ROLLBACK PLAN

If validation fails, rollback with:

```bash
python -c "
import asyncio
from sqlalchemy import update
from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus

async def rollback():
    async with AsyncSessionLocal() as session:
        # Get IDs of products that were updated
        # (This assumes you have the IDs from the fix script output)
        product_ids = [
            # Add IDs of products that were changed
        ]

        stmt = (
            update(Product)
            .where(Product.id.in_(product_ids))
            .values(status=ProductStatus.PENDING)
        )

        await session.execute(stmt)
        await session.commit()
        print('Rollback completed')

asyncio.run(rollback())
"
```

---

## TROUBLESHOOTING

### Issue: Products still not visible in frontend
**Check**:
1. Clear browser cache (Ctrl+Shift+R)
2. Verify API returns updated status
3. Check frontend is calling correct API endpoint
4. Verify no JavaScript errors in console

### Issue: Stock shows as 0
**Check**:
1. Verify `ubicaciones_inventario` relationship loaded
2. Check `stock_quantity` calculated in ProductResponse
3. Verify Inventory table has correct data
4. Check selectinload in products.py line 427-430

### Issue: Checkout fails with stock error
**Check**:
1. Verify product status is APPROVED
2. Check inventory has available stock
3. Verify stock reservation logic in order creation
4. Check payment service integration

---

## REPORTING

After validation, report results in this format:

```
STOCK FIX VALIDATION REPORT
Date: 2025-10-02
Agent: backend-framework-ai

Database Validation: ✅ PASS / ❌ FAIL
API Validation: ✅ PASS / ❌ FAIL
Frontend Validation: ✅ PASS / ❌ FAIL
E2E Checkout: ✅ PASS / ❌ FAIL

Issues Found:
- [List any issues]

Recommendations:
- [List any follow-up actions]
```

---

**Agent**: backend-framework-ai
**Status**: Validation Plan Ready ✅
**Execute After**: Running fix_pending_products_status.py
