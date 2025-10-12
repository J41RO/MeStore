# Vendor Order Management - Implementation Checklist

**Project**: Vendor Order Management System
**Date**: 2025-10-03
**Status**: Ready for Execution
**Estimated Duration**: 4 weeks

---

## Pre-Implementation Checklist

### Workspace Protocol Compliance

- [x] Read `/home/admin-jairo/MeStore/CLAUDE.md`
- [x] Read `.workspace/SYSTEM_RULES.md`
- [x] Read `.workspace/PROTECTED_FILES.md`
- [x] Read `.workspace/AGENT_PROTOCOL.md`
- [x] Read `.workspace/RESPONSIBLE_AGENTS.md`
- [x] Identify protected files that will be modified
- [x] Plan agent coordination strategy

### Protected Files to Modify

**Critical - Requires Approval:**
- [ ] `app/models/order.py` - Add PreparationStatus enum and OrderItem fields
  - **Responsible Agent**: database-architect-ai
  - **Action**: Contact for approval before modification

**High Risk - Consultation Required:**
- [ ] `app/database.py` - No changes planned ✓
- [ ] `tests/conftest.py` - Add fixtures for vendor order tests
  - **Responsible Agent**: tdd-specialist
  - **Action**: Coordinate fixture creation

**Standard - Follow TDD:**
- [ ] New files (no approval needed, follow TDD)

---

## Week 1: Database & Backend Foundation

### Phase 1.1: Database Migration (database-architect-ai)

**Priority**: Critical
**Duration**: 2 days
**Dependencies**: None

#### Tasks

- [ ] **Contact database-architect-ai for approval**
  ```bash
  python .workspace/scripts/contact_responsible_agent.py database-architect-ai app/models/order.py "Add PreparationStatus enum and new fields to OrderItem for vendor order tracking"
  ```

- [ ] **Create migration script**
  - File: `alembic/versions/YYYY_MM_DD_HHMM_add_order_item_preparation_status.py`
  - Create PreparationStatus ENUM type
  - Add `preparation_status` column to `order_items`
  - Add `preparation_started_at` timestamp
  - Add `ready_at` timestamp
  - Add `shipped_at` timestamp
  - Create index on `preparation_status`

- [ ] **Update OrderItem model**
  - File: `app/models/order.py`
  - Add PreparationStatus enum class
  - Add new columns to OrderItem class
  - Add helper methods: `can_transition_to()`, `get_preparation_timeline()`

- [ ] **Test migration locally**
  ```bash
  # Run migration
  alembic upgrade head

  # Verify schema
  psql -d mestore_dev -c "\d order_items"

  # Test rollback
  alembic downgrade -1
  alembic upgrade head
  ```

- [ ] **Run migration on staging**
  ```bash
  # Backup staging database
  pg_dump mestore_staging > backup_staging_$(date +%Y%m%d).sql

  # Run migration
  alembic upgrade head
  ```

- [ ] **Commit with workspace protocol**
  ```
  feat(database): Add preparation status tracking to order items

  Workspace-Check: ✅ Consultado
  File: app/models/order.py, alembic/versions/...
  Agent: database-architect-ai
  Protocol: APPROVAL_OBTAINED
  Tests: PASSED
  Code-Standard: ✅ ENGLISH_CODE
  Responsible: database-architect-ai

  - Add PreparationStatus enum (pending, preparing, ready_to_ship, shipped)
  - Add preparation_status column to order_items
  - Add timestamp fields for tracking status changes
  - Create index for vendor order queries
  ```

#### Acceptance Criteria

- [x] Migration runs successfully without errors
- [x] All timestamps default to NULL
- [x] preparation_status defaults to 'pending'
- [x] Index created on preparation_status
- [x] Rollback script tested and working
- [x] No data loss in existing order_items

---

### Phase 1.2: Backend Schemas (backend-framework-ai)

**Priority**: High
**Duration**: 1 day
**Dependencies**: Phase 1.1 complete

#### Tasks

- [ ] **Create Pydantic schemas**
  - File: `app/schemas/vendor_order.py`

  **Schemas to Create:**
  ```python
  # Request Schemas
  - UpdateItemStatusRequest
  - VendorOrderFilters

  # Response Schemas
  - VendorOrderListResponse
  - VendorOrderSummary
  - VendorOrderItemSummary
  - VendorOrderDetailResponse
  - VendorOrderItemDetail
  - UpdateItemStatusResponse
  - VendorOrderStatsResponse
  - TopProductStat
  - DailySalesStat
  - PreparationTimelineEvent
  ```

- [ ] **Add validation rules**
  - status transitions validation
  - date range validation
  - pagination limits (max 100)

