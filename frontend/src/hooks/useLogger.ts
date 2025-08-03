import { useEffect } from 'react';

export interface Logger {
  logInfo: (message: string, data?: any) => void;
  logError: (message: string, data?: any) => void;
  logWarn: (message: string, data?: any) => void;
  logDebug: (message: string, data?: any) => void;
  logUserAction: (action: string, component: string, data?: any) => void;
}

export const useLogger = (component: string): Logger => {
  useEffect(() => {
    console.log(`[${component}] Component mounted`);
    return () => {
      console.log(`[${component}] Component unmounted`);
    };
  }, [component]);

  return {
    logInfo: (message: string, data?: any) => {
      console.log(`[${component}] INFO: ${message}`, data || '');
    },
    logError: (message: string, data?: any) => {
      console.error(`[${component}] ERROR: ${message}`, data || '');
    },
    logWarn: (message: string, data?: any) => {
      console.warn(`[${component}] WARN: ${message}`, data || '');
    },
    logDebug: (message: string, data?: any) => {
      console.debug(`[${component}] DEBUG: ${message}`, data || '');
    },
    logUserAction: (action: string, component: string, data?: any) => {
      console.log(`[${component}] USER ACTION: ${action}`, data || '');
    }
  };
};
