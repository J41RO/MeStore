/**
 * Admin Hooks Index
 *
 * Centralized export for all admin-related custom hooks.
 */

// User Management Hooks
export { useUserManagement } from './useUserManagement';
export type { User, UserFilters } from './useUserManagement';

// Vendor Management Hooks
export { useVendorManagement } from './useVendorManagement';
export type { Vendor } from './useVendorManagement';

// Analytics Hooks
export { useAnalytics } from './useAnalytics';
export type { AnalyticsData } from './useAnalytics';

// Settings Hooks
export { useSettings } from './useSettings';
export type { SystemSettings } from './useSettings';

/**
 * Common hook utilities
 */
export const adminHookUtils = {
  /**
   * Debounce function for search inputs
   */
  useDebounce: <T>(value: T, delay: number): T => {
    const [debouncedValue, setDebouncedValue] = React.useState(value);

    React.useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, delay);

      return () => {
        clearTimeout(handler);
      };
    }, [value, delay]);

    return debouncedValue;
  },

  /**
   * Format error messages consistently
   */
  formatError: (error: unknown): string => {
    if (error instanceof Error) {
      return error.message;
    }
    if (typeof error === 'string') {
      return error;
    }
    return 'An unexpected error occurred';
  },

  /**
   * Handle API responses consistently
   */
  handleApiResponse: async <T>(
    apiCall: () => Promise<T>,
    onSuccess?: (data: T) => void,
    onError?: (error: string) => void
  ): Promise<T | null> => {
    try {
      const result = await apiCall();
      onSuccess?.(result);
      return result;
    } catch (error) {
      const errorMessage = adminHookUtils.formatError(error);
      onError?.(errorMessage);
      return null;
    }
  }
};

/**
 * Re-export React for hook utilities
 */
import React from 'react';