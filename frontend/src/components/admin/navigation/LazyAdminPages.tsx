/**
 * Lazy Loading System for Admin Pages
 *
 * Enterprise-grade lazy loading implementation with intelligent preloading,
 * error boundaries, and performance monitoring for admin pages.
 *
 * Features:
 * - Dynamic imports with code splitting
 * - Intelligent preloading based on user behavior
 * - Fallback components with skeleton loading
 * - Error boundaries for failed loads
 * - Performance monitoring and metrics
 * - Bundle size optimization
 * - Memory management
 *
 * @version 1.0.0
 * @author Frontend Performance AI
 */

import React, {
  Suspense,
  lazy,
  useEffect,
  useCallback,
  useMemo,
  useRef,
  useState
} from 'react';
import { ErrorBoundary } from 'react-error-boundary';

import { usePerformanceMonitor } from './PerformanceMonitor';
import type { NavigationItem, UserRole } from './NavigationTypes';

/**
 * Lazy loading configuration
 */
interface LazyLoadConfig {
  preloadDelay: number;        // Delay before preloading (ms)
  intersectionThreshold: number; // Intersection threshold for preloading
  maxConcurrentLoads: number;   // Maximum concurrent loads
  retryAttempts: number;        // Number of retry attempts
  retryDelay: number;          // Delay between retries (ms)
  cacheExpiryMs: number;       // Cache expiry time
}

const DEFAULT_CONFIG: LazyLoadConfig = {
  preloadDelay: 2000,
  intersectionThreshold: 0.1,
  maxConcurrentLoads: 3,
  retryAttempts: 3,
  retryDelay: 1000,
  cacheExpiryMs: 300000 // 5 minutes
};

/**
 * Admin page definitions with lazy loading
 */
interface AdminPageDefinition {
  id: string;
  path: string;
  title: string;
  component: () => Promise<{ default: React.ComponentType<any> }>;
  preload?: boolean;
  requiredRole?: UserRole;
  dependencies?: string[];
  estimatedSize?: number; // Estimated bundle size in KB
}

/**
 * Define all admin pages with lazy loading
 */
