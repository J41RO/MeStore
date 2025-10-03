import api from './api';

/**
 * Vendor Order Service - API integration for vendor order management
 *
 * Backend Endpoints:
 * - GET /api/v1/vendor/orders - List all vendor orders
 * - GET /api/v1/vendor/orders/{id} - Get order details
 * - PATCH /api/v1/vendor/orders/{order_id}/items/{item_id}/status - Update item status
 * - GET /api/v1/vendor/orders/stats/summary - Get vendor stats
 */

// ===== TYPE DEFINITIONS =====

export interface VendorOrderItem {
  id: string;
  product_id: string;
  product_name: string;
  product_sku: string;
  product_image_url?: string;
  unit_price: number;
  quantity: number;
  total_price: number;
  status: 'pending' | 'preparing' | 'ready_to_ship' | 'shipped' | 'delivered' | 'cancelled';
  variant_attributes?: Record<string, string>;
}

export interface VendorOrder {
  id: string;
  order_number: string;
  customer_name: string;
  customer_email?: string;
  customer_phone?: string;
  status: string;
  items: VendorOrderItem[];
  order_date: string;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  notes?: string;
  total_amount: number;
}

export interface VendorOrderStats {
  total_orders: number;
  pending_items: number;
  preparing_items: number;
  ready_to_ship_items: number;
  total_revenue: number;
}

export interface UpdateItemStatusRequest {
  status: 'pending' | 'preparing' | 'ready_to_ship' | 'shipped' | 'delivered' | 'cancelled';
}

// ===== VENDOR ORDER SERVICE =====

export const vendorOrderService = {
  /**
   * Get all orders for the current vendor
   * @param skip Pagination offset
   * @param limit Items per page
   * @param status Optional status filter
   */
  async getOrders(
    skip: number = 0,
    limit: number = 20,
    status: string | null = null
  ): Promise<{ orders: VendorOrder[]; total: number }> {
    const params: Record<string, any> = { skip, limit };
    if (status) {
      params.status = status;
    }

    const response = await api.get('/api/v1/vendor/orders', { params });
    return response.data;
  },

  /**
   * Get detailed information for a specific order
   * @param orderId Order ID
   */
  async getOrderDetail(orderId: string): Promise<VendorOrder> {
    const response = await api.get(`/api/v1/vendor/orders/${orderId}`);
    return response.data;
  },

  /**
   * Update the status of a specific order item
   * @param orderId Order ID
   * @param itemId Order item ID
   * @param status New status
   */
  async updateItemStatus(
    orderId: string,
    itemId: string,
    status: UpdateItemStatusRequest['status']
  ): Promise<VendorOrderItem> {
    const response = await api.patch(
      `/api/v1/vendor/orders/${orderId}/items/${itemId}/status`,
      { status }
    );
    return response.data;
  },

  /**
   * Get vendor statistics summary
   */
  async getStats(): Promise<VendorOrderStats> {
    const response = await api.get('/api/v1/vendor/orders/stats/summary');
    return response.data;
  },

  /**
   * Helper: Get human-readable status label
   */
  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      pending: 'Pendiente',
      preparing: 'Preparando',
      ready_to_ship: 'Listo para Envío',
      shipped: 'Enviado',
      delivered: 'Entregado',
      cancelled: 'Cancelado'
    };
    return labels[status] || status;
  },

  /**
   * Helper: Get status color for UI
   */
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      pending: '#F59E0B',      // Amber
      preparing: '#EF4444',    // Red
      ready_to_ship: '#10B981', // Green
      shipped: '#3B82F6',      // Blue
      delivered: '#6B7280',    // Gray
      cancelled: '#DC2626'     // Dark Red
    };
    return colors[status] || '#6B7280';
  }
};

export default vendorOrderService;