- [ ] **Create enum exports**
  - File: `app/schemas/__init__.py`
  - Export all vendor order schemas

#### Acceptance Criteria

- [x] All schemas have proper type hints
- [x] Validation rules implemented
- [x] Example values in docstrings
- [x] Schemas follow existing naming conventions
- [x] No circular import issues

---

### Phase 1.3: Vendor Order Service (backend-framework-ai)

**Priority**: High
**Duration**: 3 days
**Dependencies**: Phase 1.1, 1.2 complete

#### Tasks

- [ ] **Create VendorOrderService class**
  - File: `app/services/vendor_order_service.py`

  **Methods to Implement:**
  ```python
  - get_vendor_orders()          # List with filters
  - get_vendor_order_detail()    # Single order detail
  - update_item_status()         # Update preparation status
  - get_vendor_stats()           # Sales analytics
  - get_top_products()           # Best sellers
  - validate_vendor_access()     # Security check
  - validate_status_transition() # Business rules
  ```

- [ ] **Implement business logic**
  - Vendor can only see orders with their products
  - Filter multi-vendor orders to show only vendor's items
  - Validate status transitions
  - Calculate vendor-specific totals
  - Aggregate statistics

- [ ] **Add security validations**
  - Verify vendor owns product before allowing updates
  - Return 403 for unauthorized access
  - Log all status changes for audit trail

- [ ] **Optimize database queries**
  - Use eager loading (selectinload)
  - Add proper indexes
  - Implement pagination
  - Use async queries

#### Acceptance Criteria

- [x] All methods have docstrings
- [x] Type hints for all parameters
- [x] Proper error handling with HTTPException
- [x] Async/await used throughout
- [x] No N+1 query problems
- [x] Security checks on all operations

---

### Phase 1.4: API Endpoints (backend-framework-ai)

**Priority**: High
**Duration**: 2 days
**Dependencies**: Phase 1.3 complete

#### Tasks

- [ ] **Create vendor orders router**
  - File: `app/api/v1/endpoints/vendor_orders.py`

  **Endpoints to Create:**
  ```python
  GET    /api/v1/vendor/orders
  GET    /api/v1/vendor/orders/{order_id}
  PATCH  /api/v1/vendor/orders/{order_id}/items/{item_id}/status
  GET    /api/v1/vendor/orders/stats
  GET    /api/v1/vendor/orders/stats/products
  ```

- [ ] **Implement authentication dependency**
  - Create `get_current_vendor` dependency
  - Validate user has VENDOR role
  - Extract vendor_id from JWT token

- [ ] **Add endpoint documentation**
  - OpenAPI descriptions
  - Request/response examples
  - Error response documentation

- [ ] **Register router in main app**
  - File: `app/main.py`
  - Add router with prefix `/api/v1/vendor`
  - Add to API tags

#### Acceptance Criteria

- [x] All endpoints return correct status codes
- [x] Proper error messages for all cases
- [x] OpenAPI docs auto-generated
- [x] Rate limiting configured
- [x] CORS headers correct
- [x] Authentication required on all endpoints

---

## Week 2: Testing & Frontend Setup

### Phase 2.1: TDD Test Suite (tdd-specialist)

**Priority**: Critical
**Duration**: 3 days
**Dependencies**: Phase 1.4 complete

#### Tasks

- [ ] **Contact tdd-specialist for fixtures**
  ```bash
  python .workspace/scripts/contact_responsible_agent.py tdd-specialist tests/conftest.py "Add vendor order test fixtures"
  ```

- [ ] **Create test fixtures**
  - File: `tests/conftest.py`

  **Fixtures to Add:**
  ```python
  @pytest.fixture
  async def vendor_user(db)

  @pytest.fixture
  async def vendor_product(db, vendor_user)

  @pytest.fixture
  async def test_order_with_vendor_items(db, buyer_user, vendor_product)

  @pytest.fixture
  async def multi_vendor_order(db)

  @pytest.fixture
  async def order_item_pending(db)

  @pytest.fixture
  async def order_item_preparing(db)

  @pytest.fixture
  async def order_item_ready(db)
  ```

