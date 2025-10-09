# BACKEND CHECKOUT FLOW MAP - COMPLETE TDD COVERAGE

**Fecha**: 2025-10-09
**Misión**: FASE 1 Discovery - Mapeo completo del flujo de checkout backend
**Squad**: backend-framework-ai + database-architect-ai + api-architect

---

## 1. ENDPOINTS IDENTIFICADOS

### 1.1 Core Orders Endpoint
**Archivo**: `app/api/v1/endpoints/orders.py`

| Método | Ruta | Línea | Descripción | Status |
|--------|------|-------|-------------|--------|
| POST | `/api/v1/orders/` | 332 | Crear orden completa | ✅ Existe |
| GET | `/api/v1/orders/` | 165 | Listar órdenes del usuario | ✅ Existe |
| GET | `/api/v1/orders/{order_id}` | 246 | Detalle de orden específica | ✅ Existe |
| GET | `/api/v1/orders/health` | 228 | Health check del servicio | ✅ Existe |
| GET | `/api/v1/orders/{order_id}/tracking` | 622 | Tracking de envío | ✅ Existe |
| PATCH | `/api/v1/orders/{order_id}/cancel` | 759 | Cancelar orden | ✅ Existe |

### 1.2 Admin Orders Endpoints
**Archivo**: `app/api/v1/endpoints/admin_orders.py`

| Método | Ruta | Descripción | Status |
|--------|------|-------------|--------|
| GET | `/api/v1/admin/orders` | Admin: Lista todas las órdenes | ⚠️  Requiere verificación |
| PATCH | `/api/v1/admin/orders/{id}/status` | Admin: Cambiar status de orden | ⚠️  Requiere verificación |

### 1.3 Vendor Orders Endpoints
**Archivo**: `app/api/v1/endpoints/vendor_orders.py`

| Método | Ruta | Descripción | Status |
|--------|------|-------------|--------|
| GET | `/api/v1/vendor/orders` | Vendor: Sus órdenes recibidas | ⚠️  Requiere verificación |

---

## 2. MODELS & SCHEMAS

### 2.1 Database Models
**Archivo**: `app/models/order.py`

| Model | Tabla | Key Fields | Constraints |
|-------|-------|------------|-------------|
| `Order` | `orders` | id (UUID), order_number, buyer_id, total_amount, status | ✅ CHECK constraint en total_calculation |
| `OrderItem` | `order_items` | id (UUID), order_id, product_id, quantity, unit_price | ✅ ForeignKey a orders y products |
| `OrderTransaction` | `order_transactions` | id (UUID), order_id, amount, status, gateway | ✅ ForeignKey a orders |
| `PaymentMethod` | `payment_methods` | id (UUID), buyer_id, method_type | ✅ ForeignKey a users |

**Critical Model Fields:**
```python
# Order (líneas 31-98)
- subtotal: Numeric(10, 2)
- tax_amount: Numeric(10, 2)  # IVA 19%
- shipping_cost: Numeric(10, 2)
- discount_amount: Numeric(10, 2)
- total_amount: Numeric(10, 2)  # MUST match subtotal + tax + shipping - discount
- status: OrderStatus (PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED)

# Shipping fields (required)
- shipping_name, shipping_phone, shipping_address, shipping_city, shipping_state

# Timestamps
- created_at, confirmed_at, shipped_at, delivered_at, cancelled_at
```

### 2.2 Pydantic Schemas
**Archivo**: `app/schemas/order.py`

| Schema | Propósito | Líneas |
|--------|-----------|--------|
| `OrderStatus` | Enum de estados | 26-34 |
| `OrderItemBase` | Base para items | 45-63 |
| `OrderBase` | Base para orders | 87-128 |
| `OrderCreate` | Request de creación | 130-146 |
| `OrderSummary` | Response simplificado | 215-225 |
| `OrderTrackingResponse` | Tracking info | 251-262 |
| `OrderCancelRequest` | Request de cancelación | 265-269 |
| `OrderCancelResponse` | Response de cancelación | 272-279 |

---

## 3. BUSINESS LOGIC DETALLADA

