import React, { useState, useCallback } from 'react';
import { useLazyImage } from '../../hooks/useIntersectionObserver';

interface LazyImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
  webpSrc?: string;
  blurDataURL?: string;
  width?: number;
  height?: number;
  sizes?: string;
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNzUgMTI1SDIyNVYxNzVIMTc1VjEyNVoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTE4NSAxMzVIMTk1VjE0NUgxODVWMTM1WiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K',
  webpSrc,
  blurDataURL,
  width,
  height,
  sizes,
  priority = false,
  onLoad,
  onError
}) => {
  const [imageError, setImageError] = useState(false);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  
  // Use priority loading for above-fold images  
  const { ref, src: loadedSrc, isLoaded, hasError, isIntersecting } = useLazyImage(
    priority ? src : src, 
    {
      rootMargin: priority ? '0px' : '100px', // Load immediately if priority
      freezeOnceVisible: true
    }
  );

  // Check if browser supports WebP
  const supportsWebP = useCallback(() => {
    if (typeof window === 'undefined') return false;
    
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }, []);

  // Determine which source to use
  const getImageSrc = useCallback(() => {
    if (imageError || hasError) return placeholder;
    if (priority) return webpSrc && supportsWebP() ? webpSrc : src;
    if (isIntersecting && loadedSrc) {
      return webpSrc && supportsWebP() ? webpSrc : loadedSrc;
    }
    return blurDataURL || placeholder;
  }, [imageError, hasError, priority, webpSrc, src, isIntersecting, loadedSrc, blurDataURL, placeholder, supportsWebP]);

  const handleImageLoad = useCallback(() => {
    setIsImageLoaded(true);
    setImageError(false);
    onLoad?.();
  }, [onLoad]);

  const handleImageError = useCallback(() => {
    setImageError(true);
    setIsImageLoaded(false);
    onError?.();
  }, [onError]);

  // Calculate aspect ratio for responsive images
  const aspectRatio = width && height ? (height / width) * 100 : undefined;

  return (
    <div 
      ref={ref as React.RefObject<HTMLDivElement>}
      className={`relative overflow-hidden ${className}`}
      style={{
        ...(aspectRatio && { paddingBottom: `${aspectRatio}%` }),
        ...(width && !aspectRatio && { width }),
        ...(height && !aspectRatio && { height }),
      }}
    >
      {/* Placeholder/blur background */}
      {(!isImageLoaded || (!isLoaded && !priority)) && (
        <div 
          className={`absolute inset-0 bg-gray-200 ${
            blurDataURL ? 'bg-cover bg-center' : 'flex items-center justify-center'
          }`}
          style={blurDataURL ? { backgroundImage: `url(${blurDataURL})` } : undefined}
        >
          {!blurDataURL && (
            <div className="w-12 h-12 text-gray-400">
              <svg
                className="w-full h-full animate-pulse"
                fill="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </div>
      )}
      
      {/* Loading indicator */}
      {isIntersecting && !isImageLoaded && !priority && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="w-8 h-8">
            <svg
              className="w-full h-full animate-spin text-blue-500"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        </div>
      )}

      {/* Actual image */}
      <img
        src={getImageSrc()}
        alt={alt}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        className={`
          transition-opacity duration-500 
          ${aspectRatio ? 'absolute inset-0 w-full h-full object-cover' : 'w-full h-full object-cover'}
          ${isImageLoaded && (isLoaded || priority) && !hasError ? 'opacity-100' : 'opacity-0'}
        `}
        onLoad={handleImageLoad}
        onError={handleImageError}
        {...(width && { width })}
        {...(height && { height })}
        {...(sizes && { sizes })}
      />

      {/* Error state */}
      {(imageError || hasError) && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 text-gray-400">
          <div className="text-center">
            <svg
              className="w-12 h-12 mx-auto mb-2"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                fillRule="evenodd"
                d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm">Error al cargar imagen</p>
          </div>
        </div>
      )}
    </div>
  );
};

// HOC for existing img elements
export const withLazyLoading = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return React.forwardRef<any, P>((props, ref) => {
    return <Component {...(props as any)} ref={ref} loading="lazy" decoding="async" />;
  });
};

// Simple lazy img component for quick replacements
export const LazyImg: React.FC<React.ImgHTMLAttributes<HTMLImageElement>> = ({
  src,
  alt = '',
  className = '',
  ...props
}) => {
  const { ref, isIntersecting } = useLazyImage(src || '', {
    rootMargin: '50px'
  });

  if (!src) {
    return <div className={`bg-gray-200 ${className}`} />;
  }

  return (
    <img
      ref={ref as React.RefObject<HTMLImageElement>}
      src={isIntersecting ? src : 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'}
      alt={alt}
      className={className}
      loading="lazy"
      decoding="async"
      {...props}
    />
  );
};

export default LazyImage;