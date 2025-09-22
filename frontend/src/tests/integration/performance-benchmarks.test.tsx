// frontend/src/tests/integration/performance-benchmarks.test.tsx
// PERFORMANCE BENCHMARKING & OPTIMIZATION VALIDATION
// Tests <1s load time requirements and performance metrics

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// Jest equivalents for Vitest imports
const vi = jest;
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components under test
import VendorRegistrationFlow from '../../components/vendor/VendorRegistrationFlow';
import VendorAnalyticsOptimized from '../../components/analytics/optimized/VendorAnalyticsOptimized';
import VendorProductDashboard from '../../components/vendor/VendorProductDashboard';

// Performance monitoring utilities
class PerformanceProfiler {
  private metrics: Map<string, number[]> = new Map();
  private currentMeasurements: Map<string, number> = new Map();
  private memoryUsage: Map<string, any[]> = new Map();

  start(metricName: string) {
    this.currentMeasurements.set(metricName, performance.now());
  }

  end(metricName: string): number {
    const startTime = this.currentMeasurements.get(metricName);
    if (!startTime) {
      throw new Error(`No start time found for metric: ${metricName}`);
    }

    const duration = performance.now() - startTime;

    if (!this.metrics.has(metricName)) {
      this.metrics.set(metricName, []);
    }

    this.metrics.get(metricName)!.push(duration);
    this.currentMeasurements.delete(metricName);

    return duration;
  }

  getAverage(metricName: string): number {
    const measurements = this.metrics.get(metricName) || [];
    return measurements.reduce((sum, val) => sum + val, 0) / measurements.length;
  }

  getPercentile(metricName: string, percentile: number): number {
    const measurements = this.metrics.get(metricName) || [];
    const sorted = [...measurements].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index] || 0;
  }

  getMin(metricName: string): number {
    const measurements = this.metrics.get(metricName) || [];
    return Math.min(...measurements);
  }

  getMax(metricName: string): number {
    const measurements = this.metrics.get(metricName) || [];
    return Math.max(...measurements);
  }

  measureMemory(metricName: string) {
    if ('memory' in performance) {
      const memInfo = (performance as any).memory;
      if (!this.memoryUsage.has(metricName)) {
        this.memoryUsage.set(metricName, []);
      }
      this.memoryUsage.get(metricName)!.push({
        used: memInfo.usedJSHeapSize,
        total: memInfo.totalJSHeapSize,
        limit: memInfo.jsHeapSizeLimit,
        timestamp: Date.now()
      });
    }
  }

  getMemoryDelta(metricName: string): number {
    const measurements = this.memoryUsage.get(metricName) || [];
    if (measurements.length < 2) return 0;

    const first = measurements[0];
    const last = measurements[measurements.length - 1];
    return last.used - first.used;
  }

  reset() {
    this.metrics.clear();
    this.currentMeasurements.clear();
    this.memoryUsage.clear();
  }

  getReport(): Record<string, any> {
    const report: Record<string, any> = {};

    for (const [metricName, measurements] of this.metrics.entries()) {
      report[metricName] = {
        count: measurements.length,
        average: this.getAverage(metricName),
        min: this.getMin(metricName),
        max: this.getMax(metricName),
        p50: this.getPercentile(metricName, 50),
        p90: this.getPercentile(metricName, 90),
        p95: this.getPercentile(metricName, 95),
        p99: this.getPercentile(metricName, 99)
      };
    }

    for (const [metricName] of this.memoryUsage.entries()) {
      const memoryDelta = this.getMemoryDelta(metricName);
      report[`${metricName}_memory`] = {
        delta: memoryDelta,
        deltaFormatted: `${(memoryDelta / 1024 / 1024).toFixed(2)} MB`
      };
    }

    return report;
  }
}

// Mock heavy components for performance testing
const HeavyComponent: React.FC<{ itemCount: number }> = ({ itemCount }) => {
  const items = Array.from({ length: itemCount }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    description: `Description for item ${i}`.repeat(10)
  }));

  return (
    <div data-testid="heavy-component">
      {items.map(item => (
        <div key={item.id} className="complex-item">
          <h3>{item.name}</h3>
          <p>{item.description}</p>
          <button onClick={() => console.log(item.id)}>Action</button>
        </div>
      ))}
    </div>
  );
};

