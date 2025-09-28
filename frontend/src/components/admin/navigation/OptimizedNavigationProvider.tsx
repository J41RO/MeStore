/**
 * Optimized Enterprise Navigation Provider
 *
 * Advanced React Context provider with enterprise-grade performance optimizations,
 * including advanced memoization, batch updates, and performance monitoring.
 *
 * Performance Features:
 * - React.memo with deep equality checks
 * - useMemo for expensive computations
 * - useCallback for stable references
 * - Batched state updates
 * - Performance monitoring hooks
 * - Memory leak prevention
 * - Selective re-renders
 *
 * @version 2.0.0
 * @author Frontend Performance AI
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  useMemo,
  useRef,
  startTransition,
  unstable_batchedUpdates
} from 'react';
import { isEqual } from 'lodash-es';

import type {
  NavigationState,
  NavigationContextValue,
  NavigationActions,
  NavigationUtils,
  NavigationEvent,
  NavigationError,
  NavigationCategory,
  NavigationItem,
  UserRole,
  NavigationPreferences,
  NavigationProviderProps
} from './NavigationTypes';

import { enterpriseNavigationConfig, navigationConfigUtils } from './NavigationConfig';
import { usePerformanceMonitor } from './PerformanceMonitor';

/**
 * Navigation action types for reducer with performance optimization
 */
type NavigationAction =
  | { type: 'SET_ACTIVE_ITEM'; payload: string }
  | { type: 'SET_ACTIVE_CATEGORY'; payload: string }
  | { type: 'TOGGLE_CATEGORY'; payload: string }
  | { type: 'SET_CATEGORY_COLLAPSED'; payload: { categoryId: string; collapsed: boolean } }
  | { type: 'UPDATE_PREFERENCES'; payload: Partial<NavigationPreferences> }
  | { type: 'BATCH_UPDATE'; payload: Partial<NavigationState> }
  | { type: 'RESET_STATE' }
  | { type: 'TRACK_EVENT'; payload: NavigationEvent }
  | { type: 'HANDLE_ERROR'; payload: NavigationError }
  | { type: 'LOAD_PERSISTED_STATE'; payload: Partial<NavigationState> };

/**
 * Performance-optimized navigation state
 */
interface OptimizedNavigationState extends NavigationState {
  // Cache for computed values
  _cache: {
    filteredCategories: Map<UserRole, NavigationCategory[]>;
    itemLookup: Map<string, { item: NavigationItem; category: NavigationCategory }>;
    breadcrumbs: Map<string, string[]>;
    lastUpdate: number;
  };
}

/**
 * Default optimized state
 */
const defaultOptimizedState: OptimizedNavigationState = {
  activeItemId: null,
  activeCategoryId: null,
  collapsedState: {},
  preferences: {
    persistState: true,
    animations: true,
    compactMode: false,
    accessibility: {
      reduceMotion: false,
      highContrast: false,
      screenReader: false
    }
  },
  _cache: {
    filteredCategories: new Map(),
    itemLookup: new Map(),
    breadcrumbs: new Map(),
    lastUpdate: 0
  }
};

/**
 * Storage configuration
 */
const STORAGE_CONFIG = {
  STATE_KEY: 'mestore_admin_navigation_state_v2',
  PREFERENCES_KEY: 'mestore_admin_navigation_preferences_v2',
  METRICS_KEY: 'mestore_admin_navigation_metrics_v2',
  DEBOUNCE_MS: 300,
  CACHE_EXPIRY_MS: 30000 // 30 seconds
} as const;

/**
 * Performance optimized navigation reducer
 */
