/**
 * Enterprise Performance Monitor for Navigation System
 *
 * Advanced performance monitoring with Core Web Vitals tracking,
 * memory management, and real-time performance analytics.
 *
 * Features:
 * - Core Web Vitals (LCP, FID, CLS, FCP, TTI)
 * - Navigation performance tracking
 * - Memory leak detection
 * - Bundle size monitoring
 * - Real-time performance alerts
 * - Performance budgets enforcement
 *
 * @version 1.0.0
 * @author Frontend Performance AI
 */

import React, { useEffect, useRef, useCallback, useMemo } from 'react';

// Performance monitoring types
interface PerformanceMetrics {
  // Core Web Vitals
  largestContentfulPaint: number | null;
  firstInputDelay: number | null;
  cumulativeLayoutShift: number | null;
  firstContentfulPaint: number | null;
  timeToInteractive: number | null;

  // Navigation specific
  navigationTiming: {
    setActiveItem: number[];
    toggleCategory: number[];
    componentRender: number[];
  };

  // Memory metrics
  memoryUsage: {
    jsHeapSizeLimit: number;
    totalJSHeapSize: number;
    usedJSHeapSize: number;
  };

  // Bundle metrics
  bundleSize: {
    main: number;
    vendor: number;
    chunks: Record<string, number>;
  };

  // Performance scores
  scores: {
    overall: number;
    navigation: number;
    memory: number;
    bundle: number;
  };

  // Alerts
  alerts: PerformanceAlert[];
}

interface PerformanceAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  metric: string;
  value: number;
  threshold: number;
  message: string;
  timestamp: Date;
}

interface PerformanceBudget {
  // Core Web Vitals thresholds
  lcpThreshold: number;
  fidThreshold: number;
  clsThreshold: number;
  fcpThreshold: number;
  ttiThreshold: number;

  // Navigation thresholds
  navigationResponseThreshold: number;
  categoryToggleThreshold: number;
  renderThreshold: number;

  // Memory thresholds
  memoryThresholdMB: number;
  memoryLeakThresholdMB: number;

  // Bundle thresholds
  mainBundleThresholdKB: number;
  vendorBundleThresholdKB: number;
  chunkThresholdKB: number;
}

// Default performance budgets (enterprise targets)
const defaultBudget: PerformanceBudget = {
  lcpThreshold: 2500, // 2.5s
  fidThreshold: 100,  // 100ms
  clsThreshold: 0.1,  // 0.1
  fcpThreshold: 1800, // 1.8s
  ttiThreshold: 3800, // 3.8s

  navigationResponseThreshold: 100, // 100ms
  categoryToggleThreshold: 50,      // 50ms
  renderThreshold: 16,              // 16ms (60fps)

  memoryThresholdMB: 100,          // 100MB
  memoryLeakThresholdMB: 200,      // 200MB

  mainBundleThresholdKB: 2048,     // 2MB
  vendorBundleThresholdKB: 1024,   // 1MB
  chunkThresholdKB: 512            // 512KB
};

