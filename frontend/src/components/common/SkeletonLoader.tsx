/**
 * SkeletonLoader Component
 *
 * Skeleton screens for better perceived performance during loading.
 * Provides visual placeholders that match the final content layout.
 *
 * Features:
 * - Multiple variants (text, circular, rectangular, card)
 * - Customizable dimensions
 * - Pulse animation
 * - Grid support for lists
 * - Accessible loading states
 *
 * Usage:
 * ```tsx
 * <SkeletonLoader variant="text" count={3} />
 * <SkeletonLoader variant="card" count={5} />
 * <SkeletonLoader variant="rectangular" width="100%" height={200} />
 * ```
 */

import React from 'react';

interface SkeletonLoaderProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card' | 'table-row' | 'stats-card';
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
  animation?: 'pulse' | 'wave' | 'none';
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'rectangular',
  width,
  height,
  count = 1,
  className = '',
  animation = 'pulse',
}) => {
  // Animation classes
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  // Base skeleton styles
  const baseClasses = `bg-gray-200 ${animationClasses[animation]} ${className}`;

  // Variant-specific rendering
  const renderSkeleton = (index: number) => {
    const key = `skeleton-${index}`;

    switch (variant) {
      case 'text':
        return (
          <div
            key={key}
            className={`${baseClasses} h-4 rounded mb-2`}
            style={{ width: width || `${Math.random() * 30 + 70}%` }}
            role="status"
            aria-label="Loading content"
          />
        );

      case 'circular':
        const size = width || height || 40;
        return (
          <div
            key={key}
            className={`${baseClasses} rounded-full`}
            style={{ width: size, height: size }}
            role="status"
            aria-label="Loading"
          />
        );

      case 'rectangular':
        return (
          <div
            key={key}
            className={`${baseClasses} rounded`}
            style={{ width: width || '100%', height: height || 100 }}
            role="status"
            aria-label="Loading content"
          />
        );

      case 'card':
        return (
          <div
            key={key}
            className="bg-white rounded-lg shadow p-6 mb-4"
            role="status"
            aria-label="Loading card"
          >
            <div className="flex gap-4">
              {/* Image placeholder */}
              <div className={`${baseClasses} w-20 h-20 rounded flex-shrink-0`} />

              {/* Content placeholder */}
              <div className="flex-1 space-y-3">
                <div className={`${baseClasses} h-5 rounded w-3/4`} />
                <div className={`${baseClasses} h-4 rounded w-full`} />
                <div className={`${baseClasses} h-4 rounded w-5/6`} />

                {/* Footer */}
                <div className="flex gap-2 pt-2">
                  <div className={`${baseClasses} h-8 rounded w-24`} />
                  <div className={`${baseClasses} h-8 rounded w-24`} />
                </div>
              </div>
            </div>
          </div>
        );

      case 'table-row':
        return (
          <tr key={key} className="border-b border-gray-200">
            <td className="px-6 py-4">
              <div className={`${baseClasses} h-4 rounded w-32`} />
            </td>
            <td className="px-6 py-4">
              <div className={`${baseClasses} h-4 rounded w-48`} />
            </td>
            <td className="px-6 py-4">
              <div className={`${baseClasses} h-4 rounded w-24`} />
            </td>
            <td className="px-6 py-4">
              <div className={`${baseClasses} h-4 rounded w-20`} />
            </td>
            <td className="px-6 py-4">
              <div className="flex gap-2">
                <div className={`${baseClasses} h-8 w-8 rounded`} />
                <div className={`${baseClasses} h-8 w-8 rounded`} />
              </div>
            </td>
          </tr>
        );

      case 'stats-card':
        return (
          <div
            key={key}
            className="bg-white rounded-lg shadow p-6"
            role="status"
            aria-label="Loading statistics"
          >
            <div className={`${baseClasses} h-4 rounded w-24 mb-3`} />
            <div className={`${baseClasses} h-8 rounded w-16`} />
          </div>
        );

      default:
        return (
          <div
            key={key}
            className={`${baseClasses} rounded`}
            style={{ width: width || '100%', height: height || 20 }}
            role="status"
            aria-label="Loading"
          />
        );
    }
  };

  return (
    <div className="skeleton-container" aria-busy="true" aria-live="polite">
      {Array.from({ length: count }, (_, index) => renderSkeleton(index))}
    </div>
  );
};

export default SkeletonLoader;

/**
 * Skeleton Table Component
 * Specialized skeleton for table layouts
 */
export const SkeletonTable: React.FC<{
  rows?: number;
  columns?: number;
}> = ({ rows = 5, columns = 5 }) => (
  <div className="overflow-x-auto">
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          {Array.from({ length: columns }, (_, i) => (
            <th key={i} className="px-6 py-3">
              <div className="animate-pulse bg-gray-300 h-4 rounded w-24" />
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        <SkeletonLoader variant="table-row" count={rows} />
      </tbody>
    </table>
  </div>
);

/**
 * Skeleton Grid Component
 * Grid layout for card skeletons
 */
export const SkeletonGrid: React.FC<{
  count?: number;
  columns?: number;
}> = ({ count = 6, columns = 3 }) => {
  const gridClass = `grid grid-cols-1 md:grid-cols-${columns} gap-4`;

  return (
    <div className={gridClass}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="bg-white rounded-lg shadow p-6 space-y-3">
          <div className="animate-pulse bg-gray-200 h-40 rounded" />
          <div className="animate-pulse bg-gray-200 h-5 rounded w-3/4" />
          <div className="animate-pulse bg-gray-200 h-4 rounded w-full" />
          <div className="animate-pulse bg-gray-200 h-4 rounded w-5/6" />
        </div>
      ))}
    </div>
  );
};

/**
 * Skeleton Stats Cards
 * Specialized skeleton for statistics dashboard
 */
export const SkeletonStatsCards: React.FC<{ count?: number }> = ({ count = 4 }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <SkeletonLoader variant="stats-card" count={count} />
  </div>
);

/**
 * Skeleton Order Card
 * Specialized skeleton for order listings
 */
export const SkeletonOrderCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow overflow-hidden mb-4">
    {/* Header */}
    <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
      <div className="flex justify-between items-start">
        <div className="space-y-2">
          <div className="animate-pulse bg-gray-300 h-6 rounded w-40" />
          <div className="animate-pulse bg-gray-300 h-4 rounded w-32" />
        </div>
        <div className="space-y-2 text-right">
          <div className="animate-pulse bg-gray-300 h-4 rounded w-24 ml-auto" />
          <div className="animate-pulse bg-gray-300 h-5 rounded w-32 ml-auto" />
        </div>
      </div>
    </div>

    {/* Content */}
    <div className="px-6 py-4 space-y-4">
      {[1, 2].map((i) => (
        <div key={i} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="animate-pulse bg-gray-300 w-16 h-16 rounded flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="animate-pulse bg-gray-300 h-5 rounded w-3/4" />
            <div className="animate-pulse bg-gray-300 h-4 rounded w-1/2" />
            <div className="flex gap-4">
              <div className="animate-pulse bg-gray-300 h-4 rounded w-20" />
              <div className="animate-pulse bg-gray-300 h-4 rounded w-24" />
            </div>
          </div>
        </div>
      ))}
    </div>

    {/* Footer */}
    <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
      <div className="flex justify-between items-center">
        <div className="animate-pulse bg-gray-300 h-4 rounded w-48" />
        <div className="animate-pulse bg-gray-300 h-8 rounded w-32" />
      </div>
    </div>
  </div>
);
