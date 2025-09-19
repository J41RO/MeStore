import { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { apiClient } from './apiClient';
import { authService } from './authService';
import { handleCorsError, CorsErrorInfo } from '../utils/corsErrorHandler';
import type { AuthInterceptorConfig } from '../types';

// Configuración de retry
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 segundo base
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];
const RETRYABLE_ERROR_CODES = ['ECONNABORTED', 'ENOTFOUND', 'ECONNRESET'];

// Función para transformar errores para la UI con análisis CORS avanzado
const transformErrorForUI = (error: AxiosError, context?: string) => {
  const corsInfo: CorsErrorInfo = handleCorsError(error, context);

  const transformedError = {
    ...error,
    userMessage: corsInfo.userMessage,
    devMessage: corsInfo.devMessage,
    statusCode: error.response?.status || 0,
    timestamp: new Date().toISOString(),
    isCorsError: corsInfo.isCorsError,
    isNetworkError: corsInfo.isNetworkError,
    isConfigurationError: corsInfo.isConfigurationError,
    suggestedActions: corsInfo.suggestedActions,
  };

  // Fallback para errores con response
  if (error.response && !corsInfo.isCorsError && !corsInfo.isNetworkError) {
    const status = error.response.status;
    transformedError.userMessage =
      status >= 500
        ? 'Error del servidor. Intenta más tarde.'
        : (error.response.data as any)?.message || 'Error en la solicitud';
  }

  return transformedError;
};

// Función de retry con backoff exponencial
const retryRequest = async (
  originalRequest: InternalAxiosRequestConfig,
  retryCount = 0
): Promise<any> => {
  if (retryCount >= MAX_RETRIES) {
    throw new Error(`Max retries (${MAX_RETRIES}) exceeded`);
  }

  // Backoff exponencial: 1s, 2s, 4s
  const delay = RETRY_DELAY * Math.pow(2, retryCount);

  await new Promise(resolve => setTimeout(resolve, delay));

  console.log(
    `Retry attempt ${retryCount + 1}/${MAX_RETRIES} after ${delay}ms`
  );

  return apiClient(originalRequest);
};

// Determinar si un error es retryable
const isRetryableError = (error: AxiosError): boolean => {
  // Errores de red sin response
  if (!error.response && error.code) {
    return RETRYABLE_ERROR_CODES.includes(error.code);
  }

  // Errores HTTP específicos
  if (error.response) {
    return RETRYABLE_STATUS_CODES.includes(error.response.status);
  }

  return false;
};

// Endpoints que NO deben hacer retry
const shouldSkipRetry = (url?: string): boolean => {
  if (!url) return false;

  const skipPatterns = [
    '/auth/login',
    '/auth/refresh',
    '/auth/logout',
    '/health',
    '/ready',
  ];

  return skipPatterns.some(pattern => url.includes(pattern));
};

// Flag para evitar loops infinitos durante refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });

  failedQueue = [];
};

// Interceptor de Request: Agregar token automáticamente usando authService
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    // Manejo de errores de red y timeout en request
    if (!error.response) {
      return Promise.reject(transformErrorForUI(error, 'Request Interceptor'));
    }

    if (error.response) {
      const status = error.response.status;
      const message = (error.response.data as any)?.message || error.message;

      switch (status) {
        case 403:
          console.error('Acceso denegado:', message);
          break;
        case 404:
          console.error('Recurso no encontrado:', message);
          break;
        case 500:
          console.error('Error interno del servidor:', message);
          break;
        default:
          if (status >= 500) {
            console.error('Error del servidor:', message);
          }
      }
    }

    return Promise.reject(error);
  }
);

// Interceptor de Response: Manejar refresh automático y retry logic
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
      _retryCount?: number;
    };

    // Manejar errores 401 (unauthorized) con refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya está refreshing, agregar a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => {
            return apiClient(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = authService.getRefreshToken();

        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Usar authService para refresh token
        const tokenResponse = await authService.refreshToken(refreshToken);

        // Procesar cola de requests fallidos
        processQueue(null, tokenResponse.access_token);

        // Reintentar request original
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${tokenResponse.access_token}`;
        }

        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh falló - limpiar tokens y redirigir a login
        processQueue(refreshError, null);
        authService.clearTokens();

        // Disparar evento para que AuthContext maneje logout
        window.dispatchEvent(new CustomEvent('auth:logout'));

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Retry logic para errores retryables (excepto 401 que ya se maneja arriba)
    if (
      isRetryableError(error) &&
      !originalRequest._retry &&
      !shouldSkipRetry(originalRequest.url) &&
      error.response?.status !== 401
    ) {
      originalRequest._retry = true;
      const retryCount = originalRequest._retryCount || 0;
      originalRequest._retryCount = retryCount;

      try {
        console.log(
          `Retrying request to ${originalRequest.url} (attempt ${retryCount + 1}/${MAX_RETRIES})`
        );
        return await retryRequest(originalRequest, retryCount);
      } catch (retryError) {
        console.error('All retry attempts failed:', retryError);
        return Promise.reject(transformErrorForUI(error, 'Retry Logic'));
      }
    }

    return Promise.reject(transformErrorForUI(error, 'Response Interceptor'));
  }
);

export { apiClient };
