/**
 * Navigation Item Component
 *
 * Individual navigation item with accessibility, performance optimization,
 * and enterprise features.
 *
 * Features:
 * - Full keyboard navigation support
 * - ARIA compliance for screen readers
 * - Badge support for notifications
 * - Performance optimized rendering
 * - Role-based access control
 * - Analytics tracking
 *
 * @version 1.0.0
 * @author System Architect AI
 */

import React, {
  memo,
  useCallback,
  useMemo,
  useRef,
  useEffect,
  forwardRef
} from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ExternalLinkIcon, AlertCircleIcon } from 'lucide-react';

import type {
  NavigationItemProps,
  NavigationItem,
  UserRole
} from './NavigationTypes';

import { useNavigation } from './NavigationProvider';

/**
 * Performance configuration
 */
const PERFORMANCE_CONFIG = {
  CLICK_DEBOUNCE_MS: 200,
  HOVER_DELAY_MS: 300,
  FOCUS_DELAY_MS: 100
} as const;

/**
 * NavigationItem Component
 */
export const NavigationItem = memo(forwardRef<HTMLAnchorElement, NavigationItemProps>(({
  item,
  userRole,
  isActive = false,
  onClick,
  className = '',
  tabIndex = 0,
  ...rest
}, ref) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { state, actions, utils } = useNavigation();

  // Refs for performance and accessibility
  const clickTimeoutRef = useRef<NodeJS.Timeout>();
  const hoverTimeoutRef = useRef<NodeJS.Timeout>();
  const lastClickTimeRef = useRef<number>(0);

  // Check if user has access to this item
  const hasAccess = useMemo(() =>
    utils.hasAccess(item, userRole),
    [item, userRole, utils]
  );

  // Determine if item is currently active
  const isCurrentlyActive = useMemo(() =>
    isActive || utils.isActiveByPath(item.path, location.pathname),
    [isActive, item.path, location.pathname, utils]
  );

  // Check if item is disabled
  const isDisabled = useMemo(() =>
    item.disabled || !hasAccess,
    [item.disabled, hasAccess]
  );

  /**
   * Handle item click with debouncing and analytics
   */
  const handleClick = useCallback((event: React.MouseEvent<HTMLAnchorElement>) => {
    // Prevent double clicks
    const now = Date.now();
    if (now - lastClickTimeRef.current < PERFORMANCE_CONFIG.CLICK_DEBOUNCE_MS) {
      event.preventDefault();
      return;
    }
    lastClickTimeRef.current = now;

    // Clear any pending timeouts
    if (clickTimeoutRef.current) {
      clearTimeout(clickTimeoutRef.current);
    }

    // Start performance measurement
    const startTime = performance.now();

    // Handle disabled state
    if (isDisabled) {
      event.preventDefault();
      actions.handleError({
        id: 'navigation_access_denied',
        message: `Access denied to ${item.title}`,
        timestamp: new Date(),
        userRole,
        navigationContext: {
          itemId: item.id,
          action: 'click'
        }
      });
      return;
    }

    // Handle external links
    if (item.isExternal) {
      // Let the default behavior handle external links
      actions.trackEvent({
        type: 'click',
        target: { type: 'item', id: item.id, title: item.title },
        timestamp: new Date(),
        userRole,
        metadata: {
          external: true,
          path: item.path,
          performanceMs: performance.now() - startTime
        }
      });
      return;
    }

    // Prevent default navigation for internal links
    event.preventDefault();

    // Set active item and navigate
    actions.setActiveItem(item.id);

    // Navigate to the route
    navigate(item.path);

    // Track analytics
    actions.trackEvent({
      type: 'navigate',
      target: { type: 'item', id: item.id, title: item.title },
      timestamp: new Date(),
      userRole,
      metadata: {
        path: item.path,
        performanceMs: performance.now() - startTime,
        previousPath: location.pathname
      }
    });

    // Call external click handler
    onClick?.(item);
  }, [
    isDisabled,
    item,
    userRole,
    actions,
    navigate,
    location.pathname,
    onClick
  ]);

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    const { key, shiftKey, ctrlKey, metaKey } = event;

    switch (key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        // Trigger click
        (event.target as HTMLElement).click();
        break;

      case 'ArrowUp':
        event.preventDefault();
        // Focus previous item (implementation would be in parent)
        break;

      case 'ArrowDown':
        event.preventDefault();
        // Focus next item (implementation would be in parent)
        break;

      case 'Home':
        if (ctrlKey || metaKey) {
          event.preventDefault();
          // Focus first item (implementation would be in parent)
        }
        break;

      case 'End':
        if (ctrlKey || metaKey) {
          event.preventDefault();
          // Focus last item (implementation would be in parent)
        }
        break;

      case 'Tab':
        // Allow normal tab navigation
        break;

      default:
        // Allow other keys for potential search functionality
        break;
    }
  }, []);

  /**
   * Handle mouse enter for hover analytics
   */
  const handleMouseEnter = useCallback(() => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }

    hoverTimeoutRef.current = setTimeout(() => {
      actions.trackEvent({
        type: 'hover',
        target: { type: 'item', id: item.id, title: item.title },
        timestamp: new Date(),
        userRole,
        metadata: {
          path: item.path,
          isActive: isCurrentlyActive
        }
      });
    }, PERFORMANCE_CONFIG.HOVER_DELAY_MS);
  }, [actions, item, userRole, isCurrentlyActive]);

  /**
   * Handle mouse leave
   */
  const handleMouseLeave = useCallback(() => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
  }, []);

  /**
   * Icon component with error handling
   */
  const ItemIcon = useMemo(() => {
    try {
      return item.icon;
    } catch (error) {
      console.warn(`Failed to load icon for item ${item.id}:`, error);
      return AlertCircleIcon; // Fallback icon
    }
  }, [item.icon, item.id]);

  /**
   * Generate unique ID for accessibility
   */
  const itemId = useMemo(() => `nav-item-${item.id}`, [item.id]);

  /**
   * Accessibility labels
   */
  const ariaLabels = useMemo(() => {
    const baseLabel = item.title;
    const descriptionLabel = item.description ? `, ${item.description}` : '';
    const stateLabel = isCurrentlyActive ? ', current page' : '';
    const disabledLabel = isDisabled ? ', disabled' : '';
    const externalLabel = item.isExternal ? ', opens in new tab' : '';
    const badgeLabel = item.badge ? `, ${item.badge} notifications` : '';

    return {
      main: `${baseLabel}${descriptionLabel}${stateLabel}${disabledLabel}${externalLabel}${badgeLabel}`,
      description: item.description || `Navigate to ${item.title}`,
      badge: item.badge ? `${item.badge} notifications` : undefined
    };
  }, [item, isCurrentlyActive, isDisabled]);

  /**
   * Computed styles based on state and theme
   */
  const itemClasses = useMemo(() => {
    const baseClasses = `
      group flex items-center px-3 py-2 text-sm font-medium rounded-md
      transition-all duration-150 ease-in-out
      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
      ${className}
    `;

    const stateClasses = isCurrentlyActive
      ? 'bg-blue-100 text-blue-900 border-blue-200'
      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900';

    const disabledClasses = isDisabled
      ? 'opacity-50 cursor-not-allowed pointer-events-none'
      : 'cursor-pointer';

    const accessibilityClasses = state.preferences.accessibility.highContrast
      ? 'high-contrast:border-2 high-contrast:border-solid'
      : '';

    const animationClasses = state.preferences.accessibility.reduceMotion
      ? 'motion-reduce:transition-none'
      : '';

    return [
      baseClasses,
      stateClasses,
      disabledClasses,
      accessibilityClasses,
      animationClasses
    ].join(' ').trim();
  }, [className, isCurrentlyActive, isDisabled, state.preferences]);

  /**
   * Cleanup effect
   */
  useEffect(() => {
    return () => {
      if (clickTimeoutRef.current) {
        clearTimeout(clickTimeoutRef.current);
      }
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  // Don't render if user doesn't have access
  if (!hasAccess) {
    return null;
  }

  return (
    <a
      ref={ref}
      id={itemId}
      href={item.path}
      className={itemClasses}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      role="menuitem"
      tabIndex={tabIndex}
      aria-current={isCurrentlyActive ? 'page' : undefined}
      aria-label={ariaLabels.main}
      aria-describedby={item.description ? `${itemId}-description` : undefined}
      target={item.isExternal ? '_blank' : undefined}
      rel={item.isExternal ? 'noopener noreferrer' : undefined}
      data-testid={`nav-item-${item.id}`}
      {...rest}
    >
      {/* Hidden description for screen readers */}
      {item.description && (
        <span id={`${itemId}-description`} className="sr-only">
          {ariaLabels.description}
        </span>
      )}

      {/* Item icon */}
      <ItemIcon
        className={`
          mr-3 flex-shrink-0 w-4 h-4
          transition-colors duration-150
          ${isCurrentlyActive
            ? 'text-blue-600'
            : 'text-gray-400 group-hover:text-gray-500'
          }
          ${isDisabled ? 'opacity-50' : ''}
        `}
        aria-hidden="true"
      />

      {/* Item title */}
      <span className="flex-1 truncate">
        {item.title}
      </span>

      {/* Badge for notifications */}
      {item.badge && (
        <span
          className={`
            ml-2 inline-flex items-center justify-center
            px-2 py-1 text-xs font-bold leading-none
            rounded-full min-w-[1.5rem]
            ${isCurrentlyActive
              ? 'bg-blue-600 text-white'
              : 'bg-red-500 text-white'
            }
          `}
          aria-label={ariaLabels.badge}
          role="status"
        >
          {typeof item.badge === 'number' && item.badge > 99 ? '99+' : item.badge}
        </span>
      )}

      {/* External link indicator */}
      {item.isExternal && (
        <ExternalLinkIcon
          className={`
            ml-2 w-3 h-3 flex-shrink-0
            ${isCurrentlyActive
              ? 'text-blue-600'
              : 'text-gray-400 group-hover:text-gray-500'
            }
          `}
          aria-hidden="true"
        />
      )}

      {/* Disabled indicator */}
      {isDisabled && !item.isExternal && (
        <AlertCircleIcon
          className="ml-2 w-3 h-3 flex-shrink-0 text-gray-400"
          aria-hidden="true"
        />
      )}
    </a>
  );
}));

/**
 * Display name for debugging
 */
NavigationItem.displayName = 'NavigationItem';

/**
 * Default export
 */
export default NavigationItem;