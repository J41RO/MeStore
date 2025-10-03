/**
 * Animation Utilities
 *
 * Provides reusable animation configurations and utilities for consistent
 * motion design across the application.
 */

/**
 * Animation Timing Functions
 * Based on Material Design and modern web standards
 */
export const easings = {
  // Standard easing - most common for general animations
  standard: 'cubic-bezier(0.4, 0.0, 0.2, 1)',

  // Emphasized easing - for important state changes
  emphasized: 'cubic-bezier(0.0, 0.0, 0.2, 1)',

  // Deceleration - element entering the screen
  decelerate: 'cubic-bezier(0.0, 0.0, 0.2, 1)',

  // Acceleration - element leaving the screen
  accelerate: 'cubic-bezier(0.4, 0.0, 1, 1)',

  // Sharp - quick and decisive, use sparingly
  sharp: 'cubic-bezier(0.4, 0.0, 0.6, 1)',

  // Bounce - playful effect
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',

  // Smooth - very smooth, organic feeling
  smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
} as const;

/**
 * Animation Durations
 * Standardized durations for different types of animations
 */
export const durations = {
  // Instant - for immediate feedback (< 100ms)
  instant: 50,

  // Fast - for small elements like icons, buttons (100-200ms)
  fast: 150,

  // Normal - standard animation speed (200-300ms)
  normal: 250,

  // Moderate - for medium-sized elements (300-400ms)
  moderate: 350,

  // Slow - for large elements or complex animations (400-500ms)
  slow: 450,

  // Very slow - for page transitions (500ms+)
  verySlow: 600,
} as const;

/**
 * Transition Presets
 * Common transition configurations ready to use
 */
export const transitions = {
  // All properties with standard easing
  all: `all ${durations.normal}ms ${easings.standard}`,

  // Color transitions (background, border, text)
  color: `color ${durations.fast}ms ${easings.standard}, background-color ${durations.fast}ms ${easings.standard}, border-color ${durations.fast}ms ${easings.standard}`,

  // Transform animations (scale, rotate, translate)
  transform: `transform ${durations.normal}ms ${easings.emphasized}`,

  // Opacity fades
  fade: `opacity ${durations.normal}ms ${easings.standard}`,

  // Size changes (width, height)
  size: `width ${durations.moderate}ms ${easings.standard}, height ${durations.moderate}ms ${easings.standard}`,

  // Shadow changes
  shadow: `box-shadow ${durations.fast}ms ${easings.standard}`,

  // Combined hover effect (transform + shadow)
  hover: `transform ${durations.fast}ms ${easings.emphasized}, box-shadow ${durations.fast}ms ${easings.standard}`,

  // Button press effect
  button: `transform ${durations.instant}ms ${easings.sharp}, background-color ${durations.fast}ms ${easings.standard}`,

  // Modal/drawer animations
  modal: `opacity ${durations.moderate}ms ${easings.emphasized}, transform ${durations.moderate}ms ${easings.emphasized}`,

  // Page transitions
  page: `opacity ${durations.slow}ms ${easings.standard}, transform ${durations.slow}ms ${easings.emphasized}`,
} as const;

/**
 * Keyframe Animation Classes
 * CSS classes for complex animations
 */
export const animations = {
  // Fade animations
  fadeIn: 'animate-fade-in',
  fadeOut: 'animate-fade-out',
  fadeInUp: 'animate-fade-in-up',
  fadeInDown: 'animate-fade-in-down',

  // Slide animations
  slideInLeft: 'animate-slide-in-left',
  slideInRight: 'animate-slide-in-right',
  slideInUp: 'animate-slide-in-up',
  slideInDown: 'animate-slide-in-down',

  // Scale animations
  scaleIn: 'animate-scale-in',
  scaleOut: 'animate-scale-out',

  // Bounce animations
  bounce: 'animate-bounce',
  bounceIn: 'animate-bounce-in',

  // Shake animations
  shake: 'animate-shake',

  // Pulse/heartbeat
  pulse: 'animate-pulse',
  heartbeat: 'animate-heartbeat',

  // Spin/rotate
  spin: 'animate-spin',
  spinSlow: 'animate-spin-slow',

  // Shimmer/skeleton
  shimmer: 'animate-shimmer',

  // Progress
  indeterminateProgress: 'animate-indeterminate-progress',
} as const;