const adminPageDefinitions: AdminPageDefinition[] = [
  // Dashboard & Analytics
  {
    id: 'superuser-dashboard',
    path: '/admin/dashboard',
    title: 'Dashboard',
    component: () => import('../SuperuserDashboard'),
    preload: true,
    requiredRole: 'admin',
    estimatedSize: 150
  },
  {
    id: 'global-kpis',
    path: '/admin/analytics/kpis',
    title: 'Global KPIs',
    component: () => import('../GlobalKPIs'),
    requiredRole: 'manager',
    estimatedSize: 80
  },

  // User Management
  {
    id: 'user-management',
    path: '/admin/users',
    title: 'User Management',
    component: () => import('../UserDataTable'),
    requiredRole: 'admin',
    dependencies: ['user-filters', 'user-modals'],
    estimatedSize: 120
  },
  {
    id: 'user-create',
    path: '/admin/users/create',
    title: 'Create User',
    component: () => import('../UserCreateModal'),
    requiredRole: 'admin',
    estimatedSize: 90
  },
  {
    id: 'user-details',
    path: '/admin/users/details',
    title: 'User Details',
    component: () => import('../UserDetailsModal'),
    requiredRole: 'admin',
    estimatedSize: 100
  },

  // Vendor Management
  {
    id: 'vendor-list',
    path: '/admin/vendors',
    title: 'Vendor List',
    component: () => import('../VendorList'),
    requiredRole: 'manager',
    estimatedSize: 140
  },
  {
    id: 'vendor-detail',
    path: '/admin/vendors/detail',
    title: 'Vendor Detail',
    component: () => import('../VendorDetail'),
    requiredRole: 'manager',
    estimatedSize: 180
  },

  // Inventory Management
  {
    id: 'incoming-products',
    path: '/admin/inventory/incoming',
    title: 'Incoming Products',
    component: () => import('../IncomingProductsQueue'),
    requiredRole: 'operator',
    estimatedSize: 200
  },
  {
    id: 'inventory-audit',
    path: '/admin/inventory/audit',
    title: 'Inventory Audit',
    component: () => import('../InventoryAuditPanel'),
    requiredRole: 'operator',
    estimatedSize: 160
  },
  {
    id: 'product-verification',
    path: '/admin/inventory/verification',
    title: 'Product Verification',
    component: () => import('../ProductVerificationWorkflow'),
    requiredRole: 'operator',
    estimatedSize: 180
  },
  {
    id: 'quality-checklist',
    path: '/admin/inventory/quality',
    title: 'Quality Checklist',
    component: () => import('../QualityChecklistForm'),
    requiredRole: 'operator',
    estimatedSize: 140
  },

  // Warehouse Management
  {
    id: 'location-manager',
    path: '/admin/warehouse/locations',
    title: 'Location Manager',
    component: () => import('../LocationManager'),
    requiredRole: 'manager',
    estimatedSize: 120
  },
  {
    id: 'movement-tracker',
    path: '/admin/warehouse/movements',
    title: 'Movement Tracker',
    component: () => import('../MovementTracker'),
    requiredRole: 'operator',
    estimatedSize: 110
  },
  {
    id: 'warehouse-map',
    path: '/admin/warehouse/map',
    title: 'Warehouse Map',
    component: () => import('../WarehouseMap'),
    requiredRole: 'operator',
    estimatedSize: 160
  },
  {
    id: 'storage-manager',
    path: '/admin/warehouse/storage',
    title: 'Storage Manager',
    component: () => import('../StorageManagerDashboard'),
    requiredRole: 'manager',
    estimatedSize: 140
  },
  {
    id: 'space-optimizer',
    path: '/admin/warehouse/optimizer',
    title: 'Space Optimizer',
    component: () => import('../SpaceOptimizerDashboard'),
    requiredRole: 'manager',
    estimatedSize: 180
  },

  // Forms & Tools
  {
    id: 'qr-generator',
    path: '/admin/tools/qr-generator',
    title: 'QR Generator',
    component: () => import('../QRGeneratorForm'),
    requiredRole: 'operator',
    estimatedSize: 80
  },
  {
    id: 'location-assignment',
    path: '/admin/tools/location-assignment',
    title: 'Location Assignment',
    component: () => import('../LocationAssignmentForm'),
    requiredRole: 'operator',
    estimatedSize: 120
  },
  {
    id: 'product-rejection',
    path: '/admin/tools/product-rejection',
    title: 'Product Rejection',
    component: () => import('../ProductRejectionForm'),
    requiredRole: 'operator',
    estimatedSize: 90
  },

  // Reports
  {
    id: 'discrepancy-report',
    path: '/admin/reports/discrepancies',
    title: 'Discrepancy Report',
    component: () => import('../ReporteDiscrepancias'),
    requiredRole: 'manager',
    estimatedSize: 160
  },
  {
    id: 'incident-report',
    path: '/admin/reports/incidents',
    title: 'Incident Report',
    component: () => import('../ReportarIncidente'),
    requiredRole: 'operator',
    estimatedSize: 70
  }
];

/**
 * Lazy loading cache and state management
 */
class LazyLoadManager {
  private cache = new Map<string, Promise<React.ComponentType<any>>>();
  private loadingStates = new Map<string, boolean>();
  private retryAttempts = new Map<string, number>();
  private preloadQueue: string[] = [];
  private activeDloads = 0;
  private config: LazyLoadConfig;

  constructor(config: LazyLoadConfig = DEFAULT_CONFIG) {
    this.config = config;
  }

  /**
   * Load component with retry logic
   */
  async loadComponent(pageId: string): Promise<React.ComponentType<any>> {
    const definition = adminPageDefinitions.find(p => p.id === pageId);
    if (!definition) {
      throw new Error(`Page definition not found: ${pageId}`);
    }

    // Check cache first
    const cached = this.cache.get(pageId);
    if (cached) {
      return cached;
    }

    // Check if already loading
    if (this.loadingStates.get(pageId)) {
      // Wait for existing load to complete
      return new Promise((resolve, reject) => {
        const checkInterval = setInterval(() => {
          const cachedResult = this.cache.get(pageId);
          if (cachedResult) {
            clearInterval(checkInterval);
            resolve(cachedResult);
          }
        }, 100);

        setTimeout(() => {
          clearInterval(checkInterval);
          reject(new Error(`Timeout loading ${pageId}`));
        }, 10000);
      });
    }

    this.loadingStates.set(pageId, true);
    this.activeDloads++;

    const loadPromise = this.loadWithRetry(definition);
    this.cache.set(pageId, loadPromise);

    try {
      const component = await loadPromise;
      this.retryAttempts.delete(pageId);
      return component;
    } catch (error) {
      this.cache.delete(pageId);
      throw error;
    } finally {
      this.loadingStates.set(pageId, false);
      this.activeDloads--;
      this.processPreloadQueue();
    }
  }

