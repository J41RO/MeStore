/**
 * SecurityProvider Component
 * Frontend Security AI Implementation
 *
 * Proveedor de contexto de seguridad que inicializa y maneja
 * todas las medidas de seguridad de la aplicación
 */

import React, { createContext, useContext, useEffect, useCallback } from 'react';
import { initSecurity, loginRateLimiter } from '../../utils/security';
import { errorHandler, setupGlobalErrorHandler } from '../../utils/errorHandler';
import { useAuthStore } from '../../stores/authStore';

interface SecurityContextType {
  reportSecurityIncident: (type: 'xss' | 'csrf' | 'suspicious', details?: any) => void;
  checkRateLimit: (identifier: string) => boolean;
  getRemainingTime: (identifier: string) => number;
  isSecurityInitialized: boolean;
}

const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

export const useSecurityContext = (): SecurityContextType => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurityContext must be used within SecurityProvider');
  }
  return context;
};

interface SecurityProviderProps {
  children: React.ReactNode;
}

export const SecurityProvider: React.FC<SecurityProviderProps> = ({ children }) => {
  const [isSecurityInitialized, setIsSecurityInitialized] = React.useState(false);
  const { logout } = useAuthStore();

  // Initialize security measures
  useEffect(() => {
    const initializeSecuritySystems = async () => {
      try {
        // Initialize security utilities
        initSecurity();

        // Setup global error handlers
        setupGlobalErrorHandler();

        // Initialize CSRF protection
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (!csrfToken && import.meta.env.MODE === 'production') {
          console.warn('CSRF token not found. Consider implementing CSRF protection.');
        }

        // Monitor for suspicious activity
        setupSecurityMonitoring();

        setIsSecurityInitialized(true);
        console.info('🛡️ Security systems initialized successfully');

      } catch (error) {
        console.error('Failed to initialize security systems:', error);
        errorHandler.logError(
          errorHandler.createError(
            'SECURITY_INIT_FAILED',
            'Failed to initialize security systems',
            'security',
            { error }
          )
        );
      }
    };

    initializeSecuritySystems();
  }, []);

  // Setup security monitoring
  const setupSecurityMonitoring = useCallback(() => {
    // Monitor for rapid form submissions (potential bot activity)
    let lastSubmissionTime = 0;
    const minSubmissionInterval = 1000; // 1 second

    document.addEventListener('submit', (event) => {
      const now = Date.now();
      if (now - lastSubmissionTime < minSubmissionInterval) {
        console.warn('⚠️ Rapid form submission detected');
        reportSecurityIncident('suspicious', {
          type: 'rapid_submission',
          interval: now - lastSubmissionTime,
          form: event.target
        });
      }
      lastSubmissionTime = now;
    });

    // Monitor for suspicious script injections
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element;
            if (element.tagName === 'SCRIPT') {
              const scriptContent = element.textContent || '';
              if (scriptContent.includes('eval') || scriptContent.includes('document.write')) {
                console.warn('⚠️ Suspicious script injection detected');
                reportSecurityIncident('xss', {
                  type: 'script_injection',
                  content: scriptContent.substring(0, 100)
                });
              }
            }
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Monitor localStorage access patterns
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(key: string, value: string) {
      // Monitor for suspicious storage patterns
      if (key.includes('script') || value.includes('<script')) {
        console.warn('⚠️ Suspicious localStorage write detected');
        reportSecurityIncident('xss', {
          type: 'storage_injection',
          key,
          value: value.substring(0, 100)
        });
      }
      return originalSetItem.call(this, key, value);
    };

  }, []);

  // Report security incidents
  const reportSecurityIncident = useCallback((
    type: 'xss' | 'csrf' | 'suspicious',
    details?: any
  ) => {
    const error = errorHandler.handleSecurityError(type, details);

    // Auto-logout for severe security incidents
    if (type === 'xss' || type === 'csrf') {
      console.error('🚨 Critical security incident detected. Logging out user for safety.');
      setTimeout(() => {
        logout();
        window.location.href = '/login';
      }, 2000);
    }

    // Send to monitoring service in production
    if (import.meta.env.MODE === 'production') {
      // Implement actual security incident reporting
      console.info('Would report security incident:', error);
    }
  }, [logout]);

  // Check rate limiting
  const checkRateLimit = useCallback((identifier: string): boolean => {
    return loginRateLimiter.canAttempt(identifier);
  }, []);

  // Get remaining time for rate limit
  const getRemainingTime = useCallback((identifier: string): number => {
    return loginRateLimiter.getRemainingTime(identifier);
  }, []);

  // Setup authentication security monitoring
  useEffect(() => {
    // Monitor for token tampering
    const checkTokenIntegrity = () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Basic token format validation
          const parts = token.split('.');
          if (parts.length !== 3) {
            reportSecurityIncident('suspicious', {
              type: 'token_tampering',
              token: token.substring(0, 20) + '...'
            });
            logout();
          }
        } catch (error) {
          reportSecurityIncident('suspicious', {
            type: 'token_validation_error',
            error: error.message
          });
        }
      }
    };

    // Check token integrity periodically
    const tokenCheckInterval = setInterval(checkTokenIntegrity, 60000); // Every minute

    return () => {
      clearInterval(tokenCheckInterval);
    };
  }, [logout, reportSecurityIncident]);

  const contextValue: SecurityContextType = {
    reportSecurityIncident,
    checkRateLimit,
    getRemainingTime,
    isSecurityInitialized,
  };

  return (
    <SecurityContext.Provider value={contextValue}>
      {children}
    </SecurityContext.Provider>
  );
};

export default SecurityProvider;