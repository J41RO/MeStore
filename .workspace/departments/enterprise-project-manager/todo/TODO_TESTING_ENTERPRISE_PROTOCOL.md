# 🧪 PROTOCOLO TESTING ENTERPRISE - >85% COBERTURA GARANTIZADA

**Specialist Responsable**: @qa-engineer-pytest
**Objetivo**: Mantener cobertura >85% en backend FastAPI + frontend React/TypeScript
**Compatible con**: TODO_CONFIGURACION_BASE_ENTERPRISE.md ✅
**Integración**: Todos los módulos del sistema

---

## 🎯 ESTRATEGIA DE TESTING ENTERPRISE

### COBERTURA OBLIGATORIA POR MÓDULO:
```
📦 Módulo Products:     >85% cobertura (models + services + APIs + UI)
👥 Módulo Users:        >85% cobertura (auth + permissions + profiles)
🏪 Módulo Orders:       >90% cobertura (critical business logic)
💰 Módulo Payments:     >95% cobertura (financial transactions)
📊 Módulo Analytics:    >85% cobertura (reports + calculations)
📧 Módulo Notifications: >85% cobertura (delivery + templates)
🔒 Módulo Security:     >95% cobertura (auth + encryption + audit)
🤖 Módulo AI-Ready:     >85% cobertura (framework + interfaces)
```

---

## 🔧 BACKEND TESTING - FastAPI + Python

### TESTING STACK BACKEND:
```python
# Testing Dependencies - requirements-test.txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0  # For async API testing
pytest-mock>=3.11.0
factoryboy>=3.3.0  # Test data factories
freezegun>=1.2.0  # Time mocking
pytest-benchmark>=4.0.0  # Performance testing
pytest-xdist>=3.3.0  # Parallel testing
```

### 1. UNIT TESTS - Models & Services (Target: >90%)

```python
# tests/unit/models/test_product_model.py
import pytest
from app.models.product import Product, ProductVariant, ProductCategory
from tests.factories.product_factory import ProductFactory

class TestProductModel:
    def test_product_creation_with_required_fields(self):
        """Test product creation with minimum required fields"""
        product = ProductFactory.build()
        assert product.name is not None
        assert product.price > 0
        assert product.vendor_id is not None

    def test_product_sku_generation(self):
        """Test automatic SKU generation"""
        product = ProductFactory.create()
        assert product.sku is not None
        assert len(product.sku) >= 8

    def test_product_price_history_tracking(self):
        """Test price change tracking"""
        product = ProductFactory.create(price=100.00)
        product.update_price(150.00, changed_by=1)
        assert len(product.price_history) == 1
        assert product.price_history[0]['old_price'] == 100.00

    @pytest.mark.parametrize("role,can_access", [
        ("SUPERUSER", True),
        ("VENDOR", True),
        ("BUYER", False),
        ("ADMIN_VENTAS", True)
    ])
    def test_product_access_permissions(self, role, can_access):
        """Test product access based on user role"""
        product = ProductFactory.create()
        user = UserFactory.create(user_type=role)
        assert product.can_be_accessed_by(user) == can_access
```

### 2. INTEGRATION TESTS - APIs (Target: >88%)

