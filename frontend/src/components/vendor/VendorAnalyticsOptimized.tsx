// frontend/src/components/vendor/VendorAnalyticsOptimized.tsx
// PERFORMANCE_OPTIMIZED: Optimized analytics component for <1s load time
// Target: FCP <1s, LCP <2.5s, FID <100ms, CLS <0.1

import React, { useState, useMemo, useCallback, useEffect, lazy, Suspense, useRef } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  ShoppingCart,
  Users,
  ArrowUp,
  ArrowDown,
  Minus,
  RefreshCw,
  Download,
  AlertTriangle,
  Target,
  Zap
} from 'lucide-react';
import {
  useAnalyticsMetrics,
  useAnalyticsActions,
  useAnalyticsLoading,
  useAnalyticsLastUpdated,
  useAnalyticsFilters,
  useFilteredTrends,
  useFilteredProducts,
  useFilteredCategories,
  useTotalRevenue,
  useGrowthRate,
  usePerformanceMetrics,
  useAnalyticsConnected
} from '../../stores/analyticsStore';
import { useWebSocket } from '../../services/websocketService';
import { screenReader, focusManagement, aria, reducedMotion } from '../../utils/accessibility';

// Lazy load accessible chart components
const LazyAccessibleBarChart = lazy(() =>
  import('./charts/AccessibleBarChart').then(module => ({ default: module.AccessibleBarChart }))
);
const LazyAccessiblePieChart = lazy(() =>
  import('./charts/AccessiblePieChart').then(module => ({ default: module.AccessiblePieChart }))
);
const LazyTopProductsList = lazy(() =>
  import('./components/TopProductsList').then(module => ({ default: module.TopProductsList }))
);

interface VendorAnalyticsOptimizedProps {
  className?: string;
  vendorId?: string;
}

type TimeRange = '7d' | '30d' | '90d' | '1y';

// Memoized currency formatter
const formatCOP = (() => {
  const formatter = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
  return (amount: number) => formatter.format(amount);
})();

// Memoized compact number formatter
const formatCompact = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

// Memoized trend indicator component
const TrendIndicator = React.memo<{
  trend: 'up' | 'down' | 'stable';
  percentage: number
}>(({ trend, percentage }) => {
  const Icon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus;
  const colorClass = trend === 'up' ? 'text-secondary-600' : trend === 'down' ? 'text-red-600' : 'text-neutral-500';
  const bgClass = trend === 'up' ? 'bg-secondary-100' : trend === 'down' ? 'bg-red-100' : 'bg-neutral-100';

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClass} ${bgClass}`}>
      <Icon className="w-3 h-3 mr-1" />
      {percentage.toFixed(1)}%
    </span>
  );
});

TrendIndicator.displayName = 'TrendIndicator';

// Memoized metric card component
const MetricCard = React.memo<{
  title: string;
  value: string | number;
  previousValue?: string | number;
  trend?: 'up' | 'down' | 'stable';
  percentage?: number;
  icon: React.ReactNode;
  iconBg: string;
  badge?: React.ReactNode;
}>(({ title, value, previousValue, trend, percentage, icon, iconBg, badge }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg ${iconBg}`}>
          {icon}
        </div>
        {trend && percentage !== undefined && (
          <TrendIndicator trend={trend} percentage={percentage} />
        )}
        {badge}
      </div>
      <div>
        <p className="text-sm font-medium text-neutral-500 mb-1">{title}</p>
        <p className="text-2xl font-bold text-neutral-900">{value}</p>
        {previousValue && (
          <p className="text-sm text-neutral-600 mt-1">
            vs. {previousValue} anterior
          </p>
        )}
      </div>
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

// Chart loading skeleton
const ChartSkeleton = React.memo(() => (
  <div className="animate-pulse">
    <div className="h-4 bg-neutral-200 rounded w-1/4 mb-4"></div>
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="h-2 bg-neutral-200 rounded w-8"></div>
          <div className="flex-1 bg-neutral-200 rounded h-2"></div>
          <div className="h-2 bg-neutral-200 rounded w-16"></div>
        </div>
      ))}
    </div>
  </div>
));

