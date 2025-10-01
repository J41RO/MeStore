import axios from 'axios';
import type { CartItem, ShippingAddress, PaymentInfo } from '../stores/checkoutStore';
import type { CategoryListResponse } from '../types/category.types';

// Configuración base de axios - SIEMPRE usar backend directo (proxy de Vite no funciona en network IP)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000';

const baseApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // REMOVIDO: 'User-Agent' - No permitido en navegadores (causa error "Refused to set unsafe header")
  }
});

baseApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error response interceptor
baseApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth tokens on 401
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      // Redirect to login or trigger auth state update
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ===== TYPE DEFINITIONS =====

export interface CreateOrderRequest {
  items: Array<{
    product_id: string;
    quantity: number;
    variant_attributes?: Record<string, string>;
  }>;
  shipping_name: string;
  shipping_phone: string;
  shipping_email?: string;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code?: string;
  notes?: string;
}

export interface OrderResponse {
  id: string;
  order_number: string;
  status: string;
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  discount_amount: number;
  total_amount: number;
  shipping_address: string;
  shipping_city: string;
  shipping_state: string;
  notes?: string;
  created_at: string;
  items: Array<{
    id: string;
    product_id: string;
    product_name: string;
    product_sku: string;
    product_image_url?: string;
    unit_price: number;
    quantity: number;
    total_price: number;
    variant_attributes?: Record<string, string>;
  }>;
  is_paid: boolean;
  payment_status?: string;
}

export interface PaymentProcessRequest {
  order_id: number;
  payment_method: string;
  payment_data: {
    payment_source_id?: string;
    card_number?: string;
    card_holder?: string;
    expiration_month?: string;
    expiration_year?: string;
    cvv?: string;
    installments?: number;
    redirect_url?: string;
    // PSE specific
    bank_code?: string;
    user_type?: 'natural' | 'juridical';
    identification_type?: 'CC' | 'CE' | 'NIT' | 'TI' | 'PP';
    identification_number?: string;
  };
  save_payment_method?: boolean;
}

export interface PaymentProcessResponse {
  success: boolean;
  order_id: number;
  transaction_id: string;
  wompi_transaction_id?: string;
  status: string;
  payment_url?: string;
  fraud_score: number;
  message?: string;
}

export interface PaymentMethod {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  description?: string;
}

// ===== AUTHENTICATION API =====
export const authAPI = {
  login: (credentials: any) => baseApi.post('/api/v1/auth/login', credentials),
  register: (userData: any) => baseApi.post('/api/v1/auth/register', userData),
  refresh: (refreshToken: string) => baseApi.post('/api/v1/auth/refresh-token', { refresh_token: refreshToken }),
  logout: () => baseApi.post('/api/v1/auth/logout'),
  getProfile: () => baseApi.get('/api/v1/auth/me')
};

// ===== PRODUCTS API =====
export const productsAPI = {
  getAll: (params?: any) => baseApi.get('/api/v1/products/', { params }),
  getById: (id: string) => baseApi.get(`/api/v1/products/${id}`),
  create: (data: any) => baseApi.post('/api/v1/products/', data),
  update: (id: string, data: any) => baseApi.put(`/api/v1/products/${id}`, data),
  getWithFilters: (filters: any) => baseApi.get('/api/v1/products/', { params: filters }),
  // Additional product endpoints
  search: (query: string, filters?: any) => baseApi.get('/api/v1/search/products', {
    params: { q: query, ...filters }
  }),
  getCategories: (): Promise<{ data: CategoryListResponse }> => baseApi.get('/api/v1/categories/'),
  getByCategory: (categoryId: string, params?: any) => baseApi.get(`/api/v1/products/category/${categoryId}`, { params })
};

