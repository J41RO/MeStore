// frontend/src/components/vendor/charts/SimplePieChart.tsx
// PERFORMANCE_OPTIMIZED: Optimized pie chart with Canvas rendering and animations

import React, { useMemo, useRef, useEffect, useState, useCallback } from 'react';
import { CategorySales } from '../../../stores/analyticsStore';

interface SimplePieChartProps {
  data: CategorySales[];
  size?: number;
  showLegend?: boolean;
  showAnimation?: boolean;
  className?: string;
}

// Memoized formatters
const formatCOP = (amount: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    notation: 'compact'
  }).format(amount);
};

// Memoized legend item component
const LegendItem = React.memo<{
  item: CategorySales;
  total: number;
  isVisible: boolean;
  delay: number;
}>(({ item, total, isVisible, delay }) => {
  const [opacity, setOpacity] = useState(0);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setOpacity(1);
      }, delay);
      return () => clearTimeout(timer);
    }
  }, [isVisible, delay]);

  const percentage = total > 0 ? (item.sales / total) * 100 : 0;

  return (
    <div
      className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-neutral-50 transition-all duration-200"
      style={{
        opacity,
        transform: `translateY(${opacity === 0 ? '10px' : '0'})`,
        transition: 'opacity 0.3s ease, transform 0.3s ease'
      }}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div
          className="w-4 h-4 rounded-full flex-shrink-0 shadow-sm"
          style={{ backgroundColor: item.color }}
        />
        <span className="text-sm font-medium text-neutral-700 truncate">
          {item.category}
        </span>
      </div>
      <div className="text-right flex-shrink-0">
        <div className="text-sm font-semibold text-neutral-900">
          {item.sales} ventas
        </div>
        <div className="text-xs text-neutral-500">
          {percentage.toFixed(1)}% • {formatCOP(item.revenue)}
        </div>
      </div>
    </div>
  );
});

LegendItem.displayName = 'LegendItem';

// Canvas-based pie chart for performance
const CanvasPieChart = React.memo<{
  data: CategorySales[];
  size: number;
  showAnimation: boolean;
  isVisible: boolean;
}>(({ data, size, showAnimation, isVisible }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [animationProgress, setAnimationProgress] = useState(0);

  const { chartData, total } = useMemo(() => {
    const totalSales = data.reduce((sum, item) => sum + item.sales, 0);
    let currentAngle = -Math.PI / 2; // Start at top

    const processedData = data.map(item => {
      const percentage = totalSales > 0 ? item.sales / totalSales : 0;
      const angle = percentage * 2 * Math.PI;
      const result = {
        ...item,
        percentage,
        startAngle: currentAngle,
        endAngle: currentAngle + angle,
        angle
      };
      currentAngle += angle;
      return result;
    });

    return { chartData: processedData, total: totalSales };
  }, [data]);

  const drawChart = useCallback((progress: number = 1) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = size / 2;
    const centerY = size / 2;
    const radius = (size - 40) / 2; // Leave margin

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

    // Enable anti-aliasing
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // Draw pie slices
    chartData.forEach((item, index) => {
      const animatedEndAngle = item.startAngle + (item.angle * progress);

      if (animatedEndAngle > item.startAngle) {
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, item.startAngle, animatedEndAngle);
        ctx.closePath();

        // Gradient fill for visual appeal
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
        gradient.addColorStop(0, item.color);
        gradient.addColorStop(1, item.color + '80'); // Add transparency

        ctx.fillStyle = gradient;
        ctx.fill();

        // Stroke for definition
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Add subtle shadow
        ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
        ctx.shadowBlur = 3;
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;
      }
    });

    // Reset shadow
    ctx.shadowColor = 'transparent';

    // Draw center circle for donut effect
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.4, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = '#f3f4f6';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Add center text
    ctx.fillStyle = '#374151';
    ctx.font = 'bold 14px system-ui';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${total}`, centerX, centerY - 8);

    ctx.font = '12px system-ui';
    ctx.fillStyle = '#6b7280';
    ctx.fillText('ventas', centerX, centerY + 8);
  }, [chartData, size, total]);

  // Animation effect
  useEffect(() => {
    if (!showAnimation || !isVisible) {
      setAnimationProgress(1);
      drawChart(1);
      return;
    }

    const duration = 1500; // 1.5 seconds
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);

      setAnimationProgress(easeOutCubic);
      drawChart(easeOutCubic);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [showAnimation, isVisible, drawChart]);

  // Static draw for non-animated charts
  useEffect(() => {
    if (!showAnimation) {
      drawChart(1);
    }
  }, [showAnimation, drawChart]);

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      className="mx-auto"
      style={{ maxWidth: '100%', height: 'auto' }}
    />
  );
});

CanvasPieChart.displayName = 'CanvasPieChart';

export const SimplePieChart: React.FC<SimplePieChartProps> = React.memo(({
  data,
  size = 200,
  showLegend = true,
  showAnimation = true,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  // Memoize calculations
  const { processedData, total, hasData } = useMemo(() => {
    if (!data || data.length === 0) {
      return { processedData: [], total: 0, hasData: false };
    }

    const totalSales = data.reduce((sum, item) => sum + item.sales, 0);
    const sorted = [...data]
      .filter(item => item.sales > 0)
      .sort((a, b) => b.sales - a.sales);

    return {
      processedData: sorted,
      total: totalSales,
      hasData: sorted.length > 0
    };
  }, [data]);

  // Intersection Observer for performance
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Empty state
  if (!hasData) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height: size }}>
        <div className="text-center">
          <div className="text-neutral-400 mb-2">
            <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
          <p className="text-xs text-neutral-500">Sin datos de categorías</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`space-y-4 ${className}`}>
      {/* Canvas Chart */}
      <div className="flex justify-center">
        <CanvasPieChart
          data={processedData}
          size={size}
          showAnimation={showAnimation}
          isVisible={isVisible}
        />
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="space-y-1">
          {processedData.map((item, index) => (
            <LegendItem
              key={item.category}
              item={item}
              total={total}
              isVisible={isVisible}
              delay={index * 100}
            />
          ))}
        </div>
      )}

      {/* Performance indicator */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 text-xs text-neutral-400">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          Canvas optimizado
        </div>
      </div>
    </div>
  );
});

SimplePieChart.displayName = 'SimplePieChart';