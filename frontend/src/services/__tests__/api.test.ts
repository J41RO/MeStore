import { api } from '../api';
import { apiClient } from '../authInterceptors';

// Mock apiClient
jest.mock('../authInterceptors', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('api helper', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('auth methods', () => {
    it('should call login endpoint with credentials', () => {
      const credentials = { email: 'test@test.com', password: 'password' };
      
      api.auth.login(credentials);
      
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/auth/login', credentials);
    });

    it('should call register endpoint with user data', () => {
      const userData = { email: 'test@test.com', name: 'Test User' };
      
      api.auth.register(userData);
      
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/auth/register', userData);
    });

    it('should call refresh endpoint with token', () => {
      const refreshToken = 'refresh-token';
      
      api.auth.refresh(refreshToken);
      
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/auth/refresh', { 
        refresh_token: refreshToken 
      });
    });
  });

  describe('users methods', () => {
    it('should call get profile endpoint', () => {
      api.users.getProfile();
      
      expect(mockedApiClient.get).toHaveBeenCalledWith('/api/users/me');
    });

    it('should call update profile endpoint with data', () => {
      const profileData = { name: 'Updated Name' };
      
      api.users.updateProfile(profileData);
      
      expect(mockedApiClient.put).toHaveBeenCalledWith('/api/users/me', profileData);
    });
  });

  describe('products methods', () => {
    it('should call get all products endpoint', () => {
      api.products.getAll();
      
      expect(mockedApiClient.get).toHaveBeenCalledWith('/api/products');
    });

    it('should call get product by id endpoint', () => {
      const productId = '123';
      
      api.products.getById(productId);
      
      expect(mockedApiClient.get).toHaveBeenCalledWith('/api/products/123');
    });

    it('should call create product endpoint with data', () => {
      const productData = { name: 'Test Product', price: 100 };
      
      api.products.create(productData);
      
      expect(mockedApiClient.post).toHaveBeenCalledWith('/api/products', productData);
    });
  });
});
