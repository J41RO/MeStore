// frontend/src/utils/reactOptimizations.tsx
// REACT_PERFORMANCE: Optimization utilities for React components
// Target: 60fps rendering, minimal re-renders, optimized reconciliation

import React, { memo, useMemo, useCallback, useRef, useEffect } from 'react';

// Performance-optimized memo with custom comparison
export const deepMemo = <T extends Record<string, any>>(
  Component: React.ComponentType<T>,
  customComparison?: (prevProps: T, nextProps: T) => boolean
): React.ComponentType<T> => {
  return memo(Component, customComparison || ((prevProps, nextProps) => {
    // Deep comparison for objects and arrays
    const keys = Object.keys(nextProps);
    if (keys.length !== Object.keys(prevProps).length) return false;

    for (const key of keys) {
      const prevValue = prevProps[key];
      const nextValue = nextProps[key];

      if (prevValue === nextValue) continue;

      // Handle arrays
      if (Array.isArray(prevValue) && Array.isArray(nextValue)) {
        if (prevValue.length !== nextValue.length) return false;
        for (let i = 0; i < prevValue.length; i++) {
          if (prevValue[i] !== nextValue[i]) return false;
        }
        continue;
      }

      // Handle objects
      if (
        typeof prevValue === 'object' &&
        typeof nextValue === 'object' &&
        prevValue !== null &&
        nextValue !== null
      ) {
        const prevKeys = Object.keys(prevValue);
        const nextKeys = Object.keys(nextValue);

        if (prevKeys.length !== nextKeys.length) return false;

        for (const objKey of prevKeys) {
          if (prevValue[objKey] !== nextValue[objKey]) return false;
        }
        continue;
      }

      return false;
    }

    return true;
  }));
};

// Optimized list rendering with virtualization support
interface OptimizedListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string;
  className?: string;
  itemHeight?: number;
  containerHeight?: number;
  overscan?: number;
}

export const OptimizedList = memo(<T extends any>({
  items,
  renderItem,
  keyExtractor,
  className = '',
  itemHeight = 100,
  containerHeight = 400,
  overscan = 5
}: OptimizedListProps<T>) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(items.length, start + visibleCount + overscan * 2);
    return { start, end };
  }, [scrollTop, itemHeight, containerHeight, overscan, items.length]);

  // Memoized visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end).map((item, index) => ({
      item,
      originalIndex: visibleRange.start + index
    }));
  }, [items, visibleRange]);

  // Optimized scroll handler
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, originalIndex }) => (
          <div
            key={keyExtractor(item, originalIndex)}
            style={{
              position: 'absolute',
              top: originalIndex * itemHeight,
              left: 0,
              right: 0,
              height: itemHeight
            }}
          >
            {renderItem(item, originalIndex)}
          </div>
        ))}
      </div>
    </div>
  );
}) as <T>(props: OptimizedListProps<T>) => JSX.Element;

// Optimized form field with debounced updates
interface OptimizedFormFieldProps {
  value: string;
  onChange: (value: string) => void;
  debounceMs?: number;
  placeholder?: string;
  className?: string;
  type?: string;
}

export const OptimizedFormField = memo(({
  value,
  onChange,
  debounceMs = 300,
  placeholder,
  className = '',
  type = 'text'
}: OptimizedFormFieldProps) => {
  const [localValue, setLocalValue] = React.useState(value);
  const timeoutRef = useRef<NodeJS.Timeout>();

  // Sync with external value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Debounced update handler
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setLocalValue(newValue);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      onChange(newValue);
    }, debounceMs);
  }, [onChange, debounceMs]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <input
      type={type}
      value={localValue}
      onChange={handleChange}
      placeholder={placeholder}
      className={className}
    />
  );
});

