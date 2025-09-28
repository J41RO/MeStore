/**
 * Mobile UX Audit Utility
 * Comprehensive responsive design and mobile UX validation
 * For MeStocker hierarchical sidebar mobile excellence
 */

export interface MobileUxMetrics {
  breakpoints: BreakpointAnalysis;
  touchTargets: TouchTargetAnalysis;
  performance: PerformanceMetrics;
  accessibility: AccessibilityMetrics;
  gestures: GestureSupport;
  coreWebVitals: CoreWebVitals;
}

export interface BreakpointAnalysis {
  mobile: { min: number; max: number; tested: boolean };
  tablet: { min: number; max: number; tested: boolean };
  desktop: { min: number; max: number; tested: boolean };
  currentBreakpoint: string;
  responsive: boolean;
}

export interface TouchTargetAnalysis {
  minimumSize: number;
  compliance: boolean;
  wcagLevel: 'AA' | 'AAA';
  elements: TouchTargetElement[];
}

export interface TouchTargetElement {
  selector: string;
  width: number;
  height: number;
  compliant: boolean;
  recommended: boolean;
}

export interface PerformanceMetrics {
  renderTime: number;
  interactionTime: number;
  memoryUsage: number;
  networkCalls: number;
  bundleSize: number;
}

export interface AccessibilityMetrics {
  ariaCompliance: boolean;
  keyboardNavigation: boolean;
  screenReaderSupport: boolean;
  colorContrast: boolean;
  focusManagement: boolean;
}

export interface GestureSupport {
  swipe: boolean;
  pinch: boolean;
  doubleTap: boolean;
  longPress: boolean;
  multiTouch: boolean;
}

export interface CoreWebVitals {
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  fcp: number; // First Contentful Paint
  ttfb: number; // Time to First Byte
}

export class MobileUxAuditor {
  private metrics: Partial<MobileUxMetrics> = {};

  constructor() {
    this.initializeMetrics();
  }

  private initializeMetrics(): void {
    this.metrics = {
      breakpoints: this.analyzeBreakpoints(),
      touchTargets: this.analyzeTouchTargets(),
      performance: this.measurePerformance(),
      accessibility: this.auditAccessibility(),
      gestures: this.checkGestureSupport(),
      coreWebVitals: this.measureCoreWebVitals()
    };
  }

  /**
   * Analyze responsive breakpoints and current viewport behavior
   */
  private analyzeBreakpoints(): BreakpointAnalysis {
    const viewportWidth = window.innerWidth;

    const breakpoints = {
      mobile: { min: 320, max: 767, tested: false },
      tablet: { min: 768, max: 1023, tested: false },
      desktop: { min: 1024, max: 1920, tested: false }
    };

    // Determine current breakpoint
    let currentBreakpoint = 'desktop';
    if (viewportWidth <= 767) {
      currentBreakpoint = 'mobile';
      breakpoints.mobile.tested = true;
    } else if (viewportWidth <= 1023) {
      currentBreakpoint = 'tablet';
      breakpoints.tablet.tested = true;
    } else {
      breakpoints.desktop.tested = true;
    }

    // Test responsive behavior by checking sidebar behavior
    const sidebar = document.querySelector('[data-testid="menu-category-container"]');
    const responsive = this.testResponsiveBehavior(sidebar);

    return {
      ...breakpoints,
      currentBreakpoint,
      responsive
    };
  }

  private testResponsiveBehavior(element: Element | null): boolean {
    if (!element) return false;

    const computedStyle = getComputedStyle(element);
    const hasResponsiveClasses = element.className.includes('md:') ||
                                element.className.includes('lg:') ||
                                element.className.includes('sm:');

    return hasResponsiveClasses;
  }

