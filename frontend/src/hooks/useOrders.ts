// frontend/src/hooks/useOrders.ts
// PRODUCTION_READY: Hook personalizado para gestión de órdenes

import { useState, useEffect, useCallback } from 'react';
import { orderService } from '../services/orderService';
import {
  Order,
  OrderFilters,
  OrdersResponse,
  VendorOrderSummary,
  TrackingInfo
} from '../types/orders';
import { useAuthStore } from '../stores/authStore';

export interface UseOrdersOptions {
  userRole?: 'buyer' | 'vendor' | 'admin';
  autoLoad?: boolean;
  filters?: OrderFilters;
}

export interface UseOrdersReturn {
  // Data state
  orders: Order[] | VendorOrderSummary[];
  loading: boolean;
  error: string | null;
  selectedOrder: Order | VendorOrderSummary | null;

  // Pagination
  totalOrders: number;
  currentPage: number;
  totalPages: number;

  // Actions
  loadOrders: (showLoading?: boolean) => Promise<void>;
  selectOrder: (order: Order | VendorOrderSummary) => void;
  updateOrderStatus: (orderId: string, status: string, notes?: string) => Promise<void>;
  refreshOrders: () => Promise<void>;

  // Filters
  filters: OrderFilters;
  updateFilters: (newFilters: Partial<OrderFilters>) => void;

  // Stats
  stats: {
    total: number;
    pending: number;
    processing: number;
    shipped: number;
    delivered: number;
    cancelled: number;
  };
}

export const useOrders = (options: UseOrdersOptions = {}): UseOrdersReturn => {
  const { userRole = 'buyer', autoLoad = true, filters: initialFilters = {} } = options;
  const { user } = useAuthStore();

  // State
  const [orders, setOrders] = useState<Order[] | VendorOrderSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | VendorOrderSummary | null>(null);
  const [totalOrders, setTotalOrders] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<OrderFilters>({
    status: 'all',
    page: 1,
    limit: 20,
    ...initialFilters
  });

  // Load orders based on user role
  const loadOrders = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);

      let response;

      if (userRole === 'vendor') {
        // Use vendor-specific endpoint
        const vendorFilters = {
          status: filters.status !== 'all' ? filters.status : undefined,
          skip: ((filters.page || 1) - 1) * (filters.limit || 20),
          limit: filters.limit || 20
        };

        const vendorOrders = await orderService.getVendorOrders(vendorFilters);

        setOrders(vendorOrders || []);
        setTotalOrders(vendorOrders?.length || 0);
        setCurrentPage(filters.page || 1);
        setTotalPages(Math.ceil((vendorOrders?.length || 0) / (filters.limit || 20)));
      } else {
        // Use standard endpoint for buyers/admin
        const queryFilters = userRole === 'buyer' && user?.id
          ? { ...filters, buyer_id: user.id }
          : filters;

        response = await orderService.getOrders(queryFilters);

        setOrders(response.data.orders);
        setTotalOrders(response.data.total);
        setCurrentPage(response.data.page);
        setTotalPages(response.data.total_pages);
      }
    } catch (err: any) {
      console.error('Error loading orders:', err);
      setError(err.message || 'Error al cargar las órdenes');
      setOrders([]);
      setTotalOrders(0);
    } finally {
      setLoading(false);
    }
  }, [filters, userRole, user?.id]);

  // Update order status
  const updateOrderStatus = useCallback(async (orderId: string, status: string, notes?: string) => {
    try {
      if (userRole === 'vendor') {
        await orderService.updateVendorOrderStatus(orderId, status, notes);
      } else {
        await orderService.updateOrderStatus(orderId, { status: status as any, notes });
      }

      // Update local state
      setOrders(prev => prev.map(order =>
        order.id.toString() === orderId
          ? { ...order, status }
          : order
      ));

      // Update selected order if it matches
      if (selectedOrder && selectedOrder.id.toString() === orderId) {
        setSelectedOrder(prev => prev ? { ...prev, status } : null);
      }

    } catch (err: any) {
      console.error('Error updating order status:', err);
      throw new Error(err.message || 'Error al actualizar el estado');
    }
  }, [userRole, selectedOrder]);

  // Select order
  const selectOrder = useCallback((order: Order | VendorOrderSummary) => {
    setSelectedOrder(order);
  }, []);

  // Refresh orders
  const refreshOrders = useCallback(() => {
    return loadOrders(false);
  }, [loadOrders]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<OrderFilters>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      page: newFilters.page || 1 // Reset to first page on filter change
    }));
  }, []);

  // Calculate stats
  const stats = {
    total: totalOrders,
    pending: orders.filter(o => o.status === 'pending').length,
    processing: orders.filter(o => ['confirmed', 'processing'].includes(o.status)).length,
    shipped: orders.filter(o => o.status === 'shipped').length,
    delivered: orders.filter(o => o.status === 'delivered').length,
    cancelled: orders.filter(o => o.status === 'cancelled').length,
  };

  // Auto load on mount and filter changes
  useEffect(() => {
    if (autoLoad) {
      loadOrders();
    }
  }, [autoLoad, loadOrders]);

  return {
    // Data state
    orders,
    loading,
    error,
    selectedOrder,

    // Pagination
    totalOrders,
    currentPage,
    totalPages,

    // Actions
    loadOrders,
    selectOrder,
    updateOrderStatus,
    refreshOrders,

    // Filters
    filters,
    updateFilters,

    // Stats
    stats
  };
};

