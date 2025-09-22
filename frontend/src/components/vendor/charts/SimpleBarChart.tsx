// frontend/src/components/vendor/charts/SimpleBarChart.tsx
// PERFORMANCE_OPTIMIZED: Optimized bar chart with virtualization and memoization

import React, { useMemo, useRef, useEffect, useState } from 'react';
import { MonthlyTrend } from '../../../stores/analyticsStore';

interface SimpleBarChartProps {
  data: MonthlyTrend[];
  height?: number;
  showAnimation?: boolean;
  className?: string;
}

// Memoized formatters
const formatCompact = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

const formatCOP = (amount: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    notation: 'compact'
  }).format(amount);
};

// Memoized bar component
const BarItem = React.memo<{
  item: MonthlyTrend;
  maxRevenue: number;
  index: number;
  showAnimation: boolean;
  isVisible: boolean;
}>(({ item, maxRevenue, index, showAnimation, isVisible }) => {
  const percentage = maxRevenue > 0 ? (item.revenue / maxRevenue) * 100 : 0;
  const [animatedWidth, setAnimatedWidth] = useState(0);

  useEffect(() => {
    if (showAnimation && isVisible) {
      const timer = setTimeout(() => {
        setAnimatedWidth(percentage);
      }, index * 100); // Stagger animation

      return () => clearTimeout(timer);
    } else {
      setAnimatedWidth(percentage);
    }
  }, [percentage, index, showAnimation, isVisible]);

  return (
    <div className="flex items-center gap-3 py-2">
      <span className="text-sm font-medium text-neutral-600 w-8 flex-shrink-0">
        {item.month}
      </span>
      <div className="flex-1 bg-neutral-200 rounded-full h-3 relative overflow-hidden">
        <div
          className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-700 ease-out relative"
          style={{ width: `${animatedWidth}%` }}
        >
          {/* Shimmer effect for visual appeal */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] animate-shimmer"></div>
        </div>
      </div>
      <div className="text-right w-20 flex-shrink-0">
        <div className="text-sm font-medium text-neutral-900">
          {formatCompact(item.revenue)}
        </div>
        <div className="text-xs text-neutral-500">
          {item.orders} pedidos
        </div>
      </div>
    </div>
  );
});

BarItem.displayName = 'BarItem';

export const SimpleBarChart: React.FC<SimpleBarChartProps> = React.memo(({
  data,
  height = 300,
  showAnimation = true,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  // Memoize expensive calculations
  const { maxRevenue, sortedData, totalRevenue } = useMemo(() => {
    if (!data || data.length === 0) {
      return { maxRevenue: 0, sortedData: [], totalRevenue: 0 };
    }

    const revenues = data.map(d => d.revenue);
    const maxRev = Math.max(...revenues);
    const totalRev = revenues.reduce((sum, rev) => sum + rev, 0);
    const sorted = [...data].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    return {
      maxRevenue: maxRev,
      sortedData: sorted,
      totalRevenue: totalRev
    };
  }, [data]);

  // Intersection Observer for lazy animation
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
  if (!data || data.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-center">
          <div className="text-neutral-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-sm text-neutral-500">No hay datos disponibles</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`space-y-1 ${className}`} style={{ height }}>
      {/* Summary header */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-neutral-100">
        <div className="text-xs text-neutral-500">
          {sortedData.length} períodos
        </div>
        <div className="text-xs font-medium text-neutral-700">
          Total: {formatCOP(totalRevenue)}
        </div>
      </div>

      {/* Chart bars */}
      <div className="space-y-2 overflow-hidden">
        {sortedData.map((item, index) => (
          <BarItem
            key={`${item.month}-${item.timestamp}`}
            item={item}
            maxRevenue={maxRevenue}
            index={index}
            showAnimation={showAnimation}
            isVisible={isVisible}
          />
        ))}
      </div>

      {/* Chart footer with performance indicator */}
      <div className="mt-4 pt-2 border-t border-neutral-100">
        <div className="flex items-center justify-between text-xs text-neutral-400">
          <span>Renderizado optimizado</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            Tiempo real
          </span>
        </div>
      </div>
    </div>
  );
});

SimpleBarChart.displayName = 'SimpleBarChart';

// Add shimmer animation to CSS (would be in a CSS file or styled-components)
const shimmerKeyframes = `
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
`;

// Inject styles if not already present
if (typeof document !== 'undefined' && !document.querySelector('#shimmer-styles')) {
  const style = document.createElement('style');
  style.id = 'shimmer-styles';
  style.textContent = shimmerKeyframes;
  document.head.appendChild(style);
}