/**
 * Transition Components
 *
 * Reusable transition wrappers for consistent animations across the application
 */

import React, { ReactNode, useEffect, useState } from 'react';
import { transitions, durations, easings } from '../../utils/animations';

interface TransitionProps {
  children: ReactNode;
  show: boolean;
  className?: string;
  appear?: boolean;
}

/**
 * FadeTransition - Smooth fade in/out
 */
export const FadeTransition: React.FC<TransitionProps> = ({
  children,
  show,
  className = '',
  appear = true,
}) => {
  const [shouldRender, setShouldRender] = useState(show);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      setTimeout(() => setIsVisible(true), 10);
    } else {
      setIsVisible(false);
      setTimeout(() => setShouldRender(false), durations.normal);
    }
  }, [show]);

  if (!shouldRender && !appear) return null;
  if (!shouldRender) return null;

  return (
    <div
      className={`transition-opacity ${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transition: transitions.fade,
      }}
    >
      {children}
    </div>
  );
};

/**
 * ScaleTransition - Scale up/down with fade
 */
export const ScaleTransition: React.FC<TransitionProps> = ({
  children,
  show,
  className = '',
  appear = true,
}) => {
  const [shouldRender, setShouldRender] = useState(show);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      setTimeout(() => setIsVisible(true), 10);
    } else {
      setIsVisible(false);
      setTimeout(() => setShouldRender(false), durations.moderate);
    }
  }, [show]);

  if (!shouldRender && !appear) return null;
  if (!shouldRender) return null;

  return (
    <div
      className={`${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'scale(1)' : 'scale(0.95)',
        transition: transitions.modal,
      }}
    >
      {children}
    </div>
  );
};

/**
 * SlideTransition - Slide from direction
 */
interface SlideTransitionProps extends TransitionProps {
  direction?: 'left' | 'right' | 'up' | 'down';
  distance?: number;
}

export const SlideTransition: React.FC<SlideTransitionProps> = ({
  children,
  show,
  className = '',
  appear = true,
  direction = 'up',
  distance = 20,
}) => {
  const [shouldRender, setShouldRender] = useState(show);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      setTimeout(() => setIsVisible(true), 10);
    } else {
      setIsVisible(false);
      setTimeout(() => setShouldRender(false), durations.moderate);
    }
  }, [show]);

  if (!shouldRender && !appear) return null;
  if (!shouldRender) return null;

  const getTransform = () => {
    if (isVisible) return 'translate(0, 0)';

    switch (direction) {
      case 'left':
        return `translateX(-${distance}px)`;
      case 'right':
        return `translateX(${distance}px)`;
      case 'up':
        return `translateY(${distance}px)`;
      case 'down':
        return `translateY(-${distance}px)`;
      default:
        return 'translate(0, 0)';
    }
  };

  return (
    <div
      className={`${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: getTransform(),
        transition: `opacity ${durations.moderate}ms ${easings.emphasized}, transform ${durations.moderate}ms ${easings.emphasized}`,
      }}
    >
      {children}
    </div>
  );
};

/**
 * CollapseTransition - Expand/collapse height
 */
export const CollapseTransition: React.FC<TransitionProps> = ({
  children,
  show,
  className = '',
}) => {
  const [height, setHeight] = useState<number | 'auto'>(show ? 'auto' : 0);
  const contentRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (show) {
      // Get the natural height
      const naturalHeight = contentRef.current?.scrollHeight || 0;
      setHeight(naturalHeight);
      // After animation, set to auto for dynamic content
      setTimeout(() => setHeight('auto'), durations.moderate);
    } else {
      // Set to current height first
      const currentHeight = contentRef.current?.scrollHeight || 0;
      setHeight(currentHeight);
      // Then animate to 0
      setTimeout(() => setHeight(0), 10);
    }
  }, [show]);

  return (
    <div
      ref={contentRef}
      className={`overflow-hidden ${className}`}
      style={{
        height: height === 'auto' ? 'auto' : `${height}px`,
        transition: transitions.size,
      }}
    >
      {children}
    </div>
  );
};

/**
 * StaggeredList - Animate list items with stagger
 */
interface StaggeredListProps {
  children: ReactNode[];
  className?: string;
  itemClassName?: string;
  staggerDelay?: number;
}

export const StaggeredList: React.FC<StaggeredListProps> = ({
  children,
  className = '',
  itemClassName = '',
  staggerDelay = 75,
}) => {
  const [visibleItems, setVisibleItems] = useState<number>(0);

  useEffect(() => {
    // Trigger animation on mount
    const timer = setInterval(() => {
      setVisibleItems((prev) => {
        if (prev >= children.length) {
          clearInterval(timer);
          return prev;
        }
        return prev + 1;
      });
    }, staggerDelay);

    return () => clearInterval(timer);
  }, [children.length, staggerDelay]);

  return (
    <div className={className}>
      {React.Children.map(children, (child, index) => (
        <div
          key={index}
          className={`${itemClassName} ${
            index < visibleItems ? 'animate-fade-in-up' : 'opacity-0'
          }`}
          style={{
            animationDelay: `${index * staggerDelay}ms`,
          }}
        >
          {child}
        </div>
      ))}
    </div>
  );
};

/**
 * ModalTransition - Optimized for modal/dialog animations
 */
interface ModalTransitionProps extends TransitionProps {
  backdrop?: boolean;
  onClose?: () => void;
}

export const ModalTransition: React.FC<ModalTransitionProps> = ({
  children,
  show,
  className = '',
  backdrop = true,
  onClose,
}) => {
  const [shouldRender, setShouldRender] = useState(show);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      // Add overflow hidden to body
      document.body.style.overflow = 'hidden';
      setTimeout(() => setIsVisible(true), 10);
    } else {
      setIsVisible(false);
      setTimeout(() => {
        setShouldRender(false);
        // Restore overflow
        document.body.style.overflow = '';
      }, durations.moderate);
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [show]);

  if (!shouldRender) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={(e) => {
        if (backdrop && e.target === e.currentTarget && onClose) {
          onClose();
        }
      }}
    >
      {/* Backdrop */}
      {backdrop && (
        <div
          className="absolute inset-0 bg-black"
          style={{
            opacity: isVisible ? 0.5 : 0,
            transition: transitions.fade,
          }}
        />
      )}

      {/* Modal content */}
      <div
        className={`relative z-10 ${className}`}
        style={{
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'scale(1)' : 'scale(0.95)',
          transition: transitions.modal,
        }}
      >
        {children}
      </div>
    </div>
  );
};

/**
 * PageTransition - For page-level transitions
 */
export const PageTransition: React.FC<{ children: ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation on mount
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  return (
    <div
      className={`${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        transition: transitions.page,
      }}
    >
      {children}
    </div>
  );
};

export default {
  Fade: FadeTransition,
  Scale: ScaleTransition,
  Slide: SlideTransition,
  Collapse: CollapseTransition,
  StaggeredList,
  Modal: ModalTransition,
  Page: PageTransition,
};
