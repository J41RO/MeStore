/**
 * Accessibility Utilities for WCAG 2.1 AA Compliance
 * Comprehensive helper functions for accessible interfaces
 */

// Focus management utilities
export const focusManagement = {
  /**
   * Set focus to element with proper announcement
   */
  setFocus: (element: HTMLElement | null, announceText?: string) => {
    if (!element) return;

    element.focus();

    if (announceText) {
      announceToScreenReader(announceText);
    }
  },

  /**
   * Focus trap for modals and overlays
   */
  createFocusTrap: (container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);

    // Focus first element initially
    firstElement?.focus();

    return () => container.removeEventListener('keydown', handleTabKey);
  },

  /**
   * Skip link implementation
   */
  createSkipLink: (targetId: string, text: string = 'Saltar al contenido principal') => {
    const skipLink = document.createElement('a');
    skipLink.href = `#${targetId}`;
    skipLink.className = 'skip-link sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded z-50';
    skipLink.textContent = text;

    skipLink.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById(targetId);
      if (target) {
        target.focus();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });

    return skipLink;
  }
};

// Screen reader utilities
export const screenReader = {
  /**
   * Announce text to screen readers
   */
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },

  /**
   * Create live region for dynamic content
   */
  createLiveRegion: (id: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = document.createElement('div');
    liveRegion.id = id;
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';

    document.body.appendChild(liveRegion);

    return {
      announce: (message: string) => {
        liveRegion.textContent = message;
      },
      remove: () => {
        if (liveRegion.parentNode) {
          liveRegion.parentNode.removeChild(liveRegion);
        }
      }
    };
  }
};

// Keyboard navigation utilities
export const keyboardNavigation = {
  /**
   * Handle arrow key navigation in lists/grids
   */
  handleArrowNavigation: (
    currentIndex: number,
    totalItems: number,
    direction: 'up' | 'down' | 'left' | 'right',
    itemsPerRow?: number
  ): number => {
    switch (direction) {
      case 'up':
        if (itemsPerRow) {
          return Math.max(0, currentIndex - itemsPerRow);
        }
        return Math.max(0, currentIndex - 1);

      case 'down':
        if (itemsPerRow) {
          return Math.min(totalItems - 1, currentIndex + itemsPerRow);
        }
        return Math.min(totalItems - 1, currentIndex + 1);

      case 'left':
        return Math.max(0, currentIndex - 1);

      case 'right':
        return Math.min(totalItems - 1, currentIndex + 1);

      default:
        return currentIndex;
    }
  },

  /**
   * Enhanced keyboard event handler
   */
  createKeyboardHandler: (handlers: Record<string, () => void>) => {
    return (event: KeyboardEvent) => {
      const key = event.key;
      const handler = handlers[key];

      if (handler) {
        event.preventDefault();
        handler();
      }
    };
  }
};

// Color contrast utilities
export const colorContrast = {
  /**
   * Calculate relative luminance of a color
   */
  getLuminance: (color: string): number => {
    const rgb = parseColor(color);
    if (!rgb) return 0;

    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  },

  /**
   * Calculate contrast ratio between two colors
   */
  getContrastRatio: (color1: string, color2: string): number => {
    const lum1 = colorContrast.getLuminance(color1);
    const lum2 = colorContrast.getLuminance(color2);

    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);

    return (brightest + 0.05) / (darkest + 0.05);
  },

  /**
   * Check if contrast ratio meets WCAG AA standards
   */
  meetsWCAG_AA: (foreground: string, background: string, isLargeText: boolean = false): boolean => {
    const ratio = colorContrast.getContrastRatio(foreground, background);
    return ratio >= (isLargeText ? 3 : 4.5);
  },

  /**
   * Check if contrast ratio meets WCAG AAA standards
   */
  meetsWCAG_AAA: (foreground: string, background: string, isLargeText: boolean = false): boolean => {
    const ratio = colorContrast.getContrastRatio(foreground, background);
    return ratio >= (isLargeText ? 4.5 : 7);
  }
};

// Touch accessibility utilities
export const touchAccessibility = {
  /**
   * Check if element meets minimum touch target size (44px x 44px)
   */
  meetsMinimumTouchTarget: (element: HTMLElement): boolean => {
    const rect = element.getBoundingClientRect();
    return rect.width >= 44 && rect.height >= 44;
  },

  /**
   * Add touch-friendly styling
   */
  makeTouchFriendly: (element: HTMLElement) => {
    const currentStyle = window.getComputedStyle(element);
    const width = parseInt(currentStyle.width);
    const height = parseInt(currentStyle.height);

    if (width < 44) {
      element.style.minWidth = '44px';
    }
    if (height < 44) {
      element.style.minHeight = '44px';
    }

    // Add appropriate padding if needed
    if (!element.style.padding && (width < 44 || height < 44)) {
      element.style.padding = '12px';
    }
  }
};

// ARIA utilities
export const aria = {
  /**
   * Set ARIA attributes programmatically
   */
  setAttributes: (element: HTMLElement, attributes: Record<string, string | boolean | number>) => {
    Object.entries(attributes).forEach(([key, value]) => {
      if (key.startsWith('aria-')) {
        element.setAttribute(key, String(value));
      }
    });
  },

  /**
   * Create accessible description
   */
  createDescription: (text: string, id?: string): HTMLElement => {
    const description = document.createElement('div');
    description.id = id || `desc-${Date.now()}`;
    description.className = 'sr-only';
    description.textContent = text;

    return description;
  },

  /**
   * Enhanced ARIA live region
   */
  createEnhancedLiveRegion: (options: {
    id: string;
    level: 'polite' | 'assertive';
    atomic?: boolean;
    relevant?: string;
  }) => {
    const region = document.createElement('div');
    region.id = options.id;
    region.setAttribute('aria-live', options.level);
    region.setAttribute('aria-atomic', options.atomic ? 'true' : 'false');

    if (options.relevant) {
      region.setAttribute('aria-relevant', options.relevant);
    }

    region.className = 'sr-only';
    document.body.appendChild(region);

    return region;
  }
};

// Reduced motion utilities
export const reducedMotion = {
  /**
   * Check if user prefers reduced motion
   */
  prefersReducedMotion: (): boolean => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Apply motion based on user preference
   */
  respectMotionPreference: (
    element: HTMLElement,
    animationConfig: {
      normal: string;
      reduced: string;
    }
  ) => {
    const motion = reducedMotion.prefersReducedMotion() ? animationConfig.reduced : animationConfig.normal;
    element.style.animation = motion;
  },

  /**
   * Create motion-safe CSS classes
   */
  getMotionSafeClasses: (normalClasses: string, reducedClasses: string = ''): string => {
    return reducedMotion.prefersReducedMotion() ? reducedClasses : normalClasses;
  }
};

// Helper functions
function parseColor(color: string): [number, number, number] | null {
  // Simple RGB parser - in a real implementation, you'd want a more robust parser
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    if (hex.length === 3) {
      return [
        parseInt(hex[0] + hex[0], 16),
        parseInt(hex[1] + hex[1], 16),
        parseInt(hex[2] + hex[2], 16)
      ];
    } else if (hex.length === 6) {
      return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16)
      ];
    }
  }

  // RGB/RGBA parser
  const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
  }

  return null;
}

function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  screenReader.announce(message, priority);
}

// Export convenience functions
export {
  announceToScreenReader,
  parseColor
};

// Default export with all utilities
export default {
  focusManagement,
  screenReader,
  keyboardNavigation,
  colorContrast,
  touchAccessibility,
  aria,
  reducedMotion
};