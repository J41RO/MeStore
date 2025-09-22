// frontend/src/components/analytics/charts/CategoryChart.tsx
// PERFORMANCE_OPTIMIZED: Interactive category sales chart with drill-down
// Target: Touch-optimized pie chart with <300ms interaction response

import React, { memo, useMemo, useState, useCallback } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { PieChart as PieChartIcon, BarChart3, Eye, TrendingUp } from 'lucide-react';
import { useFilteredCategories, useAnalyticsActions } from '../../../stores/analyticsStore';

interface CategoryChartProps {
  height?: number;
  chartType?: 'pie' | 'bar';
  showLegend?: boolean;
  showValues?: boolean;
  mobile?: boolean;
  className?: string;
  onCategoryClick?: (category: string) => void;
}

// Optimized color palette for categories
const CATEGORY_COLORS = [
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f97316', // Orange
  '#8b5cf6', // Purple
  '#ef4444', // Red
  '#06b6d4', // Cyan
  '#84cc16', // Lime
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#6366f1'  // Indigo
];

// Memoized custom tooltip
const CategoryTooltip = memo(({ active, payload }: any) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;

  const formatCOP = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="bg-white p-4 border border-neutral-200 rounded-lg shadow-lg">
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <p className="font-semibold text-neutral-900">{data.category}</p>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between gap-4">
          <span className="text-sm text-neutral-600">Ventas:</span>
          <span className="font-medium text-neutral-900">{data.sales}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-sm text-neutral-600">Ingresos:</span>
          <span className="font-medium text-primary-600">{formatCOP(data.revenue)}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-sm text-neutral-600">Participación:</span>
          <span className="font-medium text-secondary-600">{data.percentage}%</span>
        </div>
      </div>
    </div>
  );
});

CategoryTooltip.displayName = 'CategoryTooltip';

// Custom pie chart label
const renderCustomLabel = memo(({ cx, cy, midAngle, innerRadius, outerRadius, percentage, category, mobile }: any) => {
  if (mobile && percentage < 10) return null; // Hide small labels on mobile

  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={mobile ? 10 : 12}
      fontWeight="bold"
    >
      {percentage < 5 ? '' : `${percentage.toFixed(0)}%`}
    </text>
  );
});

renderCustomLabel.displayName = 'CustomLabel';