### 3.1 Flujo de Creación de Orden (POST /orders/)
**Archivo**: `app/api/v1/endpoints/orders.py` líneas 332-615

#### STEP 1: Validación de Request (líneas 367-407)
```python
Required fields:
- items[]: Array con product_id + quantity
- shipping_name, shipping_phone, shipping_address, shipping_city, shipping_state

Validations:
✅ Cart no vacío (al menos 1 item)
✅ Cada item tiene product_id y quantity > 0
✅ Shipping info completa
```

#### STEP 2: Fetch Products (líneas 409-428)
```python
Query con eager loading:
- Product.ubicaciones_inventario (para stock)
- Verificar que todos los product_id existen
```

#### STEP 3: Stock Validation (líneas 430-462)
```python
CRITICAL HOTFIX (línea 439-451):
# Cálculo directo de stock para evitar async issues
stock_disponible = sum(
    ubicacion.cantidad - ubicacion.cantidad_reservada
    for ubicacion in product.ubicaciones_inventario
)

⚠️  ESTE ES EL FIX DEL 500 ERROR
- Bypass de product.get_stock_disponible() que falla en async
- Fallback a 999999 si no hay inventory loaded
```

#### STEP 4: Calculate Totals (líneas 464-489)
```python
Cálculos:
1. subtotal = sum(precio_venta * quantity)
2. tax_amount = calculate_tax(subtotal)  # 19% IVA
3. shipping_cost = calculate_shipping_cost(subtotal)  # Free si >= 200k
4. total_amount = subtotal + tax_amount + shipping_cost

CRITICAL: Usar Decimal types - NO float
Razón: CHECK constraint ck_order_total_calculation con tolerance 0.01
```

#### STEP 5: Database Transaction (líneas 492-559)
```python
async with db.begin():  # Atomic transaction
    1. Generar order_number: ORD-YYYYMMDD-XXXXXXXX
    2. Crear Order con DECIMAL types (NO float)
    3. db.flush() para obtener order.id
    4. Crear OrderItems con snapshot de producto
    5. db.commit()
    6. Refresh para obtener relationships
```

#### STEP 6: Format Response (líneas 561-605)
```python
Return:
{
    "success": true,
    "data": {
        "id", "order_number", "buyer_id", "status",
        "subtotal", "tax_amount", "shipping_cost", "total_amount",
        "shipping_info": {...},
        "items": [...]
    },
    "message": "Order {order_number} created successfully"
}
```

### 3.2 Autenticación y Autorización
**Archivo**: `app/api/v1/endpoints/orders.py` líneas 42-113

#### CRITICAL SECURITY FIX (líneas 89-102)
```python
# SECURITY FIX 2025-10-09
user_type = payload.get("user_type", "").upper()

if user_type == "VENDOR":
    raise HTTPException(
        status_code=403,
        detail="Vendors cannot create orders. Only customers can place orders."
    )

✅ ESTE FIX EVITA QUE VENDORS CREEN ÓRDENES
✅ Vendors son sellers, NO buyers
```

### 3.3 Utility Functions

#### `generate_order_number()` (línea 119)
```python
Format: ORD-YYYYMMDD-XXXXXXXX
Example: ORD-20251009-A1B2C3D4
```

#### `calculate_shipping_cost(subtotal)` (línea 126)
```python
Rules:
- subtotal >= 200,000 COP → Free (0.00)
- subtotal < 200,000 COP → 15,000 COP
```

#### `calculate_tax(subtotal)` (línea 142)
```python
IVA Rate: 19%
tax = subtotal * 0.19
```

---

## 4. DEPENDENCIES & INTEGRATIONS

### 4.1 Database Layer
- **PostgreSQL**: Tablas orders, order_items, order_transactions
- **AsyncSession**: SQLAlchemy async engine
- **Transactions**: `async with db.begin()` para atomicidad

### 4.2 Authentication
- **JWT Tokens**: decode_access_token from app.core.security
- **User Types**: VENDOR (rejected), CUSTOMER/BUYER/ADMIN/SUPERUSER (allowed)
- **Bypass en Testing**: PYTEST_CURRENT_TEST environment var

