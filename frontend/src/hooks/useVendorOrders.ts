// ~/frontend/src/hooks/useVendorOrders.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Vendor Orders Hook (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Custom hook para vendor orders con estado optimizado
 *
 * Features enterprise:
 * - Estado reactivo con React Query pattern
 * - Auto-refresh configurable
 * - Error handling integrado
 * - Loading states optimizados
 * - Cache invalidation inteligente
 * - Real-time updates support
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { vendorOrderService } from '../services/vendorOrderService';
import { VENDOR_CONFIG, VendorOrder, VendorOrderFilters, VendorOrderResponse } from '../config/vendorConfig';

interface UseVendorOrdersState {
  orders: VendorOrder[];
  isLoading: boolean;
  error: string | null;
  totalOrders: number;
  vendorEmail: string;
  lastUpdated: Date | null;
}

interface UseVendorOrdersActions {
  refresh: () => Promise<void>;
  updateFilters: (filters: VendorOrderFilters) => void;
  updateOrderStatus: (orderId: number, status: string, notes?: string) => Promise<boolean>;
  clearError: () => void;
}

type UseVendorOrdersReturn = UseVendorOrdersState & UseVendorOrdersActions;

export const useVendorOrders = (
  vendorId: string,
  initialFilters: VendorOrderFilters = {},
  enableAutoRefresh = true
): UseVendorOrdersReturn => {

  // Estado principal
  const [state, setState] = useState<UseVendorOrdersState>({
    orders: [],
    isLoading: false,
    error: null,
    totalOrders: 0,
    vendorEmail: '',
    lastUpdated: null,
  });

  const [filters, setFilters] = useState<VendorOrderFilters>(initialFilters);

  // Refs para cleanup y control
  const refreshInterval = useRef<NodeJS.Timeout | null>(null);
  const abortController = useRef<AbortController | null>(null);
  const isUnmounted = useRef(false);

  // PERFORMANCE_CRITICAL: Fetch orders con abort signal
  const fetchOrders = useCallback(async (showLoading = true) => {
    // Cancelar request anterior si existe
    if (abortController.current) {
      abortController.current.abort();
    }

    abortController.current = new AbortController();

    if (showLoading) {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
    }

    try {
      const result = await vendorOrderService.getVendorOrders(vendorId, filters);

      // Verificar si component fue unmounted
      if (isUnmounted.current) return;

      if (result.success && result.data) {
        setState(prev => ({
          ...prev,
          orders: result.data!.orders,
          totalOrders: result.data!.total_orders,
          vendorEmail: result.data!.vendor_email,
          isLoading: false,
          error: null,
          lastUpdated: new Date(),
        }));
      } else {
        setState(prev => ({
          ...prev,
          orders: [],
          isLoading: false,
          error: result.error || 'Error loading orders',
          lastUpdated: new Date(),
        }));
      }
    } catch (error) {
      if (isUnmounted.current) return;

      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
        lastUpdated: new Date(),
      }));
    }
  }, [vendorId, filters]);

  // Setup auto-refresh
  useEffect(() => {
    if (!enableAutoRefresh) return;

    const setupAutoRefresh = () => {
      if (refreshInterval.current) {
        clearInterval(refreshInterval.current);
      }

      refreshInterval.current = setInterval(() => {
        fetchOrders(false); // Background refresh sin loading state
      }, VENDOR_CONFIG.ORDER_REFRESH_INTERVAL);
    };

    setupAutoRefresh();

    return () => {
      if (refreshInterval.current) {
        clearInterval(refreshInterval.current);
      }
    };
  }, [fetchOrders, enableAutoRefresh]);

  // Real-time updates listener
  useEffect(() => {
    const handleRealTimeUpdate = (event: CustomEvent) => {
      const update = event.detail;

      // Refresh orders cuando hay update en tiempo real
      if (update.vendorId === vendorId) {
        fetchOrders(false);
      }
    };

    window.addEventListener('vendor-orders-updated', handleRealTimeUpdate as EventListener);

    // Enable real-time updates si está configurado
    if (VENDOR_CONFIG.ENABLE_REALTIME && vendorId) {
      vendorOrderService.enableRealTimeUpdates(vendorId);
    }

    return () => {
      window.removeEventListener('vendor-orders-updated', handleRealTimeUpdate as EventListener);
      vendorOrderService.disconnect();
    };
  }, [vendorId, fetchOrders]);

  // Initial fetch y cleanup
  useEffect(() => {
    isUnmounted.current = false;

    if (vendorId) {
      fetchOrders();
    }

    return () => {
      isUnmounted.current = true;

      if (abortController.current) {
        abortController.current.abort();
      }

      if (refreshInterval.current) {
        clearInterval(refreshInterval.current);
      }
    };
  }, [fetchOrders, vendorId]);

  // Refetch cuando filters cambian
  useEffect(() => {
    if (vendorId) {
      fetchOrders();
    }
  }, [filters, fetchOrders, vendorId]);

  // PRODUCTION_READY: Actions para component
  const actions: UseVendorOrdersActions = {
    refresh: async () => {
      await fetchOrders(true);
    },

    updateFilters: useCallback((newFilters: VendorOrderFilters) => {
      setFilters(prev => ({ ...prev, ...newFilters }));
    }, []),

    updateOrderStatus: useCallback(async (orderId: number, status: string, notes?: string) => {
      setState(prev => ({ ...prev, error: null }));

      try {
        const result = await vendorOrderService.updateOrderStatus(orderId, status, notes);

        if (result.success) {
          // Refresh orders después de actualizar
          await fetchOrders(false);
          return true;
        } else {
          setState(prev => ({
            ...prev,
            error: result.error || 'Error updating order status'
          }));
          return false;
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState(prev => ({ ...prev, error: errorMessage }));
        return false;
      }
    }, [fetchOrders]),

    clearError: useCallback(() => {
      setState(prev => ({ ...prev, error: null }));
    }, []),
  };

  return {
    ...state,
    ...actions,
  };
};

// Hook para obtener lista de vendors (development/testing)
export const useVendorsList = () => {
  const [vendors, setVendors] = useState<Array<{id: string; email: string; full_name: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVendors = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await vendorOrderService.getVendors();

      if (result.success && result.data) {
        setVendors(result.data);
      } else {
        setError(result.error || 'Error loading vendors');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchVendors();
  }, [fetchVendors]);

  return {
    vendors,
    isLoading,
    error,
    refresh: fetchVendors,
  };
};

export default useVendorOrders;