/**
 * Memory Leak Prevention System
 *
 * Enterprise-grade memory management and leak prevention system for React navigation components.
 * Provides automated cleanup, memory monitoring, and leak detection.
 *
 * Features:
 * - Automatic cleanup of event listeners
 * - Memory leak detection
 * - WeakMap-based caching
 * - Reference tracking
 * - Garbage collection optimization
 * - Performance monitoring
 * - Development warnings
 *
 * @version 1.0.0
 * @author Frontend Performance AI
 */

import React, {
  useEffect,
  useRef,
  useCallback,
  useMemo,
  useState,
  createContext,
  useContext
} from 'react';

/**
 * Memory tracking configuration
 */
interface MemoryConfig {
  trackingEnabled: boolean;
  alertThresholdMB: number;
  leakDetectionIntervalMs: number;
  maxRetainedObjects: number;
  gcForceIntervalMs: number;
  developmentWarnings: boolean;
}

const DEFAULT_MEMORY_CONFIG: MemoryConfig = {
  trackingEnabled: true,
  alertThresholdMB: 50,
  leakDetectionIntervalMs: 30000, // 30 seconds
  maxRetainedObjects: 1000,
  gcForceIntervalMs: 300000, // 5 minutes
  developmentWarnings: true
};

/**
 * Memory metrics interface
 */
interface MemoryMetrics {
  jsHeapSizeLimit: number;
  totalJSHeapSize: number;
  usedJSHeapSize: number;
  timestamp: number;
  componentCount: number;
  eventListenerCount: number;
  timerCount: number;
  cacheSize: number;
}

/**
 * Memory leak detector
 */
class MemoryLeakDetector {
  private config: MemoryConfig;
  private metrics: MemoryMetrics[] = [];
  private componentRegistry = new WeakMap<object, string>();
  private eventListenerRegistry = new Map<string, Set<() => void>>();
  private timerRegistry = new Set<NodeJS.Timeout | number>();
  private cacheRegistry = new WeakMap<object, any>();
  private alertCallbacks = new Set<(alert: MemoryAlert) => void>();

  constructor(config: MemoryConfig = DEFAULT_MEMORY_CONFIG) {
    this.config = config;
    this.startMonitoring();
  }

  /**
   * Start memory monitoring
   */
  private startMonitoring(): void {
    if (!this.config.trackingEnabled || typeof window === 'undefined') return;

    // Memory measurement interval
    const measureInterval = setInterval(() => {
      this.measureMemoryUsage();
    }, this.config.leakDetectionIntervalMs);

    // Garbage collection hint interval (development only)
    const gcInterval = setInterval(() => {
      if (process.env.NODE_ENV === 'development' && 'gc' in window) {
        try {
          (window as any).gc();
        } catch (error) {
          // GC not available, ignore
        }
      }
    }, this.config.gcForceIntervalMs);

    // Cleanup on page unload
    const cleanup = () => {
      clearInterval(measureInterval);
      clearInterval(gcInterval);
      this.cleanup();
    };

    window.addEventListener('beforeunload', cleanup);
    window.addEventListener('pagehide', cleanup);
  }

  /**
   * Measure current memory usage
   */
  private measureMemoryUsage(): void {
    if (!('memory' in performance)) return;

    const memory = (performance as any).memory;
    const now = Date.now();

    const metrics: MemoryMetrics = {
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      totalJSHeapSize: memory.totalJSHeapSize,
      usedJSHeapSize: memory.usedJSHeapSize,
      timestamp: now,
      componentCount: this.getComponentCount(),
      eventListenerCount: this.getEventListenerCount(),
      timerCount: this.timerRegistry.size,
      cacheSize: this.getCacheSize()
    };

    this.metrics.push(metrics);

    // Keep only last 100 measurements
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }

    this.detectMemoryLeaks(metrics);
  }

  /**
   * Detect potential memory leaks
   */
  private detectMemoryLeaks(currentMetrics: MemoryMetrics): void {
    if (this.metrics.length < 10) return; // Need enough data points

    const usedMB = currentMetrics.usedJSHeapSize / (1024 * 1024);
    const totalMB = currentMetrics.totalJSHeapSize / (1024 * 1024);

    // Check for memory threshold breach
    if (usedMB > this.config.alertThresholdMB) {
      this.triggerAlert({
        type: 'memory_threshold',
        severity: 'warning',
        message: `Memory usage (${usedMB.toFixed(1)}MB) exceeds threshold (${this.config.alertThresholdMB}MB)`,
        metrics: currentMetrics
      });
    }

    // Check for memory growth trend
    const recentMetrics = this.metrics.slice(-10);
    const memoryGrowth = this.calculateMemoryGrowth(recentMetrics);

    if (memoryGrowth.isGrowing && memoryGrowth.rate > 1) {
      this.triggerAlert({
        type: 'memory_leak_suspected',
        severity: 'error',
        message: `Potential memory leak detected: ${memoryGrowth.rate.toFixed(2)}MB/min growth`,
        metrics: currentMetrics
      });
    }

    // Check for excessive object retention
    if (currentMetrics.componentCount > this.config.maxRetainedObjects) {
      this.triggerAlert({
        type: 'object_retention',
        severity: 'warning',
        message: `Excessive object retention: ${currentMetrics.componentCount} components`,
        metrics: currentMetrics
      });
    }

    // Check for timer leaks
    if (currentMetrics.timerCount > 50) {
      this.triggerAlert({
        type: 'timer_leak',
        severity: 'warning',
        message: `Potential timer leak: ${currentMetrics.timerCount} active timers`,
        metrics: currentMetrics
      });
    }
  }

  /**
   * Calculate memory growth rate
   */
  private calculateMemoryGrowth(metrics: MemoryMetrics[]): { isGrowing: boolean; rate: number } {
    if (metrics.length < 2) return { isGrowing: false, rate: 0 };

    const first = metrics[0];
    const last = metrics[metrics.length - 1];

    const timeDiffMinutes = (last.timestamp - first.timestamp) / (1000 * 60);
    const memoryDiffMB = (last.usedJSHeapSize - first.usedJSHeapSize) / (1024 * 1024);

    const rate = memoryDiffMB / timeDiffMinutes;
    const isGrowing = rate > 0.5; // Growing more than 0.5MB per minute

    return { isGrowing, rate };
  }

  /**
   * Register component for tracking
   */
  registerComponent(component: object, name: string): void {
    this.componentRegistry.set(component, name);

    if (this.config.developmentWarnings && process.env.NODE_ENV === 'development') {
      console.log(`[MemoryTracker] Registered component: ${name}`);
    }
  }

  /**
   * Register event listener for cleanup tracking
   */
  registerEventListener(componentId: string, cleanup: () => void): void {
    if (!this.eventListenerRegistry.has(componentId)) {
      this.eventListenerRegistry.set(componentId, new Set());
    }
    this.eventListenerRegistry.get(componentId)!.add(cleanup);
  }

  /**
   * Register timer for tracking
   */
  registerTimer(timer: NodeJS.Timeout | number): void {
    this.timerRegistry.add(timer);
  }

  /**
   * Unregister timer
   */
  unregisterTimer(timer: NodeJS.Timeout | number): void {
    this.timerRegistry.delete(timer);
  }

  /**
   * Add cache entry with automatic cleanup
   */
  addToCache<T>(key: object, value: T): void {
    this.cacheRegistry.set(key, value);
  }

  /**
   * Get from cache
   */
  getFromCache<T>(key: object): T | undefined {
    return this.cacheRegistry.get(key);
  }

  /**
   * Cleanup component resources
   */
  cleanupComponent(componentId: string): void {
    const listeners = this.eventListenerRegistry.get(componentId);
    if (listeners) {
      listeners.forEach(cleanup => {
        try {
          cleanup();
        } catch (error) {
          console.warn('[MemoryTracker] Error during cleanup:', error);
        }
      });
      this.eventListenerRegistry.delete(componentId);
    }
  }

  /**
   * Force cleanup of all resources
   */
  cleanup(): void {
    // Cleanup all event listeners
    this.eventListenerRegistry.forEach((listeners, componentId) => {
      this.cleanupComponent(componentId);
    });

    // Clear all timers
    this.timerRegistry.forEach(timer => {
      clearTimeout(timer as NodeJS.Timeout);
      clearInterval(timer as NodeJS.Timeout);
    });

    // Clear registries
    this.eventListenerRegistry.clear();
    this.timerRegistry.clear();
    this.metrics.length = 0;
  }

  /**
   * Get component count
   */
  private getComponentCount(): number {
    // WeakMap doesn't have size, so we estimate based on registrations
    return this.eventListenerRegistry.size;
  }

  /**
   * Get event listener count
   */
  private getEventListenerCount(): number {
    let count = 0;
    this.eventListenerRegistry.forEach(listeners => {
      count += listeners.size;
    });
    return count;
  }

  /**
   * Get cache size estimation
   */
  private getCacheSize(): number {
    // WeakMap doesn't have size, return 0 as placeholder
    return 0;
  }

  /**
   * Subscribe to memory alerts
   */
  onAlert(callback: (alert: MemoryAlert) => void): () => void {
    this.alertCallbacks.add(callback);
    return () => this.alertCallbacks.delete(callback);
  }

  /**
   * Trigger memory alert
   */
  private triggerAlert(alert: MemoryAlert): void {
    if (this.config.developmentWarnings && process.env.NODE_ENV === 'development') {
      console.warn('[MemoryTracker] Alert:', alert);
    }

    this.alertCallbacks.forEach(callback => {
      try {
        callback(alert);
      } catch (error) {
        console.error('[MemoryTracker] Error in alert callback:', error);
      }
    });
  }

  /**
   * Get current metrics
   */
  getMetrics(): MemoryMetrics | null {
    return this.metrics[this.metrics.length - 1] || null;
  }

  /**
   * Get metrics history
   */
  getMetricsHistory(): MemoryMetrics[] {
    return [...this.metrics];
  }
}

