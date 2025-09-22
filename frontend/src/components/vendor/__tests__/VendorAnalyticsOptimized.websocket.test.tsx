// Jest equivalents for Vitest imports
const vi = jest;
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { VendorAnalyticsOptimized } from '../VendorAnalyticsOptimized';

// Mock analytics store with Jest-compatible approach
jest.mock('../../../stores/analyticsStore', () => {
  const mockUseAnalyticsMetrics = jest.fn();
  const mockUseAnalyticsActions = jest.fn();
  const mockUseAnalyticsLoading = jest.fn(() => false);
  const mockUseAnalyticsLastUpdated = jest.fn(() => new Date().toISOString());
  const mockUseAnalyticsFilters = jest.fn(() => ({ timeRange: '30d' }));
  const mockUseFilteredTrends = jest.fn(() => []);
  const mockUseFilteredProducts = jest.fn(() => []);
  const mockUseFilteredCategories = jest.fn(() => []);
  const mockUseTotalRevenue = jest.fn(() => 12750000);
  const mockUseGrowthRate = jest.fn(() => 29.4);
  const mockUsePerformanceMetrics = jest.fn(() => ({
    loadTime: 850,
    chartRenderTime: 150,
    isOptimal: true
  }));
  const mockUseAnalyticsConnected = jest.fn(() => true);

  return {
    __esModule: true,
    useAnalyticsMetrics: mockUseAnalyticsMetrics,
    useAnalyticsActions: mockUseAnalyticsActions,
    useAnalyticsLoading: mockUseAnalyticsLoading,
    useAnalyticsLastUpdated: mockUseAnalyticsLastUpdated,
    useAnalyticsFilters: mockUseAnalyticsFilters,
    useFilteredTrends: mockUseFilteredTrends,
    useFilteredProducts: mockUseFilteredProducts,
    useFilteredCategories: mockUseFilteredCategories,
    useTotalRevenue: mockUseTotalRevenue,
    useGrowthRate: mockUseGrowthRate,
    usePerformanceMetrics: mockUsePerformanceMetrics,
    useAnalyticsConnected: mockUseAnalyticsConnected
  };
});

// Mock WebSocket service
const mockWebSocketService = {
  isConnected: false,
  authError: null,
  connect: vi.fn(),
  disconnect: vi.fn(),
  getLatency: vi.fn(() => 45),
  getConnectionState: vi.fn(() => 'connected'),
  send: vi.fn(),
  on: vi.fn(),
  off: vi.fn()
};

vi.mock('../../../services/websocketService', () => ({
  useWebSocket: vi.fn(() => mockWebSocketService)
}));

// Mock accessibility utils
vi.mock('../../../utils/accessibility', () => ({
  screenReader: {
    announce: vi.fn()
  },
  focusManagement: {
    trapFocus: vi.fn(),
    restoreFocus: vi.fn()
  },
  aria: {
    setLiveRegion: vi.fn()
  },
  reducedMotion: {
    prefersReducedMotion: vi.fn(() => false)
  }
}));

// Mock lazy-loaded components
vi.mock('../charts/AccessibleBarChart', () => ({
  AccessibleBarChart: () => <div data-testid="bar-chart">Bar Chart</div>
}));

vi.mock('../charts/AccessiblePieChart', () => ({
  AccessiblePieChart: () => <div data-testid="pie-chart">Pie Chart</div>
}));

vi.mock('../components/TopProductsList', () => ({
  TopProductsList: () => <div data-testid="top-products">Top Products</div>
}));