  /**
   * Load with retry logic
   */
  private async loadWithRetry(definition: AdminPageDefinition): Promise<React.ComponentType<any>> {
    const attempts = this.retryAttempts.get(definition.id) || 0;

    try {
      const startTime = performance.now();
      const module = await definition.component();
      const endTime = performance.now();

      // Track performance
      if (typeof window !== 'undefined' && (window as any).__navigationPerformanceTracker) {
        (window as any).__navigationPerformanceTracker('componentLoad', endTime - startTime);
      }

      return module.default;
    } catch (error) {
      if (attempts < this.config.retryAttempts) {
        this.retryAttempts.set(definition.id, attempts + 1);

        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));

        return this.loadWithRetry(definition);
      }

      throw new Error(`Failed to load ${definition.id} after ${attempts + 1} attempts: ${error}`);
    }
  }

  /**
   * Preload component
   */
  preload(pageId: string): void {
    if (this.cache.has(pageId) || this.loadingStates.get(pageId)) {
      return;
    }

    if (this.activeDloads >= this.config.maxConcurrentLoads) {
      if (!this.preloadQueue.includes(pageId)) {
        this.preloadQueue.push(pageId);
      }
      return;
    }

    this.loadComponent(pageId).catch(error => {
      console.warn(`Failed to preload ${pageId}:`, error);
    });
  }

  /**
   * Process preload queue
   */
  private processPreloadQueue(): void {
    while (this.preloadQueue.length > 0 && this.activeDloads < this.config.maxConcurrentLoads) {
      const pageId = this.preloadQueue.shift();
      if (pageId) {
        this.preload(pageId);
      }
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): { cached: number; loading: number; queued: number } {
    return {
      cached: this.cache.size,
      loading: this.activeDloads,
      queued: this.preloadQueue.length
    };
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
    this.loadingStates.clear();
    this.retryAttempts.clear();
    this.preloadQueue.length = 0;
    this.activeDloads = 0;
  }
}

// Global lazy load manager instance
const lazyLoadManager = new LazyLoadManager();

/**
 * Skeleton loading component
 */
const AdminPageSkeleton: React.FC<{ pageId: string }> = ({ pageId }) => (
  <div className="animate-pulse space-y-4 p-6">
    <div className="h-8 bg-gray-200 rounded w-1/3"></div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-gray-100 rounded-lg p-4 space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      ))}
    </div>
  </div>
);

/**
 * Error fallback component
 */
const LazyLoadErrorFallback: React.FC<{
  error: Error;
  resetErrorBoundary: () => void;
  pageId: string;
}> = ({ error, resetErrorBoundary, pageId }) => (
  <div className="flex flex-col items-center justify-center p-8 bg-red-50 rounded-lg border border-red-200">
    <div className="text-red-600 text-lg font-semibold mb-2">
      Failed to load page
    </div>
    <div className="text-red-500 text-sm mb-4">
      {error.message}
    </div>
    <button
      onClick={resetErrorBoundary}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    >
      Try Again
    </button>
  </div>
);

/**
 * Lazy admin page component wrapper
 */
export interface LazyAdminPageProps {
  pageId: string;
  userRole: UserRole;
  fallback?: React.ComponentType;
  [key: string]: any;
}

