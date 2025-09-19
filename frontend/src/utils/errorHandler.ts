/**
 * Centralized Error Handler
 * Frontend Security AI Implementation
 *
 * Sistema centralizado de manejo de errores con logging y notificaciones
 */

export interface AppError {
  code: string;
  message: string;
  type: 'validation' | 'network' | 'auth' | 'api' | 'security' | 'unknown';
  details?: any;
  timestamp: string;
  userAgent?: string;
  url?: string;
}

// Error codes mapping
export const ERROR_CODES = {
  // Authentication errors
  AUTH_INVALID_CREDENTIALS: 'AUTH_001',
  AUTH_TOKEN_EXPIRED: 'AUTH_002',
  AUTH_TOKEN_INVALID: 'AUTH_003',
  AUTH_INSUFFICIENT_PERMISSIONS: 'AUTH_004',
  AUTH_RATE_LIMITED: 'AUTH_005',
  AUTH_ACCOUNT_DISABLED: 'AUTH_006',

  // Network errors
  NETWORK_CONNECTION_ERROR: 'NET_001',
  NETWORK_TIMEOUT: 'NET_002',
  NETWORK_SERVER_ERROR: 'NET_003',

  // Validation errors
  VALIDATION_EMAIL_INVALID: 'VAL_001',
  VALIDATION_PASSWORD_WEAK: 'VAL_002',
  VALIDATION_REQUIRED_FIELD: 'VAL_003',

  // API errors
  API_BAD_REQUEST: 'API_001',
  API_NOT_FOUND: 'API_002',
  API_INTERNAL_ERROR: 'API_003',

  // Security errors
  SECURITY_XSS_DETECTED: 'SEC_001',
  SECURITY_CSRF_INVALID: 'SEC_002',
  SECURITY_SUSPICIOUS_ACTIVITY: 'SEC_003',
} as const;

// User-friendly error messages
const ERROR_MESSAGES: Record<string, string> = {
  [ERROR_CODES.AUTH_INVALID_CREDENTIALS]: 'Email o contraseña incorrectos',
  [ERROR_CODES.AUTH_TOKEN_EXPIRED]: 'Su sesión ha expirado. Por favor, inicie sesión nuevamente',
  [ERROR_CODES.AUTH_TOKEN_INVALID]: 'Token de sesión inválido',
  [ERROR_CODES.AUTH_INSUFFICIENT_PERMISSIONS]: 'No tiene permisos para realizar esta acción',
  [ERROR_CODES.AUTH_RATE_LIMITED]: 'Demasiados intentos. Intente nuevamente más tarde',
  [ERROR_CODES.AUTH_ACCOUNT_DISABLED]: 'Su cuenta ha sido deshabilitada',

  [ERROR_CODES.NETWORK_CONNECTION_ERROR]: 'Error de conexión. Verifique su conexión a internet',
  [ERROR_CODES.NETWORK_TIMEOUT]: 'Tiempo de espera agotado. Intente nuevamente',
  [ERROR_CODES.NETWORK_SERVER_ERROR]: 'Error del servidor. Intente más tarde',

  [ERROR_CODES.VALIDATION_EMAIL_INVALID]: 'El formato del email no es válido',
  [ERROR_CODES.VALIDATION_PASSWORD_WEAK]: 'La contraseña no cumple con los requisitos de seguridad',
  [ERROR_CODES.VALIDATION_REQUIRED_FIELD]: 'Este campo es requerido',

  [ERROR_CODES.API_BAD_REQUEST]: 'Solicitud inválida',
  [ERROR_CODES.API_NOT_FOUND]: 'Recurso no encontrado',
  [ERROR_CODES.API_INTERNAL_ERROR]: 'Error interno del servidor',

  [ERROR_CODES.SECURITY_XSS_DETECTED]: 'Contenido potencialmente peligroso detectado',
  [ERROR_CODES.SECURITY_CSRF_INVALID]: 'Token de seguridad inválido',
  [ERROR_CODES.SECURITY_SUSPICIOUS_ACTIVITY]: 'Actividad sospechosa detectada',
};

class ErrorHandler {
  private errors: AppError[] = [];
  private maxErrors: number = 100;

  // Create standardized error
  createError(
    code: string,
    message: string,
    type: AppError['type'],
    details?: any
  ): AppError {
    return {
      code,
      message,
      type,
      details,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };
  }

  // Handle API errors
  handleApiError(error: any): AppError {
    console.error('API Error:', error);

    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          return this.createError(
            ERROR_CODES.API_BAD_REQUEST,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.API_BAD_REQUEST],
            'api',
            { status, data }
          );

