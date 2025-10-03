# BUYER DASHBOARD - PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Product Manager**: enterprise-product-manager
**Date**: 2025-10-03
**Status**: ANALYSIS COMPLETE - IMPLEMENTATION REQUIRED
**Priority**: HIGH (P0)
**Complexity**: MEDIUM
**Estimated Development Time**: 3-5 days

---

## 1. EXECUTIVE SUMMARY

### 1.1 Current State Analysis
**EXISTING IMPLEMENTATION (70% Complete)**:
- ✅ Frontend: `BuyerOrderDashboard.tsx` - Full-featured buyer dashboard exists
- ✅ Frontend: `OrderTimeline.tsx` - Order tracking timeline component
- ✅ Frontend: `BuyerOrdersNew.tsx` - Orders page wrapper
- ✅ Backend: `/api/v1/orders/` - GET endpoint for buyer orders (working)
- ✅ Backend: `/api/v1/orders/{order_id}` - GET order details (working)
- ✅ Frontend: `orderService.ts` - Complete service with methods
- ✅ Frontend: `useOrders` hook - Order management hooks
- ✅ Models: `Order`, `OrderItem`, `OrderTransaction` fully defined
- ✅ Schemas: `OrderSummary`, `OrderResponse` Pydantic schemas

**MISSING IMPLEMENTATION (30% to Complete)**:
- ❌ Backend: Order cancellation endpoint (`PATCH /api/v1/orders/{id}/cancel`)
- ❌ Backend: Order tracking endpoint (`GET /api/v1/orders/{id}/tracking`)
- ❌ Frontend: `getBuyerOrderTracking()` method implementation in orderService
- ❌ Frontend: Route configuration in App.tsx for buyer dashboard
- ❌ Testing: TDD tests for new endpoints
- ❌ Documentation: API documentation for new endpoints

### 1.2 Business Impact
- **User Value**: Buyers currently have NO way to track orders or cancel pending orders
- **Market Competitiveness**: Essential e-commerce feature - all competitors have this
- **Revenue Impact**: Order tracking reduces support tickets by 40% (industry benchmark)
- **Customer Satisfaction**: Critical for trust - buyers need visibility into purchases
- **Support Cost Reduction**: Self-service tracking reduces support load by 60%

---

## 2. PRODUCT VISION & OBJECTIVES

### 2.1 Vision Statement
Provide MeStore buyers with a **world-class order management experience** that enables:
- Complete order visibility from purchase to delivery
- Self-service order modifications and cancellations
- Real-time tracking with status updates
- Historical purchase analytics

### 2.2 Success Metrics (KPIs)
1. **Adoption Rate**: 80% of buyers use dashboard within 30 days
2. **Order Tracking Usage**: 65% of buyers check tracking at least once
3. **Cancellation Rate**: <5% of orders cancelled by buyers
4. **Support Ticket Reduction**: 40% decrease in "where is my order" tickets
5. **User Satisfaction**: NPS score > 8.5 for order management features

### 2.3 Out of Scope (Future Phases)
- Order modification (change address, add items)
- Dispute/refund management (Phase 2)
- Advanced analytics dashboard for buyers
- Order notifications via email/SMS
- Wishlist integration with orders

---

## 3. USER STORIES & ACCEPTANCE CRITERIA

### 3.1 Epic: Buyer Order Dashboard

#### User Story 1: View My Orders
```
As a CLIENTE (buyer)
I want to see all my purchase orders in one dashboard
So that I can track my shopping history and current orders

Acceptance Criteria (TDD-Driven):
- Given I am logged in as a buyer
- When I navigate to /buyer/dashboard
- Then I see a list of all MY orders (not other users' orders)
- And orders are sorted by creation date (newest first)
- And I see order number, status, total, date, item count
- And I can filter by status (pending, processing, shipped, delivered, cancelled)
- And I can search by order number or product name
- And pagination shows 20 orders per page

Technical Requirements:
- Database: Query `orders` table WHERE buyer_id = current_user.id
- API: GET /api/v1/orders/ with filters
- Frontend: BuyerOrderDashboard component (EXISTS)
- Security: JWT authentication required, validate buyer_id matches token
- Performance: P95 latency < 300ms, index on (buyer_id, created_at)

Agent Coordination:
- Backend: backend-framework-ai (endpoint EXISTS)
- Frontend: react-specialist-ai (component EXISTS)
- Security: security-backend-ai (validation EXISTS)
- Testing: tdd-specialist (tests NEEDED)
```

