/**
 * PWA Testing and Validation Utilities
 * Tests PWA functionality and validates implementation
 */

interface PWATestResult {
  test: string;
  passed: boolean;
  message: string;
  score: number; // 0-100
}

interface PWATestReport {
  overallScore: number;
  results: PWATestResult[];
  recommendations: string[];
}

export class PWAValidator {
  private results: PWATestResult[] = [];

  /**
   * Runs comprehensive PWA validation tests
   */
  async validatePWA(): Promise<PWATestReport> {
    this.results = [];

    // Core PWA tests
    await this.testServiceWorker();
    await this.testManifest();
    await this.testInstallability();
    await this.testOfflineSupport();
    await this.testPerformance();
    await this.testMobileOptimization();
    await this.testNetworkOptimization();
    await this.testColombianFeatures();

    const overallScore = this.calculateOverallScore();
    const recommendations = this.generateRecommendations();

    return {
      overallScore,
      results: this.results,
      recommendations
    };
  }

  private async testServiceWorker(): Promise<void> {
    const test = 'Service Worker Registration';

    try {
      if (!('serviceWorker' in navigator)) {
        this.addResult(test, false, 'Service Worker not supported', 0);
        return;
      }

      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        this.addResult(test, true, 'Service Worker registered successfully', 100);
      } else {
        this.addResult(test, false, 'Service Worker not registered', 0);
      }
    } catch (error) {
      this.addResult(test, false, `Service Worker error: ${error}`, 0);
    }
  }

  private async testManifest(): Promise<void> {
    const test = 'Web App Manifest';

    try {
      const manifestLink = document.querySelector('link[rel="manifest"]');
      if (!manifestLink) {
        this.addResult(test, false, 'Manifest link not found', 0);
        return;
      }

      const manifestUrl = (manifestLink as HTMLLinkElement).href;
      const response = await fetch(manifestUrl);
      const manifest = await response.json();

      let score = 0;
      const requirements = [
        { key: 'name', weight: 20 },
        { key: 'short_name', weight: 15 },
        { key: 'icons', weight: 25 },
        { key: 'start_url', weight: 15 },
        { key: 'display', weight: 15 },
        { key: 'theme_color', weight: 10 }
      ];

      requirements.forEach(({ key, weight }) => {
        if (manifest[key]) score += weight;
      });

      // Check icons specifically
      if (manifest.icons && manifest.icons.length > 0) {
        const hasRequiredSizes = manifest.icons.some((icon: any) =>
          ['192x192', '512x512'].includes(icon.sizes)
        );
        if (!hasRequiredSizes) score -= 10;
      }

      this.addResult(
        test,
        score >= 80,
        `Manifest score: ${score}/100`,
        score
      );
    } catch (error) {
      this.addResult(test, false, `Manifest error: ${error}`, 0);
    }
  }

  private async testInstallability(): Promise<void> {
    const test = 'PWA Installability';

    // Test if app can be installed
    const installPromptAvailable = 'beforeinstallprompt' in window;
    const standalone = window.matchMedia('(display-mode: standalone)').matches;
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

    let score = 0;
    let message = '';

    if (standalone) {
      score = 100;
      message = 'App is already installed';
    } else if (installPromptAvailable) {
      score = 90;
      message = 'App is installable (Android/Desktop)';
    } else if (iOS) {
      score = 70;
      message = 'Manual installation available (iOS)';
    } else {
      score = 30;
      message = 'Installation may not be available';
    }

    this.addResult(test, score >= 70, message, score);
  }

  private async testOfflineSupport(): Promise<void> {
    const test = 'Offline Functionality';

    try {
      // Test cache availability
      if (!('caches' in window)) {
        this.addResult(test, false, 'Cache API not supported', 0);
        return;
      }

      const cacheNames = await caches.keys();
      const hasWorkboxCache = cacheNames.some(name =>
        name.includes('workbox') || name.includes('precache')
      );

      let score = 0;
      if (hasWorkboxCache) score += 50;

      // Test if critical resources are cached
      const criticalUrls = ['/', '/manifest.json'];
      for (const url of criticalUrls) {
        try {
          const cache = await caches.open(cacheNames[0] || 'test');
          const response = await cache.match(url);
          if (response) score += 25;
        } catch (error) {
          // Cache miss is okay
        }
      }

      this.addResult(
        test,
        score >= 50,
        `Offline support score: ${score}/100`,
        score
      );
    } catch (error) {
      this.addResult(test, false, `Offline test error: ${error}`, 0);
    }
  }

  private async testPerformance(): Promise<void> {
    const test = 'Mobile Performance';

    let score = 100;
    const performance = window.performance;

    // Test First Contentful Paint
    if (performance && performance.getEntriesByType) {
      const paintEntries = performance.getEntriesByType('paint');
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');

      if (fcp) {
        const fcpTime = fcp.startTime;
        if (fcpTime > 3000) score -= 30; // >3s is poor on mobile
        else if (fcpTime > 2000) score -= 15; // >2s is needs improvement
      }
    }

    // Test bundle size
    const scripts = document.querySelectorAll('script[src]');
    let totalScriptSize = 0;

    for (const script of scripts) {
      try {
        const src = (script as HTMLScriptElement).src;
        if (src.includes('/assets/')) {
          // Estimate size from URL or use Performance API
          totalScriptSize += 500; // Rough estimate
        }
      } catch (error) {
        // Ignore CORS errors
      }
    }

    if (totalScriptSize > 1000) score -= 20; // >1MB is poor for mobile

    // Test device capabilities
    const hardwareConcurrency = navigator.hardwareConcurrency || 2;
    if (hardwareConcurrency <= 2) {
      // Adjust expectations for low-end devices
      score = Math.max(score - 10, 60);
    }

    this.addResult(
      test,
      score >= 70,
      `Performance score: ${score}/100`,
      score
    );
  }

  private async testMobileOptimization(): Promise<void> {
    const test = 'Mobile UX Optimization';

    let score = 0;

    // Test viewport configuration
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport && (viewport as HTMLMetaElement).content.includes('width=device-width')) {
      score += 20;
    }

    // Test touch target sizes
    const buttons = document.querySelectorAll('button, a[href], input');
    const touchFriendlyButtons = Array.from(buttons).filter(button => {
      const rect = button.getBoundingClientRect();
      return rect.width >= 44 && rect.height >= 44;
    });

    const touchFriendlyPercentage = (touchFriendlyButtons.length / buttons.length) * 100;
    score += touchFriendlyPercentage * 0.3; // Max 30 points

    // Test font sizes
    const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
    const readableText = Array.from(textElements).filter(element => {
      const style = window.getComputedStyle(element);
      const fontSize = parseInt(style.fontSize);
      return fontSize >= 16;
    });

    const readablePercentage = (readableText.length / textElements.length) * 100;
    score += readablePercentage * 0.2; // Max 20 points

    // Test for mobile-specific features
    const hasBottomNav = document.querySelector('[class*="bottom"]') !== null;
    const hasMobileMenu = document.querySelector('[class*="mobile"]') !== null;

    if (hasBottomNav) score += 15;
    if (hasMobileMenu) score += 15;

    this.addResult(
      test,
      score >= 70,
      `Mobile optimization score: ${Math.round(score)}/100`,
      Math.round(score)
    );
  }

  private async testNetworkOptimization(): Promise<void> {
    const test = '3G Network Optimization';

    let score = 0;

    // Test image optimization
    const images = document.querySelectorAll('img');
    const optimizedImages = Array.from(images).filter(img => {
      return img.src.includes('webp') ||
             img.src.includes('q=') ||
             img.hasAttribute('loading') ||
             img.hasAttribute('data-src');
    });

    if (images.length > 0) {
      const optimizationPercentage = (optimizedImages.length / images.length) * 100;
      score += optimizationPercentage * 0.4; // Max 40 points
    } else {
      score += 40; // No images to optimize
    }

    // Test lazy loading
    const lazyElements = document.querySelectorAll('[loading="lazy"], [data-src]');
    if (lazyElements.length > 0) score += 20;

    // Test compression headers (if available)
    try {
      const response = await fetch(window.location.href, { method: 'HEAD' });
      const contentEncoding = response.headers.get('content-encoding');
      if (contentEncoding && (contentEncoding.includes('gzip') || contentEncoding.includes('br'))) {
        score += 20;
      }
    } catch (error) {
      // Cannot test headers in this context
      score += 10; // Assume compression is enabled
    }

    // Test resource hints
    const preconnects = document.querySelectorAll('link[rel="preconnect"]');
    const preloads = document.querySelectorAll('link[rel="preload"]');

    if (preconnects.length > 0) score += 10;
    if (preloads.length > 0) score += 10;

    this.addResult(
      test,
      score >= 70,
      `Network optimization score: ${Math.round(score)}/100`,
      Math.round(score)
    );
  }

  private async testColombianFeatures(): Promise<void> {
    const test = 'Colombian Market Features';

    let score = 0;

    // Test language localization
    const htmlLang = document.documentElement.lang;
    if (htmlLang === 'es' || htmlLang === 'es-CO') score += 20;

    // Test currency formatting
    const priceElements = document.querySelectorAll('[class*="price"], [data-currency]');
    const hasCOPCurrency = Array.from(priceElements).some(element =>
      element.textContent?.includes('COP') ||
      element.textContent?.includes('$') ||
      element.textContent?.includes('peso')
    );
    if (hasCOPCurrency) score += 15;

    // Test payment methods (PSE, Colombian banks)
    const paymentText = document.body.textContent || '';
    const hasColombianPayments = paymentText.includes('PSE') ||
                                 paymentText.includes('Bancolombia') ||
                                 paymentText.includes('Nequi') ||
                                 paymentText.includes('DaviPlata');
    if (hasColombianPayments) score += 25;

    // Test location references
    const hasColombianLocations = paymentText.includes('Bucaramanga') ||
                                  paymentText.includes('Santander') ||
                                  paymentText.includes('Colombia');
    if (hasColombianLocations) score += 15;

    // Test WhatsApp integration
    const hasWhatsApp = document.querySelector('a[href*="wa.me"]') ||
                        document.querySelector('a[href*="whatsapp"]') ||
                        paymentText.includes('WhatsApp');
    if (hasWhatsApp) score += 25;

    this.addResult(
      test,
      score >= 60,
      `Colombian features score: ${score}/100`,
      score
    );
  }

  private addResult(test: string, passed: boolean, message: string, score: number): void {
    this.results.push({ test, passed, message, score });
  }

  private calculateOverallScore(): number {
    if (this.results.length === 0) return 0;

    const weightedScores = this.results.map((result, index) => {
      // Weight more important tests higher
      const weights = [25, 20, 15, 15, 10, 10, 3, 2]; // Service Worker, Manifest, etc.
      const weight = weights[index] || 1;
      return result.score * weight;
    });

    const totalWeight = this.results.reduce((sum, _, index) => {
      const weights = [25, 20, 15, 15, 10, 10, 3, 2];
      return sum + (weights[index] || 1);
    }, 0);

    return Math.round(weightedScores.reduce((sum, score) => sum + score, 0) / totalWeight);
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];

    this.results.forEach(result => {
      if (!result.passed || result.score < 80) {
        switch (result.test) {
          case 'Service Worker Registration':
            if (!result.passed) {
              recommendations.push('Implement service worker for offline support and caching');
            }
            break;

          case 'Web App Manifest':
            if (result.score < 80) {
              recommendations.push('Complete web app manifest with all required fields and icons');
            }
            break;

          case 'PWA Installability':
            if (result.score < 70) {
              recommendations.push('Ensure app meets PWA installability criteria');
            }
            break;

          case 'Offline Functionality':
            if (result.score < 50) {
              recommendations.push('Implement offline caching for critical resources');
            }
            break;

          case 'Mobile Performance':
            if (result.score < 70) {
              recommendations.push('Optimize bundle size and loading performance for mobile');
            }
            break;

          case 'Mobile UX Optimization':
            if (result.score < 70) {
              recommendations.push('Improve touch targets, font sizes, and mobile navigation');
            }
            break;

          case '3G Network Optimization':
            if (result.score < 70) {
              recommendations.push('Implement image optimization and lazy loading for slow networks');
            }
            break;

          case 'Colombian Market Features':
            if (result.score < 60) {
              recommendations.push('Add Colombian payment methods, currency, and local features');
            }
            break;
        }
      }
    });

    return recommendations;
  }
}

/**
 * Runs PWA validation and logs results
 */
export const runPWAValidation = async (): Promise<PWATestReport> => {
  const validator = new PWAValidator();
  const report = await validator.validatePWA();

  console.group('🔍 PWA Validation Report');
  console.log(`Overall Score: ${report.overallScore}/100`);

  console.group('📊 Test Results');
  report.results.forEach(result => {
    const emoji = result.passed ? '✅' : '❌';
    console.log(`${emoji} ${result.test}: ${result.message} (${result.score}/100)`);
  });
  console.groupEnd();

  if (report.recommendations.length > 0) {
    console.group('💡 Recommendations');
    report.recommendations.forEach(rec => console.log(`• ${rec}`));
    console.groupEnd();
  }

  console.groupEnd();

  return report;
};

export default { PWAValidator, runPWAValidation };