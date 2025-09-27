/**
 * Enterprise Navigation Provider
 *
 * Advanced React Context provider for hierarchical navigation state management
 * with performance optimization, accessibility, and enterprise features.
 *
 * Features:
 * - Persistent state with localStorage
 * - Performance optimization with memoization
 * - Role-based access control
 * - Analytics tracking
 * - Error handling and recovery
 * - Accessibility support
 *
 * @version 1.0.0
 * @author System Architect AI
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  useMemo,
  useRef
} from 'react';

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

/**
 * Navigation action types for reducer
 */
type NavigationAction =
  | { type: 'SET_ACTIVE_ITEM'; payload: string }
  | { type: 'SET_ACTIVE_CATEGORY'; payload: string }
  | { type: 'TOGGLE_CATEGORY'; payload: string }
  | { type: 'SET_CATEGORY_COLLAPSED'; payload: { categoryId: string; collapsed: boolean } }
  | { type: 'UPDATE_PREFERENCES'; payload: Partial<NavigationPreferences> }
  | { type: 'RESET_STATE' }
  | { type: 'TRACK_EVENT'; payload: NavigationEvent }
  | { type: 'HANDLE_ERROR'; payload: NavigationError }
  | { type: 'LOAD_PERSISTED_STATE'; payload: Partial<NavigationState> };

/**
 * Default navigation preferences
 */
const defaultPreferences: NavigationPreferences = {
  persistState: true,
  animations: true,
  compactMode: false,
  accessibility: {
    reduceMotion: false,
    highContrast: false,
    screenReader: false
  }
};

/**
 * Default navigation state
 */
const defaultState: NavigationState = {
  activeItemId: null,
  activeCategoryId: null,
  collapsedState: {},
  preferences: defaultPreferences
};

/**
 * Local storage keys
 */
const STORAGE_KEYS = {
  STATE: 'mestore_admin_navigation_state',
  PREFERENCES: 'mestore_admin_navigation_preferences',
  METRICS: 'mestore_admin_navigation_metrics'
} as const;

/**
 * Navigation state reducer with performance optimizations
 */
function navigationReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'SET_ACTIVE_ITEM':
      return {
        ...state,
        activeItemId: action.payload,
        activeCategoryId: getActiveCategoryId(action.payload)
      };

    case 'SET_ACTIVE_CATEGORY':
      return {
        ...state,
        activeCategoryId: action.payload
      };

    case 'TOGGLE_CATEGORY':
      return {
        ...state,
        collapsedState: {
          ...state.collapsedState,
          [action.payload]: !state.collapsedState[action.payload]
        }
      };

    case 'SET_CATEGORY_COLLAPSED':
      return {
        ...state,
        collapsedState: {
          ...state.collapsedState,
          [action.payload.categoryId]: action.payload.collapsed
        }
      };

    case 'UPDATE_PREFERENCES':
      return {
        ...state,
        preferences: {
          ...state.preferences,
          ...action.payload
        }
      };

    case 'RESET_STATE':
      return defaultState;

    case 'LOAD_PERSISTED_STATE':
      return {
        ...state,
        ...action.payload
      };

    case 'TRACK_EVENT':
      // Handle analytics tracking
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', action.payload.type, {
          event_category: 'navigation',
          event_label: action.payload.target.id,
          custom_map: action.payload.metadata
        });
      }
      return state;

    case 'HANDLE_ERROR':
      // Error handling logic
      console.error('Navigation Error:', action.payload);
      // Could integrate with error reporting service
      return state;

    default:
      return state;
  }
}

/**
 * Utility function to get active category ID from item ID
 */
function getActiveCategoryId(itemId: string): string | null {
  const result = navigationConfigUtils.getItemById(itemId);
  return result?.category.id || null;
}

/**
 * Navigation context
 */
const NavigationContext = createContext<NavigationContextValue | undefined>(undefined);