### 4.3 External Services (Potential)
- **Email**: Order confirmation (order_notification_service.py)
- **Webhooks**: Payment callbacks (webhooks.py)
- **Payments**: Wompi/PayU/Efecty integration

### 4.4 Other Services
**Archivo**: `app/services/`

| Service | Archivo | Propósito |
|---------|---------|-----------|
| `order_state_service.py` | - | State machine para transiciones de status |
| `order_tracking_service.py` | - | Tracking de courier y eventos |
| `order_notification_service.py` | - | Emails y notificaciones |
| `integrated_payment_service.py` | - | Integración con gateways |

---

## 5. EXISTING TEST COVERAGE

### 5.1 Test Files Found
```bash
tests/models/test_order.py
tests/services/test_order_state_service.py
tests/services/test_order_tracking_service.py
tests/services/test_notification_orders.py
tests/regression/test_orders_stock_fix.py
tests/api/test_orders_buyer.py
tests/test_admin_orders_endpoints.py
```

### 5.2 Coverage Analysis Needed
```bash
# TODO: Ejecutar para obtener baseline
python -m pytest tests/ -k "order" --cov=app.api.v1.endpoints.orders --cov-report=term
```

**Expected Gaps:**
- ❌ No tests para VENDOR validation (línea 96)
- ❌ No tests para stock calculation hotfix (línea 440)
- ❌ No tests para Decimal type constraints
- ❌ No tests para shipping cost calculation
- ❌ No tests para tax calculation (IVA 19%)
- ❌ No tests para order cancellation flow
- ❌ No tests para tracking endpoint

---

## 6. CRITICAL EDGE CASES IDENTIFIED

### 6.1 Security Vulnerabilities
| Caso | Archivo:Línea | Severidad | Status |
|------|---------------|-----------|--------|
| VENDOR creating orders | orders.py:96 | 🔴 CRITICAL | ✅ FIXED |
| Unauthorized order access | orders.py:662 | 🔴 CRITICAL | ✅ IMPLEMENTED |
| Missing JWT validation | orders.py:75 | 🔴 CRITICAL | ✅ IMPLEMENTED |

### 6.2 Data Integrity Issues
| Caso | Archivo:Línea | Severidad | Status |
|------|---------------|-----------|--------|
| Float precision in totals | orders.py:502 | 🔴 CRITICAL | ✅ FIXED (Decimal) |
| CHECK constraint violation | orders.py:499 | 🔴 CRITICAL | ✅ FIXED (Decimal) |
| Stock calculation async bug | orders.py:440 | 🔴 CRITICAL | ✅ FIXED (bypass) |

### 6.3 Business Logic Gaps
| Caso | Descripción | Severidad | Status |
|------|-------------|-----------|--------|
| Empty cart | Creating order with 0 items | 🟡 MEDIUM | ✅ Validated (línea 372) |
| Insufficient stock | Quantity > available | 🔴 CRITICAL | ✅ Validated (línea 453) |
| Non-existent product | Invalid product_id | 🔴 CRITICAL | ✅ Validated (línea 424) |
| Missing price | Product without precio_venta | 🔴 CRITICAL | ✅ Validated (línea 473) |
| Order cancellation after shipment | Cancel SHIPPED order | 🟡 MEDIUM | ✅ Blocked (línea 820) |

---

## 7. TEST SCENARIOS TO IMPLEMENT

### 7.1 Unit Tests (Aislados)

#### OrderModel Tests
- [ ] `test_order_creation_with_required_fields`
- [ ] `test_order_total_calculation_decimal_precision`
- [ ] `test_order_requires_shipping_info`
- [ ] `test_order_status_transitions`
- [ ] `test_order_item_total_calculation`

#### Validation Tests
- [ ] `test_vendor_cannot_create_order` (CRITICAL)
- [ ] `test_customer_can_create_order`
- [ ] `test_order_requires_valid_products`
- [ ] `test_order_checks_stock_availability`
- [ ] `test_empty_cart_rejected`
- [ ] `test_missing_shipping_info_rejected`

