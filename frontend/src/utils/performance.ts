/**
 * Performance Optimization Utilities for Mobile
 * Optimized for Colombian 3G networks and low-end devices
 */

// Network connection types and speed estimates
interface NetworkInfo {
  effectiveType: string;
  downlink: number;
  rtt: number;
  saveData: boolean;
}

interface PerformanceConfig {
  imageQuality: 'low' | 'medium' | 'high';
  enableLazyLoading: boolean;
  preloadCritical: boolean;
  enableCompression: boolean;
  enableCaching: boolean;
}

/**
 * Detects network quality and returns performance configuration
 */
export const getNetworkBasedConfig = (): PerformanceConfig => {
  const connection = (navigator as any).connection;
  const defaultConfig: PerformanceConfig = {
    imageQuality: 'medium',
    enableLazyLoading: true,
    preloadCritical: true,
    enableCompression: true,
    enableCaching: true
  };

  if (!connection) {
    return defaultConfig;
  }

  const networkInfo: NetworkInfo = {
    effectiveType: connection.effectiveType || '4g',
    downlink: connection.downlink || 10,
    rtt: connection.rtt || 100,
    saveData: connection.saveData || false
  };

  // Optimize for slow connections (common in Colombia)
  if (networkInfo.effectiveType === 'slow-2g' || networkInfo.effectiveType === '2g') {
    return {
      imageQuality: 'low',
      enableLazyLoading: true,
      preloadCritical: false,
      enableCompression: true,
      enableCaching: true
    };
  }

  // Optimize for 3G (most common in Colombian regions)
  if (networkInfo.effectiveType === '3g') {
    return {
      imageQuality: 'medium',
      enableLazyLoading: true,
      preloadCritical: true,
      enableCompression: true,
      enableCaching: true
    };
  }

  // Honor data saver preference (common in Colombia)
  if (networkInfo.saveData) {
    return {
      imageQuality: 'low',
      enableLazyLoading: true,
      preloadCritical: false,
      enableCompression: true,
      enableCaching: true
    };
  }

  return defaultConfig;
};

/**
 * Image optimization based on network and device capabilities
 */
export class ImageOptimizer {
  private config: PerformanceConfig;

  constructor() {
    this.config = getNetworkBasedConfig();
  }

  /**
   * Gets optimized image URL with appropriate quality and format
   */
  getOptimizedImageUrl(
    originalUrl: string,
    width?: number,
    height?: number
  ): string {
    if (!originalUrl) return '';

    const url = new URL(originalUrl, window.location.origin);
    const params = new URLSearchParams();

    // Add quality parameter
    switch (this.config.imageQuality) {
      case 'low':
        params.append('q', '60');
        params.append('f', 'webp');
        break;
      case 'medium':
        params.append('q', '75');
        params.append('f', 'webp');
        break;
      case 'high':
        params.append('q', '90');
        break;
    }

    // Add dimensions if provided
    if (width) params.append('w', width.toString());
    if (height) params.append('h', height.toString());

    // Enable compression for slow networks
    if (this.config.enableCompression) {
      params.append('compress', 'true');
    }

    url.search = params.toString();
    return url.toString();
  }

  /**
   * Creates responsive image sources for different screen densities
   */
  getResponsiveImageSources(
    originalUrl: string,
    sizes: { width: number; density?: number }[]
  ): string {
    return sizes
      .map(({ width, density = 1 }) => {
        const optimizedUrl = this.getOptimizedImageUrl(originalUrl, width);
        return `${optimizedUrl} ${density}x`;
      })
      .join(', ');
  }

  /**
   * Preloads critical images
   */
  preloadImage(url: string, priority: 'high' | 'low' = 'low'): Promise<void> {
    if (!this.config.preloadCritical && priority === 'low') {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = reject;
      img.src = this.getOptimizedImageUrl(url);
    });
  }
}

/**
 * Lazy loading utility optimized for mobile scrolling
 */
export class LazyLoader {
  private observer: IntersectionObserver | null = null;
  private config: PerformanceConfig;

  constructor() {
    this.config = getNetworkBasedConfig();
    this.initObserver();
  }

  private initObserver() {
    if (!('IntersectionObserver' in window) || !this.config.enableLazyLoading) {
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.loadElement(entry.target as HTMLElement);
            this.observer?.unobserve(entry.target);
          }
        });
      },
      {
        root: null,
        rootMargin: '50px', // Load images 50px before they come into view
        threshold: 0.1
      }
    );
  }

  private loadElement(element: HTMLElement) {
    if (element.tagName === 'IMG') {
      const img = element as HTMLImageElement;
      const dataSrc = img.getAttribute('data-src');
      if (dataSrc) {
        img.src = dataSrc;
        img.removeAttribute('data-src');
        img.classList.add('loaded');
      }
    } else {
      // Handle background images
      const dataBg = element.getAttribute('data-bg');
      if (dataBg) {
        element.style.backgroundImage = `url(${dataBg})`;
        element.removeAttribute('data-bg');
        element.classList.add('loaded');
      }
    }
  }

  observe(element: HTMLElement) {
    if (this.observer) {
      this.observer.observe(element);
    } else {
      // Fallback: load immediately if Intersection Observer not supported
      this.loadElement(element);
    }
  }

  unobserve(element: HTMLElement) {
    if (this.observer) {
      this.observer.unobserve(element);
    }
  }
}

