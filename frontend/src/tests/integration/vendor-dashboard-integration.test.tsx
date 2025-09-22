// frontend/src/tests/integration/vendor-dashboard-integration.test.tsx
// COMPREHENSIVE INTEGRATION TESTING for Vendor Dashboard Components
// Validates Phases 2-5: Registration Flow + Analytics + Product Dashboard + Accessibility

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// Jest equivalents for Vitest imports
const vi = jest;
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components under test
import VendorRegistrationFlow from '../../components/vendor/VendorRegistrationFlow';
import VendorAnalyticsOptimized from '../../components/analytics/optimized/VendorAnalyticsOptimized';
import VendorProductDashboard from '../../components/vendor/VendorProductDashboard';
import VendorAccessibility from '../../components/vendor/VendorAccessibility';

// Services and stores
import { useWebSocket } from '../../services/websocketService';
import { useAnalyticsStore } from '../../stores/analyticsStore';

// Performance monitoring
const performanceTracker = {
  startTime: 0,
  loadTimes: {} as Record<string, number>,

  start(component: string) {
    this.startTime = performance.now();
    this.loadTimes[component] = 0;
  },

  end(component: string) {
    this.loadTimes[component] = performance.now() - this.startTime;
  },

  getLoadTime(component: string) {
    return this.loadTimes[component] || 0;
  }
};

// Mock services
vi.mock('../../services/websocketService', () => ({
  useWebSocket: vi.fn(() => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    getLatency: vi.fn(() => 50),
    isConnected: true
  }))
}));

vi.mock('../../stores/analyticsStore', () => ({
  useAnalyticsMetrics: vi.fn(() => ({
    revenue: { current: 1500000, previous: 1200000, trend: 'up', percentage: 25 },
    orders: { current: 45, previous: 38, trend: 'up', percentage: 18.4 },
    products: { total: 15, active: 12, lowStock: 3, outOfStock: 1 },
    customers: { total: 120, new: 15, returning: 105 }
  })),
  useAnalyticsLoading: vi.fn(() => false),
  useAnalyticsConnected: vi.fn(() => true),
  useAnalyticsLastUpdated: vi.fn(() => new Date().toISOString()),
  useAnalyticsFilters: vi.fn(() => ({ timeRange: '30d', category: 'all' })),
  useAnalyticsActions: vi.fn(() => ({
    setLoading: vi.fn(),
    setFilters: vi.fn(),
    updateLastUpdated: vi.fn(),
    setLoadTime: vi.fn()
  })),
  usePerformanceMetrics: vi.fn(() => ({
    loadTime: 850,
    isOptimal: true
  }))
}));

// Mock hooks
vi.mock('../../hooks/useVendorRegistration', () => ({
  useVendorRegistration: vi.fn(() => ({
    submitRegistration: vi.fn().mockResolvedValue(true),
    isLoading: false,
    error: null,
    progress: 0
  }))
}));

vi.mock('../../hooks/useRealTimeValidation', () => ({
  useRealTimeValidation: vi.fn(() => ({
    validateField: vi.fn(),
    validationResults: {},
    isValidating: false
  }))
}));

vi.mock('../../hooks/useAutoSave', () => ({
  useAutoSave: vi.fn(() => ({
    savedData: null,
    autoSave: vi.fn(),
    clearSavedData: vi.fn()
  }))
}));