function optimizedNavigationReducer(
  state: OptimizedNavigationState,
  action: NavigationAction
): OptimizedNavigationState {
  const newState = { ...state };

  switch (action.type) {
    case 'SET_ACTIVE_ITEM':
      if (state.activeItemId === action.payload) return state;

      newState.activeItemId = action.payload;
      newState.activeCategoryId = getActiveCategoryId(action.payload);
      newState._cache.lastUpdate = Date.now();
      break;

    case 'SET_ACTIVE_CATEGORY':
      if (state.activeCategoryId === action.payload) return state;

      newState.activeCategoryId = action.payload;
      newState._cache.lastUpdate = Date.now();
      break;

    case 'TOGGLE_CATEGORY':
      const currentCollapsed = state.collapsedState[action.payload];
      newState.collapsedState = {
        ...state.collapsedState,
        [action.payload]: !currentCollapsed
      };
      newState._cache.lastUpdate = Date.now();
      break;

    case 'SET_CATEGORY_COLLAPSED':
      if (state.collapsedState[action.payload.categoryId] === action.payload.collapsed) {
        return state;
      }

      newState.collapsedState = {
        ...state.collapsedState,
        [action.payload.categoryId]: action.payload.collapsed
      };
      newState._cache.lastUpdate = Date.now();
      break;

    case 'UPDATE_PREFERENCES':
      if (isEqual(state.preferences, { ...state.preferences, ...action.payload })) {
        return state;
      }

      newState.preferences = {
        ...state.preferences,
        ...action.payload
      };
      newState._cache.lastUpdate = Date.now();
      break;

    case 'BATCH_UPDATE':
      Object.assign(newState, action.payload);
      newState._cache.lastUpdate = Date.now();
      break;

    case 'RESET_STATE':
      return { ...defaultOptimizedState };

    case 'LOAD_PERSISTED_STATE':
      Object.assign(newState, action.payload);
      newState._cache.lastUpdate = Date.now();
      break;

    case 'TRACK_EVENT':
      // Analytics tracking without state mutation
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', action.payload.type, {
          event_category: 'navigation',
          event_label: action.payload.target.id,
          custom_map: action.payload.metadata
        });
      }
      return state;

    case 'HANDLE_ERROR':
      console.error('Navigation Error:', action.payload);
      return state;

    default:
      return state;
  }

  // Clear cache if it's expired
  if (Date.now() - newState._cache.lastUpdate > STORAGE_CONFIG.CACHE_EXPIRY_MS) {
    newState._cache = {
      filteredCategories: new Map(),
      itemLookup: new Map(),
      breadcrumbs: new Map(),
      lastUpdate: newState._cache.lastUpdate
    };
  }

  return newState;
}

/**
 * Get active category ID with caching
 */
function getActiveCategoryId(itemId: string): string | null {
  const result = navigationConfigUtils.getItemById(itemId);
  return result?.category.id || null;
}

/**
 * Navigation context with performance optimization
 */
const OptimizedNavigationContext = createContext<NavigationContextValue | undefined>(undefined);

/**
 * Optimized Enterprise Navigation Provider Component
 */
