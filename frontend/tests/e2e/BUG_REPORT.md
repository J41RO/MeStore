# Bug Report - E2E Testing Checkout Flow

**Date**: 2025-10-01
**Reporter**: e2e-testing-ai
**Severity Scale**: 🔴 Critical | 🟠 High | 🟡 Medium | 🔵 Low | ℹ️ Info

---

## 🔴 BUG #1: Missing data-testid Attributes Throughout Application

**Severity**: Critical
**Priority**: P0
**Component**: Frontend - All checkout-related components
**Impact**: E2E tests cannot reliably locate UI elements
**Status**: Open

### Description
UI components lack `data-testid` attributes necessary for reliable automated testing. This prevents E2E test execution and makes tests brittle (dependent on class names or text content that may change).

### Affected Components

#### Marketplace Page
```tsx
❌ Missing: [data-testid="product-grid"]
❌ Missing: [data-testid="product-card-{id}"]
❌ Missing: [data-testid="category-navigation"]
❌ Missing: [data-testid="category-{name}"]
❌ Missing: [data-testid="search-input"]
```

#### Product Detail Page
```tsx
❌ Missing: [data-testid="product-detail"]
❌ Missing: [data-testid="product-name"]
❌ Missing: [data-testid="product-price"]
❌ Missing: [data-testid="product-stock"]
❌ Missing: [data-testid="quantity-input"]
❌ Missing: [data-testid="add-to-cart-button"]
❌ Missing: [data-testid="out-of-stock-badge"]
❌ Missing: [data-testid="low-stock-warning"]
```

#### Cart Components
```tsx
❌ Missing: [data-testid="cart-button"]
❌ Missing: [data-testid="cart-drawer"]
❌ Missing: [data-testid="cart-item-{id}"]
❌ Missing: [data-testid="cart-item-quantity"]
❌ Missing: [data-testid="cart-item-price"]
❌ Missing: [data-testid="remove-item"]
❌ Missing: [data-testid="cart-subtotal"]
❌ Missing: [data-testid="cart-iva"]
❌ Missing: [data-testid="cart-shipping"]
❌ Missing: [data-testid="cart-total"]
❌ Missing: [data-testid="proceed-to-checkout"]
❌ Missing: [data-testid="close-cart"]
❌ Missing: [data-testid="add-to-cart-success"]
```

#### Checkout Pages
```tsx
❌ Missing: [data-testid="checkout-progress"]
❌ Missing: [data-testid="shipping-form"]
❌ Missing: [data-testid="shipping-name"]
❌ Missing: [data-testid="shipping-phone"]
❌ Missing: [data-testid="shipping-address"]
❌ Missing: [data-testid="shipping-city"]
❌ Missing: [data-testid="shipping-department"]
❌ Missing: [data-testid="continue-to-payment"]
❌ Missing: [data-testid="error-shipping-name"]
❌ Missing: [data-testid="error-shipping-phone"]
❌ Missing: [data-testid="error-shipping-address"]
```

#### Payment Components
```tsx
❌ Missing: [data-testid="payment-step"]
❌ Missing: [data-testid="payment-method-credit_card"]
❌ Missing: [data-testid="payment-method-pse"]
❌ Missing: [data-testid="payment-method-nequi"]
❌ Missing: [data-testid="payment-method-cash_on_delivery"]
❌ Missing: [data-testid="wompi-container"]
❌ Missing: [data-testid="payment-amount"]
❌ Missing: [data-testid="payment-reference"]
❌ Missing: [data-testid="process-payment"]
❌ Missing: [data-testid="payment-processing"]
❌ Missing: [data-testid="payment-error"]
❌ Missing: [data-testid="payment-security-info"]
❌ Missing: [data-testid="pse-bank-selector"]
```

#### Confirmation Page
```tsx
❌ Missing: [data-testid="confirmation-page"]
❌ Missing: [data-testid="order-id"]
❌ Missing: [data-testid="order-summary"]
```

### Reproduction Steps
1. Run E2E test suite: `npm run test:e2e`
2. Observe tests failing with "selector not found" errors
3. Check component code - no data-testid attributes present

### Expected Behavior
All interactive UI elements should have `data-testid` attributes for reliable automated testing.

### Actual Behavior
Components lack test identifiers, making E2E testing impossible.

### Recommended Fix