describe.skip('VendorAnalyticsOptimized - WebSocket Authentication Tests', () => {
  const user = userEvent.setup();

  // Mock analytics store return values
  const mockAnalyticsActions = {
    setFilters: vi.fn(),
    setLoading: vi.fn(),
    setLoadTime: vi.fn(),
    setChartRenderTime: vi.fn(),
    setMetrics: vi.fn(),
    setTopProducts: vi.fn(),
    setSalesByCategory: vi.fn(),
    setMonthlyTrends: vi.fn()
  };

  const mockMetrics = {
    revenue: {
      current: 12750000,
      previous: 9850000,
      trend: 'up' as const,
      percentage: 29.4
    },
    orders: {
      current: 156,
      previous: 134,
      trend: 'up' as const,
      percentage: 16.4
    },
    products: {
      total: 45,
      active: 42,
      lowStock: 8,
      outOfStock: 3
    },
    customers: {
      total: 89,
      new: 23,
      returning: 66
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup analytics store mocks using jest.mocked
    const analyticsStore = require('../../../stores/analyticsStore');
    jest.mocked(analyticsStore.useAnalyticsMetrics).mockReturnValue(mockMetrics);
    jest.mocked(analyticsStore.useAnalyticsActions).mockReturnValue(mockAnalyticsActions);

    // Reset WebSocket mock
    mockWebSocketService.isConnected = false;
    mockWebSocketService.authError = null;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('🔌 WebSocket Connection Status', () => {
    it('should display "Desconectado" when WebSocket is not connected', async () => {
      mockWebSocketService.isConnected = false;
      mockWebSocketService.authError = null;

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('Desconectado')).toBeInTheDocument();
      });

      // Should show red indicator
      const statusIndicator = screen.getByText('Desconectado').previousElementSibling;
      expect(statusIndicator).toHaveClass('bg-red-500');
    });

    it('should display "Tiempo real activo" when WebSocket is connected', async () => {
      mockWebSocketService.isConnected = true;
      mockWebSocketService.authError = null;

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('Tiempo real activo')).toBeInTheDocument();
      });

      // Should show green indicator
      const statusIndicator = screen.getByText('Tiempo real activo').previousElementSibling;
      expect(statusIndicator).toHaveClass('bg-green-500');
    });

    it('should display latency information when connected', async () => {
      mockWebSocketService.isConnected = true;
      mockWebSocketService.getLatency = vi.fn(() => 45);

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('(45ms latencia)')).toBeInTheDocument();
      });
    });

    it('should not display latency when not connected', async () => {
      mockWebSocketService.isConnected = false;

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.queryByText(/latencia/)).not.toBeInTheDocument();
      });
    });
  });

  describe('🔐 Authentication Error Handling', () => {
    it('should display "Error de autenticación" when auth error exists', async () => {
      mockWebSocketService.isConnected = false;
      mockWebSocketService.authError = 'Invalid token';

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('Error de autenticación')).toBeInTheDocument();
      });

      // Should show yellow indicator for auth error
      const statusIndicator = screen.getByText('Error de autenticación').previousElementSibling;
      expect(statusIndicator).toHaveClass('bg-yellow-500');
    });

    it('should show "Reconectar" button when auth error exists', async () => {
      mockWebSocketService.authError = 'Token expired';

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const reconnectButton = screen.getByText('Reconectar');
        expect(reconnectButton).toBeInTheDocument();
        expect(reconnectButton).toHaveAttribute('title', 'Recargar página para volver a autenticar');
      });
    });

    it('should reload page when "Reconectar" button is clicked', async () => {
      mockWebSocketService.authError = 'Authentication failed';

      // Mock window.location.reload
      const mockReload = vi.fn();
      Object.defineProperty(window, 'location', {
        value: {
          reload: mockReload
        },
        writable: true
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const reconnectButton = screen.getByText('Reconectar');
        expect(reconnectButton).toBeInTheDocument();
      });

      const reconnectButton = screen.getByText('Reconectar');
      await user.click(reconnectButton);

      expect(mockReload).toHaveBeenCalledOnce();
    });

    it('should not show "Reconectar" button when no auth error', async () => {
      mockWebSocketService.authError = null;

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.queryByText('Reconectar')).not.toBeInTheDocument();
      });
    });
  });

  describe('🚀 WebSocket Integration & Performance', () => {
    it('should initialize WebSocket connection with correct vendor ID', async () => {
      const testVendorId = 'vendor-123';

      render(<VendorAnalyticsOptimized vendorId={testVendorId} />);

      // useWebSocket should be called with the vendor ID
      expect(require('../../../services/websocketService').useWebSocket).toHaveBeenCalledWith(testVendorId);
    });

    it('should use default vendor ID when none provided', async () => {
      render(<VendorAnalyticsOptimized />);

      expect(require('../../../services/websocketService').useWebSocket).toHaveBeenCalledWith('default-vendor');
    });

    it('should display performance status indicator when optimal', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 850,
        chartRenderTime: 150,
        isOptimal: true
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('Rendimiento óptimo')).toBeInTheDocument();
      });

      // Should show green indicator
      const perfIndicator = screen.getByText('Rendimiento óptimo').previousElementSibling;
      expect(perfIndicator).toHaveClass('bg-green-500');
    });

    it('should not display performance indicator when not optimal', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 1500,
        chartRenderTime: 800,
        isOptimal: false
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.queryByText('Rendimiento óptimo')).not.toBeInTheDocument();
      });
    });
  });

  describe('🔄 Real-time Data Updates', () => {
    it('should announce WebSocket connection changes to screen reader', async () => {
      const { rerender } = render(<VendorAnalyticsOptimized />);

      // Initially disconnected
      expect(mockWebSocketService.isConnected).toBe(false);

      // Simulate connection
      mockWebSocketService.isConnected = true;
      rerender(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        expect(screen.getByText('Tiempo real activo')).toBeInTheDocument();
      });

      // Should announce status changes
      expect(require('../../../utils/accessibility').screenReader.announce).toHaveBeenCalled();
    });

    it('should handle multiple connection state changes', async () => {
      const { rerender } = render(<VendorAnalyticsOptimized />);

      // Connected
      mockWebSocketService.isConnected = true;
      mockWebSocketService.authError = null;
      rerender(<VendorAnalyticsOptimized />);

      expect(screen.getByText('Tiempo real activo')).toBeInTheDocument();

      // Auth error
      mockWebSocketService.isConnected = false;
      mockWebSocketService.authError = 'Token expired';
      rerender(<VendorAnalyticsOptimized />);

      expect(screen.getByText('Error de autenticación')).toBeInTheDocument();

      // Disconnected
      mockWebSocketService.isConnected = false;
      mockWebSocketService.authError = null;
      rerender(<VendorAnalyticsOptimized />);

      expect(screen.getByText('Desconectado')).toBeInTheDocument();
    });

    it('should display live region for screen reader announcements', async () => {
      render(<VendorAnalyticsOptimized />);

      const liveRegion = screen.getByLabelText('analytics-announcements') ||
                        document.getElementById('analytics-announcements');

      expect(liveRegion).toBeInTheDocument();
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveAttribute('aria-atomic', 'false');
    });
  });

  describe('⚡ Performance Metrics Display', () => {
    it('should display load time in green when under 1000ms', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 850,
        chartRenderTime: 150,
        isOptimal: true
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const loadTime = screen.getByText('850 milisegundos');
        expect(loadTime).toBeInTheDocument();
        expect(loadTime).toHaveClass('text-green-600');
      });
    });

    it('should display load time in red when over 1000ms', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 1200,
        chartRenderTime: 150,
        isOptimal: false
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const loadTime = screen.getByText('1200 milisegundos');
        expect(loadTime).toBeInTheDocument();
        expect(loadTime).toHaveClass('text-red-600');
      });
    });

    it('should display render time in green when under 500ms', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 850,
        chartRenderTime: 350,
        isOptimal: true
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const renderTime = screen.getByText('350 milisegundos');
        expect(renderTime).toBeInTheDocument();
        expect(renderTime).toHaveClass('text-green-600');
      });
    });

    it('should display render time in red when over 500ms', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 850,
        chartRenderTime: 750,
        isOptimal: false
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const renderTime = screen.getByText('750 milisegundos');
        expect(renderTime).toBeInTheDocument();
        expect(renderTime).toHaveClass('text-red-600');
      });
    });

    it('should display optimal status in green', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 450,
        chartRenderTime: 120,
        isOptimal: true
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const status = screen.getByText('Óptimo');
        expect(status).toBeInTheDocument();
        expect(status).toHaveClass('text-green-600');
      });
    });

    it('should display non-optimal status in yellow', async () => {
      const analyticsStore = require('../../../stores/analyticsStore');
      jest.mocked(analyticsStore.usePerformanceMetrics).mockReturnValue({
        loadTime: 1200,
        chartRenderTime: 800,
        isOptimal: false
      });

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        const status = screen.getByText('Mejorable');
        expect(status).toBeInTheDocument();
        expect(status).toHaveClass('text-yellow-600');
      });
    });
  });

  describe('🎯 Accessibility & User Experience', () => {
    it('should have proper ARIA labels for status indicators', async () => {
      render(<VendorAnalyticsOptimized />);

      const statusSection = screen.getByLabelText('Estado del sistema');
      expect(statusSection).toBeInTheDocument();
      expect(statusSection).toHaveAttribute('role', 'status');
    });

    it('should provide screen reader context for connection status', async () => {
      mockWebSocketService.isConnected = true;

      render(<VendorAnalyticsOptimized />);

      await waitFor(() => {
        // Status should be announced properly
        expect(screen.getByText('Tiempo real activo')).toBeInTheDocument();
      });
    });

    it('should handle focus management for reconnect button', async () => {
      mockWebSocketService.authError = 'Connection failed';

      render(<VendorAnalyticsOptimized />);

      const reconnectButton = await screen.findByText('Reconectar');

      reconnectButton.focus();
      expect(reconnectButton).toHaveFocus();
    });

    it('should maintain accessibility during WebSocket state changes', async () => {
      const { rerender } = render(<VendorAnalyticsOptimized />);

      // Verify initial accessibility
      expect(screen.getByLabelText('Estado del sistema')).toBeInTheDocument();

      // Change state and verify accessibility is maintained
      mockWebSocketService.isConnected = true;
      rerender(<VendorAnalyticsOptimized />);

      expect(screen.getByLabelText('Estado del sistema')).toBeInTheDocument();
    });
  });
});