#### Stock Calculation Tests
- [ ] `test_stock_calculation_in_async_context` (CRITICAL)
- [ ] `test_product_with_no_locations_has_zero_stock`
- [ ] `test_stock_calculation_matches_direct_calculation`
- [ ] `test_insufficient_stock_error`

#### Utility Function Tests
- [ ] `test_generate_order_number_format`
- [ ] `test_calculate_shipping_cost_free_threshold`
- [ ] `test_calculate_shipping_cost_standard`
- [ ] `test_calculate_tax_iva_19_percent`

### 7.2 Integration Tests (API + DB)

#### Order Creation Flow
- [ ] `test_complete_order_flow_customer`
- [ ] `test_order_creation_vendor_rejected` (CRITICAL - 403 not 500)
- [ ] `test_order_creation_saves_to_database`
- [ ] `test_order_updates_inventory_stock`
- [ ] `test_order_creates_order_items_snapshot`
- [ ] `test_order_transaction_atomic_rollback`

#### Order Retrieval
- [ ] `test_get_user_orders_pagination`
- [ ] `test_get_order_details_with_items`
- [ ] `test_get_order_unauthorized_access` (CRITICAL - Security)

#### Order Tracking
- [ ] `test_get_order_tracking_with_history`
- [ ] `test_tracking_unauthorized_access`
- [ ] `test_tracking_for_shipped_order`

#### Order Cancellation
- [ ] `test_cancel_pending_order_success`
- [ ] `test_cancel_shipped_order_rejected`
- [ ] `test_cancel_with_refund_request`
- [ ] `test_cancel_unauthorized_access`

### 7.3 Security Tests

#### Authentication
- [ ] `test_orders_endpoint_requires_authentication`
- [ ] `test_invalid_jwt_token_rejected`
- [ ] `test_expired_jwt_token_rejected`

#### Authorization
- [ ] `test_vendor_blocked_from_creating_orders` (CRITICAL)
- [ ] `test_user_cannot_access_other_users_orders`
- [ ] `test_admin_can_access_all_orders`

#### Input Validation
- [ ] `test_sql_injection_prevention`
- [ ] `test_xss_prevention_in_notes`
- [ ] `test_invalid_uuid_format_rejected`

### 7.4 Edge Cases & Error Handling

#### Data Validation
- [ ] `test_negative_quantity_rejected`
- [ ] `test_zero_quantity_rejected`
- [ ] `test_invalid_product_id_format`
- [ ] `test_product_without_price_rejected`

#### Concurrent Operations
- [ ] `test_concurrent_stock_deduction`
- [ ] `test_race_condition_stock_availability`

#### Error Scenarios
- [ ] `test_database_connection_error_handling`
- [ ] `test_transaction_rollback_on_error`
- [ ] `test_invalid_decimal_precision_error`

---

## 8. RECOMMENDED TEST STRUCTURE

```
tests/
├── unit/
│   ├── models/
│   │   └── test_order_model_comprehensive.py
│   ├── schemas/
│   │   └── test_order_schemas_validation.py
│   ├── services/
│   │   ├── test_order_calculations.py
│   │   └── test_stock_validation_service.py
│   └── utils/
│       └── test_order_utils.py
├── integration/
│   ├── api/
│   │   ├── test_order_creation_flow.py
│   │   ├── test_order_retrieval_flow.py
│   │   ├── test_order_tracking_flow.py
│   │   └── test_order_cancellation_flow.py
│   ├── database/
│   │   ├── test_order_persistence.py
│   │   └── test_order_relationships.py
│   └── security/
│       ├── test_order_authentication.py
│       └── test_order_authorization.py
├── e2e/
│   └── test_complete_checkout_journey.py
└── fixtures/
    ├── order_fixtures.py
    ├── product_fixtures.py
    └── user_fixtures.py
```

---

## 9. PRIORITY TESTING ROADMAP

### 🔴 PRIORITY 1: CRITICAL SECURITY (Do First)
1. **VENDOR Validation**
   - `test_vendor_cannot_create_order` → MUST return 403, not 500
   - `test_customer_can_create_order` → Baseline happy path

