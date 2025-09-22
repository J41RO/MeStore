// Mock API service for tests
// Prevents real HTTP calls during testing

// Mock data
const mockProducts = [
  {
    id: '1',
    name: 'Test Product 1',
    price: 50000,
    stock: 10,
    vendor_id: 'vendor-1',
    sku: 'TEST-001',
  },
  {
    id: '2',
    name: 'Test Product 2',
    price: 30000,
    stock: 5,
    vendor_id: 'vendor-2',
    sku: 'TEST-002',
  },
];

const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'buyer',
};

const mockVendor = {
  id: 'vendor-123',
  business_name: 'Test Vendor',
  email: 'vendor@example.com',
  status: 'active',
};

// Create mock axios instance
const mockAxiosInstance = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  patch: jest.fn(),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn() },
  },
  defaults: {
    baseURL: 'http://localhost:8000/api/v1',
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
  },
};

// Default successful responses
mockAxiosInstance.get.mockImplementation((url: string) => {
  if (url.includes('/products')) {
    return Promise.resolve({ data: mockProducts });
  }
  if (url.includes('/users/profile')) {
    return Promise.resolve({ data: mockUser });
  }
  if (url.includes('/vendedores')) {
    return Promise.resolve({ data: mockVendor });
  }
  return Promise.resolve({ data: {} });
});

mockAxiosInstance.post.mockImplementation((url: string, data: any) => {
  if (url.includes('/auth/login')) {
    return Promise.resolve({
      data: {
        access_token: 'mock-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser,
      },
    });
  }
  if (url.includes('/orders')) {
    return Promise.resolve({
      data: {
        id: 'order-123',
        order_number: 'ORD-123',
        status: 'pending',
        total_amount: 80000,
      },
    });
  }
  if (url.includes('/payments/process')) {
    return Promise.resolve({
      data: {
        success: true,
        transaction_id: 'txn-123',
        payment_url: 'https://mock-payment.com/pay/123',
      },
    });
  }
  return Promise.resolve({ data: { success: true } });
});

mockAxiosInstance.put.mockResolvedValue({ data: { success: true } });
mockAxiosInstance.delete.mockResolvedValue({ data: { success: true } });