// Mock services with performance tracking
vi.mock('../../services/websocketService', () => ({
  useWebSocket: vi.fn(() => ({
    connect: vi.fn().mockResolvedValue(true),
    disconnect: vi.fn(),
    getLatency: vi.fn(() => 45),
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

// Mock hooks with performance tracking
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

// Test wrapper with performance tracking
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

describe('Performance Benchmarks & Optimization Validation', () => {
  let profiler: PerformanceProfiler;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    profiler = new PerformanceProfiler();
    user = userEvent.setup();

    // Mock performance.now for consistent testing
    vi.spyOn(performance, 'now').mockImplementation(() => Date.now());

    // Mock requestAnimationFrame for smooth animations
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      setTimeout(cb, 16); // ~60fps
      return 1;
    });
  });

  afterEach(() => {
    profiler.reset();
    vi.restoreAllMocks();
  });

  describe('1. Component Load Time Benchmarks', () => {
    it('should load VendorRegistrationFlow within 1 second', async () => {
      const iterations = 10;

      for (let i = 0; i < iterations; i++) {
        profiler.start('vendor-registration-load');
        profiler.measureMemory('vendor-registration');

        const { unmount } = render(
          <TestWrapper>
            <VendorRegistrationFlow />
          </TestWrapper>
        );

        // Wait for component to be fully rendered
        await waitFor(() => {
          expect(screen.getByText('Registro de Vendedor')).toBeInTheDocument();
        });

        const loadTime = profiler.end('vendor-registration-load');
        profiler.measureMemory('vendor-registration');

        unmount();

        // Individual load should be under 1 second
        expect(loadTime).toBeLessThan(1000);
      }

      const avgLoadTime = profiler.getAverage('vendor-registration-load');
      const p95LoadTime = profiler.getPercentile('vendor-registration-load', 95);

      expect(avgLoadTime).toBeLessThan(800); // Average under 800ms
      expect(p95LoadTime).toBeLessThan(1000); // 95th percentile under 1s

      console.log('VendorRegistrationFlow Performance:', {
        average: `${avgLoadTime.toFixed(2)}ms`,
        p95: `${p95LoadTime.toFixed(2)}ms`,
        memoryDelta: profiler.getMemoryDelta('vendor-registration')
      });
    });

    it('should load VendorAnalyticsOptimized within 1 second', async () => {
      const iterations = 10;

      for (let i = 0; i < iterations; i++) {
        profiler.start('analytics-load');
        profiler.measureMemory('analytics');

        const { unmount } = render(
          <TestWrapper>
            <VendorAnalyticsOptimized vendorId="test-vendor" />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
        });

        const loadTime = profiler.end('analytics-load');
        profiler.measureMemory('analytics');

        unmount();

        expect(loadTime).toBeLessThan(1000);
      }

      const avgLoadTime = profiler.getAverage('analytics-load');
      const p95LoadTime = profiler.getPercentile('analytics-load', 95);

      expect(avgLoadTime).toBeLessThan(600); // Average under 600ms
      expect(p95LoadTime).toBeLessThan(1000); // 95th percentile under 1s

      console.log('VendorAnalyticsOptimized Performance:', {
        average: `${avgLoadTime.toFixed(2)}ms`,
        p95: `${p95LoadTime.toFixed(2)}ms`,
        memoryDelta: profiler.getMemoryDelta('analytics')
      });
    });

    it('should load VendorProductDashboard within 1.5 seconds', async () => {
      const iterations = 10;

      for (let i = 0; i < iterations; i++) {
        profiler.start('product-dashboard-load');
        profiler.measureMemory('product-dashboard');

        const { unmount } = render(
          <TestWrapper>
            <VendorProductDashboard vendorId="test-vendor" />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText('Mis Productos')).toBeInTheDocument();
        });

        const loadTime = profiler.end('product-dashboard-load');
        profiler.measureMemory('product-dashboard');

        unmount();

        expect(loadTime).toBeLessThan(1500);
      }

      const avgLoadTime = profiler.getAverage('product-dashboard-load');
      const p95LoadTime = profiler.getPercentile('product-dashboard-load', 95);

      expect(avgLoadTime).toBeLessThan(1000); // Average under 1s
      expect(p95LoadTime).toBeLessThan(1500); // 95th percentile under 1.5s

      console.log('VendorProductDashboard Performance:', {
        average: `${avgLoadTime.toFixed(2)}ms`,
        p95: `${p95LoadTime.toFixed(2)}ms`,
        memoryDelta: profiler.getMemoryDelta('product-dashboard')
      });
    });
  });

  describe('2. Interaction Response Time Benchmarks', () => {
    it('should respond to form interactions within 100ms', async () => {
      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      const input = screen.getByLabelText(/nombre de empresa/i);

      for (let i = 0; i < 20; i++) {
        profiler.start('form-interaction');

        await user.type(input, 'a');
        await user.clear(input);

        const responseTime = profiler.end('form-interaction');
        expect(responseTime).toBeLessThan(100);
      }

      const avgResponseTime = profiler.getAverage('form-interaction');
      expect(avgResponseTime).toBeLessThan(50); // Average under 50ms

      console.log('Form Interaction Performance:', {
        average: `${avgResponseTime.toFixed(2)}ms`,
        p95: `${profiler.getPercentile('form-interaction', 95).toFixed(2)}ms`
      });
    });

    it('should respond to filter changes within 200ms', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/buscar productos/i);

      for (let i = 0; i < 10; i++) {
        profiler.start('filter-interaction');

        await user.type(searchInput, 'test query');
        await user.clear(searchInput);

        const responseTime = profiler.end('filter-interaction');
        expect(responseTime).toBeLessThan(200);
      }

      const avgResponseTime = profiler.getAverage('filter-interaction');
      expect(avgResponseTime).toBeLessThan(100); // Average under 100ms

      console.log('Filter Interaction Performance:', {
        average: `${avgResponseTime.toFixed(2)}ms`,
        p95: `${profiler.getPercentile('filter-interaction', 95).toFixed(2)}ms`
      });
    });

    it('should handle rapid analytics updates within 50ms', async () => {
      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      const refreshButton = screen.getByRole('button', { name: /actualizar/i });

      for (let i = 0; i < 15; i++) {
        profiler.start('analytics-update');

        await user.click(refreshButton);

        // Wait for update to complete
        await waitFor(() => {
          expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
        });

        const updateTime = profiler.end('analytics-update');
        expect(updateTime).toBeLessThan(100);
      }

      const avgUpdateTime = profiler.getAverage('analytics-update');
      expect(avgUpdateTime).toBeLessThan(50); // Average under 50ms

      console.log('Analytics Update Performance:', {
        average: `${avgUpdateTime.toFixed(2)}ms`,
        p95: `${profiler.getPercentile('analytics-update', 95).toFixed(2)}ms`
      });
    });
  });

  describe('3. Memory Usage and Leak Detection', () => {
    it('should not leak memory during component mounting/unmounting', async () => {
      const iterations = 20;

      for (let i = 0; i < iterations; i++) {
        profiler.measureMemory('memory-leak-test');

        const { unmount } = render(
          <TestWrapper>
            <VendorAnalyticsOptimized />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
        });

        unmount();

        // Force garbage collection if available
        if (global.gc) {
          global.gc();
        }

        profiler.measureMemory('memory-leak-test');
      }

      const memoryDelta = profiler.getMemoryDelta('memory-leak-test');

      // Memory usage should not grow significantly
      expect(memoryDelta).toBeLessThan(5 * 1024 * 1024); // Less than 5MB increase

      console.log('Memory Usage:', {
        delta: `${(memoryDelta / 1024 / 1024).toFixed(2)} MB`,
        perIteration: `${(memoryDelta / iterations / 1024).toFixed(2)} KB`
      });
    });

    it('should handle large datasets efficiently', async () => {
      const itemCounts = [100, 500, 1000, 2000];

      for (const itemCount of itemCounts) {
        profiler.start(`large-dataset-${itemCount}`);
        profiler.measureMemory(`large-dataset-${itemCount}`);

        const { unmount } = render(<HeavyComponent itemCount={itemCount} />);

        await waitFor(() => {
          expect(screen.getByTestId('heavy-component')).toBeInTheDocument();
        });

        const renderTime = profiler.end(`large-dataset-${itemCount}`);
        profiler.measureMemory(`large-dataset-${itemCount}`);

        unmount();

        // Render time should scale reasonably
        expect(renderTime).toBeLessThan(itemCount * 2); // Max 2ms per item

        console.log(`Dataset ${itemCount} items:`, {
          renderTime: `${renderTime.toFixed(2)}ms`,
          memoryDelta: `${(profiler.getMemoryDelta(`large-dataset-${itemCount}`) / 1024 / 1024).toFixed(2)} MB`
        });
      }
    });
  });

  describe('4. Bundle Size and Loading Performance', () => {
    it('should lazy load components efficiently', async () => {
      // Simulate code splitting and lazy loading
      const LazyComponent = React.lazy(() =>
        new Promise(resolve => {
          setTimeout(() => {
            resolve({ default: VendorAnalyticsOptimized });
          }, 100); // Simulate network delay
        })
      );

      profiler.start('lazy-load');

      render(
        <TestWrapper>
          <React.Suspense fallback={<div>Loading...</div>}>
            <LazyComponent />
          </React.Suspense>
        </TestWrapper>
      );

      // Should show loading state first
      expect(screen.getByText('Loading...')).toBeInTheDocument();

      // Wait for lazy component to load
      await waitFor(() => {
        expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();
      });

      const loadTime = profiler.end('lazy-load');

      // Should handle lazy loading efficiently
      expect(loadTime).toBeLessThan(500);

      console.log('Lazy Loading Performance:', {
        loadTime: `${loadTime.toFixed(2)}ms`
      });
    });

    it('should minimize re-renders with React.memo', async () => {
      let renderCount = 0;

      const MemoizedComponent = React.memo(() => {
        renderCount++;
        return <div data-testid="memoized">Memoized Component</div>;
      });

      const ParentComponent: React.FC<{ value: number }> = ({ value }) => (
        <div>
          <div>Value: {value}</div>
          <MemoizedComponent />
        </div>
      );

      const { rerender } = render(<ParentComponent value={1} />);

      expect(renderCount).toBe(1);

      // Re-render with same props - should not re-render memoized component
      rerender(<ParentComponent value={1} />);
      expect(renderCount).toBe(1);

      // Re-render with different props - should not re-render memoized component
      rerender(<ParentComponent value={2} />);
      expect(renderCount).toBe(1);

      console.log('Memoization Performance:', {
        renderCount,
        expectedRenders: 1
      });
    });
  });

  describe('5. Animation and Transition Performance', () => {
    it('should maintain 60fps during animations', async () => {
      const frameTimings: number[] = [];
      let lastFrameTime = performance.now();

      // Mock requestAnimationFrame to track frame timing
      vi.spyOn(window, 'requestAnimationFrame').mockImplementation(callback => {
        const currentTime = performance.now();
        frameTimings.push(currentTime - lastFrameTime);
        lastFrameTime = currentTime;

        setTimeout(() => callback(currentTime), 16); // 60fps
        return 1;
      });

      render(
        <TestWrapper>
          <VendorRegistrationFlow />
        </TestWrapper>
      );

      // Trigger step transition animation
      const nextButton = screen.getByRole('button', { name: /siguiente/i });

      // Fill required fields first
      await user.type(screen.getByLabelText(/nombre de empresa/i), 'Test Company');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/teléfono/i), '3001234567');

      profiler.start('animation-performance');
      await user.click(nextButton);

      // Wait for animation to complete
      await waitFor(() => {
        expect(screen.getByTestId('business-details-step')).toBeInTheDocument();
      });

      const animationTime = profiler.end('animation-performance');

      // Animation should complete quickly
      expect(animationTime).toBeLessThan(500);

      // Check frame consistency (should be close to 16.67ms for 60fps)
      const avgFrameTime = frameTimings.reduce((sum, time) => sum + time, 0) / frameTimings.length;
      expect(avgFrameTime).toBeLessThan(20); // Allow some variance from perfect 16.67ms

      console.log('Animation Performance:', {
        animationTime: `${animationTime.toFixed(2)}ms`,
        avgFrameTime: `${avgFrameTime.toFixed(2)}ms`,
        targetFrameTime: '16.67ms (60fps)'
      });
    });
  });

  describe('6. Concurrent Operations Performance', () => {
    it('should handle multiple simultaneous operations efficiently', async () => {
      render(
        <TestWrapper>
          <VendorProductDashboard />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/buscar productos/i);
      const filtersButton = screen.getByRole('button', { name: /filtros/i });

      profiler.start('concurrent-operations');

      // Perform multiple operations simultaneously
      const operations = [
        user.type(searchInput, 'concurrent test'),
        user.click(filtersButton),
        user.click(screen.getByRole('button', { name: /actualizar/i }))
      ];

      await Promise.all(operations);

      const operationTime = profiler.end('concurrent-operations');

      // Multiple operations should complete efficiently
      expect(operationTime).toBeLessThan(1000);

      console.log('Concurrent Operations Performance:', {
        operationTime: `${operationTime.toFixed(2)}ms`,
        operationsCount: operations.length
      });
    });
  });

  describe('7. Network Performance Simulation', () => {
    it('should handle slow API responses gracefully', async () => {
      // Mock slow API responses
      const slowFetch = vi.fn().mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ data: 'slow response' })
        }), 2000))
      );

      global.fetch = slowFetch;

      profiler.start('slow-api-handling');

      render(
        <TestWrapper>
          <VendorAnalyticsOptimized />
        </TestWrapper>
      );

      // Component should render immediately with loading states
      expect(screen.getByText('Analytics Optimizado')).toBeInTheDocument();

      const initialRenderTime = profiler.end('slow-api-handling');

      // Initial render should not be blocked by API calls
      expect(initialRenderTime).toBeLessThan(500);

      console.log('Slow API Handling Performance:', {
        initialRenderTime: `${initialRenderTime.toFixed(2)}ms`,
        apiResponseTime: '2000ms (simulated)'
      });
    });
  });

  describe('8. Final Performance Report', () => {
    it('should generate comprehensive performance report', () => {
      const report = profiler.getReport();

      // Validate all key metrics are within targets
      const performanceTargets = {
        'vendor-registration-load': { max: 1000, target: 800 },
        'analytics-load': { max: 1000, target: 600 },
        'product-dashboard-load': { max: 1500, target: 1000 },
        'form-interaction': { max: 100, target: 50 },
        'filter-interaction': { max: 200, target: 100 },
        'analytics-update': { max: 100, target: 50 }
      };

      const performanceResults: Record<string, any> = {};

      for (const [metric, targets] of Object.entries(performanceTargets)) {
        const metricData = report[metric];
        if (metricData) {
          const passed = metricData.p95 <= targets.max;
          const optimal = metricData.average <= targets.target;

          performanceResults[metric] = {
            average: `${metricData.average.toFixed(2)}ms`,
            p95: `${metricData.p95.toFixed(2)}ms`,
            target: `${targets.target}ms`,
            max: `${targets.max}ms`,
            passed,
            optimal,
            status: optimal ? '✅ OPTIMAL' : passed ? '⚠️ ACCEPTABLE' : '❌ FAILED'
          };

          expect(metricData.p95).toBeLessThanOrEqual(targets.max);
        }
      }

      console.log('\n📊 FINAL PERFORMANCE REPORT 📊');
      console.log('='.repeat(50));
      console.table(performanceResults);

      // Overall performance score
      const totalMetrics = Object.keys(performanceTargets).length;
      const passedMetrics = Object.values(performanceResults).filter(r => r.passed).length;
      const optimalMetrics = Object.values(performanceResults).filter(r => r.optimal).length;

      const performanceScore = {
        passed: `${passedMetrics}/${totalMetrics} (${(passedMetrics/totalMetrics*100).toFixed(1)}%)`,
        optimal: `${optimalMetrics}/${totalMetrics} (${(optimalMetrics/totalMetrics*100).toFixed(1)}%)`,
        overallGrade: optimalMetrics === totalMetrics ? 'A+' :
                     passedMetrics === totalMetrics ? 'A' :
                     passedMetrics/totalMetrics >= 0.8 ? 'B' : 'C'
      };

      console.log('\n🎯 PERFORMANCE SCORE 🎯');
      console.log('='.repeat(30));
      console.table([performanceScore]);

      // Assert minimum performance standards
      expect(passedMetrics).toBe(totalMetrics); // All metrics must pass
      expect(optimalMetrics / totalMetrics).toBeGreaterThanOrEqual(0.7); // 70% should be optimal
    });
  });
});