import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '../auth/LoginForm';

// Mock fetch para testing
global.fetch = jest.fn();

describe('LoginForm', () => {
  beforeEach(() => {
    // Reset fetch mock antes de cada test
    (fetch as jest.MockedFunction<typeof fetch>).mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderizado del componente', () => {
    test('renderiza todos los elementos correctamente', () => {
      render(<LoginForm />);
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    test('aplica className personalizada', () => {
      const { container } = render(<LoginForm className="custom-class" />);
      expect(container.firstChild).toHaveClass('login-form', 'custom-class');
    });
  });

  describe('Validación de email', () => {
    test('muestra error para email inválido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'email-invalido');
      
      expect(screen.getByText(/por favor ingresa un email válido/i)).toBeInTheDocument();
    });

    test('no muestra error para email válido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'test@example.com');
      
      expect(screen.queryByText(/por favor ingresa un email válido/i)).not.toBeInTheDocument();
    });

    test('no muestra error cuando email está vacío', () => {
      render(<LoginForm />);
      expect(screen.queryByText(/por favor ingresa un email válido/i)).not.toBeInTheDocument();
    });
  });

  describe('Validación de password', () => {
    test('muestra error para password que no cumple requisitos', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const passwordInput = screen.getByLabelText(/password/i);
      await user.type(passwordInput, 'weak');
      
      expect(screen.getByText(/mínimo 8 caracteres, 1 mayúscula y 1 número/i)).toBeInTheDocument();
    });

    test('no muestra error para password válido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const passwordInput = screen.getByLabelText(/password/i);
      await user.type(passwordInput, 'StrongPass123');
      
      expect(screen.queryByText(/mínimo 8 caracteres, 1 mayúscula y 1 número/i)).not.toBeInTheDocument();
    });
  });

  describe('Estado del botón', () => {
    test('botón deshabilitado cuando formulario es inválido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const button = screen.getByRole('button', { name: /login/i });
      expect(button).toBeDisabled();
      
      // Email válido pero password inválido
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'weak');
      
      expect(button).toBeDisabled();
    });

    test('botón habilitado cuando formulario es válido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const button = screen.getByRole('button', { name: /login/i });
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'StrongPass123');
      
      expect(button).not.toBeDisabled();
    });
  });

  describe('Submit del formulario', () => {
    test('previene submit cuando formulario es inválido', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);
      
      const form = screen.getByRole('button', { name: /login/i }).closest('form');
      
      fireEvent.submit(form!);
      
      expect(screen.getByText(/por favor corrige los errores antes de enviar/i)).toBeInTheDocument();
      expect(fetch).not.toHaveBeenCalled();
    });

    test('realiza submit exitoso con datos válidos', async () => {
      const user = userEvent.setup();
      const mockOnLoginSuccess = jest.fn();
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Login exitoso',
          data: { user: 'test' }
        })
      } as Response);
      
      render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'StrongPass123');
      await user.click(screen.getByRole('button', { name: /login/i }));
      
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'StrongPass123',
        }),
      });

      await waitFor(() => {
        expect(screen.getByText(/inicio de sesión exitoso/i)).toBeInTheDocument();
      });

      expect(mockOnLoginSuccess).toHaveBeenCalledWith({ user: 'test' });
    });

    test('maneja error de API correctamente', async () => {
      const user = userEvent.setup();
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: false,
          message: 'Credenciales inválidas'
        })
      } as Response);
      
      render(<LoginForm />);
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'WrongPass123');
      await user.click(screen.getByRole('button', { name: /login/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/credenciales inválidas/i)).toBeInTheDocument();
      });
    });

    test('maneja error de conexión', async () => {
      const user = userEvent.setup();
      
      (fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(
        new Error('Network error')
      );
      
      render(<LoginForm />);
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'StrongPass123');
      await user.click(screen.getByRole('button', { name: /login/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/error de conexión/i)).toBeInTheDocument();
      });
    });
  });

  describe('Estados de loading', () => {
    test('muestra estado de loading durante submit', async () => {
      const user = userEvent.setup();
      
      // Mock que nunca se resuelve para simular loading
      (fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(
        () => new Promise(() => {}) // Promise que nunca se resuelve
      );
      
      render(<LoginForm />);
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'StrongPass123');
      await user.click(screen.getByRole('button', { name: /login/i }));
      
      expect(screen.getByText(/logging in\.\.\./i)).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });

  describe('Limpieza del formulario', () => {
    test('limpia formulario después de login exitoso', async () => {
      const user = userEvent.setup();
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Login exitoso',
          data: { user: 'test' }
        })
      } as Response);
      
      render(<LoginForm />);
      
      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
      
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'StrongPass123');
      await user.click(screen.getByRole('button', { name: /login/i }));
      
      await waitFor(() => {
        expect(emailInput.value).toBe('');
        expect(passwordInput.value).toBe('');
      });
    });
  });
});