/**
 * Bundle optimization utilities
 */
export const BundleOptimizer = {
  /**
   * Dynamically imports components based on route
   */
  async loadComponent<T>(importFn: () => Promise<T>): Promise<T> {
    const startTime = performance.now();

    try {
      const component = await importFn();
      const loadTime = performance.now() - startTime;

      // Log slow loads for monitoring
      if (loadTime > 1000) {
        console.warn(`Slow component load: ${loadTime}ms`);
      }

      return component;
    } catch (error) {
      console.error('Component load failed:', error);
      throw error;
    }
  },

  /**
   * Preloads route components for likely navigation
   */
  preloadRoutes(routes: (() => Promise<any>)[]) {
    const config = getNetworkBasedConfig();

    // Only preload on fast connections
    if (config.imageQuality === 'high') {
      routes.forEach((route) => {
        // Use requestIdleCallback if available
        if ('requestIdleCallback' in window) {
          (window as any).requestIdleCallback(() => route());
        } else {
          setTimeout(() => route(), 100);
        }
      });
    }
  }
};

/**
 * Memory optimization for mobile devices
 */
export const MemoryOptimizer = {
  /**
   * Monitors memory usage and triggers cleanup
   */
  monitorMemory() {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      const usedPercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;

      if (usedPercent > 80) {
        this.triggerCleanup();
      }
    }
  },

  /**
   * Triggers garbage collection and cleanup
   */
  triggerCleanup() {
    // Clear unused caches
    if ('caches' in window) {
      caches.keys().then((cacheNames) => {
        cacheNames.forEach((cacheName) => {
          if (cacheName.includes('old') || cacheName.includes('temp')) {
            caches.delete(cacheName);
          }
        });
      });
    }

    // Clear large arrays or objects from memory
    console.log('Memory cleanup triggered');
  },

  /**
   * Optimizes large lists with virtual scrolling
   */
  shouldUseVirtualScrolling(itemCount: number): boolean {
    // Use virtual scrolling for lists > 100 items on mobile
    const isMobile = window.innerWidth < 768;
    return isMobile && itemCount > 100;
  }
};

/**
 * Colombian-specific performance optimizations
 */
export const ColombianOptimizer = {
  /**
   * Optimizes for common Colombian mobile patterns
   */
  getOptimizationSettings() {
    const isMobile = window.innerWidth < 768;
    const isLowEndDevice = navigator.hardwareConcurrency <= 2;

    return {
      // Reduce animations on low-end devices
      enableAnimations: !isLowEndDevice,

      // Optimize for frequent WhatsApp switching
      enableFastResuming: isMobile,

      // Reduce memory usage for limited RAM devices
      enableMemoryOptimization: isLowEndDevice,

      // Optimize for portrait usage (common in Colombia)
      optimizeForPortrait: isMobile,

      // Enable offline support for connectivity issues
      enableOfflineFirst: true,

      // Optimize images for data saving (common concern)
      enableDataSaving: true
    };
  },

  /**
   * Sets up performance monitoring for Colombian market
   */
  setupPerformanceMonitoring() {
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            console.log('LCP:', entry.startTime);
          }
          if (entry.entryType === 'first-input') {
            console.log('FID:', (entry as any).processingStart - entry.startTime);
          }
          if (entry.entryType === 'layout-shift') {
            console.log('CLS:', (entry as any).value);
          }
        });
      });

      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    }
  }
};

// Initialize performance monitoring
export const initPerformanceOptimization = () => {
  const settings = ColombianOptimizer.getOptimizationSettings();

  // Set up monitoring
  ColombianOptimizer.setupPerformanceMonitoring();

  // Monitor memory usage every 30 seconds
  if (settings.enableMemoryOptimization) {
    setInterval(() => {
      MemoryOptimizer.monitorMemory();
    }, 30000);
  }

  // Add performance hints to document
  const config = getNetworkBasedConfig();
  document.documentElement.style.setProperty(
    '--image-quality',
    config.imageQuality
  );

  return {
    imageOptimizer: new ImageOptimizer(),
    lazyLoader: new LazyLoader(),
    settings
  };
};

export default {
  getNetworkBasedConfig,
  ImageOptimizer,
  LazyLoader,
  BundleOptimizer,
  MemoryOptimizer,
  ColombianOptimizer,
  initPerformanceOptimization
};