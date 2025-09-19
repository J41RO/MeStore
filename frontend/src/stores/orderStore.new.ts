/**
 * Order Store for MeStore Frontend
 * Type-safe Zustand store with consistent EntityId types
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { orderApiService } from '../services/orderApiService';
import type {
  EntityId,
  Order,
  CreateOrderRequest,
  UpdateOrderRequest,
  OrderSearchRequest,
  OrderFilters,
  OrderSort,
  OrderState,
  OrderActions,
  OrderStore,
  OrderStatus,
  PaymentStatus,
  EntityCollection,
} from '../types';

// ========================================
// EXTENDED ORDER STATE
// ========================================

/**
 * Extended order state with UI-specific fields
 */
interface ExtendedOrderState extends OrderState {
  // Cache management
  lastFetch: string | null;
  cacheExpiry: number;

  // Multi-selection
  selectedOrderIds: EntityId[];
  showBulkActions: boolean;

  // Context-specific views
  currentContext: 'buyer' | 'vendor' | 'admin';
  currentVendorId?: EntityId;
  currentUserId?: EntityId;

  // Status management
  statusUpdateLoading: Record<EntityId, boolean>;

  // Pagination
  currentPage: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;

  // Analytics cache
  metricsCache: Record<string, any>;
  metricsLastFetch: Record<string, string>;
}

/**
 * Extended order actions with additional functionality
 */
interface ExtendedOrderActions extends OrderActions {
  // Context management
  setContext: (context: 'buyer' | 'vendor' | 'admin', userId?: EntityId) => void;

  // Multi-selection
  selectOrders: (ids: EntityId[]) => void;
  selectAllOrders: () => void;
  clearSelection: () => void;
  toggleOrderSelection: (id: EntityId) => void;
  getSelectedOrders: () => Order[];

  // Bulk operations
  bulkUpdateStatus: (status: OrderStatus) => Promise<boolean>;
  bulkCancel: (reason?: string) => Promise<boolean>;

  // Status-specific actions
  confirmOrders: (ids: EntityId[]) => Promise<boolean>;
  processOrders: (ids: EntityId[]) => Promise<boolean>;
  shipOrders: (ids: EntityId[], trackingNumbers?: Record<EntityId, string>) => Promise<boolean>;
  markDelivered: (ids: EntityId[]) => Promise<boolean>;

  // Vendor-specific actions
  fetchMyVendorOrders: () => Promise<void>;
  acceptOrder: (id: EntityId) => Promise<boolean>;
  rejectOrder: (id: EntityId, reason: string) => Promise<boolean>;

  // Admin-specific actions
  fetchAllOrdersForAdmin: () => Promise<void>;
  adminForceStatus: (id: EntityId, status: OrderStatus, notes?: string) => Promise<boolean>;
  refundOrder: (id: EntityId, reason?: string) => Promise<boolean>;

  // Analytics
  fetchOrderMetrics: (period?: string) => Promise<any>;
  fetchVendorMetrics: (vendorId: EntityId, period?: string) => Promise<any>;

  // Cache management
  invalidateCache: () => void;
  isCacheValid: () => boolean;

  // Pagination
  goToPage: (page: number) => Promise<void>;
  goToNextPage: () => Promise<void>;
  goToPreviousPage: () => Promise<void>;
}

/**
 * Complete extended order store
 */
type ExtendedOrderStore = ExtendedOrderState & ExtendedOrderActions;

// ========================================
// STORE IMPLEMENTATION
// ========================================

/**
 * Type-safe order store with EntityId consistency
 */