interface PerformanceMonitorProps {
  enabled?: boolean;
  budget?: Partial<PerformanceBudget>;
  onAlert?: (alert: PerformanceAlert) => void;
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
  reportInterval?: number;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  enabled = true,
  budget = {},
  onAlert,
  onMetricsUpdate,
  reportInterval = 5000 // 5 seconds
}) => {
  const metricsRef = useRef<PerformanceMetrics>({
    largestContentfulPaint: null,
    firstInputDelay: null,
    cumulativeLayoutShift: null,
    firstContentfulPaint: null,
    timeToInteractive: null,
    navigationTiming: {
      setActiveItem: [],
      toggleCategory: [],
      componentRender: []
    },
    memoryUsage: {
      jsHeapSizeLimit: 0,
      totalJSHeapSize: 0,
      usedJSHeapSize: 0
    },
    bundleSize: {
      main: 0,
      vendor: 0,
      chunks: {}
    },
    scores: {
      overall: 0,
      navigation: 0,
      memory: 0,
      bundle: 0
    },
    alerts: []
  });

  const activeBudget = useMemo(() => ({
    ...defaultBudget,
    ...budget
  }), [budget]);

  const observersRef = useRef<{
    lcp?: PerformanceObserver;
    fid?: PerformanceObserver;
    cls?: PerformanceObserver;
    memory?: PerformanceObserver;
  }>({});

  const intervalRef = useRef<NodeJS.Timeout>();

  /**
   * Create performance alert
   */
  const createAlert = useCallback((
    type: PerformanceAlert['type'],
    metric: string,
    value: number,
    threshold: number,
    message: string
  ): PerformanceAlert => ({
    id: `${metric}_${Date.now()}`,
    type,
    metric,
    value,
    threshold,
    message,
    timestamp: new Date()
  }), []);

  /**
   * Add alert to metrics and trigger callback
   */
  const addAlert = useCallback((alert: PerformanceAlert) => {
    metricsRef.current.alerts.push(alert);

    // Keep only last 50 alerts
    if (metricsRef.current.alerts.length > 50) {
      metricsRef.current.alerts = metricsRef.current.alerts.slice(-50);
    }

    if (onAlert) {
      onAlert(alert);
    }
  }, [onAlert]);

  /**
   * Core Web Vitals monitoring
   */
  const initializeCoreWebVitals = useCallback(() => {
    if (!enabled || typeof window === 'undefined') return;

    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;

        if (lastEntry) {
          const lcp = lastEntry.startTime;
          metricsRef.current.largestContentfulPaint = lcp;

          if (lcp > activeBudget.lcpThreshold) {
            addAlert(createAlert(
              'warning',
              'LCP',
              lcp,
              activeBudget.lcpThreshold,
              `LCP (${lcp.toFixed(0)}ms) exceeds threshold (${activeBudget.lcpThreshold}ms)`
            ));
          }
        }
      });

      try {
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        observersRef.current.lcp = lcpObserver;
      } catch (error) {
        console.warn('LCP observer not supported:', error);
      }

      // First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          const fid = entry.processingStart - entry.startTime;
          metricsRef.current.firstInputDelay = fid;

          if (fid > activeBudget.fidThreshold) {
            addAlert(createAlert(
              'warning',
              'FID',
              fid,
              activeBudget.fidThreshold,
              `FID (${fid.toFixed(0)}ms) exceeds threshold (${activeBudget.fidThreshold}ms)`
            ));
          }
        });
      });

      try {
        fidObserver.observe({ entryTypes: ['first-input'] });
        observersRef.current.fid = fidObserver;
      } catch (error) {
        console.warn('FID observer not supported:', error);
      }

      // Cumulative Layout Shift (CLS)
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            metricsRef.current.cumulativeLayoutShift = clsValue;

            if (clsValue > activeBudget.clsThreshold) {
              addAlert(createAlert(
                'warning',
                'CLS',
                clsValue,
                activeBudget.clsThreshold,
                `CLS (${clsValue.toFixed(3)}) exceeds threshold (${activeBudget.clsThreshold})`
              ));
            }
          }
        });
      });

      try {
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        observersRef.current.cls = clsObserver;
      } catch (error) {
        console.warn('CLS observer not supported:', error);
      }

      // First Contentful Paint (FCP) and TTI
      const paintObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.name === 'first-contentful-paint') {
            const fcp = entry.startTime;
            metricsRef.current.firstContentfulPaint = fcp;

            if (fcp > activeBudget.fcpThreshold) {
              addAlert(createAlert(
                'info',
                'FCP',
                fcp,
                activeBudget.fcpThreshold,
                `FCP (${fcp.toFixed(0)}ms) exceeds threshold (${activeBudget.fcpThreshold}ms)`
              ));
            }
          }
        });
      });

      try {
        paintObserver.observe({ entryTypes: ['paint'] });
      } catch (error) {
        console.warn('Paint observer not supported:', error);
      }
    }
  }, [enabled, activeBudget, addAlert, createAlert]);

  /**
   * Memory monitoring
   */
  const monitorMemoryUsage = useCallback(() => {
    if (!enabled || typeof window === 'undefined') return;

    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const memoryUsage = {
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
          totalJSHeapSize: memory.totalJSHeapSize,
          usedJSHeapSize: memory.usedJSHeapSize
        };

        metricsRef.current.memoryUsage = memoryUsage;

        const usedMB = memoryUsage.usedJSHeapSize / (1024 * 1024);
        const totalMB = memoryUsage.totalJSHeapSize / (1024 * 1024);

        if (usedMB > activeBudget.memoryThresholdMB) {
          addAlert(createAlert(
            'warning',
            'Memory',
            usedMB,
            activeBudget.memoryThresholdMB,
            `Memory usage (${usedMB.toFixed(1)}MB) exceeds threshold (${activeBudget.memoryThresholdMB}MB)`
          ));
        }

        if (totalMB > activeBudget.memoryLeakThresholdMB) {
          addAlert(createAlert(
            'error',
            'Memory Leak',
            totalMB,
            activeBudget.memoryLeakThresholdMB,
            `Potential memory leak detected: ${totalMB.toFixed(1)}MB total heap`
          ));
        }
      }
    };

    // Check memory usage every 10 seconds
    const memoryInterval = setInterval(checkMemory, 10000);
    checkMemory(); // Initial check

    return () => clearInterval(memoryInterval);
  }, [enabled, activeBudget, addAlert, createAlert]);

  /**
   * Bundle size monitoring
   */
  const monitorBundleSize = useCallback(() => {
    if (!enabled || typeof window === 'undefined') return;

    // Monitor resource loading
    const resourceObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: any) => {
        if (entry.initiatorType === 'script' && entry.transferSize) {
          const sizeMB = entry.transferSize / 1024; // Convert to KB

          // Categorize bundle chunks
          if (entry.name.includes('main')) {
            metricsRef.current.bundleSize.main = sizeMB;

            if (sizeMB > activeBudget.mainBundleThresholdKB) {
              addAlert(createAlert(
                'warning',
                'Main Bundle',
                sizeMB,
                activeBudget.mainBundleThresholdKB,
                `Main bundle (${sizeMB.toFixed(1)}KB) exceeds threshold (${activeBudget.mainBundleThresholdKB}KB)`
              ));
            }
          } else if (entry.name.includes('vendor')) {
            metricsRef.current.bundleSize.vendor = sizeMB;

            if (sizeMB > activeBudget.vendorBundleThresholdKB) {
              addAlert(createAlert(
                'info',
                'Vendor Bundle',
                sizeMB,
                activeBudget.vendorBundleThresholdKB,
                `Vendor bundle (${sizeMB.toFixed(1)}KB) exceeds threshold (${activeBudget.vendorBundleThresholdKB}KB)`
              ));
            }
          } else {
            // Other chunks
            const chunkName = entry.name.split('/').pop() || 'unknown';
            metricsRef.current.bundleSize.chunks[chunkName] = sizeMB;

            if (sizeMB > activeBudget.chunkThresholdKB) {
              addAlert(createAlert(
                'info',
                'Chunk Size',
                sizeMB,
                activeBudget.chunkThresholdKB,
                `Chunk ${chunkName} (${sizeMB.toFixed(1)}KB) exceeds threshold (${activeBudget.chunkThresholdKB}KB)`
              ));
            }
          }
        }
      });
    });

    try {
      resourceObserver.observe({ entryTypes: ['resource'] });
    } catch (error) {
      console.warn('Resource observer not supported:', error);
    }

    return () => resourceObserver.disconnect();
  }, [enabled, activeBudget, addAlert, createAlert]);

  /**
   * Calculate performance scores
   */
  const calculateScores = useCallback(() => {
    const metrics = metricsRef.current;
    let overallScore = 100;
    let navigationScore = 100;
    let memoryScore = 100;
    let bundleScore = 100;

    // Core Web Vitals scoring
    if (metrics.largestContentfulPaint !== null) {
      const lcpScore = Math.max(0, 100 - (metrics.largestContentfulPaint / activeBudget.lcpThreshold) * 50);
      overallScore = Math.min(overallScore, lcpScore);
    }

    if (metrics.firstInputDelay !== null) {
      const fidScore = Math.max(0, 100 - (metrics.firstInputDelay / activeBudget.fidThreshold) * 50);
      overallScore = Math.min(overallScore, fidScore);
      navigationScore = Math.min(navigationScore, fidScore);
    }

    if (metrics.cumulativeLayoutShift !== null) {
      const clsScore = Math.max(0, 100 - (metrics.cumulativeLayoutShift / activeBudget.clsThreshold) * 100);
      overallScore = Math.min(overallScore, clsScore);
    }

    // Navigation timing scoring
    const avgSetActiveItem = metrics.navigationTiming.setActiveItem.length > 0
      ? metrics.navigationTiming.setActiveItem.reduce((a, b) => a + b, 0) / metrics.navigationTiming.setActiveItem.length
      : 0;

    if (avgSetActiveItem > 0) {
      const navScore = Math.max(0, 100 - (avgSetActiveItem / activeBudget.navigationResponseThreshold) * 50);
      navigationScore = Math.min(navigationScore, navScore);
    }

    // Memory scoring
    if (metrics.memoryUsage.usedJSHeapSize > 0) {
      const usedMB = metrics.memoryUsage.usedJSHeapSize / (1024 * 1024);
      const memScore = Math.max(0, 100 - (usedMB / activeBudget.memoryThresholdMB) * 50);
      memoryScore = Math.min(memoryScore, memScore);
    }

    // Bundle scoring
    const totalBundleKB = metrics.bundleSize.main + metrics.bundleSize.vendor;
    if (totalBundleKB > 0) {
      const bundleThreshold = activeBudget.mainBundleThresholdKB + activeBudget.vendorBundleThresholdKB;
      const bundScore = Math.max(0, 100 - (totalBundleKB / bundleThreshold) * 50);
      bundleScore = Math.min(bundleScore, bundScore);
    }

    metrics.scores = {
      overall: Math.round(overallScore),
      navigation: Math.round(navigationScore),
      memory: Math.round(memoryScore),
      bundle: Math.round(bundleScore)
    };
  }, [activeBudget]);

  /**
   * Report metrics
   */
  const reportMetrics = useCallback(() => {
    calculateScores();

    if (onMetricsUpdate) {
      onMetricsUpdate({ ...metricsRef.current });
    }
  }, [calculateScores, onMetricsUpdate]);

  /**
   * Navigation performance tracking API
   */
  const trackNavigationPerformance = useCallback((operation: string, duration: number) => {
    const metrics = metricsRef.current.navigationTiming;

    switch (operation) {
      case 'setActiveItem':
        metrics.setActiveItem.push(duration);
        // Keep only last 10 measurements
        if (metrics.setActiveItem.length > 10) {
          metrics.setActiveItem = metrics.setActiveItem.slice(-10);
        }

        if (duration > activeBudget.navigationResponseThreshold) {
          addAlert(createAlert(
            'warning',
            'Navigation Response',
            duration,
            activeBudget.navigationResponseThreshold,
            `setActiveItem (${duration.toFixed(1)}ms) exceeds threshold (${activeBudget.navigationResponseThreshold}ms)`
          ));
        }
        break;

      case 'toggleCategory':
        metrics.toggleCategory.push(duration);
        if (metrics.toggleCategory.length > 10) {
          metrics.toggleCategory = metrics.toggleCategory.slice(-10);
        }

        if (duration > activeBudget.categoryToggleThreshold) {
          addAlert(createAlert(
            'warning',
            'Category Toggle',
            duration,
            activeBudget.categoryToggleThreshold,
            `toggleCategory (${duration.toFixed(1)}ms) exceeds threshold (${activeBudget.categoryToggleThreshold}ms)`
          ));
        }
        break;

      case 'componentRender':
        metrics.componentRender.push(duration);
        if (metrics.componentRender.length > 10) {
          metrics.componentRender = metrics.componentRender.slice(-10);
        }

        if (duration > activeBudget.renderThreshold) {
          addAlert(createAlert(
            'info',
            'Render Time',
            duration,
            activeBudget.renderThreshold,
            `Component render (${duration.toFixed(1)}ms) exceeds 60fps threshold (${activeBudget.renderThreshold}ms)`
          ));
        }
        break;
    }
  }, [activeBudget, addAlert, createAlert]);

  /**
   * Initialize monitoring
   */
  useEffect(() => {
    if (!enabled) return;

    initializeCoreWebVitals();
    const memoryCleanup = monitorMemoryUsage();
    const bundleCleanup = monitorBundleSize();

    // Start periodic reporting
    intervalRef.current = setInterval(reportMetrics, reportInterval);

    return () => {
      // Cleanup observers
      Object.values(observersRef.current).forEach(observer => {
        if (observer) {
          observer.disconnect();
        }
      });

      // Cleanup intervals
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      if (memoryCleanup) {
        memoryCleanup();
      }

      if (bundleCleanup) {
        bundleCleanup();
      }
    };
  }, [enabled, initializeCoreWebVitals, monitorMemoryUsage, monitorBundleSize, reportMetrics, reportInterval]);

  // Expose tracking API to global window for use by navigation components
  useEffect(() => {
    if (enabled && typeof window !== 'undefined') {
      (window as any).__navigationPerformanceTracker = trackNavigationPerformance;
    }

    return () => {
      if (typeof window !== 'undefined') {
        delete (window as any).__navigationPerformanceTracker;
      }
    };
  }, [enabled, trackNavigationPerformance]);

  // This component doesn't render anything, it just monitors performance
  return null;
};

/**
 * Performance monitoring hook for components
 */
export const usePerformanceMonitor = () => {
  const trackStart = useCallback((operation: string) => {
    return performance.now();
  }, []);

  const trackEnd = useCallback((operation: string, startTime: number) => {
    const endTime = performance.now();
    const duration = endTime - startTime;

    if (typeof window !== 'undefined' && (window as any).__navigationPerformanceTracker) {
      (window as any).__navigationPerformanceTracker(operation, duration);
    }

    return duration;
  }, []);

  const trackOperation = useCallback((operation: string, fn: () => void) => {
    const startTime = trackStart(operation);
    fn();
    return trackEnd(operation, startTime);
  }, [trackStart, trackEnd]);

  return {
    trackStart,
    trackEnd,
    trackOperation
  };
};

export default PerformanceMonitor;