export const OptimizedNavigationProvider: React.FC<NavigationProviderProps> = React.memo(({
  children,
  initialState,
  categories = enterpriseNavigationConfig,
  userRole,
  onError
}) => {
  const [state, dispatch] = useReducer(optimizedNavigationReducer, {
    ...defaultOptimizedState,
    ...initialState
  });

  const { trackStart, trackEnd, trackOperation } = usePerformanceMonitor();

  // Refs for performance optimization
  const persistenceTimeoutRef = useRef<NodeJS.Timeout>();
  const isInitializedRef = useRef(false);
  const metricsRef = useRef<Record<string, number>>({});
  const previousStateRef = useRef<OptimizedNavigationState>(state);
  const updateBatchRef = useRef<Partial<NavigationState>>({});
  const batchTimeoutRef = useRef<NodeJS.Timeout>();

  /**
   * Batched dispatch for performance
   */
  const batchedDispatch = useCallback((update: Partial<NavigationState>) => {
    Object.assign(updateBatchRef.current, update);

    if (batchTimeoutRef.current) {
      clearTimeout(batchTimeoutRef.current);
    }

    batchTimeoutRef.current = setTimeout(() => {
      if (Object.keys(updateBatchRef.current).length > 0) {
        unstable_batchedUpdates(() => {
          dispatch({ type: 'BATCH_UPDATE', payload: updateBatchRef.current });
        });
        updateBatchRef.current = {};
      }
    }, 16); // Next frame
  }, []);

  /**
   * Load persisted state with performance tracking
   */
  useEffect(() => {
    if (isInitializedRef.current) return;

    const loadTime = trackStart('loadPersistedState');

    try {
      const persistedState = localStorage.getItem(STORAGE_CONFIG.STATE_KEY);
      const persistedPreferences = localStorage.getItem(STORAGE_CONFIG.PREFERENCES_KEY);

      const updates: Partial<NavigationState> = {};

      if (persistedState) {
        const parsedState = JSON.parse(persistedState);
        Object.assign(updates, parsedState);
      }

      if (persistedPreferences) {
        const parsedPreferences = JSON.parse(persistedPreferences);
        updates.preferences = { ...state.preferences, ...parsedPreferences };
      }

      if (Object.keys(updates).length > 0) {
        startTransition(() => {
          dispatch({ type: 'LOAD_PERSISTED_STATE', payload: updates });
        });
      }
    } catch (error) {
      console.warn('Failed to load persisted navigation state:', error);
      if (onError) {
        onError({
          id: 'persistence_load_error',
          message: 'Failed to load persisted navigation state',
          timestamp: new Date(),
          navigationContext: { action: 'load_state' }
        });
      }
    } finally {
      trackEnd('loadPersistedState', loadTime);
      isInitializedRef.current = true;
    }
  }, [onError, trackStart, trackEnd, state.preferences]);

  /**
   * Persist state with debouncing and performance tracking
   */
  useEffect(() => {
    if (!isInitializedRef.current || !state.preferences.persistState) return;

    // Check if state actually changed
    if (isEqual(previousStateRef.current, state)) return;
    previousStateRef.current = state;

    if (persistenceTimeoutRef.current) {
      clearTimeout(persistenceTimeoutRef.current);
    }

    persistenceTimeoutRef.current = setTimeout(() => {
      const persistTime = trackStart('persistState');

      try {
        const stateToSave = {
          activeItemId: state.activeItemId,
          activeCategoryId: state.activeCategoryId,
          collapsedState: state.collapsedState
        };

        localStorage.setItem(STORAGE_CONFIG.STATE_KEY, JSON.stringify(stateToSave));
        localStorage.setItem(STORAGE_CONFIG.PREFERENCES_KEY, JSON.stringify(state.preferences));
      } catch (error) {
        console.warn('Failed to persist navigation state:', error);
        if (onError) {
          onError({
            id: 'persistence_save_error',
            message: 'Failed to persist navigation state',
            timestamp: new Date(),
            navigationContext: { action: 'save_state' }
          });
        }
      } finally {
        trackEnd('persistState', persistTime);
      }
    }, STORAGE_CONFIG.DEBOUNCE_MS);

    return () => {
      if (persistenceTimeoutRef.current) {
        clearTimeout(persistenceTimeoutRef.current);
      }
    };
  }, [state, onError, trackStart, trackEnd]);

  /**
   * Memoized filtered categories with caching
   */
  const filteredCategories = useMemo(() => {
    const cacheKey = userRole;
    const cached = state._cache.filteredCategories.get(cacheKey);

    if (cached && Date.now() - state._cache.lastUpdate < STORAGE_CONFIG.CACHE_EXPIRY_MS) {
      return cached;
    }

    const computeTime = trackStart('filterCategories');
    const filtered = navigationConfigUtils.getCategoriesByRole(userRole);

    // Update cache
    state._cache.filteredCategories.set(cacheKey, filtered);

    trackEnd('filterCategories', computeTime);
    return filtered;
  }, [userRole, state._cache, trackStart, trackEnd]);

  /**
   * Memoized item lookup with caching
   */
  const itemLookup = useMemo(() => {
    if (state._cache.itemLookup.size > 0 &&
        Date.now() - state._cache.lastUpdate < STORAGE_CONFIG.CACHE_EXPIRY_MS) {
      return state._cache.itemLookup;
    }

    const computeTime = trackStart('buildItemLookup');
    const lookup = new Map<string, { item: NavigationItem; category: NavigationCategory }>();

    filteredCategories.forEach(category => {
      const accessibleItems = navigationConfigUtils.getItemsByRole(category, userRole);
      accessibleItems.forEach(item => {
        lookup.set(item.id, { item, category });
      });
    });

    // Update cache
    state._cache.itemLookup.clear();
    lookup.forEach((value, key) => {
      state._cache.itemLookup.set(key, value);
    });

    trackEnd('buildItemLookup', computeTime);
    return lookup;
  }, [filteredCategories, userRole, state._cache, trackStart, trackEnd]);

  /**
   * Optimized navigation actions with performance tracking
   */
  const actions: NavigationActions = useMemo(() => ({
    setActiveItem: useCallback((itemId: string) => {
      trackOperation('setActiveItem', () => {
        dispatch({ type: 'SET_ACTIVE_ITEM', payload: itemId });

        // Track analytics event
        dispatch({
          type: 'TRACK_EVENT',
          payload: {
            type: 'navigate',
            target: { type: 'item', id: itemId, title: itemId },
            timestamp: new Date(),
            userRole,
            metadata: { source: 'setActiveItem' }
          }
        });
      });
    }, [userRole, trackOperation]),

    toggleCategory: useCallback((categoryId: string) => {
      trackOperation('toggleCategory', () => {
        dispatch({ type: 'TOGGLE_CATEGORY', payload: categoryId });

        dispatch({
          type: 'TRACK_EVENT',
          payload: {
            type: 'expand',
            target: { type: 'category', id: categoryId, title: categoryId },
            timestamp: new Date(),
            userRole,
            metadata: { source: 'toggleCategory' }
          }
        });
      });
    }, [userRole, trackOperation]),

    setCategoryCollapsed: useCallback((categoryId: string, collapsed: boolean) => {
      dispatch({
        type: 'SET_CATEGORY_COLLAPSED',
        payload: { categoryId, collapsed }
      });
    }, []),

    updatePreferences: useCallback((preferences: Partial<NavigationPreferences>) => {
      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences });
    }, []),

    resetState: useCallback(() => {
      dispatch({ type: 'RESET_STATE' });

      try {
        localStorage.removeItem(STORAGE_CONFIG.STATE_KEY);
        localStorage.removeItem(STORAGE_CONFIG.PREFERENCES_KEY);
      } catch (error) {
        console.warn('Failed to clear navigation state from localStorage:', error);
      }
    }, []),

    trackEvent: useCallback((event: NavigationEvent) => {
      dispatch({ type: 'TRACK_EVENT', payload: event });
    }, []),

    handleError: useCallback((error: NavigationError) => {
      dispatch({ type: 'HANDLE_ERROR', payload: error });
      if (onError) {
        onError(error);
      }
    }, [onError])
  }), [userRole, trackOperation, onError]);

  /**
   * Optimized navigation utilities with caching
   */
  const utils: NavigationUtils = useMemo(() => ({
    hasAccess: useCallback((item: NavigationItem | NavigationCategory, userRole: UserRole) => {
      if (!item.requiredRole) return true;

      const roleHierarchy = {
        viewer: 0,
        operator: 1,
        manager: 2,
        admin: 3,
        superuser: 4
      };

      return roleHierarchy[userRole] >= roleHierarchy[item.requiredRole];
    }, []),

    getCategoryByItemId: useCallback((itemId: string) => {
      const result = itemLookup.get(itemId);
      return result?.category || null;
    }, [itemLookup]),

    getItemById: useCallback((itemId: string) => {
      const result = itemLookup.get(itemId);
      return result?.item || null;
    }, [itemLookup]),

    filterByRole: useCallback((items: NavigationItem[], userRole: UserRole) => {
      return items.filter(item => utils.hasAccess(item, userRole));
    }, []),

    getBreadcrumb: useCallback((itemId: string) => {
      const cached = state._cache.breadcrumbs.get(itemId);

      if (cached && Date.now() - state._cache.lastUpdate < STORAGE_CONFIG.CACHE_EXPIRY_MS) {
        return cached;
      }

      const result = itemLookup.get(itemId);
      if (!result) return [];

      const breadcrumb = [result.category.title, result.item.title];
      state._cache.breadcrumbs.set(itemId, breadcrumb);

      return breadcrumb;
    }, [itemLookup, state._cache]),

    isActiveByPath: useCallback((path: string, currentPath: string) => {
      return path === currentPath || currentPath.startsWith(path + '/');
    }, [])
  }), [itemLookup, state._cache]);

  /**
   * Memoized context value with deep equality check
   */
  const contextValue = useMemo(() => ({
    state,
    actions,
    utils
  }), [state, actions, utils]);

  /**
   * Cleanup effect
   */
  useEffect(() => {
    return () => {
      if (persistenceTimeoutRef.current) {
        clearTimeout(persistenceTimeoutRef.current);
      }
      if (batchTimeoutRef.current) {
        clearTimeout(batchTimeoutRef.current);
      }
    };
  }, []);

  return (
    <OptimizedNavigationContext.Provider value={contextValue}>
      {children}
    </OptimizedNavigationContext.Provider>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for React.memo
  return (
    isEqual(prevProps.initialState, nextProps.initialState) &&
    isEqual(prevProps.categories, nextProps.categories) &&
    prevProps.userRole === nextProps.userRole &&
    prevProps.onError === nextProps.onError
  );
});