#### Example Implementation
```tsx
// MarketplaceLayout.tsx
export function MarketplaceLayout() {
  return (
    <div className="marketplace">
      <div className="product-grid" data-testid="product-grid">
        {products.map(product => (
          <ProductCard
            key={product.id}
            product={product}
            data-testid={`product-card-${product.id}`}
          />
        ))}
      </div>
    </div>
  );
}

// AddToCartButton.tsx
export function AddToCartButton({ onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      data-testid="add-to-cart-button"
      className="btn-primary"
    >
      Add to Cart
    </button>
  );
}

// CartDrawer.tsx
export function CartDrawer() {
  return (
    <div data-testid="cart-drawer" className="drawer">
      <div className="cart-summary">
        <div data-testid="cart-subtotal">Subtotal: {formatCOP(subtotal)}</div>
        <div data-testid="cart-iva">IVA (19%): {formatCOP(iva)}</div>
        <div data-testid="cart-shipping">Shipping: {formatCOP(shipping)}</div>
        <div data-testid="cart-total">Total: {formatCOP(total)}</div>
      </div>
      <button data-testid="proceed-to-checkout" onClick={goToCheckout}>
        Proceed to Checkout
      </button>
    </div>
  );
}
```

### Owner
**Responsible**: react-specialist-ai
**Estimated Effort**: 4-6 hours
**Affected Files**: ~25 React components

### Action Items
- [ ] Add data-testid to all marketplace components
- [ ] Add data-testid to all cart components
- [ ] Add data-testid to all checkout components
- [ ] Add data-testid to all payment components
- [ ] Add data-testid to all form elements and error messages
- [ ] Update component documentation with testing guidelines
- [ ] Re-run E2E test suite to verify

---

## 🟠 BUG #2: Network Idle Timeout on Marketplace Page

**Severity**: High
**Priority**: P1
**Component**: Frontend - Marketplace page
**Impact**: E2E tests timeout after 30 seconds waiting for network idle
**Status**: Open

### Description
Marketplace page has long-running network requests or polling connections that prevent the page from reaching "networkidle" state within the 30-second timeout.

### Error Message
```
TimeoutError: page.waitForLoadState: Timeout 30000ms exceeded.
Location: cart-calculations.spec.ts:18:16

await page.goto('/marketplace');
await page.waitForLoadState('networkidle');
                ^
```

### Reproduction Steps
1. Navigate to http://192.168.1.137:5173/marketplace
2. Open browser DevTools Network tab
3. Observe network requests continue indefinitely
4. Page never reaches "idle" state

### Possible Causes
- Analytics tracking (Google Analytics, Facebook Pixel, etc.)
- Polling for product updates or inventory
- WebSocket connections for real-time updates
- Third-party scripts (Wompi, payment providers)
- Image lazy loading that never completes
- Infinite scroll or pagination loading

### Impact on Testing
- E2E tests cannot proceed past marketplace page load
- All checkout flow tests blocked
- Test execution time unnecessarily extended

### Recommended Fix

#### Option 1: Use Specific Element Selectors (Recommended)
```typescript
// Before (unreliable)
await page.goto('/marketplace');
await page.waitForLoadState('networkidle');

// After (reliable)
await page.goto('/marketplace');
await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });
```

#### Option 2: Increase Timeout
```typescript
await page.waitForLoadState('networkidle', { timeout: 60000 });
```

#### Option 3: Use domcontentloaded
```typescript
await page.goto('/marketplace', { waitUntil: 'domcontentloaded' });
await page.waitForSelector('[data-testid="product-grid"]');
```

#### Option 4: Audit and Optimize Network Requests
```bash
# Identify long-running requests
# Use browser DevTools or Lighthouse audit
# Defer or cancel non-critical requests
```

### Owner
**Responsible**: frontend-performance-ai
**Estimated Effort**: 2-3 hours
**Affected Tests**: All E2E tests

### Action Items
- [ ] Audit network requests on marketplace page
- [ ] Identify polling/long-running connections
- [ ] Implement request cancellation on page navigation
- [ ] Update E2E tests to use element selectors instead of networkidle
- [ ] Document network optimization in performance guide

---

## 🟡 BUG #3: Wompi Public Key Not Configured for Testing

**Severity**: Medium
**Priority**: P2
**Component**: Backend - Payment configuration
**Impact**: Cannot test actual payment flow in E2E environment
**Status**: Open

### Description
Wompi integration is implemented in code but public key for sandbox/test environment is not configured, preventing E2E testing of payment flow.

### Current State
```typescript
// WompiCheckout.tsx - Component exists
const WompiCheckout: React.FC<WompiCheckoutProps> = ({
  publicKey,  // ❌ No default/test value provided
  ...
}) => {
  if (!publicKey) {
    setError('Wompi public key not configured');
    return;
  }
}
```