ChartSkeleton.displayName = 'ChartSkeleton';

// Main optimized component
export const VendorAnalyticsOptimized: React.FC<VendorAnalyticsOptimizedProps> = React.memo(({
  className = '',
  vendorId = 'default-vendor'
}) => {
  // Performance tracking
  const performanceStartTime = useMemo(() => performance.now(), []);
  const mainRef = useRef<HTMLDivElement>(null);
  const [announcements, setAnnouncements] = useState<string[]>([]);

  // Store hooks with fine-grained subscriptions
  const metrics = useAnalyticsMetrics();
  const isLoading = useAnalyticsLoading();
  const lastUpdated = useAnalyticsLastUpdated();
  const filters = useAnalyticsFilters();
  const filteredTrends = useFilteredTrends();
  const filteredProducts = useFilteredProducts();
  const filteredCategories = useFilteredCategories();
  const totalRevenue = useTotalRevenue();
  const growthRate = useGrowthRate();
  const performanceMetrics = usePerformanceMetrics();
  const isConnected = useAnalyticsConnected();

  // WebSocket connection for real-time updates
  const {
    isConnected: wsConnected,
    authError,
    connect: wsConnect,
    disconnect: wsDisconnect,
    getLatency,
    getConnectionState
  } = useWebSocket(vendorId);

  // Actions
  const {
    setFilters,
    setLoading,
    setLoadTime,
    setChartRenderTime,
    setMetrics,
    setTopProducts,
    setSalesByCategory,
    setMonthlyTrends
  } = useAnalyticsActions();

  // Local state
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Announce changes to screen readers
  const announceChange = useCallback((message: string) => {
    screenReader.announce(message, 'polite');
    setAnnouncements(prev => [...prev.slice(-4), message]); // Keep last 5 announcements
  }, []);

  // Memoized formatted values
  const formattedRevenue = useMemo(() =>
    metrics ? formatCOP(metrics.revenue.current) : '',
    [metrics?.revenue.current]
  );

  const formattedPreviousRevenue = useMemo(() =>
    metrics ? formatCOP(metrics.revenue.previous) : '',
    [metrics?.revenue.previous]
  );

  // Mock data for initial load (would be replaced with API call)
  const MOCK_METRICS = useMemo(() => ({
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
  }), []);

  const MOCK_TOP_PRODUCTS = useMemo(() => [
    {
      id: '1',
      name: 'Smartphone Samsung Galaxy A54',
      sales: 23,
      revenue: 2050000,
      image: '/api/placeholder/60/60',
      trend: 'up' as const
    },
    {
      id: '2',
      name: 'Auriculares Bluetooth Sony',
      sales: 18,
      revenue: 1440000,
      image: '/api/placeholder/60/60',
      trend: 'up' as const
    },
    {
      id: '3',
      name: 'Camiseta Polo Lacoste',
      sales: 15,
      revenue: 945000,
      image: '/api/placeholder/60/60',
      trend: 'stable' as const
    }
  ], []);

  const MOCK_CATEGORIES = useMemo(() => [
    { category: 'Electrónicos', sales: 45, revenue: 6750000, color: '#3b82f6', percentage: 36 },
    { category: 'Ropa', sales: 32, revenue: 3200000, color: '#10b981', percentage: 26 },
    { category: 'Hogar', sales: 28, revenue: 2100000, color: '#f97316', percentage: 22 },
    { category: 'Deportes', sales: 15, revenue: 700000, color: '#8b5cf6', percentage: 12 }
  ], []);

  const MOCK_TRENDS = useMemo(() => [
    { month: 'Ene', revenue: 8500000, orders: 95, customers: 65, timestamp: '2024-01-01' },
    { month: 'Feb', revenue: 9200000, orders: 108, customers: 72, timestamp: '2024-02-01' },
    { month: 'Mar', revenue: 10100000, orders: 125, customers: 78, timestamp: '2024-03-01' },
    { month: 'Abr', revenue: 11800000, orders: 142, customers: 85, timestamp: '2024-04-01' },
    { month: 'May', revenue: 12750000, orders: 156, customers: 89, timestamp: '2024-05-01' },
  ], []);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      const startTime = performance.now();
      setLoading(true);

      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 200));

        // Load data into store
        setMetrics(MOCK_METRICS);
        setTopProducts(MOCK_TOP_PRODUCTS);
        setSalesByCategory(MOCK_CATEGORIES);
        setMonthlyTrends(MOCK_TRENDS);

        const loadTime = performance.now() - startTime;
        setLoadTime(loadTime);

      } catch (error) {
        console.error('Failed to load analytics data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (!metrics) {
      loadData();
    }
  }, [metrics, setLoading, setMetrics, setTopProducts, setSalesByCategory, setMonthlyTrends, setLoadTime, MOCK_METRICS, MOCK_TOP_PRODUCTS, MOCK_CATEGORIES, MOCK_TRENDS]);

  // Track component render time
  useEffect(() => {
    const renderTime = performance.now() - performanceStartTime;
    if (renderTime > 0) {
      setChartRenderTime(renderTime);
    }
  }, [performanceStartTime, setChartRenderTime]);

  // Memoized event handlers
  const handleTimeRangeChange = useCallback((range: TimeRange) => {
    setFilters({ timeRange: range });
    const rangeText = {
      '7d': 'últimos 7 días',
      '30d': 'últimos 30 días',
      '90d': 'últimos 90 días',
      '1y': 'último año'
    }[range];
    announceChange(`Período cambiado a ${rangeText}`);
  }, [setFilters, announceChange]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    announceChange('Actualizando datos de analytics...');

    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 500));

    setIsRefreshing(false);
    announceChange('Datos actualizados exitosamente');
  }, [announceChange]);

  const handleExport = useCallback(() => {
    // Export functionality would go here
    console.log('Exporting analytics data...');
  }, []);

  // Early loading state
  if (isLoading && !metrics) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-neutral-200 rounded w-1/4 mb-2"></div>
          <div className="h-4 bg-neutral-200 rounded w-1/2"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
              <div className="h-12 bg-neutral-200 rounded mb-4"></div>
              <div className="h-4 bg-neutral-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-neutral-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <main
      ref={mainRef}
      className={`space-y-6 ${className}`}
      role="main"
      aria-labelledby="analytics-heading"
      aria-describedby="analytics-description"
    >
      {/* Live region for announcements */}
      <div
        className="sr-only"
        aria-live="polite"
        aria-atomic="false"
        id="analytics-announcements"
      >
        {announcements.map((announcement, index) => (
          <div key={index}>{announcement}</div>
        ))}
      </div>
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 id="analytics-heading" className="text-2xl font-bold text-neutral-900">Analytics</h1>
          <p id="analytics-description" className="text-neutral-600">Insights de rendimiento de tu tienda con datos en tiempo real</p>
          <div className="flex items-center gap-4 mt-1" role="status" aria-label="Estado del sistema">
            {performanceMetrics.isOptimal && (
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 bg-green-500 rounded-full"
                  aria-hidden="true"
                ></div>
                <span className="text-xs text-green-600">Rendimiento óptimo</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : authError ? 'bg-yellow-500' : 'bg-red-500'}`}
                aria-hidden="true"
              ></div>
              <span className={`text-xs ${wsConnected ? 'text-green-600' : authError ? 'text-yellow-600' : 'text-red-600'}`}>
                {wsConnected ? 'Tiempo real activo' : authError ? 'Error de autenticación' : 'Desconectado'}
              </span>
              {wsConnected && getLatency && (
                <span className="text-xs text-neutral-500">
                  ({getLatency().toFixed(0)}ms latencia)
                </span>
              )}
              {authError && (
                <button
                  onClick={() => window.location.reload()}
                  className="text-xs text-yellow-600 underline hover:text-yellow-700"
                  title="Recargar página para volver a autenticar"
                >
                  Reconectar
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3" role="toolbar" aria-label="Controles de analytics">
          <label htmlFor="time-range-select" className="sr-only">
            Seleccionar período de tiempo para análisis
          </label>
          <select
            id="time-range-select"
            value={filters.timeRange}
            onChange={(e) => handleTimeRangeChange(e.target.value as TimeRange)}
            className="px-3 py-2 border border-neutral-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            aria-describedby="time-range-help"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
            <option value="1y">Último año</option>
          </select>
          <div id="time-range-help" className="sr-only">
            Cambia el período de tiempo para ver diferentes rangos de datos
          </div>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 disabled:opacity-50 transition-colors focus:ring-2 focus:ring-primary-500"
            aria-describedby="refresh-help"
            aria-live="polite"
          >
            <RefreshCw
              className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
            {isRefreshing ? 'Actualizando...' : 'Actualizar'}
          </button>
          <div id="refresh-help" className="sr-only">
            Actualiza todos los datos de analytics con la información más reciente
          </div>

          <button
            onClick={handleExport}
            className="flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 border border-primary-200 rounded-md hover:bg-primary-100 transition-colors focus:ring-2 focus:ring-primary-500"
            aria-describedby="export-help"
          >
            <Download className="w-4 h-4 mr-2" aria-hidden="true" />
            Exportar
          </button>
          <div id="export-help" className="sr-only">
            Exporta los datos de analytics en formato Excel para análisis detallado
          </div>
        </div>
      </header>

      {/* Main Metrics */}
      <section
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        aria-labelledby="metrics-heading"
      >
        <h2 id="metrics-heading" className="sr-only">Métricas principales</h2>
        <MetricCard
          title="Ingresos totales"
          value={formattedRevenue}
          previousValue={formattedPreviousRevenue}
          trend={metrics?.revenue.trend}
          percentage={metrics?.revenue.percentage}
          icon={<DollarSign className="h-6 w-6 text-secondary-600" />}
          iconBg="bg-secondary-100"
        />

        <MetricCard
          title="Órdenes"
          value={metrics?.orders.current || 0}
          previousValue={`${metrics?.orders.previous || 0}`}
          trend={metrics?.orders.trend}
          percentage={metrics?.orders.percentage}
          icon={<ShoppingCart className="h-6 w-6 text-primary-600" />}
          iconBg="bg-primary-100"
        />

        <MetricCard
          title="Productos"
          value={metrics?.products.total || 0}
          icon={<Package className="h-6 w-6 text-accent-600" />}
          iconBg="bg-accent-100"
          badge={
            metrics?.products.lowStock && metrics.products.lowStock > 0 ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <AlertTriangle className="w-3 h-3 mr-1" />
                Stock bajo
              </span>
            ) : undefined
          }
        />

        <MetricCard
          title="Clientes"
          value={metrics?.customers.total || 0}
          icon={<Users className="h-6 w-6 text-purple-600" />}
          iconBg="bg-purple-100"
          badge={
            metrics?.customers.new ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {metrics.customers.new} nuevos
              </span>
            ) : undefined
          }
        />
      </section>

      {/* Charts Section with Lazy Loading */}
      <section
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        aria-labelledby="charts-heading"
      >
        <h2 id="charts-heading" className="sr-only">Gráficos y tendencias</h2>
        <article className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <header>
            <h3 className="text-lg font-semibold text-neutral-900 mb-6">Tendencia de Ingresos</h3>
          </header>
          <Suspense fallback={<ChartSkeleton />}>
            <LazyAccessibleBarChart
              data={filteredTrends}
              title="Tendencia de Ingresos Mensuales"
              description="Evolución de ingresos, órdenes y clientes por mes"
              ariaLabel="Gráfico de barras mostrando la tendencia de ingresos mensuales"
            />
          </Suspense>
        </article>

        <article className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <header>
            <h3 className="text-lg font-semibold text-neutral-900 mb-6">Ventas por Categoría</h3>
          </header>
          <Suspense fallback={<ChartSkeleton />}>
            <LazyAccessiblePieChart
              data={filteredCategories}
              title="Distribución de Ventas por Categoría"
              description="Porcentaje de ventas y ingresos distribuidos por categoría de productos"
              ariaLabel="Gráfico circular mostrando la distribución de ventas por categoría"
            />
          </Suspense>
        </article>
      </section>

      {/* Top Products with Lazy Loading */}
      <section className="bg-white rounded-lg shadow-sm border border-neutral-200">
        <header className="p-6 border-b border-neutral-200">
          <h2 className="text-lg font-semibold text-neutral-900">Productos Más Vendidos</h2>
        </header>
        <div className="p-6">
          <Suspense fallback={<ChartSkeleton />}>
            <LazyTopProductsList products={filteredProducts} />
          </Suspense>
        </div>
      </section>

      {/* Performance and insights */}
      <section
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        aria-labelledby="insights-heading"
      >
        <h2 id="insights-heading" className="sr-only">Rendimiento e insights</h2>
        {/* Performance Metrics */}
        <article className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <header className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-accent-600" aria-hidden="true" />
            <h3 className="text-lg font-semibold text-neutral-900">Rendimiento del Sistema</h3>
          </header>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-neutral-600">Tiempo de carga:</dt>
              <dd className={`font-medium ${performanceMetrics.loadTime < 1000 ? 'text-green-600' : 'text-red-600'}`}>
                {performanceMetrics.loadTime.toFixed(0)} milisegundos
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-neutral-600">Tiempo de renderizado:</dt>
              <dd className={`font-medium ${performanceMetrics.chartRenderTime < 500 ? 'text-green-600' : 'text-red-600'}`}>
                {performanceMetrics.chartRenderTime.toFixed(0)} milisegundos
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-neutral-600">Estado general:</dt>
              <dd className={`font-medium ${performanceMetrics.isOptimal ? 'text-green-600' : 'text-yellow-600'}`}>
                {performanceMetrics.isOptimal ? 'Óptimo' : 'Mejorable'}
              </dd>
            </div>
          </dl>
        </article>

        {/* Business Insights */}
        <article className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <header className="flex items-center gap-2 mb-4">
            <Target className="h-5 w-5 text-primary-600" aria-hidden="true" />
            <h3 className="text-lg font-semibold text-neutral-900">Insights de Negocio</h3>
          </header>
          <div className="space-y-4" role="list" aria-label="Lista de insights de negocio">
            {metrics?.revenue.trend === 'up' && (
              <div className="p-3 bg-secondary-50 rounded-lg border border-secondary-200" role="listitem">
                <div className="flex items-start gap-2">
                  <TrendingUp className="h-4 w-4 text-secondary-600 mt-0.5" aria-hidden="true" />
                  <div>
                    <p className="text-sm font-medium text-secondary-800">Crecimiento sólido</p>
                    <p className="text-xs text-secondary-700 mt-1">
                      Las ventas han crecido un {metrics.revenue.percentage.toFixed(1)}% comparado con el período anterior
                    </p>
                  </div>
                </div>
              </div>
            )}

            {metrics?.products.lowStock && metrics.products.lowStock > 0 && (
              <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200" role="listitem">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" aria-hidden="true" />
                  <div>
                    <p className="text-sm font-medium text-yellow-800">Alerta de stock bajo</p>
                    <p className="text-xs text-yellow-700 mt-1">
                      {metrics.products.lowStock} productos necesitan reabastecimiento urgente
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </article>
      </section>

      {/* Last updated indicator */}
      {lastUpdated && (
        <footer className="text-xs text-neutral-500 text-center" role="contentinfo">
          <time dateTime={lastUpdated}>
            Última actualización: {new Date(lastUpdated).toLocaleString('es-CO')}
          </time>
        </footer>
      )}
    </main>
  );
});

VendorAnalyticsOptimized.displayName = 'VendorAnalyticsOptimized';

export default VendorAnalyticsOptimized;