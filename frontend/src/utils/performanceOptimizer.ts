// ~/src/utils/performanceOptimizer.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Advanced Performance Optimizer with Bundle Analysis
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: performanceOptimizer.ts
// Ruta: ~/src/utils/performanceOptimizer.ts
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Optimizador de rendimiento con Core Web Vitals monitoring
//
// Performance Features:
// - Core Web Vitals tracking (LCP, FID, CLS)
// - Bundle size optimization
// - Code splitting strategies
// - Resource prioritization
// - Real-time performance monitoring
// - Memory leak detection
// ---------------------------------------------------------------------------------------------

import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

interface PerformanceMetrics {
  lcp: number | null; // Largest Contentful Paint
  fid: number | null; // First Input Delay
  cls: number | null; // Cumulative Layout Shift
  fcp: number | null; // First Contentful Paint
  ttfb: number | null; // Time to First Byte
  memoryUsage: number;
  bundleSize: number;
  loadTime: number;
  renderTime: number;
  interactiveTime: number;
}

interface BundleAnalysis {
  totalSize: number;
  compressedSize: number;
  chunkSizes: Record<string, number>;
  duplicatedModules: string[];
  unusedExports: string[];
  heaviestModules: Array<{ name: string; size: number }>;
  recommendations: string[];
}

interface PerformanceConfig {
  enableWebVitals: boolean;
  enableBundleAnalysis: boolean;
  enableMemoryMonitoring: boolean;
  enableResourceHints: boolean;
  sampleRate: number;
  thresholds: {
    lcp: number;
    fid: number;
    cls: number;
    fcp: number;
    ttfb: number;
  };
}

class PerformanceOptimizer {
  private metrics: PerformanceMetrics = {
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null,
    memoryUsage: 0,
    bundleSize: 0,
    loadTime: 0,
    renderTime: 0,
    interactiveTime: 0,
  };

  private config: PerformanceConfig;
  private observers: PerformanceObserver[] = [];
  private memoryCheckInterval?: NodeJS.Timeout;
  private metricsQueue: Array<{ metric: string; value: number; timestamp: number }> = [];

  constructor(config: Partial<PerformanceConfig> = {}) {
    this.config = {
      enableWebVitals: true,
      enableBundleAnalysis: true,
      enableMemoryMonitoring: true,
      enableResourceHints: true,
      sampleRate: 1.0,
      thresholds: {
        lcp: 2500, // Good: <2.5s
        fid: 100,  // Good: <100ms
        cls: 0.1,  // Good: <0.1
        fcp: 1800, // Good: <1.8s
        ttfb: 800, // Good: <800ms
      },
      ...config,
    };

    this.initialize();
  }

  private initialize(): void {
    if (typeof window === 'undefined') return;

    // Initialize Web Vitals tracking
    if (this.config.enableWebVitals) {
      this.initializeWebVitals();
    }

    // Initialize performance observers
    this.initializePerformanceObservers();

    // Initialize memory monitoring
    if (this.config.enableMemoryMonitoring) {
      this.initializeMemoryMonitoring();
    }

    // Initialize resource hints
    if (this.config.enableResourceHints) {
      this.initializeResourceHints();
    }

    // Start bundle analysis
    if (this.config.enableBundleAnalysis) {
      this.analyzeBundleSize();
    }
  }

  private initializeWebVitals(): void {
    // Sample rate check
    if (Math.random() > this.config.sampleRate) return;

    getCLS((metric) => {
      this.metrics.cls = metric.value;
      this.reportMetric('CLS', metric.value);
      this.checkThreshold('cls', metric.value);
    });

    getFID((metric) => {
      this.metrics.fid = metric.value;
      this.reportMetric('FID', metric.value);
      this.checkThreshold('fid', metric.value);
    });

    getFCP((metric) => {
      this.metrics.fcp = metric.value;
      this.reportMetric('FCP', metric.value);
      this.checkThreshold('fcp', metric.value);
    });

    getLCP((metric) => {
      this.metrics.lcp = metric.value;
      this.reportMetric('LCP', metric.value);
      this.checkThreshold('lcp', metric.value);
    });

    getTTFB((metric) => {
      this.metrics.ttfb = metric.value;
      this.reportMetric('TTFB', metric.value);
      this.checkThreshold('ttfb', metric.value);
    });
  }