- [ ] **Create TDD test file**
  - File: `tests/test_vendor_order_endpoints.py`

  **Test Categories:**
  ```python
  class TestVendorOrderList:
      - test_get_vendor_orders_success
      - test_vendor_orders_filtered_by_status
      - test_vendor_orders_pagination
      - test_vendor_cannot_see_other_vendor_orders
      - test_vendor_orders_with_date_range

  class TestVendorOrderDetail:
      - test_get_order_detail_success
      - test_order_detail_shows_only_vendor_items
      - test_order_detail_forbidden_for_other_vendor
      - test_order_detail_not_found

  class TestItemStatusUpdate:
      - test_update_status_pending_to_preparing
      - test_update_status_preparing_to_ready
      - test_update_status_invalid_transition
      - test_update_other_vendor_item_forbidden
      - test_update_timestamps_correctly_set

  class TestVendorStats:
      - test_get_vendor_stats_success
      - test_vendor_stats_date_filtering
      - test_top_products_calculation
      - test_stats_exclude_other_vendors
  ```

- [ ] **Run TDD test suite**
  ```bash
  # Run only TDD tests
  python -m pytest tests/test_vendor_order_endpoints.py -m "tdd" -v

  # Run with coverage
  python -m pytest tests/test_vendor_order_endpoints.py --cov=app.services.vendor_order_service --cov=app.api.v1.endpoints.vendor_orders --cov-report=term-missing
  ```

- [ ] **Achieve 80%+ coverage**
  - Service layer: 85%+ coverage
  - Endpoints: 80%+ coverage
  - Edge cases tested

#### Acceptance Criteria

- [x] All tests pass (100% pass rate)
- [x] Coverage > 80% for new code
- [x] All edge cases covered
- [x] No flaky tests
- [x] Tests run in < 30 seconds
- [x] Fixtures follow existing patterns

---

### Phase 2.2: Frontend Type Definitions (react-specialist-ai)

**Priority**: Medium
**Duration**: 1 day
**Dependencies**: Phase 1.4 complete

#### Tasks

- [ ] **Create TypeScript interfaces**
  - File: `frontend/src/types/vendorOrder.ts`

  **Interfaces to Create:**
  ```typescript
  export interface VendorOrderSummary {
    order_id: number;
    order_number: string;
    buyer_name: string;
    buyer_email: string;
    order_status: OrderStatus;
    order_created_at: string;
    vendor_items_count: number;
    vendor_items_total: number;
    pending_items: number;
    ready_items: number;
    items: VendorOrderItemSummary[];
  }

  export interface VendorOrderItemSummary {
    item_id: number;
    product_id: number;
    product_name: string;
    product_sku: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    preparation_status: PreparationStatus;
    can_update_status: boolean;
  }

  export interface VendorOrderDetailResponse {
    // ... (see implementation plan)
  }

  export interface VendorOrderStatsResponse {
    // ... (see implementation plan)
  }

  export enum PreparationStatus {
    PENDING = 'pending',
    PREPARING = 'preparing',
    READY_TO_SHIP = 'ready_to_ship',
    SHIPPED = 'shipped'
  }

  export interface OrderFilters {
    status?: string;
    preparation_status?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
  }

  export interface PaginationState {
    skip: number;
    limit: number;
    total: number;
  }
  ```

- [ ] **Export types**
  - File: `frontend/src/types/index.ts`
  - Add vendor order types to exports

#### Acceptance Criteria

- [x] All interfaces match backend schemas
- [x] Proper TypeScript types (no `any`)
- [x] Enums match backend enums
- [x] JSDoc comments for all interfaces
- [x] No compilation errors

---

### Phase 2.3: Frontend Service Layer (react-specialist-ai)

**Priority**: Medium
**Duration**: 2 days
**Dependencies**: Phase 2.2 complete

#### Tasks

- [ ] **Create vendor order service**
  - File: `frontend/src/services/vendorOrderService.ts`

  **Methods to Implement:**
  ```typescript
  export const vendorOrderService = {
    getOrders: async (
      filters: OrderFilters,
      pagination: PaginationState
    ): Promise<VendorOrderListResponse>

    getOrderDetail: async (
      orderId: number
    ): Promise<VendorOrderDetailResponse>

    updateItemStatus: async (
      orderId: number,
      itemId: number,
      newStatus: PreparationStatus,
      notes?: string
    ): Promise<UpdateItemStatusResponse>

    getStats: async (
      period: string
    ): Promise<VendorOrderStatsResponse>

    getTopProducts: async (
      limit: number
    ): Promise<TopProductStat[]>
  };
  ```

- [ ] **Implement API client**
  - Use existing axios instance
  - Add JWT token to headers
  - Implement error handling
  - Add request/response interceptors

- [ ] **Add error handling**
  - Network errors
  - Authentication errors (401)
  - Authorization errors (403)
  - Validation errors (400)
  - Server errors (500)

#### Acceptance Criteria

- [x] All API calls use async/await
- [x] Proper TypeScript types on all methods
- [x] Error handling for all cases
- [x] Loading states supported
- [x] JWT token automatically included
- [x] Response data properly typed

