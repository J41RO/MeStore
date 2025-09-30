import React from 'react';
import { 
  PackageIcon, 
  DollarSignIcon, 
  ShoppingBagIcon, 
  TrendingUpIcon,
  TrendingDownIcon,
  UsersIcon,
  StarIcon,
  ClockIcon,
  BarChart3Icon
} from 'lucide-react';
import { VendorMetrics } from '../../hooks/useVendorMetrics';

interface MetricsGridProps {
  metrics: VendorMetrics | null;
  loading?: boolean;
  className?: string;
}

interface MetricCardData {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ComponentType<any>;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'yellow';
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ 
  metrics, 
  loading = false, 
  className = "" 
}) => {
  if (loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
        {[1, 2, 3, 4].map((i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  const primaryMetrics: MetricCardData[] = [
    {
      title: 'Total Productos',
      value: metrics?.totalProductos || 0,
      change: metrics?.productosChange || 0,
      icon: PackageIcon,
      color: 'blue',
      description: 'Todos tus productos',
      trend: (metrics?.productosChange || 0) > 0 ? 'up' : 'neutral'
    },
    {
      title: 'Productos Aprobados',
      value: metrics?.productosAprobados || 0,
      icon: PackageIcon,
      color: 'green',
      description: 'Visibles en marketplace',
      trend: 'neutral'
    },
    {
      title: 'Pendientes Aprobación',
      value: metrics?.productosPendientes || 0,
      icon: PackageIcon,
      color: 'yellow',
      description: 'Esperando revisión admin',
      trend: 'neutral'
    },
    {
      title: 'Ventas del Mes', 
      value: `$${(metrics?.ventasDelMes || 0).toLocaleString()}`,
      change: metrics?.ventasChange || 0,
      icon: DollarSignIcon,
      color: 'green',
      description: 'COP',
      trend: (metrics?.ventasChange || 0) > 0 ? 'up' : (metrics?.ventasChange || 0) < 0 ? 'down' : 'neutral'
    },
    {
      title: 'Ingresos Totales',
      value: `$${(metrics?.ingresosTotales || 0).toLocaleString()}`,
      change: metrics?.ingresosChange || 0,
      icon: TrendingUpIcon,
      color: 'purple',
      description: 'Histórico',
      trend: (metrics?.ingresosChange || 0) > 0 ? 'up' : (metrics?.ingresosChange || 0) < 0 ? 'down' : 'neutral'
    },
    {
      title: 'Órdenes Pendientes',
      value: metrics?.ordenesPendientes || 0,
      change: metrics?.ordenesChange || 0,
      icon: ShoppingBagIcon,
      color: 'orange',
      description: 'Requieren atención',
      trend: (metrics?.ordenesChange || 0) > 0 ? 'up' : 'neutral'
    }
  ];

  const secondaryMetrics: MetricCardData[] = [
    {
      title: 'Clientes Únicos',
      value: metrics?.clientesUnicos || 0,
      icon: UsersIcon,
      color: 'blue',
      description: 'Este mes'
    },
    {
      title: 'Puntuación',
      value: `${(metrics?.puntuacionVendedor || 0).toFixed(1)}/5.0`,
      icon: StarIcon,
      color: 'yellow',
      description: 'Rating promedio'
    },
    {
      title: 'Tiempo Entrega',
      value: `${metrics?.tiempoPromedioEntrega || 0} días`,
      icon: ClockIcon,
      color: 'purple',
      description: 'Promedio'
    },
    {
      title: 'Órdenes Completadas',
      value: metrics?.ordenesCompletadas || 0,
      icon: BarChart3Icon,
      color: 'green',
      description: 'Total histórico'
    }
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Métricas Principales */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Métricas Principales</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {primaryMetrics.map((metric, index) => (
            <MetricCard key={index} {...metric} showChange={true} />
          ))}
        </div>
      </div>

      {/* Métricas Secundarias */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Estadísticas Adicionales</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {secondaryMetrics.map((metric, index) => (
            <MetricCard key={index} {...metric} showChange={false} />
          ))}
        </div>
      </div>

      {/* Resumen de Performance */}
      <PerformanceSummary metrics={metrics} />
    </div>
  );
};

// Componente de tarjeta de métrica individual
const MetricCard: React.FC<MetricCardData & { showChange?: boolean }> = ({ 
  title, 
  value, 
  change = 0,
  icon: Icon, 
  color, 
  description,
  trend,
  showChange = true 
}) => {
  const colorClasses = {
    blue: 'bg-blue-500 text-blue-100',
    green: 'bg-green-500 text-green-100', 
    purple: 'bg-purple-500 text-purple-100',
    orange: 'bg-orange-500 text-orange-100',
    red: 'bg-red-500 text-red-100',
    yellow: 'bg-yellow-500 text-yellow-100'
  };

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUpIcon className="h-4 w-4 text-green-600" />;
    if (trend === 'down') return <TrendingDownIcon className="h-4 w-4 text-red-600" />;
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center">
        <div className={`rounded-full p-3 ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-center space-x-2">
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {getTrendIcon()}
          </div>
          
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
          
          {showChange && change !== 0 && (
            <p className={`text-sm mt-1 ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change > 0 ? '+' : ''}{change}% vs mes anterior
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Componente skeleton para loading
const MetricCardSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
      <div className="flex items-center">
        <div className="rounded-full bg-gray-200 h-12 w-12"></div>
        <div className="ml-4 flex-1">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </div>
  );
};

// Resumen de performance del vendedor
const PerformanceSummary: React.FC<{ metrics: VendorMetrics | null }> = ({ metrics }) => {
  if (!metrics) return null;

  const performanceScore = metrics.puntuacionVendedor || 0;
  const getPerformanceColor = (score: number) => {
    if (score >= 4.5) return 'text-green-600 bg-green-50';
    if (score >= 4.0) return 'text-blue-600 bg-blue-50';
    if (score >= 3.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getPerformanceLevel = (score: number) => {
    if (score >= 4.5) return 'Excelente';
    if (score >= 4.0) return 'Muy Bueno';
    if (score >= 3.5) return 'Bueno';
    return 'Necesita Mejora';
  };

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6">
      <h4 className="text-md font-semibold text-gray-900 mb-4">Resumen de Performance</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPerformanceColor(performanceScore)}`}>
            {getPerformanceLevel(performanceScore)}
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{performanceScore.toFixed(1)}/5.0</p>
          <p className="text-sm text-gray-600">Puntuación General</p>
        </div>
        
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{metrics.clientesUnicos || 0}</p>
          <p className="text-sm text-gray-600">Clientes Atendidos</p>
          <p className="text-xs text-gray-500 mt-1">Este mes</p>
        </div>
        
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{metrics.tiempoPromedioEntrega || 0}</p>
          <p className="text-sm text-gray-600">Días Promedio</p>
          <p className="text-xs text-gray-500 mt-1">Tiempo de entrega</p>
        </div>
      </div>
      
      {metrics.productoMasVendido && metrics.productoMasVendido !== 'N/A' && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Producto más vendido:</span> {metrics.productoMasVendido}
          </p>
          {metrics.categoriaTopVentas && metrics.categoriaTopVentas !== 'N/A' && (
            <p className="text-sm text-gray-600">
              <span className="font-medium">Categoría top:</span> {metrics.categoriaTopVentas}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default MetricsGrid;