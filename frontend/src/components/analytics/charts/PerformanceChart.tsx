// frontend/src/components/analytics/charts/PerformanceChart.tsx
// PERFORMANCE_OPTIMIZED: Base chart component with memoization and mobile optimization
// Target: <500ms render time, 60fps animations

import React, { memo, useMemo, useRef, useEffect } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

export interface PerformanceChartProps {
  data: ChartDataPoint[];
  width?: number;
  height?: number;
  type?: 'line' | 'area' | 'bar' | 'composed';
  colors?: string[];
  showGrid?: boolean;
  showTooltip?: boolean;
  showLegend?: boolean;
  loading?: boolean;
  className?: string;
  onDataPointClick?: (data: ChartDataPoint) => void;
  responsive?: boolean;
  animate?: boolean;
  mobile?: boolean;
}

// Memoized tooltip component for performance
const CustomTooltip = memo(({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white p-3 border border-neutral-200 rounded-lg shadow-lg">
      <p className="text-sm font-semibold text-neutral-900 mb-1">{label}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-sm" style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
        </p>
      ))}
    </div>
  );
});

CustomTooltip.displayName = 'CustomTooltip';

// Memoized loading skeleton
const ChartSkeleton = memo(({ height }: { height: number }) => (
  <div
    className="bg-neutral-100 rounded-lg animate-pulse"
    style={{ height }}
  >
    <div className="flex items-end justify-around h-full p-4">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="bg-neutral-300 rounded"
          style={{
            height: `${Math.random() * 60 + 40}%`,
            width: '12%'
          }}
        />
      ))}
    </div>
  </div>
));

ChartSkeleton.displayName = 'ChartSkeleton';

export const PerformanceChart: React.FC<PerformanceChartProps> = memo(({
  data,
  width,
  height = 300,
  type = 'line',
  colors = ['#3b82f6', '#10b981', '#f97316', '#8b5cf6'],
  showGrid = true,
  showTooltip = true,
  showLegend = false,
  loading = false,
  className = '',
  onDataPointClick,
  responsive = true,
  animate = true,
  mobile = false
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const renderStartTime = useRef(0);

  // Performance tracking
  useEffect(() => {
    renderStartTime.current = performance.now();

    const handleLoad = () => {
      const renderTime = performance.now() - renderStartTime.current;
      if (renderTime > 500) {
        console.warn(`Chart render time exceeded target: ${renderTime.toFixed(2)}ms`);
      }
    };

    // Use requestAnimationFrame to measure after render
    requestAnimationFrame(handleLoad);
  }, [data]);

  // Memoized chart configuration for performance
  const chartConfig = useMemo(() => ({
    margin: mobile
      ? { top: 10, right: 10, left: 10, bottom: 10 }
      : { top: 20, right: 30, left: 20, bottom: 20 },
    strokeWidth: mobile ? 1 : 2,
    dot: mobile ? false : { strokeWidth: 2, r: 4 },
    activeDot: mobile ? { r: 3 } : { r: 6, strokeWidth: 0 }
  }), [mobile]);

  // Memoized data processing
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Optimize data for mobile (reduce points if needed)
    if (mobile && data.length > 20) {
      const step = Math.ceil(data.length / 20);
      return data.filter((_, index) => index % step === 0);
    }

    return data;
  }, [data, mobile]);

  // Handle loading state
  if (loading) {
    return <ChartSkeleton height={height} />;
  }

  // Handle empty data
  if (!processedData || processedData.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-neutral-50 rounded-lg"
        style={{ height }}
      >
        <p className="text-neutral-500 text-sm">No hay datos disponibles</p>
      </div>
    );
  }

  // Chart click handler
  const handleClick = (data: any) => {
    if (onDataPointClick && data && data.activePayload?.[0]?.payload) {
      onDataPointClick(data.activePayload[0].payload);
    }
  };

  // Render chart based on type
  const renderChart = () => {
    const commonProps = {
      data: processedData,
      margin: chartConfig.margin,
      onClick: handleClick,
      style: { cursor: onDataPointClick ? 'pointer' : 'default' }
    };

    const dataKeys = useMemo(() => {
      if (processedData.length === 0) return [];
      return Object.keys(processedData[0]).filter(key =>
        key !== 'name' && typeof processedData[0][key] === 'number'
      );
    }, [processedData]);

    switch (type) {
      case 'area':
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
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
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {dataKeys.map((key, index) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stackId="1"
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={0.3}
                strokeWidth={chartConfig.strokeWidth}
                animationDuration={animate ? 1000 : 0}
              />
            ))}
          </ComposedChart>
        );

      case 'bar':
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
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
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {dataKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={colors[index % colors.length]}
                radius={[2, 2, 0, 0]}
                animationDuration={animate ? 1000 : 0}
              />
            ))}
          </ComposedChart>
        );

      case 'composed':
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
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
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {dataKeys.slice(0, 2).map((key, index) => (
              <Bar
                key={`bar-${key}`}
                dataKey={key}
                fill={colors[index % colors.length]}
                radius={[2, 2, 0, 0]}
                animationDuration={animate ? 1000 : 0}
              />
            ))}
            {dataKeys.slice(2).map((key, index) => (
              <Line
                key={`line-${key}`}
                type="monotone"
                dataKey={key}
                stroke={colors[(index + 2) % colors.length]}
                strokeWidth={chartConfig.strokeWidth}
                dot={chartConfig.dot}
                activeDot={chartConfig.activeDot}
                animationDuration={animate ? 1000 : 0}
              />
            ))}
          </ComposedChart>
        );

      default: // line
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
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
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {dataKeys.map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={colors[index % colors.length]}
                strokeWidth={chartConfig.strokeWidth}
                dot={chartConfig.dot}
                activeDot={chartConfig.activeDot}
                animationDuration={animate ? 1000 : 0}
              />
            ))}
          </ComposedChart>
        );
    }
  };

  return (
    <div ref={chartRef} className={className}>
      <ResponsiveContainer
        width={responsive ? '100%' : width}
        height={height}
      >
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
});

PerformanceChart.displayName = 'PerformanceChart';

export default PerformanceChart;