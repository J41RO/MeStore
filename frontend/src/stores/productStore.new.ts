/**
 * Product Store for MeStore Frontend
 * Type-safe Zustand store with consistent EntityId types
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { productApiService } from '../services/productApiService';
import type {
  EntityId,
  Product,
  CreateProductRequest,
  UpdateProductRequest,
  ProductSearchRequest,
  ProductFilters,
  ProductSort,
  ProductState,
  ProductActions,
  ProductStore,
  EntityCollection,
  LoadingState,
} from '../types';

// ========================================
// EXTENDED PRODUCT STATE
// ========================================

/**
 * Extended product state with UI-specific fields
 */
interface ExtendedProductState extends ProductState {
  // Cache management
  lastFetch: string | null;
  cacheExpiry: number; // Cache duration in milliseconds

  // UI state
  selectedProductIds: EntityId[];
  showBulkActions: boolean;
  showFiltersPanel: boolean;

  // Form state
  isUploading: boolean;
  uploadProgress: number;

  // Pagination
  currentPage: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

/**
 * Extended product actions with additional functionality
 */
interface ExtendedProductActions extends ProductActions {
  // Cache management
  invalidateCache: () => void;
  isCacheValid: () => boolean;
  setCacheExpiry: (duration: number) => void;

  // Selection management
  selectProducts: (ids: EntityId[]) => void;
  selectAllProducts: () => void;
  clearSelection: () => void;
  toggleProductSelection: (id: EntityId) => void;
  getSelectedProducts: () => Product[];

  // Bulk operations
  bulkUpdateProducts: (updates: Partial<UpdateProductRequest>) => Promise<boolean>;
  bulkDeleteProducts: () => Promise<boolean>;
  bulkToggleActive: () => Promise<boolean>;
  bulkToggleFeatured: () => Promise<boolean>;

  // UI management
  toggleFiltersPanel: () => void;
  toggleBulkActions: () => void;

  // Upload management
  setUploadProgress: (progress: number) => void;
  resetUpload: () => void;