// Hook específico para tracking de órdenes
export interface UseOrderTrackingReturn {
  trackingInfo: TrackingInfo | null;
  loading: boolean;
  error: string | null;
  loadTracking: (orderId: string) => Promise<void>;
  refreshTracking: () => Promise<void>;
}

export const useOrderTracking = (): UseOrderTrackingReturn => {
  const [trackingInfo, setTrackingInfo] = useState<TrackingInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastOrderId, setLastOrderId] = useState<string | null>(null);

  const loadTracking = useCallback(async (orderId: string) => {
    try {
      setLoading(true);
      setError(null);
      setLastOrderId(orderId);

      const response = await orderService.getBuyerOrderTracking(orderId);
      setTrackingInfo(response.data);
    } catch (err: any) {
      console.error('Error loading tracking:', err);
      setError(err.message || 'Error al cargar el seguimiento');
      setTrackingInfo(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshTracking = useCallback(() => {
    if (lastOrderId) {
      return loadTracking(lastOrderId);
    }
    return Promise.resolve();
  }, [lastOrderId, loadTracking]);

  return {
    trackingInfo,
    loading,
    error,
    loadTracking,
    refreshTracking
  };
};

// Hook para estadísticas de órdenes
export interface UseOrderStatsReturn {
  stats: {
    totalOrders: number;
    totalRevenue: number;
    averageOrderValue: number;
    monthlyGrowth: number;
    statusDistribution: Record<string, number>;
    recentOrders: Order[];
  };
  loading: boolean;
  error: string | null;
  refreshStats: () => Promise<void>;
}

export const useOrderStats = (userRole: 'buyer' | 'vendor' = 'buyer'): UseOrderStatsReturn => {
  const { orders, loading, error, refreshOrders } = useOrders({
    userRole,
    autoLoad: true,
    filters: { limit: 100 } // Get more orders for better stats
  });

  const calculateStats = useCallback(() => {
    const typedOrders = orders as Order[];

    if (!typedOrders.length) {
      return {
        totalOrders: 0,
        totalRevenue: 0,
        averageOrderValue: 0,
        monthlyGrowth: 0,
        statusDistribution: {},
        recentOrders: []
      };
    }

    const totalRevenue = typedOrders.reduce((sum, order) => {
      return sum + (userRole === 'vendor'
        ? (order as any).vendor_items_total || 0
        : order.total_amount || 0
      );
    }, 0);

    const averageOrderValue = totalRevenue / typedOrders.length;

    // Calculate monthly growth (simplified)
    const currentMonth = new Date().getMonth();
    const currentMonthOrders = typedOrders.filter(order =>
      new Date(order.created_at).getMonth() === currentMonth
    );
    const lastMonthOrders = typedOrders.filter(order =>
      new Date(order.created_at).getMonth() === currentMonth - 1
    );

    const monthlyGrowth = lastMonthOrders.length > 0
      ? ((currentMonthOrders.length - lastMonthOrders.length) / lastMonthOrders.length) * 100
      : 0;

    // Status distribution
    const statusDistribution = typedOrders.reduce((acc, order) => {
      acc[order.status] = (acc[order.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Recent orders (last 5)
    const recentOrders = [...typedOrders]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);

    return {
      totalOrders: typedOrders.length,
      totalRevenue,
      averageOrderValue,
      monthlyGrowth,
      statusDistribution,
      recentOrders
    };
  }, [orders, userRole]);

  const stats = calculateStats();

  return {
    stats,
    loading,
    error,
    refreshStats: refreshOrders
  };
};

export default useOrders;