/**
 * Route Synchronization Component
 *
 * Automatically synchronizes navigation state with React Router location
 * to ensure the correct navigation item is highlighted based on the current route.
 *
 * Features:
 * - Automatic active item detection from pathname
 * - Category expansion on route change
 * - Breadcrumb generation
 * - Route change analytics tracking
 *
 * @version 1.0.0
 * @author Integration Quality AI
 */

import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigation } from './NavigationProvider';
import { enterpriseNavigationConfig } from './NavigationConfig';

/**
 * RouteSync Component Props
 */
interface RouteSyncProps {
  /** Whether to enable automatic breadcrumb updates */
  enableBreadcrumbs?: boolean;

  /** Whether to enable analytics tracking */
  enableAnalytics?: boolean;

  /** Custom route mapping for legacy paths */
  routeMapping?: Record<string, string>;
}

/**
 * RouteSync Component
 */
export const RouteSync: React.FC<RouteSyncProps> = ({
  enableBreadcrumbs = true,
  enableAnalytics = true,
  routeMapping = {}
}) => {
  const location = useLocation();
  const { actions, utils } = useNavigation();

  /**
   * Find navigation item by pathname
   */
  const findItemByPath = (pathname: string): string | null => {
    // Remove base path if present
    const cleanPath = pathname.replace('/admin-secure-portal', '');

    // Check direct path matches
    for (const category of enterpriseNavigationConfig) {
      for (const item of category.items) {
        const itemPath = item.path.replace('/admin-secure-portal', '');
        if (itemPath === cleanPath) {
          return item.id;
        }
      }
    }

    // Check for partial path matches (for nested routes)
    for (const category of enterpriseNavigationConfig) {
      for (const item of category.items) {
        const itemPath = item.path.replace('/admin-secure-portal', '');
        if (cleanPath.startsWith(itemPath) && itemPath !== '/') {
          return item.id;
        }
      }
    }

    // Check custom route mapping
    const mappedPath = routeMapping[cleanPath];
    if (mappedPath) {
      return findItemByPath(mappedPath);
    }

    return null;
  };

  /**
   * Update navigation state based on current route
   */
  useEffect(() => {
    const itemId = findItemByPath(location.pathname);

    if (itemId) {
      // Set active item (this will also set the active category)
      actions.setActiveItem(itemId);

      // Track analytics if enabled
      if (enableAnalytics) {
        const item = utils.getItemById(itemId);
        const category = utils.getCategoryByItemId(itemId);

        if (item && category) {
          actions.trackEvent({
            type: 'navigate',
            target: {
              type: 'item',
              id: itemId,
              title: item.title
            },
            timestamp: new Date(),
            metadata: {
              pathname: location.pathname,
              category: category.title,
              source: 'route_sync'
            }
          });
        }
      }
    }
  }, [location.pathname, actions, utils, enableAnalytics]);

  /**
   * Update document title and breadcrumbs
   */
  useEffect(() => {
    if (enableBreadcrumbs) {
      const itemId = findItemByPath(location.pathname);

      if (itemId) {
        const breadcrumb = utils.getBreadcrumb(itemId);

        if (breadcrumb.length > 0) {
          // Update document title
          const title = breadcrumb.length > 1
            ? `${breadcrumb[1]} - ${breadcrumb[0]} - MeStore Admin`
            : `${breadcrumb[0]} - MeStore Admin`;

          document.title = title;

          // Dispatch breadcrumb update event for other components
          window.dispatchEvent(new CustomEvent('breadcrumb-update', {
            detail: { breadcrumb, pathname: location.pathname }
          }));
        }
      }
    }
  }, [location.pathname, utils, enableBreadcrumbs]);

  // This component doesn't render anything
  return null;
};

/**
 * Hook for custom route synchronization
 */
export const useRouteSync = () => {
  const location = useLocation();
  const { state, actions, utils } = useNavigation();

  /**
   * Manually sync route
   */
  const syncRoute = (pathname: string = location.pathname) => {
    // Implementation here would be similar to the component logic
    // This allows manual synchronization if needed
  };

  /**
   * Check if current route is active
   */
  const isRouteActive = (path: string) => {
    return utils.isActiveByPath(path, location.pathname);
  };

  /**
   * Get current breadcrumb
   */
  const getCurrentBreadcrumb = () => {
    const cleanPath = location.pathname.replace('/admin-secure-portal', '');

    for (const category of enterpriseNavigationConfig) {
      for (const item of category.items) {
        const itemPath = item.path.replace('/admin-secure-portal', '');
        if (itemPath === cleanPath || (cleanPath.startsWith(itemPath) && itemPath !== '/')) {
          return utils.getBreadcrumb(item.id);
        }
      }
    }

    return [];
  };

  return {
    syncRoute,
    isRouteActive,
    getCurrentBreadcrumb,
    currentPath: location.pathname,
    activeItemId: state.activeItemId,
    activeCategoryId: state.activeCategoryId
  };
};

/**
 * Default export
 */
export default RouteSync;