/**
 * Memory alert interface
 */
interface MemoryAlert {
  type: 'memory_threshold' | 'memory_leak_suspected' | 'object_retention' | 'timer_leak';
  severity: 'info' | 'warning' | 'error';
  message: string;
  metrics: MemoryMetrics;
}

// Global memory leak detector instance
let globalDetector: MemoryLeakDetector | null = null;

/**
 * Get or create global detector
 */
function getMemoryDetector(config?: Partial<MemoryConfig>): MemoryLeakDetector {
  if (!globalDetector) {
    globalDetector = new MemoryLeakDetector({
      ...DEFAULT_MEMORY_CONFIG,
      ...config
    });
  }
  return globalDetector;
}

/**
 * Memory context for sharing detector instance
 */
const MemoryContext = createContext<MemoryLeakDetector | null>(null);

/**
 * Memory provider component
 */
export const MemoryLeakPreventionProvider: React.FC<{
  children: React.ReactNode;
  config?: Partial<MemoryConfig>;
}> = ({ children, config }) => {
  const detector = useMemo(() => getMemoryDetector(config), [config]);

  return (
    <MemoryContext.Provider value={detector}>
      {children}
    </MemoryContext.Provider>
  );
};

/**
 * Hook for memory leak prevention
 */
export const useMemoryLeakPrevention = (componentName: string = 'unknown') => {
  const detector = useContext(MemoryContext) || getMemoryDetector();
  const componentIdRef = useRef(`${componentName}_${Date.now()}_${Math.random()}`);
  const cleanupFunctionsRef = useRef<Set<() => void>>(new Set());
  const timersRef = useRef<Set<NodeJS.Timeout | number>>(new Set());

  // Register component
  useEffect(() => {
    detector.registerComponent({}, componentIdRef.current);

    return () => {
      detector.cleanupComponent(componentIdRef.current);
    };
  }, [detector]);

  /**
   * Add event listener with automatic cleanup
   */
  const addEventListener = useCallback(<T extends Event>(
    target: EventTarget,
    event: string,
    handler: (event: T) => void,
    options?: AddEventListenerOptions
  ) => {
    const wrappedHandler = handler as EventListener;
    target.addEventListener(event, wrappedHandler, options);

    const cleanup = () => {
      target.removeEventListener(event, wrappedHandler, options);
    };

    cleanupFunctionsRef.current.add(cleanup);
    detector.registerEventListener(componentIdRef.current, cleanup);

    return cleanup;
  }, [detector]);

  /**
   * Set timeout with automatic cleanup
   */
  const setManagedTimeout = useCallback((
    callback: () => void,
    delay: number
  ): NodeJS.Timeout => {
    const timer = setTimeout(() => {
      callback();
      timersRef.current.delete(timer);
      detector.unregisterTimer(timer);
    }, delay);

    timersRef.current.add(timer);
    detector.registerTimer(timer);

    return timer;
  }, [detector]);

  /**
   * Set interval with automatic cleanup
   */
  const setManagedInterval = useCallback((
    callback: () => void,
    delay: number
  ): NodeJS.Timeout => {
    const timer = setInterval(callback, delay);

    timersRef.current.add(timer);
    detector.registerTimer(timer);

    return timer;
  }, [detector]);

  /**
   * Clear managed timer
   */
  const clearManagedTimer = useCallback((timer: NodeJS.Timeout | number) => {
    clearTimeout(timer as NodeJS.Timeout);
    clearInterval(timer as NodeJS.Timeout);
    timersRef.current.delete(timer);
    detector.unregisterTimer(timer);
  }, [detector]);

  /**
   * Add cleanup function
   */
  const addCleanup = useCallback((cleanup: () => void) => {
    cleanupFunctionsRef.current.add(cleanup);
    detector.registerEventListener(componentIdRef.current, cleanup);
  }, [detector]);

  /**
   * Manual cleanup
   */
  const cleanup = useCallback(() => {
    // Cleanup all registered functions
    cleanupFunctionsRef.current.forEach(cleanupFn => {
      try {
        cleanupFn();
      } catch (error) {
        console.warn('[MemoryLeakPrevention] Cleanup error:', error);
      }
    });

    // Clear all timers
    timersRef.current.forEach(timer => {
      clearManagedTimer(timer);
    });

    // Clear sets
    cleanupFunctionsRef.current.clear();
    timersRef.current.clear();
  }, [clearManagedTimer]);

  /**
   * Cleanup effect
   */
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    addEventListener,
    setManagedTimeout,
    setManagedInterval,
    clearManagedTimer,
    addCleanup,
    cleanup
  };
};

