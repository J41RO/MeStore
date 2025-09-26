/**
 * Enterprise Navigation Architecture Types
 *
 * Comprehensive TypeScript interfaces for hierarchical admin navigation
 * with performance optimization, accessibility, and scalability considerations.
 *
 * @version 1.0.0
 * @author System Architect AI
 */

import { type LucideIcon } from 'lucide-react';

/**
 * Core navigation item interface with enterprise features
 */
export interface NavigationItem {
  /** Unique identifier for the navigation item */
  id: string;

  /** Display title for the navigation item */
  title: string;

  /** Navigation path/route */
  path: string;

  /** Lucide icon component for visual representation */
  icon: LucideIcon;

  /** Optional description for accessibility and tooltips */
  description?: string;

  /** Minimum role required to access this item */
  requiredRole?: UserRole;

  /** Badge or notification count */
  badge?: number | string;

  /** Whether this item is currently disabled */
  disabled?: boolean;

  /** External link indicator */
  isExternal?: boolean;

  /** SEO and analytics data */
  metadata?: {
    keywords?: string[];
    analyticsId?: string;
    priority?: number;
  };
}

/**
 * Navigation category with enterprise hierarchy support
 */
export interface NavigationCategory {
  /** Unique identifier for the category */
  id: string;

  /** Display title for the category */
  title: string;

  /** Lucide icon component for category representation */
  icon: LucideIcon;

  /** Array of navigation items in this category */
  items: NavigationItem[];

  /** Whether the category is currently collapsed */
  isCollapsed: boolean;

  /** Minimum role required to view this category */
  requiredRole?: UserRole;

  /** Category order/priority for sorting */
  order?: number;

  /** Category description for accessibility */
  description?: string;

  /** Color theme for the category */
  theme?: CategoryTheme;

  /** Whether category should be lazy loaded */
  lazy?: boolean;
}

/**
 * Navigation state management interface
 */
export interface NavigationState {
  /** Current active item ID */
  activeItemId: string | null;

  /** Current active category ID */
  activeCategoryId: string | null;

  /** Collapsed state for each category */
  collapsedState: Record<string, boolean>;

  /** User preferences for navigation */
  preferences: NavigationPreferences;

  /** Performance metrics */
  metrics?: NavigationMetrics;
}

/**
 * User role enumeration for access control
 */
export enum UserRole {
  SUPERUSER = 'superuser',
  ADMIN = 'admin',
  MANAGER = 'manager',
  OPERATOR = 'operator',
  VIEWER = 'viewer'
}

/**
 * Category visual themes
 */
export interface CategoryTheme {
  /** Primary color for the category */
  primary: string;

  /** Secondary color for hover states */
  secondary: string;

  /** Text color */
  text: string;

  /** Background color */
  background: string;
}

/**
 * User navigation preferences
 */
export interface NavigationPreferences {
  /** Whether to persist collapsed state */
  persistState: boolean;

  /** Animation preferences */
  animations: boolean;

  /** Compact mode preference */
  compactMode: boolean;

  /** Preferred category order */
  categoryOrder?: string[];

  /** Accessibility preferences */
  accessibility: {
    reduceMotion: boolean;
    highContrast: boolean;
    screenReader: boolean;
  };
}

/**
 * Performance monitoring for navigation
 */
export interface NavigationMetrics {
  /** Render time for each category */
  renderTimes: Record<string, number>;

  /** Click analytics */
  clickCounts: Record<string, number>;

  /** Load times for lazy components */
  loadTimes: Record<string, number>;

  /** Error tracking */
  errors: NavigationError[];
}

/**
 * Navigation error tracking
 */
export interface NavigationError {
  /** Error identifier */
  id: string;

  /** Error message */
  message: string;

  /** Stack trace */
  stack?: string;

  /** Timestamp */
  timestamp: Date;

  /** User context */
  userRole?: UserRole;

  /** Navigation context */
  navigationContext: {
    categoryId?: string;
    itemId?: string;
    action?: string;
  };
}

/**
 * Navigation provider context value
 */
export interface NavigationContextValue {
  /** Navigation state */
  state: NavigationState;

  /** Actions for state management */
  actions: NavigationActions;

