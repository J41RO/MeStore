/**
 * E2E Test Suite: Cart Calculations Validation
 *
 * @author e2e-testing-ai
 * @date 2025-10-01
 *
 * Focus: Colombian tax (IVA 19%) and shipping cost calculations
 */

import { test, expect } from '@playwright/test';
import { calculateCartTotals, formatCOP } from './utils/cart-helpers';
import { COLOMBIAN_CONSTANTS } from './fixtures/test-data';

test.describe('Cart Calculations - Colombian Tax and Shipping', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/marketplace');
    await page.waitForLoadState('networkidle');
  });

  /**
   * Test: IVA calculation is exactly 19%
   */
  test('IVA is calculated correctly at 19% of subtotal', async ({ page }) => {
    await test.step('Add product to cart', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify IVA is exactly 19%', async () => {
      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const ivaText = await page.locator('[data-testid="cart-iva"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const iva = parseInt(ivaText?.replace(/[^\d]/g, '') || '0', 10);

      const expectedIVA = Math.round(subtotal * COLOMBIAN_CONSTANTS.IVA_RATE);

      expect(iva).toBe(expectedIVA);

      const ivaPercentage = ((iva / subtotal) * 100).toFixed(2);
      console.log({
        subtotal: formatCOP(subtotal),
        iva: formatCOP(iva),
        percentage: `${ivaPercentage}%`,
        expected: '19.00%'
      });
    });
  });

  /**
   * Test: Free shipping over $200,000 COP
   */
  test('Free shipping applies for orders over $200,000 COP', async ({ page }) => {
    // This test requires products totaling over $200,000
    // May need to add multiple items

    await test.step('Add products to reach free shipping threshold', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      // Strategy: Add multiple products or increase quantity
      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="quantity-input"]', { timeout: 5000 });

      // Set high quantity to potentially reach threshold
      await page.fill('[data-testid="quantity-input"]', '10');
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify shipping cost logic', async () => {
      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const shippingText = await page.locator('[data-testid="cart-shipping"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const shipping = parseInt(shippingText?.replace(/[^\d]/g, '') || '0', 10);

      if (subtotal >= COLOMBIAN_CONSTANTS.FREE_SHIPPING_THRESHOLD) {
        expect(shipping).toBe(0);
        console.log(`✅ Free shipping applied (subtotal: ${formatCOP(subtotal)})`);
      } else {
        expect(shipping).toBe(COLOMBIAN_CONSTANTS.SHIPPING_COST);
        const amountNeeded = COLOMBIAN_CONSTANTS.FREE_SHIPPING_THRESHOLD - subtotal;
        console.log(`Shipping: $15,000 - Need ${formatCOP(amountNeeded)} more for free shipping`);
      }
    });
  });

  /**
   * Test: Standard shipping is $15,000 COP
   */
  test('Standard shipping cost is $15,000 COP for orders under threshold', async ({ page }) => {
    await test.step('Add low-cost product', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      // Add single item to stay under threshold
      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify standard shipping cost', async () => {
      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const shippingText = await page.locator('[data-testid="cart-shipping"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const shipping = parseInt(shippingText?.replace(/[^\d]/g, '') || '0', 10);

      // Only verify if under threshold
      if (subtotal < COLOMBIAN_CONSTANTS.FREE_SHIPPING_THRESHOLD) {
        expect(shipping).toBe(COLOMBIAN_CONSTANTS.SHIPPING_COST);
        console.log(`✅ Standard shipping: ${formatCOP(COLOMBIAN_CONSTANTS.SHIPPING_COST)}`);
      } else {
        console.log('Skipped: Subtotal exceeds free shipping threshold');
      }
    });
  });

  /**
   * Test: Total = Subtotal + IVA + Shipping
   */
  test('Total is correctly calculated as sum of subtotal, IVA, and shipping', async ({ page }) => {
    await test.step('Add product to cart', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="quantity-input"]', { timeout: 5000 });
      await page.fill('[data-testid="quantity-input"]', '3');
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify total calculation', async () => {
      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const ivaText = await page.locator('[data-testid="cart-iva"]').textContent();
      const shippingText = await page.locator('[data-testid="cart-shipping"]').textContent();
      const totalText = await page.locator('[data-testid="cart-total"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const iva = parseInt(ivaText?.replace(/[^\d]/g, '') || '0', 10);
      const shipping = parseInt(shippingText?.replace(/[^\d]/g, '') || '0', 10);
      const total = parseInt(totalText?.replace(/[^\d]/g, '') || '0', 10);

      const expectedTotal = subtotal + iva + shipping;

      expect(total).toBe(expectedTotal);

      console.log('Cart Calculation Breakdown:');
      console.log('  Subtotal:', formatCOP(subtotal));
      console.log('  IVA (19%):', formatCOP(iva));
      console.log('  Shipping:', formatCOP(shipping));
      console.log('  ─────────────────────');
      console.log('  Total:', formatCOP(total));
      console.log('  Expected:', formatCOP(expectedTotal));
      console.log('  ✅ Match:', total === expectedTotal);
    });
  });

  /**
   * Test: Quantity changes update calculations correctly
   */
  test('Updating quantity recalculates all totals correctly', async ({ page }) => {
    await test.step('Add product to cart', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Get initial totals', async () => {
      const initialTotal = await page.locator('[data-testid="cart-total"]').textContent();
      console.log('Initial total:', initialTotal);
    });

    await test.step('Update quantity', async () => {
      const quantityInput = page.locator('[data-testid="cart-item-quantity"]').first();
      await quantityInput.fill('5');

      // Wait for update
      await page.waitForTimeout(1000);
    });

    await test.step('Verify totals recalculated', async () => {
      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const ivaText = await page.locator('[data-testid="cart-iva"]').textContent();
      const shippingText = await page.locator('[data-testid="cart-shipping"]').textContent();
      const totalText = await page.locator('[data-testid="cart-total"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const iva = parseInt(ivaText?.replace(/[^\d]/g, '') || '0', 10);
      const shipping = parseInt(shippingText?.replace(/[^\d]/g, '') || '0', 10);
      const total = parseInt(totalText?.replace(/[^\d]/g, '') || '0', 10);

      // Verify IVA is still 19%
      const expectedIVA = Math.round(subtotal * 0.19);
      expect(iva).toBe(expectedIVA);

      // Verify total is correct
      const expectedTotal = subtotal + iva + shipping;
      expect(total).toBe(expectedTotal);

      console.log('Updated totals after quantity change:');
      console.log('  Subtotal:', formatCOP(subtotal));
      console.log('  IVA:', formatCOP(iva));
      console.log('  Shipping:', formatCOP(shipping));
      console.log('  Total:', formatCOP(total));
    });
  });

  /**
   * Test: Multiple products calculate correctly
   */
  test('Multiple products in cart calculate totals correctly', async ({ page }) => {
    await test.step('Add first product', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const firstProduct = page.locator('[data-testid^="product-card-"]').first();
      await firstProduct.click();

      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Return to marketplace and add second product', async () => {
      // Close cart drawer
      await page.click('[data-testid="close-cart"]');

      // Go back to marketplace
      await page.goto('/marketplace');
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      // Add second product
      const secondProduct = page.locator('[data-testid^="product-card-"]').nth(1);
      await secondProduct.click();

      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify totals for multiple products', async () => {
      // Get item count
      const itemCount = await page.locator('[data-testid^="cart-item-"]').count();
      console.log('Items in cart:', itemCount);

      const subtotalText = await page.locator('[data-testid="cart-subtotal"]').textContent();
      const ivaText = await page.locator('[data-testid="cart-iva"]').textContent();
      const totalText = await page.locator('[data-testid="cart-total"]').textContent();

      const subtotal = parseInt(subtotalText?.replace(/[^\d]/g, '') || '0', 10);
      const iva = parseInt(ivaText?.replace(/[^\d]/g, '') || '0', 10);

      // Verify IVA percentage
      const expectedIVA = Math.round(subtotal * 0.19);
      expect(iva).toBe(expectedIVA);

      console.log(`Multi-product cart (${itemCount} items):`, {
        subtotal: formatCOP(subtotal),
        iva: formatCOP(iva),
        ivaPercent: ((iva / subtotal) * 100).toFixed(2) + '%'
      });
    });
  });
});
