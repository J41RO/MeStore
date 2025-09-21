# Skipped Tests Enablement Plan
*Test Architect - 2025-09-20*

## 🎯 OVERVIEW
**Current Skipped Tests**: 158 tests across 25+ files
**Target**: Enable all critical tests (estimated 120+ tests)
**Timeline**: 4-week phased approach

## 📊 SKIPPED TESTS INVENTORY

### 🔥 CRITICAL PRIORITY (Week 1) - 45 Tests

#### Authentication & Security (15 tests)
```bash
File: tests/api/test_critical_endpoints_mvp.py
- test_refresh_token_success                    # Auth flow
- test_logout_success                          # Session cleanup
- test_get_payment_methods_success             # Payment auth

Reason: "Complex async mocking - needs refactoring"
Issue: Async dependency injection conflicts
Solution: Implement proper async fixture patterns
```

#### Payment System (25 tests)
```bash
File: tests/api/test_payments_endpoints.py
- TestPaymentsEndpoints (25 methods)           # Full payment testing
- TestPaymentsAuthentication (5 methods)       # Payment auth
- TestPaymentsSecurity (8 methods)             # Payment security
- TestPaymentsErrorHandling (12 methods)       # Error scenarios

Reason: "Payments testing requires complex external service mocking"
Issue: Wompi service dependency not mocked
Solution: Create comprehensive Wompi mock service
```

#### Order Processing (5 tests)
```bash
File: tests/api/test_orders_endpoints.py
- test_get_user_orders_success                 # Core functionality
- test_create_order_success                    # Order creation
- test_get_user_orders_with_pagination         # Pagination
- test_get_user_orders_with_status_filter      # Filtering
- test_get_user_orders_unauthorized            # Security

Reason: "Complex dependency injection issue with orders endpoint"
Issue: Database session conflicts with auth dependencies
Solution: Isolate dependencies using proper fixture setup
```

### ⚠️ HIGH PRIORITY (Week 2) - 60 Tests

#### Vendor Management (35 tests)
```bash
File: tests/api/test_vendor_endpoints.py
- Entire test suite skipped                    # All vendor functionality

Reason: "Vendor endpoint tests - performance optimization during database work"
Issue: Performance optimization during development
Solution: Re-enable with optimized test data and fixtures
```

#### Product Management (33 tests)
```bash
File: tests/api/test_productos.py
- Entire test suite skipped                    # All product functionality

Reason: "Product tests - performance optimization during database work"
Issue: Performance optimization during development
Solution: Streamline test data and enable incrementally
```

#### Product Upload (9 tests)
```bash
File: tests/api/test_productos_upload.py
- Entire test suite skipped                    # File upload functionality

Reason: "Product upload tests - performance optimization during database work"
Issue: File handling complexity during optimization
Solution: Mock file operations and enable testing
```

### 🟡 MEDIUM PRIORITY (Week 3) - 35 Tests

#### Vendor Analytics (18 tests)
```bash
File: tests/api/test_vendor_analytics.py
- Entire test suite skipped                    # WebSocket analytics

Reason: "WebSocket analytics tests - performance optimization during database work"
Issue: WebSocket testing complexity
Solution: Mock WebSocket connections and enable testing
```

#### Banking Profiles (3 tests)
```bash
File: tests/api/test_perfil_bancarios.py
- Entire test suite skipped                    # Banking integration

Reason: "Banking profile tests - performance optimization during database work"
Issue: External banking service dependencies
Solution: Mock banking services and enable testing
```

#### Payment History (1 test)
```bash
File: tests/api/test_pagos_historial.py
- test_get_historial_pagos_basic               # Payment history

Reason: "Database performance optimization - test incompatible with current setup"
Issue: Database performance issues
Solution: Optimize database queries and enable
```

#### Health Endpoints (1 test)
```bash
File: tests/api/test_health.py
- test_health_full_v1_endpoint                 # Health check

Reason: "Endpoint dependency injection issues during testing"
Issue: Dependency injection conflicts
Solution: Fix dependency setup and enable
```

#### Orders Authentication & Error Handling (12 tests)
```bash
File: tests/api/test_orders_endpoints.py
- TestOrdersAuthentication (6 methods)         # Auth testing
- TestOrdersErrorHandling (6 methods)          # Error scenarios

Reason: "Authentication/Error handling testing incompatible with performance optimizations"
Issue: Complex test setup during optimization
Solution: Simplify test setup and re-enable
```

### 🟢 LOW PRIORITY (Week 4) - 18 Tests

#### Debugging Tests (8 tests)
```bash
File: tests/debugging/test_duplicados_corregido.py
File: tests/debugging/test_log_rotation.py
- Entire debugging test suites skipped

Reason: "Debugging tests - performance optimization during database work"
Issue: Debugging tests not needed in CI/CD
Solution: Keep disabled or move to separate test category
```

#### Performance & Optimization (10 tests)
```bash
Various files with optimization-related skips
- Complex validation testing
- Performance testing incompatible with current setup

Reason: "Performance optimization during development"
Issue: Tests conflict with performance work
Solution: Re-enable after performance optimization complete
```

## 🛠️ ENABLEMENT IMPLEMENTATION PLAN

### Week 1: Critical Foundation Tests

#### Day 1-2: Authentication System
```python
# Fix: tests/api/test_critical_endpoints_mvp.py
# Issues: Async dependency injection

# Solution Pattern:
@pytest.fixture
async def async_auth_client():
    async with AsyncClient() as client:
        # Proper async client setup
        yield client

@pytest.mark.asyncio
async def test_refresh_token_success(async_auth_client, mock_db, mock_user):
    # Remove skip decorator
    # Use proper async patterns
    response = await async_auth_client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
```

