import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ForgotPassword from '../auth/ForgotPassword';

// Mock fetch globally
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('ForgotPassword Component', () => {
  const mockOnBackToLogin = jest.fn();

  beforeEach(() => {
    mockFetch.mockClear();
    mockOnBackToLogin.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders forgot password form correctly', () => {
    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    expect(screen.getByText('Recuperar contraseña')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /enviar enlace de recuperación/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /volver al login/i })
    ).toBeInTheDocument();
  });

  test('validates email format with yup schema', async () => {
    const user = userEvent.setup();
    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    // Test invalid email
    await user.type(emailInput, 'invalid-email');
    await waitFor(() => {
      expect(screen.getByText('Formato de email inválido')).toBeInTheDocument();
    });

    expect(submitButton).toBeDisabled();

    // Test valid email
    await user.clear(emailInput);
    await user.type(emailInput, 'test@example.com');
    await waitFor(() => {
      expect(
        screen.queryByText('Formato de email inválido')
      ).not.toBeInTheDocument();
    });

    expect(submitButton).not.toBeDisabled();
  });

  test('validates required email field', async () => {
    const user = userEvent.setup();
    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    // Initially button should be disabled (no email)
    expect(submitButton).toBeDisabled();

    // Type and clear to trigger validation
    await user.type(emailInput, 'a');
    await user.clear(emailInput);

    await waitFor(
      () => {
        expect(screen.getByText('El email es obligatorio')).toBeInTheDocument();
      },
      { timeout: 2000 }
    );

    expect(submitButton).toBeDisabled();
  });

  test('handles successful password recovery request', async () => {
    const user = userEvent.setup();

    // Mock successful response with delay
    mockFetch.mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({
                  success: true,
                  message: 'Email de recuperación enviado exitosamente',
                }),
              } as Response),
            100
          )
        )
    );

    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    await user.type(emailInput, 'test@example.com');

    // Click submit and immediately check for loading state
    await user.click(submitButton);

    // Check for loading state with more flexible matcher
    await waitFor(
      () => {
        expect(screen.getByText(/enviando/i)).toBeInTheDocument();
      },
      { timeout: 1000 }
    );

    // Wait for success screen
    await waitFor(
      () => {
        expect(screen.getByText('Revisa tu email')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );

    expect(
      screen.getByText(/se ha enviado un enlace de recuperación a/i)
    ).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();

    // Verify API call
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/auth/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: 'test@example.com' }),
    });
  });

  test('handles API error response', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        success: false,
        message: 'Email no encontrado en el sistema',
      }),
    } as Response);

    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    await user.type(emailInput, 'nonexistent@example.com');
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText('Email no encontrado en el sistema')
      ).toBeInTheDocument();
    });

    // Should stay on form, not redirect to success
    expect(screen.queryByText('Revisa tu email')).not.toBeInTheDocument();
  });

  test('handles network error', async () => {
    const user = userEvent.setup();

    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText('Error de conexión. Intenta nuevamente.')
      ).toBeInTheDocument();
    });
  });

  test('calls onBackToLogin when back button is clicked', async () => {
    const user = userEvent.setup();
    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const backButton = screen.getByRole('button', { name: /volver al login/i });
    await user.click(backButton);

    expect(mockOnBackToLogin).toHaveBeenCalledTimes(1);
  });

  test('calls onBackToLogin from success screen', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Email enviado',
      }),
    } as Response);

    render(<ForgotPassword onBackToLogin={mockOnBackToLogin} />);

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', {
      name: /enviar enlace de recuperación/i,
    });

    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);

    // Wait for success screen
    await waitFor(() => {
      expect(screen.getByText('Revisa tu email')).toBeInTheDocument();
    });

    const backButtonSuccess = screen.getByRole('button', {
      name: /volver al login/i,
    });
    await user.click(backButtonSuccess);

    expect(mockOnBackToLogin).toHaveBeenCalledTimes(1);
  });
});
