// frontend/src/utils/performanceMonitor.ts
// PERFORMANCE_MONITORING: Enterprise-grade performance monitoring system
// Target: FCP <1s, LCP <2.5s, FID <100ms, CLS <0.1, Bundle <500KB

export interface PerformanceMetrics {
  // Core Web Vitals
  fcp?: number; // First Contentful Paint
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
  ttfb?: number; // Time to First Byte

  // Custom Metrics
  componentRenderTime?: number;
  bundleSize?: number;
  memoryUsage?: number;
  apiResponseTime?: number;
  wsLatency?: number;

  // User Experience
  navigationTiming?: PerformanceNavigationTiming;
  resourceTiming?: PerformanceResourceTiming[];

  // Framework specific
  reactRenderTime?: number;
  stateUpdateTime?: number;

  timestamp: number;
  url: string;
  userAgent: string;
  connectionType?: string;
}

export interface PerformanceAlert {
  type: 'warning' | 'error' | 'info';
  metric: keyof PerformanceMetrics;
  value: number;
  threshold: number;
  message: string;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private alerts: PerformanceAlert[] = [];
  private observers: PerformanceObserver[] = [];
  private isEnabled = true;

  // Performance thresholds
  private thresholds = {
    fcp: 1000, // 1s
    lcp: 2500, // 2.5s
    fid: 100,  // 100ms
    cls: 0.1,  // 0.1
    ttfb: 500, // 500ms
    componentRenderTime: 16, // 60fps = 16.67ms per frame
    apiResponseTime: 200, // 200ms
    wsLatency: 150, // 150ms
    memoryUsage: 100 * 1024 * 1024, // 100MB
    bundleSize: 500 * 1024 // 500KB
  };

  private listeners: ((metrics: PerformanceMetrics) => void)[] = [];
  private alertListeners: ((alert: PerformanceAlert) => void)[] = [];

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    if (!this.isEnabled || typeof window === 'undefined') return;

    // Initialize Core Web Vitals monitoring
    this.initializeCoreWebVitals();

    // Initialize custom performance tracking
    this.initializeCustomMetrics();

    // Initialize resource monitoring
    this.initializeResourceMonitoring();

    // Start memory monitoring
    this.startMemoryMonitoring();

