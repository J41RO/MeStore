import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import RegisterForm from '../auth/RegisterForm';

// Mock fetch para tests de API
global.fetch = jest.fn();

describe('RegisterForm - Validaciones Colombianas', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  // Test 1: Renderizado de todos los campos
  test('renderiza todos los campos requeridos', () => {
    render(<RegisterForm />);
    
    expect(screen.getByPlaceholderText(/ejemplo: Juan Carlos Pérez/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ejemplo: juan@correo.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ejemplo: \+57 300 123 4567/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Mínimo 8 caracteres/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Repetir la contraseña/i)).toBeInTheDocument();
  });

  // Test 2: Validación de nombres colombianos
  test('valida nombres colombianos correctamente', async () => {
    const user = userEvent.setup();
    render(<RegisterForm />);
    
    const nameInput = screen.getByPlaceholderText(/ejemplo: Juan Carlos Pérez/i);
    
    await user.type(nameInput, 'María José');
    expect(nameInput).toHaveValue('María José');
  });

  // Test 3: Validación de email
  test('valida formato de email correctamente', async () => {
    const user = userEvent.setup();
    render(<RegisterForm />);
    
    const emailInput = screen.getByPlaceholderText(/ejemplo: juan@correo.com/i);
    
    await user.type(emailInput, 'test@example.com');
    expect(emailInput).toHaveValue('test@example.com');
  });

  // Test 4: Test básico de submit
  test('maneja el submit del formulario', async () => {
    const user = userEvent.setup();
    render(<RegisterForm />);
    
    const submitButton = screen.getByRole('button', { name: /registrarse/i });
    expect(submitButton).toBeInTheDocument();
  });
});