  /** Utility functions */
  utils: NavigationUtils;
}

/**
 * Navigation actions interface
 */
export interface NavigationActions {
  /** Set active navigation item */
  setActiveItem: (itemId: string) => void;

  /** Toggle category collapsed state */
  toggleCategory: (categoryId: string) => void;

  /** Set category collapsed state */
  setCategoryCollapsed: (categoryId: string, collapsed: boolean) => void;

  /** Update user preferences */
  updatePreferences: (preferences: Partial<NavigationPreferences>) => void;

  /** Reset navigation state */
  resetState: () => void;

  /** Track navigation event */
  trackEvent: (event: NavigationEvent) => void;

  /** Handle navigation error */
  handleError: (error: NavigationError) => void;
}

/**
 * Navigation utility functions
 */
export interface NavigationUtils {
  /** Check if user has access to item */
  hasAccess: (item: NavigationItem | NavigationCategory, userRole: UserRole) => boolean;

  /** Get category by item ID */
  getCategoryByItemId: (itemId: string) => NavigationCategory | null;

  /** Get item by ID */
  getItemById: (itemId: string) => NavigationItem | null;

  /** Filter items by user role */
  filterByRole: (items: NavigationItem[], userRole: UserRole) => NavigationItem[];

  /** Generate breadcrumb */
  getBreadcrumb: (itemId: string) => string[];

  /** Check if path is active */
  isActiveByPath: (path: string, currentPath: string) => boolean;
}

/**
 * Navigation event for analytics
 */
export interface NavigationEvent {
  /** Event type */
  type: 'click' | 'hover' | 'expand' | 'collapse' | 'navigate';

  /** Target element */
  target: {
    type: 'category' | 'item';
    id: string;
    title: string;
  };

  /** Timestamp */
  timestamp: Date;

  /** User context */
  userRole?: UserRole;

  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Hook return type for navigation management
 */
export interface UseNavigationReturn {
  /** Navigation categories */
  categories: NavigationCategory[];

  /** Current navigation state */
  state: NavigationState;

  /** Navigation actions */
  actions: NavigationActions;

  /** Utility functions */
  utils: NavigationUtils;

  /** Loading state */
  isLoading: boolean;

  /** Error state */
  error: NavigationError | null;
}

/**
 * Component props interfaces
 */

export interface NavigationProviderProps {
  children: React.ReactNode;
  initialState?: Partial<NavigationState>;
  categories: NavigationCategory[];
  userRole: UserRole;
  onError?: (error: NavigationError) => void;
}

export interface CategoryNavigationProps {
  categories: NavigationCategory[];
  userRole: UserRole;
  className?: string;
  onItemClick?: (item: NavigationItem) => void;
  onCategoryToggle?: (categoryId: string) => void;
}

export interface NavigationCategoryProps {
  category: NavigationCategory;
  userRole: UserRole;
  isActive?: boolean;
  onToggle?: () => void;
  onItemClick?: (item: NavigationItem) => void;
  className?: string;
}

export interface NavigationItemProps {
  item: NavigationItem;
  userRole: UserRole;
  isActive?: boolean;
  onClick?: (item: NavigationItem) => void;
  className?: string;
  tabIndex?: number;
}

/**
 * Performance configuration
 */
export interface NavigationPerformanceConfig {
  /** Enable lazy loading for categories */
  lazyLoading: boolean;

  /** Virtual scrolling threshold */
  virtualScrollThreshold: number;

  /** Debounce time for state persistence */
  persistenceDebounceMs: number;

  /** Maximum cache size for rendered items */
  maxCacheSize: number;

  /** Enable performance monitoring */
  monitoring: boolean;
}

/**
 * Accessibility configuration
 */
export interface NavigationAccessibilityConfig {
  /** Enable keyboard navigation */
  keyboardNavigation: boolean;

  /** Enable screen reader support */
  screenReaderSupport: boolean;

  /** Enable high contrast mode */
  highContrastMode: boolean;

  /** Enable reduced motion */
  reducedMotion: boolean;

  /** ARIA labels configuration */
  ariaLabels: {
    navigation: string;
    category: string;
    item: string;
    toggle: string;
    expanded: string;
    collapsed: string;
  };
}