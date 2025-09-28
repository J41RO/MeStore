/**
 * DashboardCard Component
 *
 * Reusable card component for displaying metrics and data in admin dashboards.
 * Supports various display modes including stats, charts, and custom content.
 *
 * Features:
 * - Responsive design with mobile-first approach
 * - Loading states with skeleton animations
 * - Error handling with retry functionality
 * - Accessibility compliance (WCAG AA)
 * - Theme support and customization
 * - Performance optimized with React.memo
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, { memo, ReactNode, useMemo } from 'react';
import {
  Loader2,
  AlertCircle,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  Info
} from 'lucide-react';

/**
 * Trend direction for metrics
 */
export type TrendDirection = 'up' | 'down' | 'neutral';

/**
 * Card size variants
 */
export type CardSize = 'sm' | 'md' | 'lg' | 'xl';

/**
 * Card theme variants
 */
export type CardTheme = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';

/**
 * DashboardCard component props
 */
export interface DashboardCardProps {
  /** Card title */
  title: string;

  /** Card subtitle or description */
  subtitle?: string;

  /** Main value to display */
  value?: string | number;

  /** Previous value for trend calculation */
  previousValue?: string | number;

  /** Manual trend direction override */
  trend?: TrendDirection;

  /** Trend percentage change */
  trendPercentage?: number;

  /** Card content (overrides value/trend display) */
  children?: ReactNode;

  /** Loading state */
  isLoading?: boolean;

  /** Error state */
  error?: string | null;

  /** Retry callback for error state */
  onRetry?: () => void;

  /** Card size variant */
  size?: CardSize;

  /** Card theme variant */
  theme?: CardTheme;

  /** Custom icon component */
  icon?: React.ComponentType<any>;

  /** Icon color override */
  iconColor?: string;

  /** Additional CSS classes */
  className?: string;

  /** Click handler */
  onClick?: () => void;

  /** Whether card is clickable */
  clickable?: boolean;

  /** Format function for displaying values */
  formatValue?: (value: string | number) => string;

  /** Footer content */
  footer?: ReactNode;

  /** Custom actions in header */
  actions?: ReactNode;

  /** Test ID for testing */
  testId?: string;
}

/**
 * DashboardCard Component
 */
export const DashboardCard: React.FC<DashboardCardProps> = memo(({
  title,
  subtitle,
  value,
  previousValue,
  trend,
  trendPercentage,
  children,
  isLoading = false,
  error = null,
  onRetry,
  size = 'md',
  theme = 'default',
  icon: Icon,
  iconColor,
  className = '',
  onClick,
  clickable = false,
  formatValue = (val) => String(val),
  footer,
  actions,
  testId = 'dashboard-card'
}) => {
  /**
   * Calculate trend direction from values
   */
  const calculatedTrend = useMemo((): TrendDirection => {
    if (trend) return trend;

    if (typeof value === 'number' && typeof previousValue === 'number') {
      if (value > previousValue) return 'up';
      if (value < previousValue) return 'down';
      return 'neutral';
    }

    return 'neutral';
  }, [value, previousValue, trend]);

  /**
   * Calculate trend percentage
   */
  const calculatedTrendPercentage = useMemo((): number => {
    if (trendPercentage !== undefined) return trendPercentage;

    if (typeof value === 'number' && typeof previousValue === 'number' && previousValue !== 0) {
      return ((value - previousValue) / Math.abs(previousValue)) * 100;
    }

    return 0;
  }, [value, previousValue, trendPercentage]);

  /**
   * Size classes mapping
   */
  const sizeClasses = useMemo(() => {
    const sizes = {
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-6',
      xl: 'p-8'
    };
    return sizes[size];
  }, [size]);

  /**
   * Theme classes mapping
   */
  const themeClasses = useMemo(() => {
    const themes = {
      default: 'bg-white border-gray-200',
      primary: 'bg-blue-50 border-blue-200',
      success: 'bg-green-50 border-green-200',
      warning: 'bg-yellow-50 border-yellow-200',
      danger: 'bg-red-50 border-red-200',
      info: 'bg-indigo-50 border-indigo-200'
    };
    return themes[theme];
  }, [theme]);

  /**
   * Trend icon and color
   */
  const trendDisplay = useMemo(() => {
    const trendIcons = {
      up: TrendingUp,
      down: TrendingDown,
      neutral: Minus
    };

    const trendColors = {
      up: 'text-green-600',
      down: 'text-red-600',
      neutral: 'text-gray-400'
    };

    const TrendIcon = trendIcons[calculatedTrend];

    return {
      icon: TrendIcon,
      color: trendColors[calculatedTrend],
      percentage: Math.abs(calculatedTrendPercentage)
    };
  }, [calculatedTrend, calculatedTrendPercentage]);

  /**
   * Card container classes
   */
  const cardClasses = useMemo(() => `
    ${sizeClasses}
    ${themeClasses}
    border rounded-lg shadow-sm transition-all duration-200
    ${clickable || onClick ? 'cursor-pointer hover:shadow-md hover:border-gray-300' : ''}
    ${className}
  `.trim(), [sizeClasses, themeClasses, clickable, onClick, className]);

  /**
   * Render loading state
   */
  if (isLoading) {
    return (
      <div className={cardClasses} data-testid={`${testId}-loading`}>
        <div className="animate-pulse">
          <div className="flex items-start justify-between mb-4">
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-24"></div>
              <div className="h-3 bg-gray-200 rounded w-32"></div>
            </div>
            {Icon && (
              <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
            )}
          </div>
          <div className="space-y-2">
            <div className="h-8 bg-gray-200 rounded w-20"></div>
            <div className="h-4 bg-gray-200 rounded w-16"></div>
          </div>
        </div>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <div className={`${cardClasses} border-red-200 bg-red-50`} data-testid={`${testId}-error`}>
        <div className="flex items-center justify-center flex-col space-y-4 text-center">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <div>
            <h3 className="text-lg font-medium text-red-900">{title}</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  /**
   * Main render
   */
  return (
    <div
      className={cardClasses}
      onClick={onClick}
      data-testid={testId}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={clickable ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      } : undefined}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">
              {subtitle}
            </p>
          )}
        </div>

        <div className="flex items-center space-x-2 ml-4">
          {actions}
          {Icon && (
            <div className={`p-2 rounded-lg ${theme === 'default' ? 'bg-gray-100' : 'bg-white/50'}`}>
              <Icon
                className={`w-6 h-6 ${iconColor || 'text-gray-600'}`}
                aria-hidden="true"
              />
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-2">
        {children ? (
          children
        ) : (
          <>
            {/* Value Display */}
            {value !== undefined && (
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold text-gray-900 ${size === 'lg' || size === 'xl' ? 'text-3xl' : ''}`}>
                  {formatValue(value)}
                </span>

                {/* Trend Indicator */}
                {(calculatedTrendPercentage !== 0 || trend) && (
                  <div className={`flex items-center space-x-1 ${trendDisplay.color}`}>
                    <trendDisplay.icon className="w-4 h-4" aria-hidden="true" />
                    <span className="text-sm font-medium">
                      {trendDisplay.percentage.toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      {footer && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
});

/**
 * Display name for debugging
 */
DashboardCard.displayName = 'DashboardCard';

/**
 * Default export
 */
export default DashboardCard;