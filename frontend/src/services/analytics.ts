interface EventProperties {
  [key: string]: any;
}

interface ConversionData {
  event_name: string;
  value?: number;
  currency?: string;
  items?: any[];
}

class AnalyticsService {
  private isProduction = import.meta.env.PROD;
  private gaId = import.meta.env.VITE_GA_MEASUREMENT_ID || 'G-PLACEHOLDER';

  constructor() {
    this.initializeAnalytics();
  }

  private initializeAnalytics() {
    if (!this.isGtagAvailable()) {
      console.warn('Google Analytics not loaded yet');
      return;
    }

    // Set default parameters
    window.gtag('config', this.gaId, {
      custom_map: {
        custom_parameter_1: 'user_type',
        custom_parameter_2: 'business_type'
      }
    });
  }

  private isGtagAvailable(): boolean {
    return typeof window !== 'undefined' && 'gtag' in window;
  }

  // Page tracking
  trackPageView(pagePath?: string, pageTitle?: string) {
    if (!this.isGtagAvailable()) return;

    window.gtag('event', 'page_view', {
      page_path: pagePath || window.location.pathname,
      page_title: pageTitle || document.title,
      page_location: window.location.href
    });

    if (!this.isProduction) {
      console.log('📊 Page view tracked:', { pagePath, pageTitle });
    }
  }

  // Event tracking
  trackEvent(eventName: string, properties: EventProperties = {}) {
    if (!this.isGtagAvailable()) return;

    window.gtag('event', eventName, {
      event_category: properties.category || 'engagement',
      event_label: properties.label,
      value: properties.value,
      custom_parameter_1: properties.user_type,
      custom_parameter_2: properties.business_type,
      ...properties
    });

    if (!this.isProduction) {
      console.log(`📊 Event tracked: ${eventName}`, properties);
    }
  }

  // Form tracking
  trackFormStart(formName: string, properties: EventProperties = {}) {
    this.trackEvent('form_start', {
      form_name: formName,
      category: 'form_interaction',
      ...properties
    });
  }

  trackFormSubmit(formName: string, success: boolean = true, properties: EventProperties = {}) {
    this.trackEvent('form_submit', {
      form_name: formName,
      success: success,
      category: 'form_interaction',
      ...properties
    });
  }

  trackFormError(formName: string, errorMessage: string, properties: EventProperties = {}) {
    this.trackEvent('form_error', {
      form_name: formName,
      error_message: errorMessage,
      category: 'form_interaction',
      ...properties
    });
  }

  // Button/CTA tracking
  trackButtonClick(buttonName: string, location: string, properties: EventProperties = {}) {
    this.trackEvent('button_click', {
      button_name: buttonName,
      button_location: location,
      category: 'cta_interaction',
      ...properties
    });
  }

  // E-commerce tracking
  trackPurchase(transactionId: string, value: number, currency: string = 'COP', items: any[] = []) {
    if (!this.isGtagAvailable()) return;

    window.gtag('event', 'purchase', {
      transaction_id: transactionId,
      value: value,
      currency: currency,
      items: items
    });
  }

  trackAddToCart(currency: string = 'COP', value: number, items: any[] = []) {
    if (!this.isGtagAvailable()) return;

    window.gtag('event', 'add_to_cart', {
      currency: currency,
      value: value,
      items: items
    });
  }

  // Lead tracking
  trackLeadGeneration(leadType: string, source: string, value?: number) {
    this.trackEvent('generate_lead', {
      lead_type: leadType,
      lead_source: source,
      value: value,
      currency: 'COP',
      category: 'conversion'
    });
  }

  // User engagement
  trackScroll(scrollDepth: number) {
    // Throttle scroll tracking to 25%, 50%, 75%, 100%
    const milestones = [25, 50, 75, 100];
    const milestone = milestones.find(m => scrollDepth >= m && scrollDepth < m + 5);
    
    if (milestone) {
      this.trackEvent('scroll_depth', {
        scroll_depth: milestone,
        category: 'engagement'
      });
    }
  }

  trackTimeOnPage(timeInSeconds: number) {
    // Track engagement milestones
    const milestones = [30, 60, 120, 300]; // 30s, 1min, 2min, 5min
    const milestone = milestones.find(m => timeInSeconds >= m && timeInSeconds < m + 5);
    
    if (milestone) {
      this.trackEvent('time_on_page', {
        time_milestone: milestone,
        category: 'engagement'
      });
    }
  }

  // Custom conversions
  trackConversion(conversionData: ConversionData) {
    if (!this.isGtagAvailable()) return;

    window.gtag('event', conversionData.event_name, {
      value: conversionData.value,
      currency: conversionData.currency || 'COP',
      items: conversionData.items || []
    });
  }

  // User identification (for logged in users)
  setUserId(userId: string) {
    if (!this.isGtagAvailable()) return;

    window.gtag('config', this.gaId, {
      user_id: userId
    });
  }

  setUserProperties(properties: EventProperties) {
    if (!this.isGtagAvailable()) return;

    window.gtag('set', {
      user_properties: properties
    });
  }

  // Debug methods
  debugEvent(eventName: string, properties: EventProperties = {}) {
    if (this.isProduction) return;

    console.group(`🔍 Analytics Debug: ${eventName}`);
    console.log('Properties:', properties);
    console.log('GA Available:', this.isGtagAvailable());
    console.log('GA ID:', this.gaId);
    console.groupEnd();
  }
}

// Export singleton instance
export const analytics = new AnalyticsService();

// Export individual functions for convenience
export const trackPageView = (pagePath?: string, pageTitle?: string) => 
  analytics.trackPageView(pagePath, pageTitle);

export const trackEvent = (eventName: string, properties?: EventProperties) => 
  analytics.trackEvent(eventName, properties);

export const trackFormStart = (formName: string, properties?: EventProperties) => 
  analytics.trackFormStart(formName, properties);

export const trackFormSubmit = (formName: string, success?: boolean, properties?: EventProperties) => 
  analytics.trackFormSubmit(formName, success, properties);

export const trackButtonClick = (buttonName: string, location: string, properties?: EventProperties) => 
  analytics.trackButtonClick(buttonName, location, properties);

export const trackFormError = (formName: string, errorMessage: string, properties?: EventProperties) => 
  analytics.trackFormError(formName, errorMessage, properties);

export const trackLeadGeneration = (leadType: string, source: string, value?: number) => 
  analytics.trackLeadGeneration(leadType, source, value);

// Default export
export default analytics;

// Type declarations for gtag
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
    dataLayer: any[];
    ENV?: {
      GA_MEASUREMENT_ID?: string;
    };
  }
}