### Missing Configuration
```bash
# .env or environment configuration
VITE_WOMPI_PUBLIC_KEY=pub_test_xxxxxxxxxxxxx  # ❌ Not set
VITE_WOMPI_ENVIRONMENT=sandbox                # ❌ Not set
```

### Impact
- Cannot test credit card payment flow
- Cannot test PSE bank transfer flow
- Cannot verify Wompi widget initialization
- Cannot test payment success/failure scenarios
- Cannot verify webhook integration

### Recommended Fix

#### Step 1: Obtain Wompi Test Keys
```bash
# Register for Wompi sandbox account
# Get test public key from Wompi dashboard
# Example: pub_test_xYz9K3mN7pQrStUvWx2aBcDe
```

#### Step 2: Configure Environment
```bash
# frontend/.env.development
VITE_WOMPI_PUBLIC_KEY=pub_test_xYz9K3mN7pQrStUvWx2aBcDe
VITE_WOMPI_ENVIRONMENT=sandbox
VITE_WOMPI_CURRENCY=COP
```

#### Step 3: Update Component
```typescript
// src/config/payment.ts
export const WOMPI_CONFIG = {
  publicKey: import.meta.env.VITE_WOMPI_PUBLIC_KEY,
  environment: import.meta.env.VITE_WOMPI_ENVIRONMENT || 'sandbox',
  currency: import.meta.env.VITE_WOMPI_CURRENCY || 'COP',
  testCards: {
    approved: '4242424242424242',
    declined: '4000000000000002',
    insufficient: '4000000000009995'
  }
};
```

#### Step 4: Document Test Cards
```tsx
// Add to payment page in development mode
{import.meta.env.DEV && (
  <div className="test-cards-info">
    <h4>Test Cards (Sandbox Mode)</h4>
    <ul>
      <li>Approved: 4242 4242 4242 4242</li>
      <li>Declined: 4000 0000 0000 0002</li>
      <li>Expiry: Any future date</li>
      <li>CVV: Any 3 digits</li>
    </ul>
  </div>
)}
```

### Test Data for QA
```
# Wompi Sandbox Test Cards
Approved:      4242 4242 4242 4242
Declined:      4000 0000 0000 0002
Insufficient:  4000 0000 0000 9995

Expiry:        12/25 (any future date)
CVV:           123 (any 3 digits)
Holder Name:   Test Customer
```

### Owner
**Responsible**: payment-systems-ai
**Estimated Effort**: 3-4 hours
**Dependencies**: Wompi account registration

### Action Items
- [ ] Register for Wompi sandbox account
- [ ] Obtain test public key
- [ ] Configure environment variables
- [ ] Add test card documentation to UI (dev mode)
- [ ] Update payment component to use environment config
- [ ] Test payment flow with sandbox credentials
- [ ] Document Wompi integration for QA team

---

## 🔵 BUG #4: Cart Totals Display Missing Clear Labels

**Severity**: Low
**Priority**: P3
**Component**: Frontend - Cart components
**Impact**: User may not understand tax breakdown
**Status**: Open

### Description
Cart summary displays subtotal, IVA, shipping, and total but labels may not be clear enough for users unfamiliar with Colombian tax structure.

### Current Display (Assumed)
```
Subtotal: $50,000
IVA: $9,500
Shipping: $15,000
Total: $74,500
```

### Recommended Display
```
Subtotal: $50,000 COP
IVA (19%): $9,500 COP
Envío: $15,000 COP
━━━━━━━━━━━━━━━━━━━
Total a Pagar: $74,500 COP

ℹ️ Envío gratis en compras superiores a $200,000 COP
```

### Enhancement Suggestions
- Add percentage to IVA label: "IVA (19%)"
- Show currency (COP) on all amounts
- Add free shipping threshold info
- Use visual separator before total
- Bold or enlarge total amount
- Add tooltips explaining IVA and shipping

### Owner
**Responsible**: ux-design-ai
**Estimated Effort**: 1-2 hours

---

## ℹ️ INFO #5: Missing Stock Level Indicators on Product Cards

**Severity**: Info
**Priority**: P4
**Component**: Frontend - Product cards in marketplace
**Impact**: Users cannot see stock availability until clicking product
**Status**: Enhancement

### Description
Product cards in marketplace grid do not show stock level indicators. Users must click into product detail to see if item is in stock.

