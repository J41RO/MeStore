import { renderHook, act } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';
import { useAuth } from '../useAuth';
import React from 'react';

// Mock the authService
jest.mock('../../services/authService', () => ({
  authService: {
    login: jest.fn(),
    logout: jest.fn(),
    getCurrentUser: jest.fn(),
    isAuthenticated: jest.fn(),
    getToken: jest.fn(),
    getRefreshToken: jest.fn(),
    clearTokens: jest.fn(),
    validateToken: jest.fn(),
    register: jest.fn(),
    adminLogin: jest.fn(),
    refreshToken: jest.fn(),
    forgotPassword: jest.fn(),
    resetPassword: jest.fn(),
    sendOTP: jest.fn(),
    verifyOTP: jest.fn(),
  },
}));

const wrapper = ({ children }: { children: React.ReactNode }) =>
  React.createElement(AuthProvider, null, children);

import { authService } from '../../services/authService';

const mockAuthService = authService as jest.Mocked<typeof authService>;

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up default mock implementations
    mockAuthService.isAuthenticated.mockReturnValue(false);
    mockAuthService.getToken.mockReturnValue(null);
    mockAuthService.getRefreshToken.mockReturnValue(null);
    mockAuthService.clearTokens.mockReturnValue(undefined);
    mockAuthService.validateToken.mockResolvedValue(false);
    mockAuthService.getCurrentUser.mockResolvedValue({
      success: false,
      error: 'Not authenticated'
    });
  });

  test('returns initial state correctly', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.isLoggedIn).toBe(false);
    expect(result.current.userRole).toBe('guest');
  });

  test('signIn works correctly', async () => {
    // Mock successful login
    mockAuthService.login.mockResolvedValue({
      success: true,
      data: {
        access_token: 'fake-token',
        refresh_token: 'fake-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      }
    });

    mockAuthService.getCurrentUser.mockResolvedValue({
      success: true,
      data: {
        id: '1',
        email: 'test@example.com',
        name: 'test',
        user_type: 'buyer',
        is_active: true,
        is_verified: true,
        phone: null,
        city: null,
        address: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    });

    mockAuthService.isAuthenticated.mockReturnValue(true);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      const response = await result.current.signIn(
        'test@example.com',
        'password'
      );
      expect(response.success).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.userEmail).toBe('test@example.com');
    expect(result.current.userName).toBe('test');
  });

  test('signOut works correctly', async () => {
    // Mock successful login first
    mockAuthService.login.mockResolvedValue({
      success: true,
      data: {
        access_token: 'fake-token',
        refresh_token: 'fake-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      }
    });

    mockAuthService.getCurrentUser.mockResolvedValue({
      success: true,
      data: {
        id: '1',
        email: 'test@example.com',
        name: 'test',
        user_type: 'buyer',
        is_active: true,
        is_verified: true,
        phone: null,
        city: null,
        address: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    });

    mockAuthService.isAuthenticated.mockReturnValue(true);

    const { result } = renderHook(() => useAuth(), { wrapper });

    // Login first
    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    // Mock logout
    mockAuthService.logout.mockResolvedValue({ success: true });
    mockAuthService.isAuthenticated.mockReturnValue(false);
    mockAuthService.getToken.mockReturnValue(null);

    // Then logout
    await act(async () => {
      const response = await result.current.signOut();
      expect(response.success).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });
});
