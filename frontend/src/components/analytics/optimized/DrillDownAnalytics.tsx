// frontend/src/components/analytics/optimized/DrillDownAnalytics.tsx
// PERFORMANCE_OPTIMIZED: Interactive drill-down analytics modal
// Target: <300ms interaction response with detailed data visualization

import React, { memo, useMemo, useState, useCallback } from 'react';
import {
  X,
  TrendingUp,
  TrendingDown,
  Calendar,
  Filter,
  Download,
  Eye,
  BarChart3,
  PieChart,
  LineChart,
  Grid3X3,
  List
} from 'lucide-react';
import { PerformanceChart } from '../charts/PerformanceChart';

interface DrillDownData {
  type: 'category' | 'period' | 'product';
  title: string;
  subtitle?: string;
  data: any[];
  metrics: {
    total: number;
    growth: number;
    trend: 'up' | 'down' | 'stable';
    period: string;
  };
}

interface DrillDownAnalyticsProps {
  isOpen: boolean;
  onClose: () => void;
  drillDownData: DrillDownData | null;
  mobile?: boolean;
}

// Memoized header component
const DrillDownHeader = memo(({
  title,
  subtitle,
  metrics,
  onClose,
  mobile
}: {
  title: string;
  subtitle?: string;
  metrics: DrillDownData['metrics'];
  onClose: () => void;
  mobile?: boolean;
}) => {
  const formatCOP = useMemo(() => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }, []);

  const trendColor = useMemo(() => {
    return metrics.trend === 'up' ? 'text-green-600' : metrics.trend === 'down' ? 'text-red-600' : 'text-neutral-600';
  }, [metrics.trend]);

  const TrendIcon = metrics.trend === 'up' ? TrendingUp : metrics.trend === 'down' ? TrendingDown : BarChart3;

  return (
    <div className="flex items-start justify-between p-6 border-b border-neutral-200">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-2">
          <h2 className="text-xl font-bold text-neutral-900 truncate">{title}</h2>
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-neutral-100 ${trendColor}`}>
            <TrendIcon className="w-3 h-3" />
            {metrics.growth > 0 ? '+' : ''}{metrics.growth.toFixed(1)}%
          </div>
        </div>

        {subtitle && (
          <p className="text-sm text-neutral-600 mb-3">{subtitle}</p>
        )}

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-primary-50 p-3 rounded-lg">
            <p className="text-xs font-medium text-primary-600 mb-1">Total</p>
            <p className="text-sm font-bold text-primary-900">
              {formatCOP.format(metrics.total)}
            </p>
          </div>

          <div className="bg-secondary-50 p-3 rounded-lg">
            <p className="text-xs font-medium text-secondary-600 mb-1">Período</p>
            <p className="text-sm font-bold text-secondary-900">
              {metrics.period}
            </p>
          </div>

          <div className={`p-3 rounded-lg ${
            metrics.trend === 'up' ? 'bg-green-50' : metrics.trend === 'down' ? 'bg-red-50' : 'bg-neutral-50'
          }`}>
            <p className={`text-xs font-medium mb-1 ${trendColor}`}>Tendencia</p>
            <p className={`text-sm font-bold ${trendColor}`}>
              {metrics.trend === 'up' ? 'Crecimiento' : metrics.trend === 'down' ? 'Declive' : 'Estable'}
            </p>
          </div>
        </div>
      </div>

      <button
        onClick={onClose}
        className="ml-4 p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
});

DrillDownHeader.displayName = 'DrillDownHeader';

// Memoized data table component
const DataTable = memo(({ data, type }: { data: any[]; type: string }) => {
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  const sortedData = useMemo(() => {
    if (!sortField) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();

      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
  }, [data, sortField, sortDirection]);

  const handleSort = useCallback((field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  }, [sortField, sortDirection]);

  const formatCOP = useMemo(() => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }, []);

  if (viewMode === 'grid') {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-neutral-900">Datos Detallados</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('table')}
              className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className="p-2 text-primary-600 bg-primary-100 rounded-lg"
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedData.map((item, index) => (
            <div key={index} className="bg-white p-4 border border-neutral-200 rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium text-neutral-900 truncate">{item.name || item.category || item.period}</h4>
                <Eye className="w-4 h-4 text-neutral-400" />
              </div>

              <div className="space-y-2">
                {item.sales && (
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Ventas:</span>
                    <span className="text-sm font-medium text-neutral-900">{item.sales}</span>
                  </div>
                )}
                {item.revenue && (
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Ingresos:</span>
                    <span className="text-sm font-medium text-primary-600">{formatCOP.format(item.revenue)}</span>
                  </div>
                )}
                {item.orders && (
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Órdenes:</span>
                    <span className="text-sm font-medium text-neutral-900">{item.orders}</span>
                  </div>
                )}
                {item.customers && (
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Clientes:</span>
                    <span className="text-sm font-medium text-neutral-900">{item.customers}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">Datos Detallados</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('table')}
            className="p-2 text-primary-600 bg-primary-100 rounded-lg"
          >
            <List className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border border-neutral-200 rounded-lg">
          <thead className="bg-neutral-50">
            <tr>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-100"
                onClick={() => handleSort('name')}
              >
                Nombre
              </th>
              {data[0]?.sales !== undefined && (
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-100"
                  onClick={() => handleSort('sales')}
                >
                  Ventas
                </th>
              )}
              {data[0]?.revenue !== undefined && (
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-100"
                  onClick={() => handleSort('revenue')}
                >
                  Ingresos
                </th>
              )}
              {data[0]?.orders !== undefined && (
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-100"
                  onClick={() => handleSort('orders')}
                >
                  Órdenes
                </th>
              )}
              {data[0]?.customers !== undefined && (
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-100"
                  onClick={() => handleSort('customers')}
                >
                  Clientes
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200">
            {sortedData.map((item, index) => (
              <tr key={index} className="hover:bg-neutral-50">
                <td className="px-4 py-4 text-sm font-medium text-neutral-900">
                  {item.name || item.category || item.period}
                </td>
                {item.sales !== undefined && (
                  <td className="px-4 py-4 text-sm text-neutral-900">{item.sales}</td>
                )}
                {item.revenue !== undefined && (
                  <td className="px-4 py-4 text-sm text-primary-600">{formatCOP.format(item.revenue)}</td>
                )}
                {item.orders !== undefined && (
                  <td className="px-4 py-4 text-sm text-neutral-900">{item.orders}</td>
                )}
                {item.customers !== undefined && (
                  <td className="px-4 py-4 text-sm text-neutral-900">{item.customers}</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});

DataTable.displayName = 'DataTable';

export const DrillDownAnalytics: React.FC<DrillDownAnalyticsProps> = memo(({
  isOpen,
  onClose,
  drillDownData,
  mobile = false
}) => {
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area'>('line');

  // Handle export functionality
  const handleExport = useCallback(() => {
    if (!drillDownData) return;

    console.log('Exporting drill-down data:', drillDownData);
    // Export functionality will be implemented in the export service
  }, [drillDownData]);

  // Memoized chart data processing
  const chartData = useMemo(() => {
    if (!drillDownData?.data) return [];

    return drillDownData.data.map(item => ({
      name: item.name || item.category || item.period || item.month,
      value: item.revenue || item.sales || item.orders || 0,
      sales: item.sales || 0,
      revenue: item.revenue || 0,
      orders: item.orders || 0,
      customers: item.customers || 0
    }));
  }, [drillDownData]);

  if (!isOpen || !drillDownData) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className={`inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle ${
          mobile ? 'w-full max-w-sm' : 'w-full max-w-6xl'
        }`}>

          {/* Header */}
          <DrillDownHeader
            title={drillDownData.title}
            subtitle={drillDownData.subtitle}
            metrics={drillDownData.metrics}
            onClose={onClose}
            mobile={mobile}
          />

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Chart controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-neutral-700">Vista:</span>
                <div className="flex items-center gap-1 bg-neutral-100 rounded-lg p-1">
                  <button
                    onClick={() => setChartType('line')}
                    className={`p-1 rounded ${chartType === 'line' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <LineChart className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setChartType('bar')}
                    className={`p-1 rounded ${chartType === 'bar' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <BarChart3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setChartType('area')}
                    className={`p-1 rounded ${chartType === 'area' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <PieChart className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <button
                onClick={handleExport}
                className="flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 border border-primary-200 rounded-md hover:bg-primary-100 transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </button>
            </div>

            {/* Chart */}
            <div className="bg-white border border-neutral-200 rounded-lg p-4">
              <PerformanceChart
                data={chartData}
                type={chartType}
                height={mobile ? 250 : 350}
                mobile={mobile}
                showGrid={true}
                showTooltip={true}
                showLegend={false}
                animate={true}
              />
            </div>

            {/* Data table */}
            <DataTable data={drillDownData.data} type={drillDownData.type} />
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-neutral-50 border-t border-neutral-200">
            <div className="flex items-center justify-between">
              <p className="text-sm text-neutral-600">
                {drillDownData.data.length} elementos • Actualizado en tiempo real
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

DrillDownAnalytics.displayName = 'DrillDownAnalytics';

export default DrillDownAnalytics;