// Optimized image component with lazy loading
interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  placeholder?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export const OptimizedImage = memo(({
  src,
  alt,
  className = '',
  width,
  height,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRjNGNEY2Ii8+Cjx0ZXh0IHg9IjE1MCIgeT0iMTUwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5Q0EzQUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIwLjNlbSI+TG9hZGluZy4uLjwvdGV4dD4KPHN2Zz4K',
  onLoad,
  onError
}: OptimizedImageProps) => {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);
  const [isInView, setIsInView] = React.useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver>();

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    observerRef.current = observer;

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Image load handlers
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    setHasError(false);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setHasError(true);
    setIsLoaded(false);
    onError?.();
  }, [onError]);

  const displaySrc = isInView ? (hasError ? placeholder : src) : placeholder;

  return (
    <img
      ref={imgRef}
      src={displaySrc}
      alt={alt}
      className={`transition-opacity duration-300 ${
        isLoaded ? 'opacity-100' : 'opacity-50'
      } ${className}`}
      width={width}
      height={height}
      onLoad={handleLoad}
      onError={handleError}
      loading="lazy"
    />
  );
});

// Optimized modal with focus management and escape handling
interface OptimizedModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  overlayClassName?: string;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

export const OptimizedModal = memo(({
  isOpen,
  onClose,
  children,
  className = '',
  overlayClassName = '',
  closeOnOverlayClick = true,
  closeOnEscape = true
}: OptimizedModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement>();

  // Focus management
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousActiveElement.current?.focus();
    }
  }, [isOpen]);

  // Escape key handler
  useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose, closeOnEscape]);

  // Click outside handler
  const handleOverlayClick = useCallback((e: React.MouseEvent) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose, closeOnOverlayClick]);

  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 ${overlayClassName}`}
      onClick={handleOverlayClick}
    >
      <div
        ref={modalRef}
        className={`bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto ${className}`}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
      >
        {children}
      </div>
    </div>
  );
});

// Optimized button with automatic loading state
interface OptimizedButtonProps {
  onClick: () => Promise<void> | void;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  loadingText?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const OptimizedButton = memo(({
  onClick,
  children,
  className = '',
  disabled = false,
  loadingText = 'Loading...',
  type = 'button'
}: OptimizedButtonProps) => {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleClick = useCallback(async () => {
    if (isLoading || disabled) return;

    try {
      setIsLoading(true);
      await onClick();
    } finally {
      setIsLoading(false);
    }
  }, [onClick, isLoading, disabled]);

  return (
    <button
      type={type}
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`transition-all duration-200 ${
        isLoading ? 'opacity-50 cursor-not-allowed' : ''
      } ${className}`}
    >
      {isLoading ? loadingText : children}
    </button>
  );
});

// Performance context for tracking render counts
interface PerformanceContextValue {
  renderCount: number;
  lastRenderTime: number;
  incrementRender: () => void;
}

const PerformanceContext = React.createContext<PerformanceContextValue | null>(null);

export const PerformanceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [renderCount, setRenderCount] = React.useState(0);
  const [lastRenderTime, setLastRenderTime] = React.useState(Date.now());

  const incrementRender = useCallback(() => {
    setRenderCount(prev => prev + 1);
    setLastRenderTime(Date.now());
  }, []);

  const value = useMemo(() => ({
    renderCount,
    lastRenderTime,
    incrementRender
  }), [renderCount, lastRenderTime, incrementRender]);

  return (
    <PerformanceContext.Provider value={value}>
      {children}
    </PerformanceContext.Provider>
  );
};

export const usePerformanceContext = () => {
  const context = React.useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformanceContext must be used within a PerformanceProvider');
  }
  return context;
};

// Hook for tracking component render performance
export const useRenderPerformance = (componentName: string) => {
  const renderStartTime = useRef(0);
  const renderCount = useRef(0);

  useEffect(() => {
    renderStartTime.current = performance.now();
    renderCount.current += 1;
  });

  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;

    if (renderTime > 16) { // > 60fps threshold
      console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms (render #${renderCount.current})`);
    }
  });

  return {
    renderCount: renderCount.current,
    componentName
  };
};

export default {
  deepMemo,
  OptimizedList,
  OptimizedFormField,
  OptimizedImage,
  OptimizedModal,
  OptimizedButton,
  PerformanceProvider,
  usePerformanceContext,
  useRenderPerformance
};