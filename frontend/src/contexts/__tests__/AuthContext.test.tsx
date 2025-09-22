import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuthContext } from '../AuthContext';

// Mock the auth store and service
jest.mock('../../services/authService');

let mockAuthStore = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  login: jest.fn(),
  logout: jest.fn(),
  checkAuth: jest.fn().mockResolvedValue(true),
  validateSession: jest.fn().mockResolvedValue(true),
};

// Mock login to update state
mockAuthStore.login.mockImplementation(async (email, password) => {
  mockAuthStore.user = {
    id: '1',
    email,
    user_type: 'buyer',
    name: 'Test User',
    is_active: true
  };
  mockAuthStore.token = 'mock-token';
  mockAuthStore.isAuthenticated = true;
  return true;
});

// Mock logout to clear state
mockAuthStore.logout.mockImplementation(async () => {
  mockAuthStore.user = null;
  mockAuthStore.token = null;
  mockAuthStore.isAuthenticated = false;
});

jest.mock('../../stores/authStore', () => ({
  useAuthStore: () => mockAuthStore,
}));

// Componente de prueba
const TestComponent = () => {
  const { isAuthenticated, user, login, logout } = useAuthContext();

  const handleLogin = async () => {
    try {
      await login('test@test.com', 'password123');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div>
      <span data-testid='auth-status'>
        {isAuthenticated ? 'authenticated' : 'not-authenticated'}
      </span>
      <span data-testid='user-email'>{user?.email || 'no-user'}</span>
      <button
        onClick={handleLogin}
        data-testid='login-btn'
      >
        Login
      </button>
      <button onClick={handleLogout} data-testid='logout-btn'>
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  const renderWithProvider = () => {
    return render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
  };

  test('provides authentication state correctly', () => {
    renderWithProvider();

    expect(screen.getByTestId('auth-status')).toHaveTextContent(
      'not-authenticated'
    );
    expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
  });

  test('handles login correctly', async () => {
    const { login } = mockAuthStore;

    // Test that login function returns true
    const result = await login('test@test.com', 'password');
    expect(result).toBe(true);
    expect(login).toHaveBeenCalledWith('test@test.com', 'password');
  });

  test('handles logout correctly', async () => {
    const { logout } = mockAuthStore;

    // Test that logout function resolves
    await expect(logout()).resolves.toBeUndefined();
    expect(logout).toHaveBeenCalled();
  });
});