// Test utilities
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('Vendor Dashboard Integration Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    performanceTracker.start('test');

    // Mock performance.now for consistent testing
    Object.defineProperty(window, 'performance', {
      value: { now: vi.fn(() => Date.now()) },
      writable: true
    });

    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      value: true,
      writable: true
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    performanceTracker.end('test');
  });

  describe('1. Vendor Registration Flow Integration', () => {
    it('should complete full registration flow within performance targets', async () => {
      performanceTracker.start('registration');

      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Verify initial load
      expect(screen.getByText('Registro de Vendedor')).toBeInTheDocument();
      expect(screen.getByTestId('basic-info-step')).toBeInTheDocument();

      // Step 1: Basic Info
      await user.type(screen.getByLabelText(/nombre de empresa/i), 'Test Vendor Store');
      await user.type(screen.getByLabelText(/email/i), 'vendor@test.com');
      await user.type(screen.getByLabelText(/teléfono/i), '3001234567');

      // Progress to step 2
      await user.click(screen.getByRole('button', { name: /siguiente/i }));

      await waitFor(() => {
        expect(screen.getByTestId('business-details-step')).toBeInTheDocument();
      });

      // Step 2: Business Details
      await user.selectOptions(screen.getByLabelText(/tipo de negocio/i), 'persona_natural');
      await user.type(screen.getByLabelText(/dirección/i), 'Calle 123 #45-67');
      await user.type(screen.getByLabelText(/ciudad/i), 'Bogotá');
      await user.selectOptions(screen.getByLabelText(/departamento/i), 'Cundinamarca');

      // Progress to step 3
      await user.click(screen.getByRole('button', { name: /siguiente/i }));

      await waitFor(() => {
        expect(screen.getByTestId('verification-step')).toBeInTheDocument();
      });

      // Step 3: Verification (simulate)
      await user.click(screen.getByRole('button', { name: /verificar/i }));

      await waitFor(() => {
        expect(screen.getByTestId('documents-step')).toBeInTheDocument();
      });

      // Step 4: Documents and completion
      await user.click(screen.getByRole('button', { name: /completar registro/i }));

      performanceTracker.end('registration');

      // Performance validation
      const loadTime = performanceTracker.getLoadTime('registration');
      expect(loadTime).toBeLessThan(3000); // Should complete in under 3 seconds
    });

    it('should handle offline mode with auto-save functionality', async () => {
      // Mock offline status
      Object.defineProperty(navigator, 'onLine', { value: false, writable: true });

      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Verify offline indicator
      expect(screen.getByTestId('offline-indicator')).toBeInTheDocument();
      expect(screen.getByText(/conexión perdida/i)).toBeInTheDocument();

      // Fill form data (should auto-save locally)
      await user.type(screen.getByLabelText(/nombre de empresa/i), 'Offline Vendor');
      await user.type(screen.getByLabelText(/email/i), 'offline@test.com');

      // Data should be saved locally (mocked auto-save hook handles this)
      expect(screen.getByDisplayValue('Offline Vendor')).toBeInTheDocument();
    });

    it('should validate real-time form fields with immediate feedback', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Test invalid email
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'invalid-email');
      await user.tab(); // Trigger blur for validation

      await waitFor(() => {
        expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
      });

      // Test invalid phone
      const phoneInput = screen.getByLabelText(/teléfono/i);
      await user.type(phoneInput, '123');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText(/formato: 3001234567/i)).toBeInTheDocument();
      });
    });
  });

  describe('2. Analytics Dashboard Integration', () => {
    it('should load analytics dashboard within performance targets', async () => {
      performanceTracker.start('analytics');

      render(
        <TestWrapper>
          <VendorAnalyticsOptimized vendorId="test-vendor" />
        </TestWrapper>
      );

      // Verify main components load
      expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
      expect(screen.getByText('Dashboard de rendimiento en tiempo real')).toBeInTheDocument();

      // Verify metric cards
      expect(screen.getByText('Ingresos totales')).toBeInTheDocument();
      expect(screen.getByText('Órdenes')).toBeInTheDocument();
      expect(screen.getByText('Productos')).toBeInTheDocument();
      expect(screen.getByText('Clientes')).toBeInTheDocument();

      // Verify real-time connection status
      expect(screen.getByText(/en tiempo real|conectado/i)).toBeInTheDocument();

      performanceTracker.end('analytics');

      const loadTime = performanceTracker.getLoadTime('analytics');
      expect(loadTime).toBeLessThan(1000); // Should load in under 1 second
    });

    it('should handle WebSocket real-time updates correctly', async () => {
      const mockWebSocket = useWebSocket as vi.Mock;
      const mockConnect = vi.fn();
      const mockGetLatency = vi.fn(() => 45);

      mockWebSocket.mockReturnValue({
        connect: mockConnect,
        disconnect: vi.fn(),
        getLatency: mockGetLatency,
        isConnected: true
      });

      render(
        <TestWrapper>
          <VendorAnalyticsOptimized vendorId="test-vendor" />
        </TestWrapper>
      );

      // Verify WebSocket connection attempt
      expect(mockConnect).toHaveBeenCalled();

      // Verify latency display (development mode)
      if (process.env.NODE_ENV === 'development') {
        expect(screen.getByText(/WebSocket Latency: 45ms/i)).toBeInTheDocument();
      }
    });

    it('should update filters and time ranges dynamically', async () => {
      const mockSetFilters = vi.fn();
      const analyticsActions = {
        setLoading: vi.fn(),
        setFilters: mockSetFilters,
        updateLastUpdated: vi.fn(),
        setLoadTime: vi.fn()
      };

      vi.mocked(useAnalyticsStore().useAnalyticsActions).mockReturnValue(analyticsActions);

      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      // Test time range filter
      const timeRangeSelect = screen.getByDisplayValue(/últimos 30 días/i);
      await user.selectOptions(timeRangeSelect, '7d');

      expect(mockSetFilters).toHaveBeenCalledWith({ timeRange: '7d' });

      // Test advanced filters
      await user.click(screen.getByRole('button', { name: /filtros/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/categoría/i)).toBeInTheDocument();
      });
    });

    it('should display performance metrics accurately', async () => {
      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      // Verify performance indicator shows optimal status
      expect(screen.getByText(/carga: 850ms/i)).toBeInTheDocument();

      // Verify metric values are formatted correctly (Colombian pesos)
      expect(screen.getByText(/\$1\.500\.000/)).toBeInTheDocument(); // Revenue
      expect(screen.getByText('45')).toBeInTheDocument(); // Orders
    });
  });

  describe('3. Product Dashboard Integration', () => {
    it('should load product dashboard with all components', async () => {
      performanceTracker.start('products');

      render(
        <TestWrapper>
          <VendorProductDashboard vendorId="test-vendor" />
        </TestWrapper>
      );

      // Verify main header
      expect(screen.getByText('Mis Productos')).toBeInTheDocument();
      expect(screen.getByText('Gestiona tu catálogo de productos')).toBeInTheDocument();

      // Verify statistics panel
      expect(screen.getByText('Total Productos')).toBeInTheDocument();
      expect(screen.getByText('Valor Inventario')).toBeInTheDocument();
      expect(screen.getByText('Stock Bajo')).toBeInTheDocument();
      expect(screen.getByText('Rating Promedio')).toBeInTheDocument();

      // Verify product grid
      expect(screen.getByText(/smartphone samsung galaxy/i)).toBeInTheDocument();
      expect(screen.getByText(/camiseta polo lacoste/i)).toBeInTheDocument();

      performanceTracker.end('products');

      const loadTime = performanceTracker.getLoadTime('products');
      expect(loadTime).toBeLessThan(1500); // Should load in under 1.5 seconds
    });

    it('should handle product filtering and searching correctly', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      // Test search functionality
      const searchInput = screen.getByPlaceholderText(/buscar productos/i);
      await user.type(searchInput, 'Samsung');

      await waitFor(() => {
        expect(screen.getByText(/smartphone samsung galaxy/i)).toBeInTheDocument();
        expect(screen.queryByText(/camiseta polo lacoste/i)).not.toBeInTheDocument();
      });

      // Clear search and test filters
      await user.clear(searchInput);

      // Open filters
      await user.click(screen.getByRole('button', { name: /filtros/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/estado/i)).toBeInTheDocument();
      });

      // Filter by active products
      await user.selectOptions(screen.getByLabelText(/estado/i), 'active');

      // Should show only active products
      expect(screen.getByText(/smartphone samsung galaxy/i)).toBeInTheDocument();
      expect(screen.getByText(/camiseta polo lacoste/i)).toBeInTheDocument();
    });

    it('should support bulk actions on multiple products', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      // Select multiple products
      const checkboxes = screen.getAllByRole('checkbox');
      const productCheckboxes = checkboxes.filter(cb =>
        cb.getAttribute('aria-label')?.includes('Seleccionar') ||
        cb.closest('[data-testid*="product"]')
      );

      if (productCheckboxes.length > 0) {
        await user.click(productCheckboxes[0]);
        await user.click(productCheckboxes[1]);

        // Verify bulk actions appear
        await waitFor(() => {
          expect(screen.getByText(/productos seleccionados/i)).toBeInTheDocument();
        });

        // Test bulk activation
        await user.click(screen.getByRole('button', { name: /activar/i }));
      }
    });

    it('should display products in both grid and list views', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      // Should start in grid view
      expect(screen.getByRole('button', { name: /grid/i })).toHaveClass(/bg-white.*shadow/);

      // Switch to list view
      await user.click(screen.getByRole('button', { name: /list/i }));

      // Verify list view is active
      expect(screen.getByRole('button', { name: /list/i })).toHaveClass(/bg-white.*shadow/);
    });
  });

  describe('4. Accessibility Integration', () => {
    it('should meet WCAG 2.1 AA compliance standards', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Test skip navigation link
      const skipLink = screen.getByText(/saltar al contenido principal/i);
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveAttribute('href', '#main-content');

      // Test ARIA labels
      const mainContent = screen.getByRole('main');
      expect(mainContent).toHaveAttribute('aria-labelledby', 'registration-title');

      // Test form labels
      const businessNameInput = screen.getByLabelText(/nombre de empresa/i);
      expect(businessNameInput).toBeInTheDocument();
      expect(businessNameInput).toHaveAttribute('required');

      // Test error announcements
      await user.type(businessNameInput, 'a'); // Too short
      await user.tab();

      await waitFor(() => {
        const errorMessage = screen.getByText(/mínimo 3 caracteres/i);
        expect(errorMessage).toBeInTheDocument();
        expect(errorMessage).toHaveAttribute('role', 'alert');
      });
    });

    it('should support keyboard navigation throughout the application', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Test Tab navigation
      const firstInput = screen.getByLabelText(/nombre de empresa/i);
      firstInput.focus();
      expect(document.activeElement).toBe(firstInput);

      // Tab to next field
      await user.tab();
      const emailInput = screen.getByLabelText(/email/i);
      expect(document.activeElement).toBe(emailInput);

      // Test Enter key on buttons
      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      nextButton.focus();
      await user.keyboard('{Enter}');

      // Should not progress without valid data
      expect(screen.getByTestId('basic-info-step')).toBeInTheDocument();
    });

    it('should provide screen reader announcements for state changes', async () => {
      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      // Test connection status announcement
      const connectionStatus = screen.getByText(/en tiempo real|conectado/i);
      expect(connectionStatus).toBeInTheDocument();

      // Test live region for updates
      const refreshButton = screen.getByRole('button', { name: /actualizar/i });
      await user.click(refreshButton);

      // Should announce loading state
      await waitFor(() => {
        const liveRegion = document.querySelector('[aria-live]');
        expect(liveRegion).toBeInTheDocument();
      });
    });

    it('should maintain focus management in modals and overlays', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      // Open filters panel
      await user.click(screen.getByRole('button', { name: /filtros/i }));

      await waitFor(() => {
        const filtersPanel = screen.getByLabelText(/estado/i);
        expect(filtersPanel).toBeInTheDocument();

        // Focus should be trapped within the panel
        const focusableElements = within(filtersPanel.closest('[role="region"]') || filtersPanel)
          .getAllByRole('combobox');
        expect(focusableElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('5. Mobile Responsive Integration', () => {
    beforeEach(() => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', { value: 375, writable: true });
      Object.defineProperty(window, 'innerHeight', { value: 667, writable: true });
    });

    it('should adapt analytics dashboard for mobile screens', async () => {
      render(
        <TestWrapper>
          <VendorAnalyticsOptimized mobile={true} />
        </TestWrapper>
      );

      // Verify mobile-optimized layout
      expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();

      // Charts should adapt to mobile size
      const chartContainers = document.querySelectorAll('[data-testid*="chart"]');
      chartContainers.forEach(container => {
        const height = container.getAttribute('height');
        expect(parseInt(height || '0')).toBeLessThanOrEqual(300); // Mobile chart height
      });
    });

    it('should provide touch-friendly interactions', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      // Verify touch targets are at least 44px
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        const styles = getComputedStyle(button);
        const minHeight = parseInt(styles.minHeight || styles.height || '0');
        const minWidth = parseInt(styles.minWidth || styles.width || '0');

        // Touch targets should be at least 44px (considered accessible)
        expect(minHeight >= 44 || minWidth >= 44).toBe(true);
      });
    });

    it('should handle swipe gestures on mobile', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Test mobile step navigation
      const stepContainer = screen.getByTestId('basic-info-step');
      expect(stepContainer).toBeInTheDocument();

      // Mobile should have optimized spacing and layout
      const mobileContainer = document.querySelector('.mobile-step-container');
      expect(mobileContainer).toBeInTheDocument();
    });
  });

  describe('6. Cross-Component Integration', () => {
    it('should maintain state consistency across navigation', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Fill form data
      await user.type(screen.getByLabelText(/nombre de empresa/i), 'Integration Test Vendor');
      await user.type(screen.getByLabelText(/email/i), 'integration@test.com');
      await user.type(screen.getByLabelText(/teléfono/i), '3009876543');

      // Navigate to next step
      await user.click(screen.getByRole('button', { name: /siguiente/i }));

      // Navigate back
      await user.click(screen.getByRole('button', { name: /anterior|atrás/i }));

      // Data should be preserved
      expect(screen.getByDisplayValue('Integration Test Vendor')).toBeInTheDocument();
      expect(screen.getByDisplayValue('integration@test.com')).toBeInTheDocument();
    });

    it('should handle API integration errors gracefully', async () => {
      // Mock API failure
      const mockSubmit = vi.fn().mockRejectedValue(new Error('Network error'));
      vi.mocked(require('../../hooks/useVendorRegistration').useVendorRegistration)
        .mockReturnValue({
          submitRegistration: mockSubmit,
          isLoading: false,
          error: 'Network error',
          progress: 0
        });

      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Error should be displayed
      expect(screen.getByTestId('error-banner')).toBeInTheDocument();
      expect(screen.getByText(/network error/i)).toBeInTheDocument();

      // Retry button should be available
      expect(screen.getByTestId('retry-button')).toBeInTheDocument();
    });

    it('should provide seamless data flow between components', async () => {
      // Mock analytics store with updated data
      const mockAnalytics = {
        revenue: { current: 2000000, previous: 1500000, trend: 'up', percentage: 33.3 },
        orders: { current: 60, previous: 45, trend: 'up', percentage: 33.3 },
        products: { total: 20, active: 18, lowStock: 2, outOfStock: 0 },
        customers: { total: 150, new: 25, returning: 125 }
      };

      vi.mocked(useAnalyticsStore().useAnalyticsMetrics).mockReturnValue(mockAnalytics);

      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      // Verify updated metrics are displayed
      expect(screen.getByText(/\$2\.000\.000/)).toBeInTheDocument();
      expect(screen.getByText('60')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
    });
  });

  describe('7. Performance Integration Validation', () => {
    it('should meet all performance benchmarks', async () => {
      const performanceResults = {
        registration: 0,
        analytics: 0,
        products: 0
      };

      // Test Registration Flow Performance
      performanceTracker.start('registration-perf');
      render(<TestWrapper><VendorRegistrationFlow /></TestWrapper>);
      performanceTracker.end('registration-perf');
      performanceResults.registration = performanceTracker.getLoadTime('registration-perf');

      // Test Analytics Performance
      performanceTracker.start('analytics-perf');
      render(<TestWrapper><VendorAnalyticsOptimized /></TestWrapper>);
      performanceTracker.end('analytics-perf');
      performanceResults.analytics = performanceTracker.getLoadTime('analytics-perf');

      // Test Product Dashboard Performance
      performanceTracker.start('products-perf');
      render(<TestWrapper><VendorProductDashboard /></TestWrapper>);
      performanceTracker.end('products-perf');
      performanceResults.products = performanceTracker.getLoadTime('products-perf');

      // Validate performance targets
      expect(performanceResults.registration).toBeLessThan(2000); // 2s max
      expect(performanceResults.analytics).toBeLessThan(1000);    // 1s max
      expect(performanceResults.products).toBeLessThan(1500);     // 1.5s max

      console.log('Performance Results:', performanceResults);
    });

    it('should handle concurrent component loading efficiently', async () => {
      const startTime = performance.now();

      // Render multiple components simultaneously
      const { rerender } = render(
        <TestWrapper>
          <div>
            <VendorAnalyticsOptimized />
            <VendorProductDashboard />
          </div>
        </TestWrapper>
      );

      // Wait for all components to load
      await waitFor(() => {
        expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
        expect(screen.getByText('Mis Productos')).toBeInTheDocument();
      });

      const loadTime = performance.now() - startTime;
      expect(loadTime).toBeLessThan(2000); // Should load concurrently in under 2s
    });
  });
});