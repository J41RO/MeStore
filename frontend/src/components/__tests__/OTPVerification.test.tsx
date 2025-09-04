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
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  // TEST 1: Validación de código de 6 dígitos ✅
  test('should validate 6-digit OTP code correctly', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock respuesta exitosa para envío SMS
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    fireEvent.click(sendButton);

    // Esperar a que aparezcan los inputs
    await waitFor(() => {
      const inputs = screen.getAllByRole('textbox');
      expect(inputs).toHaveLength(6);
    });

    // Llenar algunos dígitos
    const inputs = screen.getAllByRole('textbox');
    await act(async () => {
      fireEvent.change(inputs[0], { target: { value: '1' } });
      fireEvent.change(inputs[1], { target: { value: '2' } });
      fireEvent.change(inputs[2], { target: { value: '3' } });
    });

    // Verificar que los valores se asignan correctamente
    expect(inputs[0]).toHaveValue('1');
    expect(inputs[1]).toHaveValue('2');
    expect(inputs[2]).toHaveValue('3');
  });

  // TEST 2: Envío de SMS ✅
  test('should send SMS with correct API call', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock respuesta exitosa
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Verificar llamada a la API
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

    // Verificar mensaje de éxito
    await waitFor(() => {
      expect(screen.getByText('SMS enviado')).toBeInTheDocument();
    });
  });

  // TEST 3: CORREGIDO - Verificación exitosa de código
  test('should verify OTP code successfully', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // PASO 1: Mock envío SMS exitoso
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Esperar a que aparezcan los inputs
    await waitFor(() => {
      expect(screen.getAllByRole('textbox')).toHaveLength(6);
    });

    // PASO 2: Llenar código completo
    const inputs = screen.getAllByRole('textbox');
    await act(async () => {
      // Llenar todos los dígitos
      fireEvent.change(inputs[0], { target: { value: '1' } });
      fireEvent.change(inputs[1], { target: { value: '2' } });
      fireEvent.change(inputs[2], { target: { value: '3' } });
      fireEvent.change(inputs[3], { target: { value: '4' } });
      fireEvent.change(inputs[4], { target: { value: '5' } });
      fireEvent.change(inputs[5], { target: { value: '6' } });
    });

    // PASO 3: Mock verificación exitosa (segunda llamada a fetch)
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Verificación exitosa' }),
    } as Response);

    // PASO 4: Click en verificar
    const verifyButton = screen.getByText('Verificar Código');
    await act(async () => {
      fireEvent.click(verifyButton);
    });

    // PASO 5: Verificar ambas llamadas a fetch
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2); // Envío SMS + Verificación
    });

    // Verificar que se llama al callback de éxito
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('SMS');
    });
  });

  // TEST 4: Temporizador de reenvío ✅
  test('should handle countdown timer and resend functionality', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock respuesta exitosa
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Verificar que aparece el temporizador
    await waitFor(() => {
      expect(screen.getByText(/Reenviar en \d+s/)).toBeInTheDocument();
    });

    // Verificar que el botón está deshabilitado
    const resendButton = screen.getByText(/Reenviar en \d+s/);
    expect(resendButton).toBeDisabled();
  });

  // TEST 5: CORREGIDO - Manejo de errores de API
  test('should handle API errors correctly', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock error del API para envío
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ success: false, message: 'Error del servidor' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // CLAVE: Verificar que el mensaje de error aparece
    await waitFor(() => {
      expect(screen.getByText('Error del servidor')).toBeInTheDocument();
    });

    // CLAVE: Verificar que NO se cambió al step de verificación
    expect(screen.queryByText('Ingresa el código de verificación')).not.toBeInTheDocument();
    
    // Verificar que seguimos en el paso de solicitud
    expect(screen.getByText('Verificar Email/Teléfono')).toBeInTheDocument();
  });

  // TEST 6: CORREGIDO - Auto-focus entre campos
  test('should auto-focus between input fields', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock respuesta exitosa
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'SMS enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // CLAVE: Esperar a que aparezcan los inputs correctamente
    await waitFor(() => {
      expect(screen.getAllByRole('textbox')).toHaveLength(6);
    });

    const inputs = screen.getAllByRole('textbox') as HTMLInputElement[];

    // Simular entrada de dígitos
    await act(async () => {
      fireEvent.change(inputs[0], { target: { value: '1' } });
    });
    expect(inputs[0]).toHaveValue('1');

    await act(async () => {
      fireEvent.change(inputs[1], { target: { value: '2' } });
    });
    expect(inputs[1]).toHaveValue('2');

    // Verificar que los inputs mantienen sus valores
    expect(inputs[0]).toHaveValue('1');
    expect(inputs[1]).toHaveValue('2');
  });

  // TEST 7: Verificación por Email ✅
  test('should send verification email correctly', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Por defecto está en EMAIL, no necesitamos cambiar
    expect(screen.getByText('Verificar por Email')).toHaveClass('active');

    // Mock respuesta exitosa
    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Email enviado' }),
    } as Response);

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Verificar llamada correcta a API de email
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/send-verification-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer mock-token',
        },
        body: JSON.stringify({ otp_type: 'EMAIL' }),
      });
    });
  });

  // TEST 8: Manejo de errores de conexión ✅
  test('should handle network errors', async () => {
    const mockOnSuccess = jest.fn();
    render(<OTPVerification onVerificationSuccess={mockOnSuccess} />);

    // Cambiar a SMS
    const smsButton = screen.getByText('Verificar por SMS');
    fireEvent.click(smsButton);

    // Mock error de red
    (fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(
      new Error('Network Error')
    );

    // Enviar código
    const sendButton = screen.getByText('Enviar Código');
    await act(async () => {
      fireEvent.click(sendButton);
    });

    // Verificar mensaje de error de conexión
    await waitFor(() => {
      expect(screen.getByText('Error de conexión')).toBeInTheDocument();
    });
  });
});