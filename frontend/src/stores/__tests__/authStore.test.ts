import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuthStore, UserType } from '../authStore';

// Mock the authService
jest.mock('../../services/authService', () => ({
  authService: {
    login: jest.fn(),
    getCurrentUser: jest.fn(),
    getToken: jest.fn(),
    validateToken: jest.fn(),
    logout: jest.fn(),
    getRefreshToken: jest.fn(),
    refreshToken: jest.fn(),
  },
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Get the mocked authService after the mock is defined
const { authService } = require('../../services/authService');

describe('AuthStore', () => {
  beforeEach(async () => {
    jest.clearAllMocks();
    // Configure mocks
    authService.login.mockResolvedValue({
      success: true,
      data: { access_token: 'mock-token' }
    });
    authService.getCurrentUser.mockResolvedValue({
      success: true,
      data: {
        id: '1',
        email: 'test@example.com',
        user_type: 'BUYER',
        nombre: 'Test User',
        email_verified: true,
        phone_verified: false,
        is_active: true
      }
    });
    authService.getToken.mockReturnValue('existing-token');
    authService.validateToken.mockResolvedValue(true);
    // Reset store state
    await useAuthStore.getState().logout();
  });

  test('should initialize with default state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  test('should login user and set authentication state', async () => {
    const { result } = renderHook(() => useAuthStore());
    const email = 'test@example.com';
    const password = 'password123';

    await act(async () => {
      await result.current.login(email, password);
    });

    await waitFor(() => {
      expect(result.current.user).not.toBeNull();
      expect(result.current.user?.email).toBe(email);
      expect(result.current.token).toBe('mock-token');
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  test('should logout user and clear state', async () => {
    const { result } = renderHook(() => useAuthStore());

    // First login
    await act(async () => {
      await result.current.login('test@test.com', 'password123');
    });

    // Then logout
    await act(async () => {
      await result.current.logout();
    });

    await waitFor(() => {
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  test('should check auth from localStorage', async () => {
    mockLocalStorage.getItem.mockReturnValue('existing-token');
    const { result } = renderHook(() => useAuthStore());

    let isAuthenticated;
    await act(async () => {
      isAuthenticated = await result.current.checkAuth();
    });

    await waitFor(() => {
      expect(isAuthenticated).toBe(true);
      expect(result.current.token).toBe('existing-token');
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  test('should return false when no token in localStorage', async () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    authService.getToken.mockReturnValue(null);
    const { result } = renderHook(() => useAuthStore());

    let isAuthenticated;
    await act(async () => {
      isAuthenticated = await result.current.checkAuth();
    });

    await waitFor(() => {
      expect(isAuthenticated).toBe(false);
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});