/**
 * Enterprise Navigation Provider Component
 */
export const NavigationProvider: React.FC<NavigationProviderProps> = ({
  children,
  initialState,
  categories = enterpriseNavigationConfig,
  userRole,
  onError
}) => {
  const [state, dispatch] = useReducer(navigationReducer, {
    ...defaultState,
    ...initialState
  });

  // Refs for performance optimization
  const persistenceTimeoutRef = useRef<NodeJS.Timeout>();
  const isInitializedRef = useRef(false);
  const metricsRef = useRef<Record<string, number>>({});

  /**
   * Load persisted state from localStorage
   */
  useEffect(() => {
    if (isInitializedRef.current) return;

    try {
      const persistedState = localStorage.getItem(STORAGE_KEYS.STATE);
      const persistedPreferences = localStorage.getItem(STORAGE_KEYS.PREFERENCES);

      if (persistedState) {
        const parsedState = JSON.parse(persistedState);
        dispatch({ type: 'LOAD_PERSISTED_STATE', payload: parsedState });
      }

      if (persistedPreferences) {
        const parsedPreferences = JSON.parse(persistedPreferences);
        dispatch({ type: 'UPDATE_PREFERENCES', payload: parsedPreferences });
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
    }

    isInitializedRef.current = true;
  }, [onError]);

  /**
   * Persist state to localStorage with debouncing
   */
  useEffect(() => {
    if (!isInitializedRef.current || !state.preferences.persistState) return;

    // Clear previous timeout
    if (persistenceTimeoutRef.current) {
      clearTimeout(persistenceTimeoutRef.current);
    }

    // Debounce persistence to avoid excessive writes
    persistenceTimeoutRef.current = setTimeout(() => {
      try {
        const stateToSave = {
          activeItemId: state.activeItemId,
          activeCategoryId: state.activeCategoryId,
          collapsedState: state.collapsedState
        };

        localStorage.setItem(STORAGE_KEYS.STATE, JSON.stringify(stateToSave));
        localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(state.preferences));
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
      }
    }, 300); // 300ms debounce

    return () => {
      if (persistenceTimeoutRef.current) {
        clearTimeout(persistenceTimeoutRef.current);
      }
    };
  }, [state, onError]);

  /**
   * Navigation actions with proper memoization
   */
  const actions: NavigationActions = useMemo(() => ({
    setActiveItem: (itemId: string) => {
      const startTime = performance.now();
      dispatch({ type: 'SET_ACTIVE_ITEM', payload: itemId });

      // Track performance metrics
      const endTime = performance.now();
      metricsRef.current[`setActiveItem_${itemId}`] = endTime - startTime;

      // Track analytics event
      dispatch({
        type: 'TRACK_EVENT',
        payload: {
          type: 'navigate',
          target: { type: 'item', id: itemId, title: itemId },
          timestamp: new Date(),
          userRole,
          metadata: { performanceMs: endTime - startTime }
        }
      });
    },

    toggleCategory: (categoryId: string) => {
      const startTime = performance.now();
      dispatch({ type: 'TOGGLE_CATEGORY', payload: categoryId });

      const endTime = performance.now();
      metricsRef.current[`toggleCategory_${categoryId}`] = endTime - startTime;

      dispatch({
        type: 'TRACK_EVENT',
        payload: {
          type: 'expand',
          target: { type: 'category', id: categoryId, title: categoryId },
          timestamp: new Date(),
          userRole,
          metadata: { performanceMs: endTime - startTime }
        }
      });
    },

    setCategoryCollapsed: (categoryId: string, collapsed: boolean) => {
      dispatch({
        type: 'SET_CATEGORY_COLLAPSED',
        payload: { categoryId, collapsed }
      });
    },

    updatePreferences: (preferences: Partial<NavigationPreferences>) => {
      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences });
    },

    resetState: () => {
      dispatch({ type: 'RESET_STATE' });

      // Clear localStorage
      try {
        localStorage.removeItem(STORAGE_KEYS.STATE);
        localStorage.removeItem(STORAGE_KEYS.PREFERENCES);
      } catch (error) {
        console.warn('Failed to clear navigation state from localStorage:', error);
      }
    },

    trackEvent: (event: NavigationEvent) => {
      dispatch({ type: 'TRACK_EVENT', payload: event });
    },

    handleError: (error: NavigationError) => {
      dispatch({ type: 'HANDLE_ERROR', payload: error });
      if (onError) {
        onError(error);
      }
    }
  }), [userRole, onError]);

  /**
   * Navigation utilities with proper memoization
   */
  const utils: NavigationUtils = useMemo(() => ({
    hasAccess: (item: NavigationItem | NavigationCategory, userRole: UserRole) => {
      if (!item.requiredRole) return true;

      const roleHierarchy = {
        viewer: 0,
        operator: 1,
        manager: 2,
        admin: 3,
        superuser: 4
      };

      return roleHierarchy[userRole] >= roleHierarchy[item.requiredRole];
    },

    getCategoryByItemId: (itemId: string) => {
      const result = navigationConfigUtils.getItemById(itemId);
      return result?.category || null;
    },

    getItemById: (itemId: string) => {
      const result = navigationConfigUtils.getItemById(itemId);
      return result?.item || null;
    },

    filterByRole: (items: NavigationItem[], userRole: UserRole) => {
      return navigationConfigUtils.getItemsByRole({ items } as NavigationCategory, userRole);
    },

    getBreadcrumb: (itemId: string) => {
      const result = navigationConfigUtils.getItemById(itemId);
      if (!result) return [];

      return [result.category.title, result.item.title];
    },

    isActiveByPath: (path: string, currentPath: string) => {
      return path === currentPath || currentPath.startsWith(path + '/');
    }
  }), []);

  /**
   * Memoized context value to prevent unnecessary re-renders
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
    };
  }, []);

  return (
    <NavigationContext.Provider value={contextValue}>
      {children}
    </NavigationContext.Provider>
  );
};

/**
 * Hook to use navigation context
 */
