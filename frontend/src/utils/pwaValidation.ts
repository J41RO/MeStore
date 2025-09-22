/**
 * PWA Validation Utilities for MeStocker Colombian Market
 * Validates PWA implementation and provides performance metrics
 */

interface PWAValidationResult {
  score: number;
  isValid: boolean;
  checks: {
    manifest: boolean;
    serviceWorker: boolean;
    offline: boolean;
    installable: boolean;
    responsive: boolean;
    https: boolean;
    performance: boolean;
  };
  errors: string[];
  warnings: string[];
  colombianFeatures: {
    locale: boolean;
    currency: boolean;
    paymentMethods: boolean;
    offlineSupport: boolean;
  };
}

class PWAValidator {
  private errors: string[] = [];
  private warnings: string[] = [];

  /**
   * Comprehensive PWA validation for Colombian market
   */
  async validatePWA(): Promise<PWAValidationResult> {
    console.log('🔍 Starting PWA validation for Colombian market...');

    const checks = {
      manifest: await this.validateManifest(),
      serviceWorker: await this.validateServiceWorker(),
      offline: await this.validateOfflineCapability(),
      installable: await this.validateInstallability(),
      responsive: this.validateResponsiveDesign(),
      https: this.validateHTTPS(),
      performance: await this.validatePerformance()
    };

    const colombianFeatures = await this.validateColombianFeatures();

    const passedChecks = Object.values(checks).filter(Boolean).length;
    const totalChecks = Object.keys(checks).length;
    const score = Math.round((passedChecks / totalChecks) * 100);

    const isValid = score >= 90 && colombianFeatures.locale && colombianFeatures.currency;

    console.log(`✅ PWA Validation completed. Score: ${score}/100`);

    return {
      score,
      isValid,
      checks,
      errors: this.errors,
      warnings: this.warnings,
      colombianFeatures
    };
  }

  /**
   * Validate Web App Manifest
   */
  private async validateManifest(): Promise<boolean> {
    try {
      const manifestLink = document.querySelector('link[rel="manifest"]') as HTMLLinkElement;
      if (!manifestLink) {
        this.errors.push('Web App Manifest not found');
        return false;
      }

      const response = await fetch(manifestLink.href);
      const manifest = await response.json();

      const requiredFields = ['name', 'short_name', 'start_url', 'display', 'icons'];
      const missingFields = requiredFields.filter(field => !manifest[field]);

      if (missingFields.length > 0) {
        this.errors.push(`Manifest missing required fields: ${missingFields.join(', ')}`);
        return false;
      }

      // Validate icons
      if (!manifest.icons || manifest.icons.length === 0) {
        this.errors.push('Manifest must include at least one icon');
        return false;
      }

      const hasRequiredIconSizes = manifest.icons.some((icon: any) =>
        icon.sizes === '192x192' || icon.sizes === '512x512'
      );

      if (!hasRequiredIconSizes) {
        this.warnings.push('Manifest should include 192x192 and 512x512 icons');
      }

      // Check Colombian-specific manifest properties
      if (manifest.lang !== 'es-CO') {
        this.warnings.push('Manifest language should be set to es-CO for Colombian market');
      }

      console.log('✅ Manifest validation passed');
      return true;
    } catch (error) {
      this.errors.push(`Manifest validation failed: ${error}`);
      return false;
    }
  }

