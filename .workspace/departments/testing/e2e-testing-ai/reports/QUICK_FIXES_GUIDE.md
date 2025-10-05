# ⚡ Quick Fixes Guide - E2E Testing Issues

**Generated**: 2025-10-03 by E2E Testing AI
**Priority**: URGENT - Action Required Before Production

---

## 🚨 CRITICAL ISSUES - Fix Immediately

### Issue #1: Database Schema Mismatch ✅ FIXED

**Problem**: `cancelled_at` column missing from orders table

**Fix Applied**:
```bash
cd /home/admin-jairo/MeStore
sqlite3 mestore.db "ALTER TABLE orders ADD COLUMN cancelled_at DATETIME;"
sqlite3 mestore.db "ALTER TABLE orders ADD COLUMN cancellation_reason TEXT;"
```

**Verify Fix**:
```bash
sqlite3 mestore.db ".schema orders" | grep -i cancel
# Should show: cancelled_at DATETIME, cancellation_reason TEXT
```

**Status**: ✅ COMPLETED

---

### Issue #2: Product-Order Type Mismatch 🚨 ACTIVE

**Problem**: Cannot link order items to products due to type mismatch

**Root Cause**:
```
products.id        → VARCHAR(36)  # UUID string
order_items.product_id → INTEGER      # Numeric foreign key
```

**Impact**:
- ❌ Cannot create test orders programmatically
- ❌ Foreign key relationship broken
- ⚠️ Potential production data integrity issue

**Recommended Fix** (Choose ONE approach):

#### Option A: Change product_id to VARCHAR (Recommended)
```sql
-- 1. Create backup
cp mestore.db mestore.db.backup

-- 2. Create new order_items table with correct type
CREATE TABLE order_items_new (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id VARCHAR(36) NOT NULL,  -- Changed from INTEGER
    product_name VARCHAR(500) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    product_image_url VARCHAR(1000),
    unit_price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    variant_attributes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 3. Copy existing data (if any)
INSERT INTO order_items_new SELECT * FROM order_items;

-- 4. Drop old table and rename
DROP TABLE order_items;
ALTER TABLE order_items_new RENAME TO order_items;
```

#### Option B: Add numeric ID to products (Alternative)
```sql
-- Add auto-increment ID to products
ALTER TABLE products ADD COLUMN numeric_id INTEGER;
-- Then update order_items to use numeric_id
```

**Action Required**: Database architect must review and implement

---

## ⚠️ HIGH PRIORITY - Fix This Week

### Issue #3: Missing Test Data Infrastructure

**Problem**: No test orders for E2E validation

**Quick Fix Script Created**: `create_test_orders.py`
**Status**: ⏳ Blocked by Issue #2 (product_id type mismatch)

**Temporary Workaround** - Manual Order Creation:
```sql
-- After fixing product_id type, run:
INSERT INTO orders (
    order_number, buyer_id, subtotal, tax_amount, shipping_cost,
    discount_amount, total_amount, status, created_at,
    shipping_name, shipping_phone, shipping_address,
    shipping_city, shipping_state, shipping_country
) VALUES (
    'TEST-001', '655c3dee-7879-4380-8fbd-151f7f80187a',
    100000, 19000, 15000, 0, 134000,
    'confirmed', datetime('now'),
    'Test Buyer', '+57 300 123 4567', 'Calle 123 #45-67',
    'Bogotá', 'Cundinamarca', 'CO'
);
```

**Permanent Solution**:
1. Fix product_id type issue
2. Run seeding script: `python3 create_test_orders.py`
3. Integrate seeding into development setup

---

## 🔧 Medium Priority - Improve System

### Issue #4: Migration Deployment Process

**Problem**: Alembic migrations not auto-applied

**Current Behavior**:
- Migration exists: `2025_10_03_0614-34bac231e539_add_cancellation_fields_to_orders.py`
- Database missing columns
- Application crashes with 500 errors

**Recommended Fix**:

1. **Add startup validation** in `app/main.py`:
```python
# Add to app/main.py startup event
@app.on_event("startup")
async def validate_database_schema():
    """Validate database schema matches models"""
    from app.database import engine
    from app.models import Base

    # Check if all columns exist
    # If mismatch found, log error and prevent startup
```

