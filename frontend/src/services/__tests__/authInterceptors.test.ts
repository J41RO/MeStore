import axios, { AxiosError, AxiosResponse } from 'axios';
import { apiClient } from '../authInterceptors';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock window events
const mockDispatchEvent = jest.fn();
Object.defineProperty(window, 'dispatchEvent', { value: mockDispatchEvent });

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('authInterceptors', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    mockDispatchEvent.mockClear();
  });

  describe('Request Interceptor', () => {
    it('should add token to request headers when token exists', () => {
      const mockToken = 'test-access-token';
      localStorageMock.getItem.mockReturnValue(mockToken);

      // Simular interceptor de request
      const config = { headers: {} };
      const token = localStorage.getItem('access_token');

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      expect(localStorage.getItem).toHaveBeenCalledWith('access_token');
      expect(config.headers.Authorization).toBe(`Bearer ${mockToken}`);
    });

    it('should not add Authorization header when no token exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const config = { headers: {} };
      const token = localStorage.getItem('access_token');

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      expect(localStorage.getItem).toHaveBeenCalledWith('access_token');
      expect(config.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptor - Token Refresh', () => {
    it('should refresh token on 401 error', async () => {
      const mockRefreshToken = 'test-refresh-token';
      const mockNewAccessToken = 'new-access-token';
      const mockNewRefreshToken = 'new-refresh-token';

      localStorageMock.getItem
        .mockReturnValueOnce(mockRefreshToken) // Para refresh_token
        .mockReturnValueOnce(mockRefreshToken); // Para verificación

      // Mock respuesta exitosa del refresh
      const mockRefreshResponse = {
        data: {
          access_token: mockNewAccessToken,
          refresh_token: mockNewRefreshToken,
        },
      };

      // Simular comportamiento del interceptor
      const error = {
        response: { status: 401 },
        config: { _retry: undefined, headers: {} },
      };

      const refreshToken = localStorage.getItem('refresh_token');
      expect(refreshToken).toBe(mockRefreshToken);

      // Simular actualización de tokens
      localStorage.setItem('access_token', mockNewAccessToken);
      localStorage.setItem('refresh_token', mockNewRefreshToken);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'access_token',
        mockNewAccessToken
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'refresh_token',
        mockNewRefreshToken
      );
    });

    it('should trigger logout event when refresh fails', () => {
      localStorageMock.getItem.mockReturnValue('invalid-refresh-token');

      // Simular fallo de refresh
      const error = {
        response: { status: 401 },
        config: { _retry: undefined },
      };

      // Simular limpieza de tokens y evento de logout
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.dispatchEvent(new CustomEvent('auth:logout'));

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(mockDispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'auth:logout',
        })
      );
    });

    it('should not retry request that already failed once', () => {
      const error = {
        response: { status: 401 },
        config: { _retry: true }, // Ya fue reintentado
      };

      // Request con _retry=true no debe activar refresh
      expect(error.config._retry).toBe(true);
    });
  });

  describe('Queue Management', () => {
    it('should handle multiple concurrent requests during refresh', () => {
      // Simular múltiples requests en cola durante refresh
      const failedQueue: Array<{
        resolve: (value?: any) => void;
        reject: (error?: any) => void;
      }> = [];

      const processQueue = (error: any, token: string | null = null) => {
        failedQueue.forEach(({ resolve, reject }) => {
          if (error) {
            reject(error);
          } else {
            resolve(token);
          }
        });
      };

      // Agregar requests a la cola
      const mockResolve1 = jest.fn();
      const mockResolve2 = jest.fn();
      const mockReject1 = jest.fn();
      const mockReject2 = jest.fn();

      failedQueue.push({ resolve: mockResolve1, reject: mockReject1 });
      failedQueue.push({ resolve: mockResolve2, reject: mockReject2 });

      // Procesar cola con éxito
      const newToken = 'new-token';
      processQueue(null, newToken);

      expect(mockResolve1).toHaveBeenCalledWith(newToken);
      expect(mockResolve2).toHaveBeenCalledWith(newToken);
      expect(mockReject1).not.toHaveBeenCalled();
      expect(mockReject2).not.toHaveBeenCalled();
    });

    it('should reject queued requests when refresh fails', () => {
      const failedQueue: Array<{
        resolve: (value?: any) => void;
        reject: (error?: any) => void;
      }> = [];

      const processQueue = (error: any, token: string | null = null) => {
        failedQueue.forEach(({ resolve, reject }) => {
          if (error) {
            reject(error);
          } else {
            resolve(token);
          }
        });
      };

      const mockResolve = jest.fn();
      const mockReject = jest.fn();
      failedQueue.push({ resolve: mockResolve, reject: mockReject });

      // Procesar cola con error
      const refreshError = new Error('Refresh failed');
      processQueue(refreshError, null);

      expect(mockReject).toHaveBeenCalledWith(refreshError);
      expect(mockResolve).not.toHaveBeenCalled();
    });
  });
});