        case 401:
          return this.createError(
            ERROR_CODES.AUTH_TOKEN_INVALID,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.AUTH_TOKEN_INVALID],
            'auth',
            { status, data }
          );

        case 403:
          return this.createError(
            ERROR_CODES.AUTH_INSUFFICIENT_PERMISSIONS,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.AUTH_INSUFFICIENT_PERMISSIONS],
            'auth',
            { status, data }
          );

        case 404:
          return this.createError(
            ERROR_CODES.API_NOT_FOUND,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.API_NOT_FOUND],
            'api',
            { status, data }
          );

        case 429:
          return this.createError(
            ERROR_CODES.AUTH_RATE_LIMITED,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.AUTH_RATE_LIMITED],
            'auth',
            { status, data }
          );

        case 500:
        default:
          return this.createError(
            ERROR_CODES.API_INTERNAL_ERROR,
            data?.detail || ERROR_MESSAGES[ERROR_CODES.API_INTERNAL_ERROR],
            'api',
            { status, data }
          );
      }
    } else if (error.request) {
      return this.createError(
        ERROR_CODES.NETWORK_CONNECTION_ERROR,
        ERROR_MESSAGES[ERROR_CODES.NETWORK_CONNECTION_ERROR],
        'network',
        { request: error.request }
      );
    } else {
      return this.createError(
        'UNKNOWN_ERROR',
        error.message || 'Error desconocido',
        'unknown',
        { originalError: error }
      );
    }
  }

  // Handle validation errors
  handleValidationError(field: string, value: any, rule: string): AppError {
    let code: string;
    let message: string;

    switch (rule) {
      case 'required':
        code = ERROR_CODES.VALIDATION_REQUIRED_FIELD;
        message = `${field} es requerido`;
        break;
      case 'email':
        code = ERROR_CODES.VALIDATION_EMAIL_INVALID;
        message = ERROR_MESSAGES[code];
        break;
      case 'password':
        code = ERROR_CODES.VALIDATION_PASSWORD_WEAK;
        message = ERROR_MESSAGES[code];
        break;
      default:
        code = 'VALIDATION_ERROR';
        message = `Error de validación en ${field}`;
    }

    return this.createError(code, message, 'validation', { field, value, rule });
  }

  // Handle security errors
  handleSecurityError(type: 'xss' | 'csrf' | 'suspicious', details?: any): AppError {
    let code: string;
    let message: string;

    switch (type) {
      case 'xss':
        code = ERROR_CODES.SECURITY_XSS_DETECTED;
        message = ERROR_MESSAGES[code];
        break;
      case 'csrf':
        code = ERROR_CODES.SECURITY_CSRF_INVALID;
        message = ERROR_MESSAGES[code];
        break;
      case 'suspicious':
        code = ERROR_CODES.SECURITY_SUSPICIOUS_ACTIVITY;
        message = ERROR_MESSAGES[code];
        break;
      default:
        code = 'SECURITY_ERROR';
        message = 'Error de seguridad detectado';
    }

    const error = this.createError(code, message, 'security', details);
    this.logError(error);
    return error;
  }

  // Log error to console and storage
  logError(error: AppError): void {
    console.error('Application Error:', error);

    // Store error for debugging
    this.errors.push(error);

    // Keep only the last maxErrors errors
    if (this.errors.length > this.maxErrors) {
      this.errors = this.errors.slice(-this.maxErrors);
    }

    // In production, you could send errors to monitoring service
    if (import.meta.env.MODE === 'production') {
      this.sendToMonitoring(error);
    }
  }

  // Send error to monitoring service (placeholder)
  private sendToMonitoring(error: AppError): void {
    // Implement actual error monitoring service here
    // e.g., Sentry, LogRocket, etc.
    console.info('Would send to monitoring:', error.code);
  }

  // Get user-friendly error message
  getUserMessage(error: AppError): string {
    return ERROR_MESSAGES[error.code] || error.message || 'Ha ocurrido un error inesperado';
  }

  // Check if error should trigger logout
  shouldLogout(error: AppError): boolean {
    const logoutCodes = [
      ERROR_CODES.AUTH_TOKEN_EXPIRED,
      ERROR_CODES.AUTH_TOKEN_INVALID,
      ERROR_CODES.AUTH_ACCOUNT_DISABLED,
    ];
    return logoutCodes.includes(error.code);
  }

  // Get recent errors for debugging
  getRecentErrors(count: number = 10): AppError[] {
    return this.errors.slice(-count);
  }

  // Clear error history
  clearErrors(): void {
    this.errors = [];
  }

  // Create error from fetch response
  async handleFetchError(response: Response): Promise<AppError> {
    let errorData: any = {};

    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { detail: response.statusText };
    }

    return this.handleApiError({
      response: {
        status: response.status,
        data: errorData,
      },
    });
  }
}

// Global error handler instance
export const errorHandler = new ErrorHandler();

// Global error boundary for unhandled errors
export const setupGlobalErrorHandler = (): void => {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    const error = errorHandler.createError(
      'UNHANDLED_PROMISE',
      'Error no manejado en la aplicación',
      'unknown',
      { reason: event.reason }
    );
    errorHandler.logError(error);
  });

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
    const error = errorHandler.createError(
      'UNCAUGHT_ERROR',
      event.message || 'Error no capturado',
      'unknown',
      {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
      }
    );
    errorHandler.logError(error);
  });
};

export default errorHandler;