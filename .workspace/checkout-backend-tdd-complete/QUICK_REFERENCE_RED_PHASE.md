# QUICK REFERENCE - RED PHASE COMPLETE

**Status**: ✅ COMPLETE
**Date**: 2025-10-09
**Commit**: 7ea9c2a9

---

## 📁 FILES CREATED

```bash
tests/unit/orders/
├── test_order_security_vendor_validation.py  # 473 LOC, 9 tests
├── test_order_authentication.py              # 595 LOC, 11 tests
└── test_order_authorization.py               # 553 LOC, 8 tests

tests/fixtures/orders/
└── conftest.py                               # 396 LOC, shared fixtures

.workspace/checkout-backend-tdd-complete/
├── CHECKOUT_MAP.md                           # Discovery phase
├── COVERAGE_BASELINE.md                      # Pre-TDD state
├── RED_PHASE_RESULTS.md                      # Detailed analysis
├── EXECUTIVE_SUMMARY_RED_PHASE.md            # Executive overview
└── QUICK_REFERENCE_RED_PHASE.md              # This file
```

**Total**: 1621 lines of test code + 396 lines fixtures

---

## 🧪 TEST COMMANDS

### Run All RED Phase Tests
```bash
python -m pytest tests/unit/orders/ -v -m "tdd and red_test"
```

### Run Specific Category
```bash
# Vendor validation only
python -m pytest tests/unit/orders/test_order_security_vendor_validation.py -v

# Authentication only
python -m pytest tests/unit/orders/test_order_authentication.py -v

# Authorization only
python -m pytest tests/unit/orders/test_order_authorization.py -v
```

### Run Single Test
```bash
python -m pytest tests/unit/orders/test_order_security_vendor_validation.py::test_vendor_token_rejected_with_403 -v
```

### With Coverage
```bash
python -m pytest tests/unit/orders/ --cov=app.api.v1.endpoints.orders --cov-report=term-missing -m "tdd and red_test"
```

---

## 🔴 CRITICAL BUGS TO FIX (GREEN Phase)

### Bug #1: Async Query Crash
```python
# File: app/api/v1/endpoints/orders.py
# Line: 418

# ❌ BROKEN (current):
result = await db.execute(query)

# ✅ FIX (option 1):
query = select(Product).where(Product.id.in_(product_ids))
result = await db.execute(query)

# ✅ FIX (option 2):
result = await db.execute(
    select(Product)
    .where(Product.id.in_(product_ids))
    .options(selectinload(Product.ubicaciones_inventario))
)
```

### Bug #2: Wrong Status Code
```python
# File: app/api/v1/endpoints/orders.py
# Line: 42-44

# Current: Returns 403 for missing auth
# Expected: Should return 401

# Research: Check FastAPI HTTPBearer configuration
# Or: Implement custom authentication dependency
```

---

## 📊 TEST METRICS

| Category | Tests | LOC | Status |
|----------|-------|-----|--------|
| Vendor Validation | 9 | 473 | ✅ Created |
| Authentication | 11 | 595 | ✅ Created |
| Authorization | 8 | 553 | ✅ Created |
| **Total** | **27** | **1621** | **✅ Complete** |

---

## 🎯 CRITICAL TEST CASES

### Must Pass in GREEN Phase

1. **test_vendor_token_rejected_with_403**
   - VENDOR must get 403, not 500
   - Currently: 500 (async bug)
   - Priority: CRITICAL

2. **test_no_token_returns_401**
   - Missing auth must get 401, not 403
   - Currently: 403
   - Priority: HIGH

3. **test_user_cannot_view_other_user_order**
   - Ownership validation
   - Currently: Unknown (blocked by async bug)
   - Priority: CRITICAL

4. **test_expired_token_rejected**
   - Token expiration validation
   - Currently: Unknown
   - Priority: HIGH

5. **test_valid_token_accepted**
   - Baseline positive test
   - Currently: Fails (async bug)
   - Priority: HIGH