// ===== ORDERS API =====
export const ordersAPI = {
  create: (orderData: CreateOrderRequest): Promise<{ data: OrderResponse }> =>
    baseApi.post('/api/v1/orders/', orderData),

  getAll: (params?: { skip?: number; limit?: number; status_filter?: string }) =>
    baseApi.get('/api/v1/orders/', { params }),

  getById: (orderId: string): Promise<{ data: OrderResponse }> =>
    baseApi.get(`/api/v1/orders/${orderId}`),

  cancel: (orderId: string) =>
    baseApi.patch(`/api/v1/orders/${orderId}/cancel`),

  // Public tracking (no auth required)
  trackPublic: (orderNumber: string) =>
    axios.get(`${API_BASE_URL}/api/v1/orders/track/${orderNumber}`),

  // Detailed tracking (auth required)
  trackDetailed: (orderNumber: string) =>
    baseApi.get(`/api/v1/orders/track/${orderNumber}/detailed`),

  // Generate tracking token
  generateTrackingToken: (orderNumber: string, email: string) =>
    axios.post(`${API_BASE_URL}/api/v1/orders/tracking/generate-token`, {
      order_number: orderNumber,
      email: email
    }),

  // Get tracking config
  getTrackingConfig: () =>
    axios.get(`${API_BASE_URL}/api/v1/orders/tracking/config`)
};

// ===== PAYMENTS API =====
export const paymentsAPI = {
  process: (paymentData: PaymentProcessRequest): Promise<{ data: PaymentProcessResponse }> =>
    baseApi.post('/api/v1/payments/process', paymentData),

  getStatus: (orderId: number) =>
    baseApi.get(`/api/v1/payments/status/${orderId}`),

  getMethods: (): Promise<{ data: PaymentMethod[] }> =>
    baseApi.get('/api/v1/payments/methods'),

  // Health check
  healthCheck: () =>
    baseApi.get('/api/v1/payments/health'),

  // Webhook endpoint (for internal use)
  webhook: (webhookData: any) =>
    axios.post(`${API_BASE_URL}/api/v1/payments/webhook`, webhookData)
};

// ===== USERS API =====
export const usersAPI = {
  getProfile: () => baseApi.get('/api/v1/profile'),
  updateProfile: (profileData: any) => baseApi.put('/api/v1/profile', profileData),
  getAddresses: () => baseApi.get('/api/v1/profile/addresses'),
  createAddress: (address: ShippingAddress) => baseApi.post('/api/v1/profile/addresses', address),
  updateAddress: (addressId: string, address: ShippingAddress) =>
    baseApi.put(`/api/v1/profile/addresses/${addressId}`, address),
  deleteAddress: (addressId: string) => baseApi.delete(`/api/v1/profile/addresses/${addressId}`)
};

// ===== MARKETPLACE API =====
export const marketplaceAPI = {
  getFeatured: () => baseApi.get('/api/v1/marketplace/featured'),
  getDeals: () => baseApi.get('/api/v1/marketplace/deals'),
  getNewArrivals: () => baseApi.get('/api/v1/marketplace/new-arrivals'),
  getTopRated: () => baseApi.get('/api/v1/marketplace/top-rated'),
  getBestSellers: () => baseApi.get('/api/v1/marketplace/best-sellers')
};

// ===== SEARCH API =====
export const searchAPI = {
  products: (query: string, filters?: any) =>
    baseApi.get('/api/v1/search/products', { params: { q: query, ...filters } }),
  vendors: (query: string) =>
    baseApi.get('/api/v1/search/vendors', { params: { q: query } }),
  suggestions: (query: string) =>
    baseApi.get('/api/v1/search/suggestions', { params: { q: query } })
};

// ===== UTILITY FUNCTIONS =====

/**
 * Convert CartItem to order item format
 */
export const convertCartItemToOrderItem = (item: CartItem) => ({
  product_id: item.product_id,
  quantity: item.quantity,
  variant_attributes: item.variant_attributes
});

/**
 * Convert ShippingAddress to order shipping format
 */
export const convertShippingAddressToOrder = (address: ShippingAddress) => ({
  shipping_name: address.name,
  shipping_phone: address.phone,
  shipping_address: address.address,
  shipping_city: address.city,
  shipping_state: address.department || '',
  shipping_postal_code: address.postal_code
});