  // Pagination
  goToPage: (page: number) => Promise<void>;
  goToNextPage: () => Promise<void>;
  goToPreviousPage: () => Promise<void>;
}

/**
 * Complete extended product store
 */
type ExtendedProductStore = ExtendedProductState & ExtendedProductActions;

// ========================================
// STORE IMPLEMENTATION
// ========================================

/**
 * Type-safe product store with EntityId consistency
 */
export const useProductStore = create<ExtendedProductStore>()(
  persist(
    immer((set, get) => ({
      // ========================================
      // STATE
      // ========================================

      // Core product state (from ProductState)
      data: {
        byId: {},
        allIds: [],
        total: 0,
      },
      loading: false,
      error: null,
      lastFetch: null,

      selectedProduct: null,
      filters: {},
      sort: {
        field: 'created_at',
        direction: 'desc',
      },
      searchQuery: '',
      viewMode: 'grid',
      showFilters: false,

      isCreating: false,
      isUpdating: false,
      createError: null,
      updateError: null,

      // Extended state
      cacheExpiry: 5 * 60 * 1000, // 5 minutes default
      selectedProductIds: [],
      showBulkActions: false,
      showFiltersPanel: false,
      isUploading: false,
      uploadProgress: 0,
      currentPage: 1,
      totalPages: 1,
      hasNextPage: false,
      hasPreviousPage: false,

      // ========================================
      // FETCH OPERATIONS
      // ========================================

      /**
       * Fetch products with caching support
       */
      fetchProducts: async (params?: ProductSearchRequest): Promise<void> => {
        // Check cache validity
        const { isCacheValid } = get();
        if (isCacheValid() && !params && Object.keys(get().filters).length === 0) {
          return; // Use cached data
        }

        set((state) => {
          state.loading = true;
          state.error = null;
        });

        try {
          const searchParams: ProductSearchRequest = {
            ...params,
            ...get().filters,
            sort_by: get().sort.field,
            sort_order: get().sort.direction,
            page: params?.page || get().currentPage,
            limit: params?.limit || 20,
          };

          if (get().searchQuery) {
            searchParams.query = get().searchQuery;
          }

          const response = await productApiService.getProducts(searchParams);

          set((state) => {
            // Update products collection
            const byId: Record<EntityId, Product> = {};
            const allIds: EntityId[] = [];

            response.data.forEach((product) => {
              byId[product.id] = product;
              allIds.push(product.id);
            });

            state.data = { byId, allIds, total: response.pagination?.total || 0 };
            state.loading = false;
            state.lastFetch = new Date().toISOString();

            // Update pagination
            if (response.pagination) {
              state.currentPage = response.pagination.page;
              state.totalPages = response.pagination.totalPages;
              state.hasNextPage = response.pagination.hasNext;
              state.hasPreviousPage = response.pagination.hasPrevious;
            }
          });
        } catch (error: any) {
          set((state) => {
            state.loading = false;
            state.error = error.message || 'Failed to fetch products';
          });
        }
      },

      /**
       * Fetch single product by ID
       */
      fetchProduct: async (id: EntityId): Promise<Product | null> => {
        try {
          const product = await productApiService.getProduct(id);

          set((state) => {
            // Add to collection
            state.data.byId[id] = product;
            if (!state.data.allIds.includes(id)) {
              state.data.allIds.push(id);
            }
          });

          return product;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to fetch product';
          });
          return null;
        }
      },

      // ========================================
      // CRUD OPERATIONS
      // ========================================

      /**
       * Create new product
       */
      createProduct: async (data: CreateProductRequest): Promise<Product | null> => {
        set((state) => {
          state.isCreating = true;
          state.createError = null;
        });

        try {
          const product = await productApiService.createProduct(data);

          set((state) => {
            // Add to collection
            state.data.byId[product.id] = product;
            state.data.allIds.unshift(product.id);
            state.data.total += 1;
            state.isCreating = false;
          });

          return product;
        } catch (error: any) {
          set((state) => {
            state.isCreating = false;
            state.createError = error.message || 'Failed to create product';
          });
          return null;
        }
      },

      /**
       * Update existing product
       */
      updateProduct: async (id: EntityId, data: UpdateProductRequest): Promise<Product | null> => {
        set((state) => {
          state.isUpdating = true;
          state.updateError = null;
        });

        try {
          const product = await productApiService.updateProduct(id, data);

          set((state) => {
            // Update in collection
            state.data.byId[id] = product;
            state.isUpdating = false;

            // Update selected product if it's the one being updated
            if (state.selectedProduct?.id === id) {
              state.selectedProduct = product;
            }
          });

          return product;
        } catch (error: any) {
          set((state) => {
            state.isUpdating = false;
            state.updateError = error.message || 'Failed to update product';
          });
          return null;
        }
      },

      /**
       * Delete product
       */
      deleteProduct: async (id: EntityId): Promise<boolean> => {
        try {
          await productApiService.deleteProduct(id);

          set((state) => {
            // Remove from collection
            delete state.data.byId[id];
            state.data.allIds = state.data.allIds.filter(productId => productId !== id);
            state.data.total -= 1;

            // Clear selection if deleted product was selected
            if (state.selectedProduct?.id === id) {
              state.selectedProduct = null;
            }

            // Remove from selected IDs
            state.selectedProductIds = state.selectedProductIds.filter(productId => productId !== id);
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to delete product';
          });
          return false;
        }
      },

      // ========================================
      // SELECTION AND UI
      // ========================================

      /**
       * Select product for details/editing
       */
      selectProduct: (product: Product | null): void => {
        set((state) => {
          state.selectedProduct = product;
        });
      },

      /**
       * Set filters
       */
      setFilters: (filters: Partial<ProductFilters>): void => {
        set((state) => {
          state.filters = { ...state.filters, ...filters };
          state.currentPage = 1; // Reset to first page
        });

        // Trigger fetch with new filters
        get().fetchProducts();
      },

      /**
       * Set sort configuration
       */
      setSort: (sort: ProductSort): void => {
        set((state) => {
          state.sort = sort;
          state.currentPage = 1; // Reset to first page
        });

        // Trigger fetch with new sort
        get().fetchProducts();
      },

      /**
       * Set search query
       */
      setSearchQuery: (query: string): void => {
        set((state) => {
          state.searchQuery = query;
          state.currentPage = 1; // Reset to first page
        });

        // Trigger fetch with new search
        get().fetchProducts();
      },

      /**
       * Set view mode
       */
      setViewMode: (mode: 'grid' | 'list'): void => {
        set((state) => {
          state.viewMode = mode;
        });
      },

      /**
       * Toggle filters panel
       */
      toggleFilters: (): void => {
        set((state) => {
          state.showFilters = !state.showFilters;
        });
      },

      // ========================================
      // STATE MANAGEMENT
      // ========================================

      /**
       * Clear products collection
       */
      clearProducts: (): void => {
        set((state) => {
          state.data = { byId: {}, allIds: [], total: 0 };
          state.selectedProduct = null;
          state.selectedProductIds = [];
          state.lastFetch = null;
        });
      },

      /**
       * Clear errors
       */
      clearErrors: (): void => {
        set((state) => {
          state.error = null;
          state.createError = null;
          state.updateError = null;
        });
      },

      /**
       * Reset store to initial state
       */
      reset: (): void => {
        set((state) => {
          state.data = { byId: {}, allIds: [], total: 0 };
          state.loading = false;
          state.error = null;
          state.lastFetch = null;
          state.selectedProduct = null;
          state.filters = {};
          state.sort = { field: 'created_at', direction: 'desc' };
          state.searchQuery = '';
          state.viewMode = 'grid';
          state.showFilters = false;
          state.isCreating = false;
          state.isUpdating = false;
          state.createError = null;
          state.updateError = null;
          state.selectedProductIds = [];
          state.showBulkActions = false;
          state.showFiltersPanel = false;
          state.currentPage = 1;
          state.totalPages = 1;
          state.hasNextPage = false;
          state.hasPreviousPage = false;
        });
      },

      // ========================================
      // EXTENDED ACTIONS
      // ========================================

      /**
       * Invalidate cache
       */
      invalidateCache: (): void => {
        set((state) => {
          state.lastFetch = null;
        });
      },

      /**
       * Check if cache is valid
       */
      isCacheValid: (): boolean => {
        const { lastFetch, cacheExpiry } = get();
        if (!lastFetch) return false;

        const lastFetchTime = new Date(lastFetch).getTime();
        const now = Date.now();
        return (now - lastFetchTime) < cacheExpiry;
      },

      /**
       * Set cache expiry duration
       */
      setCacheExpiry: (duration: number): void => {
        set((state) => {
          state.cacheExpiry = duration;
        });
      },

      /**
       * Select multiple products
       */
      selectProducts: (ids: EntityId[]): void => {
        set((state) => {
          state.selectedProductIds = ids;
          state.showBulkActions = ids.length > 0;
        });
      },

      /**
       * Select all products
       */
      selectAllProducts: (): void => {
        set((state) => {
          state.selectedProductIds = [...state.data.allIds];
          state.showBulkActions = state.data.allIds.length > 0;
        });
      },

      /**
       * Clear selection
       */
      clearSelection: (): void => {
        set((state) => {
          state.selectedProductIds = [];
          state.showBulkActions = false;
        });
      },

      /**
       * Toggle product selection
       */
      toggleProductSelection: (id: EntityId): void => {
        set((state) => {
          const isSelected = state.selectedProductIds.includes(id);
          if (isSelected) {
            state.selectedProductIds = state.selectedProductIds.filter(productId => productId !== id);
          } else {
            state.selectedProductIds.push(id);
          }
          state.showBulkActions = state.selectedProductIds.length > 0;
        });
      },

      /**
       * Get selected products
       */
      getSelectedProducts: (): Product[] => {
        const { selectedProductIds, data } = get();
        return selectedProductIds.map(id => data.byId[id]).filter(Boolean);
      },

      /**
       * Bulk update products
       */
      bulkUpdateProducts: async (updates: Partial<UpdateProductRequest>): Promise<boolean> => {
        const { selectedProductIds } = get();
        if (selectedProductIds.length === 0) return false;

        try {
          const updatePromises = selectedProductIds.map(id =>
            productApiService.updateProduct(id, { id, ...updates })
          );

          const updatedProducts = await Promise.all(updatePromises);

          set((state) => {
            updatedProducts.forEach(product => {
              state.data.byId[product.id] = product;
            });
            state.selectedProductIds = [];
            state.showBulkActions = false;
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Bulk update failed';
          });
          return false;
        }
      },

      /**
       * Bulk delete products
       */
      bulkDeleteProducts: async (): Promise<boolean> => {
        const { selectedProductIds } = get();
        if (selectedProductIds.length === 0) return false;

        try {
          await productApiService.bulkDeleteProducts(selectedProductIds);

          set((state) => {
            selectedProductIds.forEach(id => {
              delete state.data.byId[id];
              state.data.allIds = state.data.allIds.filter(productId => productId !== id);
            });
            state.data.total -= selectedProductIds.length;
            state.selectedProductIds = [];
            state.showBulkActions = false;
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Bulk delete failed';
          });
          return false;
        }
      },

      /**
       * Bulk toggle active status
       */
      bulkToggleActive: async (): Promise<boolean> => {
        return get().bulkUpdateProducts({ is_active: true });
      },

      /**
       * Bulk toggle featured status
       */
      bulkToggleFeatured: async (): Promise<boolean> => {
        return get().bulkUpdateProducts({ is_featured: true });
      },

      /**
       * Toggle filters panel
       */
      toggleFiltersPanel: (): void => {
        set((state) => {
          state.showFiltersPanel = !state.showFiltersPanel;
        });
      },

      /**
       * Toggle bulk actions
       */
      toggleBulkActions: (): void => {
        set((state) => {
          state.showBulkActions = !state.showBulkActions;
          if (!state.showBulkActions) {
            state.selectedProductIds = [];
          }
        });
      },

      /**
       * Set upload progress
       */
      setUploadProgress: (progress: number): void => {
        set((state) => {
          state.uploadProgress = progress;
          state.isUploading = progress < 100;
        });
      },

      /**
       * Reset upload state
       */
      resetUpload: (): void => {
        set((state) => {
          state.isUploading = false;
          state.uploadProgress = 0;
        });
      },

      /**
       * Go to specific page
       */
      goToPage: async (page: number): Promise<void> => {
        set((state) => {
          state.currentPage = page;
        });
        await get().fetchProducts({ page });
      },

      /**
       * Go to next page
       */
      goToNextPage: async (): Promise<void> => {
        const { currentPage, hasNextPage } = get();
        if (hasNextPage) {
          await get().goToPage(currentPage + 1);
        }
      },

      /**
       * Go to previous page
       */
      goToPreviousPage: async (): Promise<void> => {
        const { currentPage, hasPreviousPage } = get();
        if (hasPreviousPage) {
          await get().goToPage(currentPage - 1);
        }
      },
    })),
    {
      name: 'product-store',
      storage: createJSONStorage(() => sessionStorage), // Use session storage for product cache
      partialize: (state) => ({
        filters: state.filters,
        sort: state.sort,
        viewMode: state.viewMode,
        showFilters: state.showFilters,
        cacheExpiry: state.cacheExpiry,
        // Don't persist data or loading states
      }),
    }
  )
);