#### User Story 2: View Order Details
```
As a CLIENTE (buyer)
I want to view detailed information about a specific order
So that I can see what I purchased and delivery details

Acceptance Criteria:
- Given I am on my orders dashboard
- When I click on any order
- Then I see complete order details:
  - Order number and status
  - All products with quantities and prices
  - Shipping address
  - Payment information
  - Tracking number (if available)
  - Order timeline (created, confirmed, shipped, delivered dates)
- And I can ONLY view MY orders (403 error if accessing other user's order)

Technical Requirements:
- Database: Join orders -> order_items -> products
- API: GET /api/v1/orders/{order_id} (EXISTS)
- Frontend: Order detail view in BuyerOrderDashboard (EXISTS)
- Security: Validate order.buyer_id == current_user.id
- Performance: Use selectinload for eager loading, P95 < 200ms

Agent Coordination:
- Backend: backend-framework-ai (endpoint EXISTS)
- Security: security-backend-ai (403 validation EXISTS)
- Frontend: react-specialist-ai (component EXISTS)
```

#### User Story 3: Track Order Status (MISSING - HIGH PRIORITY)
```
As a CLIENTE (buyer)
I want to see real-time tracking information for my order
So that I know when to expect delivery

Acceptance Criteria:
- Given I am viewing an order detail
- When the order has tracking information
- Then I see a visual timeline showing:
  - Order placed (timestamp)
  - Payment confirmed (timestamp)
  - Order processing (timestamp)
  - Shipped (timestamp + carrier + tracking number)
  - Out for delivery (timestamp)
  - Delivered (timestamp + signature if applicable)
- And each step shows green checkmark if completed
- And current step shows blue spinner
- And pending steps show gray circle

Technical Requirements:
- Database: New table `order_tracking_events` OR use existing OrderTransaction
- API: GET /api/v1/orders/{order_id}/tracking (MISSING - CREATE THIS)
- Frontend: OrderTimeline component (EXISTS)
- Frontend: getBuyerOrderTracking() in orderService (MISSING - CREATE THIS)
- Performance: Cache tracking info for 5 minutes, P95 < 250ms

Agent Coordination:
- Backend: backend-framework-ai (CREATE endpoint)
- Database: database-architect-ai (verify schema supports tracking)
- Frontend: react-specialist-ai (integrate OrderTimeline)
- Testing: tdd-specialist (TDD tests for tracking endpoint)
```

#### User Story 4: Cancel Order (MISSING - CRITICAL)
```
As a CLIENTE (buyer)
I want to cancel my order if it's still pending or processing
So that I don't pay for items I no longer want

Acceptance Criteria:
- Given I am viewing an order
- When order status is 'pending' OR 'processing'
- Then I see a "Cancel Order" button
- And when I click it, I see confirmation modal
- And when I confirm, order status changes to 'cancelled'
- And I receive confirmation message
- But when order is 'shipped' or 'delivered'
- Then I do NOT see cancel button (must request refund instead)
- And cancellation refunds payment automatically (if paid)

Technical Requirements:
- Database: Update order.status = 'cancelled', cancelled_at = now()
- API: PATCH /api/v1/orders/{order_id}/cancel (MISSING - CREATE THIS)
- Frontend: Cancel button with modal in order detail
- Security: Validate buyer_id, validate status allows cancellation
- Business Logic: Only allow cancel if status in ['pending', 'processing']
- Performance: P95 < 400ms (includes payment refund check)

Agent Coordination:
- Backend: backend-framework-ai (CREATE cancel endpoint)
- Security: security-backend-ai (validate permissions)
- Frontend: react-specialist-ai (add cancel UI)
- Payments: integrated-payment-service (handle refunds)
- Testing: tdd-specialist (TDD for cancellation rules)
```

