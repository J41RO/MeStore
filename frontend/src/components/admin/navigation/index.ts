/**
 * Enterprise Navigation System - Main Export File
 *
 * Centralized export for all navigation components, types, and utilities.
 * Provides a clean API for consuming the navigation system throughout the application.
 *
 * @version 1.0.0
 * @author System Architect AI
 */

// Core component exports
export { NavigationProvider, useNavigation, useCategoryNavigation, useItemNavigation, useNavigationMetrics } from './NavigationProvider';
export { CategoryNavigation } from './CategoryNavigation';
export { NavigationCategory } from './NavigationCategory';
export { NavigationItem } from './NavigationItem';
export { AdminSidebar } from './AdminSidebar';

// Configuration exports
export { enterpriseNavigationConfig, navigationMetadata, navigationConfigUtils } from './NavigationConfig';
export {
  ACCESSIBLE_COLORS,
  ACCESSIBLE_TYPOGRAPHY,
  KEYBOARD_NAVIGATION,
  ARIA_LABELS,
  SCREEN_READER_CONFIG,
  FOCUS_MANAGEMENT,
  MOTION_PREFERENCES,
  RESPONSIVE_ACCESSIBILITY,
  DEFAULT_ACCESSIBILITY_CONFIG,
  AccessibilityUtils
} from './AccessibilityConfig';

// Type exports
export type {
  NavigationItem as NavigationItemType,
  NavigationCategory as NavigationCategoryType,
  NavigationState,
  NavigationContextValue,
  NavigationActions,
  NavigationUtils,
  NavigationEvent,
  NavigationError,
  NavigationPreferences,
  NavigationMetrics,
  UserRole,
  CategoryTheme,
  UseNavigationReturn,
  NavigationProviderProps,
  CategoryNavigationProps,
  NavigationCategoryProps,
  NavigationItemProps,
  NavigationPerformanceConfig,
  NavigationAccessibilityConfig
} from './NavigationTypes';

export type { AdminSidebarProps } from './AdminSidebar';

// Re-export everything from types for convenience
export * from './NavigationTypes';

/**
 * Navigation system version information
 */
export const NAVIGATION_SYSTEM_INFO = {
  version: '1.0.0',
  buildDate: new Date().toISOString(),
  features: [
    'Hierarchical navigation with 4 enterprise categories',
    'Role-based access control',
    'Performance optimization with lazy loading',
    'WCAG AA accessibility compliance',
    'Keyboard navigation support',
    'Screen reader optimization',
    'Analytics tracking',
    'State persistence',
    'Mobile responsive design',
    'Error handling and recovery'
  ],
  components: [
    'NavigationProvider',
    'CategoryNavigation',
    'NavigationCategory',
    'NavigationItem'
  ],
  categories: [
    'Users (4 items)',
    'Vendors (5 items)',
    'Analytics (5 items)',
    'Settings (5 items)'
  ],
  totalNavigationItems: 19
} as const;

/**
 * Quick start configuration for easy setup
 */
export const QUICK_START_CONFIG = {
  /**
   * Basic setup for the navigation system
   */
  basic: {
    userRole: 'admin' as const,
    persistState: true,
    animations: true,
    accessibility: {
      keyboardNavigation: true,
      screenReaderSupport: true,
      highContrast: false,
      reducedMotion: false
    }
  },

  /**
   * High-performance setup for large-scale deployments
   */
  performance: {
    userRole: 'admin' as const,
    persistState: true,
    animations: false,
    accessibility: {
      keyboardNavigation: true,
      screenReaderSupport: true,
      highContrast: false,
      reducedMotion: true
    },
    lazyLoading: true,
    virtualScrolling: true,
    caching: true
  },

  /**
   * Maximum accessibility setup
   */
  accessibility: {
    userRole: 'admin' as const,
    persistState: true,
    animations: false,
    accessibility: {
      keyboardNavigation: true,
      screenReaderSupport: true,
      highContrast: true,
      reducedMotion: true
    },
    colorContrast: 'AAA',
    focusManagement: 'enhanced',
    ariaVerbosity: 'detailed'
  }
} as const;

/**
 * Migration guide for existing implementations
 */
export const MIGRATION_GUIDE = {
  fromHierarchicalSidebar: {
    steps: [
      '1. Replace HierarchicalSidebar import with CategoryNavigation',
      '2. Wrap application with NavigationProvider',
      '3. Update navigation structure to use NavigationConfig',
      '4. Replace custom state management with useNavigation hook',
      '5. Update styling to use new theme system'
    ],
    breaking_changes: [
      'sidebarStructure format changed to NavigationCategory[]',
      'State management moved to NavigationProvider',
      'Icon system changed from strings to Lucide components',
      'Accessibility attributes are now automatically generated'
    ],
    compatibility: {
      AdminLayout: 'Compatible with minor modifications',
      SidebarProvider: 'Replace with NavigationProvider',
      MenuCategory: 'Replace with NavigationCategory',
      MenuItem: 'Replace with NavigationItem'
    }
  }
} as const;

/**
 * Performance recommendations
 */
export const PERFORMANCE_RECOMMENDATIONS = {
  /**
   * For applications with many categories (>10)
   */
  manyCategories: [
    'Enable lazy loading in CategoryNavigation',
    'Use virtual scrolling for large lists',
    'Implement category-level code splitting',
    'Consider pagination for items within categories'
  ],

  /**
   * For mobile-first applications
   */
  mobile: [
    'Enable touch-optimized target sizes',
    'Use swipe gestures for category navigation',
    'Implement collapsible navigation for small screens',
    'Optimize for thumb navigation zones'
  ],

  /**
   * For accessibility-first applications
   */
  accessibility: [
    'Enable comprehensive keyboard navigation',
    'Implement skip links for main content',
    'Use semantic HTML structure',
    'Provide multiple navigation methods'
  ],

  /**
   * For high-traffic applications
   */
  scale: [
    'Enable performance monitoring',
    'Implement analytics tracking',
    'Use CDN for icon assets',
    'Enable aggressive caching strategies'
  ]
} as const;

/**
 * Troubleshooting guide
 */
export const TROUBLESHOOTING = {
  common_issues: {
    'Navigation not rendering': [
      'Check if NavigationProvider wraps the component',
      'Verify user role has access to categories',
      'Check console for TypeScript errors'
    ],
    'Icons not displaying': [
      'Ensure Lucide React is installed',
      'Check icon imports in NavigationConfig',
      'Verify icon names match Lucide exports'
    ],
    'State not persisting': [
      'Check localStorage availability',
      'Verify persistState preference is true',
      'Check browser privacy settings'
    ],
    'Poor performance': [
      'Enable lazy loading for large lists',
      'Check for unnecessary re-renders',
      'Use React DevTools Profiler'
    ],
    'Accessibility issues': [
      'Run axe-core audit',
      'Test with keyboard navigation',
      'Verify ARIA attributes are present'
    ]
  },

  debugging: {
    development_mode: 'Set NODE_ENV=development for debug info',
    performance_metrics: 'Use useNavigationMetrics hook',
    state_inspection: 'Use React DevTools for state debugging',
    accessibility_testing: 'Use browser accessibility tools'
  }
} as const;

/**
 * Default export provides the complete navigation system
 */
export default {
  // Core components
  NavigationProvider,
  CategoryNavigation,
  NavigationCategory,
  NavigationItem,

  // Configuration
  config: enterpriseNavigationConfig,
  accessibility: DEFAULT_ACCESSIBILITY_CONFIG,

  // Utilities
  utils: navigationConfigUtils,

  // System information
  info: NAVIGATION_SYSTEM_INFO,

  // Quick start configurations
  quickStart: QUICK_START_CONFIG,

  // Migration and troubleshooting
  migration: MIGRATION_GUIDE,
  troubleshooting: TROUBLESHOOTING,
  performance: PERFORMANCE_RECOMMENDATIONS
};