// ========================================
// SELECTORS
// ========================================

/**
 * Product store selectors for optimized component subscriptions
 */
export const productSelectors = {
  // Products data
  products: (state: ExtendedProductStore) => state.data.allIds.map(id => state.data.byId[id]),
  productById: (id: EntityId) => (state: ExtendedProductStore) => state.data.byId[id],
  productsCount: (state: ExtendedProductStore) => state.data.total,

  // Loading and error states
  isLoading: (state: ExtendedProductStore) => state.loading,
  error: (state: ExtendedProductStore) => state.error,
  isCreating: (state: ExtendedProductStore) => state.isCreating,
  isUpdating: (state: ExtendedProductStore) => state.isUpdating,

  // Selection
  selectedProduct: (state: ExtendedProductStore) => state.selectedProduct,
  selectedProductIds: (state: ExtendedProductStore) => state.selectedProductIds,
  selectedProducts: (state: ExtendedProductStore) => state.getSelectedProducts(),
  hasSelection: (state: ExtendedProductStore) => state.selectedProductIds.length > 0,

  // UI state
  viewMode: (state: ExtendedProductStore) => state.viewMode,
  showFilters: (state: ExtendedProductStore) => state.showFilters,
  showBulkActions: (state: ExtendedProductStore) => state.showBulkActions,
  uploadProgress: (state: ExtendedProductStore) => state.uploadProgress,
  isUploading: (state: ExtendedProductStore) => state.isUploading,

  // Pagination
  currentPage: (state: ExtendedProductStore) => state.currentPage,
  totalPages: (state: ExtendedProductStore) => state.totalPages,
  hasNextPage: (state: ExtendedProductStore) => state.hasNextPage,
  hasPreviousPage: (state: ExtendedProductStore) => state.hasPreviousPage,

  // Filters and search
  filters: (state: ExtendedProductStore) => state.filters,
  searchQuery: (state: ExtendedProductStore) => state.searchQuery,
  sort: (state: ExtendedProductStore) => state.sort,

  // Cache
  isCacheValid: (state: ExtendedProductStore) => state.isCacheValid(),
  lastFetch: (state: ExtendedProductStore) => state.lastFetch,
};

// ========================================
// HOOKS
// ========================================

/**
 * Hook for products list
 */
export const useProducts = () => useProductStore(productSelectors.products);

/**
 * Hook for single product by ID
 */
export const useProduct = (id: EntityId) => useProductStore(productSelectors.productById(id));

/**
 * Hook for loading state
 */
export const useProductsLoading = () => useProductStore(productSelectors.isLoading);

/**
 * Hook for selected products
 */
export const useSelectedProducts = () => useProductStore(productSelectors.selectedProducts);

/**
 * Hook for pagination
 */
export const useProductsPagination = () => useProductStore((state) => ({
  currentPage: state.currentPage,
  totalPages: state.totalPages,
  hasNextPage: state.hasNextPage,
  hasPreviousPage: state.hasPreviousPage,
  goToPage: state.goToPage,
  goToNextPage: state.goToNextPage,
  goToPreviousPage: state.goToPreviousPage,
}));

// ========================================
// EXPORTS
// ========================================

export type { ExtendedProductState, ExtendedProductActions, ExtendedProductStore };
export default useProductStore;