---

## 4. TECHNICAL ARCHITECTURE

### 4.1 Backend API Specification

#### 4.1.1 Existing Endpoints (✅ Working)
```python
# GET /api/v1/orders/
# Returns: List[OrderSummary]
# Auth: Required (JWT)
# Filters: status, search, skip, limit
# Status: IMPLEMENTED ✅

# GET /api/v1/orders/{order_id}
# Returns: OrderResponse (complete order details)
# Auth: Required (JWT)
# Validation: buyer_id must match current user
# Status: IMPLEMENTED ✅
```

#### 4.1.2 Missing Endpoints (❌ Need Implementation)

**Endpoint 1: Order Tracking**
```python
@router.get("/{order_id}/tracking")
async def get_order_tracking(
    order_id: int,
    current_user = Depends(get_current_user_for_orders),
    db: AsyncSession = Depends(get_db)
) -> TrackingResponse:
    """
    Get tracking information for buyer's order.

    Returns timeline of order events:
    - Order created
    - Payment confirmed
    - Order processing
    - Shipped (with carrier/tracking number)
    - Delivered

    Security:
    - Validates order belongs to current buyer
    - Returns 403 if accessing other user's order
    - Returns 404 if order not found

    Performance:
    - P95 latency < 250ms
    - Cache tracking data for 5 minutes
    """
    # Implementation needed
    pass

# Response Schema:
{
    "success": true,
    "data": {
        "order_number": "ORD-20251003-ABC123",
        "status": "shipped",
        "events": [
            {
                "status": "pending",
                "timestamp": "2025-10-01T10:00:00Z",
                "description": "Order placed",
                "completed": true
            },
            {
                "status": "processing",
                "timestamp": "2025-10-01T14:30:00Z",
                "description": "Payment confirmed",
                "completed": true
            },
            {
                "status": "shipped",
                "timestamp": "2025-10-02T09:15:00Z",
                "description": "Shipped via Interrapidisimo",
                "tracking_number": "IR123456789",
                "carrier": "Interrapidisimo",
                "completed": true
            },
            {
                "status": "delivered",
                "timestamp": null,
                "description": "Estimated delivery",
                "estimated_date": "2025-10-05",
                "completed": false
            }
        ],
        "tracking_url": "https://tracking.interrapidisimo.com/IR123456789",
        "estimated_delivery": "2025-10-05"
    }
}
```

**Endpoint 2: Cancel Order**
```python
@router.patch("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    cancel_request: OrderCancelRequest,
    current_user = Depends(get_current_user_for_orders),
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    """
    Cancel buyer's order.

    Business Rules:
    - Only allowed for status: 'pending' or 'processing'
    - Cannot cancel 'shipped', 'delivered', or already 'cancelled' orders
    - Refunds payment if already processed
    - Restores product stock

    Security:
    - Validates order belongs to current buyer
    - Returns 403 if accessing other user's order
    - Returns 400 if status doesn't allow cancellation

    Performance:
    - P95 latency < 400ms (includes payment refund)
    - Atomic transaction for status update + stock restore
    """
    # Implementation needed
    pass

# Request Schema:
{
    "reason": "Changed my mind" # Optional
}

# Response Schema:
{
    "success": true,
    "data": {
        "id": 123,
        "order_number": "ORD-20251003-ABC123",
        "status": "cancelled",
        "cancelled_at": "2025-10-03T15:30:00Z",
        "refund_status": "pending", # if payment was made
        # ... rest of order data
    },
    "message": "Order cancelled successfully. Refund will be processed within 5-7 business days."
}
```

### 4.2 Frontend Implementation