```python
# tests/integration/api/test_product_endpoints.py
import pytest
from httpx import AsyncClient
from app.main import app
from tests.factories.user_factory import UserFactory

@pytest.mark.asyncio
class TestProductAPIs:
    async def test_superuser_can_get_all_products(self, async_client: AsyncClient):
        """SUPERUSER should access all products from all vendors"""
        superuser = UserFactory.create(user_type="SUPERUSER")
        ProductFactory.create_batch(5)  # Different vendors

        response = await async_client.get(
            "/api/v1/superuser/products/all",
            headers={"Authorization": f"Bearer {superuser.access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 5
        assert data["total_count"] == 5

    async def test_vendor_can_only_see_own_products(self, async_client: AsyncClient):
        """Vendor should only see their own products"""
        vendor = UserFactory.create(user_type="VENDOR")
        ProductFactory.create_batch(3, vendor_id=vendor.id)
        ProductFactory.create_batch(2)  # Other vendors

        response = await async_client.get(
            "/api/v1/vendor/products/",
            headers={"Authorization": f"Bearer {vendor.access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 3  # Only own products

    async def test_bulk_product_update_superuser_only(self, async_client: AsyncClient):
        """Only SUPERUSER can perform bulk operations"""
        vendor = UserFactory.create(user_type="VENDOR")
        products = ProductFactory.create_batch(3)

        bulk_data = {
            "product_ids": [p.id for p in products],
            "updates": {"is_featured": True}
        }

        # Vendor should be denied
        response = await async_client.post(
            "/api/v1/superuser/products/bulk-update",
            json=bulk_data,
            headers={"Authorization": f"Bearer {vendor.access_token}"}
        )
        assert response.status_code == 403

        # SUPERUSER should succeed
        superuser = UserFactory.create(user_type="SUPERUSER")
        response = await async_client.post(
            "/api/v1/superuser/products/bulk-update",
            json=bulk_data,
            headers={"Authorization": f"Bearer {superuser.access_token}"}
        )
        assert response.status_code == 200
```

### 3. PERFORMANCE TESTS - Load Testing

```python
# tests/performance/test_product_performance.py
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

class TestProductPerformance:
    def test_product_search_performance(self, benchmark: BenchmarkFixture):
        """Product search should complete within acceptable time"""
        def search_products():
            return ProductService.search_products(
                query="smartphone",
                filters={"category": "electronics"},
                limit=50
            )

        result = benchmark(search_products)
        assert len(result) > 0
        # Benchmark will automatically fail if >500ms (configured)

    @pytest.mark.asyncio
    async def test_bulk_product_update_performance(self, benchmark: BenchmarkFixture):
        """Bulk operations should handle 1000+ products efficiently"""
        products = ProductFactory.create_batch(1000)

        async def bulk_update():
            return await ProductService.bulk_update_products(
                product_ids=[p.id for p in products[:100]],
                updates={"is_featured": True}
            )

        result = await benchmark(bulk_update)
        assert result["updated_count"] == 100
```

---

## ⚛️ FRONTEND TESTING - React + TypeScript

### TESTING STACK FRONTEND:
```json
// frontend/package.json - Testing dependencies
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.0.0",
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "jsdom": "^23.0.0",
    "msw": "^2.0.0",  // Mock Service Worker
    "@vitest/coverage-v8": "^1.0.0",
    "axe-jest": "^4.8.0"  // Accessibility testing
  }
}
```

### 1. COMPONENT UNIT TESTS (Target: >85%)