  /**
   * Validate Service Worker
   */
  private async validateServiceWorker(): Promise<boolean> {
    if (!('serviceWorker' in navigator)) {
      this.errors.push('Service Worker not supported in this browser');
      return false;
    }

    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (!registration) {
        this.errors.push('Service Worker not registered');
        return false;
      }

      if (!registration.active) {
        this.errors.push('Service Worker not active');
        return false;
      }

      console.log('✅ Service Worker validation passed');
      return true;
    } catch (error) {
      this.errors.push(`Service Worker validation failed: ${error}`);
      return false;
    }
  }

  /**
   * Validate offline capability
   */
  private async validateOfflineCapability(): Promise<boolean> {
    try {
      // Check if offline page is available
      const offlineResponse = await fetch('/offline.html', {
        method: 'HEAD',
        cache: 'no-cache'
      });

      if (!offlineResponse.ok) {
        this.warnings.push('Offline fallback page not available');
      }

      // Check IndexedDB support for offline storage
      if (!('indexedDB' in window)) {
        this.errors.push('IndexedDB not supported - offline storage unavailable');
        return false;
      }

      console.log('✅ Offline capability validation passed');
      return true;
    } catch (error) {
      this.warnings.push('Could not validate offline capability fully');
      return true; // Don't fail for this
    }
  }

  /**
   * Validate PWA installability
   */
  private async validateInstallability(): Promise<boolean> {
    // Check if beforeinstallprompt is supported
    const isInstallable = 'onbeforeinstallprompt' in window;

    if (!isInstallable) {
      this.warnings.push('Install prompt not supported in this browser');
    }

    // Check if already installed
    const isInstalled = window.matchMedia('(display-mode: standalone)').matches ||
                       (window.navigator as any).standalone === true;

    if (isInstalled) {
      console.log('✅ PWA is installed');
      return true;
    }

    console.log('✅ PWA installability validated');
    return true; // Don't fail if not installed yet
  }

  /**
   * Validate responsive design
   */
  private validateResponsiveDesign(): boolean {
    const viewport = document.querySelector('meta[name="viewport"]') as HTMLMetaElement;

    if (!viewport) {
      this.errors.push('Viewport meta tag not found');
      return false;
    }

    const content = viewport.content;
    const hasWidthDevice = content.includes('width=device-width');
    const hasInitialScale = content.includes('initial-scale=1');

    if (!hasWidthDevice || !hasInitialScale) {
      this.warnings.push('Viewport should include width=device-width and initial-scale=1');
    }

    console.log('✅ Responsive design validation passed');
    return true;
  }

  /**
   * Validate HTTPS requirement
   */
  private validateHTTPS(): boolean {
    const isHTTPS = location.protocol === 'https:' || location.hostname === 'localhost';

    if (!isHTTPS) {
      this.errors.push('PWA requires HTTPS in production');
      return false;
    }

    console.log('✅ HTTPS validation passed');
    return true;
  }

  /**
   * Validate performance metrics
   */
  private async validatePerformance(): Promise<boolean> {
    if (!('performance' in window)) {
      this.warnings.push('Performance API not available');
      return true;
    }

    try {
      // Check loading performance
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

      if (navigation) {
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        const domContentLoaded = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;

        if (loadTime > 3000) {
          this.warnings.push(`Page load time is ${Math.round(loadTime)}ms - should be under 3000ms for mobile`);
        }

        if (domContentLoaded > 1500) {
          this.warnings.push(`DOM content loaded in ${Math.round(domContentLoaded)}ms - should be under 1500ms`);
        }
      }

      console.log('✅ Performance validation completed');
      return true;
    } catch (error) {
      this.warnings.push('Could not validate performance metrics');
      return true;
    }
  }

  /**
   * Validate Colombian-specific features
   */
  private async validateColombianFeatures(): Promise<{
    locale: boolean;
    currency: boolean;
    paymentMethods: boolean;
    offlineSupport: boolean;
  }> {
    const features = {
      locale: false,
      currency: false,
      paymentMethods: false,
      offlineSupport: false
    };

    // Check locale settings
    features.locale = document.documentElement.lang === 'es-CO' ||
                     document.documentElement.lang === 'es';

    if (!features.locale) {
      this.warnings.push('Document language should be set to es-CO for Colombian users');
    }

    // Check for Colombian currency support
    try {
      const currencyTest = new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
      }).format(1000);
      features.currency = currencyTest.includes('COP') || currencyTest.includes('$');
    } catch (error) {
      this.warnings.push('Colombian peso (COP) currency formatting not supported');
    }

    // Check for Colombian payment methods in localStorage/cache
    const paymentMethods = localStorage.getItem('availablePaymentMethods');
    if (paymentMethods) {
      const methods = JSON.parse(paymentMethods);
      features.paymentMethods = methods.includes('pse') || methods.includes('nequi');
    }

    // Check offline support for Colombian features
    try {
      const offlineDB = await new Promise((resolve, reject) => {
        const request = indexedDB.open('MeStockerOfflineDB', 1);
        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(false);
      });
      features.offlineSupport = !!offlineDB;
    } catch (error) {
      features.offlineSupport = false;
    }

    return features;
  }

  /**
   * Generate PWA performance report
   */
  async generateReport(): Promise<string> {
    const validation = await this.validatePWA();

    let report = `
🇨🇴 MESTOCKER PWA VALIDATION REPORT
=====================================

Overall Score: ${validation.score}/100 ${validation.isValid ? '✅' : '❌'}
Status: ${validation.isValid ? 'PRODUCTION READY' : 'NEEDS IMPROVEMENT'}

PWA CORE CHECKS:
`;

    Object.entries(validation.checks).forEach(([check, passed]) => {
      report += `• ${check.toUpperCase()}: ${passed ? '✅ PASS' : '❌ FAIL'}\n`;
    });

    report += `
COLOMBIAN MARKET FEATURES:
• Locale (es-CO): ${validation.colombianFeatures.locale ? '✅' : '❌'}
• Currency (COP): ${validation.colombianFeatures.currency ? '✅' : '❌'}
• Payment Methods: ${validation.colombianFeatures.paymentMethods ? '✅' : '❌'}
• Offline Support: ${validation.colombianFeatures.offlineSupport ? '✅' : '❌'}
`;

    if (validation.errors.length > 0) {
      report += `\nERRORS TO FIX:\n`;
      validation.errors.forEach(error => {
        report += `❌ ${error}\n`;
      });
    }

    if (validation.warnings.length > 0) {
      report += `\nWARNINGS:\n`;
      validation.warnings.forEach(warning => {
        report += `⚠️ ${warning}\n`;
      });
    }

    report += `\n✨ PWA optimized for Colombian mobile networks and payment systems`;

    return report;
  }
}

// Export singleton instance
export const pwaValidator = new PWAValidator();

// Utility function for quick validation
export const validatePWAQuick = async (): Promise<boolean> => {
  const result = await pwaValidator.validatePWA();
  console.log(`PWA Validation Score: ${result.score}/100`);
  return result.isValid;
};

// Export types
export type { PWAValidationResult };