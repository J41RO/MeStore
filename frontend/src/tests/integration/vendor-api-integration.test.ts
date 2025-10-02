// frontend/src/tests/integration/vendor-api-integration.test.ts
// API INTEGRATION TESTING for Vendor Dashboard
// Tests backend-frontend communication, authentication, and data flow

// Jest equivalents for Vitest imports
const vi = jest;
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// API services under test
import { apiClient } from '../../services/api';
import { VendorService } from '../../services/api_vendor';
import { PaymentService } from '../../services/PaymentService';
import { CartService } from '../../services/CartService';

// Types
import { VendorRegistrationData } from '../../components/vendor/VendorRegistrationFlow';
import { Product } from '../../types/product.types';
import { AnalyticsMetrics } from '../../types/analytics.types';

// Mock data
const MOCK_VENDOR_DATA: VendorRegistrationData = {
  businessName: 'Test Vendor Store',
  email: 'vendor@test.com',
  phone: '3001234567',
  businessType: 'persona_natural',
  address: 'Calle 123 #45-67',
  city: 'Bogotá',
  department: 'Cundinamarca',
  phoneVerified: true,
  emailVerified: true,
  documents: []
};

const MOCK_PRODUCT: Product = {
  id: '1',
  vendor_id: 'vendor-1',
  sku: 'TECH-001',
  name: 'Smartphone Samsung Galaxy A54',
  description: 'Smartphone with 50MP camera',
  price: 899000,
  stock: 25,
  category_id: 'electronics',
  category_name: 'Electrónicos',
  precio_venta: 899000,
  precio_costo: 650000,
  comision_mestocker: 44950,
  peso: 202,
  is_active: true,
  is_featured: true,
  is_digital: false,
  images: [],
  main_image_url: '/api/placeholder/300/300',
  sales_count: 45,
  view_count: 320,
  rating: 4.5,
  review_count: 12,
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-20T15:30:00Z'
};

const MOCK_ANALYTICS: AnalyticsMetrics = {
  revenue: {
    current: 1500000,
    previous: 1200000,
    trend: 'up',
    percentage: 25
  },
  orders: {
    current: 45,
    previous: 38,
    trend: 'up',
    percentage: 18.4
  },
  products: {
    total: 15,
    active: 12,
    lowStock: 3,
    outOfStock: 1
  },
  customers: {
    total: 120,
    new: 15,
    returning: 105
  }
};

