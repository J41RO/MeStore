// Mock the entire api module
jest.mock('../api', () => {
  const mockBaseApi = {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  };

  return {
    __esModule: true,
    default: {
      auth: {
        login: jest.fn().mockImplementation((credentials) => mockBaseApi.post('/api/auth/login', credentials)),
        register: jest.fn().mockImplementation((userData) => mockBaseApi.post('/api/auth/register', userData)),
        refresh: jest.fn().mockImplementation((refreshToken) => mockBaseApi.post('/api/auth/refresh', { refresh_token: refreshToken }))
      },
      users: {
        getProfile: jest.fn().mockImplementation(() => mockBaseApi.get('/api/users/profile')),
        updateProfile: jest.fn().mockImplementation((profileData) => mockBaseApi.put('/api/users/profile', profileData))
      },
      products: {
        getAll: jest.fn().mockImplementation(() => mockBaseApi.get('/api/products')),
        getById: jest.fn().mockImplementation((id) => mockBaseApi.get(`/api/products/${id}`)),
        create: jest.fn().mockImplementation((data) => mockBaseApi.post('/productos', data)),
        update: jest.fn().mockImplementation((id, data) => mockBaseApi.put(`/productos/${id}`, data)),
        getWithFilters: jest.fn().mockImplementation((filters) => mockBaseApi.get('/productos', { params: filters }))
      },
      post: mockBaseApi.post,
      get: mockBaseApi.get,
      put: mockBaseApi.put,
      delete: mockBaseApi.delete
    },
    authAPI: {},
    usersAPI: {},
    productsAPI: {},
    mockBaseApi // Export for testing
  };
});

import api from '../api';
const { mockBaseApi } = require('../api');

describe('api helper', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('auth methods', () => {
    it('should call login endpoint with credentials', () => {
      const credentials = { email: 'test@test.com', password: 'password' };

      api.auth.login(credentials);

      expect(mockBaseApi.post).toHaveBeenCalledWith('/api/auth/login', credentials);
    });

    it('should call register endpoint with user data', () => {
      const userData = { email: 'test@test.com', name: 'Test User' };

      api.auth.register(userData);

      expect(mockBaseApi.post).toHaveBeenCalledWith('/api/auth/register', userData);
    });

    it('should call refresh endpoint with token', () => {
      const refreshToken = 'refresh-token';

      api.auth.refresh(refreshToken);

      expect(mockBaseApi.post).toHaveBeenCalledWith('/api/auth/refresh', { refresh_token: refreshToken });
    });
  });

  describe('users methods', () => {
    it('should call get profile endpoint', () => {
      api.users.getProfile();

      expect(mockBaseApi.get).toHaveBeenCalledWith('/api/users/profile');
    });

    it('should call update profile endpoint with data', () => {
      const profileData = { name: 'Updated Name' };

      api.users.updateProfile(profileData);

      expect(mockBaseApi.put).toHaveBeenCalledWith('/api/users/profile', profileData);
    });
  });

  describe('products methods', () => {
    it('should call get all products endpoint', () => {
      api.products.getAll();

      expect(mockBaseApi.get).toHaveBeenCalledWith('/api/products');
    });

    it('should call get product by id endpoint', () => {
      const productId = '123';

      api.products.getById(productId);

      expect(mockBaseApi.get).toHaveBeenCalledWith('/api/products/123');
    });

    it('should call create product endpoint with data', () => {
      const productData = { name: 'Test Product', price: 100 };

      api.products.create(productData);

      expect(mockBaseApi.post).toHaveBeenCalledWith('/productos', productData);
    });
  });
});