// frontend/src/stores/analyticsStore.ts
// PERFORMANCE_OPTIMIZED: Zustand store for real-time analytics data
// Designed for <1s load time and <500ms updates

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export interface AnalyticsMetrics {
  revenue: {
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
  };
  orders: {
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
  };
  products: {
    total: number;
    active: number;
    lowStock: number;
    outOfStock: number;
  };
  customers: {
    total: number;
    new: number;
    returning: number;
  };
}

export interface TopProduct {
  id: string;
  name: string;
  sales: number;
  revenue: number;
  image: string;
  trend: 'up' | 'down' | 'stable';
}

export interface CategorySales {
  category: string;
  sales: number;
  revenue: number;
  color: string;
  percentage: number;
}

export interface MonthlyTrend {
  month: string;
  revenue: number;
  orders: number;
  customers: number;
  timestamp: string;
}

export interface AnalyticsFilters {
  timeRange: '7d' | '30d' | '90d' | '1y';
  category: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface AnalyticsState {
  // Data
  metrics: AnalyticsMetrics | null;
  topProducts: TopProduct[];
  salesByCategory: CategorySales[];
  monthlyTrends: MonthlyTrend[];

  // UI State
  isLoading: boolean;
  isConnected: boolean;
  lastUpdated: string | null;
  filters: AnalyticsFilters;

  // Performance tracking
  loadTime: number;
  chartRenderTime: number;

  // Actions
  setMetrics: (metrics: AnalyticsMetrics) => void;
  setTopProducts: (products: TopProduct[]) => void;
  setSalesByCategory: (sales: CategorySales[]) => void;
  setMonthlyTrends: (trends: MonthlyTrend[]) => void;
  setFilters: (filters: Partial<AnalyticsFilters>) => void;
  setLoading: (loading: boolean) => void;
  setConnected: (connected: boolean) => void;
  updateLastUpdated: () => void;
  setLoadTime: (time: number) => void;
  setChartRenderTime: (time: number) => void;

  // Real-time updates
  updateRealTimeMetrics: (metrics: Partial<AnalyticsMetrics>) => void;
  addRealTimeOrder: (order: { value: number; category: string }) => void;
  updateFullAnalyticsData: (data: {
    metrics?: AnalyticsMetrics;
    topProducts?: TopProduct[];
    salesByCategory?: CategorySales[];
    monthlyTrends?: MonthlyTrend[];
  }) => void;

  // Computed selectors (memoized)
  getFilteredTrends: () => MonthlyTrend[];
  getFilteredProducts: () => TopProduct[];
  getFilteredCategories: () => CategorySales[];
  getTotalRevenue: () => number;
  getGrowthRate: () => number;
  getPerformanceMetrics: () => {
    loadTime: number;
    chartRenderTime: number;
    isOptimal: boolean;
  };
}

// Performance-optimized store with fine-grained selectors
export const useAnalyticsStore = create<AnalyticsState>()(
  subscribeWithSelector(
    immer((set, get) => ({
      // Initial state
      metrics: null,
      topProducts: [],
      salesByCategory: [],
      monthlyTrends: [],
      isLoading: false,
      isConnected: false,
      lastUpdated: null,
      filters: {
        timeRange: '30d',
        category: 'all'
      },
      loadTime: 0,
      chartRenderTime: 0,

      // Basic setters
      setMetrics: (metrics) => set((state) => {
        state.metrics = metrics;
        state.lastUpdated = new Date().toISOString();
      }),

      setTopProducts: (products) => set((state) => {
        state.topProducts = products;
      }),

      setSalesByCategory: (sales) => set((state) => {
        state.salesByCategory = sales;
      }),

      setMonthlyTrends: (trends) => set((state) => {
        state.monthlyTrends = trends;
      }),

      setFilters: (newFilters) => set((state) => {
        state.filters = { ...state.filters, ...newFilters };
      }),

      setLoading: (loading) => set((state) => {
        state.isLoading = loading;
      }),

      setConnected: (connected) => set((state) => {
        state.isConnected = connected;
      }),

      updateLastUpdated: () => set((state) => {
        state.lastUpdated = new Date().toISOString();
      }),

      setLoadTime: (time) => set((state) => {
        state.loadTime = time;
      }),

      setChartRenderTime: (time) => set((state) => {
        state.chartRenderTime = time;
      }),

      // Real-time updates (optimized for performance)
      updateRealTimeMetrics: (newMetrics) => set((state) => {
        if (state.metrics) {
          Object.assign(state.metrics, newMetrics);
          state.lastUpdated = new Date().toISOString();
        }
      }),

      addRealTimeOrder: (order) => set((state) => {
        // Update metrics
        if (state.metrics) {
          state.metrics.orders.current += 1;
          state.metrics.revenue.current += order.value;
        }

        // Update category sales
        const categoryIndex = state.salesByCategory.findIndex(
          cat => cat.category.toLowerCase() === order.category.toLowerCase()
        );
        if (categoryIndex !== -1) {
          state.salesByCategory[categoryIndex].sales += 1;
          state.salesByCategory[categoryIndex].revenue += order.value;
        }

        // Update monthly trends (current month)
        if (state.monthlyTrends.length > 0) {
          const currentMonth = state.monthlyTrends[state.monthlyTrends.length - 1];
          currentMonth.orders += 1;
          currentMonth.revenue += order.value;
        }

        state.lastUpdated = new Date().toISOString();
      }),

      updateFullAnalyticsData: (data) => set((state) => {
        // Update all analytics data from WebSocket
        if (data.metrics) {
          state.metrics = data.metrics;
        }
        if (data.topProducts) {
          state.topProducts = data.topProducts;
        }
        if (data.salesByCategory) {
          state.salesByCategory = data.salesByCategory;
        }
        if (data.monthlyTrends) {
          state.monthlyTrends = data.monthlyTrends;
        }
        state.lastUpdated = new Date().toISOString();
      }),

      // Memoized selectors
      getFilteredTrends: () => {
        const { monthlyTrends, filters } = get();
        const daysMap = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 };
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - daysMap[filters.timeRange]);

        return monthlyTrends.filter(trend => {
          const trendDate = new Date(trend.timestamp || trend.month);
          return trendDate >= cutoffDate;
        });
      },

      getFilteredProducts: () => {
        const { topProducts, filters } = get();
        if (filters.category === 'all') return topProducts;

        // Filter by category if implemented in future
        return topProducts;
      },

      getFilteredCategories: () => {
        const { salesByCategory, filters } = get();
        if (filters.category === 'all') return salesByCategory;

        return salesByCategory.filter(cat =>
          cat.category.toLowerCase().includes(filters.category.toLowerCase())
        );
      },

      getTotalRevenue: () => {
        const { metrics } = get();
        return metrics?.revenue.current || 0;
      },

      getGrowthRate: () => {
        const { metrics } = get();
        return metrics?.revenue.percentage || 0;
      },

      getPerformanceMetrics: () => {
        const { loadTime, chartRenderTime } = get();
        return {
          loadTime,
          chartRenderTime,
          isOptimal: loadTime < 1000 && chartRenderTime < 500
        };
      }
    }))
  )
);