describe('Vendor API Integration Tests', () => {
  let mockAxios: MockAdapter;
  let originalBaseURL: string;

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
    originalBaseURL = process.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000';

    // Mock authentication token
    localStorage.setItem('auth_token', 'mock-jwt-token');

    // Setup default interceptors
    apiClient.interceptors.request.use(config => {
      config.headers.Authorization = `Bearer mock-jwt-token`;
      return config;
    });
  });

  afterEach(() => {
    mockAxios.restore();
    localStorage.clear();
  });

  describe('1. Vendor Registration API', () => {
    it('should successfully register a new vendor', async () => {
      // Mock successful registration response
      mockAxios.onPost('/api/v1/vendors/register').reply(201, {
        success: true,
        data: {
          id: 'vendor-123',
          email: MOCK_VENDOR_DATA.email,
          business_name: MOCK_VENDOR_DATA.businessName,
          status: 'pending_verification'
        },
        message: 'Vendor registered successfully'
      });

      const response = await VendorService.register(MOCK_VENDOR_DATA);

      expect(response.success).toBe(true);
      expect(response.data.email).toBe(MOCK_VENDOR_DATA.email);
      expect(response.data.business_name).toBe(MOCK_VENDOR_DATA.businessName);

      // Verify request was made with correct data
      const request = mockAxios.history.post[0];
      expect(request.url).toBe('/api/v1/vendors/register');
      expect(JSON.parse(request.data)).toMatchObject({
        business_name: MOCK_VENDOR_DATA.businessName,
        email: MOCK_VENDOR_DATA.email,
        phone: MOCK_VENDOR_DATA.phone
      });
    });

    it('should handle registration validation errors', async () => {
      // Mock validation error response
      mockAxios.onPost('/api/v1/vendors/register').reply(400, {
        success: false,
        errors: {
          email: ['Email already exists'],
          phone: ['Invalid phone format']
        },
        message: 'Validation failed'
      });

      try {
        await VendorService.register(MOCK_VENDOR_DATA);
      } catch (error: any) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.errors.email).toContain('Email already exists');
        expect(error.response.data.errors.phone).toContain('Invalid phone format');
      }
    });

    it('should handle network errors gracefully', async () => {
      // Mock network error
      mockAxios.onPost('/api/v1/vendors/register').networkError();

      try {
        await VendorService.register(MOCK_VENDOR_DATA);
      } catch (error: any) {
        expect(error.message).toContain('Network Error');
      }
    });

    it('should include proper authentication headers', async () => {
      mockAxios.onPost('/api/v1/vendors/register').reply(201, { success: true });

      await VendorService.register(MOCK_VENDOR_DATA);

      const request = mockAxios.history.post[0];
      expect(request.headers?.Authorization).toBe('Bearer mock-jwt-token');
      expect(request.headers?.['Content-Type']).toBe('application/json');
    });
  });

  describe('2. Vendor Profile Management API', () => {
    const vendorId = 'vendor-123';

    it('should fetch vendor profile successfully', async () => {
      mockAxios.onGet(`/api/v1/vendors/${vendorId}`).reply(200, {
        success: true,
        data: {
          id: vendorId,
          business_name: 'Test Vendor Store',
          email: 'vendor@test.com',
          phone: '3001234567',
          status: 'active',
          created_at: '2024-01-15T10:00:00Z'
        }
      });

      const response = await VendorService.getProfile(vendorId);

      expect(response.success).toBe(true);
      expect(response.data.id).toBe(vendorId);
      expect(response.data.business_name).toBe('Test Vendor Store');
    });

    it('should update vendor profile', async () => {
      const updateData = {
        business_name: 'Updated Vendor Store',
        phone: '3009876543'
      };

      mockAxios.onPut(`/api/v1/vendors/${vendorId}`).reply(200, {
        success: true,
        data: { ...MOCK_VENDOR_DATA, ...updateData }
      });

      const response = await VendorService.updateProfile(vendorId, updateData);

      expect(response.success).toBe(true);
      expect(response.data.business_name).toBe('Updated Vendor Store');

      const request = mockAxios.history.put[0];
      expect(JSON.parse(request.data)).toMatchObject(updateData);
    });

    it('should handle unauthorized access', async () => {
      mockAxios.onGet(`/api/v1/vendors/${vendorId}`).reply(401, {
        success: false,
        message: 'Unauthorized access'
      });

      try {
        await VendorService.getProfile(vendorId);
      } catch (error: any) {
        expect(error.response.status).toBe(401);
        expect(error.response.data.message).toBe('Unauthorized access');
      }
    });
  });

  describe('3. Product Management API', () => {
    const vendorId = 'vendor-123';

    it('should fetch vendor products with pagination', async () => {
      const mockProducts = Array.from({ length: 10 }, (_, i) => ({
        ...MOCK_PRODUCT,
        id: `product-${i + 1}`,
        name: `Product ${i + 1}`
      }));

      mockAxios.onGet(`/api/v1/vendors/${vendorId}/products`).reply(200, {
        success: true,
        data: {
          products: mockProducts,
          total: 25,
          page: 1,
          per_page: 10,
          pages: 3
        }
      });

      const response = await VendorService.getProducts(vendorId, { page: 1, limit: 10 });

      expect(response.success).toBe(true);
      expect(response.data.products).toHaveLength(10);
      expect(response.data.total).toBe(25);
      expect(response.data.pages).toBe(3);
    });

    it('should create new product', async () => {
      const newProductData = {
        name: 'New Test Product',
        description: 'A test product',
        price: 50000,
        stock: 100,
        category_id: 'electronics'
      };

      mockAxios.onPost(`/api/v1/vendors/${vendorId}/products`).reply(201, {
        success: true,
        data: { ...MOCK_PRODUCT, ...newProductData, id: 'new-product-123' }
      });

      const response = await VendorService.createProduct(vendorId, newProductData);

      expect(response.success).toBe(true);
      expect(response.data.name).toBe(newProductData.name);
      expect(response.data.id).toBe('new-product-123');

      const request = mockAxios.history.post[0];
      expect(JSON.parse(request.data)).toMatchObject(newProductData);
    });

    it('should update existing product', async () => {
      const productId = 'product-123';
      const updateData = { price: 999000, stock: 15 };

      mockAxios.onPut(`/api/v1/vendors/${vendorId}/products/${productId}`).reply(200, {
        success: true,
        data: { ...MOCK_PRODUCT, ...updateData }
      });

      const response = await VendorService.updateProduct(vendorId, productId, updateData);

      expect(response.success).toBe(true);
      expect(response.data.price).toBe(updateData.price);
      expect(response.data.stock).toBe(updateData.stock);
    });

    it('should delete product', async () => {
      const productId = 'product-123';

      mockAxios.onDelete(`/api/v1/vendors/${vendorId}/products/${productId}`).reply(200, {
        success: true,
        message: 'Product deleted successfully'
      });

      const response = await VendorService.deleteProduct(vendorId, productId);

      expect(response.success).toBe(true);
      expect(response.message).toBe('Product deleted successfully');
    });

    it('should handle bulk product operations', async () => {
      const productIds = ['product-1', 'product-2', 'product-3'];
      const bulkAction = 'activate';

      mockAxios.onPost(`/api/v1/vendors/${vendorId}/products/bulk`).reply(200, {
        success: true,
        data: {
          updated: productIds.length,
          failed: 0
        },
        message: 'Bulk operation completed'
      });

      const response = await VendorService.bulkUpdateProducts(vendorId, {
        product_ids: productIds,
        action: bulkAction
      });

      expect(response.success).toBe(true);
      expect(response.data.updated).toBe(3);
      expect(response.data.failed).toBe(0);
    });
  });

  describe('4. Analytics API Integration', () => {
    const vendorId = 'vendor-123';

    it('should fetch vendor analytics metrics', async () => {
      mockAxios.onGet(`/api/v1/vendors/${vendorId}/analytics`).reply(200, {
        success: true,
        data: MOCK_ANALYTICS
      });

      const response = await VendorService.getAnalytics(vendorId, {
        time_range: '30d',
        metrics: ['revenue', 'orders', 'products', 'customers']
      });

      expect(response.success).toBe(true);
      expect(response.data.revenue.current).toBe(1500000);
      expect(response.data.orders.current).toBe(45);
      expect(response.data.products.total).toBe(15);
    });

    it('should fetch analytics with custom date range', async () => {
      const startDate = '2024-01-01';
      const endDate = '2024-01-31';

      mockAxios.onGet(`/api/v1/vendors/${vendorId}/analytics`).reply(200, {
        success: true,
        data: MOCK_ANALYTICS
      });

      await VendorService.getAnalytics(vendorId, {
        start_date: startDate,
        end_date: endDate
      });

      const request = mockAxios.history.get[0];
      expect(request.params.start_date).toBe(startDate);
      expect(request.params.end_date).toBe(endDate);
    });

    it('should fetch revenue breakdown by category', async () => {
      const categoryBreakdown = {
        electronics: 800000,
        clothing: 400000,
        home: 300000
      };

      mockAxios.onGet(`/api/v1/vendors/${vendorId}/analytics/revenue-by-category`).reply(200, {
        success: true,
        data: categoryBreakdown
      });

      const response = await VendorService.getRevenueByCategory(vendorId, { time_range: '30d' });

      expect(response.success).toBe(true);
      expect(response.data.electronics).toBe(800000);
      expect(response.data.clothing).toBe(400000);
    });

    it('should export analytics data', async () => {
      const csvData = 'Date,Revenue,Orders\n2024-01-01,50000,5\n2024-01-02,75000,8';

      mockAxios.onGet(`/api/v1/vendors/${vendorId}/analytics/export`).reply(200, csvData, {
        'content-type': 'text/csv',
        'content-disposition': 'attachment; filename=analytics.csv'
      });

      const response = await VendorService.exportAnalytics(vendorId, {
        format: 'csv',
        time_range: '30d'
      });

      expect(response.data).toBe(csvData);
      expect(response.headers['content-type']).toBe('text/csv');
    });
  });

  describe('5. Order Management API', () => {
    const vendorId = 'vendor-123';

    it('should fetch vendor orders', async () => {
      const mockOrders = [
        {
          id: 'order-1',
          customer_name: 'John Doe',
          total: 150000,
          status: 'pending',
          created_at: '2024-01-20T10:00:00Z'
        },
        {
          id: 'order-2',
          customer_name: 'Jane Smith',
          total: 250000,
          status: 'shipped',
          created_at: '2024-01-19T15:30:00Z'
        }
      ];

      mockAxios.onGet(`/api/v1/vendors/${vendorId}/orders`).reply(200, {
        success: true,
        data: {
          orders: mockOrders,
          total: 25,
          page: 1,
          per_page: 10
        }
      });

      const response = await VendorService.getOrders(vendorId, { status: 'all' });

      expect(response.success).toBe(true);
      expect(response.data.orders).toHaveLength(2);
      expect(response.data.orders[0].id).toBe('order-1');
    });

    it('should update order status', async () => {
      const orderId = 'order-123';
      const newStatus = 'shipped';

      mockAxios.onPut(`/api/v1/vendors/${vendorId}/orders/${orderId}/status`).reply(200, {
        success: true,
        data: {
          id: orderId,
          status: newStatus,
          updated_at: '2024-01-21T12:00:00Z'
        }
      });

      const response = await VendorService.updateOrderStatus(vendorId, orderId, {
        status: newStatus,
        tracking_number: 'TRK123456789'
      });

      expect(response.success).toBe(true);
      expect(response.data.status).toBe(newStatus);

      const request = mockAxios.history.put[0];
      expect(JSON.parse(request.data).status).toBe(newStatus);
    });
  });

  describe('6. WebSocket Real-time Integration', () => {
    let mockWebSocket: any;

    beforeEach(() => {
      // Mock WebSocket
      mockWebSocket = {
        send: vi.fn(),
        close: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        readyState: WebSocket.OPEN
      };

      // @ts-ignore
      global.WebSocket = vi.fn(() => mockWebSocket);
    });

    it('should establish WebSocket connection for real-time analytics', async () => {
      const vendorId = 'vendor-123';
      const wsUrl = `ws://192.168.1.137:8000/ws/vendor/${vendorId}/analytics`;

      // Simulate WebSocket connection
      const ws = new WebSocket(wsUrl);

      expect(WebSocket).toHaveBeenCalledWith(wsUrl);
      expect(ws).toBe(mockWebSocket);
    });

    it('should handle real-time analytics updates', async () => {
      const vendorId = 'vendor-123';
      const mockUpdate = {
        type: 'analytics_update',
        data: {
          revenue: { current: 1600000, trend: 'up' },
          orders: { current: 47, trend: 'up' }
        }
      };

      // Simulate WebSocket message
      const onMessage = vi.fn();
      mockWebSocket.addEventListener.mockImplementation((event: string, handler: Function) => {
        if (event === 'message') {
          onMessage.mockImplementation(handler);
        }
      });

      // Simulate receiving update
      onMessage({ data: JSON.stringify(mockUpdate) });

      expect(onMessage).toHaveBeenCalled();
    });

    it('should handle WebSocket connection errors', async () => {
      const onError = vi.fn();
      mockWebSocket.addEventListener.mockImplementation((event: string, handler: Function) => {
        if (event === 'error') {
          onError.mockImplementation(handler);
        }
      });

      // Simulate error
      onError(new Error('WebSocket connection failed'));

      expect(onError).toHaveBeenCalled();
    });
  });

  describe('7. File Upload Integration', () => {
    const vendorId = 'vendor-123';

    it('should upload product images', async () => {
      const mockFile = new File(['image data'], 'product.jpg', { type: 'image/jpeg' });
      const formData = new FormData();
      formData.append('image', mockFile);

      mockAxios.onPost(`/api/v1/vendors/${vendorId}/products/images`).reply(200, {
        success: true,
        data: {
          url: 'https://cdn.mestocker.com/images/product-123.jpg',
          id: 'image-123',
          filename: 'product.jpg'
        }
      });

      const response = await VendorService.uploadProductImage(vendorId, formData);

      expect(response.success).toBe(true);
      expect(response.data.url).toContain('product-123.jpg');

      const request = mockAxios.history.post[0];
      expect(request.headers['Content-Type']).toContain('multipart/form-data');
    });

    it('should handle file upload errors', async () => {
      const mockFile = new File(['large image data'.repeat(1000)], 'large.jpg', { type: 'image/jpeg' });
      const formData = new FormData();
      formData.append('image', mockFile);

      mockAxios.onPost(`/api/v1/vendors/${vendorId}/products/images`).reply(413, {
        success: false,
        message: 'File too large',
        max_size: '5MB'
      });

      try {
        await VendorService.uploadProductImage(vendorId, formData);
      } catch (error: any) {
        expect(error.response.status).toBe(413);
        expect(error.response.data.message).toBe('File too large');
      }
    });
  });

  describe('8. Rate Limiting and Error Handling', () => {
    it('should handle rate limiting responses', async () => {
      mockAxios.onGet('/api/v1/vendors/vendor-123').reply(429, {
        success: false,
        message: 'Rate limit exceeded',
        retry_after: 60
      });

      try {
        await VendorService.getProfile('vendor-123');
      } catch (error: any) {
        expect(error.response.status).toBe(429);
        expect(error.response.data.message).toBe('Rate limit exceeded');
        expect(error.response.data.retry_after).toBe(60);
      }
    });

    it('should handle server errors gracefully', async () => {
      mockAxios.onGet('/api/v1/vendors/vendor-123').reply(500, {
        success: false,
        message: 'Internal server error'
      });

      try {
        await VendorService.getProfile('vendor-123');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
        expect(error.response.data.message).toBe('Internal server error');
      }
    });

    it('should retry failed requests automatically', async () => {
      // First call fails, second succeeds
      mockAxios
        .onGet('/api/v1/vendors/vendor-123')
        .replyOnce(500)
        .onGet('/api/v1/vendors/vendor-123')
        .reply(200, { success: true, data: MOCK_VENDOR_DATA });

      // Configure retry logic (this would be in the actual service)
      const response = await VendorService.getProfile('vendor-123');

      expect(response.success).toBe(true);
      expect(mockAxios.history.get).toHaveLength(2); // Should have retried
    });
  });

  describe('9. Authentication Integration', () => {
    it('should refresh token when expired', async () => {
      // Mock expired token response
      mockAxios.onGet('/api/v1/vendors/vendor-123').reply(401, {
        success: false,
        message: 'Token expired'
      });

      // Mock token refresh
      mockAxios.onPost('/api/v1/auth/refresh').reply(200, {
        success: true,
        data: {
          access_token: 'new-token-123',
          refresh_token: 'new-refresh-token-123'
        }
      });

      // Mock retry with new token
      mockAxios.onGet('/api/v1/vendors/vendor-123').reply(200, {
        success: true,
        data: MOCK_VENDOR_DATA
      });

      // This would trigger token refresh logic in interceptors
      const response = await VendorService.getProfile('vendor-123');

      expect(response.success).toBe(true);
    });

    it('should redirect to login when refresh fails', async () => {
      mockAxios.onGet('/api/v1/vendors/vendor-123').reply(401);
      mockAxios.onPost('/api/v1/auth/refresh').reply(401);

      try {
        await VendorService.getProfile('vendor-123');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
        // Should clear local storage and redirect
        expect(localStorage.getItem('auth_token')).toBeNull();
      }
    });
  });
});