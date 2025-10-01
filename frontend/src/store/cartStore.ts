/**
 * Cart Store - Backwards Compatibility Layer
 * MeStore Marketplace - Colombian E-commerce
 *
 * This file provides backwards compatibility by re-exporting from the unified checkoutStore.
 * All cart functionality has been merged into checkoutStore for a single source of truth.
 *
 * @deprecated This file exists for backwards compatibility only.
 * New code should import directly from '../stores/checkoutStore'
 */

// Re-export the unified store as useCartStore
export {
  useCheckoutStore as useCartStore,
  formatCOP,
  hasFreeShipping,
  amountNeededForFreeShipping
} from '../stores/checkoutStore';

// Re-export types
export type {
  CartItem,
  CheckoutState as CartStore,
  ShippingAddress,
  PaymentInfo
} from '../stores/checkoutStore';

/**
 * Migration Note:
 * If you're seeing this file in your imports, consider migrating to:
 *
 * Old:
 * import { useCartStore } from '../store/cartStore';
 *
 * New:
 * import { useCheckoutStore as useCartStore } from '../stores/checkoutStore';
 * // or simply
 * import { useCheckoutStore } from '../stores/checkoutStore';
 *
 * All features from the old cartStore have been preserved:
 * - Colombian IVA calculation (19%)
 * - Free shipping logic ($200,000 COP threshold)
 * - COP currency formatting
 * - Drawer state management
 * - Stock validation
 *
 * Plus additional features from checkoutStore:
 * - Checkout flow management
 * - Shipping address management
 * - Payment information handling
 * - Order management
 * - Error handling
 */
