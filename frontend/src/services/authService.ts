/**
 * AuthService - Production Ready API Integration
 * React Specialist AI Implementation
 *
 * Servicio de autenticación totalmente integrado con FastAPI backend
 * Incluye manejo avanzado de errores, interceptors y tipos TypeScript
 */

import axios, { AxiosResponse } from 'axios';
import { getEnvVar } from '../utils/env';

// Helper function to determine environment
const isDevelopment = () => {
  try {
    // Check if running in Jest test environment
    if (typeof global !== 'undefined' && global.importMetaMock) {
      return global.importMetaMock.env.DEV || false;
    }

    // Check for Node.js test environment (Jest)
    if (typeof process !== 'undefined' && process.env.NODE_ENV === 'test') {
      return false;
    }

    // In browser environment, check for development
    if (typeof window !== 'undefined') {
      const env = (window as any).__VITE_ENV__ || {};
      return env.DEV || false;
    }
  } catch (error) {
    // Fallback
  }

  return false;
};

// Create a robust axios client for auth with environment-aware configuration
const authClient = axios.create({
  // In development, use proxy. In production, use direct API URL
  baseURL: isDevelopment()
    ? undefined
    : (getEnvVar('VITE_API_BASE_URL') || 'http://192.168.1.137:8000'),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add request interceptor for debugging and auth token
authClient.interceptors.request.use(request => {
  // Add authorization token if available
  const token = localStorage.getItem('access_token');
  if (token) {
    request.headers.Authorization = `Bearer ${token}`;
  }

  const fullUrl = request.baseURL ? `${request.baseURL}${request.url}` : request.url;
  console.log('🚀 AUTH REQUEST:', request.method?.toUpperCase(), fullUrl);
  console.log('📤 Headers:', JSON.stringify(request.headers, null, 2));
  console.log('📦 Payload:', JSON.stringify(request.data, null, 2));
  return request;
});

// Add response interceptor for debugging
authClient.interceptors.response.use(
  response => {
    const fullUrl = response.config.baseURL ? `${response.config.baseURL}${response.config.url}` : response.config.url;
    console.log('✅ AUTH SUCCESS:', response.status, fullUrl);
    return response;
  },
  error => {
    const fullUrl = error.config?.baseURL ? `${error.config.baseURL}${error.config.url}` : error.config?.url;
    console.log('❌ AUTH ERROR:', error.response?.status, fullUrl);
    console.log('💥 Error data:', JSON.stringify(error.response?.data, null, 2));
    console.log('🔍 Request URL details:', {
      baseURL: error.config?.baseURL,
      url: error.config?.url,
      fullUrl: fullUrl
    });
    return Promise.reject(error);
  }
);
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserInfoResponse,
  PasswordResetRequest,
  PasswordResetConfirm,
  PasswordResetResponse,
  RefreshTokenRequest,
  OTPSendRequest,
  OTPVerifyRequest,
  OTPResponse,
  ApiError as IApiError,
} from '../types';

// Re-export for backward compatibility
export interface UserInfo extends UserInfoResponse {}
export interface AuthError {
  detail: string;
  status_code?: number;
}

/**
 * Custom ApiError class for consistent error handling
 */
class ApiError extends Error implements IApiError {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Authentication endpoints (proxy forwards to backend at target/api with path rewrite)
const AUTH_ENDPOINTS = {
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  ADMIN_LOGIN: '/api/v1/auth/admin-login',
  LOGOUT: '/api/v1/auth/logout',
  REFRESH: '/api/v1/auth/refresh-token',
  ME: '/api/v1/auth/me',
  FORGOT_PASSWORD: '/api/v1/auth/forgot-password',
  RESET_PASSWORD: '/api/v1/auth/reset-password',
  SEND_OTP: '/api/v1/auth/send-otp',
  VERIFY_OTP: '/api/v1/auth/verify-otp',
} as const;

/**
 * Enhanced Authentication Service with complete API integration
 */
class AuthService {
  private readonly endpoints = AUTH_ENDPOINTS;

  /**
   * Handle API errors consistently
   */
  private handleApiError(error: any, defaultMessage: string): ApiError {
    if (error.response) {
      const { status, data } = error.response;
      return new ApiError(
        data?.message || data?.detail || defaultMessage,
        status,
        data?.code,
        data
      );
    } else if (error.request) {
      return new ApiError(
        'Error de conexión. Verifica tu conexión a internet.',
        0,
        'NETWORK_ERROR'
      );
    } else {
      return new ApiError(
        error.message || defaultMessage,
        500,
        'UNKNOWN_ERROR'
      );
    }
  }

  /**
   * Check if token is expired
   */
  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  }

  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<{ success: boolean; data?: TokenResponse; error?: string }> {
    try {
      // Sanitize credentials to remove leading/trailing spaces
      const sanitizedCredentials = {
        email: credentials.email.trim(),
        password: credentials.password.trim()
      };

      const response = await authClient.post<TokenResponse>(
        this.endpoints.LOGIN,
        sanitizedCredentials
      );

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        return { success: true, data: response.data };
      } else {
        return { success: false, error: 'No se recibió token de acceso' };
      }
    } catch (error: any) {
      const apiError = this.handleApiError(error, 'Error al iniciar sesión');
      return { success: false, error: apiError.message };
    }
  }

  /**
   * Admin login with enhanced validation
   */
  async adminLogin(credentials: LoginRequest): Promise<{ success: boolean; data?: TokenResponse; error?: string }> {
    try {
      // Sanitize credentials to remove leading/trailing spaces
      const sanitizedCredentials = {
        email: credentials.email.trim(),
        password: credentials.password.trim()
      };

      const response = await authClient.post<TokenResponse>(
        this.endpoints.ADMIN_LOGIN,
        sanitizedCredentials
      );

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        return { success: true, data: response.data };
      } else {
        return { success: false, error: 'No se recibió token de acceso' };
      }
    } catch (error: any) {
      const apiError = this.handleApiError(error, 'Error en autenticación administrativa');
      return { success: false, error: apiError.message };
    }
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<{ success: boolean; data?: UserInfo; error?: string }> {
    try {
      const response = await authClient.get<UserInfo>(this.endpoints.ME);
      return { success: true, data: response.data };
    } catch (error: any) {
      const apiError = this.handleApiError(error, 'Error al obtener información del usuario');
      return { success: false, error: apiError.message };
    }
  }

  /**
   * Register new user
   */
  async register(userData: LoginRequest): Promise<{ success: boolean; data?: TokenResponse; error?: string }> {
    try {
      const response = await authClient.post<TokenResponse>(
        this.endpoints.REGISTER,
        userData
      );

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        return { success: true, data: response.data };
      } else {
        return { success: false, error: 'No se recibió token de acceso' };
      }
    } catch (error: any) {
      const apiError = this.handleApiError(error, 'Error al registrar usuario');
      return { success: false, error: apiError.message };
    }
  }

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<{ success: boolean; error?: string }> {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          await authClient.post(this.endpoints.LOGOUT);
        } catch (error) {
          console.warn('Error en logout del servidor:', error);
        }
      }

      this.clearTokens();
      return { success: true };
    } catch (error: any) {
      this.clearTokens();
      return { success: false, error: 'Error durante el logout' };
    }
  }

  /**
   * Password reset methods
   */
  async forgotPassword(request: PasswordResetRequest): Promise<PasswordResetResponse> {
    try {
      const response = await authClient.post<PasswordResetResponse>(
        this.endpoints.FORGOT_PASSWORD,
        request
      );
      return response.data;
    } catch (error: any) {
      throw this.handleApiError(error, 'Error al solicitar recuperación de contraseña');
    }
  }

  async resetPassword(request: PasswordResetConfirm): Promise<PasswordResetResponse> {
    try {
      const response = await authClient.post<PasswordResetResponse>(
        this.endpoints.RESET_PASSWORD,
        request
      );
      return response.data;
    } catch (error: any) {
      throw this.handleApiError(error, 'Error al restablecer contraseña');
    }
  }

  /**
   * OTP methods
   */
  async sendOTP(request: OTPSendRequest): Promise<OTPResponse> {
    try {
      const response = await authClient.post<OTPResponse>(
        this.endpoints.SEND_OTP,
        request
      );
      return response.data;
    } catch (error: any) {
      throw this.handleApiError(error, 'Error al enviar código OTP');
    }
  }

  async verifyOTP(request: OTPVerifyRequest): Promise<OTPResponse> {
    try {
      const response = await authClient.post<OTPResponse>(
        this.endpoints.VERIFY_OTP,
        request
      );
      return response.data;
    } catch (error: any) {
      throw this.handleApiError(error, 'Error al verificar código OTP');
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(refreshTokenValue?: string): Promise<TokenResponse> {
    const token = refreshTokenValue || localStorage.getItem('refresh_token');

    if (!token) {
      throw new ApiError('No refresh token available', 401);
    }

    try {
      const response = await authClient.post<TokenResponse>(
        this.endpoints.REFRESH,
        { refresh_token: token }
      );

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }

      return response.data;
    } catch (error: any) {
      this.clearTokens();
      throw this.handleApiError(error, 'Error al refrescar token');
    }
  }

  /**
   * Utility methods
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token && !this.isTokenExpired(token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('auth_token'); // Legacy cleanup
  }

  async validateToken(): Promise<boolean> {
    try {
      const result = await this.getCurrentUser();
      return result.success;
    } catch (error) {
      return false;
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;

// Export class and error for testing purposes
export { AuthService, ApiError };