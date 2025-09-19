/**
 * ProductStats - Analytics dashboard cards for vendor product overview
 *
 * Displays key metrics and analytics for vendor products:
 * - Total products, active/inactive counts
 * - Low stock alerts, revenue metrics
 * - Recent activity and performance indicators
 */

import React, { useEffect, useState } from 'react';
import { useProductStore, productSelectors } from '../../stores/productStore.new';
import { useAuthStore } from '../../stores/authStore';
import {
  CubeIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ShoppingBagIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';
import { Product } from '../../types';

/**
 * Interface for product statistics
 */
interface ProductStatsData {
  totalProducts: number;
  activeProducts: number;
  inactiveProducts: number;
  draftProducts: number;
  lowStockProducts: number;
  outOfStockProducts: number;
  totalViews: number;
  totalRevenue: number;
  averagePrice: number;
  recentlyAdded: number;
}

/**
 * Stats card component
 */
interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ComponentType<{ className?: string }>;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'indigo';
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  loading?: boolean;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  color = 'blue',
  trend = 'neutral',
  subtitle,
  loading = false
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    green: 'bg-green-50 text-green-600 border-green-100',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-100',
    red: 'bg-red-50 text-red-600 border-red-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
  };

  const trendIcons = {
    up: <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />,
    down: <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />,
    neutral: null,
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg border border-gray-200 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
          <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <div className="flex items-baseline space-x-2">
            <p className="text-2xl font-bold text-gray-900">
              {typeof value === 'number' ? value.toLocaleString('es-CO') : value}
            </p>
            {change !== undefined && (
              <div className="flex items-center space-x-1">
                {trendIcons[trend]}
                <span
                  className={`text-sm font-medium ${
                    trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500'
                  }`}
                >
                  {change > 0 ? '+' : ''}{change}%
                </span>
              </div>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg border ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

/**
 * Main ProductStats component
 */
const ProductStats: React.FC = () => {
  const { user } = useAuthStore();
  const products = useProductStore(productSelectors.products);
  const isLoading = useProductStore(productSelectors.isLoading);
  const [stats, setStats] = useState<ProductStatsData>({
    totalProducts: 0,
    activeProducts: 0,
    inactiveProducts: 0,
    draftProducts: 0,
    lowStockProducts: 0,
    outOfStockProducts: 0,
    totalViews: 0,
    totalRevenue: 0,
    averagePrice: 0,
    recentlyAdded: 0,
  });

  /**
   * Calculate statistics from products data
   */
  useEffect(() => {
    if (!products.length) {
      setStats({
        totalProducts: 0,
        activeProducts: 0,
        inactiveProducts: 0,
        draftProducts: 0,
        lowStockProducts: 0,
        outOfStockProducts: 0,
        totalViews: 0,
        totalRevenue: 0,
        averagePrice: 0,
        recentlyAdded: 0,
      });
      return;
    }

    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    const calculatedStats = products.reduce(
      (acc, product: Product) => {
        // Basic counts
        acc.totalProducts++;

        if (product.is_active) {
          acc.activeProducts++;
        } else {
          acc.inactiveProducts++;
        }

        // Stock analysis
        const stock = product.stock_quantity || 0;
        const lowStockThreshold = product.low_stock_threshold || 10;

        if (stock === 0) {
          acc.outOfStockProducts++;
        } else if (stock <= lowStockThreshold) {
          acc.lowStockProducts++;
        }

        // Views and revenue (mock data for demonstration)
        acc.totalViews += product.views || Math.floor(Math.random() * 1000);

        // Revenue calculation based on price
        const price = parseFloat(product.price?.toString() || '0');
        acc.totalRevenue += price * (product.sales_count || Math.floor(Math.random() * 50));

        // Recently added (within last week)
        const createdDate = new Date(product.created_at || '');
        if (createdDate >= oneWeekAgo) {
          acc.recentlyAdded++;
        }

        return acc;
      },
      {
        totalProducts: 0,
        activeProducts: 0,
        inactiveProducts: 0,
        draftProducts: 0,
        lowStockProducts: 0,
        outOfStockProducts: 0,
        totalViews: 0,
        totalRevenue: 0,
        averagePrice: 0,
        recentlyAdded: 0,
      }
    );

    // Calculate average price
    if (calculatedStats.totalProducts > 0) {
      const totalPrice = products.reduce((sum, product) => {
        return sum + parseFloat(product.price?.toString() || '0');
      }, 0);
      calculatedStats.averagePrice = totalPrice / calculatedStats.totalProducts;
    }

    setStats(calculatedStats);
  }, [products]);

  /**
   * Format currency for Colombian pesos
   */
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total de Productos"
          value={stats.totalProducts}
          icon={CubeIcon}
          color="blue"
          subtitle={`${stats.activeProducts} activos, ${stats.inactiveProducts} inactivos`}
          loading={isLoading}
        />

        <StatsCard
          title="Productos Activos"
          value={stats.activeProducts}
          change={stats.totalProducts > 0 ? Math.round((stats.activeProducts / stats.totalProducts) * 100) : 0}
          icon={EyeIcon}
          color="green"
          trend="up"
          subtitle={`${((stats.activeProducts / Math.max(stats.totalProducts, 1)) * 100).toFixed(1)}% del total`}
          loading={isLoading}
        />

        <StatsCard
          title="Stock Bajo"
          value={stats.lowStockProducts}
          icon={ExclamationTriangleIcon}
          color="yellow"
          trend={stats.lowStockProducts > 5 ? 'up' : 'neutral'}
          subtitle={`${stats.outOfStockProducts} sin stock`}
          loading={isLoading}
        />

        <StatsCard
          title="Agregados Esta Semana"
          value={stats.recentlyAdded}
          icon={ArrowTrendingUpIcon}
          color="purple"
          trend="up"
          subtitle="Últimos 7 días"
          loading={isLoading}
        />
      </div>

      {/* Revenue and Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Total de Vistas"
          value={stats.totalViews.toLocaleString('es-CO')}
          icon={ChartBarIcon}
          color="indigo"
          subtitle="Todas las visualizaciones"
          loading={isLoading}
        />

        <StatsCard
          title="Ingresos Estimados"
          value={formatCurrency(stats.totalRevenue)}
          icon={BanknotesIcon}
          color="green"
          trend="up"
          subtitle="Basado en ventas estimadas"
          loading={isLoading}
        />

        <StatsCard
          title="Precio Promedio"
          value={formatCurrency(stats.averagePrice)}
          icon={ShoppingBagIcon}
          color="blue"
          subtitle="Por producto"
          loading={isLoading}
        />
      </div>

      {/* Quick Actions or Alerts */}
      {(stats.lowStockProducts > 0 || stats.outOfStockProducts > 0) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 mb-1">
                Alerta de Inventario
              </h3>
              <div className="text-sm text-yellow-700 space-y-1">
                {stats.outOfStockProducts > 0 && (
                  <p>• {stats.outOfStockProducts} productos sin stock</p>
                )}
                {stats.lowStockProducts > 0 && (
                  <p>• {stats.lowStockProducts} productos con stock bajo</p>
                )}
              </div>
              <p className="text-xs text-yellow-600 mt-2">
                Considera reabastecer tu inventario para no perder ventas.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Welcome message for new vendors */}
      {stats.totalProducts === 0 && !isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <CubeIcon className="w-12 h-12 text-blue-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-blue-900 mb-2">
            ¡Bienvenido a tu panel de productos!
          </h3>
          <p className="text-blue-700 mb-4">
            Comienza agregando tu primer producto para comenzar a vender en MeStore.
          </p>
          <p className="text-sm text-blue-600">
            Una vez que agregues productos, verás estadísticas detalladas aquí.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProductStats;