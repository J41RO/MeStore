/**
 * Accessibility Provider Component
 *
 * Comprehensive accessibility provider that handles WCAG 2.1 AA compliance
 * for the enterprise navigation system including screen reader announcements,
 * focus management, and dynamic state updates.
 *
 * Features:
 * - Live region announcements for state changes
 * - Screen reader optimized content descriptions
 * - High contrast mode support
 * - Reduced motion preferences
 * - Keyboard navigation enhancements
 * - Touch accessibility for mobile
 *
 * @version 1.0.0
 * @author Accessibility AI
 */

import React, {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  useMemo
} from 'react';

/**
 * Accessibility context types
 */
interface AccessibilityState {
  announcements: string[];
  isHighContrast: boolean;
  isReducedMotion: boolean;
  isScreenReaderActive: boolean;
  isMobile: boolean;
  fontSize: 'normal' | 'large' | 'extra-large';
  announceDelay: number;
}

interface AccessibilityActions {
  announce: (message: string, priority?: 'polite' | 'assertive', delay?: number) => void;
  announceNavigation: (item: string, category?: string) => void;
  announceStateChange: (change: string, context?: string) => void;
  announceError: (error: string) => void;
  toggleHighContrast: () => void;
  setReducedMotion: (enabled: boolean) => void;
  setFontSize: (size: AccessibilityState['fontSize']) => void;
  clearAnnouncements: () => void;
}

interface AccessibilityContextValue {
  state: AccessibilityState;
  actions: AccessibilityActions;
}

interface AccessibilityProviderProps {
  children: React.ReactNode;
  initialPreferences?: Partial<AccessibilityState>;
}

/**
 * Default accessibility state
 */
const defaultState: AccessibilityState = {
  announcements: [],
  isHighContrast: false,
  isReducedMotion: false,
  isScreenReaderActive: false,
  isMobile: false,
  fontSize: 'normal',
  announceDelay: 100
};

/**
 * Accessibility context
 */
const AccessibilityContext = createContext<AccessibilityContextValue | undefined>(undefined);

/**
 * Accessibility Provider Component
 */
