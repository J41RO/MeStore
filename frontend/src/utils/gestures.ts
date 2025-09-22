/**
 * Gesture Utilities for Mobile UX
 * Provides touch interactions and gesture recognition for MeStocker mobile app
 */

import { useGesture } from '@use-gesture/react';
import { useSpring, animated } from '@framer-motion/spring';

export interface GestureConfig {
  swipeThreshold?: number;
  pinchThreshold?: number;
  tapThreshold?: number;
  longPressThreshold?: number;
}

export interface SwipeHandler {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

export interface PinchHandler {
  onPinchStart?: (scale: number) => void;
  onPinch?: (scale: number) => void;
  onPinchEnd?: (scale: number) => void;
}

export interface TapHandler {
  onTap?: (event: TouchEvent | MouseEvent) => void;
  onDoubleTap?: (event: TouchEvent | MouseEvent) => void;
  onLongPress?: (event: TouchEvent | MouseEvent) => void;
}

// Default configuration for Colombian mobile users
const DEFAULT_CONFIG: Required<GestureConfig> = {
  swipeThreshold: 50, // Minimum distance for swipe recognition
  pinchThreshold: 0.1, // Minimum scale change for pinch recognition
  tapThreshold: 10, // Maximum movement for tap recognition
  longPressThreshold: 500 // Minimum time for long press (ms)
};

/**
 * Hook for swipe gestures
 * Optimized for Colombian mobile shopping patterns
 */
export const useSwipeGestures = (
  handlers: SwipeHandler,
  config: GestureConfig = {}
) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  return useGesture({
    onDrag: ({ movement: [mx, my], direction: [xDir, yDir], distance, cancel }) => {
      if (distance > finalConfig.swipeThreshold) {
        // Horizontal swipes (navigation)
        if (Math.abs(mx) > Math.abs(my)) {
          if (xDir > 0 && handlers.onSwipeRight) {
            handlers.onSwipeRight();
            cancel();
          } else if (xDir < 0 && handlers.onSwipeLeft) {
            handlers.onSwipeLeft();
            cancel();
          }
        }
        // Vertical swipes (scroll actions)
        else {
          if (yDir > 0 && handlers.onSwipeDown) {
            handlers.onSwipeDown();
            cancel();
          } else if (yDir < 0 && handlers.onSwipeUp) {
            handlers.onSwipeUp();
            cancel();
          }
        }
      }
    }
  });
};

/**
 * Hook for pinch zoom gestures
 * Useful for product images and maps
 */
export const usePinchGestures = (
  handlers: PinchHandler,
  config: GestureConfig = {}
) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  return useGesture({
    onPinch: ({ offset: [scale], first, last }) => {
      if (first && handlers.onPinchStart) {
        handlers.onPinchStart(scale);
      } else if (last && handlers.onPinchEnd) {
        handlers.onPinchEnd(scale);
      } else if (handlers.onPinch) {
        handlers.onPinch(scale);
      }
    }
  });
};

/**
 * Hook for tap gestures
 * Handles tap, double tap, and long press
 */
export const useTapGestures = (
  handlers: TapHandler,
  config: GestureConfig = {}
) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  let tapCount = 0;
  let tapTimer: NodeJS.Timeout | null = null;
  let longPressTimer: NodeJS.Timeout | null = null;

  return useGesture({
    onPointerDown: ({ event }) => {
      // Start long press timer
      if (handlers.onLongPress) {
        longPressTimer = setTimeout(() => {
          handlers.onLongPress!(event as TouchEvent | MouseEvent);
          tapCount = 0; // Cancel tap if long press triggered
        }, finalConfig.longPressThreshold);
      }
    },

    onPointerUp: ({ event, distance }) => {
      // Clear long press timer
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        longPressTimer = null;
      }

      // Check if movement was minimal (tap vs drag)
      if (distance < finalConfig.tapThreshold) {
        tapCount++;

        if (tapCount === 1) {
          // Wait for potential second tap
          tapTimer = setTimeout(() => {
            if (handlers.onTap) {
              handlers.onTap(event as TouchEvent | MouseEvent);
            }
            tapCount = 0;
          }, 300); // Double tap window
        } else if (tapCount === 2) {
          // Double tap detected
          if (tapTimer) {
            clearTimeout(tapTimer);
            tapTimer = null;
          }
          if (handlers.onDoubleTap) {
            handlers.onDoubleTap(event as TouchEvent | MouseEvent);
          }
          tapCount = 0;
        }
      }
    }
  });
};

/**
 * Combined gesture hook for complex interactions
 * Useful for product cards, image galleries, etc.
 */