OptimizedNavigationProvider.displayName = 'OptimizedNavigationProvider';

/**
 * Hook to use optimized navigation context
 */
export const useOptimizedNavigation = (): NavigationContextValue => {
  const context = useContext(OptimizedNavigationContext);

  if (context === undefined) {
    throw new Error('useOptimizedNavigation must be used within an OptimizedNavigationProvider');
  }

  return context;
};

/**
 * Performance metrics hook
 */
export const useNavigationPerformanceMetrics = () => {
  const metricsRef = useRef<Record<string, number[]>>({});

  const recordMetric = useCallback((operation: string, duration: number) => {
    if (!metricsRef.current[operation]) {
      metricsRef.current[operation] = [];
    }

    metricsRef.current[operation].push(duration);

    // Keep only last 50 measurements
    if (metricsRef.current[operation].length > 50) {
      metricsRef.current[operation] = metricsRef.current[operation].slice(-50);
    }
  }, []);

  const getMetrics = useCallback(() => {
    const summary: Record<string, { avg: number; min: number; max: number; count: number }> = {};

    Object.entries(metricsRef.current).forEach(([operation, durations]) => {
      if (durations.length > 0) {
        summary[operation] = {
          avg: durations.reduce((a, b) => a + b, 0) / durations.length,
          min: Math.min(...durations),
          max: Math.max(...durations),
          count: durations.length
        };
      }
    });

    return summary;
  }, []);

  const clearMetrics = useCallback(() => {
    metricsRef.current = {};
  }, []);

  return {
    recordMetric,
    getMetrics,
    clearMetrics
  };
};

export default OptimizedNavigationProvider;