import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from '../Login';
import { useAuthStore } from '../../stores/authStore';

// Mock the auth store
jest.mock('../../stores/authStore');
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

// Mock react-router-dom Navigate

// Mock fetch globally
global.fetch = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({ to }: { to: string }) => (
    <div data-testid="navigate" data-to={to}>
      Redirecting to {to}
    </div>
  ),
}));

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
};

describe('Login', () => {
  const mockLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render login form when not authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Contraseña')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ingresar' })).toBeInTheDocument();
  });

  test('should redirect to dashboard when already authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: { id: '1', email: 'test@test.com' },
      token: 'mock-token',
    });

    renderLogin();

    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/dashboard');
  });

  test('should handle form submission and call login', async () => {
    // Mock fetch response
    const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        token: 'demo_token_123',
        user: { id: '1', email: 'test@example.com', name: 'Usuario Demo' }
      })
    } as Response);
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Contraseña');
    const submitButton = screen.getByRole('button', { name: 'Ingresar' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(
        expect.stringContaining('demo_token_'),
        { id: '1', email: 'test@example.com', name: 'Usuario Demo' }
      );
    });
  });

  test('should require email and password fields', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Contraseña');

    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  test('should update input values when typing', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    const emailInput = screen.getByPlaceholderText('Email') as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText('Contraseña') as HTMLInputElement;

    fireEvent.change(emailInput, { target: { value: 'user@test.com' } });
    fireEvent.change(passwordInput, { target: { value: 'mypassword' } });

    expect(emailInput.value).toBe('user@test.com');
    expect(passwordInput.value).toBe('mypassword');
  });
});