```typescript
// frontend/src/components/__tests__/ProductManagementDashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { ProductManagementDashboard } from '../ProductManagementDashboard';
import { productService } from '../../services/productService';

// Mock service
vi.mock('../../services/productService');

describe('ProductManagementDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders dashboard for SUPERUSER with all products', async () => {
    // Mock auth store
    const mockAuthStore = {
      user: { user_type: 'SUPERUSER', id: 1 },
      hasPermission: vi.fn().mockReturnValue(true)
    };

    // Mock service response
    productService.getAllProducts = vi.fn().mockResolvedValue({
      products: [
        { id: 1, name: 'Product 1', vendor_id: 1 },
        { id: 2, name: 'Product 2', vendor_id: 2 }
      ],
      total: 2
    });

    render(
      <AuthProvider value={mockAuthStore}>
        <ProductManagementDashboard />
      </AuthProvider>
    );

    // Verify SUPERUSER can see all products
    await waitFor(() => {
      expect(screen.getByText('Product 1')).toBeInTheDocument();
      expect(screen.getByText('Product 2')).toBeInTheDocument();
    });

    expect(productService.getAllProducts).toHaveBeenCalledTimes(1);
  });

  test('bulk actions are available for SUPERUSER', async () => {
    const user = userEvent.setup();

    render(
      <AuthProvider value={{ user: { user_type: 'SUPERUSER' }}}>
        <ProductManagementDashboard />
      </AuthProvider>
    );

    // Check bulk action buttons
    expect(screen.getByText('Bulk Edit')).toBeInTheDocument();
    expect(screen.getByText('Bulk Delete')).toBeInTheDocument();
    expect(screen.getByText('Export All')).toBeInTheDocument();

    // Test bulk selection
    const selectAllCheckbox = screen.getByRole('checkbox', { name: /select all/i });
    await user.click(selectAllCheckbox);

    expect(screen.getByText('2 products selected')).toBeInTheDocument();
  });

  test('denies access for non-SUPERUSER', () => {
    render(
      <AuthProvider value={{
        user: { user_type: 'VENDOR' },
        hasPermission: vi.fn().mockReturnValue(false)
      }}>
        <ProductManagementDashboard />
      </AuthProvider>
    );

    expect(screen.getByText('Unauthorized')).toBeInTheDocument();
    expect(productService.getAllProducts).not.toHaveBeenCalled();
  });
});
```

### 2. INTEGRATION TESTS - API Integration (Target: >90%)

```typescript
// frontend/src/services/__tests__/productService.integration.test.ts
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { productService } from '../productService';

const server = setupServer(
  rest.get('/api/v1/superuser/products/all', (req, res, ctx) => {
    return res(
      ctx.json({
        products: [
          { id: 1, name: 'Test Product', price: 100 }
        ],
        total: 1
      })
    );
  }),

  rest.post('/api/v1/superuser/products/bulk-update', (req, res, ctx) => {
    return res(
      ctx.json({ updated_count: 5, success: true })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ProductService Integration', () => {
  test('getAllProducts fetches data correctly', async () => {
    const result = await productService.getAllProducts();

    expect(result.products).toHaveLength(1);
    expect(result.products[0].name).toBe('Test Product');
    expect(result.total).toBe(1);
  });

  test('bulkUpdateProducts sends correct payload', async () => {
    const updateData = {
      product_ids: [1, 2, 3],
      updates: { is_featured: true }
    };

    const result = await productService.bulkUpdateProducts(updateData);

    expect(result.success).toBe(true);
    expect(result.updated_count).toBe(5);
  });

  test('handles API errors gracefully', async () => {
    server.use(
      rest.get('/api/v1/superuser/products/all', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    await expect(productService.getAllProducts()).rejects.toThrow('Server error');
  });
});
```

### 3. E2E TESTS - Complete User Workflows (Target: >80%)

```typescript
// frontend/e2e/product-management.e2e.test.ts
import { test, expect } from '@playwright/test';

test.describe('Product Management E2E', () => {
  test('SUPERUSER can manage all vendor products', async ({ page }) => {
    // Login as SUPERUSER
    await page.goto('/admin-login');
    await page.fill('[name="email"]', 'admin@mestore.com');
    await page.fill('[name="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Navigate to product management
    await page.goto('/admin/products');
    await expect(page.locator('h1')).toContainText('Product Management');

    // Verify can see all products from all vendors
    await expect(page.locator('[data-testid="product-row"]')).toHaveCount.greaterThan(0);

    // Test search functionality
    await page.fill('[name="search"]', 'smartphone');
    await page.keyboard.press('Enter');
    await expect(page.locator('[data-testid="product-row"]')).toHaveCount.lessThanOrEqual(10);

    // Test bulk operations
    await page.click('[data-testid="select-all"]');
    await page.click('[data-testid="bulk-feature"]');
    await expect(page.locator('[data-testid="success-notification"]')).toBeVisible();
  });

  test('Vendor can only manage own products', async ({ page }) => {
    // Login as vendor
    await page.goto('/login');
    await page.fill('[name="email"]', 'vendor@example.com');
    await page.fill('[name="password"]', 'vendor123');
    await page.click('button[type="submit"]');

    // Navigate to vendor products
    await page.goto('/vendor/products');

    // Verify only sees own products
    const productRows = await page.locator('[data-testid="product-row"]').all();
    for (const row of productRows) {
      await expect(row.locator('[data-testid="vendor-name"]')).toContainText('Current Vendor');
    }

    // Verify no access to bulk operations for other vendors
    await expect(page.locator('[data-testid="bulk-edit-all"]')).not.toBeVisible();
  });
});
```

