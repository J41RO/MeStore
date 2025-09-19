/**
 * Centralized Store Exports for MeStore Frontend
 * Type-safe Zustand stores with consistent EntityId types
 */

// ========================================
// AUTHENTICATION STORE
// ========================================
export {
  useAuthStore,
  authSelectors,
  useUser,
  useIsAuthenticated,
  useIsAdmin,
  useIsVendor,
  useAuthLoading,
  useAuthError,
} from './authStore.new';

export type {
  ExtendedAuthState,
  ExtendedAuthActions,
  ExtendedAuthStore,
} from './authStore.new';

// ========================================
// PRODUCT STORE
// ========================================
export {
  useProductStore,
  productSelectors,
  useProducts,
  useProduct,
  useProductsLoading,
  useSelectedProducts,
  useProductsPagination,
} from './productStore.new';

export type {
  ExtendedProductState,
  ExtendedProductActions,
  ExtendedProductStore,
} from './productStore.new';

// ========================================
// ORDER STORE
// ========================================
export {
  useOrderStore,
  orderSelectors,
  useOrders,
  useOrder,
  useOrdersLoading,
  useSelectedOrders,
  useOrdersForContext,
  useOrdersPagination,
} from './orderStore.new';

export type {
  ExtendedOrderState,
  ExtendedOrderActions,
  ExtendedOrderStore,
} from './orderStore.new';

// ========================================
// LEGACY STORE EXPORTS (for backward compatibility)
// ========================================

// Note: These are the existing stores that can be gradually migrated
export { useAppStore, appSelectors } from './appStore';
export { useCategoryStore, categorySelectors } from './categoryStore';
export { useSearchStore, useSearch, searchSelectors } from './searchStore';

// ========================================
// STORE COMBINATIONS AND UTILITIES
// ========================================

/**
 * Combined store hook for admin dashboard
 */
export const useAdminStores = () => ({
  auth: useAuthStore(),
  products: useProductStore(),
  orders: useOrderStore(),
});

/**
 * Combined store hook for vendor dashboard
 */
export const useVendorStores = () => ({
  auth: useAuthStore(),
  products: useProductStore(),
  orders: useOrderStore(),
});

/**
 * Combined store hook for buyer experience
 */
export const useBuyerStores = () => ({
  auth: useAuthStore(),
  products: useProductStore(),
  orders: useOrderStore(),
});

/**
 * Global store reset utility
 */
export const resetAllStores = () => {
  useAuthStore.getState().clearAuth();
  useProductStore.getState().reset();
  useOrderStore.getState().reset();
};

/**
 * Global error clearing utility
 */
export const clearAllErrors = () => {
  useAuthStore.getState().clearError();
  useProductStore.getState().clearErrors();
  useOrderStore.getState().clearErrors();
};

// ========================================
// STORE PERSISTENCE UTILITIES
// ========================================

/**
 * Clear all persisted store data
 */
export const clearPersistedData = () => {
  localStorage.removeItem('auth-store');
  sessionStorage.removeItem('product-store');
  sessionStorage.removeItem('order-store');
};

/**
 * Initialize stores with user context
 */
export const initializeStoresForUser = (userId: string, userType: 'admin' | 'vendor' | 'buyer') => {
  const authStore = useAuthStore.getState();
  const productStore = useProductStore.getState();
  const orderStore = useOrderStore.getState();

  // Set contexts based on user type
  switch (userType) {
    case 'admin':
      orderStore.setContext('admin');
      break;
    case 'vendor':
      orderStore.setContext('vendor', userId);
      break;
    case 'buyer':
      orderStore.setContext('buyer', userId);
      break;
  }

  // Initialize with cached data if available
  if (authStore.isAuthenticated) {
    productStore.fetchProducts();
    orderStore.fetchOrders();
  }
};

// ========================================
// TYPE EXPORTS
// ========================================

export type {
  // Core types from stores
  EntityId,
  LoadingState,
  AsyncState,
  EntityCollection,
} from '../types';

// ========================================
// STORE CONFIGURATION
// ========================================

/**
 * Store configuration for development
 */
export const storeConfig = {
  // Cache durations
  productCacheExpiry: 5 * 60 * 1000, // 5 minutes
  orderCacheExpiry: 3 * 60 * 1000,   // 3 minutes
  authSessionExpiry: 24 * 60 * 60 * 1000, // 24 hours

  // Pagination defaults
  defaultPageSize: 20,
  maxPageSize: 100,

  // Development helpers
  enableDevTools: import.meta.env.MODE === 'development',
  enableLogging: import.meta.env.MODE === 'development',
};

/**
 * Store debugging utilities (development only)
 */
if (import.meta.env.MODE === 'development') {
  // @ts-ignore
  window.__STORE_DEBUG__ = {
    auth: useAuthStore,
    products: useProductStore,
    orders: useOrderStore,
    resetAll: resetAllStores,
    clearErrors: clearAllErrors,
    clearPersisted: clearPersistedData,
  };
}

// ========================================
// EXPORT DEFAULT
// ========================================

export default {
  useAuthStore,
  useProductStore,
  useOrderStore,
  resetAllStores,
  clearAllErrors,
  clearPersistedData,
  initializeStoresForUser,
  storeConfig,
};