---

## Week 3: Frontend Components & Pages

### Phase 3.1: Shared Components (react-specialist-ai)

**Priority**: High
**Duration**: 2 days
**Dependencies**: Phase 2.3 complete

#### Tasks

- [ ] **Create OrderCard component**
  - File: `frontend/src/components/vendor/orders/OrderCard.tsx`
  - Props: order, onStatusUpdate, onViewDetails
  - Display order summary with items
  - Quick action buttons

- [ ] **Create OrderItemCard component**
  - File: `frontend/src/components/vendor/orders/OrderItemCard.tsx`
  - Props: item, onStatusUpdate
  - Display item details
  - Status badge
  - Update button

- [ ] **Create StatusUpdateButton component**
  - File: `frontend/src/components/vendor/orders/StatusUpdateButton.tsx`
  - Props: item, onUpdate
  - Conditional rendering based on status
  - Loading state
  - Disabled states

- [ ] **Create PreparationTimeline component**
  - File: `frontend/src/components/vendor/orders/PreparationTimeline.tsx`
  - Props: items
  - Visual timeline
  - Status indicators
  - Timestamps

- [ ] **Create OrderFilters component**
  - File: `frontend/src/components/vendor/orders/OrderFilters.tsx`
  - Props: filters, onFilterChange
  - Filter controls
  - Search input
  - Clear filters button

- [ ] **Create StatsWidget component**
  - File: `frontend/src/components/vendor/orders/StatsWidget.tsx`
  - Props: title, value, change, icon
  - Metric card
  - Trend indicator
  - Icon support

#### Acceptance Criteria

- [x] All components are TypeScript
- [x] PropTypes or TypeScript interfaces defined
- [x] Accessible (ARIA labels, keyboard nav)
- [x] Mobile responsive
- [x] Loading and error states
- [x] Vitest tests for each component

---

### Phase 3.2: VendorOrderManagement Page (react-specialist-ai)

**Priority**: High
**Duration**: 3 days
**Dependencies**: Phase 3.1 complete

#### Tasks

- [ ] **Create main page component**
  - File: `frontend/src/pages/vendor/VendorOrderManagement.tsx`

- [ ] **Implement state management**
  - useState for orders, filters, pagination
  - useEffect for data fetching
  - Loading/error states

- [ ] **Implement filter functionality**
  - Status filter
  - Preparation status filter
  - Search by order number
  - Date range filter
  - Clear filters

- [ ] **Implement pagination**
  - Previous/Next buttons
  - Page number display
  - Items per page selector
  - Total count display

- [ ] **Implement status updates**
  - Quick update from card
  - Optimistic UI updates
  - Error rollback
  - Success toast

- [ ] **Add responsive grid**
  - Mobile: 1 column
  - Tablet: 2 columns
  - Desktop: 3 columns
  - Large: 4 columns

- [ ] **Add pull-to-refresh (mobile)**
  - Detect pull gesture
  - Show refresh indicator
  - Trigger data reload

#### Acceptance Criteria

- [x] Page loads orders on mount
- [x] Filters work correctly
- [x] Pagination works
- [x] Status updates work
- [x] Mobile responsive
- [x] Loading states shown
- [x] Error states handled
- [x] Empty state shown when no orders

---

### Phase 3.3: VendorOrderDetail Page (react-specialist-ai)

**Priority**: High
**Duration**: 2 days
**Dependencies**: Phase 3.1 complete

#### Tasks

- [ ] **Create detail page component**
  - File: `frontend/src/pages/vendor/VendorOrderDetail.tsx`

- [ ] **Implement data fetching**
  - Fetch on mount using orderId from URL params
  - Loading state while fetching
  - Error state if not found or forbidden

- [ ] **Display order information**
  - Order header with number and status
  - Customer information card
  - Shipping address card
  - Order timeline

- [ ] **Display vendor's items**
  - List of vendor's items only
  - Item details with images
  - Preparation status for each
  - Update buttons

- [ ] **Implement status updates**
  - Update individual items
  - Refresh page after update
  - Show success/error messages

- [ ] **Add back navigation**
  - Back button to order list
  - Browser back button support

#### Acceptance Criteria

- [x] Page loads order details
- [x] Shows only vendor's items
- [x] Status updates work
- [x] Navigation works
- [x] Mobile responsive
- [x] 404 for invalid order_id
- [x] 403 for unauthorized access

---

### Phase 3.4: VendorOrderStats Page (react-specialist-ai)

**Priority**: Medium
**Duration**: 2 days
**Dependencies**: Phase 3.1 complete

