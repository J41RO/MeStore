// ~/frontend/src/services/orderService.ts
// PRODUCTION_READY: Cliente API robusto para órdenes enterprise

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  OrderFilters,
  OrdersResponse,
  OrderResponse,
  CreateOrderRequest,
  UpdateOrderStatusRequest,
  TrackingResponse,
  getApiBaseUrl
} from '../types/orders';

class OrderService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 10000, // 10 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('authToken');
          sessionStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get all orders with filters
   */
  async getOrders(filters?: OrderFilters): Promise<OrdersResponse> {
    try {
      const params = new URLSearchParams();
      
      if (filters) {
        if (filters.status && filters.status !== 'all') {
          params.append('status', filters.status);
        }
        if (filters.search) {
          params.append('search', filters.search);
        }
        if (filters.date_from) {
          params.append('date_from', filters.date_from);
        }
        if (filters.date_to) {
          params.append('date_to', filters.date_to);
        }
        if (filters.buyer_id) {
          params.append('buyer_id', filters.buyer_id);
        }
        if (filters.page) {
          params.append('page', filters.page.toString());
        }
        if (filters.limit) {
          params.append('limit', filters.limit.toString());
        }
      }

      const response = await this.api.get<OrdersResponse>(
        `/api/v1/orders${params.toString() ? `?${params.toString()}` : ''}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching orders:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get single order by ID
   */
  async getOrder(orderId: string): Promise<OrderResponse> {
    try {
      const response = await this.api.get<OrderResponse>(`/api/v1/orders/${orderId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching order:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Create new order
   */
  async createOrder(orderData: CreateOrderRequest): Promise<OrderResponse> {
    try {
      const response = await this.api.post<OrderResponse>('/api/v1/orders', orderData);
      return response.data;
    } catch (error: any) {
      console.error('Error creating order:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Update order status
   */
  async updateOrderStatus(orderId: string, statusData: UpdateOrderStatusRequest): Promise<OrderResponse> {
    try {
      const response = await this.api.patch<OrderResponse>(
        `/api/v1/orders/${orderId}/status`,
        statusData
      );
      return response.data;
    } catch (error: any) {
      console.error('Error updating order status:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Cancel order
   */
  async cancelOrder(orderId: string, reason?: string): Promise<OrderResponse> {
    try {
      const response = await this.api.post<OrderResponse>(
        `/api/v1/orders/${orderId}/cancel`,
        { reason }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error cancelling order:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get public tracking information (no auth required)
   */
  async getPublicTracking(orderNumber: string): Promise<TrackingResponse> {
    try {
      const response = await axios.get<TrackingResponse>(
        `${getApiBaseUrl()}/api/v1/orders/track/${orderNumber}`,
        { timeout: 10000 }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error fetching public tracking:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get detailed tracking information (auth required)
   */
  async getDetailedTracking(orderNumber: string): Promise<TrackingResponse> {
    try {
      const response = await this.api.get<TrackingResponse>(
        `/api/v1/orders/track/${orderNumber}/detailed`
      );
      return response.data;
    } catch (error: any) {
      console.error('Error fetching detailed tracking:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Generate tracking token for public access
   */
  async generateTrackingToken(orderNumber: string, email: string): Promise<{
    success: boolean;
    data: {
      tracking_token: string;
      tracking_url: string;
      expires_in: string;
      order_number: string;
    };
    message?: string;
  }> {
    try {
      const response = await axios.post(
        `${getApiBaseUrl()}/api/v1/orders/tracking/generate-token`,
        { order_number: orderNumber, email },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error generating tracking token:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get my orders (for current authenticated user)
   */
  async getMyOrders(filters?: Omit<OrderFilters, 'buyer_id'>): Promise<OrdersResponse> {
    try {
      return await this.getOrders(filters);
    } catch (error: any) {
      console.error('Error fetching my orders:', error);
      throw this.handleApiError(error);
    }
  }

  /**
   * Handle API errors consistently
   */
  private handleApiError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Error ${error.response.status}: ${error.response.statusText}`;
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Error de conexión. Verifique su conexión a internet.');
    } else {
      // Other error
      return new Error(error.message || 'Error inesperado');
    }
  }

  /**
   * Retry wrapper for important operations
   */
  private async retryOperation<T>(
    operation: () => Promise<T>,
    retries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryOperation(operation, retries - 1, delay * 2);
      }
      throw error;
    }
  }

  /**
   * Get orders with retry for reliability
   */
  async getOrdersWithRetry(filters?: OrderFilters): Promise<OrdersResponse> {
    return this.retryOperation(() => this.getOrders(filters));
  }
}

// Export singleton instance
export const orderService = new OrderService();
export default orderService;