// Performance-optimized selectors
export const useAnalyticsMetrics = () => useAnalyticsStore(state => state.metrics);
export const useAnalyticsTopProducts = () => useAnalyticsStore(state => state.topProducts);
export const useAnalyticsSalesByCategory = () => useAnalyticsStore(state => state.salesByCategory);
export const useAnalyticsMonthlyTrends = () => useAnalyticsStore(state => state.monthlyTrends);
export const useAnalyticsFilters = () => useAnalyticsStore(state => state.filters);
export const useAnalyticsLoading = () => useAnalyticsStore(state => state.isLoading);
export const useAnalyticsConnected = () => useAnalyticsStore(state => state.isConnected);
export const useAnalyticsLastUpdated = () => useAnalyticsStore(state => state.lastUpdated);

// Computed selectors
export const useFilteredTrends = () => useAnalyticsStore(state => state.getFilteredTrends());
export const useFilteredProducts = () => useAnalyticsStore(state => state.getFilteredProducts());
export const useFilteredCategories = () => useAnalyticsStore(state => state.getFilteredCategories());
export const useTotalRevenue = () => useAnalyticsStore(state => state.getTotalRevenue());
export const useGrowthRate = () => useAnalyticsStore(state => state.getGrowthRate());
export const usePerformanceMetrics = () => useAnalyticsStore(state => state.getPerformanceMetrics());

// Actions
export const useAnalyticsActions = () => useAnalyticsStore(state => ({
  setMetrics: state.setMetrics,
  setTopProducts: state.setTopProducts,
  setSalesByCategory: state.setSalesByCategory,
  setMonthlyTrends: state.setMonthlyTrends,
  setFilters: state.setFilters,
  setLoading: state.setLoading,
  setConnected: state.setConnected,
  updateLastUpdated: state.updateLastUpdated,
  setLoadTime: state.setLoadTime,
  setChartRenderTime: state.setChartRenderTime,
  updateRealTimeMetrics: state.updateRealTimeMetrics,
  addRealTimeOrder: state.addRealTimeOrder,
  updateFullAnalyticsData: state.updateFullAnalyticsData
}));