export const useOrderStore = create<ExtendedOrderStore>()(
  persist(
    immer((set, get) => ({
      // ========================================
      // STATE
      // ========================================

      // Core order state (from OrderState)
      data: {
        byId: {},
        allIds: [],
        total: 0,
      },
      loading: false,
      error: null,
      lastFetch: null,

      selectedOrder: null,
      filters: {},
      sort: {
        field: 'created_at',
        direction: 'desc',
      },
      searchQuery: '',
      showFilters: false,

      isCreating: false,
      isUpdating: false,
      createError: null,
      updateError: null,

      userRole: 'buyer',
      currentUserId: undefined,

      // Extended state
      cacheExpiry: 3 * 60 * 1000, // 3 minutes for orders (more dynamic data)
      selectedOrderIds: [],
      showBulkActions: false,
      currentContext: 'buyer',
      currentVendorId: undefined,
      statusUpdateLoading: {},
      currentPage: 1,
      totalPages: 1,
      hasNextPage: false,
      hasPreviousPage: false,
      metricsCache: {},
      metricsLastFetch: {},

      // ========================================
      // FETCH OPERATIONS
      // ========================================

      /**
       * Fetch orders with context awareness
       */
      fetchOrders: async (params?: OrderSearchRequest): Promise<void> => {
        // Check cache validity for non-filtered requests
        const { isCacheValid } = get();
        if (isCacheValid() && !params && Object.keys(get().filters).length === 0) {
          return;
        }

        set((state) => {
          state.loading = true;
          state.error = null;
        });

        try {
          const { currentContext, currentUserId, currentVendorId, filters, sort, searchQuery, currentPage } = get();

          const searchParams: OrderSearchRequest = {
            ...params,
            ...filters,
            sort_by: sort.field,
            sort_order: sort.direction,
            page: params?.page || currentPage,
            limit: params?.limit || 20,
          };

          // Add context-specific filters
          if (currentContext === 'vendor' && currentVendorId) {
            searchParams.vendor_id = currentVendorId;
          } else if (currentContext === 'buyer' && currentUserId) {
            searchParams.user_id = currentUserId;
          }

          if (searchQuery) {
            searchParams.customer_email = searchQuery;
          }

          let response;
          switch (currentContext) {
            case 'vendor':
              response = currentVendorId
                ? await orderApiService.getVendorOrders(currentVendorId, searchParams)
                : await orderApiService.getMyVendorOrders(searchParams);
              break;
            case 'admin':
              response = await orderApiService.getAdminOrders(searchParams);
              break;
            default:
              response = currentUserId
                ? await orderApiService.getUserOrders(currentUserId, searchParams)
                : await orderApiService.getMyOrders(searchParams);
          }

          set((state) => {
            // Update orders collection
            const byId: Record<EntityId, Order> = {};
            const allIds: EntityId[] = [];

            response.data.forEach((order) => {
              byId[order.id] = order;
              allIds.push(order.id);
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
            state.error = error.message || 'Failed to fetch orders';
          });
        }
      },

      /**
       * Fetch single order by ID
       */
      fetchOrder: async (id: EntityId): Promise<Order | null> => {
        try {
          const order = await orderApiService.getOrder(id);

          set((state) => {
            // Add to collection
            state.data.byId[id] = order;
            if (!state.data.allIds.includes(id)) {
              state.data.allIds.push(id);
            }
          });

          return order;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to fetch order';
          });
          return null;
        }
      },

      /**
       * Fetch user orders
       */
      fetchUserOrders: async (userId: EntityId): Promise<void> => {
        set((state) => {
          state.currentUserId = userId;
          state.currentContext = 'buyer';
        });
        await get().fetchOrders();
      },

      /**
       * Fetch vendor orders
       */
      fetchVendorOrders: async (vendorId: EntityId): Promise<void> => {
        set((state) => {
          state.currentVendorId = vendorId;
          state.currentContext = 'vendor';
        });
        await get().fetchOrders();
      },

      // ========================================
      // CRUD OPERATIONS
      // ========================================

      /**
       * Create new order
       */
      createOrder: async (data: CreateOrderRequest): Promise<Order | null> => {
        set((state) => {
          state.isCreating = true;
          state.createError = null;
        });

        try {
          const order = await orderApiService.createOrder(data);

          set((state) => {
            // Add to collection
            state.data.byId[order.id] = order;
            state.data.allIds.unshift(order.id);
            state.data.total += 1;
            state.isCreating = false;
          });

          return order;
        } catch (error: any) {
          set((state) => {
            state.isCreating = false;
            state.createError = error.message || 'Failed to create order';
          });
          return null;
        }
      },

      /**
       * Update existing order
       */
      updateOrder: async (id: EntityId, data: UpdateOrderRequest): Promise<Order | null> => {
        set((state) => {
          state.isUpdating = true;
          state.updateError = null;
        });

        try {
          const order = await orderApiService.updateOrder(id, data);

          set((state) => {
            // Update in collection
            state.data.byId[id] = order;
            state.isUpdating = false;

            // Update selected order if it's the one being updated
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return order;
        } catch (error: any) {
          set((state) => {
            state.isUpdating = false;
            state.updateError = error.message || 'Failed to update order';
          });
          return null;
        }
      },

      /**
       * Cancel order
       */
      cancelOrder: async (id: EntityId, reason?: string): Promise<boolean> => {
        try {
          const order = await orderApiService.cancelOrder(id, reason);

          set((state) => {
            // Update in collection
            state.data.byId[id] = order;

            // Update selected order if it's the one being updated
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to cancel order';
          });
          return false;
        }
      },

      // ========================================
      // STATUS MANAGEMENT
      // ========================================

      /**
       * Update order status
       */
      updateOrderStatus: async (id: EntityId, status: OrderStatus): Promise<boolean> => {
        set((state) => {
          state.statusUpdateLoading[id] = true;
        });

        try {
          const order = await orderApiService.updateOrderStatus(id, status);

          set((state) => {
            // Update in collection
            state.data.byId[id] = order;
            delete state.statusUpdateLoading[id];

            // Update selected order if it's the one being updated
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            delete state.statusUpdateLoading[id];
            state.error = error.message || 'Failed to update order status';
          });
          return false;
        }
      },

      /**
       * Update payment status
       */
      updatePaymentStatus: async (id: EntityId, status: PaymentStatus): Promise<boolean> => {
        try {
          const order = await orderApiService.updatePaymentStatus(id, status);

          set((state) => {
            // Update in collection
            state.data.byId[id] = order;

            // Update selected order if it's the one being updated
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to update payment status';
          });
          return false;
        }
      },

      /**
       * Add tracking number
       */
      addTrackingNumber: async (id: EntityId, trackingNumber: string): Promise<boolean> => {
        try {
          const order = await orderApiService.addTrackingNumber(id, trackingNumber);

          set((state) => {
            // Update in collection
            state.data.byId[id] = order;

            // Update selected order if it's the one being updated
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to add tracking number';
          });
          return false;
        }
      },

      // ========================================
      // SELECTION AND UI
      // ========================================

      /**
       * Select order for details/editing
       */
      selectOrder: (order: Order | null): void => {
        set((state) => {
          state.selectedOrder = order;
        });
      },

      /**
       * Set filters
       */
      setFilters: (filters: Partial<OrderFilters>): void => {
        set((state) => {
          state.filters = { ...state.filters, ...filters };
          state.currentPage = 1; // Reset to first page
        });

        // Trigger fetch with new filters
        get().fetchOrders();
      },

      /**
       * Set sort configuration
       */
      setSort: (sort: OrderSort): void => {
        set((state) => {
          state.sort = sort;
          state.currentPage = 1; // Reset to first page
        });

        // Trigger fetch with new sort
        get().fetchOrders();
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
        get().fetchOrders();
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
       * Clear orders collection
       */
      clearOrders: (): void => {
        set((state) => {
          state.data = { byId: {}, allIds: [], total: 0 };
          state.selectedOrder = null;
          state.selectedOrderIds = [];
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
          state.selectedOrder = null;
          state.filters = {};
          state.sort = { field: 'created_at', direction: 'desc' };
          state.searchQuery = '';
          state.showFilters = false;
          state.isCreating = false;
          state.isUpdating = false;
          state.createError = null;
          state.updateError = null;
          state.selectedOrderIds = [];
          state.showBulkActions = false;
          state.currentPage = 1;
          state.totalPages = 1;
          state.hasNextPage = false;
          state.hasPreviousPage = false;
          state.statusUpdateLoading = {};
        });
      },

      // ========================================
      // EXTENDED ACTIONS
      // ========================================

      /**
       * Set current context
       */
      setContext: (context: 'buyer' | 'vendor' | 'admin', userId?: EntityId): void => {
        set((state) => {
          state.currentContext = context;
          state.userRole = context;
          if (context === 'vendor') {
            state.currentVendorId = userId;
          } else if (context === 'buyer') {
            state.currentUserId = userId;
          }
        });
      },

      /**
       * Select multiple orders
       */
      selectOrders: (ids: EntityId[]): void => {
        set((state) => {
          state.selectedOrderIds = ids;
          state.showBulkActions = ids.length > 0;
        });
      },

      /**
       * Select all orders
       */
      selectAllOrders: (): void => {
        set((state) => {
          state.selectedOrderIds = [...state.data.allIds];
          state.showBulkActions = state.data.allIds.length > 0;
        });
      },

      /**
       * Clear selection
       */
      clearSelection: (): void => {
        set((state) => {
          state.selectedOrderIds = [];
          state.showBulkActions = false;
        });
      },

      /**
       * Toggle order selection
       */
      toggleOrderSelection: (id: EntityId): void => {
        set((state) => {
          const isSelected = state.selectedOrderIds.includes(id);
          if (isSelected) {
            state.selectedOrderIds = state.selectedOrderIds.filter(orderId => orderId !== id);
          } else {
            state.selectedOrderIds.push(id);
          }
          state.showBulkActions = state.selectedOrderIds.length > 0;
        });
      },

      /**
       * Get selected orders
       */
      getSelectedOrders: (): Order[] => {
        const { selectedOrderIds, data } = get();
        return selectedOrderIds.map(id => data.byId[id]).filter(Boolean);
      },

      /**
       * Bulk update status
       */
      bulkUpdateStatus: async (status: OrderStatus): Promise<boolean> => {
        const { selectedOrderIds } = get();
        if (selectedOrderIds.length === 0) return false;

        try {
          const updatePromises = selectedOrderIds.map(id =>
            orderApiService.updateOrderStatus(id, status)
          );

          const updatedOrders = await Promise.all(updatePromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
            state.selectedOrderIds = [];
            state.showBulkActions = false;
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Bulk status update failed';
          });
          return false;
        }
      },

      /**
       * Bulk cancel orders
       */
      bulkCancel: async (reason?: string): Promise<boolean> => {
        const { selectedOrderIds } = get();
        if (selectedOrderIds.length === 0) return false;

        try {
          const cancelPromises = selectedOrderIds.map(id =>
            orderApiService.cancelOrder(id, reason)
          );

          const updatedOrders = await Promise.all(cancelPromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
            state.selectedOrderIds = [];
            state.showBulkActions = false;
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Bulk cancel failed';
          });
          return false;
        }
      },

      /**
       * Confirm orders
       */
      confirmOrders: async (ids: EntityId[]): Promise<boolean> => {
        const idsToUse = ids.length > 0 ? ids : get().selectedOrderIds;
        if (idsToUse.length === 0) return false;

        try {
          const confirmPromises = idsToUse.map(id =>
            orderApiService.confirmOrder(id)
          );

          const updatedOrders = await Promise.all(confirmPromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to confirm orders';
          });
          return false;
        }
      },

      /**
       * Process orders
       */
      processOrders: async (ids: EntityId[]): Promise<boolean> => {
        const idsToUse = ids.length > 0 ? ids : get().selectedOrderIds;
        if (idsToUse.length === 0) return false;

        try {
          const processPromises = idsToUse.map(id =>
            orderApiService.startProcessing(id)
          );

          const updatedOrders = await Promise.all(processPromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to process orders';
          });
          return false;
        }
      },

      /**
       * Ship orders
       */
      shipOrders: async (ids: EntityId[], trackingNumbers?: Record<EntityId, string>): Promise<boolean> => {
        const idsToUse = ids.length > 0 ? ids : get().selectedOrderIds;
        if (idsToUse.length === 0) return false;

        try {
          const shipPromises = idsToUse.map(id =>
            orderApiService.shipOrder(id, trackingNumbers?.[id])
          );

          const updatedOrders = await Promise.all(shipPromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to ship orders';
          });
          return false;
        }
      },

      /**
       * Mark orders as delivered
       */
      markDelivered: async (ids: EntityId[]): Promise<boolean> => {
        const idsToUse = ids.length > 0 ? ids : get().selectedOrderIds;
        if (idsToUse.length === 0) return false;

        try {
          const deliverPromises = idsToUse.map(id =>
            orderApiService.markDelivered(id)
          );

          const updatedOrders = await Promise.all(deliverPromises);

          set((state) => {
            updatedOrders.forEach(order => {
              state.data.byId[order.id] = order;
            });
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to mark orders as delivered';
          });
          return false;
        }
      },

      /**
       * Fetch vendor orders for current vendor
       */
      fetchMyVendorOrders: async (): Promise<void> => {
        set((state) => {
          state.currentContext = 'vendor';
        });
        await get().fetchOrders();
      },

      /**
       * Accept order (vendor action)
       */
      acceptOrder: async (id: EntityId): Promise<boolean> => {
        return get().updateOrderStatus(id, OrderStatus.CONFIRMED);
      },

      /**
       * Reject order (vendor action)
       */
      rejectOrder: async (id: EntityId, reason: string): Promise<boolean> => {
        return get().cancelOrder(id, reason);
      },

      /**
       * Fetch all orders for admin
       */
      fetchAllOrdersForAdmin: async (): Promise<void> => {
        set((state) => {
          state.currentContext = 'admin';
        });
        await get().fetchOrders();
      },

      /**
       * Admin force status update
       */
      adminForceStatus: async (id: EntityId, status: OrderStatus, notes?: string): Promise<boolean> => {
        try {
          const order = await orderApiService.adminUpdateStatus(id, status, notes);

          set((state) => {
            state.data.byId[id] = order;
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to update order status';
          });
          return false;
        }
      },

      /**
       * Refund order (admin action)
       */
      refundOrder: async (id: EntityId, reason?: string): Promise<boolean> => {
        try {
          const order = await orderApiService.refundOrder(id, reason);

          set((state) => {
            state.data.byId[id] = order;
            if (state.selectedOrder?.id === id) {
              state.selectedOrder = order;
            }
          });

          return true;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to refund order';
          });
          return false;
        }
      },

      /**
       * Fetch order metrics
       */
      fetchOrderMetrics: async (period?: string): Promise<any> => {
        try {
          const cacheKey = `metrics_${period || 'default'}`;
          const metrics = await orderApiService.getOrderMetrics({ period });

          set((state) => {
            state.metricsCache[cacheKey] = metrics;
            state.metricsLastFetch[cacheKey] = new Date().toISOString();
          });

          return metrics;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to fetch order metrics';
          });
          return null;
        }
      },

      /**
       * Fetch vendor metrics
       */
      fetchVendorMetrics: async (vendorId: EntityId, period?: string): Promise<any> => {
        try {
          const cacheKey = `vendor_metrics_${vendorId}_${period || 'default'}`;
          const metrics = await orderApiService.getVendorOrderAnalytics(vendorId, period);

          set((state) => {
            state.metricsCache[cacheKey] = metrics;
            state.metricsLastFetch[cacheKey] = new Date().toISOString();
          });

          return metrics;
        } catch (error: any) {
          set((state) => {
            state.error = error.message || 'Failed to fetch vendor metrics';
          });
          return null;
        }
      },

      /**
       * Invalidate cache
       */
      invalidateCache: (): void => {
        set((state) => {
          state.lastFetch = null;
          state.metricsCache = {};
          state.metricsLastFetch = {};
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
       * Go to specific page
       */
      goToPage: async (page: number): Promise<void> => {
        set((state) => {
          state.currentPage = page;
        });
        await get().fetchOrders({ page });
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
      name: 'order-store',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        filters: state.filters,
        sort: state.sort,
        showFilters: state.showFilters,
        currentContext: state.currentContext,
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
 * Order store selectors for optimized component subscriptions
 */
export const orderSelectors = {
  // Orders data
  orders: (state: ExtendedOrderStore) => state.data.allIds.map(id => state.data.byId[id]),
  orderById: (id: EntityId) => (state: ExtendedOrderStore) => state.data.byId[id],
  ordersCount: (state: ExtendedOrderStore) => state.data.total,

  // Loading and error states
  isLoading: (state: ExtendedOrderStore) => state.loading,
  error: (state: ExtendedOrderStore) => state.error,
  isCreating: (state: ExtendedOrderStore) => state.isCreating,
  isUpdating: (state: ExtendedOrderStore) => state.isUpdating,

  // Selection
  selectedOrder: (state: ExtendedOrderStore) => state.selectedOrder,
  selectedOrderIds: (state: ExtendedOrderStore) => state.selectedOrderIds,
  selectedOrders: (state: ExtendedOrderStore) => state.getSelectedOrders(),
  hasSelection: (state: ExtendedOrderStore) => state.selectedOrderIds.length > 0,

  // Context
  currentContext: (state: ExtendedOrderStore) => state.currentContext,
  userRole: (state: ExtendedOrderStore) => state.userRole,

  // Status updates
  statusUpdateLoading: (id: EntityId) => (state: ExtendedOrderStore) => state.statusUpdateLoading[id] || false,

  // UI state
  showFilters: (state: ExtendedOrderStore) => state.showFilters,
  showBulkActions: (state: ExtendedOrderStore) => state.showBulkActions,

  // Pagination
  currentPage: (state: ExtendedOrderStore) => state.currentPage,
  totalPages: (state: ExtendedOrderStore) => state.totalPages,
  hasNextPage: (state: ExtendedOrderStore) => state.hasNextPage,
  hasPreviousPage: (state: ExtendedOrderStore) => state.hasPreviousPage,

  // Filters and search
  filters: (state: ExtendedOrderStore) => state.filters,
  searchQuery: (state: ExtendedOrderStore) => state.searchQuery,
  sort: (state: ExtendedOrderStore) => state.sort,

  // Metrics
  metricsCache: (key: string) => (state: ExtendedOrderStore) => state.metricsCache[key],
};

// ========================================
// HOOKS
// ========================================

/**
 * Hook for orders list
 */
export const useOrders = () => useOrderStore(orderSelectors.orders);

/**
 * Hook for single order by ID
 */
export const useOrder = (id: EntityId) => useOrderStore(orderSelectors.orderById(id));

/**
 * Hook for loading state
 */
export const useOrdersLoading = () => useOrderStore(orderSelectors.isLoading);

/**
 * Hook for selected orders
 */
export const useSelectedOrders = () => useOrderStore(orderSelectors.selectedOrders);

/**
 * Hook for context-specific orders
 */
export const useOrdersForContext = (context: 'buyer' | 'vendor' | 'admin') => {
  const orders = useOrders();
  const currentContext = useOrderStore(orderSelectors.currentContext);
  return currentContext === context ? orders : [];
};

/**
 * Hook for pagination
 */
export const useOrdersPagination = () => useOrderStore((state) => ({
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

export type { ExtendedOrderState, ExtendedOrderActions, ExtendedOrderStore };
export default useOrderStore;