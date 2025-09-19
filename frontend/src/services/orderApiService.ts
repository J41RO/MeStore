/**
 * Order API Service for MeStore Frontend
 * Handles all order-related API operations with consistent EntityId types
 */

import { BaseApiService } from './baseApiService';
import type {
  EntityId,
  PaginatedResponse,
  Order,
  CreateOrderRequest,
  UpdateOrderRequest,
  OrderSearchRequest,
  OrderResponse,
  OrderListResponse,
  OrderStatus,
  PaymentStatus,
} from '../types';

// ========================================
// ORDER API ENDPOINTS
// ========================================

const ORDER_ENDPOINTS = {
  BASE: '/orders',
  SEARCH: '/orders/search',
  USER_ORDERS: '/orders/user',
  VENDOR_ORDERS: '/orders/vendor',
  ADMIN_ORDERS: '/orders/admin',
  STATUS_UPDATE: '/orders/status',
  PAYMENT_UPDATE: '/orders/payment',
  TRACKING: '/orders/tracking',
  CANCEL: '/orders/cancel',
  METRICS: '/orders/metrics',
} as const;

// ========================================
// ORDER API SERVICE
// ========================================

/**
 * OrderApiService - Complete order API integration
 */
export class OrderApiService extends BaseApiService {
  private readonly endpoints = ORDER_ENDPOINTS;

  // ========================================
  // BASIC CRUD OPERATIONS
  // ========================================

  /**
   * Get all orders with optional pagination and filters
   */
  async getOrders(params?: OrderSearchRequest): Promise<OrderListResponse> {
    return this.getList<Order>(this.endpoints.BASE, params);
  }

  /**
   * Get a single order by ID
   */
  async getOrder(id: EntityId): Promise<Order> {
    return this.getById<Order>(this.endpoints.BASE, id);
  }

  /**
   * Create a new order
   */
  async createOrder(data: CreateOrderRequest): Promise<Order> {
    return this.post<Order, CreateOrderRequest>(this.endpoints.BASE, data);
  }

  /**
   * Update an existing order
   */
  async updateOrder(id: EntityId, data: UpdateOrderRequest): Promise<Order> {
    return this.put<Order, UpdateOrderRequest>(this.endpoints.BASE, id, data);
  }

  /**
   * Partially update an order
   */
  async patchOrder(id: EntityId, data: Partial<UpdateOrderRequest>): Promise<Order> {
    return this.patch<Order, Partial<UpdateOrderRequest>>(this.endpoints.BASE, id, data);
  }

  /**
   * Cancel an order
   */
  async cancelOrder(id: EntityId, reason?: string): Promise<Order> {
    const data = reason ? { reason } : {};
    return this.post<Order, any>(`${this.endpoints.CANCEL}/${id}`, data);
  }

  // ========================================
  // USER-SPECIFIC OPERATIONS
  // ========================================

  /**
   * Get orders for a specific user (buyer)
   */
  async getUserOrders(userId: EntityId, params?: OrderSearchRequest): Promise<OrderListResponse> {
    const searchParams = {
      ...params,
      user_id: userId,
    };
    return this.getList<Order>(`${this.endpoints.USER_ORDERS}/${userId}`, searchParams);
  }

  /**
   * Get current user's orders
   */
  async getMyOrders(params?: OrderSearchRequest): Promise<OrderListResponse> {
    return this.getList<Order>(`${this.endpoints.USER_ORDERS}/me`, params);
  }

  /**
   * Get orders for a specific vendor
   */
  async getVendorOrders(vendorId: EntityId, params?: OrderSearchRequest): Promise<OrderListResponse> {
    const searchParams = {
      ...params,
      vendor_id: vendorId,
    };
    return this.getList<Order>(`${this.endpoints.VENDOR_ORDERS}/${vendorId}`, searchParams);
  }

  /**
   * Get current vendor's orders
   */
  async getMyVendorOrders(params?: OrderSearchRequest): Promise<OrderListResponse> {
    return this.getList<Order>(`${this.endpoints.VENDOR_ORDERS}/me`, params);
  }

  // ========================================
  // SEARCH AND FILTERING
  // ========================================

  /**
   * Search orders with advanced filters
   */
  async searchOrders(request: OrderSearchRequest): Promise<OrderListResponse> {
    const params = this.buildSearchParams(request);
    return this.getList<Order>(this.endpoints.SEARCH, params);
  }

  /**
   * Get orders by status
   */
  async getOrdersByStatus(status: OrderStatus[], params?: OrderSearchRequest): Promise<OrderListResponse> {
    const searchParams = {
      ...params,
      status: status.join(','),
    };
    return this.getList<Order>(this.endpoints.BASE, searchParams);
  }

  /**
   * Get orders by payment status
   */
  async getOrdersByPaymentStatus(paymentStatus: PaymentStatus[], params?: OrderSearchRequest): Promise<OrderListResponse> {
    const searchParams = {
      ...params,
      payment_status: paymentStatus.join(','),
    };
    return this.getList<Order>(this.endpoints.BASE, searchParams);
  }

  // ========================================
  // STATUS MANAGEMENT
  // ========================================

  /**
   * Update order status
   */
  async updateOrderStatus(id: EntityId, status: OrderStatus, notes?: string): Promise<Order> {
    this.validateEntityId(id);

    const data = {
      status,
      ...(notes && { notes }),
    };

    return this.post<Order, typeof data>(`${this.endpoints.STATUS_UPDATE}/${id}`, data);
  }

