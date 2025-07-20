/**
 * Hook personalizado para logging en componentes React
 */

import { useEffect, useCallback } from 'react';
import logger from '../utils/logger';

interface UseLoggerOptions {
  component?: string;
  autoLogMount?: boolean;
  autoLogUnmount?: boolean;
}

export const useLogger = (options: UseLoggerOptions = {}) => {
  const { component, autoLogMount = false, autoLogUnmount = false } = options;

  // Auto-log mount/unmount si está habilitado
  useEffect(() => {
    if (autoLogMount && component) {
      logger.debug(`Component ${component} mounted`, {}, component, 'mount');
    }

    return () => {
      if (autoLogUnmount && component) {
        logger.debug(`Component ${component} unmounted`, {}, component, 'unmount');
      }
    };
  }, [component, autoLogMount, autoLogUnmount]);

  // Funciones de logging con componente pre-configurado
  const logInfo = useCallback((message: string, data?: any, action?: string) => {
    logger.info(message, data, component, action);
  }, [component]);

  const logError = useCallback((message: string, data?: any, action?: string) => {
    logger.error(message, data, component, action);
  }, [component]);

  const logWarn = useCallback((message: string, data?: any, action?: string) => {
    logger.warn(message, data, component, action);
  }, [component]);

  const logDebug = useCallback((message: string, data?: any, action?: string) => {
    logger.debug(message, data, component, action);
  }, [component]);

  const logUserAction = useCallback((action: string, data?: any) => {
    logger.logUserAction(action, component || 'Unknown', data);
  }, [component]);

  return {
    logInfo,
    logError,
    logWarn,
    logDebug,
    logUserAction,
    // Acceso directo al logger global si es necesario
    logger
  };
};

export default useLogger;