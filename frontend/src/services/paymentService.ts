/**
 * Payment Service - Frontend
 * Handles payment processing, status tracking, and payment method management
 */

export interface PaymentRequest {
  order_id: number;
  payment_method: 'pse' | 'credit_card' | 'bank_transfer' | 'cash_on_delivery';
  payment_data: {
    // PSE specific
    user_type?: string;
    user_legal_id?: string;
    financial_institution_code?: string;
    payment_description?: string;

    // Credit card specific
    card_number?: string;
    card_holder?: string;
    expiration_month?: string;
    expiration_year?: string;
    cvv?: string;
    installments?: number;

    // Common
    redirect_url?: string;
  };
  save_payment_method?: boolean;
}

export interface PaymentResponse {
  success: boolean;
  order_id: number;
  transaction_id: string;
  wompi_transaction_id?: string;
  status: string;
  payment_url?: string;
  fraud_score: number;
  message?: string;
}

export interface PaymentStatusResponse {
  order_id: number;
  order_status: string;
  payment_status: string;
  transaction_id?: string;
  wompi_transaction_id?: string;
  amount: number;
  last_updated?: string;
}

export interface PaymentMethod {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  description?: string;
}

class PaymentService {
  private baseUrl = '/api/v1/payments';

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Process a payment for an order
   */
  async processPayment(paymentRequest: PaymentRequest): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/process`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(paymentRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || errorData.detail || 'Error procesando el pago');
      }

      return await response.json();
    } catch (error) {
      console.error('Payment processing error:', error);
      throw error;
    }
  }

  /**
   * Get payment status for an order
   */
  async getPaymentStatus(orderId: number): Promise<PaymentStatusResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/status/${orderId}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error obteniendo estado del pago');
      }

      return await response.json();
    } catch (error) {
      console.error('Payment status error:', error);
      throw error;
    }
  }

  /**
   * Get available payment methods
   */
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    try {
      const response = await fetch(`${this.baseUrl}/methods`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error obteniendo métodos de pago');
      }

      return await response.json();
    } catch (error) {
      console.error('Payment methods error:', error);
      throw error;
    }
  }

  /**
   * Poll payment status until completion or timeout
   */
  async pollPaymentStatus(
    orderId: number,
    onStatusUpdate?: (status: PaymentStatusResponse) => void,
    maxPolls: number = 30,
    pollInterval: number = 2000
  ): Promise<PaymentStatusResponse> {
    for (let i = 0; i < maxPolls; i++) {
      try {
        const status = await this.getPaymentStatus(orderId);

        if (onStatusUpdate) {
          onStatusUpdate(status);
        }

        // Stop polling if payment is in final state
        if (['APPROVED', 'DECLINED', 'ERROR', 'CANCELLED'].includes(status.payment_status)) {
          return status;
        }

        // Wait before next poll
        if (i < maxPolls - 1) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
      } catch (error) {
        console.error(`Payment status poll ${i + 1} failed:`, error);
        if (i === maxPolls - 1) {
          throw error;
        }
      }
    }

    throw new Error('Payment status polling timeout');
  }

  /**
   * Create a WebSocket connection for real-time payment updates
   */
  createPaymentStatusSocket(orderId: number, onStatusUpdate: (status: PaymentStatusResponse) => void): WebSocket | null {
    try {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/payments/${orderId}?token=${token}`;

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('Payment status WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const status = JSON.parse(event.data);
          onStatusUpdate(status);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Payment status WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('Payment status WebSocket disconnected');
      };

      return ws;
    } catch (error) {
      console.error('Error creating payment status WebSocket:', error);
      return null;
    }
  }

  /**
   * Get health status of payment service
   */
  async getHealthStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Payment service health check failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Payment service health check error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const paymentService = new PaymentService();
export default paymentService;