  /**
   * Update payment status
   */
  async updatePaymentStatus(id: EntityId, paymentStatus: PaymentStatus, paymentReference?: string): Promise<Order> {
    this.validateEntityId(id);

    const data = {
      payment_status: paymentStatus,
      ...(paymentReference && { payment_reference: paymentReference }),
    };

    return this.post<Order, typeof data>(`${this.endpoints.PAYMENT_UPDATE}/${id}`, data);
  }

  /**
   * Mark order as confirmed
   */
  async confirmOrder(id: EntityId): Promise<Order> {
    return this.updateOrderStatus(id, OrderStatus.CONFIRMED);
  }

  /**
   * Mark order as processing
   */
  async startProcessing(id: EntityId): Promise<Order> {
    return this.updateOrderStatus(id, OrderStatus.PROCESSING);
  }

  /**
   * Mark order as shipped
   */
  async shipOrder(id: EntityId, trackingNumber?: string): Promise<Order> {
    const order = await this.updateOrderStatus(id, OrderStatus.SHIPPED);

    if (trackingNumber) {
      await this.addTrackingNumber(id, trackingNumber);
    }

    return order;
  }

  /**
   * Mark order as delivered
   */
  async markDelivered(id: EntityId): Promise<Order> {
    return this.updateOrderStatus(id, OrderStatus.DELIVERED);
  }

  // ========================================
  // TRACKING AND SHIPPING
  // ========================================

  /**
   * Add tracking number to order
   */
  async addTrackingNumber(id: EntityId, trackingNumber: string): Promise<Order> {
    this.validateEntityId(id);

    const data = { tracking_number: trackingNumber };
    return this.post<Order, typeof data>(`${this.endpoints.TRACKING}/${id}`, data);
  }

  /**
   * Get order tracking information
   */
  async getTrackingInfo(id: EntityId): Promise<any> {
    this.validateEntityId(id);
    return this.get<any>(`${this.endpoints.TRACKING}/${id}`);
  }

  /**
   * Update shipping address
   */
  async updateShippingAddress(id: EntityId, shippingAddress: any): Promise<Order> {
    return this.patch<Order, { shipping_address: any }>(
      this.endpoints.BASE,
      id,
      { shipping_address: shippingAddress }
    );
  }

  // ========================================
  // ADMIN OPERATIONS
  // ========================================

  /**
   * Get all orders for admin dashboard
   */
  async getAdminOrders(params?: OrderSearchRequest): Promise<OrderListResponse> {
    return this.getList<Order>(this.endpoints.ADMIN_ORDERS, params);
  }

  /**
   * Admin force status update
   */
  async adminUpdateStatus(id: EntityId, status: OrderStatus, adminNotes?: string): Promise<Order> {
    this.validateEntityId(id);

    const data = {
      status,
      admin_notes: adminNotes,
    };

    return this.post<Order, typeof data>(`${this.endpoints.ADMIN_ORDERS}/${id}/status`, data);
  }

  /**
   * Admin refund order
   */
  async refundOrder(id: EntityId, refundReason?: string): Promise<Order> {
    this.validateEntityId(id);

    const data = {
      reason: refundReason,
    };

    return this.post<Order, typeof data>(`${this.endpoints.ADMIN_ORDERS}/${id}/refund`, data);
  }

  // ========================================
  // ANALYTICS AND METRICS
  // ========================================

  /**
   * Get order metrics
   */
  async getOrderMetrics(params?: { period?: string; vendor_id?: EntityId }): Promise<any> {
    return this.get<any>(this.endpoints.METRICS, params);
  }

  /**
   * Get vendor order analytics
   */
  async getVendorOrderAnalytics(vendorId: EntityId, period: string = '30d'): Promise<any> {
    const url = `${this.endpoints.VENDOR_ORDERS}/${vendorId}/analytics`;
    return this.get<any>(url, { period });
  }

  /**
   * Get revenue analytics
   */
  async getRevenueAnalytics(params?: {
    period?: string;
    vendor_id?: EntityId;
    group_by?: 'day' | 'week' | 'month'
  }): Promise<any> {
    const url = `${this.endpoints.METRICS}/revenue`;
    return this.get<any>(url, params);
  }

  // ========================================
  // HELPER METHODS
  // ========================================

  /**
   * Build search parameters from OrderSearchRequest
   */
  private buildSearchParams(request: OrderSearchRequest): Record<string, any> {
    const params: Record<string, any> = {};

    if (request.user_id) params.user_id = request.user_id;
    if (request.vendor_id) params.vendor_id = request.vendor_id;
    if (request.status && request.status.length > 0) params.status = request.status.join(',');
    if (request.payment_status && request.payment_status.length > 0) {
      params.payment_status = request.payment_status.join(',');
    }
    if (request.payment_method && request.payment_method.length > 0) {
      params.payment_method = request.payment_method.join(',');
    }
    if (request.order_number) params.order_number = request.order_number;
    if (request.customer_email) params.customer_email = request.customer_email;
    if (request.date_from) params.date_from = request.date_from;
    if (request.date_to) params.date_to = request.date_to;
    if (request.min_amount !== undefined) params.min_amount = request.min_amount;
    if (request.max_amount !== undefined) params.max_amount = request.max_amount;
    if (request.sort_by) params.sort_by = request.sort_by;
    if (request.sort_order) params.sort_order = request.sort_order;
    if (request.page) params.page = request.page;
    if (request.limit) params.limit = request.limit;

    return params;
  }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

/**
 * Default order API service instance
 */
export const orderApiService = new OrderApiService();

// ========================================
// EXPORTS
// ========================================

export { OrderApiService };
export default orderApiService;