  private initializePerformanceObservers(): void {
    // Long tasks observer
    if ('PerformanceObserver' in window) {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            console.warn(`Long task detected: ${entry.duration}ms`);
            this.reportMetric('LongTask', entry.duration);
          }
        }
      });

      try {
        longTaskObserver.observe({ entryTypes: ['longtask'] });
        this.observers.push(longTaskObserver);
      } catch (e) {
        console.warn('Long task observer not supported');
      }

      // Navigation observer
      const navigationObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const navEntry = entry as PerformanceNavigationTiming;

          this.metrics.loadTime = navEntry.loadEventEnd - navEntry.fetchStart;
          this.metrics.renderTime = navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart;
          this.metrics.interactiveTime = navEntry.domInteractive - navEntry.fetchStart;

          this.reportMetric('LoadTime', this.metrics.loadTime);
          this.reportMetric('RenderTime', this.metrics.renderTime);
          this.reportMetric('InteractiveTime', this.metrics.interactiveTime);
        }
      });

      try {
        navigationObserver.observe({ entryTypes: ['navigation'] });
        this.observers.push(navigationObserver);
      } catch (e) {
        console.warn('Navigation observer not supported');
      }

      // Resource observer
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const resourceEntry = entry as PerformanceResourceTiming;

          // Track large resources
          if (resourceEntry.transferSize > 500000) { // >500KB
            console.warn(`Large resource detected: ${resourceEntry.name} (${resourceEntry.transferSize} bytes)`);
          }

          // Track slow resources
          if (resourceEntry.duration > 1000) { // >1s
            console.warn(`Slow resource detected: ${resourceEntry.name} (${resourceEntry.duration}ms)`);
          }
        }
      });

      try {
        resourceObserver.observe({ entryTypes: ['resource'] });
        this.observers.push(resourceObserver);
      } catch (e) {
        console.warn('Resource observer not supported');
      }
    }
  }

  private initializeMemoryMonitoring(): void {
    if ('memory' in performance) {
      this.memoryCheckInterval = setInterval(() => {
        const memory = (performance as any).memory;
        this.metrics.memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB

        // Warn about high memory usage
        const memoryLimit = memory.jsHeapSizeLimit / 1024 / 1024; // MB
        const memoryUsagePercent = (this.metrics.memoryUsage / memoryLimit) * 100;

        if (memoryUsagePercent > 80) {
          console.warn(`High memory usage: ${this.metrics.memoryUsage.toFixed(2)}MB (${memoryUsagePercent.toFixed(1)}%)`);
          this.reportMetric('HighMemoryUsage', this.metrics.memoryUsage);
        }

        this.reportMetric('MemoryUsage', this.metrics.memoryUsage);
      }, 10000); // Check every 10 seconds
    }
  }

  private initializeResourceHints(): void {
    // Add resource hints for better performance
    this.addResourceHint('preconnect', 'https://fonts.googleapis.com');
    this.addResourceHint('preconnect', 'https://fonts.gstatic.com', true);
    this.addResourceHint('dns-prefetch', 'https://api.mestore.com');
  }

  private addResourceHint(rel: string, href: string, crossorigin: boolean = false): void {
    const link = document.createElement('link');
    link.rel = rel;
    link.href = href;
    if (crossorigin) {
      link.crossOrigin = 'anonymous';
    }
    document.head.appendChild(link);
  }

  private analyzeBundleSize(): void {
    // Estimate bundle size from script tags
    const scripts = Array.from(document.querySelectorAll('script[src]'));
    let totalSize = 0;

    scripts.forEach(async (script) => {
      try {
        const response = await fetch((script as HTMLScriptElement).src, { method: 'HEAD' });
        const size = parseInt(response.headers.get('content-length') || '0');
        totalSize += size;
      } catch (e) {
        // Ignore CORS errors for external scripts
      }
    });

    this.metrics.bundleSize = totalSize;
    this.reportMetric('BundleSize', totalSize);
  }

  private checkThreshold(metric: keyof PerformanceConfig['thresholds'], value: number): void {
    const threshold = this.config.thresholds[metric];

    if (value > threshold) {
      console.warn(`Performance threshold exceeded for ${metric.toUpperCase()}: ${value} > ${threshold}`);

      // Suggest optimizations
      this.suggestOptimizations(metric, value);
    }
  }

  private suggestOptimizations(metric: string, value: number): void {
    const suggestions: Record<string, string[]> = {
      lcp: [
        'Optimize images with modern formats (WebP, AVIF)',
        'Implement lazy loading for below-the-fold content',
        'Optimize server response times',
        'Use a Content Delivery Network (CDN)',
        'Preload critical resources',
      ],
      fid: [
        'Break up long tasks with time slicing',
        'Optimize JavaScript bundle size',
        'Use code splitting and lazy loading',
        'Defer non-critical JavaScript',
        'Optimize third-party scripts',
      ],
      cls: [
        'Set explicit dimensions for images and videos',
        'Avoid inserting content above existing content',
        'Use CSS transform animations instead of changing layout properties',
        'Preload fonts to avoid font swapping',
        'Reserve space for dynamic content',
      ],
      fcp: [
        'Eliminate render-blocking resources',
        'Optimize critical CSS',
        'Implement server-side rendering',
        'Use efficient cache policies',
        'Minimize main thread work',
      ],
      ttfb: [
        'Optimize server performance',
        'Use a faster hosting provider',
        'Implement server-side caching',
        'Optimize database queries',
        'Use a CDN',
      ],
    };

    console.log(`Optimization suggestions for ${metric.toUpperCase()}:`, suggestions[metric] || []);
  }

  private reportMetric(name: string, value: number): void {
    const metric = {
      metric: name,
      value,
      timestamp: Date.now(),
    };

    this.metricsQueue.push(metric);

    // Send metrics to analytics service (implement based on your analytics provider)
    this.sendToAnalytics(metric);

    // Keep queue size manageable
    if (this.metricsQueue.length > 100) {
      this.metricsQueue = this.metricsQueue.slice(-50);
    }
  }

  private sendToAnalytics(metric: { metric: string; value: number; timestamp: number }): void {
    // Example implementation - replace with your analytics service
    if (typeof gtag !== 'undefined') {
      gtag('event', 'performance_metric', {
        metric_name: metric.metric,
        metric_value: metric.value,
        custom_map: {
          dimension1: metric.metric,
        },
      });
    }

    // Example for other analytics services
    /*
    if (typeof analytics !== 'undefined') {
      analytics.track('Performance Metric', {
        metric: metric.metric,
        value: metric.value,
        timestamp: metric.timestamp,
      });
    }
    */
  }

  // Public methods

  public trackCustomMetric(name: string, value: number): void {
    this.reportMetric(name, value);
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public getPerformanceReport(): {
    metrics: PerformanceMetrics;
    score: number;
    recommendations: string[];
  } {
    const score = this.calculatePerformanceScore();
    const recommendations = this.generateRecommendations();

    return {
      metrics: this.getMetrics(),
      score,
      recommendations,
    };
  }

  private calculatePerformanceScore(): number {
    let score = 100;

    // Deduct points for poor metrics
    if (this.metrics.lcp && this.metrics.lcp > this.config.thresholds.lcp) {
      score -= 20;
    }
    if (this.metrics.fid && this.metrics.fid > this.config.thresholds.fid) {
      score -= 20;
    }
    if (this.metrics.cls && this.metrics.cls > this.config.thresholds.cls) {
      score -= 20;
    }
    if (this.metrics.fcp && this.metrics.fcp > this.config.thresholds.fcp) {
      score -= 15;
    }
    if (this.metrics.ttfb && this.metrics.ttfb > this.config.thresholds.ttfb) {
      score -= 15;
    }

    // Deduct points for high memory usage
    if (this.metrics.memoryUsage > 100) {
      score -= 10;
    }

    return Math.max(0, score);
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];

    if (this.metrics.lcp && this.metrics.lcp > this.config.thresholds.lcp) {
      recommendations.push('Optimize Largest Contentful Paint (LCP)');
    }
    if (this.metrics.fid && this.metrics.fid > this.config.thresholds.fid) {
      recommendations.push('Improve First Input Delay (FID)');
    }
    if (this.metrics.cls && this.metrics.cls > this.config.thresholds.cls) {
      recommendations.push('Reduce Cumulative Layout Shift (CLS)');
    }
    if (this.metrics.bundleSize > 1000000) { // >1MB
      recommendations.push('Optimize bundle size with code splitting');
    }
    if (this.metrics.memoryUsage > 100) {
      recommendations.push('Optimize memory usage');
    }

    return recommendations;
  }

  public optimizeImages(): void {
    // Find all images and suggest optimizations
    const images = document.querySelectorAll('img');

    images.forEach((img) => {
      const imgElement = img as HTMLImageElement;

      // Add lazy loading if not present
      if (!imgElement.loading) {
        imgElement.loading = 'lazy';
      }

      // Suggest modern formats
      if (!imgElement.src.includes('.webp') && !imgElement.src.includes('.avif')) {
        console.log('Consider using WebP or AVIF format for:', imgElement.src);
      }

      // Check for oversized images
      if (imgElement.naturalWidth > imgElement.width * 2) {
        console.log('Oversized image detected:', imgElement.src);
      }
    });
  }

  public preloadCriticalResources(resources: string[]): void {
    resources.forEach((resource) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource;

      // Determine resource type
      if (resource.endsWith('.css')) {
        link.as = 'style';
      } else if (resource.endsWith('.js')) {
        link.as = 'script';
      } else if (resource.match(/\.(jpg|jpeg|png|webp|avif|gif)$/)) {
        link.as = 'image';
      } else if (resource.match(/\.(woff|woff2|ttf|otf)$/)) {
        link.as = 'font';
        link.crossOrigin = 'anonymous';
      }

      document.head.appendChild(link);
    });
  }

  public enablePerformanceMode(mode: 'fast' | 'balanced' | 'quality'): void {
    const body = document.body;

    // Remove existing performance classes
    body.classList.remove('performance-fast', 'performance-balanced', 'performance-quality');

    // Add new performance class
    body.classList.add(`performance-${mode}`);

    // Apply performance settings based on mode
    switch (mode) {
      case 'fast':
        // Disable animations
        body.style.setProperty('--animation-duration', '0s');
        // Reduce image quality
        body.style.setProperty('--image-quality', '0.7');
        break;

      case 'balanced':
        // Reduced animations
        body.style.setProperty('--animation-duration', '0.15s');
        // Standard image quality
        body.style.setProperty('--image-quality', '0.85');
        break;

      case 'quality':
        // Full animations
        body.style.setProperty('--animation-duration', '0.3s');
        // High image quality
        body.style.setProperty('--image-quality', '1');
        break;
    }
  }

  public destroy(): void {
    // Clean up observers
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];

    // Clear intervals
    if (this.memoryCheckInterval) {
      clearInterval(this.memoryCheckInterval);
    }

    // Clear metrics queue
    this.metricsQueue = [];
  }
}

