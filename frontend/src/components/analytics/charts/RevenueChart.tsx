// frontend/src/components/analytics/charts/RevenueChart.tsx
// PERFORMANCE_OPTIMIZED: Revenue trend chart with drill-down capabilities
// Target: Interactive revenue analysis with <500ms response time

import React, { memo, useMemo, useState, useCallback } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Brush
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { useFilteredTrends, useAnalyticsActions } from '../../../stores/analyticsStore';

interface RevenueChartProps {
  height?: number;
  showComparison?: boolean;
  showBrush?: boolean;
  mobile?: boolean;
  className?: string;
  onPeriodSelect?: (period: { start: string; end: string }) => void;
}

// Memoized tooltip with Colombian peso formatting
const RevenueTooltip = memo(({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  const formatCOP = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const currentRevenue = payload.find((p: any) => p.dataKey === 'revenue')?.value || 0;
  const previousRevenue = payload.find((p: any) => p.dataKey === 'previousRevenue')?.value;
  const orders = payload.find((p: any) => p.dataKey === 'orders')?.value || 0;

  const trend = previousRevenue
    ? currentRevenue > previousRevenue ? 'up' : currentRevenue < previousRevenue ? 'down' : 'stable'
    : null;

  const trendPercentage = previousRevenue
    ? ((currentRevenue - previousRevenue) / previousRevenue) * 100
    : 0;

  return (
    <div className="bg-white p-4 border border-neutral-200 rounded-lg shadow-lg min-w-[200px]">
      <p className="text-sm font-semibold text-neutral-900 mb-2">{label}</p>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-neutral-600">Ingresos:</span>
          <span className="font-semibold text-primary-600">{formatCOP(currentRevenue)}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-neutral-600">Órdenes:</span>
          <span className="font-medium text-neutral-900">{orders}</span>
        </div>

        {previousRevenue && trend && (
          <div className="flex items-center justify-between pt-2 border-t border-neutral-100">
            <span className="text-sm text-neutral-600">Tendencia:</span>
            <div className="flex items-center gap-1">
              {trend === 'up' ? (
                <TrendingUp className="w-3 h-3 text-green-600" />
              ) : trend === 'down' ? (
                <TrendingDown className="w-3 h-3 text-red-600" />
              ) : null}
              <span className={`text-sm font-medium ${
                trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-neutral-600'
              }`}>
                {trendPercentage > 0 ? '+' : ''}{trendPercentage.toFixed(1)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

RevenueTooltip.displayName = 'RevenueTooltip';

// Performance metrics component
const PerformanceMetrics = memo(({ data }: { data: any[] }) => {
  const metrics = useMemo(() => {
    if (!data || data.length === 0) return null;

    const totalRevenue = data.reduce((sum, item) => sum + (item.revenue || 0), 0);
    const totalOrders = data.reduce((sum, item) => sum + (item.orders || 0), 0);
    const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

    const revenueGrowth = data.length > 1
      ? ((data[data.length - 1].revenue - data[0].revenue) / data[0].revenue) * 100
      : 0;

    return { totalRevenue, totalOrders, avgOrderValue, revenueGrowth };
  }, [data]);

  if (!metrics) return null;

  const formatCOP = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 p-3 rounded-lg">
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-primary-600" />
          <span className="text-xs font-medium text-primary-600">Ingresos Totales</span>
        </div>
        <p className="text-sm font-bold text-primary-900 mt-1">
          {formatCOP(metrics.totalRevenue)}
        </p>
      </div>

      <div className="bg-gradient-to-r from-secondary-50 to-secondary-100 p-3 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-secondary-600">Órdenes Totales</span>
        </div>
        <p className="text-sm font-bold text-secondary-900 mt-1">
          {metrics.totalOrders.toLocaleString()}
        </p>
      </div>

      <div className="bg-gradient-to-r from-accent-50 to-accent-100 p-3 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-accent-600">Valor Promedio</span>
        </div>
        <p className="text-sm font-bold text-accent-900 mt-1">
          {formatCOP(metrics.avgOrderValue)}
        </p>
      </div>

      <div className={`bg-gradient-to-r p-3 rounded-lg ${
        metrics.revenueGrowth >= 0
          ? 'from-green-50 to-green-100'
          : 'from-red-50 to-red-100'
      }`}>
        <div className="flex items-center gap-2">
          {metrics.revenueGrowth >= 0 ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <span className={`text-xs font-medium ${
            metrics.revenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            Crecimiento
          </span>
        </div>
        <p className={`text-sm font-bold mt-1 ${
          metrics.revenueGrowth >= 0 ? 'text-green-900' : 'text-red-900'
        }`}>
          {metrics.revenueGrowth > 0 ? '+' : ''}{metrics.revenueGrowth.toFixed(1)}%
        </p>
      </div>
    </div>
  );
});

PerformanceMetrics.displayName = 'PerformanceMetrics';

export const RevenueChart: React.FC<RevenueChartProps> = memo(({
  height = 400,
  showComparison = true,
  showBrush = false,
  mobile = false,
  className = '',
  onPeriodSelect
}) => {
  const data = useFilteredTrends();
  const { setChartRenderTime } = useAnalyticsActions();
  const [selectedRange, setSelectedRange] = useState<{ startIndex?: number; endIndex?: number }>({});

  // Performance tracking
  const renderStart = performance.now();

  React.useEffect(() => {
    const renderTime = performance.now() - renderStart;
    setChartRenderTime(renderTime);
  }, [data, setChartRenderTime, renderStart]);

  // Process data with previous period comparison
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    return data.map((item, index) => {
      const previousItem = index > 0 ? data[index - 1] : null;

      return {
        name: item.month,
        revenue: item.revenue,
        orders: item.orders,
        customers: item.customers || 0,
        previousRevenue: previousItem?.revenue,
        timestamp: item.timestamp
      };
    });
  }, [data]);

  // Handle brush selection for drill-down
  const handleBrushChange = useCallback((brushData: any) => {
    if (brushData && brushData.startIndex !== undefined && brushData.endIndex !== undefined) {
      setSelectedRange({
        startIndex: brushData.startIndex,
        endIndex: brushData.endIndex
      });

      if (onPeriodSelect && chartData.length > 0) {
        const startItem = chartData[brushData.startIndex];
        const endItem = chartData[brushData.endIndex];

        onPeriodSelect({
          start: startItem.timestamp || startItem.name,
          end: endItem.timestamp || endItem.name
        });
      }
    }
  }, [chartData, onPeriodSelect]);

  // Handle chart click for drill-down
  const handleChartClick = useCallback((data: any) => {
    if (data && data.activePayload?.[0]?.payload) {
      const clickedData = data.activePayload[0].payload;
      console.log('Revenue chart clicked:', clickedData);

      // Could trigger drill-down modal or navigation
      // Example: navigate to detailed view for selected period
    }
  }, []);

  if (!chartData || chartData.length === 0) {
    return (
      <div className={`bg-white p-6 rounded-lg border border-neutral-200 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <p className="text-neutral-500">No hay datos de ingresos disponibles</p>
        </div>
      </div>
    );
  }

  const chartConfig = {
    margin: mobile
      ? { top: 10, right: 10, left: 10, bottom: showBrush ? 50 : 10 }
      : { top: 20, right: 30, left: 20, bottom: showBrush ? 70 : 20 }
  };

  return (
    <div className={`bg-white p-6 rounded-lg border border-neutral-200 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          Tendencia de Ingresos
        </h3>
        <p className="text-sm text-neutral-600">
          Análisis de rendimiento de ventas e ingresos en el tiempo
        </p>
      </div>

      <PerformanceMetrics data={chartData} />

      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={chartConfig.margin}
            onClick={handleChartClick}
            style={{ cursor: 'pointer' }}
          >
            <defs>
              <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />

            <XAxis
              dataKey="name"
              tick={{ fontSize: mobile ? 10 : 12 }}
              tickLine={false}
              axisLine={false}
            />

            <YAxis
              tick={{ fontSize: mobile ? 10 : 12 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => {
                if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
                if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
                return `$${value}`;
              }}
            />

            <Tooltip content={<RevenueTooltip />} />

            {/* Revenue area chart */}
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#3b82f6"
              strokeWidth={mobile ? 2 : 3}
              fill="url(#revenueGradient)"
              animationDuration={1000}
            />

            {/* Orders line chart */}
            <Line
              type="monotone"
              dataKey="orders"
              stroke="#10b981"
              strokeWidth={mobile ? 1 : 2}
              dot={{ r: mobile ? 2 : 4, strokeWidth: 0 }}
              activeDot={{ r: mobile ? 4 : 6, strokeWidth: 0 }}
              yAxisId="right"
              animationDuration={1000}
            />

            {/* Comparison line (previous period) */}
            {showComparison && (
              <Line
                type="monotone"
                dataKey="previousRevenue"
                stroke="#94a3b8"
                strokeWidth={1}
                strokeDasharray="5,5"
                dot={false}
                activeDot={false}
                animationDuration={1000}
              />
            )}

            {/* Average revenue reference line */}
            <ReferenceLine
              y={chartData.reduce((sum, item) => sum + item.revenue, 0) / chartData.length}
              stroke="#f97316"
              strokeDasharray="3,3"
              strokeWidth={1}
              label={{ value: "Promedio", position: "topRight", fontSize: 10 }}
            />

            {/* Brush for period selection */}
            {showBrush && (
              <Brush
                dataKey="name"
                height={30}
                stroke="#3b82f6"
                onChange={handleBrushChange}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {selectedRange.startIndex !== undefined && selectedRange.endIndex !== undefined && (
        <div className="mt-3 p-3 bg-primary-50 rounded-lg">
          <p className="text-sm text-primary-700">
            <strong>Período seleccionado:</strong> {chartData[selectedRange.startIndex]?.name} - {chartData[selectedRange.endIndex]?.name}
          </p>
        </div>
      )}
    </div>
  );
});

RevenueChart.displayName = 'RevenueChart';

export default RevenueChart;