#### Tasks

- [ ] **Create stats page component**
  - File: `frontend/src/pages/vendor/VendorOrderStats.tsx`

- [ ] **Implement metrics cards**
  - Total sales
  - Total orders
  - Pending orders
  - Items sold
  - Ready items
  - Average order value

- [ ] **Add period selector**
  - Today, Week, Month, Year
  - Custom date range
  - Update stats on period change

- [ ] **Display top products**
  - Product list with sales data
  - Bar chart visualization
  - Percentage breakdown

- [ ] **Add export functionality**
  - Export to PDF
  - Export to CSV
  - Include selected period

#### Acceptance Criteria

- [x] Stats load correctly
- [x] Period selector works
- [x] Top products display
- [x] Charts render properly
- [x] Export functions work
- [x] Mobile responsive
- [x] Loading states shown

---

## Week 4: Integration, Testing & Deployment

### Phase 4.1: Routing Configuration (react-specialist-ai)

**Priority**: High
**Duration**: 1 day
**Dependencies**: Phase 3.2, 3.3, 3.4 complete

#### Tasks

- [ ] **Add routes to router config**
  - File: `frontend/src/App.tsx` or router config

  **Routes to Add:**
  ```typescript
  {
    path: '/vendor/orders',
    element: <VendorOrderManagement />,
    meta: { requiresAuth: true, roles: ['VENDOR'] }
  },
  {
    path: '/vendor/orders/:orderId',
    element: <VendorOrderDetail />,
    meta: { requiresAuth: true, roles: ['VENDOR'] }
  },
  {
    path: '/vendor/orders/stats',
    element: <VendorOrderStats />,
    meta: { requiresAuth: true, roles: ['VENDOR'] }
  }
  ```

- [ ] **Update VendorDashboard navigation**
  - File: `frontend/src/components/dashboard/VendorDashboard.tsx`
  - Add "Ver Órdenes" link
  - Update quick actions

- [ ] **Add to sidebar/menu (if exists)**
  - Add "Órdenes" menu item
  - Add "Estadísticas" menu item

#### Acceptance Criteria

- [x] Routes registered correctly
- [x] Authentication guard works
- [x] Role-based access works
- [x] Navigation links work
- [x] Browser back/forward works

---

### Phase 4.2: Frontend Testing (react-specialist-ai + tdd-specialist)

**Priority**: High
**Duration**: 2 days
**Dependencies**: Phase 4.1 complete

#### Tasks

- [ ] **Create component tests**
  - File: `frontend/src/components/vendor/orders/__tests__/`

  **Tests for Each Component:**
  - OrderCard.test.tsx
  - OrderItemCard.test.tsx
  - StatusUpdateButton.test.tsx
  - PreparationTimeline.test.tsx
  - OrderFilters.test.tsx
  - StatsWidget.test.tsx

- [ ] **Create page tests**
  - VendorOrderManagement.test.tsx
  - VendorOrderDetail.test.tsx
  - VendorOrderStats.test.tsx

- [ ] **Run test suite**
  ```bash
  cd frontend
  npm run test
  npm run test:coverage
  ```

- [ ] **Achieve coverage targets**
  - Components: 80%+ coverage
  - Pages: 75%+ coverage
  - Services: 90%+ coverage

#### Acceptance Criteria

- [x] All tests pass
- [x] Coverage meets targets
- [x] No console errors in tests
- [x] Tests run in < 60 seconds
- [x] Mock API calls properly

---

### Phase 4.3: Integration Testing (e2e-testing-ai)

**Priority**: Critical
**Duration**: 2 days
**Dependencies**: All previous phases complete

#### Tasks

- [ ] **Create E2E test scenarios**
  - File: `tests/e2e/test_vendor_order_workflow.py`

  **Scenarios:**
  ```python
  test_vendor_complete_order_workflow:
    1. Vendor logs in
    2. Navigates to orders page
    3. Sees order with their products
    4. Opens order detail
    5. Updates item status to preparing
    6. Updates item status to ready
    7. Verifies timestamps updated
    8. Views stats page
    9. Sees updated metrics

  test_multi_vendor_isolation:
    1. Create order with products from 2 vendors
    2. Vendor A logs in
    3. Sees only their items
    4. Cannot update Vendor B's items
    5. Vendor B logs in
    6. Sees only their items
    7. Cannot update Vendor A's items

  test_status_transition_validation:
    1. Vendor logs in
    2. Attempts invalid status transition
    3. Receives error message
    4. Attempts valid transition
    5. Succeeds

  test_mobile_responsive:
    1. Set mobile viewport
    2. Navigate all pages
    3. Verify layout works
    4. Test swipe gestures
    5. Test touch targets
  ```

