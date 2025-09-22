// Mock Analytics Store for tests
// Prevents Zustand infinite loops and real store operations

// Mock data
const mockAnalyticsData = {
  revenue: {
    current: 1500000,
    previous: 1200000,
    trend: 'up' as const,
    percentage: 25,
  },
  orders: {
    current: 45,
    previous: 38,
    trend: 'up' as const,
    percentage: 18.4,
  },
  products: {
    total: 15,
    active: 12,
    lowStock: 3,
    outOfStock: 1,
  },
  customers: {
    total: 120,
    new: 15,
    returning: 105,
  },
  trends: [
    { date: '2024-01-01', revenue: 100000, orders: 10 },
    { date: '2024-01-02', revenue: 150000, orders: 15 },
    { date: '2024-01-03', revenue: 120000, orders: 12 },
  ],
  topProducts: [
    { id: '1', name: 'Product 1', sales: 50, revenue: 500000 },
    { id: '2', name: 'Product 2', sales: 30, revenue: 300000 },
  ],
  categories: [
    { id: 'electronics', name: 'Electronics', sales: 80, percentage: 60 },
    { id: 'clothing', name: 'Clothing', sales: 40, percentage: 30 },
  ],
};

// Mock store state
const mockStoreState = {
  // Data
  isConnected: false,
  isLoading: false,
  error: null,
  lastUpdated: new Date().toISOString(),
  ...mockAnalyticsData,

  // Filters
  timeRange: '30d' as const,
  selectedCategories: [] as string[],
  sortBy: 'revenue' as const,
  sortOrder: 'desc' as const,

  // Pagination
  currentPage: 1,
  itemsPerPage: 10,
  totalItems: 25,

  // Actions (all mocked)
  setConnected: jest.fn(),
  setLoading: jest.fn(),
  setError: jest.fn(),
  updateMetrics: jest.fn(),
  updateTrends: jest.fn(),
  updateTopProducts: jest.fn(),
  updateCategories: jest.fn(),
  setTimeRange: jest.fn(),
  setSelectedCategories: jest.fn(),
  setSortBy: jest.fn(),
  setSortOrder: jest.fn(),
  setCurrentPage: jest.fn(),
  setItemsPerPage: jest.fn(),
  reset: jest.fn(),

  // Computed values (cached to prevent infinite loops)
  getFilteredTrends: jest.fn().mockReturnValue(mockAnalyticsData.trends),
  getFilteredProducts: jest.fn().mockReturnValue(mockAnalyticsData.topProducts),
  getFilteredCategories: jest.fn().mockReturnValue(mockAnalyticsData.categories),
  getTotalRevenue: jest.fn().mockReturnValue(1500000),
  getTotalOrders: jest.fn().mockReturnValue(45),
  getAverageOrderValue: jest.fn().mockReturnValue(33333),
  getGrowthRate: jest.fn().mockReturnValue(25),
  getPaginatedProducts: jest.fn().mockReturnValue(mockAnalyticsData.topProducts),
  getPaginationInfo: jest.fn().mockReturnValue({
    currentPage: 1,
    totalPages: 3,
    totalItems: 25,
    hasNext: true,
    hasPrev: false,
  }),
};

// Create the mock store function
const useAnalyticsStore = jest.fn();

// Set default implementation to return the mock state
useAnalyticsStore.mockImplementation((selector?: (state: any) => any) => {
  if (selector) {
    return selector(mockStoreState);
  }
  return mockStoreState;
});

// Add getState method for direct access
useAnalyticsStore.getState = jest.fn().mockReturnValue(mockStoreState);

// Export computed selectors with cached results
export const useFilteredTrends = jest.fn().mockReturnValue(mockAnalyticsData.trends);
export const useFilteredProducts = jest.fn().mockReturnValue(mockAnalyticsData.topProducts);
export const useFilteredCategories = jest.fn().mockReturnValue(mockAnalyticsData.categories);
export const useTotalRevenue = jest.fn().mockReturnValue(1500000);

// Export the main store hook
export { useAnalyticsStore };
export default useAnalyticsStore;

// Reset function for tests
export const resetAnalyticsStoreMock = () => {
  useAnalyticsStore.mockClear();
  useFilteredTrends.mockClear();
  useFilteredProducts.mockClear();
  useFilteredCategories.mockClear();
  useTotalRevenue.mockClear();

  // Reset all action mocks
  Object.values(mockStoreState).forEach((value: any) => {
    if (jest.isMockFunction(value)) {
      value.mockClear();
    }
  });
};

// Helper to update mock data for specific tests
export const setMockAnalyticsData = (newData: Partial<typeof mockAnalyticsData>) => {
  Object.assign(mockAnalyticsData, newData);
  Object.assign(mockStoreState, newData);
};