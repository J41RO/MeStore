/**
 * Admin Common Components Index
 *
 * Centralized export for all reusable admin components.
 * Provides easy imports and consistent API access.
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

// Dashboard Components
export { default as DashboardCard } from './DashboardCard';
export type {
  DashboardCardProps,
  TrendDirection,
  CardSize,
  CardTheme
} from './DashboardCard';

// Data Components
export { default as DataTable } from './DataTable';
export type {
  DataTableProps,
  TableColumn,
  SortConfig,
  FilterConfig,
  PaginationConfig,
  BulkAction
} from './DataTable';

// Filter Components
export { default as FilterPanel } from './FilterPanel';
export type {
  FilterPanelProps,
  FilterDefinition,
  ActiveFilter,
  FilterPreset,
  FilterType,
  FilterOperator
} from './FilterPanel';

// Status Components
export { default as StatusBadge } from './StatusBadge';
export {
  SuccessBadge,
  ErrorBadge,
  WarningBadge,
  InfoBadge,
  PendingBadge,
  ActiveBadge,
  InactiveBadge,
  ProcessingBadge
} from './StatusBadge';
export type {
  StatusBadgeProps,
  StatusVariant,
  StatusSize
} from './StatusBadge';

/**
 * Common component utilities and helpers
 */
export const commonComponentUtils = {
  /**
   * Format currency values
   */
  formatCurrency: (value: number, currency = 'COP'): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  },

  /**
   * Format percentage values
   */
  formatPercentage: (value: number, decimals = 1): string => {
    return `${value.toFixed(decimals)}%`;
  },

  /**
   * Format large numbers with suffixes
   */
  formatNumber: (value: number): string => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  },

  /**
   * Format date values
   */
  formatDate: (date: Date | string, format: 'short' | 'medium' | 'long' = 'medium'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    const options: Intl.DateTimeFormatOptions = {
      short: { month: 'short', day: 'numeric' },
      medium: { month: 'short', day: 'numeric', year: 'numeric' },
      long: { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }
    };

    return new Intl.DateTimeFormat('es-CO', options[format]).format(dateObj);
  },

  /**
   * Get relative time string
   */
  getRelativeTime: (date: Date | string): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

    if (diffInSeconds < 60) return 'hace un momento';
    if (diffInSeconds < 3600) return `hace ${Math.floor(diffInSeconds / 60)} minutos`;
    if (diffInSeconds < 86400) return `hace ${Math.floor(diffInSeconds / 3600)} horas`;
    if (diffInSeconds < 2592000) return `hace ${Math.floor(diffInSeconds / 86400)} días`;

    return commonComponentUtils.formatDate(dateObj, 'medium');
  },

  /**
   * Generate consistent color schemes for charts and visualizations
   */
  getColorScheme: (type: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info') => {
    const schemes = {
      primary: ['#3B82F6', '#1D4ED8', '#1E40AF', '#1E3A8A'],
      secondary: ['#6B7280', '#4B5563', '#374151', '#1F2937'],
      success: ['#10B981', '#047857', '#065F46', '#064E3B'],
      warning: ['#F59E0B', '#D97706', '#B45309', '#92400E'],
      danger: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
      info: ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6']
    };
    return schemes[type];
  },

  /**
   * Validate and sanitize user input
   */
  sanitizeInput: (input: string): string => {
    return input.trim().replace(/[<>]/g, '');
  },

  /**
   * Generate consistent spacing classes
   */
  getSpacingClass: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'): string => {
    const spacings = {
      xs: 'p-2 gap-2',
      sm: 'p-4 gap-4',
      md: 'p-6 gap-6',
      lg: 'p-8 gap-8',
      xl: 'p-12 gap-12'
    };
    return spacings[size];
  }
};

/**
 * Common responsive breakpoints for components
 */
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
};

/**
 * Common color palette for consistent theming
 */
export const colorPalette = {
  primary: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    200: '#BFDBFE',
    300: '#93C5FD',
    400: '#60A5FA',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
    800: '#1E40AF',
    900: '#1E3A8A'
  },
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827'
  },
  success: {
    50: '#ECFDF5',
    100: '#D1FAE5',
    200: '#A7F3D0',
    300: '#6EE7B7',
    400: '#34D399',
    500: '#10B981',
    600: '#059669',
    700: '#047857',
    800: '#065F46',
    900: '#064E3B'
  },
  warning: {
    50: '#FFFBEB',
    100: '#FEF3C7',
    200: '#FDE68A',
    300: '#FCD34D',
    400: '#FBBF24',
    500: '#F59E0B',
    600: '#D97706',
    700: '#B45309',
    800: '#92400E',
    900: '#78350F'
  },
  danger: {
    50: '#FEF2F2',
    100: '#FEE2E2',
    200: '#FECACA',
    300: '#FCA5A5',
    400: '#F87171',
    500: '#EF4444',
    600: '#DC2626',
    700: '#B91C1C',
    800: '#991B1B',
    900: '#7F1D1D'
  }
};