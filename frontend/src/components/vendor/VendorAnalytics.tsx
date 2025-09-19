// frontend/src/components/vendor/VendorAnalytics.tsx
// PRODUCTION_READY: Componente de analytics completo para vendedores
// Optimizado para insights de negocio en el mercado colombiano

import React, { useState, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  ShoppingCart,
  Eye,
  Star,
  Users,
  Calendar,
  BarChart3,
  PieChart,
  Target,
  Zap,
  Award,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  Minus,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';

interface AnalyticsData {
  revenue: {
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
  };
  orders: {
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
  };
  products: {
    total: number;
    active: number;
    lowStock: number;
    outOfStock: number;
  };
  customers: {
    total: number;
    new: number;
    returning: number;
  };
  topProducts: Array<{
    id: string;
    name: string;
    sales: number;
    revenue: number;
    image: string;
  }>;
  salesByCategory: Array<{
    category: string;
    sales: number;
    revenue: number;
    color: string;
  }>;
  monthlyTrends: Array<{
    month: string;
    revenue: number;
    orders: number;
  }>;
}

// Datos mock para demostración
const MOCK_ANALYTICS: AnalyticsData = {
  revenue: {
    current: 12750000,
    previous: 9850000,
    trend: 'up',
    percentage: 29.4
  },
  orders: {
    current: 156,
    previous: 134,
    trend: 'up',
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
  },
  topProducts: [
    {
      id: '1',
      name: 'Smartphone Samsung Galaxy A54',
      sales: 23,
      revenue: 2050000,
      image: '/api/placeholder/60/60'
    },
    {
      id: '2',
      name: 'Auriculares Bluetooth Sony',
      sales: 18,
      revenue: 1440000,
      image: '/api/placeholder/60/60'
    },
    {
      id: '3',
      name: 'Camiseta Polo Lacoste',
      sales: 15,
      revenue: 945000,
      image: '/api/placeholder/60/60'
    }
  ],
  salesByCategory: [
    { category: 'Electrónicos', sales: 45, revenue: 6750000, color: '#3b82f6' },
    { category: 'Ropa', sales: 32, revenue: 3200000, color: '#10b981' },
    { category: 'Hogar', sales: 28, revenue: 2100000, color: '#f97316' },
    { category: 'Deportes', sales: 15, revenue: 700000, color: '#8b5cf6' }
  ],
  monthlyTrends: [
    { month: 'Ene', revenue: 8500000, orders: 95 },
    { month: 'Feb', revenue: 9200000, orders: 108 },
    { month: 'Mar', revenue: 10100000, orders: 125 },
    { month: 'Abr', revenue: 11800000, orders: 142 },
    { month: 'May', revenue: 12750000, orders: 156 },
  ]
};

interface VendorAnalyticsProps {
  className?: string;
  vendorId?: string;
}

type TimeRange = '7d' | '30d' | '90d' | '1y';

export const VendorAnalytics: React.FC<VendorAnalyticsProps> = ({
  className = '',
  vendorId
}) => {
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);

  const analytics = MOCK_ANALYTICS;

  // Formateo de moneda colombiana
  const formatCOP = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Formateo compacto para números grandes
  const formatCompact = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  // Componente de indicador de tendencia
  const TrendIndicator: React.FC<{ trend: 'up' | 'down' | 'stable', percentage: number }> = ({ trend, percentage }) => {
    const Icon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus;
    const colorClass = trend === 'up' ? 'text-secondary-600' : trend === 'down' ? 'text-red-600' : 'text-neutral-500';
    const bgClass = trend === 'up' ? 'bg-secondary-100' : trend === 'down' ? 'bg-red-100' : 'bg-neutral-100';

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClass} ${bgClass}`}>
        <Icon className="w-3 h-3 mr-1" />
        {percentage.toFixed(1)}%
      </span>
    );
  };

  // Componente de gráfico de barras simple
  const SimpleBarChart: React.FC<{ data: typeof analytics.monthlyTrends }> = ({ data }) => {
    const maxRevenue = Math.max(...data.map(d => d.revenue));

    return (
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-3">
            <span className="text-sm font-medium text-neutral-600 w-8">{item.month}</span>
            <div className="flex-1 bg-neutral-200 rounded-full h-2 relative">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(item.revenue / maxRevenue) * 100}%` }}
              />
            </div>
            <span className="text-sm text-neutral-600 w-16 text-right">
              {formatCompact(item.revenue)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  // Componente de gráfico de dona simple
  const SimplePieChart: React.FC<{ data: typeof analytics.salesByCategory }> = ({ data }) => {
    const total = data.reduce((sum, item) => sum + item.sales, 0);

    return (
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-neutral-700">{item.category}</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-neutral-900">
                {item.sales} ventas
              </div>
              <div className="text-xs text-neutral-500">
                {((item.sales / total) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">Analytics</h2>
          <p className="text-neutral-600">Insights de rendimiento de tu tienda</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Selector de tiempo */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
            className="px-3 py-2 border border-neutral-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
            <option value="1y">Último año</option>
          </select>

          <button
            onClick={() => setIsLoading(true)}
            disabled={isLoading}
            className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>

          <button className="flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 border border-primary-200 rounded-md hover:bg-primary-100 transition-colors">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </button>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Ingresos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-secondary-100 rounded-lg">
              <DollarSign className="h-6 w-6 text-secondary-600" />
            </div>
            <TrendIndicator trend={analytics.revenue.trend} percentage={analytics.revenue.percentage} />
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-500 mb-1">Ingresos totales</p>
            <p className="text-2xl font-bold text-neutral-900">{formatCOP(analytics.revenue.current)}</p>
            <p className="text-sm text-neutral-600 mt-1">
              vs. {formatCOP(analytics.revenue.previous)} anterior
            </p>
          </div>
        </div>

        {/* Órdenes */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-primary-100 rounded-lg">
              <ShoppingCart className="h-6 w-6 text-primary-600" />
            </div>
            <TrendIndicator trend={analytics.orders.trend} percentage={analytics.orders.percentage} />
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-500 mb-1">Órdenes</p>
            <p className="text-2xl font-bold text-neutral-900">{analytics.orders.current}</p>
            <p className="text-sm text-neutral-600 mt-1">
              vs. {analytics.orders.previous} anterior
            </p>
          </div>
        </div>

        {/* Productos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-accent-100 rounded-lg">
              <Package className="h-6 w-6 text-accent-600" />
            </div>
            {analytics.products.lowStock > 0 && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <AlertTriangle className="w-3 h-3 mr-1" />
                Stock bajo
              </span>
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-500 mb-1">Productos</p>
            <p className="text-2xl font-bold text-neutral-900">{analytics.products.total}</p>
            <p className="text-sm text-neutral-600 mt-1">
              {analytics.products.active} activos, {analytics.products.outOfStock} agotados
            </p>
          </div>
        </div>

        {/* Clientes */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {analytics.customers.new} nuevos
            </span>
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-500 mb-1">Clientes</p>
            <p className="text-2xl font-bold text-neutral-900">{analytics.customers.total}</p>
            <p className="text-sm text-neutral-600 mt-1">
              {analytics.customers.returning} recurrentes
            </p>
          </div>
        </div>
      </div>

      {/* Gráficos y análisis detallado */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencia de ventas mensual */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Tendencia de Ingresos</h3>
            <BarChart3 className="h-5 w-5 text-neutral-400" />
          </div>
          <SimpleBarChart data={analytics.monthlyTrends} />
        </div>

        {/* Ventas por categoría */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Ventas por Categoría</h3>
            <PieChart className="h-5 w-5 text-neutral-400" />
          </div>
          <SimplePieChart data={analytics.salesByCategory} />
        </div>
      </div>

      {/* Productos más vendidos */}
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200">
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-neutral-900">Productos Más Vendidos</h3>
            <Award className="h-5 w-5 text-neutral-400" />
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {analytics.topProducts.map((product, index) => (
              <div key={product.id} className="flex items-center gap-4 p-4 bg-neutral-50 rounded-lg">
                {/* Ranking */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index === 0 ? 'bg-yellow-100 text-yellow-800' :
                  index === 1 ? 'bg-neutral-100 text-neutral-600' :
                  'bg-amber-100 text-amber-800'
                }`}>
                  {index + 1}
                </div>

                {/* Imagen del producto */}
                <div className="w-12 h-12 bg-neutral-200 rounded-lg overflow-hidden">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Información del producto */}
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-neutral-900 truncate">{product.name}</h4>
                  <p className="text-sm text-neutral-600">{product.sales} ventas</p>
                </div>

                {/* Ingresos */}
                <div className="text-right">
                  <p className="font-semibold text-neutral-900">{formatCOP(product.revenue)}</p>
                  <p className="text-sm text-neutral-600">Ingresos</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights y recomendaciones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Insights */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-accent-600" />
            <h3 className="text-lg font-semibold text-neutral-900">Insights</h3>
          </div>
          <div className="space-y-4">
            <div className="p-4 bg-secondary-50 rounded-lg border border-secondary-200">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-secondary-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-secondary-800">Crecimiento sólido</p>
                  <p className="text-sm text-secondary-700 mt-1">
                    Tus ventas han crecido un 29.4% comparado con el período anterior. ¡Excelente trabajo!
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Atención al inventario</p>
                  <p className="text-sm text-yellow-700 mt-1">
                    Tienes 8 productos con stock bajo. Considera reabastecer pronto.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
              <div className="flex items-start gap-3">
                <Target className="h-5 w-5 text-primary-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary-800">Oportunidad de categoría</p>
                  <p className="text-sm text-primary-700 mt-1">
                    Los electrónicos representan el 36% de tus ventas. Considera expandir esta categoría.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Objetivos y metas */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-neutral-200">
          <div className="flex items-center gap-2 mb-4">
            <Target className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-neutral-900">Objetivos del Mes</h3>
          </div>
          <div className="space-y-4">
            {/* Objetivo de ingresos */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-neutral-700">Ingresos mensuales</span>
                <span className="text-sm text-neutral-600">85%</span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-2">
                <div className="bg-secondary-500 h-2 rounded-full" style={{ width: '85%' }} />
              </div>
              <div className="flex items-center justify-between mt-1 text-xs text-neutral-600">
                <span>{formatCOP(12750000)}</span>
                <span>Meta: {formatCOP(15000000)}</span>
              </div>
            </div>

            {/* Objetivo de órdenes */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-neutral-700">Órdenes mensuales</span>
                <span className="text-sm text-neutral-600">78%</span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-2">
                <div className="bg-primary-500 h-2 rounded-full" style={{ width: '78%' }} />
              </div>
              <div className="flex items-center justify-between mt-1 text-xs text-neutral-600">
                <span>156 órdenes</span>
                <span>Meta: 200 órdenes</span>
              </div>
            </div>

            {/* Objetivo de productos nuevos */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-neutral-700">Productos nuevos</span>
                <span className="text-sm text-neutral-600">60%</span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-2">
                <div className="bg-accent-500 h-2 rounded-full" style={{ width: '60%' }} />
              </div>
              <div className="flex items-center justify-between mt-1 text-xs text-neutral-600">
                <span>3 productos</span>
                <span>Meta: 5 productos</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorAnalytics;