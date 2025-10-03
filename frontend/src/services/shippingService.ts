/**
 * Shipping Service - Order tracking and shipping management
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://192.168.1.137:8000';

// Types
export enum ShippingStatus {
  IN_TRANSIT = 'in_transit',
  AT_WAREHOUSE = 'at_warehouse',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  DELIVERED = 'delivered',
  RETURNED = 'returned',
  FAILED = 'failed'
}

export interface ShippingEvent {
  timestamp: string;
  status: ShippingStatus;
  location: string;
  description?: string;
}

export interface ShippingInfo {
  tracking_number: string | null;
  courier: string | null;
  estimated_delivery: string | null;
  shipping_events: ShippingEvent[];
  current_status: ShippingStatus | null;
}

export interface TrackingResponse {
  order_number: string;
  order_status: string;
  shipping_info: ShippingInfo;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  created_at: string;
  shipped_at: string | null;
  delivered_at: string | null;
}

export interface ShippingAssignment {
  courier: string;
  estimated_days: number;
}

export interface ShippingLocationUpdate {
  current_location: string;
  status: ShippingStatus;
  description?: string;
}

// API Service
class ShippingService {
  /**
   * Assign shipping to an order (Admin only)
   */
  async assignShipping(orderId: number, data: ShippingAssignment): Promise<any> {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/shipping/orders/${orderId}/shipping`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  }

  /**
   * Update shipping location (Admin only)
   */
  async updateShippingLocation(orderId: number, data: ShippingLocationUpdate): Promise<any> {
    const token = localStorage.getItem('access_token');
    const response = await axios.patch(
      `${API_BASE_URL}/api/v1/shipping/orders/${orderId}/shipping/location`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  }

  /**
   * Get shipping tracking information (Authenticated users)
   */
  async getShippingTracking(orderId: number): Promise<TrackingResponse> {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/shipping/orders/${orderId}/shipping/tracking`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
    return response.data;
  }

  /**
   * Track by tracking number (Public endpoint - no auth required)
   */
  async trackByNumber(trackingNumber: string): Promise<TrackingResponse> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/shipping/tracking/${trackingNumber}`
    );
    return response.data;
  }

  /**
   * Get available couriers
   */
  getAvailableCouriers(): string[] {
    return [
      'Rappi',
      'Coordinadora',
      'Servientrega',
      'Interrapidisimo',
      'Envia',
      'Otro'
    ];
  }

  /**
   * Get shipping status display text (Spanish)
   */
  getStatusDisplayText(status: ShippingStatus | string): string {
    const statusMap: Record<string, string> = {
      [ShippingStatus.IN_TRANSIT]: 'En tránsito',
      [ShippingStatus.AT_WAREHOUSE]: 'En bodega',
      [ShippingStatus.OUT_FOR_DELIVERY]: 'En reparto',
      [ShippingStatus.DELIVERED]: 'Entregado',
      [ShippingStatus.RETURNED]: 'Devuelto',
      [ShippingStatus.FAILED]: 'Fallido'
    };
    return statusMap[status] || status;
  }

  /**
   * Get shipping status color for UI
   */
  getStatusColor(status: ShippingStatus | string): string {
    const colorMap: Record<string, string> = {
      [ShippingStatus.IN_TRANSIT]: 'blue',
      [ShippingStatus.AT_WAREHOUSE]: 'orange',
      [ShippingStatus.OUT_FOR_DELIVERY]: 'purple',
      [ShippingStatus.DELIVERED]: 'green',
      [ShippingStatus.RETURNED]: 'red',
      [ShippingStatus.FAILED]: 'red'
    };
    return colorMap[status] || 'gray';
  }

  /**
   * Format date for display
   */
  formatDate(dateString: string | null): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }

  /**
   * Calculate days until delivery
   */
  getDaysUntilDelivery(estimatedDelivery: string | null): number | null {
    if (!estimatedDelivery) return null;
    const now = new Date();
    const delivery = new Date(estimatedDelivery);
    const diffTime = delivery.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }
}

export const shippingService = new ShippingService();
export default shippingService;