2. **Authentication/Authorization**
   - `test_orders_require_valid_jwt`
   - `test_user_cannot_access_other_orders`

### 🟠 PRIORITY 2: CORE BUSINESS LOGIC
3. **Stock Validation**
   - `test_stock_calculation_async_context` → The 500 error root cause
   - `test_insufficient_stock_rejected`

4. **Order Creation Flow**
   - `test_complete_order_creation_integration`
   - `test_decimal_precision_no_constraint_violation`

### 🟡 PRIORITY 3: EDGE CASES & VALIDATION
5. **Input Validation**
   - `test_empty_cart_rejected`
   - `test_invalid_product_id`
   - `test_missing_shipping_info`

6. **Calculations**
   - `test_tax_calculation_19_percent`
   - `test_shipping_cost_calculation`

### 🟢 PRIORITY 4: ADDITIONAL FEATURES
7. **Tracking & Cancellation**
   - `test_order_tracking_flow`
   - `test_order_cancellation_with_refund`

8. **Admin Operations**
   - Admin order management tests
   - Vendor orders tests

---

## 10. SUCCESS CRITERIA

### Phase 1 (RED) - Test Suite Created
- ✅ All 40+ test scenarios written
- ✅ Tests FAIL (expected RED phase)
- ✅ Clear failure messages indicating what needs implementation

### Phase 2 (GREEN) - All Tests Pass
- ✅ VENDOR validation: 403 (not 500)
- ✅ Stock calculation: No async errors
- ✅ Decimal precision: No CHECK constraint violations
- ✅ All edge cases handled gracefully
- ✅ Coverage >= 80% on orders.py

### Phase 3 (REFACTOR) - Code Quality
- ✅ Tests still GREEN after refactoring
- ✅ Code organization improved
- ✅ Performance optimized
- ✅ Error messages clear and actionable

### Phase 4 (PRODUCTION) - Deployment Ready
- ✅ Security audit passed
- ✅ All tests GREEN in CI/CD
- ✅ No 500 errors in any scenario
- ✅ Documentation updated

---

## 11. KNOWN ISSUES & FIXES APPLIED

### Issue 1: VENDOR Can Create Orders (500 Error)
**File**: `orders.py:96`
**Status**: ✅ FIXED 2025-10-09
**Fix**: Added user_type validation, returns 403 for VENDOR
**Test Needed**: `test_vendor_cannot_create_order`

### Issue 2: Stock Calculation Fails in Async Context
**File**: `orders.py:440`
**Status**: ✅ FIXED (Hotfix)
**Fix**: Direct calculation bypassing async method
**Test Needed**: `test_stock_calculation_async_context`

### Issue 3: Decimal Precision Causes CHECK Constraint Violation
**File**: `orders.py:502`
**Status**: ✅ FIXED 2025-10-02
**Fix**: Keep Decimal types throughout, no float conversion
**Test Needed**: `test_decimal_precision_no_violation`

---

## 12. NEXT STEPS - FASE 2

1. **Create Test Structure**
   ```bash
   mkdir -p tests/unit/orders
   mkdir -p tests/integration/orders
   mkdir -p tests/fixtures/orders
   ```

2. **Setup conftest.py with Fixtures**
   - customer_user fixture
   - vendor_user fixture
   - product fixtures with stock
   - order_data fixtures

3. **Write RED Tests** (Comprehensive)
   - Start with Priority 1 (Security)
   - Then Priority 2 (Core Logic)
   - Document expected failures

4. **Run RED Phase**
   ```bash
   python -m pytest tests/unit/orders/ -v --tb=short
   # Expect: FAILURES (this is correct!)
   ```

5. **Move to GREEN Phase**
   - Fix issues one by one
   - Commit after each fix
   - Keep tests passing

---

**END OF DISCOVERY PHASE**

**Prepared by**: backend-framework-ai + database-architect-ai + api-architect
**Reviewed by**: Director CEO v5.0
**Status**: ✅ COMPLETE - Ready for FASE 2 (TDD RED Phase)
