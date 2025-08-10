import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import AuthGuard from '../AuthGuard';
import { useAuthStore } from '../../stores/authStore';

// Mock the auth store
jest.mock('../../stores/authStore');
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

// Mock react-router-dom Navigate
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({ to, state }: { to: string; state?: any }) => (
    <div data-testid="navigate" data-to={to} data-state={JSON.stringify(state)}>
      Redirecting to {to}
    </div>
  ),
}));

const TestChild = () => <div data-testid="protected-content">Protected Content</div>;

const renderAuthGuard = (children: React.ReactNode = <TestChild />) => {
  return render(
    <BrowserRouter>
      <AuthGuard>{children}</AuthGuard>
    </BrowserRouter>
  );
};

describe('AuthGuard', () => {
  const mockCheckAuth = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render children when user is authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      checkAuth: mockCheckAuth,
      user: null,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    });

    renderAuthGuard();

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.queryByTestId('navigate')).not.toBeInTheDocument();
    expect(mockCheckAuth).toHaveBeenCalled();
  });

  test('should redirect to login when user is not authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      checkAuth: mockCheckAuth,
      user: null,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    });

    renderAuthGuard();

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/auth/login');
    expect(mockCheckAuth).toHaveBeenCalled();
  });

  test('should redirect to custom fallback path when specified', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      checkAuth: mockCheckAuth,
      user: null,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <BrowserRouter>
        <AuthGuard fallbackPath="/custom-login">
          <TestChild />
        </AuthGuard>
      </BrowserRouter>
    );

    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/custom-login');
  });

  test('should pass current location in state when redirecting', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      checkAuth: mockCheckAuth,
      user: null,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    });

    renderAuthGuard();

    const navigateElement = screen.getByTestId('navigate');
    const stateData = JSON.parse(navigateElement.getAttribute('data-state') || '{}');
    expect(stateData.from).toBe('/');
  });
});
