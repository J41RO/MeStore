/**
 * Base API Service for MeStore Frontend
 * Provides consistent API client with EntityId type handling
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type {
  EntityId,
  StandardResponse,
  PaginatedResponse,
  ApiError,
  isStandardResponse,
  isApiError,
} from '../types';

// ========================================
// API CONFIGURATION
// ========================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * ApiConfig - Configuration interface for API client
 */
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

/**
 * Default API configuration
 */
const defaultConfig: ApiConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'MeStore-Frontend/1.0.0',
  },
};

// ========================================
// ERROR HANDLING
// ========================================

/**
 * StandardApiError - Consistent API error structure
 */
export class StandardApiError extends Error implements ApiError {
  public status: 'error' = 'error';

  constructor(
    message: string,
    public readonly statusCode: number = 500,
    public readonly code?: string,
    public readonly field?: string,
    public readonly details?: Record<string, any>,
    public readonly errors?: Record<string, string[]>
  ) {
    super(message);
    this.name = 'StandardApiError';
  }

  /**
   * Create StandardApiError from axios error
   */
  static fromAxiosError(error: AxiosError): StandardApiError {
    if (error.response) {
      const { status, data } = error.response;
      const responseData = data as any;

      return new StandardApiError(
        responseData?.message || responseData?.detail || 'API request failed',
        status,
        responseData?.code,
        responseData?.field,
        responseData,
        responseData?.errors
      );
    } else if (error.request) {
      return new StandardApiError(
        'Network error - please check your connection',
        0,
        'NETWORK_ERROR'
      );
    } else {
      return new StandardApiError(
        error.message || 'Unknown error occurred',
        0,
        'UNKNOWN_ERROR'
      );
    }
  }
}

// ========================================
// REQUEST/RESPONSE INTERCEPTORS
// ========================================

/**
 * Request interceptor to add authentication token
 */
function requestInterceptor(config: any) {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

/**
 * Response interceptor for consistent error handling
 */
function responseInterceptor(response: AxiosResponse) {
  return response;
}

/**
 * Response error interceptor
 */
function responseErrorInterceptor(error: AxiosError) {
  const apiError = StandardApiError.fromAxiosError(error);

  // Handle token expiration
  if (apiError.statusCode === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.dispatchEvent(new CustomEvent('auth:logout'));
  }

  return Promise.reject(apiError);
}

// ========================================
// BASE API CLIENT
// ========================================

/**
 * BaseApiService - Foundational API service with consistent EntityId handling
 */
export class BaseApiService {
  protected client: AxiosInstance;

  constructor(config: Partial<ApiConfig> = {}) {
    const finalConfig = { ...defaultConfig, ...config };

    this.client = axios.create({
      baseURL: finalConfig.baseURL,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    });

    // Add interceptors
    this.client.interceptors.request.use(requestInterceptor);
    this.client.interceptors.response.use(
      responseInterceptor,
      responseErrorInterceptor
    );
  }

  // ========================================
  // HELPER METHODS
  // ========================================

  /**
   * Validate EntityId parameter
   */
  protected validateEntityId(id: EntityId, paramName: string = 'id'): void {
    if (!id || typeof id !== 'string' || id.trim().length === 0) {
      throw new StandardApiError(
        `Invalid ${paramName}: must be a non-empty string`,
        400,
        'INVALID_ENTITY_ID',
        paramName
      );
    }
  }

  /**
   * Build URL with EntityId parameter
   */
  protected buildUrl(basePath: string, id: EntityId): string {
    this.validateEntityId(id);
    return `${basePath}/${encodeURIComponent(id)}`;
  }

  /**
   * Extract data from StandardResponse
   */
  protected extractResponseData<T>(response: AxiosResponse<StandardResponse<T>>): T {
    const data = response.data;

    if (!isStandardResponse(data)) {
      throw new StandardApiError(
        'Invalid response format',
        response.status,
        'INVALID_RESPONSE_FORMAT'
      );
    }

    if (data.status === 'error') {
      throw new StandardApiError(
        data.message || 'API request failed',
        response.status,
        'API_ERROR',
        undefined,
        data as any
      );
    }

    if (!data.data) {
      throw new StandardApiError(
        'No data in response',
        response.status,
        'NO_DATA'
      );
    }

    return data.data;
  }

  /**
   * Extract paginated data
   */
  protected extractPaginatedData<T>(response: AxiosResponse<PaginatedResponse<T>>): PaginatedResponse<T> {
    const data = response.data;

    if (!isStandardResponse(data)) {
      throw new StandardApiError(
        'Invalid response format',
        response.status,
        'INVALID_RESPONSE_FORMAT'
      );
    }

    if (data.status === 'error') {
      throw new StandardApiError(
        data.message || 'API request failed',
        response.status,
        'API_ERROR',
        undefined,
        data as any
      );
    }

    return data;
  }

  // ========================================
  // GENERIC CRUD OPERATIONS
  // ========================================

  /**
   * Generic GET request
   */
  protected async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const response = await this.client.get<StandardResponse<T>>(url, { params });
    return this.extractResponseData(response);
  }

  /**
   * Generic GET by ID request
   */
  protected async getById<T>(basePath: string, id: EntityId): Promise<T> {
    const url = this.buildUrl(basePath, id);
    return this.get<T>(url);
  }

  /**
   * Generic GET list request with pagination
   */
  protected async getList<T>(
    url: string,
    params?: Record<string, any>
  ): Promise<PaginatedResponse<T>> {
    const response = await this.client.get<PaginatedResponse<T>>(url, { params });
    return this.extractPaginatedData(response);
  }

  /**
   * Generic POST request
   */
  protected async post<T, D = any>(url: string, data: D): Promise<T> {
    const response = await this.client.post<StandardResponse<T>>(url, data);
    return this.extractResponseData(response);
  }

  /**
   * Generic PUT request
   */
  protected async put<T, D = any>(basePath: string, id: EntityId, data: D): Promise<T> {
    const url = this.buildUrl(basePath, id);
    const response = await this.client.put<StandardResponse<T>>(url, data);
    return this.extractResponseData(response);
  }

  /**
   * Generic PATCH request
   */
  protected async patch<T, D = any>(basePath: string, id: EntityId, data: D): Promise<T> {
    const url = this.buildUrl(basePath, id);
    const response = await this.client.patch<StandardResponse<T>>(url, data);
    return this.extractResponseData(response);
  }

  /**
   * Generic DELETE request
   */
  protected async delete(basePath: string, id: EntityId): Promise<boolean> {
    const url = this.buildUrl(basePath, id);
    await this.client.delete(url);
    return true; // If no error thrown, deletion was successful
  }

  // ========================================
  // UTILITY METHODS
  // ========================================

  /**
   * Get the axios instance for advanced usage
   */
  public getClient(): AxiosInstance {
    return this.client;
  }

  /**
   * Update authentication token
   */
  public setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Remove authentication token
   */
  public clearAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }

  /**
   * Update base URL
   */
  public setBaseURL(baseURL: string): void {
    this.client.defaults.baseURL = baseURL;
  }

  /**
   * Add custom headers
   */
  public setHeaders(headers: Record<string, string>): void {
    Object.assign(this.client.defaults.headers.common, headers);
  }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

/**
 * Default API client instance
 */
export const apiClient = new BaseApiService();

// ========================================
// EXPORTS
// ========================================

export type { ApiConfig };
export default BaseApiService;