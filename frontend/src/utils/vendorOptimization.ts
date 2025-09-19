// frontend/src/utils/vendorOptimization.ts
// PRODUCTION_READY: Utilidades de optimización para componentes de vendedor
// Optimizado para condiciones de red colombianas y dispositivos móviles

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';

// Tipos para optimización
export interface NetworkConditions {
  effectiveType: '2g' | '3g' | '4g' | 'slow-2g';
  downlink: number;
  rtt: number;
  saveData: boolean;
}

export interface ImageOptimizationOptions {
  quality: number;
  format: 'webp' | 'jpeg' | 'png';
  maxWidth: number;
  maxHeight: number;
  lazy: boolean;
}

export interface VendorPerformanceConfig {
  enableLazyLoading: boolean;
  enableImageOptimization: boolean;
  enableDataSaving: boolean;
  debounceMs: number;
  cacheMaxAge: number;
}

// Hook para detectar condiciones de red
export const useNetworkConditions = (): NetworkConditions | null => {
  const [networkInfo, setNetworkInfo] = useState<NetworkConditions | null>(null);

  useEffect(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;

      const updateNetworkInfo = () => {
        setNetworkInfo({
          effectiveType: connection.effectiveType || '4g',
          downlink: connection.downlink || 10,
          rtt: connection.rtt || 50,
          saveData: connection.saveData || false
        });
      };

      updateNetworkInfo();
      connection.addEventListener('change', updateNetworkInfo);

      return () => {
        connection.removeEventListener('change', updateNetworkInfo);
      };
    }
  }, []);

  return networkInfo;
};

// Hook para configuración adaptativa basada en red
export const useAdaptiveConfig = (): VendorPerformanceConfig => {
  const networkInfo = useNetworkConditions();

  return useMemo(() => {
    if (!networkInfo) {
      return {
        enableLazyLoading: true,
        enableImageOptimization: true,
        enableDataSaving: false,
        debounceMs: 300,
        cacheMaxAge: 300000 // 5 minutos
      };
    }

    const isSlowNetwork = networkInfo.effectiveType === '2g' || networkInfo.effectiveType === 'slow-2g';
    const isSaveDataEnabled = networkInfo.saveData;

    return {
      enableLazyLoading: true,
      enableImageOptimization: true,
      enableDataSaving: isSlowNetwork || isSaveDataEnabled,
      debounceMs: isSlowNetwork ? 600 : 300,
      cacheMaxAge: isSlowNetwork ? 600000 : 300000 // 10 min para redes lentas, 5 min para redes rápidas
    };
  }, [networkInfo]);
};

// Hook para carga lazy de imágenes
export const useLazyImage = (src: string, options: Partial<ImageOptimizationOptions> = {}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const config = useAdaptiveConfig();

  const defaultOptions: ImageOptimizationOptions = {
    quality: config.enableDataSaving ? 60 : 80,
    format: 'webp',
    maxWidth: config.enableDataSaving ? 400 : 800,
    maxHeight: config.enableDataSaving ? 400 : 800,
    lazy: config.enableLazyLoading,
    ...options
  };

  // Intersection Observer para lazy loading
  useEffect(() => {
    if (!defaultOptions.lazy || !imgRef.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );

    observer.observe(imgRef.current);

    return () => observer.disconnect();
  }, [defaultOptions.lazy]);

  // Cargar imagen cuando está en vista
  useEffect(() => {
    if (!isInView && defaultOptions.lazy) return;

    const img = new Image();
    img.onload = () => setIsLoaded(true);
    img.onerror = () => setError('Error al cargar la imagen');

    // Generar URL optimizada
    const optimizedSrc = generateOptimizedImageUrl(src, defaultOptions);
    img.src = optimizedSrc;
  }, [isInView, src, defaultOptions]);

  return {
    imgRef,
    isLoaded: defaultOptions.lazy ? (isInView && isLoaded) : isLoaded,
    error,
    src: defaultOptions.lazy && !isInView ? '' : generateOptimizedImageUrl(src, defaultOptions)
  };
};

// Generar URL de imagen optimizada
export const generateOptimizedImageUrl = (
  src: string,
  options: ImageOptimizationOptions
): string => {
  if (!src || src.startsWith('data:') || src.startsWith('blob:')) {
    return src;
  }

  // Si es una URL externa, mantenerla como está
  if (src.startsWith('http') && !src.includes(window.location.origin)) {
    return src;
  }

  // Para URLs internas, agregar parámetros de optimización
  const url = new URL(src, window.location.origin);
  url.searchParams.set('q', options.quality.toString());
  url.searchParams.set('f', options.format);
  url.searchParams.set('w', options.maxWidth.toString());
  url.searchParams.set('h', options.maxHeight.toString());

  return url.toString();
};

// Hook para debounce optimizado
export const useOptimizedDebounce = <T>(value: T, delay?: number): T => {
  const config = useAdaptiveConfig();
  const actualDelay = delay || config.debounceMs;
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, actualDelay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, actualDelay]);

  return debouncedValue;
};

// Cache adaptativo para datos de vendedor
export class VendorDataCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private config: VendorPerformanceConfig;

  constructor(config: VendorPerformanceConfig) {
    this.config = config;
  }

  set(key: string, data: any, customTtl?: number): void {
    const ttl = customTtl || this.config.cacheMaxAge;
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);

    if (!entry) return null;

    const isExpired = Date.now() - entry.timestamp > entry.ttl;

    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// Hook para cache de datos
export const useVendorCache = () => {
  const config = useAdaptiveConfig();
  const cacheRef = useRef<VendorDataCache>();

  if (!cacheRef.current) {
    cacheRef.current = new VendorDataCache(config);
  }

  return cacheRef.current;
};

// Utilidad para formateo de números grandes (optimizado para móviles)
export const formatCompactNumber = (num: number, locale: string = 'es-CO'): string => {
  const config = useAdaptiveConfig();

  // En dispositivos con poco ancho de banda, usar formato más compacto
  if (config.enableDataSaving) {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  }

  // Formato completo para redes rápidas
  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    maximumFractionDigits: 1
  }).format(num);
};

// Hook para optimización de renderizado de listas
export const useVirtualizedList = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length]);

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex).map((item, index) => ({
      item,
      index: visibleRange.startIndex + index
    }));
  }, [items, visibleRange]);

  const totalHeight = items.length * itemHeight;

  return {
    visibleItems,
    totalHeight,
    offsetY: visibleRange.startIndex * itemHeight,
    onScroll: (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    }
  };
};

// Utilidad para detección de dispositivos móviles
export const useDeviceDetection = () => {
  return useMemo(() => {
    const userAgent = navigator.userAgent;
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    const isTablet = /iPad/i.test(userAgent) || (isMobile && window.innerWidth > 768);
    const isDesktop = !isMobile && !isTablet;
    const isTouchDevice = 'ontouchstart' in window;

    return {
      isMobile: isMobile && !isTablet,
      isTablet,
      isDesktop,
      isTouchDevice,
      screenSize: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };
  }, []);
};

// Hook para gestión de offline
export const useOfflineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};

// Utilidad para optimización de imágenes de productos
export const optimizeProductImage = (
  file: File,
  options: Partial<ImageOptimizationOptions> = {}
): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const config = useAdaptiveConfig();

    const defaultOptions: ImageOptimizationOptions = {
      quality: config.enableDataSaving ? 0.6 : 0.8,
      format: 'webp',
      maxWidth: config.enableDataSaving ? 800 : 1200,
      maxHeight: config.enableDataSaving ? 600 : 900,
      lazy: false,
      ...options
    };

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      // Calcular dimensiones manteniendo aspect ratio
      const { width, height } = calculateAspectRatio(
        img.width,
        img.height,
        defaultOptions.maxWidth,
        defaultOptions.maxHeight
      );

      canvas.width = width;
      canvas.height = height;

      // Dibujar imagen redimensionada
      ctx?.drawImage(img, 0, 0, width, height);

      // Convertir a blob
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Error al optimizar imagen'));
          }
        },
        defaultOptions.format === 'webp' ? 'image/webp' : `image/${defaultOptions.format}`,
        defaultOptions.quality
      );
    };

    img.onerror = () => reject(new Error('Error al cargar imagen'));
    img.src = URL.createObjectURL(file);
  });
};

// Calcular aspect ratio
const calculateAspectRatio = (
  originalWidth: number,
  originalHeight: number,
  maxWidth: number,
  maxHeight: number
): { width: number; height: number } => {
  const aspectRatio = originalWidth / originalHeight;

  let width = originalWidth;
  let height = originalHeight;

  if (width > maxWidth) {
    width = maxWidth;
    height = width / aspectRatio;
  }

  if (height > maxHeight) {
    height = maxHeight;
    width = height * aspectRatio;
  }

  return { width: Math.round(width), height: Math.round(height) };
};

// Export de todas las utilidades
export {
  useNetworkConditions,
  useAdaptiveConfig,
  useLazyImage,
  useOptimizedDebounce,
  useVendorCache,
  useVirtualizedList,
  useDeviceDetection,
  useOfflineStatus,
  optimizeProductImage,
  formatCompactNumber
};