    // Monitor bundle size
    this.monitorBundleSize();
  }

  private initializeCoreWebVitals(): void {
    // FCP - First Contentful Paint
    if ('PerformanceObserver' in window) {
      const fcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.recordMetric('fcp', fcpEntry.startTime);
        }
      });
      fcpObserver.observe({ entryTypes: ['paint'] });
      this.observers.push(fcpObserver);

      // LCP - Largest Contentful Paint
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        if (lastEntry) {
          this.recordMetric('lcp', lastEntry.startTime);
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);

      // FID - First Input Delay
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.processingStart && entry.startTime) {
            const fid = entry.processingStart - entry.startTime;
            this.recordMetric('fid', fid);
          }
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);

      // CLS - Cumulative Layout Shift
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            this.recordMetric('cls', clsValue);
          }
        });
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(clsObserver);
    }
  }

  private initializeCustomMetrics(): void {
    // Monitor navigation timing
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        this.recordMetric('ttfb', navigation.responseStart - navigation.requestStart);

        this.updateMetrics({
          navigationTiming: navigation,
          timestamp: Date.now(),
          url: window.location.href,
          userAgent: navigator.userAgent,
          connectionType: (navigator as any).connection?.effectiveType
        });
      }
    });
  }

  private initializeResourceMonitoring(): void {
    if ('PerformanceObserver' in window) {
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries() as PerformanceResourceTiming[];

        // Monitor API response times
        entries.forEach(entry => {
          if (entry.name.includes('/api/')) {
            const responseTime = entry.responseEnd - entry.requestStart;
            this.recordMetric('apiResponseTime', responseTime);
          }
        });

        this.updateMetrics({
          resourceTiming: entries,
          timestamp: Date.now(),
          url: window.location.href,
          userAgent: navigator.userAgent
        });
      });

      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    }
  }

  private startMemoryMonitoring(): void {
    // Monitor memory usage every 30 seconds
    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        this.recordMetric('memoryUsage', memory.usedJSHeapSize);
      }
    };

    checkMemory();
    setInterval(checkMemory, 30000);
  }

  private monitorBundleSize(): void {
    // Estimate bundle size from initial resources
    window.addEventListener('load', () => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const jsResources = resources.filter(resource =>
        resource.name.endsWith('.js') || resource.name.includes('chunk')
      );

      const totalSize = jsResources.reduce((total, resource) => {
        return total + (resource.transferSize || 0);
      }, 0);

      this.recordMetric('bundleSize', totalSize);
    });
  }

  // Public methods
  public recordMetric(metric: keyof PerformanceMetrics, value: number): void {
    if (!this.isEnabled) return;

    // Check against thresholds
    const threshold = this.thresholds[metric];
    if (threshold && value > threshold) {
      this.createAlert('warning', metric, value, threshold);
    }

    this.updateMetrics({
      [metric]: value,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    });
  }

  public recordComponentRenderTime(componentName: string, renderTime: number): void {
    this.recordMetric('componentRenderTime', renderTime);

    if (renderTime > this.thresholds.componentRenderTime) {
      this.createAlert(
        'warning',
        'componentRenderTime',
        renderTime,
        this.thresholds.componentRenderTime,
        `Component ${componentName} rendered slowly`
      );
    }
  }

  public recordWebSocketLatency(latency: number): void {
    this.recordMetric('wsLatency', latency);
  }

  public recordReactRenderTime(renderTime: number): void {
    this.recordMetric('reactRenderTime', renderTime);
  }

  public recordStateUpdateTime(updateTime: number): void {
    this.recordMetric('stateUpdateTime', updateTime);
  }

  private updateMetrics(newMetrics: Partial<PerformanceMetrics>): void {
    const metrics: PerformanceMetrics = {
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      ...newMetrics
    };

    this.metrics.push(metrics);

    // Keep only last 100 entries
    if (this.metrics.length > 100) {
      this.metrics.shift();
    }

    // Notify listeners
    this.listeners.forEach(listener => listener(metrics));
  }

  private createAlert(
    type: PerformanceAlert['type'],
    metric: keyof PerformanceMetrics,
    value: number,
    threshold: number,
    customMessage?: string
  ): void {
    const alert: PerformanceAlert = {
      type,
      metric,
      value,
      threshold,
      message: customMessage || `${metric} exceeded threshold: ${value.toFixed(2)} > ${threshold}`,
      timestamp: Date.now()
    };

    this.alerts.push(alert);

    // Keep only last 50 alerts
    if (this.alerts.length > 50) {
      this.alerts.shift();
    }

    // Notify alert listeners
    this.alertListeners.forEach(listener => listener(alert));

    // Console logging for development
    if (process.env.NODE_ENV === 'development') {
      console.warn(`Performance Alert [${type}]:`, alert.message);
    }
  }

  // Getters
  public getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  public getLatestMetrics(): PerformanceMetrics | null {
    return this.metrics[this.metrics.length - 1] || null;
  }

  public getAlerts(): PerformanceAlert[] {
    return [...this.alerts];
  }

  public getAverages(): Partial<PerformanceMetrics> {
    if (this.metrics.length === 0) return {};

    const averages: any = {};
    const numericKeys: (keyof PerformanceMetrics)[] = [
      'fcp', 'lcp', 'fid', 'cls', 'ttfb',
      'componentRenderTime', 'bundleSize', 'memoryUsage',
      'apiResponseTime', 'wsLatency', 'reactRenderTime', 'stateUpdateTime'
    ];

    numericKeys.forEach(key => {
      const values = this.metrics
        .map(m => m[key])
        .filter((value): value is number => typeof value === 'number');

      if (values.length > 0) {
        averages[key] = values.reduce((sum, val) => sum + val, 0) / values.length;
      }
    });

    return averages;
  }

  public isPerformanceOptimal(): boolean {
    const latest = this.getLatestMetrics();
    if (!latest) return false;

    return (
      (latest.fcp || 0) <= this.thresholds.fcp &&
      (latest.lcp || 0) <= this.thresholds.lcp &&
      (latest.fid || 0) <= this.thresholds.fid &&
      (latest.cls || 0) <= this.thresholds.cls &&
      (latest.memoryUsage || 0) <= this.thresholds.memoryUsage
    );
  }

  // Event listeners
  public onMetricsUpdate(callback: (metrics: PerformanceMetrics) => void): () => void {
    this.listeners.push(callback);
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  public onAlert(callback: (alert: PerformanceAlert) => void): () => void {
    this.alertListeners.push(callback);
    return () => {
      const index = this.alertListeners.indexOf(callback);
      if (index > -1) {
        this.alertListeners.splice(index, 1);
      }
    };
  }

  // Control methods
  public enable(): void {
    this.isEnabled = true;
    this.initialize();
  }

  public disable(): void {
    this.isEnabled = false;
    this.cleanup();
  }

  public cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.listeners = [];
    this.alertListeners = [];
  }

  // Export data
  public exportMetrics(): string {
    return JSON.stringify({
      metrics: this.metrics,
      alerts: this.alerts,
      averages: this.getAverages(),
      thresholds: this.thresholds,
      exportTimestamp: Date.now()
    }, null, 2);
  }
}

// React hook for performance monitoring
export const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = React.useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = React.useState<PerformanceAlert[]>([]);

  React.useEffect(() => {
    const unsubscribeMetrics = performanceMonitor.onMetricsUpdate(setMetrics);
    const unsubscribeAlerts = performanceMonitor.onAlert((alert) => {
      setAlerts(prev => [...prev.slice(-9), alert]); // Keep last 10 alerts
    });

    return () => {
      unsubscribeMetrics();
      unsubscribeAlerts();
    };
  }, []);

  return {
    metrics,
    alerts,
    averages: performanceMonitor.getAverages(),
    isOptimal: performanceMonitor.isPerformanceOptimal(),
    recordMetric: performanceMonitor.recordMetric.bind(performanceMonitor),
    recordComponentRenderTime: performanceMonitor.recordComponentRenderTime.bind(performanceMonitor),
    exportMetrics: performanceMonitor.exportMetrics.bind(performanceMonitor)
  };
};

// Higher-order component for automatic render time monitoring
export const withPerformanceMonitoring = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
) => {
  const name = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component';

  const MonitoredComponent = React.memo((props: P) => {
    const renderStartTime = React.useMemo(() => performance.now(), []);

    React.useLayoutEffect(() => {
      const renderTime = performance.now() - renderStartTime;
      performanceMonitor.recordComponentRenderTime(name, renderTime);
    });

    return <WrappedComponent {...props} />;
  });

  MonitoredComponent.displayName = `withPerformanceMonitoring(${name})`;
  return MonitoredComponent;
};

// Global instance
export const performanceMonitor = new PerformanceMonitor();

// Auto-start monitoring in browser environment
if (typeof window !== 'undefined') {
  performanceMonitor.enable();
}

export default performanceMonitor;