export const LazyAdminPage: React.FC<LazyAdminPageProps> = ({
  pageId,
  userRole,
  fallback: CustomFallback,
  ...props
}) => {
  const { trackStart, trackEnd } = usePerformanceMonitor();
  const [LazyComponent, setLazyComponent] = useState<React.ComponentType<any> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const mountedRef = useRef(true);

  // Check if user has access to this page
  const pageDefinition = useMemo(() =>
    adminPageDefinitions.find(p => p.id === pageId),
    [pageId]
  );

  const hasAccess = useMemo(() => {
    if (!pageDefinition?.requiredRole) return true;

    const roleHierarchy = {
      viewer: 0,
      operator: 1,
      manager: 2,
      admin: 3,
      superuser: 4
    };

    return roleHierarchy[userRole] >= roleHierarchy[pageDefinition.requiredRole];
  }, [pageDefinition, userRole]);

  /**
   * Load component effect
   */
  useEffect(() => {
    if (!hasAccess || !pageDefinition) {
      setIsLoading(false);
      return;
    }

    const loadTime = trackStart('lazyPageLoad');

    lazyLoadManager.loadComponent(pageId)
      .then(component => {
        if (mountedRef.current) {
          setLazyComponent(() => component);
          setError(null);
        }
      })
      .catch(err => {
        if (mountedRef.current) {
          setError(err);
        }
      })
      .finally(() => {
        if (mountedRef.current) {
          setIsLoading(false);
          trackEnd('lazyPageLoad', loadTime);
        }
      });

    return () => {
      mountedRef.current = false;
    };
  }, [pageId, hasAccess, pageDefinition, trackStart, trackEnd]);

  // Handle access denied
  if (!hasAccess) {
    return (
      <div className="flex items-center justify-center p-8 bg-yellow-50 rounded-lg border border-yellow-200">
        <div className="text-yellow-800 text-center">
          <div className="text-lg font-semibold mb-2">Access Denied</div>
          <div className="text-sm">
            You don't have permission to access this page.
          </div>
        </div>
      </div>
    );
  }

  // Handle page not found
  if (!pageDefinition) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-gray-600 text-center">
          <div className="text-lg font-semibold mb-2">Page Not Found</div>
          <div className="text-sm">
            The requested admin page "{pageId}" was not found.
          </div>
        </div>
      </div>
    );
  }

  // Handle loading state
  if (isLoading) {
    return CustomFallback ? (
      <CustomFallback />
    ) : (
      <AdminPageSkeleton pageId={pageId} />
    );
  }

  // Handle error state
  if (error) {
    return (
      <LazyLoadErrorFallback
        error={error}
        resetErrorBoundary={() => {
          setError(null);
          setIsLoading(true);
          lazyLoadManager.clearCache();
        }}
        pageId={pageId}
      />
    );
  }

  // Render the loaded component
  if (LazyComponent) {
    return <LazyComponent {...props} />;
  }

  // Fallback to skeleton if component is null
  return <AdminPageSkeleton pageId={pageId} />;
};

/**
 * Preloader hook for intelligent preloading
 */
export const useAdminPagePreloader = () => {
  const preloadTimeoutRef = useRef<NodeJS.Timeout>();

  const preloadPage = useCallback((pageId: string, delay: number = DEFAULT_CONFIG.preloadDelay) => {
    if (preloadTimeoutRef.current) {
      clearTimeout(preloadTimeoutRef.current);
    }

    preloadTimeoutRef.current = setTimeout(() => {
      lazyLoadManager.preload(pageId);
    }, delay);
  }, []);

  const preloadRelatedPages = useCallback((currentPageId: string) => {
    const currentDef = adminPageDefinitions.find(p => p.id === currentPageId);
    if (!currentDef) return;

    // Preload dependencies
    if (currentDef.dependencies) {
      currentDef.dependencies.forEach(depId => {
        lazyLoadManager.preload(depId);
      });
    }

    // Preload pages marked for preloading
    adminPageDefinitions
      .filter(p => p.preload && p.id !== currentPageId)
      .forEach(p => {
        preloadPage(p.id, 1000); // Shorter delay for preload-marked pages
      });
  }, [preloadPage]);

  const getStats = useCallback(() => lazyLoadManager.getStats(), []);

  useEffect(() => {
    return () => {
      if (preloadTimeoutRef.current) {
        clearTimeout(preloadTimeoutRef.current);
      }
    };
  }, []);

  return {
    preloadPage,
    preloadRelatedPages,
    getStats
  };
};

/**
 * Admin page router with lazy loading
 */
export const LazyAdminPageRouter: React.FC<{
  pageId: string;
  userRole: UserRole;
  [key: string]: any;
}> = ({ pageId, userRole, ...props }) => {
  return (
    <ErrorBoundary
      FallbackComponent={(fallbackProps) => (
        <LazyLoadErrorFallback {...fallbackProps} pageId={pageId} />
      )}
      onError={(error, errorInfo) => {
        console.error(`Lazy load error for page ${pageId}:`, error, errorInfo);
      }}
    >
      <Suspense fallback={<AdminPageSkeleton pageId={pageId} />}>
        <LazyAdminPage pageId={pageId} userRole={userRole} {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

export { adminPageDefinitions };
export default LazyAdminPage;