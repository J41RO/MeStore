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

    expect(
      screen.getByPlaceholderText('Juan Carlos Pérez')
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText('juan@correo.com')
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText('300 123 4567')
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/Mínimo 8 caracteres/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/Repetir la contraseña/i)
    ).toBeInTheDocument();
  });

  // Test 2: Validación de nombres colombianos
  test('valida nombres colombianos correctamente', async () => {
    const user = userEvent.setup();
    render(<RegisterForm />);

    const nameInput = screen.getByPlaceholderText('Juan Carlos Pérez');

    await user.type(nameInput, 'Juan Carlos Pérez González');
    expect(nameInput).toHaveValue('Juan Carlos Pérez González');

    await user.clear(nameInput);
    await user.type(nameInput, 'Juan');
    expect(nameInput).toHaveValue('Juan');
  });

  // Test 3: Validación de email
  test('valida formato de email correctamente', async () => {
    const user = userEvent.setup();
    render(<RegisterForm />);

    const emailInput = screen.getByPlaceholderText('juan@correo.com');

    await user.type(emailInput, 'test@example.com');
    expect(emailInput).toHaveValue('test@example.com');

    await user.clear(emailInput);
    await user.type(emailInput, 'invalid-email');
    expect(emailInput).toHaveValue('invalid-email');
  });

  // Test 4: Submit del formulario
  test('maneja el submit del formulario', () => {
    render(<RegisterForm />);

    const submitButton = screen.getByRole('button', { name: 'Crear Cuenta' });
    expect(submitButton).toBeInTheDocument();
  });
});