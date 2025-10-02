import React from 'react';

/**
 * DevOnly Component
 *
 * Wrapper component that ONLY renders children in development mode.
 * In production, this component returns null, ensuring debug tools are never visible.
 *
 * Security Features:
 * - Double check: Verifies both DEV and PROD env variables
 * - Production safety: Always returns null if PROD is true
 * - Development convenience: Only renders in actual development environment
 *
 * Usage:
 * ```tsx
 * <DevOnly>
 *   <DebugPanel />
 * </DevOnly>
 * ```
 *
 * @example
 * // Wrapping debug overlays
 * <DevOnly>
 *   <div className="fixed bottom-4 right-4 bg-black text-white p-4">
 *     Debug Info: {someState}
 *   </div>
 * </DevOnly>
 */
export const DevOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Double security check
  const isDevelopment = import.meta.env.DEV === true;
  const isProduction = import.meta.env.PROD === true;

  // CRITICAL: If production flag is true, NEVER render
  if (isProduction) {
    return null;
  }

  // CRITICAL: Only render if explicitly in development
  if (!isDevelopment) {
    return null;
  }

  // Safe to render in development
  return <>{children}</>;
};

/**
 * DevOnlyConsole
 *
 * Utility for console logging that only works in development.
 * In production, all console methods are no-ops.
 *
 * Usage:
 * ```tsx
 * import { DevOnlyConsole } from './DevOnly';
 *
 * DevOnlyConsole.log('Debug info:', data);
 * DevOnlyConsole.warn('Warning:', error);
 * ```
 */
export const DevOnlyConsole = {
  log: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.log('[DEV]', ...args);
    }
  },
  warn: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.warn('[DEV]', ...args);
    }
  },
  error: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.error('[DEV]', ...args);
    }
  },
  info: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.info('[DEV]', ...args);
    }
  },
  debug: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.debug('[DEV]', ...args);
    }
  },
  table: (data: any) => {
    if (import.meta.env.DEV) {
      console.table(data);
    }
  },
};

/**
 * useDevOnly Hook
 *
 * Returns true only in development mode.
 * Useful for conditional rendering or logic.
 *
 * @returns {boolean} - True if in development, false in production
 *
 * @example
 * const isDev = useDevOnly();
 *
 * return (
 *   <div>
 *     {isDev && <DebugInfo />}
 *   </div>
 * );
 */
export const useDevOnly = (): boolean => {
  const isDevelopment = import.meta.env.DEV === true;
  const isProduction = import.meta.env.PROD === true;

  // Safety first: If production, always return false
  if (isProduction) return false;

  return isDevelopment;
};

/**
 * DevOnlyScript
 *
 * Component for running scripts/effects only in development.
 * Useful for debugging, logging, or development-only side effects.
 *
 * @param {() => void} onMount - Function to run on component mount (dev only)
 *
 * @example
 * <DevOnlyScript onMount={() => {
 *   console.log('Development mode initialized');
 *   // Other dev-only setup
 * }} />
 */
export const DevOnlyScript: React.FC<{ onMount?: () => void }> = ({ onMount }) => {
  React.useEffect(() => {
    if (import.meta.env.DEV && onMount) {
      onMount();
    }
  }, [onMount]);

  return null;
};

export default DevOnly;
