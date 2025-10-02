/**
 * Cart Helper Functions for E2E Tests
 *
 * @author e2e-testing-ai
 * @date 2025-10-01
 */

import { Page, expect } from '@playwright/test';
import { COLOMBIAN_CONSTANTS } from '../fixtures/test-data';

/**
 * Calculate expected cart totals
 */
export function calculateCartTotals(items: Array<{ price: number; quantity: number }>) {
  const subtotal = items.reduce((total, item) => total + (item.price * item.quantity), 0);
  const iva = subtotal * COLOMBIAN_CONSTANTS.IVA_RATE;
  const shipping = subtotal >= COLOMBIAN_CONSTANTS.FREE_SHIPPING_THRESHOLD
    ? 0
    : COLOMBIAN_CONSTANTS.SHIPPING_COST;
  const total = subtotal + iva + shipping;

  return {
    subtotal,
    iva,
    shipping,
    total
  };
}

/**
 * Format Colombian Pesos
 */
export function formatCOP(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

/**
 * Verify cart totals in UI
 */
export async function verifyCartTotals(
  page: Page,
  expectedTotals: { subtotal: number; iva: number; shipping: number; total: number }
) {
  // Wait for totals to be visible
  await page.waitForSelector('[data-testid="cart-summary"]', { timeout: 5000 });

  // Get displayed values
  const subtotalText = await page.locator('[data-testid="subtotal"]').textContent();
  const ivaText = await page.locator('[data-testid="iva"]').textContent();
  const shippingText = await page.locator('[data-testid="shipping"]').textContent();
  const totalText = await page.locator('[data-testid="total"]').textContent();

  // Extract numbers from currency strings
  const parseAmount = (text: string | null): number => {
    if (!text) return 0;
    return parseInt(text.replace(/[^\d]/g, ''), 10);
  };

  const displayedSubtotal = parseAmount(subtotalText);
  const displayedIVA = parseAmount(ivaText);
  const displayedShipping = parseAmount(shippingText);
  const displayedTotal = parseAmount(totalText);

  // Verify calculations
  expect(displayedSubtotal).toBe(expectedTotals.subtotal);
  expect(displayedIVA).toBe(Math.round(expectedTotals.iva));
  expect(displayedShipping).toBe(expectedTotals.shipping);
  expect(displayedTotal).toBe(Math.round(expectedTotals.total));
}

/**
 * Add product to cart via UI
 */
export async function addToCart(
  page: Page,
  productSelector: string,
  quantity: number = 1
) {
  // Click product card
  await page.click(productSelector);

  // Wait for product detail page
  await page.waitForSelector('[data-testid="add-to-cart-button"]', { timeout: 5000 });

  // Set quantity if different from 1
  if (quantity > 1) {
    const quantityInput = page.locator('[data-testid="quantity-input"]');
    await quantityInput.fill(quantity.toString());
  }

  // Click add to cart
  await page.click('[data-testid="add-to-cart-button"]');

  // Wait for cart drawer to open
  await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
}

/**
 * Open cart drawer
 */
export async function openCartDrawer(page: Page) {
  await page.click('[data-testid="cart-button"]');
  await page.waitForSelector('[data-testid="cart-drawer"]', { state: 'visible', timeout: 5000 });
}

/**
 * Proceed to checkout from cart
 */
export async function proceedToCheckout(page: Page) {
  await page.click('[data-testid="proceed-to-checkout"]');
  await page.waitForURL('**/checkout**', { timeout: 10000 });
}

/**
 * Verify cart item in UI
 */
export async function verifyCartItem(
  page: Page,
  itemName: string,
  quantity: number,
  price: number
) {
  const itemLocator = page.locator(`[data-testid="cart-item-${itemName}"]`);
  await expect(itemLocator).toBeVisible();

  const quantityText = await itemLocator.locator('[data-testid="item-quantity"]').textContent();
  expect(parseInt(quantityText || '0', 10)).toBe(quantity);

  const priceText = await itemLocator.locator('[data-testid="item-price"]').textContent();
  const displayedPrice = parseInt(priceText?.replace(/[^\d]/g, '') || '0', 10);
  expect(displayedPrice).toBe(price);
}

/**
 * Update cart item quantity
 */
export async function updateCartItemQuantity(
  page: Page,
  itemName: string,
  newQuantity: number
) {
  const itemLocator = page.locator(`[data-testid="cart-item-${itemName}"]`);
  const quantityInput = itemLocator.locator('[data-testid="quantity-input"]');

  await quantityInput.fill(newQuantity.toString());
  await page.waitForTimeout(500); // Wait for update to process
}

/**
 * Remove cart item
 */
export async function removeCartItem(page: Page, itemName: string) {
  const itemLocator = page.locator(`[data-testid="cart-item-${itemName}"]`);
  await itemLocator.locator('[data-testid="remove-item"]').click();

  // Wait for item to be removed
  await expect(itemLocator).not.toBeVisible({ timeout: 3000 });
}