- [ ] **Run E2E test suite**
  ```bash
  python -m pytest tests/e2e/test_vendor_order_workflow.py -v
  ```

#### Acceptance Criteria

- [x] All E2E tests pass
- [x] Multi-vendor scenarios work
- [x] Mobile tests pass
- [x] No console errors
- [x] All user flows complete

---

### Phase 4.4: Performance Testing (performance-optimization-ai)

**Priority**: Medium
**Duration**: 1 day
**Dependencies**: Phase 4.3 complete

#### Tasks

- [ ] **Test API performance**
  ```bash
  # Load test with Apache Bench
  ab -n 1000 -c 10 http://localhost:8000/api/v1/vendor/orders

  # Or with wrk
  wrk -t4 -c100 -d30s http://localhost:8000/api/v1/vendor/orders
  ```

- [ ] **Measure response times**
  - GET /vendor/orders: Target < 200ms P95
  - GET /vendor/orders/{id}: Target < 150ms P95
  - PATCH /vendor/orders/.../status: Target < 100ms P95
  - GET /vendor/orders/stats: Target < 300ms P95

- [ ] **Test database query performance**
  ```sql
  EXPLAIN ANALYZE SELECT ...
  ```

- [ ] **Optimize slow queries**
  - Add missing indexes
  - Optimize joins
  - Use query caching

- [ ] **Test frontend performance**
  - Lighthouse audit (target > 90)
  - Time to Interactive < 2s
  - First Contentful Paint < 1s

#### Acceptance Criteria

- [x] All P95 targets met
- [x] No N+1 query problems
- [x] Database queries optimized
- [x] Lighthouse score > 90
- [x] Mobile performance good

---

### Phase 4.5: Security Audit (security-backend-ai)

**Priority**: Critical
**Duration**: 2 days
**Dependencies**: All previous phases complete

#### Tasks

- [ ] **Contact security-backend-ai for audit**
  ```bash
  python .workspace/scripts/contact_responsible_agent.py security-backend-ai app/api/v1/endpoints/vendor_orders.py "Security audit for vendor order management endpoints"
  ```

- [ ] **Test authentication**
  - Verify JWT required on all endpoints
  - Test expired tokens
  - Test invalid tokens
  - Test missing tokens

- [ ] **Test authorization**
  - Verify vendor role required
  - Test buyer accessing vendor endpoints
  - Test admin accessing vendor endpoints
  - Test vendor accessing other vendor's data

- [ ] **Test input validation**
  - SQL injection attempts
  - XSS attempts
  - Invalid status values
  - Invalid order IDs
  - Malformed JSON

- [ ] **Test rate limiting**
  - Verify 100 req/min limit enforced
  - Test rate limit headers
  - Test rate limit exceeded response

- [ ] **Run security scan**
  ```bash
  # OWASP ZAP scan
  docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8000/api/v1/vendor/orders

  # Bandit security scan
  bandit -r app/
  ```

#### Acceptance Criteria

- [x] All auth tests pass
- [x] No SQL injection vulnerabilities
- [x] No XSS vulnerabilities
- [x] Rate limiting works
- [x] OWASP scan passes
- [x] Vendor isolation verified
- [x] Security audit approved by security-backend-ai

---

### Phase 4.6: Documentation (technical-writer-ai)

**Priority**: Medium
**Duration**: 2 days
**Dependencies**: All previous phases complete

#### Tasks

- [ ] **Create API documentation**
  - File: `docs/api/vendor-orders.md`
  - Document all endpoints
  - Add request/response examples
  - Add error codes
  - Add authentication details

- [ ] **Create user guide**
  - File: `docs/user-guides/vendor-order-management.md`
  - Step-by-step instructions
  - Screenshots
  - Common scenarios
  - Troubleshooting

- [ ] **Create video tutorials**
  - "How to manage vendor orders"
  - "How to update order status"
  - "How to view sales statistics"

- [ ] **Update OpenAPI docs**
  - Ensure swagger docs complete
  - Add examples for all schemas
  - Add descriptions

#### Acceptance Criteria

- [x] API docs complete and accurate
- [x] User guide clear and helpful
- [x] Video tutorials recorded
- [x] OpenAPI docs updated
- [x] All screenshots current

---

### Phase 4.7: Staging Deployment (devops-integration-ai)

**Priority**: High
**Duration**: 1 day
**Dependencies**: Phase 4.5 complete

#### Tasks