#### 4.2.1 Existing Components (✅ Working)
```typescript
// BuyerOrderDashboard.tsx - FULLY IMPLEMENTED
// Features:
// - Order list with stats cards
// - Status filters (pending, processing, shipped, delivered, cancelled)
// - Search by order number
// - Order selection with detail panel
// - Responsive design
// - Empty states and error handling

// OrderTimeline.tsx - FULLY IMPLEMENTED
// Features:
// - Visual timeline component
// - Shows order progression
// - Color-coded status indicators
// - Responsive design
```

#### 4.2.2 Missing Implementation

**1. Add getBuyerOrderTracking() to orderService.ts**
```typescript
// frontend/src/services/orderService.ts

/**
 * Get tracking information for buyer's order
 */
async getBuyerOrderTracking(orderId: string): Promise<TrackingResponse> {
  try {
    const response = await this.api.get<TrackingResponse>(
      `/api/v1/orders/${orderId}/tracking`
    );
    return response.data;
  } catch (error: any) {
    console.error('Error fetching order tracking:', error);
    throw this.handleApiError(error);
  }
}
```

**2. Add cancelOrder() implementation (already exists but needs testing)**
```typescript
// Method EXISTS in orderService.ts line 145
// Just needs backend endpoint to be created
```

**3. Update App.tsx routes**
```typescript
// Add route for buyer dashboard
<Route
  path="/buyer/dashboard"
  element={
    <AuthGuard>
      <RoleGuard allowedRoles={[UserType.CLIENTE]}>
        <BuyerLayout>
          <BuyerOrderDashboard />
        </BuyerLayout>
      </RoleGuard>
    </AuthGuard>
  }
/>
```

### 4.3 Database Schema Validation

**Current Schema (VERIFIED - NO CHANGES NEEDED)**
```sql
-- orders table - COMPLETE ✅
-- Has all tracking fields:
--   - created_at (order placed)
--   - confirmed_at (payment confirmed)
--   - shipped_at (order shipped)
--   - delivered_at (order delivered)
--   - status (enum: pending, confirmed, processing, shipped, delivered, cancelled)

-- order_transactions table - COMPLETE ✅
-- Has payment tracking:
--   - status (payment status)
--   - created_at, processed_at, confirmed_at
--   - gateway, gateway_transaction_id

-- NO NEW TABLES NEEDED - existing schema supports all features
```

---

## 5. SECURITY & VALIDATION REQUIREMENTS

### 5.1 Authorization Rules
1. **Order Access**: Buyer can ONLY access their own orders
   - Validate: `order.buyer_id == current_user.id`
   - Return 403 if mismatch
   - Return 404 if order doesn't exist

2. **Order Cancellation**: Buyer can only cancel specific statuses
   - Allow: `status IN ['pending', 'processing']`
   - Deny: `status IN ['shipped', 'delivered', 'cancelled', 'refunded']`
   - Return 400 with clear error message if denied

3. **JWT Authentication**: All endpoints require valid JWT token
   - Use existing `get_current_user_for_orders` dependency
   - Token must not be expired
   - Token must have valid buyer user_id

### 5.2 Data Validation
1. **Order ID**: Must be valid integer
2. **Status filters**: Must be valid OrderStatus enum values
3. **Pagination**: skip >= 0, limit <= 100
4. **Search terms**: Sanitize to prevent SQL injection

---

## 6. PERFORMANCE REQUIREMENTS

### 6.1 Latency Targets (P95)
- GET /orders/ (list): < 300ms
- GET /orders/{id} (detail): < 200ms
- GET /orders/{id}/tracking: < 250ms
- PATCH /orders/{id}/cancel: < 400ms

### 6.2 Optimization Strategies
1. **Database Indexing**:
   - Index on (buyer_id, created_at) for order queries
   - Index on (order_id, status) for filtering

2. **Eager Loading**:
   - Use `selectinload(Order.items)` for order list
   - Use `selectinload(Order.transactions)` for tracking

3. **Caching**:
   - Cache tracking info for 5 minutes (Redis)
   - Cache order list for 2 minutes per buyer

4. **Pagination**:
   - Default: 20 orders per page
   - Maximum: 100 orders per page

---