/**
 * Animation Delay Utilities
 */
export const delays = {
  none: 0,
  short: 75,
  medium: 150,
  long: 300,
  veryLong: 500,
} as const;

/**
 * Spring Animation Configuration
 * For physics-based animations
 */
export const springs = {
  // Gentle spring - smooth, natural
  gentle: {
    type: 'spring',
    stiffness: 100,
    damping: 15,
  },

  // Bouncy spring - playful
  bouncy: {
    type: 'spring',
    stiffness: 200,
    damping: 10,
  },

  // Stiff spring - quick, responsive
  stiff: {
    type: 'spring',
    stiffness: 300,
    damping: 20,
  },

  // Slow spring - deliberate
  slow: {
    type: 'spring',
    stiffness: 50,
    damping: 15,
  },
} as const;

/**
 * Utility Functions
 */

/**
 * Create a custom transition string
 */
export const createTransition = (
  properties: string[],
  duration: number = durations.normal,
  easing: string = easings.standard,
  delay: number = 0
): string => {
  return properties
    .map(prop => `${prop} ${duration}ms ${easing}${delay ? ` ${delay}ms` : ''}`)
    .join(', ');
};

/**
 * Get staggered animation delay for list items
 */
export const getStaggerDelay = (index: number, baseDelay: number = 50): number => {
  return index * baseDelay;
};

/**
 * Combine multiple animation classes
 */
export const combineAnimations = (...animationClasses: string[]): string => {
  return animationClasses.filter(Boolean).join(' ');
};

/**
 * Animation Utilities for React Components
 */

/**
 * Hook-like utility to get staggered items
 * Use this for animating lists with staggered delays
 */
export const withStagger = <T,>(
  items: T[],
  baseDelay: number = delays.short
): Array<T & { animationDelay: string }> => {
  return items.map((item, index) => ({
    ...item,
    animationDelay: `${getStaggerDelay(index, baseDelay)}ms`,
  }));
};

/**
 * Preloaded animation variants for common patterns
 */
export const variants = {
  // Hover scale effect
  hoverScale: {
    rest: { scale: 1 },
    hover: { scale: 1.05 },
  },

  // Hover lift effect (scale + translate)
  hoverLift: {
    rest: { scale: 1, y: 0 },
    hover: { scale: 1.02, y: -4 },
  },

  // Button press effect
  buttonPress: {
    rest: { scale: 1 },
    press: { scale: 0.95 },
  },

  // Modal/Dialog entrance
  modalEntrance: {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
  },

  // Drawer slide
  drawerSlide: {
    hidden: { x: '-100%' },
    visible: { x: 0 },
    exit: { x: '-100%' },
  },

  // Fade variants
  fade: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
    exit: { opacity: 0 },
  },

  // List stagger container
  staggerContainer: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  },

  // List stagger item
  staggerItem: {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  },
} as const;

/**
 * CSS-in-JS style objects for common animations
 */
export const styles = {
  // Smooth hover effect
  hoverEffect: {
    transition: transitions.hover,
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    },
  },

  // Button hover
  buttonHover: {
    transition: transitions.button,
    '&:hover': {
      transform: 'scale(1.02)',
    },
    '&:active': {
      transform: 'scale(0.98)',
    },
  },

  // Card hover
  cardHover: {
    transition: transitions.hover,
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
    },
  },

  // Focus ring
  focusRing: {
    transition: `box-shadow ${durations.fast}ms ${easings.standard}`,
    '&:focus': {
      outline: 'none',
      boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.5)',
    },
  },
} as const;

export default {
  easings,
  durations,
  transitions,
  animations,
  delays,
  springs,
  variants,
  styles,
  createTransition,
  getStaggerDelay,
  combineAnimations,
  withStagger,
};
