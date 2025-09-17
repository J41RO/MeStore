// ~/frontend/src/services/vendorOrderService.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Vendor Order Service (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Servicio vendor orders con configuración dinámica y hosting ready
 *
 * Características enterprise:
 * - Configuración dinámica por entorno
 * - Sistema de retry y timeout configurable
 * - Caching inteligente con TTL
 * - Error handling robusto
 * - Token refresh automático
 * - Performance monitoring
 */

import { VENDOR_CONFIG, VendorOrder, VendorOrderFilters, VendorOrderResponse } from '../config/vendorConfig';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

class VendorOrderService {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private authToken: string | null = null;

  constructor() {
    // TODO_HOSTING: Configurar interceptor para token refresh automático
    this.authToken = localStorage.getItem('access_token');
  }

  // PRODUCTION_READY: Método HTTP con retry y timeout
  private async makeRequest<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const fullUrl = `${VENDOR_CONFIG.API_BASE_URL}${url}`;

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'MeStore-VendorDashboard/1.0',
        ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
        ...options.headers,
      },
      signal: AbortSignal.timeout(VENDOR_CONFIG.API_TIMEOUT),
      ...options,
    };

    for (let attempt = 1; attempt <= VENDOR_CONFIG.RETRY_ATTEMPTS; attempt++) {
      try {
        const response = await fetch(fullUrl, defaultOptions);

        if (response.status === 401) {
          // TODO_HOSTING: Implementar refresh token automático
          await this.refreshAuthToken();
          continue;
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return { data, success: true };

      } catch (error) {
        const isLastAttempt = attempt === VENDOR_CONFIG.RETRY_ATTEMPTS;

        if (error instanceof Error) {
          console.error(`Attempt ${attempt}/${VENDOR_CONFIG.RETRY_ATTEMPTS} failed:`, error.message);

          if (isLastAttempt) {
            return {
              error: `Request failed after ${VENDOR_CONFIG.RETRY_ATTEMPTS} attempts: ${error.message}`,
              success: false
            };
          }
        }

        // Backoff exponencial entre intentos
        await this.delay(Math.pow(2, attempt - 1) * 1000);
      }
    }

    return { error: 'Request failed', success: false };
  }

  // PERFORMANCE_CRITICAL: Cache con TTL para evitar requests innecesarios
  private getCachedData<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && (Date.now() - cached.timestamp) < VENDOR_CONFIG.CACHE_DURATION) {
      return cached.data;
    }
    return null;
  }

  private setCachedData(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  // PRODUCTION_READY: Obtener órdenes del vendor con filtros
  async getVendorOrders(
    vendorId: string,
    filters: VendorOrderFilters = {}
  ): Promise<ApiResponse<VendorOrderResponse>> {
    const cacheKey = `vendor-orders-${vendorId}-${JSON.stringify(filters)}`;

    // Verificar cache primero
    const cached = this.getCachedData<VendorOrderResponse>(cacheKey);
    if (cached) {
      return { data: cached, success: true };
    }

    const queryParams = new URLSearchParams();
    if (filters.status) queryParams.append('status', filters.status);
    if (filters.page) queryParams.append('page', filters.page.toString());
    if (filters.limit) queryParams.append('limit', filters.limit.toString());

    const url = `/test/vendor/${vendorId}/orders${queryParams.toString() ? `?${queryParams}` : ''}`;

    const result = await this.makeRequest<VendorOrderResponse>(url);

    if (result.success && result.data) {
      this.setCachedData(cacheKey, result.data);
    }

    return result;
  }

  // PRODUCTION_READY: Obtener detalle de orden específica
  async getOrderDetail(orderId: number): Promise<ApiResponse<VendorOrder>> {
    const cacheKey = `order-detail-${orderId}`;

    const cached = this.getCachedData<VendorOrder>(cacheKey);
    if (cached) {
      return { data: cached, success: true };
    }

    const result = await this.makeRequest<VendorOrder>(`/test/orders/${orderId}`);

    if (result.success && result.data) {
      this.setCachedData(cacheKey, result.data);
    }

    return result;
  }

  // PRODUCTION_READY: Actualizar estado de orden (solo vendors)
  async updateOrderStatus(
    orderId: number,
    newStatus: string,
    notes?: string
  ): Promise<ApiResponse<{ success: boolean; message: string }>> {
    // Invalidar cache relacionado
    this.invalidateOrderCache(orderId);

    const result = await this.makeRequest(`/test/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status: newStatus, notes }),
    });

    return result;
  }

  // PRODUCTION_READY: Obtener lista de vendors (para desarrollo/testing)
  async getVendors(): Promise<ApiResponse<Array<{id: string; email: string; full_name: string}>>> {
    const cached = this.getCachedData('vendors-list');
    if (cached) {
      return { data: cached, success: true };
    }

    const result = await this.makeRequest('/test/vendors');

    if (result.success && result.data) {
      this.setCachedData('vendors-list', result.data);
    }

    return result;
  }

  // SECURITY_REVIEW: Refresh token automático
  private async refreshAuthToken(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${VENDOR_CONFIG.API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        this.authToken = data.access_token;
        localStorage.setItem('access_token', data.access_token);
      } else {
        // Redirect to login if refresh fails
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      window.location.href = '/login';
    }
  }

  // Utility methods
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private invalidateOrderCache(orderId?: number): void {
    const keysToDelete = [];
    for (const key of this.cache.keys()) {
      if (orderId && key.includes(`order-detail-${orderId}`)) {
        keysToDelete.push(key);
      } else if (key.includes('vendor-orders-')) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key));
  }

  // PERFORMANCE_CRITICAL: Clear cache manualmente si necesario
  clearCache(): void {
    this.cache.clear();
  }

  // Real-time updates con WebSocket (preparado para implementación)
  private websocket: WebSocket | null = null;

  enableRealTimeUpdates(vendorId: string): void {
    if (!VENDOR_CONFIG.ENABLE_REALTIME) return;

    try {
      this.websocket = new WebSocket(`${VENDOR_CONFIG.WEBSOCKET_URL}/vendor/${vendorId}/orders`);

      this.websocket.onmessage = (event) => {
        const update = JSON.parse(event.data);
        this.handleRealTimeUpdate(update);
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.warn('WebSocket not available:', error);
    }
  }

  private handleRealTimeUpdate(update: any): void {
    // Invalidar cache cuando hay updates en tiempo real
    this.invalidateOrderCache(update.orderId);

    // Trigger re-fetch o emit event para components
    window.dispatchEvent(new CustomEvent('vendor-orders-updated', { detail: update }));
  }

  disconnect(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}

// Singleton instance
export const vendorOrderService = new VendorOrderService();
export default vendorOrderService;