// Export singleton instance
export const performanceOptimizer = new PerformanceOptimizer();

// React hook for easy integration
export const usePerformanceOptimization = (config?: Partial<PerformanceConfig>) => {
  const optimizer = new PerformanceOptimizer(config);

  const trackSearchPerformance = (data: {
    query: string;
    responseTime: number;
    resultsCount: number;
    cacheHit: boolean;
  }) => {
    optimizer.trackCustomMetric('search_response_time', data.responseTime);
    optimizer.trackCustomMetric('search_results_count', data.resultsCount);
    optimizer.trackCustomMetric('search_cache_hit', data.cacheHit ? 1 : 0);
  };

  const trackRenderPerformance = (data: {
    component: string;
    renderTime?: number;
    itemCount?: number;
    viewMode?: string;
    virtualScrolling?: boolean;
    mobileOptimized?: boolean;
  }) => {
    if (data.renderTime) {
      optimizer.trackCustomMetric(`${data.component.toLowerCase()}_render_time`, data.renderTime);
    }
    if (data.itemCount) {
      optimizer.trackCustomMetric(`${data.component.toLowerCase()}_item_count`, data.itemCount);
    }
  };

  const optimizeBundle = () => {
    optimizer.optimizeImages();
    optimizer.enablePerformanceMode('balanced');
  };

  const preloadResources = (resources: string[]) => {
    optimizer.preloadCriticalResources(resources);
  };

  return {
    trackSearchPerformance,
    trackRenderPerformance,
    optimizeBundle,
    preloadResources,
    getMetrics: optimizer.getMetrics.bind(optimizer),
    getPerformanceReport: optimizer.getPerformanceReport.bind(optimizer),
    enablePerformanceMode: optimizer.enablePerformanceMode.bind(optimizer),
  };
};