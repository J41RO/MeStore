/**
 * Admin Order Service
 *
 * SUPERUSER-only service for comprehensive order management.
 * Provides methods for viewing, filtering, updating, and cancelling orders.
 *
 * Security: All methods require SUPERUSER authentication token.
 */

import { apiClient } from './apiClient';

// ==================== TYPES ====================

export interface OrderItemDetail {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  product_image_url?: string;
  unit_price: number;
  quantity: number;
  total_price: number;
  variant_attributes?: string;
  vendor_id?: string;
  vendor_name?: string;
}

export interface OrderTransactionDetail {
  id: number;
  transaction_reference: string;
  amount: number;
  currency: string;
  status: string;
  payment_method_type: string;
  gateway: string;
  gateway_transaction_id?: string;
  created_at: string;
  processed_at?: string;
  failure_reason?: string;
}

export interface OrderListItem {
  id: number;
  order_number: string;
  buyer_id: string;
  buyer_email: string;
  buyer_name: string;
  total_amount: number;
  status: string;
  payment_status: string;
  created_at: string;
  items_count: number;
}

export interface OrderDetailAdmin {
  id: number;
  order_number: string;
  status: string;

  // Buyer information
  buyer_id: string;
  buyer_email: string;
  buyer_name: string;
  buyer_phone?: string;

  // Order totals
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  discount_amount: number;
  total_amount: number;

  // Shipping information
  shipping_name: string;
  shipping_phone: string;
  shipping_email?: string;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code?: string;
  shipping_country: string;
  tracking_number?: string;
  courier?: string;
  estimated_delivery?: string;
  shipping_events?: Array<{
    timestamp: string;
    status: string;
    location: string;
    description?: string;
  }>;

  // Timestamps
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
  cancelled_at?: string;

  // Additional info
  notes?: string;
  cancellation_reason?: string;

  // Related data
  items: OrderItemDetail[];
  transactions: OrderTransactionDetail[];
}

export interface OrdersListResponse {
  orders: OrderListItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface OrderStatsResponse {
  total_orders_today: number;
  total_orders_week: number;
  total_orders_month: number;
  revenue_today: number;
  revenue_week: number;
  revenue_month: number;
  orders_by_status: Record<string, number>;
  top_buyers: Array<{
    buyer_id: string;
    email: string;
    name: string;
    order_count: number;
    total_spent: number;
  }>;
  pending_orders_count: number;
  processing_orders_count: number;
}

export interface OrderStatusUpdate {
  status: string;
  notes?: string;
}

export interface OrderCancellation {
  reason: string;
  refund_requested?: boolean;
}

export interface CancellationResponse {
  success: boolean;
  message: string;
  order_id: number;
  cancellation_reason: string;
  refund_info?: {
    transaction_id: number;
    amount: number;
    gateway: string;
    status: string;
  };
}

// ==================== SERVICE ====================

class AdminOrderService {
  private baseURL = '/api/v1/admin';

  /**
   * Get all orders with filtering and pagination
   *
   * @param skip - Number of records to skip (pagination)
   * @param limit - Maximum number of records to return
   * @param status - Filter by order status
   * @param search - Search by order number, buyer email, or buyer name
   */
  async getAllOrders(
    skip: number = 0,
    limit: number = 20,
    status?: string,
    search?: string
  ): Promise<OrdersListResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    if (status) {
      params.append('status', status);
    }

    if (search) {
      params.append('search', search);
    }

    const response = await apiClient.get(`${this.baseURL}/orders?${params.toString()}`);
    return response.data;
  }

  /**
   * Get detailed order information
   *
   * @param orderId - Order ID
   */
  async getOrderDetail(orderId: number): Promise<OrderDetailAdmin> {
    const response = await apiClient.get(`${this.baseURL}/orders/${orderId}`);
    return response.data;
  }

  /**
   * Update order status
   *
   * @param orderId - Order ID
   * @param statusUpdate - Status update request
   */
  async updateOrderStatus(
    orderId: number,
    statusUpdate: OrderStatusUpdate
  ): Promise<OrderDetailAdmin> {
    const response = await apiClient.patch(
      `${this.baseURL}/orders/${orderId}/status`,
      statusUpdate
    );
    return response.data;
  }

  /**
   * Cancel an order
   *
   * @param orderId - Order ID
   * @param cancellation - Cancellation request with reason
   */
  async cancelOrder(
    orderId: number,
    cancellation: OrderCancellation
  ): Promise<CancellationResponse> {
    const response = await apiClient.delete(
      `${this.baseURL}/orders/${orderId}`,
      { data: cancellation }
    );
    return response.data;
  }

  /**
   * Get order statistics for admin dashboard
   */
  async getOrderStats(): Promise<OrderStatsResponse> {
    const response = await apiClient.get(`${this.baseURL}/orders/stats/dashboard`);
    return response.data;
  }

  /**
   * Export orders to CSV (future implementation)
   */
  async exportOrders(
    status?: string,
    startDate?: string,
    endDate?: string
  ): Promise<Blob> {
    // TODO: Implement export functionality
    throw new Error('Export functionality not implemented yet');
  }

  /**
   * Get order status options for filters
   */
  getOrderStatusOptions(): Array<{ value: string; label: string }> {
    return [
      { value: '', label: 'All Statuses' },
      { value: 'pending', label: 'Pending' },
      { value: 'confirmed', label: 'Confirmed' },
      { value: 'processing', label: 'Processing' },
      { value: 'shipped', label: 'Shipped' },
      { value: 'delivered', label: 'Delivered' },
      { value: 'cancelled', label: 'Cancelled' },
      { value: 'refunded', label: 'Refunded' },
    ];
  }

  /**
   * Format currency value for display
   */
  formatCurrency(amount: number, currency: string = 'COP'): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Get status badge color
   */
  getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      pending: 'warning',
      confirmed: 'info',
      processing: 'primary',
      shipped: 'secondary',
      delivered: 'success',
      cancelled: 'error',
      refunded: 'default',
    };
    return statusColors[status.toLowerCase()] || 'default';
  }

  /**
   * Get payment status badge color
   */
  getPaymentStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      pending: 'warning',
      processing: 'info',
      approved: 'success',
      declined: 'error',
      error: 'error',
      cancelled: 'default',
    };
    return statusColors[status.toLowerCase()] || 'default';
  }

  /**
   * Validate status transition
   */
  isValidStatusTransition(currentStatus: string, newStatus: string): boolean {
    const validTransitions: Record<string, string[]> = {
      pending: ['confirmed', 'cancelled'],
      confirmed: ['processing', 'cancelled'],
      processing: ['shipped', 'cancelled'],
      shipped: ['delivered', 'cancelled'],
      delivered: ['refunded'],
      cancelled: [],
      refunded: [],
    };

    const allowedStatuses = validTransitions[currentStatus.toLowerCase()] || [];
    return allowedStatuses.includes(newStatus.toLowerCase());
  }
}

export const adminOrderService = new AdminOrderService();
export default adminOrderService;