// Category summary cards
const CategorySummary = memo(({ data, onCategoryClick }: {
  data: any[];
  onCategoryClick?: (category: string) => void;
}) => {
  const totalSales = useMemo(() =>
    data.reduce((sum, item) => sum + item.sales, 0),
    [data]
  );

  const totalRevenue = useMemo(() =>
    data.reduce((sum, item) => sum + item.revenue, 0),
    [data]
  );

  const formatCOP = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
      {data.slice(0, 4).map((category, index) => (
        <div
          key={category.category}
          className="p-3 bg-gradient-to-r from-neutral-50 to-neutral-100 rounded-lg border border-neutral-200 cursor-pointer hover:shadow-md transition-all duration-200"
          onClick={() => onCategoryClick?.(category.category)}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: category.color }}
              />
              <span className="text-sm font-medium text-neutral-900 truncate">
                {category.category}
              </span>
            </div>
            <Eye className="w-4 h-4 text-neutral-400" />
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-neutral-600">Ventas:</span>
              <p className="font-semibold text-neutral-900">{category.sales}</p>
            </div>
            <div>
              <span className="text-neutral-600">Ingresos:</span>
              <p className="font-semibold text-primary-600 truncate">
                {formatCOP(category.revenue)}
              </p>
            </div>
          </div>

          <div className="mt-2 pt-2 border-t border-neutral-200">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-600">Participación:</span>
              <span className="text-xs font-bold text-secondary-600">
                {category.percentage}%
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
});

CategorySummary.displayName = 'CategorySummary';

export const CategoryChart: React.FC<CategoryChartProps> = memo(({
  height = 400,
  chartType = 'pie',
  showLegend = true,
  showValues = true,
  mobile = false,
  className = '',
  onCategoryClick
}) => {
  const data = useFilteredCategories();
  const { setChartRenderTime } = useAnalyticsActions();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Performance tracking
  const renderStart = performance.now();

  React.useEffect(() => {
    const renderTime = performance.now() - renderStart;
    setChartRenderTime(renderTime);
  }, [data, setChartRenderTime, renderStart]);

  // Process data for charts
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const totalSales = data.reduce((sum, item) => sum + item.sales, 0);

    return data.map((item, index) => ({
      ...item,
      percentage: totalSales > 0 ? Number(((item.sales / totalSales) * 100).toFixed(1)) : 0,
      color: item.color || CATEGORY_COLORS[index % CATEGORY_COLORS.length]
    }));
  }, [data]);

  // Handle chart interactions
  const handlePieClick = useCallback((data: any, index: number) => {
    if (data && data.category) {
      setSelectedCategory(data.category);
      onCategoryClick?.(data.category);
    }
  }, [onCategoryClick]);

  const handleBarClick = useCallback((data: any) => {
    if (data && data.activePayload?.[0]?.payload?.category) {
      const category = data.activePayload[0].payload.category;
      setSelectedCategory(category);
      onCategoryClick?.(category);
    }
  }, [onCategoryClick]);

  if (!chartData || chartData.length === 0) {
    return (
      <div className={`bg-white p-6 rounded-lg border border-neutral-200 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <p className="text-neutral-500">No hay datos de categorías disponibles</p>
        </div>
      </div>
    );
  }

  const renderChart = () => {
    if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            onClick={handleBarClick}
            style={{ cursor: 'pointer' }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="category"
              tick={{ fontSize: mobile ? 9 : 11 }}
              tickLine={false}
              axisLine={false}
              angle={mobile ? -45 : 0}
              textAnchor={mobile ? 'end' : 'middle'}
              height={mobile ? 60 : 40}
            />
            <YAxis
              tick={{ fontSize: mobile ? 10 : 12 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CategoryTooltip />} />
            <Bar
              dataKey="sales"
              radius={[4, 4, 0, 0]}
              animationDuration={1000}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      );
    }

    // Pie chart
    return (
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={showValues ? (props) => renderCustomLabel({ ...props, mobile }) : false}
            outerRadius={mobile ? 60 : 80}
            fill="#8884d8"
            dataKey="sales"
            onClick={handlePieClick}
            style={{ cursor: 'pointer' }}
            animationDuration={1000}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
                stroke={selectedCategory === entry.category ? '#374151' : 'none'}
                strokeWidth={selectedCategory === entry.category ? 2 : 0}
              />
            ))}
          </Pie>
          <Tooltip content={<CategoryTooltip />} />
          {showLegend && !mobile && (
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value, entry) => (
                <span style={{ color: entry.color }}>{value}</span>
              )}
            />
          )}
        </PieChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className={`bg-white p-6 rounded-lg border border-neutral-200 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
            {chartType === 'pie' ? (
              <PieChartIcon className="w-5 h-5 text-primary-600" />
            ) : (
              <BarChart3 className="w-5 h-5 text-primary-600" />
            )}
            Ventas por Categoría
          </h3>
          <p className="text-sm text-neutral-600">
            Distribución de ventas e ingresos por categoría de productos
          </p>
        </div>

        <button
          onClick={() => setSelectedCategory(null)}
          className="text-sm text-primary-600 hover:text-primary-800 transition-colors"
        >
          Ver todas
        </button>
      </div>

      <CategorySummary data={chartData} onCategoryClick={onCategoryClick} />

      <div style={{ height: mobile ? 300 : height }}>
        {renderChart()}
      </div>

      {selectedCategory && (
        <div className="mt-4 p-3 bg-primary-50 rounded-lg">
          <p className="text-sm text-primary-700">
            <strong>Categoría seleccionada:</strong> {selectedCategory}
          </p>
          <p className="text-xs text-primary-600 mt-1">
            Haz clic en "Ver todas" para mostrar todas las categorías
          </p>
        </div>
      )}
    </div>
  );
});

CategoryChart.displayName = 'CategoryChart';

export default CategoryChart;