/**
 * LoadingSpinner Component
 *
 * Reusable spinner component with multiple size and color variants.
 * Supports fullscreen overlay mode for blocking operations.
 *
 * Features:
 * - Multiple sizes (sm, md, lg, xl)
 * - Color variants (primary, secondary, white)
 * - Fullscreen overlay mode
 * - Optional loading message
 * - Accessible with ARIA attributes
 *
 * Usage:
 * ```tsx
 * <LoadingSpinner size="md" color="primary" />
 * <LoadingSpinner fullScreen message="Loading data..." />
 * ```
 */

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  fullScreen?: boolean;
  message?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  fullScreen = false,
  message,
  className = '',
}) => {
  // Size mappings
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
    xl: 'h-16 w-16 border-4',
  };

  // Color mappings
  const colorClasses = {
    primary: 'border-blue-600 border-t-transparent',
    secondary: 'border-gray-600 border-t-transparent',
    white: 'border-white border-t-transparent',
    gray: 'border-gray-400 border-t-transparent',
  };

  const spinnerClasses = `
    animate-spin
    rounded-full
    ${sizeClasses[size]}
    ${colorClasses[color]}
    ${className}
  `.trim();

  const spinner = (
    <div
      className={spinnerClasses}
      role="status"
      aria-label={message || 'Loading'}
    >
      <span className="sr-only">{message || 'Loading...'}</span>
    </div>
  );

  // Fullscreen overlay mode
  if (fullScreen) {
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
        aria-busy="true"
        aria-live="polite"
      >
        <div className="bg-white rounded-lg shadow-2xl p-8 flex flex-col items-center gap-4">
          <div className={sizeClasses.xl + ' ' + colorClasses.primary + ' animate-spin rounded-full'}>
            <span className="sr-only">Loading...</span>
          </div>
          {message && (
            <p className="text-gray-700 font-medium text-center max-w-xs">
              {message}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Inline mode with optional message
  if (message) {
    return (
      <div className="flex flex-col items-center gap-3" aria-busy="true">
        {spinner}
        <p className="text-sm text-gray-600 font-medium">{message}</p>
      </div>
    );
  }

  // Simple spinner
  return spinner;
};

export default LoadingSpinner;

/**
 * Button Loading Spinner
 * Specialized spinner for button states
 */
export const ButtonSpinner: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg
    className={`animate-spin h-4 w-4 ${className}`}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

/**
 * Inline Loading Indicator
 * Small inline spinner with text
 */
export const InlineLoader: React.FC<{ text?: string }> = ({ text = 'Loading' }) => (
  <div className="inline-flex items-center gap-2 text-sm text-gray-600">
    <LoadingSpinner size="sm" color="gray" />
    <span>{text}...</span>
  </div>
);