/**
 * Convert PaymentInfo to payment process format
 */
export const convertPaymentInfoToProcess = (paymentInfo: PaymentInfo, orderId: number): PaymentProcessRequest => ({
  order_id: orderId,
  payment_method: paymentInfo.method,
  payment_data: {
    // PSE specific
    bank_code: paymentInfo.bank_code,
    user_type: paymentInfo.user_type,
    identification_type: paymentInfo.identification_type,
    identification_number: paymentInfo.identification_number,

    // Credit card specific
    card_number: paymentInfo.card_number,
    card_holder: paymentInfo.card_holder_name,
    expiration_month: paymentInfo.expiry_month,
    expiration_year: paymentInfo.expiry_year,
    cvv: paymentInfo.cvv,

    // Common
    redirect_url: `${window.location.origin}/checkout/confirmation`
  },
  save_payment_method: false
});

// ===== CHECKOUT WORKFLOW API =====
export const checkoutAPI = {
  /**
   * Complete checkout process: create order and process payment
   */
  async completeCheckout(
    cartItems: CartItem[],
    shippingAddress: ShippingAddress,
    paymentInfo: PaymentInfo,
    orderNotes?: string
  ): Promise<{ order: OrderResponse; payment: PaymentProcessResponse }> {
    try {
      // 1. Create order
      const orderData: CreateOrderRequest = {
        items: cartItems.map(convertCartItemToOrderItem),
        notes: orderNotes,
        ...convertShippingAddressToOrder(shippingAddress),
        shipping_email: paymentInfo.email
      };

      const orderResponse = await ordersAPI.create(orderData);
      const order = orderResponse.data;

      // 2. Process payment
      const paymentData = convertPaymentInfoToProcess(paymentInfo, parseInt(order.id));
      const paymentResponse = await paymentsAPI.process(paymentData);
      const payment = paymentResponse.data;

      return { order, payment };
    } catch (error) {
      console.error('Checkout process failed:', error);
      throw error;
    }
  },

  /**
   * Validate checkout data before processing
   */
  validateCheckoutData(
    cartItems: CartItem[],
    shippingAddress: ShippingAddress,
    paymentInfo: PaymentInfo
  ): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate cart
    if (!cartItems.length) {
      errors.push('Cart is empty');
    }

    // Validate shipping
    if (!shippingAddress.name) errors.push('Shipping name is required');
    if (!shippingAddress.phone) errors.push('Shipping phone is required');
    if (!shippingAddress.address) errors.push('Shipping address is required');
    if (!shippingAddress.city) errors.push('Shipping city is required');

    // Validate payment
    if (!paymentInfo.method) errors.push('Payment method is required');

    if (paymentInfo.method === 'pse') {
      if (!paymentInfo.bank_code) errors.push('Bank selection is required for PSE');
      if (!paymentInfo.identification_type) errors.push('Identification type is required');
      if (!paymentInfo.identification_number) errors.push('Identification number is required');
      if (!paymentInfo.user_type) errors.push('User type is required');
    }

    if (paymentInfo.method === 'credit_card') {
      if (!paymentInfo.card_number) errors.push('Card number is required');
      if (!paymentInfo.card_holder_name) errors.push('Card holder name is required');
      if (!paymentInfo.expiry_month) errors.push('Expiry month is required');
      if (!paymentInfo.expiry_year) errors.push('Expiry year is required');
      if (!paymentInfo.cvv) errors.push('CVV is required');
    }

    return { valid: errors.length === 0, errors };
  }
};

// ===== MAIN API OBJECT =====
const api = Object.assign(baseApi, {
  auth: authAPI,
  users: usersAPI,
  products: productsAPI,
  orders: ordersAPI,
  payments: paymentsAPI,
  marketplace: marketplaceAPI,
  search: searchAPI,
  checkout: checkoutAPI
});

export default api;