- [ ] **Deploy backend to staging**
  ```bash
  # Run database migration
  alembic upgrade head

  # Deploy backend
  docker-compose -f docker-compose.staging.yml up -d backend

  # Verify health
  curl http://staging.mestore.com/api/v1/vendor/orders/health
  ```

- [ ] **Deploy frontend to staging**
  ```bash
  # Build production bundle
  cd frontend
  npm run build

  # Deploy to staging
  docker-compose -f docker-compose.staging.yml up -d frontend

  # Verify deployment
  curl http://staging.mestore.com/vendor/orders
  ```

- [ ] **Run smoke tests on staging**
  - Test all endpoints
  - Test frontend pages
  - Verify authentication
  - Verify database connectivity

#### Acceptance Criteria

- [x] Backend deployed successfully
- [x] Frontend deployed successfully
- [x] Database migration complete
- [x] All health checks pass
- [x] Smoke tests pass

---

### Phase 4.8: User Acceptance Testing (product-manager-ai)

**Priority**: High
**Duration**: 3 days
**Dependencies**: Phase 4.7 complete

#### Tasks

- [ ] **Recruit test vendors**
  - Select 5-10 active vendors
  - Provide staging access
  - Brief on new features

- [ ] **Create test scenarios**
  - Scenario 1: View new order
  - Scenario 2: Update item status
  - Scenario 3: View sales stats
  - Scenario 4: Filter and search
  - Scenario 5: Multi-vendor order

- [ ] **Collect feedback**
  - Usability issues
  - UI/UX improvements
  - Feature requests
  - Bug reports

- [ ] **Fix critical issues**
  - Prioritize bugs
  - Fix blocking issues
  - Re-test fixes

- [ ] **Get approval to proceed**
  - Sign-off from test vendors
  - Sign-off from product manager
  - Sign-off from CEO

#### Acceptance Criteria

- [x] UAT completed by 5+ vendors
- [x] Critical bugs fixed
- [x] Usability score > 4/5
- [x] Approval received

---

### Phase 4.9: Production Deployment (devops-integration-ai)

**Priority**: Critical
**Duration**: 1 day
**Dependencies**: Phase 4.8 complete

#### Tasks

- [ ] **Schedule deployment window**
  - Date/time: _______________
  - Duration: 1 hour
  - Notify users via email

- [ ] **Backup production database**
  ```bash
  pg_dump mestore_production > backup_prod_$(date +%Y%m%d_%H%M%S).sql
  aws s3 cp backup_prod_*.sql s3://mestore-backups/
  ```

- [ ] **Run database migration**
  ```bash
  # Production migration
  alembic upgrade head

  # Verify migration
  alembic current
  psql -d mestore_production -c "\d order_items"
  ```

- [ ] **Deploy backend**
  ```bash
  # Deploy with zero-downtime
  docker-compose -f docker-compose.production.yml up -d --no-deps backend

  # Verify health
  curl https://api.mestore.com/api/v1/vendor/orders/health
  ```

- [ ] **Deploy frontend**
  ```bash
  # Build production
  npm run build

  # Deploy to CDN
  aws s3 sync frontend/dist/ s3://mestore-frontend/
  aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
  ```

- [ ] **Monitor deployment**
  - Watch error logs
  - Monitor API metrics
  - Check user reports
  - Verify all features work

- [ ] **Rollback plan ready**
  ```bash
  # If issues occur:
  alembic downgrade -1
  docker-compose -f docker-compose.production.yml restart
  ```

#### Acceptance Criteria

- [x] Database migration successful
- [x] Backend deployed with zero downtime
- [x] Frontend deployed successfully
- [x] All health checks pass
- [x] No critical errors in logs
- [x] Monitoring shows normal metrics

---

### Phase 4.10: Post-Deployment (all agents)

**Priority**: Medium
**Duration**: Ongoing

#### Tasks

- [ ] **Monitor for 24 hours**
  - Error rates
  - Response times
  - User adoption
  - Support tickets

- [ ] **Create monitoring dashboard**
  - Vendor order stats
  - API performance
  - Error rates
  - User activity

- [ ] **Send announcement**
  - Email to all vendors
  - In-app notification
  - Blog post
  - Social media

- [ ] **Collect metrics**
  - Vendor adoption rate (target > 80% in 1 month)
  - Order prep time (target 30% reduction)
  - Support tickets (target 50% reduction)
  - User satisfaction (target > 4.5/5)

- [ ] **Plan Phase 2 features**
  - Email notifications
  - WhatsApp integration
  - Bulk operations
  - Advanced analytics

#### Acceptance Criteria

- [x] 24-hour monitoring complete
- [x] No critical issues
- [x] Announcement sent
- [x] Metrics tracking set up
- [x] Phase 2 planning started

