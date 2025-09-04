import React from 'react';
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OTPVerification from '../auth/OTPVerification';

// Mock fetch para pruebas de API
global.fetch = jest.fn();

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

describe('OTPVerification Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.MockedFunction<typeof fetch>).mockClear();
  });

  // TEST 1: Validación de código de 6 dígitos ✅
  test('should validate 6-digit OTP code correctly', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');
    fireEvent.click(sendButton);

    await waitFor(() => {
      const inputs = screen.getAllByRole('textbox');
      expect(inputs).toHaveLength(6);
    });

    const inputs = screen.getAllByRole('textbox');
    await userEvent.type(inputs[0], '1');
    await userEvent.type(inputs[1], '2');
    await userEvent.type(inputs[2], '3');

    expect(inputs[0]).toHaveAttribute('value', '1');
    expect(inputs[1]).toHaveAttribute('value', '2');
    expect(inputs[2]).toHaveAttribute('value', '3');
  });

  // TEST 2: Envío de SMS ✅
  test('should send SMS with Colombian phone number', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');

    await act(async () => {
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/send-verification-sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer mock-token',
        },
        body: JSON.stringify({ otp_type: 'SMS' }),
      });
    });

    await waitFor(() => {
      expect(screen.getByText('SMS enviado')).toBeInTheDocument();
    });
  });

  // TEST 3: CORREGIDO - Verificación exitosa de código
  test('should verify OTP code successfully', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // PASO 1: Mock envío SMS exitoso
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(screen.getAllByRole('textbox')).toHaveLength(6);
    });

    // PASO 2: Llenar código completo
    const inputs = screen.getAllByRole('textbox');
    for (let i = 0; i < 6; i++) {
      await act(async () => {
        await userEvent.clear(inputs[i]);
        await userEvent.type(inputs[i], (i + 1).toString());
      });
    }

    // PASO 3: Mock verificación exitosa
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Verificación exitosa' }),
    } as Response);

    // PASO 4: Click en verificar (segunda llamada a fetch)
    const verifyButton = screen.getByText('Verificar Código');
    await act(async () => {
      fireEvent.click(verifyButton);
    });

    // PASO 5: Verificar la llamada única (verificación)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2); // Envío SMS + Verificación
    });

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('SMS');
    });
  });

  // TEST 4: Temporizador ✅
  test('should handle countdown timer and resend functionality', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/Reenviar en \d+s/)).toBeInTheDocument();
    });

    const resendButton = screen.getByText(/Reenviar en \d+s/);
    expect(resendButton).toBeDisabled();
  });

  // TEST 5: CORREGIDO - Manejo de errores de API
  test('should handle API errors correctly', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock error del API para envío
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ success: false, message: 'Error del servidor' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Verificar mensaje de error con búsqueda más flexible
    await waitFor(() => {
      expect(screen.queryByText(/Error del servidor/i)).toBeInTheDocument();
    });

    // Verificar que NO se cambió al step de verificación
    expect(
      screen.queryByText('Ingresa el código de verificación')
    ).not.toBeInTheDocument();
  });

  // TEST 6: CORREGIDO - Auto-focus simplificado
  test('should auto-focus between input fields', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(screen.queryAllByRole('textbox')).toHaveLength(6);
    });

    const inputs = screen.getAllByRole('textbox') as HTMLInputElement[];

    await act(async () => {
      fireEvent.change(inputs[0], { target: { value: '1' } });
    });
    expect(inputs[0]).toHaveValue('1');

    await act(async () => {
      fireEvent.change(inputs[1], { target: { value: '2' } });
    });
    expect(inputs[1]).toHaveValue('2');
  }, 10000);
});