export const useCombinedGestures = (
  swipeHandlers: SwipeHandler,
  tapHandlers: TapHandler,
  pinchHandlers?: PinchHandler,
  config: GestureConfig = {}
) => {
  const swipeGestures = useSwipeGestures(swipeHandlers, config);
  const tapGestures = useTapGestures(tapHandlers, config);
  const pinchGestures = pinchHandlers ? usePinchGestures(pinchHandlers, config) : {};

  // Combine all gesture handlers
  return {
    ...swipeGestures(),
    ...tapGestures(),
    ...pinchGestures
  };
};

/**
 * Hook for pull-to-refresh gesture
 * Colombian users expect this on mobile shopping apps
 */
export const usePullToRefresh = (
  onRefresh: () => Promise<void>,
  threshold: number = 80
) => {
  const [spring, setSpring] = useSpring(() => ({ y: 0 }));
  let isRefreshing = false;

  return useGesture({
    onDrag: ({ movement: [, my], first, last, cancel }) => {
      // Only trigger on downward swipe from top
      if (window.scrollY > 0) return;

      if (first) {
        isRefreshing = false;
      }

      if (my > 0 && my < threshold * 2) {
        setSpring({ y: my * 0.5 });
      }

      if (last) {
        if (my > threshold && !isRefreshing) {
          isRefreshing = true;
          setSpring({ y: threshold });

          onRefresh().finally(() => {
            setSpring({ y: 0 });
            isRefreshing = false;
          });
        } else {
          setSpring({ y: 0 });
        }
      }
    }
  });
};

/**
 * Hook for shopping cart swipe actions
 * Remove, favorite, quantity adjustments
 */
export const useCartSwipeActions = (
  itemId: string,
  actions: {
    onRemove?: () => void;
    onFavorite?: () => void;
    onIncrease?: () => void;
    onDecrease?: () => void;
  }
) => {
  const [spring, setSpring] = useSpring(() => ({ x: 0, opacity: 1 }));

  return useGesture({
    onDrag: ({ movement: [mx], direction: [xDir], last, cancel }) => {
      if (Math.abs(mx) < 20) return; // Minimum swipe distance

      if (!last) {
        setSpring({ x: mx * 0.3 }); // Damped movement
      } else {
        // Determine action based on swipe direction and distance
        if (Math.abs(mx) > 80) {
          if (xDir > 0) {
            // Swipe right - favorite or decrease
            if (mx > 150 && actions.onFavorite) {
              actions.onFavorite();
            } else if (actions.onDecrease) {
              actions.onDecrease();
            }
          } else {
            // Swipe left - remove or increase
            if (mx < -150 && actions.onRemove) {
              setSpring({ x: -300, opacity: 0 });
              setTimeout(() => actions.onRemove!(), 200);
              return;
            } else if (actions.onIncrease) {
              actions.onIncrease();
            }
          }
        }

        // Reset position
        setSpring({ x: 0 });
      }
    }
  });
};

/**
 * Touch feedback utilities
 * Provides haptic and visual feedback for Colombian mobile users
 */
export const TouchFeedback = {
  // Haptic feedback (if supported)
  vibrate: (pattern: number | number[] = 10) => {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  },

  // Light feedback for successful actions
  success: () => {
    TouchFeedback.vibrate([10, 50, 10]);
  },

  // Medium feedback for warnings
  warning: () => {
    TouchFeedback.vibrate([50, 100, 50]);
  },

  // Strong feedback for errors
  error: () => {
    TouchFeedback.vibrate([100, 50, 100, 50, 100]);
  },

  // Subtle feedback for button taps
  tap: () => {
    TouchFeedback.vibrate(5);
  },

  // CSS class for touch visual feedback
  getTouchClass: (active: boolean = false) => {
    return active
      ? 'transform scale-95 transition-transform duration-75'
      : 'transform scale-100 transition-transform duration-75';
  }
};

/**
 * Mobile-optimized infinite scroll hook
 * For product listings with Colombian 3G network optimization
 */
export const useInfiniteScroll = (
  loadMore: () => Promise<void>,
  threshold: number = 200
) => {
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = async () => {
      if (isLoading) return;

      const { scrollTop, scrollHeight, clientHeight } = document.documentElement;

      if (scrollTop + clientHeight >= scrollHeight - threshold) {
        setIsLoading(true);
        await loadMore();
        setIsLoading(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadMore, threshold, isLoading]);

  return { isLoading };
};

export default {
  useSwipeGestures,
  usePinchGestures,
  useTapGestures,
  useCombinedGestures,
  usePullToRefresh,
  useCartSwipeActions,
  TouchFeedback,
  useInfiniteScroll
};