  /**
   * Analyze touch target sizes for WCAG compliance
   */
  private analyzeTouchTargets(): TouchTargetAnalysis {
    const touchableSelectors = [
      'button',
      'a[href]',
      '[role="button"]',
      '[role="menuitem"]',
      'input[type="button"]',
      'input[type="submit"]'
    ];

    const elements: TouchTargetElement[] = [];
    let minCompliantSize = 44; // WCAG 2.1 AA minimum
    let totalCompliant = 0;

    touchableSelectors.forEach(selector => {
      const nodeList = document.querySelectorAll(selector);
      nodeList.forEach(element => {
        const rect = element.getBoundingClientRect();
        const compliant = rect.width >= minCompliantSize && rect.height >= minCompliantSize;
        const recommended = rect.width >= 48 && rect.height >= 48; // iOS guideline

        if (compliant) totalCompliant++;

        elements.push({
          selector,
          width: rect.width,
          height: rect.height,
          compliant,
          recommended
        });
      });
    });

    return {
      minimumSize: minCompliantSize,
      compliance: totalCompliant === elements.length,
      wcagLevel: totalCompliant === elements.length ? 'AA' : 'AA',
      elements
    };
  }

  /**
   * Measure performance metrics
   */
  private measurePerformance(): PerformanceMetrics {
    const performance = window.performance;
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    // Measure memory usage (if available)
    const memoryInfo = (performance as any).memory;
    const memoryUsage = memoryInfo ? memoryInfo.usedJSHeapSize / 1024 / 1024 : 0; // MB

    // Count network requests
    const resourceEntries = performance.getEntriesByType('resource');

    return {
      renderTime: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0,
      interactionTime: this.measureFirstInteractionTime(),
      memoryUsage,
      networkCalls: resourceEntries.length,
      bundleSize: this.estimateBundleSize(resourceEntries)
    };
  }

  private measureFirstInteractionTime(): number {
    // Simple interaction time measurement
    const startTime = performance.now();

    // Simulate touch interaction
    const button = document.querySelector('button');
    if (button) {
      const clickEvent = new MouseEvent('click', { bubbles: true });
      button.dispatchEvent(clickEvent);
    }

    return performance.now() - startTime;
  }

  private estimateBundleSize(resources: PerformanceEntry[]): number {
    return resources.reduce((total, resource) => {
      const entry = resource as PerformanceResourceTiming;
      return total + (entry.transferSize || 0);
    }, 0) / 1024; // KB
  }

  /**
   * Audit accessibility compliance
   */
  private auditAccessibility(): AccessibilityMetrics {
    return {
      ariaCompliance: this.checkAriaCompliance(),
      keyboardNavigation: this.testKeyboardNavigation(),
      screenReaderSupport: this.checkScreenReaderSupport(),
      colorContrast: this.auditColorContrast(),
      focusManagement: this.testFocusManagement()
    };
  }

  private checkAriaCompliance(): boolean {
    const requiredAriaElements = document.querySelectorAll('[role]');
    let compliantCount = 0;

    requiredAriaElements.forEach(element => {
      const role = element.getAttribute('role');
      const hasAriaLabel = element.hasAttribute('aria-label') ||
                          element.hasAttribute('aria-labelledby');

      if (role && hasAriaLabel) {
        compliantCount++;
      }
    });

    return compliantCount === requiredAriaElements.length;
  }