---

## 📊 COVERAGE CONFIGURATION & AUTOMATION

### Backend Coverage Config:
```ini
# .coveragerc
[run]
source = app/
omit =
    app/tests/*
    app/migrations/*
    app/__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = coverage_html_report
```

### Frontend Coverage Config:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 85,
      functions: 85,
      branches: 80,
      statements: 85,
      exclude: [
        'coverage/**',
        'dist/**',
        'packages/*/test{,s}/**',
        '**/*.d.ts',
        '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*'
      ]
    }
  }
});
```

### Automated Testing Pipeline:
```yaml
# .github/workflows/testing.yml
name: Enterprise Testing Pipeline

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Backend Unit & Integration Tests
        run: |
          pytest tests/ --cov=app --cov-report=xml --cov-fail-under=85
      - name: Upload Backend Coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Frontend Tests
        run: |
          npm test -- --coverage --watchAll=false
          npx vitest run --coverage
      - name: Upload Frontend Coverage
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: E2E Tests
        run: |
          npm run test:e2e
```

---

## 🎯 TESTING PROTOCOL PER MODULE

### Para cada módulo nuevo:

1. **@qa-engineer-pytest** ejecuta ANTES del desarrollo:
   ```bash
   # Crear estructura de tests
   mkdir -p tests/{unit,integration,e2e}/module_name
   # Crear test templates
   # Configurar mocks y fixtures
   ```

2. **Durante desarrollo** (TDD approach):
   ```bash
   # Escribir tests ANTES de implementar
   pytest tests/unit/module_name/ --cov=app/module_name --cov-fail-under=85
   ```

3. **Post-desarrollo** (Validation):
   ```bash
   # Full test suite
   pytest tests/ --cov=app --cov-report=html --cov-fail-under=85
   npm test -- --coverage --watchAll=false
   npx playwright test
   ```

### Criterios de Aceptación para cada módulo:
- [ ] Unit Tests: >90% cobertura
- [ ] Integration Tests: >85% cobertura
- [ ] E2E Tests: Workflows críticos cubiertos
- [ ] Performance Tests: Load testing passed
- [ ] Security Tests: Vulnerability scan clean
- [ ] Accessibility Tests: WCAG 2.1 AA compliant

---

## 🚨 TESTING QUALITY GATES

### PRE-MERGE Requirements:
```bash
# All tests must pass
pytest tests/ --tb=short
npm test -- --watchAll=false
npx playwright test

# Coverage thresholds must be met
pytest --cov=app --cov-fail-under=85
npm test -- --coverage --coverageThreshold='{"global":{"lines":85}}'

# No critical security issues
bandit -r app/
npm audit --audit-level critical
```

### PRODUCTION DEPLOYMENT Gates:
- [ ] All modules >85% test coverage
- [ ] E2E tests passing in staging
- [ ] Performance benchmarks met
- [ ] Security audit clean
- [ ] Load testing successful

---

**🧪 TESTING ENTERPRISE COMPLETAMENTE CONFIGURADO**
**🎯 COBERTURA >85% GARANTIZADA**
**🔒 QUALITY GATES AUTOMATIZADOS**
**⚡ CONTINUOUS TESTING PIPELINE**