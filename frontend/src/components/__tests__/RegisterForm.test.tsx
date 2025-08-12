import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterForm from '../auth/RegisterForm';

// Mock fetch para tests de API
global.fetch = jest.fn();

describe('RegisterForm - Validaciones Colombianas', () => {
  beforeEach(() => {
    (fetch as jest.MockedFunction<typeof fetch>).mockClear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  // Test 1: Renderizado de todos los campos
  test('renderiza todos los campos colombianos', () => {
    render(<RegisterForm />);
    
    expect(screen.getByPlaceholderText(/juan carlos pérez/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/juan@correo.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/12345678/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/\+57 300 123 4567/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/mínimo 8 caracteres/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/repetir la contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeInTheDocument();
  });

  // Test 2: Validación de cédula colombiana
  test('valida cédula colombiana correctamente', async () => {
    render(<RegisterForm />);
    const cedulaInput = screen.getByPlaceholderText(/12345678/i);

    // Test cédula válida (8 dígitos)
    fireEvent.change(cedulaInput, { target: { value: '12345678' } });
    expect(screen.queryByText(/cédula debe tener entre 8-10 dígitos numéricos/i)).not.toBeInTheDocument();

    // Test cédula válida (10 dígitos)
    fireEvent.change(cedulaInput, { target: { value: '1234567890' } });
    expect(screen.queryByText(/cédula debe tener entre 8-10 dígitos numéricos/i)).not.toBeInTheDocument();

    // Test cédula inválida (7 dígitos)
    fireEvent.change(cedulaInput, { target: { value: '1234567' } });
    await waitFor(() => {
      expect(screen.getByText(/cédula debe tener entre 8-10 dígitos numéricos/i)).toBeInTheDocument();
    });

    // Test cédula inválida (con letras)
    fireEvent.change(cedulaInput, { target: { value: '123abc789' } });
    await waitFor(() => {
      expect(screen.getByText(/cédula debe tener entre 8-10 dígitos numéricos/i)).toBeInTheDocument();
    });
  });

  // Test 3: Validación de teléfono colombiano
  test('valida teléfono colombiano (+57) correctamente', async () => {
    render(<RegisterForm />);
    const telefonoInput = screen.getByPlaceholderText(/\+57 300 123 4567/i);

    // Test teléfono válido
    fireEvent.change(telefonoInput, { target: { value: '+57 300 123 4567' } });
    expect(screen.queryByText(/formato: \+57 300 123 4567/i)).not.toBeInTheDocument();

    // Test teléfono válido sin espacios
    fireEvent.change(telefonoInput, { target: { value: '+573001234567' } });
    expect(screen.queryByText(/formato: \+57 300 123 4567/i)).not.toBeInTheDocument();

    // Test teléfono inválido (sin +57)
    fireEvent.change(telefonoInput, { target: { value: '300 123 4567' } });
    await waitFor(() => {
      expect(screen.getByText(/formato: \+57 300 123 4567/i)).toBeInTheDocument();
    });

    // Test teléfono inválido (formato incorrecto)
    fireEvent.change(telefonoInput, { target: { value: '+57 123' } });
    await waitFor(() => {
      expect(screen.getByText(/formato: \+57 300 123 4567/i)).toBeInTheDocument();
    });
  });

  // Test 4: Validación de nombre completo
  test('valida nombre completo colombiano', async () => {
    render(<RegisterForm />);
    const nombreInput = screen.getByPlaceholderText(/juan carlos pérez/i);

    // Test nombre válido
    fireEvent.change(nombreInput, { target: { value: 'Juan Carlos Pérez' } });
    expect(screen.queryByText(/debe tener al menos 2 nombres y solo letras/i)).not.toBeInTheDocument();

    // Test nombre inválido (una sola palabra)
    fireEvent.change(nombreInput, { target: { value: 'Juan' } });
    await waitFor(() => {
      expect(screen.getByText(/debe tener al menos 2 nombres y solo letras/i)).toBeInTheDocument();
    });

    // Test nombre inválido (con números)
    fireEvent.change(nombreInput, { target: { value: 'Juan 123 Pérez' } });
    await waitFor(() => {
      expect(screen.getByText(/debe tener al menos 2 nombres y solo letras/i)).toBeInTheDocument();
    });
  });

  // Test 5: Validación de confirmación de password
  test('valida confirmación de contraseña', async () => {
    render(<RegisterForm />);
    const passwordInput = screen.getByPlaceholderText(/mínimo 8 caracteres/i);
    const confirmPasswordInput = screen.getByPlaceholderText(/repetir la contraseña/i);

    // Establecer password
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    
    // Test confirmación correcta
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    expect(screen.queryByText(/las contraseñas no coinciden/i)).not.toBeInTheDocument();

    // Test confirmación incorrecta
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password456' } });
    await waitFor(() => {
      expect(screen.getByText(/las contraseñas no coinciden/i)).toBeInTheDocument();
    });
  });

  // Test 6: Submit con datos colombianos válidos
  test('envía datos colombianos al API correctamente', async () => {
    const mockResponse = {
      success: true,
      message: '¡Registro exitoso! Bienvenido/a a MeStore'
    };

    (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const onRegisterSuccess = jest.fn();
    render(<RegisterForm onRegisterSuccess={onRegisterSuccess} />);

    // Llenar todos los campos con datos colombianos válidos
    fireEvent.change(screen.getByPlaceholderText(/juan carlos pérez/i), { 
      target: { value: 'Juan Carlos Pérez' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/juan@correo.com/i), { 
      target: { value: 'juan@correo.com' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/12345678/i), { 
      target: { value: '12345678' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/\+57 300 123 4567/i), { 
      target: { value: '+57 300 123 4567' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/mínimo 8 caracteres/i), { 
      target: { value: 'Password123' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/repetir la contraseña/i), { 
      target: { value: 'Password123' } 
    });

    // Submit del formulario
    fireEvent.click(screen.getByRole('button', { name: /registrarse/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre: 'Juan Carlos Pérez',
          email: 'juan@correo.com',
          cedula: '12345678',
          telefono: '+57 300 123 4567',
          password: 'Password123',
        }),
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/¡registro exitoso! bienvenido\/a a mestore/i)).toBeInTheDocument();
    });
  });

  // Test 7: Estados de loading y error
  test('maneja estados de loading y error correctamente', async () => {
    // Mock error response
    (fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(
      new Error('Error de conexión')
    );

    render(<RegisterForm />);

    // Llenar formulario válido
    fireEvent.change(screen.getByPlaceholderText(/juan carlos pérez/i), { 
      target: { value: 'Juan Carlos Pérez' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/juan@correo.com/i), { 
      target: { value: 'juan@correo.com' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/12345678/i), { 
      target: { value: '12345678' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/\+57 300 123 4567/i), { 
      target: { value: '+57 300 123 4567' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/mínimo 8 caracteres/i), { 
      target: { value: 'Password123' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/repetir la contraseña/i), { 
      target: { value: 'Password123' } 
    });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /registrarse/i }));

    // Verificar estado loading
    await waitFor(() => {
      expect(screen.getByText(/registrando\.\.\./i)).toBeInTheDocument();
    });

    // Verificar mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/error de conexión/i)).toBeInTheDocument();
    });
  });

  // Test 8: Botón deshabilitado con formulario inválido
  test('deshabilita botón cuando formulario es inválido', () => {
    render(<RegisterForm />);
    
    const submitButton = screen.getByRole('button', { name: /registrarse/i });
    
    // Botón deshabilitado inicialmente
    expect(submitButton).toBeDisabled();

    // Llenar solo algunos campos
    fireEvent.change(screen.getByPlaceholderText(/juan carlos pérez/i), { 
      target: { value: 'Juan Carlos' } 
    });
    fireEvent.change(screen.getByPlaceholderText(/juan@correo.com/i), { 
      target: { value: 'juan@correo.com' } 
    });

    // Botón sigue deshabilitado
    expect(submitButton).toBeDisabled();
  });
});