/**
 * Hook for memory monitoring
 */
export const useMemoryMonitoring = () => {
  const detector = useContext(MemoryContext) || getMemoryDetector();
  const [currentMetrics, setCurrentMetrics] = useState<MemoryMetrics | null>(null);
  const [alerts, setAlerts] = useState<MemoryAlert[]>([]);

  // Update metrics periodically
  useEffect(() => {
    const updateMetrics = () => {
      setCurrentMetrics(detector.getMetrics());
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [detector]);

  // Subscribe to alerts
  useEffect(() => {
    const unsubscribe = detector.onAlert((alert) => {
      setAlerts(prev => [...prev.slice(-9), alert]); // Keep last 10 alerts
    });

    return unsubscribe;
  }, [detector]);

  const getMetricsHistory = useCallback(() => {
    return detector.getMetricsHistory();
  }, [detector]);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  return {
    currentMetrics,
    alerts,
    getMetricsHistory,
    clearAlerts
  };
};

/**
 * Memory-optimized component wrapper
 */
export const withMemoryLeakPrevention = <P extends object>(
  Component: React.ComponentType<P>,
  componentName?: string
) => {
  const MemoryOptimizedComponent = React.memo((props: P) => {
    const { cleanup } = useMemoryLeakPrevention(componentName || Component.displayName || Component.name);

    useEffect(() => {
      return cleanup;
    }, [cleanup]);

    return <Component {...props} />;
  });

  MemoryOptimizedComponent.displayName = `withMemoryLeakPrevention(${componentName || Component.displayName || Component.name})`;

  return MemoryOptimizedComponent;
};

export default MemoryLeakPreventionProvider;