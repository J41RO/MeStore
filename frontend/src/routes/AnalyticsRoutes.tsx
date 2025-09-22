// frontend/src/routes/AnalyticsRoutes.tsx
// PERFORMANCE_OPTIMIZED: Code-split analytics routes for optimal loading

import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load analytics components for code splitting
const VendorAnalyticsOptimized = React.lazy(() =>
  import('../components/vendor/VendorAnalyticsOptimized').then(module => ({
    default: module.VendorAnalyticsOptimized
  }))
);

const VendorProductDashboard = React.lazy(() =>
  import('../components/vendor/VendorProductDashboard')
);

const AnalyticsExport = React.lazy(() =>
  import('../components/analytics/AnalyticsExport')
);

const DrillDownAnalytics = React.lazy(() =>
  import('../components/analytics/DrillDownAnalytics')
);

// Loading skeleton for analytics components
const AnalyticsLoadingSkeleton = React.memo(() => (
  <div className="animate-pulse space-y-6 p-6">
    {/* Header skeleton */}
    <div className="flex items-center justify-between">
      <div>
        <div className="h-8 bg-neutral-200 rounded w-48 mb-2"></div>
        <div className="h-4 bg-neutral-200 rounded w-64"></div>
      </div>
      <div className="flex gap-3">
        <div className="h-10 bg-neutral-200 rounded w-32"></div>
        <div className="h-10 bg-neutral-200 rounded w-24"></div>
        <div className="h-10 bg-neutral-200 rounded w-24"></div>
      </div>
    </div>

    {/* Metrics cards skeleton */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-4">
            <div className="h-12 bg-neutral-200 rounded w-12"></div>
            <div className="h-6 bg-neutral-200 rounded w-16"></div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-neutral-200 rounded w-24"></div>
            <div className="h-8 bg-neutral-200 rounded w-32"></div>
            <div className="h-3 bg-neutral-200 rounded w-28"></div>
          </div>
        </div>
      ))}
    </div>

    {/* Charts skeleton */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {[...Array(2)].map((_, i) => (
        <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="h-6 bg-neutral-200 rounded w-48 mb-6"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, j) => (
              <div key={j} className="flex items-center gap-3">
                <div className="h-2 bg-neutral-200 rounded w-8"></div>
                <div className="flex-1 bg-neutral-200 rounded h-2"></div>
                <div className="h-2 bg-neutral-200 rounded w-16"></div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>

    {/* Performance indicator */}
    <div className="text-center">
      <div className="inline-flex items-center gap-2 text-xs text-neutral-400">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
        Cargando analytics optimizados...
      </div>
    </div>
  </div>
));

AnalyticsLoadingSkeleton.displayName = 'AnalyticsLoadingSkeleton';

// Error boundary for analytics routes
class AnalyticsErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Analytics component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-96 p-6">
          <div className="text-center max-w-md">
            <div className="text-red-500 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 19c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Error en Analytics
            </h3>
            <p className="text-sm text-neutral-600 mb-4">
              Hubo un problema cargando el dashboard de analytics. Por favor, recarga la página.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              Recargar página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Main analytics routes component with performance optimizations
export const AnalyticsRoutes: React.FC = React.memo(() => {
  return (
    <AnalyticsErrorBoundary>
      <Suspense fallback={<AnalyticsLoadingSkeleton />}>
        <Routes>
          {/* Main analytics dashboard */}
          <Route
            path="/"
            element={<VendorAnalyticsOptimized />}
          />

          {/* Product analytics */}
          <Route
            path="/products"
            element={
              <Suspense fallback={<AnalyticsLoadingSkeleton />}>
                <VendorProductDashboard />
              </Suspense>
            }
          />

          {/* Export functionality */}
          <Route
            path="/export"
            element={
              <Suspense fallback={<AnalyticsLoadingSkeleton />}>
                <AnalyticsExport />
              </Suspense>
            }
          />

          {/* Drill-down analytics */}
          <Route
            path="/drilldown/:metric"
            element={
              <Suspense fallback={<AnalyticsLoadingSkeleton />}>
                <DrillDownAnalytics />
              </Suspense>
            }
          />
        </Routes>
      </Suspense>
    </AnalyticsErrorBoundary>
  );
});

AnalyticsRoutes.displayName = 'AnalyticsRoutes';

// Preload analytics components on hover for faster navigation
export const useAnalyticsPreload = () => {
  const preloadAnalytics = React.useCallback(() => {
    // Preload main analytics component
    import('../components/vendor/VendorAnalyticsOptimized');
  }, []);

  const preloadProductDashboard = React.useCallback(() => {
    // Preload product dashboard component
    import('../components/vendor/VendorProductDashboard');
  }, []);

  const preloadExport = React.useCallback(() => {
    // Preload export component
    import('../components/analytics/AnalyticsExport');
  }, []);

  return {
    preloadAnalytics,
    preloadProductDashboard,
    preloadExport
  };
};

export default AnalyticsRoutes;