export const useNavigation = (): NavigationContextValue => {
  const context = useContext(NavigationContext);

  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }

  return context;
};

/**
 * Hook for category-specific navigation management
 */
export const useCategoryNavigation = (categoryId: string) => {
  const { state, actions, utils } = useNavigation();

  const category = useMemo(() =>
    navigationConfigUtils.getCategoryById(categoryId),
    [categoryId]
  );

  const isCollapsed = useMemo(() =>
    Boolean(state.collapsedState[categoryId]),
    [state.collapsedState, categoryId]
  );

  const isActive = useMemo(() =>
    state.activeCategoryId === categoryId,
    [state.activeCategoryId, categoryId]
  );

  const toggle = useCallback(() => {
    actions.toggleCategory(categoryId);
  }, [actions, categoryId]);

  return {
    category,
    isCollapsed,
    isActive,
    toggle
  };
};

/**
 * Hook for item-specific navigation management
 */
export const useItemNavigation = (itemId: string) => {
  const { state, actions, utils } = useNavigation();

  const item = useMemo(() =>
    utils.getItemById(itemId),
    [utils, itemId]
  );

  const isActive = useMemo(() =>
    state.activeItemId === itemId,
    [state.activeItemId, itemId]
  );

  const navigate = useCallback(() => {
    actions.setActiveItem(itemId);
  }, [actions, itemId]);

  return {
    item,
    isActive,
    navigate
  };
};

/**
 * Performance monitoring hook
 */
export const useNavigationMetrics = () => {
  const metrics = metricsRef.current;

  const getMetrics = useCallback(() => ({
    ...metrics
  }), [metrics]);

  const clearMetrics = useCallback(() => {
    metricsRef.current = {};
  }, []);

  return {
    getMetrics,
    clearMetrics
  };
};