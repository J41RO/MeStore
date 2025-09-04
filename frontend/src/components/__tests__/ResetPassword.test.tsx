import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResetPassword from '../auth/ResetPassword';

// Mock fetch globally
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Simple mock for URLSearchParams
const mockURLSearchParams = jest.fn();
(global as any).URLSearchParams = jest.fn().mockImplementation(() => ({
  get: mockURLSearchParams,
}));

describe('ResetPassword Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockURLSearchParams.mockClear();
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading screen while validating token', () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    // Mock pending validation
    mockFetch.mockImplementation(() => new Promise(() => {}));

    render(<ResetPassword />);

    expect(
      screen.getByText('Validando enlace de recuperación...')
    ).toBeInTheDocument();
    expect(screen.getByText('🔄')).toBeInTheDocument();
  });

  test('shows error screen when no token in URL', async () => {
    mockURLSearchParams.mockReturnValue(null);

    render(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText('Enlace inválido')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Token no encontrado en la URL')
    ).toBeInTheDocument();
  });

  test('shows error screen when token validation fails', async () => {
    mockURLSearchParams.mockReturnValue('invalid_token_123');

    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        success: false,
        message: 'Token inválido o expirado',
      }),
    } as Response);

    render(<ResetPassword />);

    await waitFor(() => {
      expect(screen.getByText('Enlace inválido')).toBeInTheDocument();
    });

    expect(screen.getByText('Token inválido o expirado')).toBeInTheDocument();
  });

  test('renders password form when token is valid', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Token válido',
      }),
    } as Response);

    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    expect(screen.getByLabelText('Nueva contraseña')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirmar contraseña')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /actualizar contraseña/i })
    ).toBeInTheDocument();
  });

  test('validates password requirements with yup schema', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    const user = userEvent.setup();
    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Nueva contraseña');
    const submitButton = screen.getByRole('button', {
      name: /actualizar contraseña/i,
    });

    // Test weak password
    await user.type(passwordInput, 'weak');

    await waitFor(() => {
      expect(
        screen.getByText('La contraseña debe tener al menos 8 caracteres')
      ).toBeInTheDocument();
    });

    expect(submitButton).toBeDisabled();
  });

  test('validates password confirmation matching', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    const user = userEvent.setup();
    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Nueva contraseña');
    const confirmInput = screen.getByLabelText('Confirmar contraseña');

    await user.type(passwordInput, 'Password123');
    await user.type(confirmInput, 'DifferentPassword123');

    await waitFor(() => {
      expect(
        screen.getByText('Las contraseñas deben coincidir')
      ).toBeInTheDocument();
    });

    // Check visual indicator
    expect(
      screen.getByText('❌ Las contraseñas no coinciden')
    ).toBeInTheDocument();
  });

  test('shows password strength indicator', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    const user = userEvent.setup();
    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Nueva contraseña');

    // Test strong password
    await user.type(passwordInput, 'StrongPassword123');

    await waitFor(() => {
      expect(screen.getByText('Fortaleza: Muy fuerte')).toBeInTheDocument();
    });
  });

  test('handles successful password reset', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    // Mock token validation success
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    // Mock password reset success
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Contraseña actualizada exitosamente',
      }),
    } as Response);

    const user = userEvent.setup();
    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Nueva contraseña');
    const confirmInput = screen.getByLabelText('Confirmar contraseña');
    const submitButton = screen.getByRole('button', {
      name: /actualizar contraseña/i,
    });

    await user.type(passwordInput, 'NewPassword123');
    await user.type(confirmInput, 'NewPassword123');

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });

    await user.click(submitButton);

    // Wait for success screen
    await waitFor(() => {
      expect(screen.getByText('Contraseña actualizada')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Contraseña actualizada exitosamente')
    ).toBeInTheDocument();
  });

  test('handles password reset API error', async () => {
    mockURLSearchParams.mockReturnValue('valid_token_123');

    // Mock token validation success
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    // Mock password reset error
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        success: false,
        message: 'Token expirado durante el reset',
      }),
    } as Response);

    const user = userEvent.setup();
    render(<ResetPassword />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Nueva contraseña' })
      ).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Nueva contraseña');
    const confirmInput = screen.getByLabelText('Confirmar contraseña');
    const submitButton = screen.getByRole('button', {
      name: /actualizar contraseña/i,
    });

    await user.type(passwordInput, 'NewPassword123');
    await user.type(confirmInput, 'NewPassword123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText('Token expirado durante el reset')
      ).toBeInTheDocument();
    });

    // Should stay on form, not show success
    expect(
      screen.queryByText('Contraseña actualizada')
    ).not.toBeInTheDocument();
  });
});
