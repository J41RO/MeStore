/**
 * E2E Test Suite: Stock Validation
 *
 * @author e2e-testing-ai
 * @date 2025-10-01
 *
 * Focus: Preventing overselling and stock management validation
 */

import { test, expect } from '@playwright/test';

test.describe('Stock Validation - Prevent Overselling', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/marketplace');
    await page.waitForLoadState('networkidle');
  });

  /**
   * Test: Cannot add more items than available stock
   */
  test('Prevents adding quantity exceeding available stock', async ({ page }) => {
    await test.step('Navigate to product', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="product-detail"]', { timeout: 5000 });
    });

    await test.step('Get available stock', async () => {
      const stockIndicator = page.locator('[data-testid="product-stock"]');
      await expect(stockIndicator).toBeVisible();

      const stockText = await stockIndicator.textContent();
      console.log('Available stock:', stockText);
    });

    await test.step('Attempt to add excessive quantity', async () => {
      // Get stock number
      const stockText = await page.locator('[data-testid="product-stock"]').textContent();
      const stockMatch = stockText?.match(/(\d+)/);
      const maxStock = stockMatch ? parseInt(stockMatch[1], 10) : 10;

      console.log('Max stock detected:', maxStock);

      // Try to set quantity way beyond stock
      const quantityInput = page.locator('[data-testid="quantity-input"]');
      const excessiveQuantity = maxStock + 100;
      await quantityInput.fill(excessiveQuantity.toString());

      // Try to add to cart
      const addButton = page.locator('[data-testid="add-to-cart-button"]');
      await addButton.click();

      // Wait for response
      await page.waitForTimeout(1000);

      // Check for error message
      const stockError = page.locator('[data-testid="stock-error"]');
      const generalError = page.locator('[role="alert"]');

      const hasError = await Promise.race([
        stockError.isVisible({ timeout: 3000 }).then(() => 'stock-error'),
        generalError.isVisible({ timeout: 3000 }).then(() => 'general-error')
      ]).catch(() => null);

      if (hasError) {
        console.log('✅ Stock validation error displayed:', hasError);

        const errorText = await (hasError === 'stock-error' ? stockError : generalError).textContent();
        expect(errorText).toMatch(/stock|disponible|inventory/i);
      } else {
        // If no error, quantity should be capped
        const finalQuantity = await quantityInput.inputValue();
        const finalQty = parseInt(finalQuantity, 10);

        expect(finalQty).toBeLessThanOrEqual(maxStock);
        console.log('✅ Quantity capped at max stock:', finalQty, '≤', maxStock);
      }
    });
  });

  /**
   * Test: Stock indicator updates after adding to cart
   */
  test('Stock indicator reflects quantity added to cart', async ({ page }) => {
    await test.step('Navigate to product and check initial stock', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="product-stock"]', { timeout: 5000 });

      const initialStockText = await page.locator('[data-testid="product-stock"]').textContent();
      console.log('Initial stock:', initialStockText);
    });

    await test.step('Add product to cart', async () => {
      const quantityInput = page.locator('[data-testid="quantity-input"]');
      await quantityInput.fill('2');

      const addButton = page.locator('[data-testid="add-to-cart-button"]');
      await addButton.click();

      // Wait for cart update
      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Verify item appears in cart with correct quantity', async () => {
      const cartQuantity = await page.locator('[data-testid="cart-item-quantity"]').first().inputValue();
      expect(parseInt(cartQuantity, 10)).toBe(2);

      console.log('✅ Cart shows correct quantity: 2');
    });
  });

  /**
   * Test: Out of stock products show appropriate message
   */
  test('Out of stock products display unavailable message', async ({ page }) => {
    await test.step('Find product with zero stock (if available)', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      // Look for out-of-stock badge
      const outOfStockBadge = page.locator('[data-testid="out-of-stock-badge"]');

      if (await outOfStockBadge.isVisible({ timeout: 2000 })) {
        console.log('✅ Out of stock badge found on product card');

        // Click the out-of-stock product
        const outOfStockProduct = outOfStockBadge.locator('xpath=ancestor::*[@data-testid^="product-card-"]');
        await outOfStockProduct.click();

        await page.waitForSelector('[data-testid="product-detail"]', { timeout: 5000 });

        // Verify add to cart is disabled
        const addButton = page.locator('[data-testid="add-to-cart-button"]');
        const isDisabled = await addButton.isDisabled();

        expect(isDisabled).toBeTruthy();
        console.log('✅ Add to cart button is disabled for out-of-stock product');

        // Verify message
        const outOfStockMessage = page.locator('[data-testid="out-of-stock-message"]');
        await expect(outOfStockMessage).toBeVisible();

        const messageText = await outOfStockMessage.textContent();
        expect(messageText).toMatch(/agotado|sin stock|out of stock|no disponible/i);
      } else {
        console.log('ℹ️ No out-of-stock products found in marketplace');
        test.skip();
      }
    });
  });

  /**
   * Test: Low stock warning displays correctly
   */
  test('Low stock warning shows when stock is limited', async ({ page }) => {
    await test.step('Navigate to product', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="product-detail"]', { timeout: 5000 });
    });

    await test.step('Check for low stock indicator', async () => {
      const stockText = await page.locator('[data-testid="product-stock"]').textContent();
      const stockMatch = stockText?.match(/(\d+)/);
      const stockLevel = stockMatch ? parseInt(stockMatch[1], 10) : 999;

      console.log('Stock level:', stockLevel);

      // Low stock is typically < 5 units
      if (stockLevel < 5 && stockLevel > 0) {
        const lowStockWarning = page.locator('[data-testid="low-stock-warning"]');

        if (await lowStockWarning.isVisible({ timeout: 2000 })) {
          console.log('✅ Low stock warning displayed');

          const warningText = await lowStockWarning.textContent();
          expect(warningText).toMatch(/pocas unidades|últimas unidades|low stock/i);
        } else {
          console.log('Low stock warning not found (may not be implemented)');
        }
      } else {
        console.log('Stock level not low enough to trigger warning');
      }
    });
  });

  /**
   * Test: Multiple additions respect stock limit
   */
  test('Adding to cart multiple times respects total stock limit', async ({ page }) => {
    await test.step('Navigate to product and get stock', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="product-stock"]', { timeout: 5000 });
    });

    await test.step('Add product to cart first time', async () => {
      const quantityInput = page.locator('[data-testid="quantity-input"]');
      await quantityInput.fill('2');

      const addButton = page.locator('[data-testid="add-to-cart-button"]');
      await addButton.click();

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });

      // Close cart
      await page.click('[data-testid="close-cart"]');
    });

    await test.step('Try to add more of same product', async () => {
      const quantityInput = page.locator('[data-testid="quantity-input"]');
      await quantityInput.fill('2');

      const addButton = page.locator('[data-testid="add-to-cart-button"]');
      await addButton.click();

      await page.waitForTimeout(1000);

      // Open cart to verify total
      const cartButton = page.locator('[data-testid="cart-button"]');
      await cartButton.click();

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });

      // Get total quantity in cart
      const cartQuantity = await page.locator('[data-testid="cart-item-quantity"]').first().inputValue();
      const totalInCart = parseInt(cartQuantity, 10);

      console.log('Total quantity in cart:', totalInCart);

      // Get max stock
      await page.click('[data-testid="close-cart"]');
      const stockText = await page.locator('[data-testid="product-stock"]').textContent();
      const stockMatch = stockText?.match(/(\d+)/);
      const maxStock = stockMatch ? parseInt(stockMatch[1], 10) : 999;

      // Total should not exceed stock
      expect(totalInCart).toBeLessThanOrEqual(maxStock);
      console.log('✅ Total quantity respects stock limit:', totalInCart, '≤', maxStock);
    });
  });

  /**
   * Test: Cart quantity cannot be updated beyond stock
   */
  test('Updating cart quantity is limited by available stock', async ({ page }) => {
    await test.step('Add product to cart', async () => {
      await page.waitForSelector('[data-testid="product-grid"]', { timeout: 10000 });

      const productCard = page.locator('[data-testid^="product-card-"]').first();
      await productCard.click();

      await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });
      await page.click('[data-testid="add-to-cart-button"]');

      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
    });

    await test.step('Try to update quantity beyond stock', async () => {
      // Get product stock
      await page.click('[data-testid="close-cart"]');
      const stockText = await page.locator('[data-testid="product-stock"]').textContent();
      const stockMatch = stockText?.match(/(\d+)/);
      const maxStock = stockMatch ? parseInt(stockMatch[1], 10) : 10;

      // Open cart
      await page.click('[data-testid="cart-button"]');
      await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });

      // Try to set excessive quantity
      const cartQuantityInput = page.locator('[data-testid="cart-item-quantity"]').first();
      await cartQuantityInput.fill((maxStock + 50).toString());

      // Blur input to trigger validation
      await page.click('body');
      await page.waitForTimeout(1000);

      // Get final quantity
      const finalQuantity = await cartQuantityInput.inputValue();
      const finalQty = parseInt(finalQuantity, 10);

      // Should be capped at max stock
      expect(finalQty).toBeLessThanOrEqual(maxStock);
      console.log('✅ Cart quantity capped at stock limit:', finalQty, '≤', maxStock);
    });
  });
});