  private testKeyboardNavigation(): boolean {
    const focusableElements = document.querySelectorAll(
      'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    // Test if elements can receive focus
    let navigableCount = 0;
    focusableElements.forEach(element => {
      const htmlElement = element as HTMLElement;
      if (htmlElement.tabIndex >= 0) {
        navigableCount++;
      }
    });

    return navigableCount > 0;
  }

  private checkScreenReaderSupport(): boolean {
    const liveRegions = document.querySelectorAll('[aria-live]');
    const landmarks = document.querySelectorAll('[role="navigation"], [role="main"], [role="banner"]');

    return liveRegions.length > 0 && landmarks.length > 0;
  }

  private auditColorContrast(): boolean {
    // Simplified contrast check - would need more sophisticated analysis in production
    const elements = document.querySelectorAll('button, a, [role="button"]');
    let compliantCount = 0;

    elements.forEach(element => {
      const computedStyle = getComputedStyle(element);
      const backgroundColor = computedStyle.backgroundColor;
      const color = computedStyle.color;

      // Basic check for transparent or similar colors
      if (backgroundColor !== 'rgba(0, 0, 0, 0)' && color !== backgroundColor) {
        compliantCount++;
      }
    });

    return compliantCount === elements.length;
  }

  private testFocusManagement(): boolean {
    // Test if focus is properly managed
    const focusableElements = document.querySelectorAll('[tabindex]');
    let properlyManaged = 0;

    focusableElements.forEach(element => {
      const tabIndex = parseInt(element.getAttribute('tabindex') || '0');
      if (tabIndex >= -1) { // -1 is programmatically focusable, 0+ is tab order
        properlyManaged++;
      }
    });

    return properlyManaged === focusableElements.length;
  }

  /**
   * Check gesture support capabilities
   */
  private checkGestureSupport(): GestureSupport {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    return {
      swipe: isTouchDevice && 'ontouchstart' in window,
      pinch: isTouchDevice && navigator.maxTouchPoints >= 2,
      doubleTap: isTouchDevice,
      longPress: isTouchDevice,
      multiTouch: navigator.maxTouchPoints >= 2
    };
  }

  /**
   * Measure Core Web Vitals
   */
  private measureCoreWebVitals(): CoreWebVitals {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    return {
      lcp: this.measureLCP(),
      fid: this.measureFID(),
      cls: this.measureCLS(),
      fcp: navigation ? navigation.responseEnd - navigation.fetchStart : 0,
      ttfb: navigation ? navigation.responseStart - navigation.fetchStart : 0
    };
  }

  private measureLCP(): number {
    // Simplified LCP measurement
    const paintEntries = performance.getEntriesByType('paint');
    const lcpEntry = paintEntries.find(entry => entry.name === 'largest-contentful-paint');
    return lcpEntry ? lcpEntry.startTime : 0;
  }

  private measureFID(): number {
    // FID would be measured over time with user interactions
    // This is a simplified version
    return 0; // Would need real user interaction measurement
  }

  private measureCLS(): number {
    // CLS measurement would require layout shift observer
    // Simplified version returns 0
    return 0;
  }

  /**
   * Generate comprehensive audit report
   */
  public generateReport(): string {
    const metrics = this.metrics as MobileUxMetrics;

    let report = `
🚀 MOBILE UX AUDIT REPORT - MeStocker Hierarchical Sidebar
================================================================

📱 RESPONSIVE BREAKPOINTS:
- Current Breakpoint: ${metrics.breakpoints.currentBreakpoint}
- Mobile (320-767px): ${metrics.breakpoints.mobile.tested ? '✅ Tested' : '⏳ Not tested'}
- Tablet (768-1023px): ${metrics.breakpoints.tablet.tested ? '✅ Tested' : '⏳ Not tested'}
- Desktop (1024px+): ${metrics.breakpoints.desktop.tested ? '✅ Tested' : '⏳ Not tested'}
- Responsive Design: ${metrics.breakpoints.responsive ? '✅ Compliant' : '❌ Needs improvement'}

👆 TOUCH TARGET ANALYSIS:
- WCAG 2.1 ${metrics.touchTargets.wcagLevel} Compliance: ${metrics.touchTargets.compliance ? '✅ Compliant' : '❌ Non-compliant'}
- Minimum Size Required: ${metrics.touchTargets.minimumSize}px
- Total Elements Checked: ${metrics.touchTargets.elements.length}
- Compliant Elements: ${metrics.touchTargets.elements.filter(e => e.compliant).length}

⚡ PERFORMANCE METRICS:
- Render Time: ${metrics.performance.renderTime.toFixed(2)}ms
- First Interaction: ${metrics.performance.interactionTime.toFixed(2)}ms
- Memory Usage: ${metrics.performance.memoryUsage.toFixed(2)}MB
- Network Requests: ${metrics.performance.networkCalls}
- Bundle Size: ${metrics.performance.bundleSize.toFixed(2)}KB

♿ ACCESSIBILITY AUDIT:
- ARIA Compliance: ${metrics.accessibility.ariaCompliance ? '✅' : '❌'}
- Keyboard Navigation: ${metrics.accessibility.keyboardNavigation ? '✅' : '❌'}
- Screen Reader Support: ${metrics.accessibility.screenReaderSupport ? '✅' : '❌'}
- Color Contrast: ${metrics.accessibility.colorContrast ? '✅' : '❌'}
- Focus Management: ${metrics.accessibility.focusManagement ? '✅' : '❌'}

🤲 GESTURE SUPPORT:
- Swipe Gestures: ${metrics.gestures.swipe ? '✅' : '❌'}
- Pinch-to-Zoom: ${metrics.gestures.pinch ? '✅' : '❌'}
- Double Tap: ${metrics.gestures.doubleTap ? '✅' : '❌'}
- Long Press: ${metrics.gestures.longPress ? '✅' : '❌'}
- Multi-touch: ${metrics.gestures.multiTouch ? '✅' : '❌'}

📊 CORE WEB VITALS:
- LCP (Largest Contentful Paint): ${metrics.coreWebVitals.lcp.toFixed(2)}ms
- FID (First Input Delay): ${metrics.coreWebVitals.fid.toFixed(2)}ms
- CLS (Cumulative Layout Shift): ${metrics.coreWebVitals.cls.toFixed(3)}
- FCP (First Contentful Paint): ${metrics.coreWebVitals.fcp.toFixed(2)}ms
- TTFB (Time to First Byte): ${metrics.coreWebVitals.ttfb.toFixed(2)}ms

🎯 MOBILE UX RECOMMENDATIONS:
${this.generateRecommendations(metrics)}

🏆 OVERALL SCORE: ${this.calculateOverallScore(metrics)}/100
`;

    return report;
  }

  private generateRecommendations(metrics: MobileUxMetrics): string {
    const recommendations: string[] = [];

    if (!metrics.breakpoints.responsive) {
      recommendations.push('- Implement proper responsive CSS classes (sm:, md:, lg:)');
    }

    if (!metrics.touchTargets.compliance) {
      recommendations.push('- Increase touch target sizes to minimum 44px for WCAG 2.1 AA compliance');
    }

    if (metrics.performance.renderTime > 100) {
      recommendations.push('- Optimize rendering performance (target: <100ms)');
    }

    if (metrics.performance.memoryUsage > 50) {
      recommendations.push('- Reduce memory usage for better mobile performance');
    }

    if (!metrics.accessibility.ariaCompliance) {
      recommendations.push('- Improve ARIA labels and roles for screen reader support');
    }

    if (!metrics.gestures.swipe) {
      recommendations.push('- Implement swipe gestures for mobile navigation');
    }

    if (metrics.coreWebVitals.lcp > 2500) {
      recommendations.push('- Improve Largest Contentful Paint (target: <2.5s)');
    }

    if (recommendations.length === 0) {
      return '✅ All mobile UX criteria met! Ready for production.';
    }

    return recommendations.join('\n');
  }

  private calculateOverallScore(metrics: MobileUxMetrics): number {
    let score = 0;
    let maxScore = 0;

    // Responsive design (20 points)
    maxScore += 20;
    if (metrics.breakpoints.responsive) score += 20;

    // Touch targets (20 points)
    maxScore += 20;
    if (metrics.touchTargets.compliance) score += 20;

    // Performance (25 points)
    maxScore += 25;
    if (metrics.performance.renderTime < 100) score += 10;
    if (metrics.performance.memoryUsage < 50) score += 10;
    if (metrics.performance.interactionTime < 50) score += 5;

    // Accessibility (25 points)
    maxScore += 25;
    const accessibilityChecks = Object.values(metrics.accessibility);
    const passedChecks = accessibilityChecks.filter(Boolean).length;
    score += (passedChecks / accessibilityChecks.length) * 25;

    // Gestures (10 points)
    maxScore += 10;
    const gestureChecks = Object.values(metrics.gestures);
    const enabledGestures = gestureChecks.filter(Boolean).length;
    score += (enabledGestures / gestureChecks.length) * 10;

    return Math.round((score / maxScore) * 100);
  }

  /**
   * Run comprehensive mobile UX audit
   */
  public static async runAudit(): Promise<string> {
    const auditor = new MobileUxAuditor();

    // Wait for page to be fully loaded
    if (document.readyState !== 'complete') {
      await new Promise(resolve => {
        window.addEventListener('load', resolve);
      });
    }

    return auditor.generateReport();
  }
}

// Export utility functions for component testing
export const testMobileBreakpoints = (element: HTMLElement): boolean => {
  const auditor = new MobileUxAuditor();
  return auditor['testResponsiveBehavior'](element);
};

export const validateTouchTargets = (container: HTMLElement): TouchTargetElement[] => {
  const auditor = new MobileUxAuditor();
  const analysis = auditor['analyzeTouchTargets']();
  return analysis.elements;
};