### Current State
```tsx
<ProductCard>
  <img src={product.image} />
  <h3>{product.name}</h3>
  <p>{formatCOP(product.price)}</p>
  <button>Add to Cart</button>
</ProductCard>
```

### Recommended Enhancement
```tsx
<ProductCard>
  <img src={product.image} />
  {product.stock === 0 && (
    <Badge color="red" data-testid="out-of-stock-badge">
      Agotado
    </Badge>
  )}
  {product.stock > 0 && product.stock < 5 && (
    <Badge color="orange" data-testid="low-stock-badge">
      ¡Últimas {product.stock} unidades!
    </Badge>
  )}
  <h3>{product.name}</h3>
  <p>{formatCOP(product.price)}</p>
  <button disabled={product.stock === 0}>
    {product.stock > 0 ? 'Agregar al Carrito' : 'Sin Stock'}
  </button>
</ProductCard>
```

### Benefits
- Improved user experience
- Reduced clicks to cart
- Urgency for low stock items
- Clear availability indication

### Owner
**Responsible**: react-specialist-ai
**Estimated Effort**: 2-3 hours

---

## ℹ️ INFO #6: No Sandbox Mode Indicator in UI

**Severity**: Info
**Priority**: P4
**Component**: Frontend - Payment page
**Impact**: Users/testers may not realize they're in test environment
**Status**: Enhancement

### Description
When using Wompi sandbox mode, there's no visual indicator in the UI that this is a test environment.

### Recommended Enhancement
```tsx
// Payment page header
{import.meta.env.VITE_WOMPI_ENVIRONMENT === 'sandbox' && (
  <Alert color="warning" data-testid="sandbox-mode-indicator">
    <Info className="w-4 h-4" />
    <strong>Modo de Prueba</strong>
    <p>Estás en el entorno de pruebas. No se procesarán pagos reales.</p>
    <details>
      <summary>Tarjetas de Prueba</summary>
      <ul>
        <li>Aprobada: 4242 4242 4242 4242</li>
        <li>Declinada: 4000 0000 0000 0002</li>
      </ul>
    </details>
  </Alert>
)}
```

### Benefits
- Clear environment indication
- Prevents confusion for QA team
- Easy access to test card numbers
- Compliance with testing best practices

### Owner
**Responsible**: react-specialist-ai
**Estimated Effort**: 1 hour

---

## Summary Statistics

### Bugs by Severity
- 🔴 Critical: 1 (Missing data-testid attributes)
- 🟠 High: 1 (Network idle timeout)
- 🟡 Medium: 1 (Wompi configuration)
- 🔵 Low: 1 (Cart labels)
- ℹ️ Info: 2 (Stock indicators, sandbox mode)

### Total Issues: 6

### Estimated Total Effort: 13-19 hours

### Critical Path to E2E Testing
1. Fix BUG #1 (data-testid attributes) - 4-6 hours - BLOCKING
2. Fix BUG #2 (network idle) - 2-3 hours - BLOCKING
3. Configure BUG #3 (Wompi) - 3-4 hours - HIGH PRIORITY

**Minimum viable fix**: 9-13 hours

---

## Regression Risk Assessment

### High Risk Changes
- Adding data-testid attributes (LOW regression risk - non-breaking)
- Network optimization (MEDIUM risk - may affect analytics)

### Medium Risk Changes
- Wompi configuration (LOW risk - sandbox only)
- Cart label updates (LOW risk - UI text only)

### Low Risk Changes
- Stock indicators (LOW risk - additive only)
- Sandbox mode indicator (LOW risk - dev mode only)

---

## Testing Recommendations

### Before Fix
- [ ] Document current behavior
- [ ] Create screenshots of affected areas
- [ ] Note any workarounds in use

### After Fix
- [ ] Re-run complete E2E test suite
- [ ] Verify all data-testid attributes present
- [ ] Test payment flow with Wompi sandbox
- [ ] Validate cart calculations accuracy
- [ ] Confirm stock validation working

### Acceptance Criteria
- [ ] All 60 E2E tests pass successfully
- [ ] Test execution time < 5 minutes
- [ ] No flaky tests (95%+ pass rate)
- [ ] Payment flow completes in sandbox mode
- [ ] Screenshots captured for all test scenarios

---

**Report Generated**: 2025-10-01
**Reporter**: e2e-testing-ai
**Total Issues**: 6 (1 Critical, 1 High, 1 Medium, 1 Low, 2 Info)
**Blocking Issues**: 2 (BUG #1, BUG #2)
**Estimated Fix Time**: 9-13 hours for critical path