#### Day 3-4: Payment System Foundation
```python
# Fix: tests/api/test_payments_endpoints.py
# Issues: External service mocking

# Solution: Create Wompi Mock Service
@pytest.fixture
def mock_wompi_service():
    with patch('app.services.payments.wompi_service.WompiService') as mock:
        mock.create_payment_intent.return_value = {
            "id": "test_payment_id",
            "status": "pending"
        }
        yield mock

# Enable tests one by one with proper mocking
class TestPaymentsEndpoints:
    def test_create_payment_intent_success(self, mock_wompi_service):
        # Test implementation with mock
        pass
```

#### Day 5: Order Processing Foundation
```python
# Fix: tests/api/test_orders_endpoints.py
# Issues: Database session conflicts

# Solution: Proper dependency isolation
@pytest.fixture
def isolated_order_client(mock_db):
    # Isolate database dependencies
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Week 2: Core Business Logic

#### Day 1-3: Vendor Management
```python
# Fix: tests/api/test_vendor_endpoints.py
# Issues: Performance optimization

# Solution: Optimized test data
@pytest.fixture
def minimal_vendor_data():
    return {
        "name": "Test Vendor",
        "email": "test@vendor.com",
        "document": "123456789"
    }

# Remove pytestmark skip and enable tests incrementally
def test_vendor_registration(minimal_vendor_data):
    # Streamlined test with minimal data
    pass
```

#### Day 4-5: Product Management
```python
# Fix: tests/api/test_productos.py
# Issues: Performance optimization

# Solution: Lightweight product fixtures
@pytest.fixture
def minimal_product():
    return {
        "name": "Test Product",
        "price": 100.0,
        "category_id": 1
    }

# Enable tests with optimized fixtures
def test_product_creation(minimal_product):
    # Fast test with minimal data
    pass
```

### Week 3: Advanced Features

#### Day 1-2: Vendor Analytics
```python
# Fix: tests/api/test_vendor_analytics.py
# Issues: WebSocket complexity

# Solution: Mock WebSocket connections
@pytest.fixture
def mock_websocket():
    with patch('app.services.analytics_service.WebSocket') as mock:
        yield mock

def test_vendor_analytics_websocket(mock_websocket):
    # Test with mocked WebSocket
    pass
```

#### Day 3-5: Remaining Medium Priority
- Banking profiles with service mocks
- Payment history with optimized queries
- Orders auth and error handling

### Week 4: Quality & Optimization

#### Day 1-3: Performance Testing
- Re-enable performance-related tests
- Optimize test execution speed
- Add performance benchmarks

#### Day 4-5: Final Validation
- Run full test suite
- Validate coverage targets
- Document remaining skips (if any)

## 🔧 TECHNICAL SOLUTIONS

### Common Patterns for Enablement

#### 1. Async Dependency Injection Fix
```python
# Pattern for fixing async dependency issues
@pytest.fixture
async def async_client_with_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup auth headers
        client.headers.update({"Authorization": "Bearer test-token"})
        yield client
```

#### 2. External Service Mocking
```python
# Pattern for mocking external services
@pytest.fixture(autouse=True)
def mock_external_services():
    with patch.multiple(
        'app.services.integrated_payment_service',
        wompi_service=MagicMock(),
        email_service=MagicMock(),
        sms_service=MagicMock()
    ):
        yield
```

#### 3. Database Performance Optimization
```python
# Pattern for optimizing database tests
@pytest.fixture
def fast_db_session():
    # Use in-memory SQLite for speed
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine
```

#### 4. Dependency Override Pattern
```python
# Pattern for proper dependency overrides
@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_db] = lambda: test_db
    yield
    app.dependency_overrides.clear()
```

## 📋 VALIDATION CHECKLIST

### Week 1 Success Criteria
- [ ] All authentication tests enabled and passing
- [ ] Payment system foundation tests enabled
- [ ] Order processing core tests enabled
- [ ] Zero failing tests in critical modules

### Week 2 Success Criteria
- [ ] Vendor management tests enabled
- [ ] Product management tests enabled
- [ ] Product upload tests enabled
- [ ] Performance optimization maintained

### Week 3 Success Criteria
- [ ] Vendor analytics tests enabled
- [ ] Banking profile tests enabled
- [ ] Payment history tests enabled
- [ ] Orders auth/error tests enabled

### Week 4 Success Criteria
- [ ] All critical tests enabled (120+ tests)
- [ ] Test suite execution <30 seconds
- [ ] Coverage increase to 85%+
- [ ] Zero skipped critical business logic tests

## 🚨 RISK MITIGATION

### Potential Blockers
1. **Environment Variable Issues**: SECRET_KEY and other config
2. **Database Migration Conflicts**: Test database schema
3. **Async Pattern Complexity**: Proper async test setup
4. **External Service Dependencies**: Comprehensive mocking

### Mitigation Strategies
1. **Environment Setup**: Standardized test environment configuration
2. **Database Isolation**: Proper test database setup and teardown
3. **Async Best Practices**: Documented patterns for async testing
4. **Mock Services**: Comprehensive mock library for external services

### Rollback Plan
If enablement causes issues:
1. **Immediate**: Re-skip problematic tests
2. **Short-term**: Fix issues and re-enable incrementally
3. **Long-term**: Refactor test architecture if needed

---

## 📈 PROGRESS TRACKING

### Daily Metrics
- Tests enabled: X/158
- Tests passing: X/enabled
- Coverage increase: +X%
- Execution time: Xs

### Weekly Reviews
- Blockers identified and resolved
- Performance impact assessment
- Coverage trend analysis
- Next week planning

---

*This plan provides a systematic approach to enabling all 158 skipped tests while maintaining system stability and performance.*