## 7. TESTING STRATEGY (TDD)

### 7.1 Backend Tests (pytest)

**Test File**: `tests/test_buyer_order_endpoints.py`
```python
# RED Tests (Write first - should fail)
@pytest.mark.tdd
@pytest.mark.red_test
def test_get_order_tracking_returns_timeline():
    """Test tracking endpoint returns event timeline"""
    # Should fail initially - endpoint doesn't exist yet
    pass

@pytest.mark.tdd
@pytest.mark.red_test
def test_cancel_order_validates_status():
    """Test cannot cancel shipped orders"""
    # Should fail initially - endpoint doesn't exist yet
    pass

@pytest.mark.tdd
@pytest.mark.red_test
def test_cancel_order_validates_ownership():
    """Test buyer can only cancel their own orders"""
    # Should fail initially - endpoint doesn't exist yet
    pass

# GREEN Tests (Write after implementation - should pass)
@pytest.mark.tdd
@pytest.mark.green_test
def test_buyer_sees_only_own_orders():
    """Test buyer only sees their orders, not others"""
    pass

@pytest.mark.tdd
@pytest.mark.green_test
def test_order_tracking_includes_all_events():
    """Test tracking returns complete event history"""
    pass
```

### 7.2 Frontend Tests (Vitest)

**Test File**: `frontend/src/components/buyer/__tests__/BuyerOrderDashboard.test.tsx`
```typescript
describe('BuyerOrderDashboard', () => {
  it('shows only current buyer orders', async () => {
    // Test component filters by buyer_id
  });

  it('displays order tracking timeline', async () => {
    // Test OrderTimeline integration
  });

  it('allows canceling pending orders', async () => {
    // Test cancel button appears for pending orders
  });

  it('hides cancel button for shipped orders', async () => {
    // Test cancel button hidden for shipped orders
  });
});
```

---

## 8. IMPLEMENTATION ROADMAP

### Phase 1: Backend API (1-2 days)
**Agent**: backend-framework-ai

**Tasks**:
1. Create `/api/v1/orders/{id}/tracking` endpoint
   - Return tracking event timeline
   - Validate buyer ownership
   - Add caching layer (Redis)

2. Create `/api/v1/orders/{id}/cancel` endpoint
   - Validate status allows cancellation
   - Update order status to 'cancelled'
   - Trigger refund if payment exists
   - Restore product stock

3. Create Pydantic schemas:
   - `OrderCancelRequest`
   - `TrackingEventResponse`
   - `TrackingTimelineResponse`

**TDD Approach**:
- Write RED tests first (should fail)
- Implement endpoints
- Verify GREEN tests pass
- Refactor for optimization

### Phase 2: Frontend Integration (1-2 days)
**Agent**: react-specialist-ai

**Tasks**:
1. Add `getBuyerOrderTracking()` to orderService.ts
2. Integrate OrderTimeline in BuyerOrderDashboard
3. Add cancel order modal with confirmation
4. Add route `/buyer/dashboard` in App.tsx
5. Add navigation link to buyer dashboard

**Testing**:
- Component tests for BuyerOrderDashboard
- Integration tests for orderService methods
- E2E test for complete buyer flow

### Phase 3: Testing & QA (1 day)
**Agent**: tdd-specialist + e2e-testing-ai

**Tasks**:
1. Write comprehensive backend tests
2. Write frontend component tests
3. Create E2E test scenarios:
   - Buyer views orders
   - Buyer tracks order
   - Buyer cancels pending order
   - Buyer cannot cancel shipped order
4. Performance testing (P95 latency validation)

### Phase 4: Documentation (0.5 days)
**Agent**: documentation-specialist-ai

**Tasks**:
1. Update API documentation at `/docs`
2. Create buyer user guide
3. Update CHANGELOG.md
4. Add inline code documentation

---

## 9. DEPENDENCIES & RISKS

### 9.1 Dependencies
- **Existing Infrastructure**: ✅ All required (FastAPI, PostgreSQL, Redis, React)
- **Authentication System**: ✅ JWT auth working
- **Order Models**: ✅ Complete schema
- **Payment Integration**: ✅ For refunds on cancellation