2. **Auto-apply migrations** in deployment:
```bash
# Add to deployment script
alembic upgrade head
uvicorn app.main:app --reload
```

3. **Add health check endpoint**:
```python
@router.get("/health/database")
async def database_health():
    """Check database schema health"""
    # Verify critical columns exist
    # Return detailed status
```

---

## 📋 Verification Checklist

After applying fixes, verify with these commands:

### ✅ Step 1: Verify Database Schema
```bash
# Check cancelled_at exists
sqlite3 mestore.db ".schema orders" | grep cancelled_at

# Check product_id type
sqlite3 mestore.db "PRAGMA table_info(order_items);" | grep product_id
```

### ✅ Step 2: Restart Backend
```bash
# Kill existing process
pkill -f "uvicorn app.main:app"

# Restart with fresh schema
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ✅ Step 3: Test Buyer Orders Endpoint
```bash
# Login as buyer
TOKEN=$(curl -s -X POST http://192.168.1.137:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"comprador@test.com","password":"Test123456"}' \
  | jq -r '.access_token')

# Get orders (should return 200, not 500)
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.1.137:8000/api/v1/orders/
```

### ✅ Step 4: Test Admin Orders Endpoint
```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://192.168.1.137:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@mestocker.com","password":"Admin123456"}' \
  | jq -r '.access_token')

# Get admin orders (should return 200)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://192.168.1.137:8000/api/v1/admin/orders?page=1&page_size=10
```

### ✅ Step 5: Re-run E2E Test Suite
```bash
cd /home/admin-jairo/MeStore
python3 .workspace/departments/testing/e2e-testing-ai/reports/comprehensive_e2e_test_suite.py

# Expected: Higher pass rate after fixes
```

---

## 🎯 Success Criteria

After applying all fixes, you should see:

**E2E Test Results**:
```
✅ PASSED:  10+ tests (>80%)
❌ FAILED:  <3 tests (<20%)
⏳ BLOCKED: 0 tests
```

**API Responses**:
- ✅ `GET /api/v1/orders/` → 200 OK (not 500)
- ✅ `GET /api/v1/admin/orders` → 200 OK (not 500)
- ✅ `GET /api/v1/admin/orders/stats/dashboard` → 200 OK

**Database State**:
- ✅ All migrations applied
- ✅ Schema matches models
- ✅ Foreign keys valid
- ✅ Test data available

---

## 📞 Who to Contact

### For Database Issues (Issue #2)
**Contact**: database-architect-ai
**Files**: `/home/admin-jairo/MeStore/app/models/`
**Command**:
```bash
python .workspace/scripts/contact_responsible_agent.py \
  e2e-testing-ai app/models/order.py \
  "Need to fix product_id type mismatch between products and order_items"
```

### For Migration Issues (Issue #4)
**Contact**: backend-framework-ai
**Files**: `/home/admin-jairo/MeStore/alembic/`
**Command**:
```bash
python .workspace/scripts/contact_responsible_agent.py \
  e2e-testing-ai alembic/env.py \
  "Need to ensure migrations auto-apply on startup"
```

### For E2E Testing Support
**Contact**: tdd-specialist
**Files**: `/home/admin-jairo/MeStore/tests/`
**Office**: `.workspace/departments/testing/tdd-specialist/`

---

## 📚 Related Documentation

- **Full E2E Report**: `E2E_TEST_FINDINGS_REPORT.md`
- **Executive Summary**: `E2E_EXECUTIVE_SUMMARY.md`
- **Test Suite**: `comprehensive_e2e_test_suite.py`
- **Seeding Script**: `create_test_orders.py`
- **JSON Results**: `e2e_report_*.json`

---

## ⏱️ Estimated Time to Fix

| Issue | Priority | Effort | ETA |
|-------|----------|--------|-----|
| Schema mismatch | CRITICAL | ✅ Done | Completed |
| Product type mismatch | CRITICAL | 2-4 hours | Today |
| Test data setup | HIGH | 1 hour | After fix #2 |
| Migration automation | MEDIUM | 2-3 hours | This week |

**Total**: ~6 hours to resolve all critical issues

---

**Generated by**: E2E Testing AI
**Last Updated**: 2025-10-03 15:30 UTC
**Status**: Ready for action