---

## 🔧 FIXTURES AVAILABLE

Located in: `tests/fixtures/orders/conftest.py`

### User Fixtures
- `customer_user_data` - Customer user data
- `vendor_user_data` - Vendor user data
- `admin_user_data` - Admin user data
- `customer_token` - JWT token for customer
- `vendor_token` - JWT token for vendor
- `admin_token` - JWT token for admin
- `customer_auth_headers` - Auth headers for customer
- `vendor_auth_headers` - Auth headers for vendor
- `admin_auth_headers` - Auth headers for admin

### Product Fixtures
- `product_with_stock_data` - Product with available stock
- `product_without_stock_data` - Product with no stock
- `product_without_price_data` - Product without price

### Order Payload Fixtures
- `valid_order_payload` - Complete valid order data
- `empty_cart_payload` - Order with empty cart
- `missing_shipping_info_payload` - Missing required fields
- `insufficient_stock_payload` - Requesting too much stock
- `invalid_product_id_payload` - Non-existent product
- `multiple_items_payload` - Order with multiple products

### Calculation Fixtures
- `free_shipping_threshold_payload` - Order >= 200k (free shipping)
- `standard_shipping_cost_payload` - Order < 200k (15k shipping)
- `calculate_expected_total` - Helper function for totals

---

## 📋 GREEN PHASE CHECKLIST

### Step 1: Fix Async Bug (2-4 hours)
- [ ] Identify exact query construction issue
- [ ] Fix line 418 in orders.py
- [ ] Test with: `test_vendor_token_rejected_with_403`
- [ ] Verify no other async issues

### Step 2: Fix Status Codes (1-2 hours)
- [ ] Research HTTPBearer configuration
- [ ] Update to return 401 instead of 403
- [ ] Test with: `test_no_token_returns_401`
- [ ] Verify all auth endpoints

### Step 3: Validate All Tests (30 min)
- [ ] Run full test suite
- [ ] Check coverage report
- [ ] Verify VENDOR validation works
- [ ] Confirm ownership checks

### Step 4: Document Results (1 hour)
- [ ] Create GREEN_PHASE_RESULTS.md
- [ ] Update coverage metrics
- [ ] Document any remaining issues
- [ ] Plan REFACTOR phase

---

## 💡 HELPFUL COMMANDS

### Quick Test Feedback
```bash
# Run tests and show only summary
python -m pytest tests/unit/orders/ --tb=no -q -m "tdd and red_test"
```

### Debug Specific Failure
```bash
# Show full traceback for debugging
python -m pytest tests/unit/orders/test_order_security_vendor_validation.py::test_vendor_token_rejected_with_403 -vv --tb=long
```

### Watch Mode (if pytest-watch installed)
```bash
ptw tests/unit/orders/ -- -v -m "tdd and red_test"
```

### Coverage HTML Report
```bash
python -m pytest tests/unit/orders/ --cov=app.api.v1.endpoints.orders --cov-report=html
# Open: htmlcov/index.html
```

---

## 📞 CONTACT INFO

**Agent Responsible**: tdd-specialist
**Department**: Methodologies and Quality
**Office**: `.workspace/departments/testing/tdd-specialist/`

**For Questions**:
- RED Phase details: `RED_PHASE_RESULTS.md`
- Executive summary: `EXECUTIVE_SUMMARY_RED_PHASE.md`
- Original discovery: `CHECKOUT_MAP.md`

---

## 🚦 STATUS INDICATORS

| Phase | Status | Progress |
|-------|--------|----------|
| Discovery | ✅ | 100% |
| RED | ✅ | 100% |
| GREEN | 🔄 | 0% ⬅️ NEXT |
| REFACTOR | ⏳ | 0% |
| DEPLOY | ⏳ | 0% |

---

**Last Updated**: 2025-10-09
**Git Commit**: 7ea9c2a9
**Branch**: main
**Ready For**: GREEN Phase Implementation
