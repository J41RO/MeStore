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
    <div data-testid='navigate' data-to={to}>
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

    expect(screen.getAllByText('Iniciar Sesión')[0]).toBeInTheDocument();
    expect(screen.getByPlaceholderText('tu@email.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Tu contraseña')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Iniciar Sesión' })
    ).toBeInTheDocument();
  });

  test('should handle form submission and call login', async () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    const emailInput = screen.getByPlaceholderText('tu@email.com');
    const passwordInput = screen.getByPlaceholderText('Tu contraseña');
    const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });

    fireEvent.change(emailInput, { target: { value: 'admin@mestore.com' } });
    fireEvent.change(passwordInput, { target: { value: '123456' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(
        expect.any(String), 
        expect.objectContaining({ 
          email: 'admin@mestore.com',
          user_type: 'ADMIN'
        })
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

    const emailInput = screen.getByPlaceholderText('tu@email.com');
    const passwordInput = screen.getByPlaceholderText('Tu contraseña');

    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  test('should update input values when typing', async () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      checkAuth: jest.fn(),
      user: null,
      token: null,
    });

    renderLogin();

    const emailInput = screen.getByPlaceholderText('tu@email.com') as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(
      'Tu contraseña'
    ) as HTMLInputElement;

    fireEvent.change(emailInput, { target: { value: 'admin@mestore.com' } });
    fireEvent.change(passwordInput, { target: { value: '123456' } });

    expect(emailInput.value).toBe('admin@mestore.com');
    expect(passwordInput.value).toBe('123456');
  });
});