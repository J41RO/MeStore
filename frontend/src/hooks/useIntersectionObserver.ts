import { useEffect, useRef, useState } from 'react';

interface UseIntersectionObserverOptions {
  root?: Element | null;
  rootMargin?: string;
  threshold?: number | number[];
  freezeOnceVisible?: boolean;
}

interface UseIntersectionObserverResult {
  ref: React.RefObject<HTMLElement>;
  isIntersecting: boolean;
  entry: IntersectionObserverEntry | null;
}

export function useIntersectionObserver(
  options: UseIntersectionObserverOptions = {}
): UseIntersectionObserverResult {
  const {
    root = null,
    rootMargin = '50px', // Load images 50px before they're visible
    threshold = 0.1,
    freezeOnceVisible = true
  } = options;

  const ref = useRef<HTMLElement>(null);
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasBeenVisible, setHasBeenVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    
    // Check if IntersectionObserver is supported
    if (!element || !window.IntersectionObserver) {
      // Fallback: assume element is visible if IntersectionObserver is not supported
      setIsIntersecting(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]: IntersectionObserverEntry[]) => {
        const isElementIntersecting = entry?.isIntersecting || false;
        
        setEntry(entry || null);
        
        if (isElementIntersecting) {
          setIsIntersecting(true);
          setHasBeenVisible(true);
          
          // If freezeOnceVisible is true, stop observing once visible
          if (freezeOnceVisible) {
            observer.unobserve(element);
          }
        } else if (!freezeOnceVisible || !hasBeenVisible) {
          setIsIntersecting(false);
        }
      },
      {
        root,
        rootMargin,
        threshold
      }
    );

    observer.observe(element);

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, [root, rootMargin, threshold, freezeOnceVisible, hasBeenVisible]);

  return {
    ref,
    isIntersecting: freezeOnceVisible ? hasBeenVisible || isIntersecting : isIntersecting,
    entry
  };
}

// Hook specifically for lazy loading images
export function useLazyImage(src: string, options: UseIntersectionObserverOptions = {}) {
  const { ref, isIntersecting } = useIntersectionObserver({
    rootMargin: '100px', // Start loading 100px before visible
    freezeOnceVisible: true,
    ...options
  });

  const [imageSrc, setImageSrc] = useState<string>('');
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (isIntersecting && src && !imageSrc) {
      // Preload the image
      const img = new Image();
      
      img.onload = () => {
        setImageSrc(src);
        setIsLoaded(true);
        setHasError(false);
      };
      
      img.onerror = () => {
        setHasError(true);
        setIsLoaded(false);
      };
      
      img.src = src;
    }
  }, [isIntersecting, src, imageSrc]);

  return {
    ref,
    src: imageSrc,
    isLoaded,
    hasError,
    isIntersecting
  };
}

export default useIntersectionObserver;