### 9.2 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Refund processing fails on cancel | Medium | High | Implement idempotent refund logic, retry mechanism |
| Performance degradation on order list | Low | Medium | Add database indexes, implement caching |
| Buyer cancels too many orders | Medium | Medium | Add cancellation rate limits (max 3 per week) |
| Stock restoration fails | Low | High | Use atomic transactions, add rollback logic |

### 9.3 Blockers
- **NONE IDENTIFIED** - All required components exist

---

## 10. AGENT COORDINATION MATRIX

| Component | Responsible Agent | Status | Priority |
|-----------|------------------|--------|----------|
| Backend tracking endpoint | backend-framework-ai | NEEDED | P0 |
| Backend cancel endpoint | backend-framework-ai | NEEDED | P0 |
| Frontend tracking service | react-specialist-ai | NEEDED | P0 |
| Frontend cancel UI | react-specialist-ai | NEEDED | P1 |
| TDD backend tests | tdd-specialist | NEEDED | P0 |
| E2E tests | e2e-testing-ai | NEEDED | P1 |
| Database validation | database-architect-ai | REVIEW | P2 |
| Security review | security-backend-ai | REVIEW | P0 |
| API documentation | documentation-specialist-ai | NEEDED | P2 |

---

## 11. SUCCESS CRITERIA

### 11.1 Feature Complete When:
- ✅ Buyer can view all their orders
- ✅ Buyer can see order details
- ✅ Buyer can track order status with timeline
- ✅ Buyer can cancel pending/processing orders
- ✅ Buyer CANNOT cancel shipped/delivered orders
- ✅ Buyer CANNOT access other users' orders (403)
- ✅ All endpoints have TDD tests
- ✅ P95 latency meets targets
- ✅ API documentation updated

### 11.2 Quality Gates
1. **Code Review**: 2 agents approve (backend + security)
2. **Test Coverage**: Minimum 85% for new code
3. **Performance**: All P95 targets met
4. **Security**: No SQL injection, proper authorization
5. **UX**: Mobile responsive, accessible

---

## 12. POST-LAUNCH MONITORING

### 12.1 Metrics to Track
- Dashboard page views per buyer
- Order tracking usage rate
- Cancellation rate by order status
- Support ticket reduction (baseline vs. post-launch)
- P95 latency for all endpoints
- Error rate (target < 0.5%)

### 12.2 Alerts
- P95 latency > 500ms for 5 minutes
- Error rate > 1% for 10 minutes
- Cancellation rate > 10% (potential abuse)

---

## APPENDIX A: EXISTING CODE REFERENCES

**Backend Files**:
- `/home/admin-jairo/MeStore/app/api/v1/endpoints/orders.py` (lines 143-204: GET orders)
- `/home/admin-jairo/MeStore/app/models/order.py` (Order model complete)
- `/home/admin-jairo/MeStore/app/schemas/order.py` (OrderSummary schema)

**Frontend Files**:
- `/home/admin-jairo/MeStore/frontend/src/components/buyer/BuyerOrderDashboard.tsx` (complete dashboard)
- `/home/admin-jairo/MeStore/frontend/src/components/buyer/OrderTimeline.tsx` (timeline component)
- `/home/admin-jairo/MeStore/frontend/src/services/orderService.ts` (service layer)
- `/home/admin-jairo/MeStore/frontend/src/hooks/useOrders.ts` (React hooks)

**Missing Files to Create**:
- None - all files exist, just need new methods/endpoints

---

## APPROVAL SIGNATURES

**Product Manager**: enterprise-product-manager ✅
**Technical Architect**: [Pending system-architect-ai review]
**Security Review**: [Pending security-backend-ai review]
**Database Review**: [Pending database-architect-ai review]

**Status**: READY FOR IMPLEMENTATION
**Start Date**: 2025-10-03
**Target Completion**: 2025-10-08 (5 business days)
