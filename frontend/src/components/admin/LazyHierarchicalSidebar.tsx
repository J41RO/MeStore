import React, { lazy, Suspense, memo } from 'react';

// Lazy load del componente principal del sidebar
const HierarchicalSidebar = lazy(() => import('./HierarchicalSidebar').then(module => ({
  default: module.HierarchicalSidebar
})));

// Componente de fallback mientras carga
const SidebarSkeleton: React.FC = memo(() => (
  <div className="animate-pulse" data-testid="sidebar-skeleton">
    {/* Skeleton para las categorías */}
    {[1, 2, 3, 4].map((index) => (
      <div key={index} className="mb-6">
        {/* Header skeleton */}
        <div className="flex items-center justify-between px-3 py-3 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-5 h-5 mr-3 bg-gray-300 rounded" />
            <div className="h-4 bg-gray-300 rounded w-24" />
          </div>
          <div className="w-4 h-4 bg-gray-300 rounded" />
        </div>

        {/* Items skeleton */}
        <div className="mt-2 space-y-1">
          {[1, 2, 3].map((itemIndex) => (
            <div key={itemIndex} className="flex items-center px-3 py-2">
              <div className="w-5 h-5 mr-3 bg-gray-200 rounded" />
              <div className="h-3 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
));

SidebarSkeleton.displayName = 'SidebarSkeleton';

// Props del componente lazy
export interface LazyHierarchicalSidebarProps {
  onClose?: () => void;
  className?: string;
}

// Componente LazyHierarchicalSidebar con performance optimizations
export const LazyHierarchicalSidebar: React.FC<LazyHierarchicalSidebarProps> = memo(({
  onClose,
  className = ''
}) => {
  return (
    <Suspense
      fallback={<SidebarSkeleton />}
    >
      <HierarchicalSidebar
        onClose={onClose}
        className={className}
      />
    </Suspense>
  );
});

LazyHierarchicalSidebar.displayName = 'LazyHierarchicalSidebar';

// Re-export para compatibilidad
export { HierarchicalSidebar as EagerHierarchicalSidebar } from './HierarchicalSidebar';