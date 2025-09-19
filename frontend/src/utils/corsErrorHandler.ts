import { AxiosError } from 'axios';

export interface CorsErrorInfo {
  isCorsError: boolean;
  isNetworkError: boolean;
  isConfigurationError: boolean;
  userMessage: string;
  devMessage: string;
  suggestedActions: string[];
}

/**
 * Analiza errores de red para identificar problemas específicos de CORS
 */
export const analyzeCorsError = (error: AxiosError): CorsErrorInfo => {
  const errorInfo: CorsErrorInfo = {
    isCorsError: false,
    isNetworkError: false,
    isConfigurationError: false,
    userMessage: 'Error de conexión desconocido',
    devMessage: error.message || 'Unknown error',
    suggestedActions: [],
  };

  // Error sin response - típicamente errores CORS o de red
  if (!error.response && error.message) {
    const message = error.message.toLowerCase();

    // Detectar errores CORS específicos
    if (
      message.includes('cors') ||
      message.includes('access to xmlhttprequest') ||
      message.includes('access-control-allow-origin') ||
      message.includes('cross-origin request')
    ) {
      errorInfo.isCorsError = true;
      errorInfo.userMessage = 'Error de configuración CORS. El servidor no permite conexiones desde este origen.';
      errorInfo.devMessage = `CORS Error: ${error.message}`;
      errorInfo.suggestedActions = [
        'Verificar que el servidor backend incluya el origen del frontend en CORS_ORIGINS',
        'Confirmar que el servidor backend esté ejecutándose',
        'Verificar la configuración CORS_ALLOW_CREDENTIALS en el backend',
        'Revisar los headers permitidos en CORS_ALLOW_HEADERS',
      ];
    }
    // Detectar errores de red generales
    else if (
      message.includes('network error') ||
      error.code === 'ECONNABORTED' ||
      error.code === 'ENOTFOUND' ||
      error.code === 'ECONNRESET' ||
      error.code === 'ECONNREFUSED'
    ) {
      errorInfo.isNetworkError = true;
      errorInfo.userMessage = 'Error de conexión. No se puede conectar al servidor.';
      errorInfo.devMessage = `Network Error [${error.code}]: ${error.message}`;
      errorInfo.suggestedActions = [
        'Verificar que el servidor backend esté ejecutándose en el puerto correcto',
        'Confirmar la URL base de la API en la configuración del frontend',
        'Verificar la conectividad de red',
        'Revisar si hay firewalls o proxies bloqueando la conexión',
      ];
    }
    // Error de configuración (timeout, etc.)
    else {
      errorInfo.isConfigurationError = true;
      errorInfo.userMessage = 'Error de configuración de conexión.';
      errorInfo.devMessage = `Configuration Error: ${error.message}`;
      errorInfo.suggestedActions = [
        'Revisar la configuración del timeout en axios',
        'Verificar la URL base de la API',
        'Confirmar la configuración del proxy en Vite',
      ];
    }
  }
  // Error con response - problemas del servidor
  else if (error.response) {
    const status = error.response.status;

    if (status === 0) {
      errorInfo.isCorsError = true;
      errorInfo.userMessage = 'Error CORS: El servidor rechazó la conexión.';
      errorInfo.devMessage = 'HTTP Status 0 - Typically indicates CORS rejection';
      errorInfo.suggestedActions = [
        'Verificar configuración CORS en el backend',
        'Confirmar que el origen esté en la lista permitida',
      ];
    } else {
      errorInfo.userMessage = `Error del servidor (${status})`;
      errorInfo.devMessage = `HTTP ${status}: ${error.response.statusText}`;
    }
  }

  return errorInfo;
};

/**
 * Registra errores CORS con información detallada para desarrollo
 */
export const logCorsError = (errorInfo: CorsErrorInfo, context?: string) => {
  const isDevelopment = import.meta.env.MODE === 'development';

  if (isDevelopment) {
    console.group(`🚨 CORS/Network Error ${context ? `(${context})` : ''}`);
    console.error('Error Type:', {
      CORS: errorInfo.isCorsError,
      Network: errorInfo.isNetworkError,
      Configuration: errorInfo.isConfigurationError,
    });
    console.error('User Message:', errorInfo.userMessage);
    console.error('Dev Message:', errorInfo.devMessage);

    if (errorInfo.suggestedActions.length > 0) {
      console.warn('Suggested Actions:');
      errorInfo.suggestedActions.forEach((action, index) => {
        console.warn(`  ${index + 1}. ${action}`);
      });
    }

    console.groupEnd();
  } else {
    // En producción, solo log básico
    console.error('API Error:', errorInfo.userMessage);
  }
};

/**
 * Maneja errores CORS mostrando información útil al usuario y desarrollador
 */
export const handleCorsError = (error: AxiosError, context?: string): CorsErrorInfo => {
  const errorInfo = analyzeCorsError(error);
  logCorsError(errorInfo, context);
  return errorInfo;
};