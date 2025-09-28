import React, { useEffect, useState, useCallback, useMemo } from 'react';

// Interfaz para métricas de performance
export interface SidebarPerformanceMetrics {
  renderTime: number;
  categoryExpansionTime: number;
  iconLoadTime: number;
  memoryUsage: number;
  bundleImpact: number;
  timestamp: number;
}

// Interfaz para el hook de performance
export interface PerformanceHookResult {
  metrics: SidebarPerformanceMetrics | null;
  startMeasure: (name: string) => void;
  endMeasure: (name: string) => number;
  logMetrics: () => void;
}

// Hook para monitorear performance del sidebar
export const useSidebarPerformance = (): PerformanceHookResult => {
  const [metrics, setMetrics] = useState<SidebarPerformanceMetrics | null>(null);
  const [measurements, setMeasurements] = useState<Record<string, number>>({});

  // Función para iniciar medición
  const startMeasure = useCallback((name: string) => {
    if (typeof performance !== 'undefined') {
      performance.mark(`sidebar-${name}-start`);
    }
  }, []);

  // Función para finalizar medición
  const endMeasure = useCallback((name: string): number => {
    if (typeof performance !== 'undefined') {
      try {
        performance.mark(`sidebar-${name}-end`);
        performance.measure(
          `sidebar-${name}`,
          `sidebar-${name}-start`,
          `sidebar-${name}-end`
        );

        const measure = performance.getEntriesByName(`sidebar-${name}`)[0];
        const duration = measure?.duration || 0;

        setMeasurements(prev => ({
          ...prev,
          [name]: duration
        }));

        return duration;
      } catch (error) {
        console.warn(`Error measuring ${name}:`, error);
        return 0;
      }
    }
    return 0;
  }, []);

  // Función para obtener uso de memoria
  const getMemoryUsage = useCallback((): number => {
    if (typeof performance !== 'undefined' && 'memory' in performance) {
      const memory = (performance as any).memory;
      return memory?.usedJSHeapSize || 0;
    }
    return 0;
  }, []);

  // Función para actualizar métricas
  const updateMetrics = useCallback(() => {
    const newMetrics: SidebarPerformanceMetrics = {
      renderTime: measurements.render || 0,
      categoryExpansionTime: measurements.expansion || 0,
      iconLoadTime: measurements.iconLoad || 0,
      memoryUsage: getMemoryUsage(),
      bundleImpact: measurements.bundleLoad || 0,
      timestamp: Date.now()
    };

    setMetrics(newMetrics);
  }, [measurements, getMemoryUsage]);

  // Actualizar métricas cuando cambien las mediciones
  useEffect(() => {
    updateMetrics();
  }, [updateMetrics]);

  // Función para loggear métricas
  const logMetrics = useCallback(() => {
    if (metrics) {
      console.group('🚀 Sidebar Performance Metrics');
      console.log(`📊 Render Time: ${metrics.renderTime.toFixed(2)}ms`);
      console.log(`📈 Category Expansion: ${metrics.categoryExpansionTime.toFixed(2)}ms`);
      console.log(`🎨 Icon Load Time: ${metrics.iconLoadTime.toFixed(2)}ms`);
      console.log(`💾 Memory Usage: ${(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB`);
      console.log(`📦 Bundle Impact: ${metrics.bundleImpact.toFixed(2)}ms`);
      console.log(`⏰ Timestamp: ${new Date(metrics.timestamp).toISOString()}`);

      // Validar objetivos de performance
      const alerts = [];
      if (metrics.renderTime > 100) alerts.push(`⚠️ Render time (${metrics.renderTime.toFixed(2)}ms) exceeds target (100ms)`);
      if (metrics.categoryExpansionTime > 200) alerts.push(`⚠️ Category expansion (${metrics.categoryExpansionTime.toFixed(2)}ms) exceeds target (200ms)`);
      if (metrics.iconLoadTime > 50) alerts.push(`⚠️ Icon load time (${metrics.iconLoadTime.toFixed(2)}ms) exceeds target (50ms)`);

      if (alerts.length > 0) {
        console.group('🚨 Performance Alerts');
        alerts.forEach(alert => console.warn(alert));
        console.groupEnd();
      } else {
        console.log('✅ All performance targets met!');
      }

      console.groupEnd();
    }
  }, [metrics]);

  return {
    metrics,
    startMeasure,
    endMeasure,
    logMetrics
  };
};

// Componente HOC para monitorear performance
export interface WithPerformanceMonitoringProps {
  enablePerformanceMonitoring?: boolean;
  onMetricsUpdate?: (metrics: SidebarPerformanceMetrics) => void;
}

export function withSidebarPerformanceMonitoring<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  const ComponentWithPerformanceMonitoring: React.FC<P & WithPerformanceMonitoringProps> = ({
    enablePerformanceMonitoring = false,
    onMetricsUpdate,
    ...props
  }) => {
    const { metrics, startMeasure, endMeasure, logMetrics } = useSidebarPerformance();

    // Medir tiempo de render del componente
    useEffect(() => {
      if (enablePerformanceMonitoring) {
        startMeasure('render');

        // Simular finalización del render en el próximo frame
        const timeoutId = setTimeout(() => {
          endMeasure('render');
        }, 0);

        return () => clearTimeout(timeoutId);
      }
    }, [enablePerformanceMonitoring, startMeasure, endMeasure]);

    // Notificar cuando las métricas se actualicen
    useEffect(() => {
      if (enablePerformanceMonitoring && metrics && onMetricsUpdate) {
        onMetricsUpdate(metrics);
      }
    }, [metrics, onMetricsUpdate, enablePerformanceMonitoring]);

    // Loggear métricas en desarrollo
    useEffect(() => {
      if (enablePerformanceMonitoring && process.env.NODE_ENV === 'development' && metrics) {
        logMetrics();
      }
    }, [metrics, logMetrics, enablePerformanceMonitoring]);

    const enhancedProps = useMemo(() => ({
      ...props,
      performanceMonitor: enablePerformanceMonitoring ? {
        startMeasure,
        endMeasure,
        metrics
      } : undefined
    }), [props, enablePerformanceMonitoring, startMeasure, endMeasure, metrics]);

    return <WrappedComponent {...enhancedProps as P} />;
  };

  ComponentWithPerformanceMonitoring.displayName =
    `withSidebarPerformanceMonitoring(${WrappedComponent.displayName || WrappedComponent.name})`;

  return ComponentWithPerformanceMonitoring;
}

// Componente visual para mostrar métricas en desarrollo
export interface PerformanceDisplayProps {
  metrics: SidebarPerformanceMetrics | null;
  showDetails?: boolean;
}

export const SidebarPerformanceDisplay: React.FC<PerformanceDisplayProps> = ({
  metrics,
  showDetails = false
}) => {
  if (!metrics || process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-black bg-opacity-75 text-white p-3 rounded-lg text-xs font-mono z-50">
      <div className="font-bold mb-2">🚀 Sidebar Performance</div>
      <div>Render: {metrics.renderTime.toFixed(1)}ms</div>
      <div>Expand: {metrics.categoryExpansionTime.toFixed(1)}ms</div>
      <div>Icons: {metrics.iconLoadTime.toFixed(1)}ms</div>
      <div>Memory: {(metrics.memoryUsage / 1024 / 1024).toFixed(1)}MB</div>

      {showDetails && (
        <div className="mt-2 pt-2 border-t border-gray-600">
          <div>Bundle: {metrics.bundleImpact.toFixed(1)}ms</div>
          <div>Updated: {new Date(metrics.timestamp).toLocaleTimeString()}</div>
        </div>
      )}
    </div>
  );
};