// API modules mock
const mockAPI = {
  // Auth methods
  auth: {
    login: jest.fn().mockImplementation((credentials) =>
      mockAxiosInstance.post('/auth/login', credentials)
    ),
    register: jest.fn().mockImplementation((userData) =>
      mockAxiosInstance.post('/auth/register', userData)
    ),
    refresh: jest.fn().mockImplementation((refreshToken) =>
      mockAxiosInstance.post('/auth/refresh', { refresh_token: refreshToken })
    ),
    logout: jest.fn().mockResolvedValue({ data: { success: true } }),
  },

  // Users methods
  users: {
    getProfile: jest.fn().mockImplementation(() =>
      mockAxiosInstance.get('/users/profile')
    ),
    updateProfile: jest.fn().mockImplementation((profileData) =>
      mockAxiosInstance.put('/users/profile', profileData)
    ),
  },

  // Products methods
  products: {
    getAll: jest.fn().mockImplementation(() =>
      mockAxiosInstance.get('/products')
    ),
    getById: jest.fn().mockImplementation((id) =>
      mockAxiosInstance.get(`/products/${id}`)
    ),
    create: jest.fn().mockImplementation((data) =>
      mockAxiosInstance.post('/productos', data)
    ),
    update: jest.fn().mockImplementation((id, data) =>
      mockAxiosInstance.put(`/productos/${id}`, data)
    ),
    getWithFilters: jest.fn().mockImplementation((filters) =>
      mockAxiosInstance.get('/productos', { params: filters })
    ),
  },

  // Orders methods
  orders: {
    create: jest.fn().mockImplementation((orderData) =>
      mockAxiosInstance.post('/orders', orderData)
    ),
    getById: jest.fn().mockImplementation((id) =>
      mockAxiosInstance.get(`/orders/${id}`)
    ),
    trackPublic: jest.fn().mockImplementation((orderNumber) =>
      Promise.resolve({
        data: {
          success: true,
          data: {
            order_number: orderNumber,
            status: 'shipped',
            tracking_number: 'TRK-123456',
          },
        },
      })
    ),
  },

  // Payments methods
  payments: {
    process: jest.fn().mockImplementation((paymentData) =>
      mockAxiosInstance.post('/payments/process', paymentData)
    ),
    getMethods: jest.fn().mockImplementation(() =>
      Promise.resolve({
        data: [
          { id: 'pse', name: 'PSE', type: 'bank_transfer', enabled: true },
          { id: 'credit_card', name: 'Tarjeta de Crédito', type: 'card', enabled: true },
        ],
      })
    ),
    getStatus: jest.fn().mockImplementation((orderId) =>
      Promise.resolve({
        data: {
          order_id: orderId,
          order_status: 'confirmed',
          payment_status: 'approved',
          amount: 130000,
        },
      })
    ),
  },

  // Checkout methods
  checkout: {
    completeCheckout: jest.fn().mockImplementation(
      (cartItems, shippingAddress, paymentInfo, notes) =>
        Promise.resolve({
          order: {
            id: 'order-123',
            order_number: 'ORD-123',
            status: 'pending',
            total_amount: 130000,
          },
          payment: {
            success: true,
            transaction_id: 'txn-123',
            payment_url: 'https://mock-payment.com/pay/123',
          },
        })
    ),
    validateCheckoutData: jest.fn().mockReturnValue({
      valid: true,
      errors: [],
    }),
  },

  // Base axios methods
  get: mockAxiosInstance.get,
  post: mockAxiosInstance.post,
  put: mockAxiosInstance.put,
  delete: mockAxiosInstance.delete,
  patch: mockAxiosInstance.patch,
  interceptors: mockAxiosInstance.interceptors,
  defaults: mockAxiosInstance.defaults,
};

// Helper functions
export const convertCartItemToOrderItem = jest.fn().mockImplementation((cartItem) => ({
  product_id: cartItem.product_id,
  quantity: cartItem.quantity,
  variant_attributes: cartItem.variant_attributes,
}));

export const convertShippingAddressToOrder = jest.fn().mockImplementation((address) => ({
  shipping_name: address.name,
  shipping_phone: address.phone,
  shipping_address: address.address,
  shipping_city: address.city,
  shipping_state: address.department,
  shipping_postal_code: address.postal_code,
}));

export const convertPaymentInfoToProcess = jest.fn().mockImplementation((paymentInfo, orderId) => ({
  order_id: orderId,
  payment_method: paymentInfo.method,
  payment_data: {
    bank_code: paymentInfo.bank_code,
    user_type: paymentInfo.user_type,
    identification_type: paymentInfo.identification_type,
    identification_number: paymentInfo.identification_number,
    card_number: paymentInfo.card_number,
    card_holder: paymentInfo.card_holder_name,
    expiration_month: paymentInfo.expiry_month,
    expiration_year: paymentInfo.expiry_year,
    cvv: paymentInfo.cvv,
    redirect_url: `${window.location.origin}/checkout/confirmation`,
  },
  save_payment_method: false,
}));

// Export individual API sections
export const authAPI = mockAPI.auth;
export const usersAPI = mockAPI.users;
export const productsAPI = mockAPI.products;
export const ordersAPI = mockAPI.orders;
export const paymentsAPI = mockAPI.payments;
export const checkoutAPI = mockAPI.checkout;

// Export main API object as default
export default mockAPI;

// Reset function for tests
export const resetMocks = () => {
  Object.values(mockAPI).forEach((apiSection: any) => {
    if (typeof apiSection === 'object') {
      Object.values(apiSection).forEach((method: any) => {
        if (jest.isMockFunction(method)) {
          method.mockClear();
        }
      });
    }
  });
  Object.values(mockAxiosInstance).forEach((method: any) => {
    if (jest.isMockFunction(method)) {
      method.mockClear();
    }
  });
};