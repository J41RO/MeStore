import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import AuthGuard from '../AuthGuard';
import { useAuthStore } from '../../stores/authStore';

// Mock the auth store
jest.mock('../../services/authService');
jest.mock('../../stores/authStore');
jest.mock('../../hooks/useAuth');
const mockUseAuthStore = useAuthStore as jest.MockedFunction<
  typeof useAuthStore
>;

// Mock react-router-dom Navigate
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({ to, state }: { to: string; state?: any }) => (
    <div data-testid='navigate' data-to={to} data-state={JSON.stringify(state)}>
      Redirecting to {to}
    </div>
  ),
}));

const TestChild = () => (
  <div data-testid='protected-content'>Protected Content</div>
);

const renderAuthGuard = (children: React.ReactNode = <TestChild />) => {
  return render(
    <BrowserRouter>
      <AuthGuard>{children}</AuthGuard>
    </BrowserRouter>
  );
};

describe('AuthGuard', () => {
  const mockCheckAuth = jest.fn();
  const mockValidateSession = jest.fn();
  const mockLogin = jest.fn();
  const mockLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockCheckAuth.mockResolvedValue(true);
    mockValidateSession.mockResolvedValue(true);
  });

  test('should render children when user is authenticated', async () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      token: 'valid-token',
      user: {
        id: '1',
        email: 'test@example.com',
        user_type: 'BUYER',
        name: 'Test User',
        is_active: true
      },
      error: null,
      checkAuth: mockCheckAuth,
      validateSession: mockValidateSession,
      login: mockLogin,
      adminLogin: jest.fn(),
      logout: mockLogout,
      register: jest.fn(),
      refreshUserInfo: jest.fn(),
      updateUser: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearAuth: jest.fn(),
      isAdmin: jest.fn(),
      isSuperuser: jest.fn(),
      getUserType: jest.fn()
    });

    await act(async () => {
      renderAuthGuard();
    });

    await waitFor(() => {
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
    expect(screen.queryByTestId('navigate')).not.toBeInTheDocument();
  });

  test('should redirect to login when user is not authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      token: null,
      user: null,
      error: null,
      checkAuth: mockCheckAuth,
      validateSession: mockValidateSession,
      login: mockLogin,
      adminLogin: jest.fn(),
      logout: mockLogout,
      register: jest.fn(),
      refreshUserInfo: jest.fn(),
      updateUser: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearAuth: jest.fn(),
      isAdmin: jest.fn(),
      isSuperuser: jest.fn(),
      getUserType: jest.fn()
    });

    renderAuthGuard();

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toHaveAttribute(
      'data-to',
      '/auth/login'
    );
  });

  test('should redirect to custom fallback path when specified', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      token: null,
      user: null,
      error: null,
      checkAuth: mockCheckAuth,
      validateSession: mockValidateSession,
      login: mockLogin,
      adminLogin: jest.fn(),
      logout: mockLogout,
      register: jest.fn(),
      refreshUserInfo: jest.fn(),
      updateUser: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearAuth: jest.fn(),
      isAdmin: jest.fn(),
      isSuperuser: jest.fn(),
      getUserType: jest.fn()
    });

    render(
      <BrowserRouter>
        <AuthGuard redirectTo='/custom-login'>
          <TestChild />
        </AuthGuard>
      </BrowserRouter>
    );

    expect(screen.getByTestId('navigate')).toHaveAttribute(
      'data-to',
      '/custom-login'
    );
  });

  test('should pass current location in state when redirecting', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      token: null,
      user: null,
      error: null,
      checkAuth: mockCheckAuth,
      validateSession: mockValidateSession,
      login: mockLogin,
      adminLogin: jest.fn(),
      logout: mockLogout,
      register: jest.fn(),
      refreshUserInfo: jest.fn(),
      updateUser: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearAuth: jest.fn(),
      isAdmin: jest.fn(),
      isSuperuser: jest.fn(),
      getUserType: jest.fn()
    });

    renderAuthGuard();

    const navigateElement = screen.getByTestId('navigate');
    const stateData = JSON.parse(
      navigateElement.getAttribute('data-state') || '{}'
    );
    expect(stateData.from).toBe('/');
  });
});