---

## Agent Coordination Matrix

| Phase | Primary Agent | Supporting Agents | Approval Needed From |
|-------|---------------|-------------------|---------------------|
| 1.1 Database Migration | database-architect-ai | - | database-architect-ai |
| 1.2 Backend Schemas | backend-framework-ai | - | - |
| 1.3 Vendor Order Service | backend-framework-ai | database-architect-ai | - |
| 1.4 API Endpoints | backend-framework-ai | api-architect-ai | - |
| 2.1 TDD Test Suite | tdd-specialist | backend-framework-ai | tdd-specialist (fixtures) |
| 2.2 Frontend Types | react-specialist-ai | - | - |
| 2.3 Frontend Service | react-specialist-ai | - | - |
| 3.1 Shared Components | react-specialist-ai | ui-ux-specialist | - |
| 3.2 VendorOrderManagement | react-specialist-ai | - | - |
| 3.3 VendorOrderDetail | react-specialist-ai | - | - |
| 3.4 VendorOrderStats | react-specialist-ai | data-visualization-ai | - |
| 4.1 Routing | react-specialist-ai | - | - |
| 4.2 Frontend Testing | react-specialist-ai | tdd-specialist | - |
| 4.3 Integration Testing | e2e-testing-ai | tdd-specialist | - |
| 4.4 Performance Testing | performance-optimization-ai | - | - |
| 4.5 Security Audit | security-backend-ai | - | security-backend-ai |
| 4.6 Documentation | technical-writer-ai | - | - |
| 4.7 Staging Deployment | devops-integration-ai | cloud-infrastructure-ai | - |
| 4.8 UAT | product-manager-ai | - | director-enterprise-ceo |
| 4.9 Production Deployment | devops-integration-ai | cloud-infrastructure-ai | master-orchestrator |
| 4.10 Post-Deployment | master-orchestrator | all | - |

---

## Risk Mitigation Checklist

### Pre-Implementation

- [x] All protected files identified
- [x] Agent approvals obtained
- [x] Backup strategy defined
- [x] Rollback procedures documented
- [x] Testing strategy complete

### During Implementation

- [ ] Daily standup with involved agents
- [ ] Continuous integration running
- [ ] Test coverage monitored
- [ ] Security checks automated
- [ ] Code review for all PRs

### Pre-Deployment

- [ ] All tests passing (backend + frontend)
- [ ] Security audit complete
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] UAT approved
- [ ] Rollback tested

### Post-Deployment

- [ ] 24/7 monitoring active
- [ ] On-call rotation defined
- [ ] Support team trained
- [ ] Hotfix process ready
- [ ] Metrics tracking active

---

## Commit Template

```
<type>(<scope>): <description>

Workspace-Check: ✅ Consultado
File: <file-path>
Agent: <your-agent-name>
Protocol: [FOLLOWED/PRIOR_CONSULTATION/APPROVAL_OBTAINED]
Tests: [PASSED/FAILED]
Code-Standard: ✅ ENGLISH_CODE / ✅ SPANISH_UI
Admin-Portal: [VERIFIED/NOT_APPLICABLE]
Hook-Violations: [NONE/FIXED]
Responsible: <approving-agent> (if applicable)

<detailed description>

<footer>
```

**Example:**
```
feat(vendor-orders): Add vendor order list endpoint

Workspace-Check: ✅ Consultado
File: app/api/v1/endpoints/vendor_orders.py
Agent: backend-framework-ai
Protocol: FOLLOWED
Tests: PASSED
Code-Standard: ✅ ENGLISH_CODE
Responsible: N/A

Implement GET /api/v1/vendor/orders endpoint for vendor order management.

Features:
- Filter by order status and preparation status
- Pagination support (max 100 items)
- Eager loading for performance
- Security: vendor can only see their orders

Tests: 12 passed, coverage 85%
```

---

## Success Criteria Summary

### Technical

- [ ] All migrations successful
- [ ] Test coverage > 80%
- [ ] P95 latency < 200ms
- [ ] Zero critical security issues
- [ ] Mobile Lighthouse score > 90

### Business

- [ ] Vendor adoption > 80% in 1 month
- [ ] Order prep time reduced by 30%
- [ ] Support tickets reduced by 50%
- [ ] Vendor satisfaction > 4.5/5

### Quality

- [ ] All E2E tests passing
- [ ] No production bugs in first week
- [ ] Code review approval for all PRs
- [ ] Documentation complete
- [ ] Training materials ready

---

**Document Version**: 1.0
**Created**: 2025-10-03
**Status**: Ready for Execution
**Next Review**: Weekly during implementation