export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({
  children,
  initialPreferences = {}
}) => {
  const [state, setState] = useState<AccessibilityState>({
    ...defaultState,
    ...initialPreferences
  });

  // Refs for live regions and announcements
  const politeRegionRef = useRef<HTMLDivElement>(null);
  const assertiveRegionRef = useRef<HTMLDivElement>(null);
  const announcementTimeoutRef = useRef<NodeJS.Timeout>();
  const clearTimeoutRef = useRef<NodeJS.Timeout>();

  /**
   * Detect user preferences on mount
   */
  useEffect(() => {
    // Detect high contrast mode
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const mobileQuery = window.matchMedia('(max-width: 768px)');

    // Detect screen reader usage
    const detectScreenReader = () => {
      // Check for common screen reader indicators
      const hasScreenReader = !!(
        navigator.userAgent.includes('NVDA') ||
        navigator.userAgent.includes('JAWS') ||
        navigator.userAgent.includes('VoiceOver') ||
        window.speechSynthesis ||
        document.querySelector('[aria-live]')
      );

      return hasScreenReader;
    };

    setState(prev => ({
      ...prev,
      isHighContrast: highContrastQuery.matches,
      isReducedMotion: reducedMotionQuery.matches,
      isMobile: mobileQuery.matches,
      isScreenReaderActive: detectScreenReader()
    }));

    // Listen for changes
    const handleHighContrastChange = (e: MediaQueryListEvent) => {
      setState(prev => ({ ...prev, isHighContrast: e.matches }));
    };

    const handleReducedMotionChange = (e: MediaQueryListEvent) => {
      setState(prev => ({ ...prev, isReducedMotion: e.matches }));
    };

    const handleMobileChange = (e: MediaQueryListEvent) => {
      setState(prev => ({ ...prev, isMobile: e.matches }));
    };

    highContrastQuery.addEventListener('change', handleHighContrastChange);
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange);
    mobileQuery.addEventListener('change', handleMobileChange);

    return () => {
      highContrastQuery.removeEventListener('change', handleHighContrastChange);
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange);
      mobileQuery.removeEventListener('change', handleMobileChange);
    };
  }, []);

  /**
   * Core announcement function
   */
  const announce = useCallback((
    message: string,
    priority: 'polite' | 'assertive' = 'polite',
    delay: number = state.announceDelay
  ) => {
    if (!message.trim()) return;

    // Clear existing timeout
    if (announcementTimeoutRef.current) {
      clearTimeout(announcementTimeoutRef.current);
    }

    // Delay announcement to avoid rapid-fire announcements
    announcementTimeoutRef.current = setTimeout(() => {
      const targetRegion = priority === 'assertive'
        ? assertiveRegionRef.current
        : politeRegionRef.current;

      if (targetRegion) {
        // Clear previous content
        targetRegion.textContent = '';

        // Force a reflow to ensure screen readers detect the change
        targetRegion.offsetHeight;

        // Set new content
        targetRegion.textContent = message;

        // Update state for debugging
        setState(prev => ({
          ...prev,
          announcements: [...prev.announcements.slice(-9), message] // Keep last 10
        }));

        // Auto-clear after reading time estimate
        if (clearTimeoutRef.current) {
          clearTimeout(clearTimeoutRef.current);
        }

        clearTimeoutRef.current = setTimeout(() => {
          if (targetRegion) {
            targetRegion.textContent = '';
          }
        }, Math.max(3000, message.length * 50)); // ~50ms per character
      }
    }, delay);
  }, [state.announceDelay]);

  /**
   * Announce navigation changes
   */
  const announceNavigation = useCallback((item: string, category?: string) => {
    const message = category
      ? `Navigated to ${item} in ${category} category`
      : `Navigated to ${item}`;

    announce(message, 'polite');
  }, [announce]);

  /**
   * Announce state changes
   */
  const announceStateChange = useCallback((change: string, context?: string) => {
    const message = context
      ? `${change} in ${context}`
      : change;

    announce(message, 'polite');
  }, [announce]);

  /**
   * Announce errors with assertive priority
   */
  const announceError = useCallback((error: string) => {
    announce(`Error: ${error}`, 'assertive');
  }, [announce]);

  /**
   * Toggle high contrast mode
   */
  const toggleHighContrast = useCallback(() => {
    setState(prev => {
      const newHighContrast = !prev.isHighContrast;

      // Apply to document element
      if (newHighContrast) {
        document.documentElement.classList.add('high-contrast');
      } else {
        document.documentElement.classList.remove('high-contrast');
      }

      announce(
        newHighContrast ? 'High contrast mode enabled' : 'High contrast mode disabled',
        'polite'
      );

      return { ...prev, isHighContrast: newHighContrast };
    });
  }, [announce]);

  /**
   * Set reduced motion preference
   */
  const setReducedMotion = useCallback((enabled: boolean) => {
    setState(prev => {
      // Apply to document element
      if (enabled) {
        document.documentElement.classList.add('reduce-motion');
      } else {
        document.documentElement.classList.remove('reduce-motion');
      }

      announce(
        enabled ? 'Reduced motion enabled' : 'Reduced motion disabled',
        'polite'
      );

      return { ...prev, isReducedMotion: enabled };
    });
  }, [announce]);

  /**
   * Set font size preference
   */
  const setFontSize = useCallback((size: AccessibilityState['fontSize']) => {
    setState(prev => {
      // Remove previous font size classes
      document.documentElement.classList.remove('font-large', 'font-extra-large');

      // Apply new font size class
      if (size === 'large') {
        document.documentElement.classList.add('font-large');
      } else if (size === 'extra-large') {
        document.documentElement.classList.add('font-extra-large');
      }

      announce(`Font size changed to ${size}`, 'polite');

      return { ...prev, fontSize: size };
    });
  }, [announce]);

  /**
   * Clear all announcements
   */
  const clearAnnouncements = useCallback(() => {
    setState(prev => ({ ...prev, announcements: [] }));

    if (politeRegionRef.current) {
      politeRegionRef.current.textContent = '';
    }
    if (assertiveRegionRef.current) {
      assertiveRegionRef.current.textContent = '';
    }
  }, []);

  /**
   * Actions object
   */
  const actions: AccessibilityActions = useMemo(() => ({
    announce,
    announceNavigation,
    announceStateChange,
    announceError,
    toggleHighContrast,
    setReducedMotion,
    setFontSize,
    clearAnnouncements
  }), [
    announce,
    announceNavigation,
    announceStateChange,
    announceError,
    toggleHighContrast,
    setReducedMotion,
    setFontSize,
    clearAnnouncements
  ]);

  /**
   * Context value
   */
  const contextValue = useMemo(() => ({
    state,
    actions
  }), [state, actions]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (announcementTimeoutRef.current) {
        clearTimeout(announcementTimeoutRef.current);
      }
      if (clearTimeoutRef.current) {
        clearTimeout(clearTimeoutRef.current);
      }
    };
  }, []);

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {/* Live regions for screen reader announcements */}
      <div
        ref={politeRegionRef}
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        role="status"
        aria-label="Status announcements"
      />

      <div
        ref={assertiveRegionRef}
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
        role="alert"
        aria-label="Important announcements"
      />

      {/* Skip link for keyboard navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50
                   focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded
                   focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        onFocus={() => announce('Skip to main content link focused', 'polite')}
      >
        Skip to main content
      </a>

      {/* Accessibility status indicator for development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white p-2 rounded text-xs max-w-xs">
          <div className="font-bold">Accessibility Status</div>
          <div>High Contrast: {state.isHighContrast ? 'ON' : 'OFF'}</div>
          <div>Reduced Motion: {state.isReducedMotion ? 'ON' : 'OFF'}</div>
          <div>Screen Reader: {state.isScreenReaderActive ? 'ON' : 'OFF'}</div>
          <div>Mobile: {state.isMobile ? 'YES' : 'NO'}</div>
          <div>Font Size: {state.fontSize}</div>
          <div>Announcements: {state.announcements.length}</div>
        </div>
      )}

      {children}
    </AccessibilityContext.Provider>
  );
};

/**
 * Hook to use accessibility context
 */
export const useAccessibility = (): AccessibilityContextValue => {
  const context = useContext(AccessibilityContext);

  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }

  return context;
};

/**
 * Hook for screen reader announcements
 */
export const useScreenReaderAnnouncements = () => {
  const { actions } = useAccessibility();

  return {
    announce: actions.announce,
    announceNavigation: actions.announceNavigation,
    announceStateChange: actions.announceStateChange,
    announceError: actions.announceError
  };
};

/**
 * Hook for accessibility preferences
 */
export const useAccessibilityPreferences = () => {
  const { state, actions } = useAccessibility();

  return {
    preferences: {
      isHighContrast: state.isHighContrast,
      isReducedMotion: state.isReducedMotion,
      fontSize: state.fontSize,
      isMobile: state.isMobile
    },
    toggleHighContrast: actions.toggleHighContrast,
    setReducedMotion: actions.setReducedMotion,
    setFontSize: actions.setFontSize
  };
};

export default AccessibilityProvider;