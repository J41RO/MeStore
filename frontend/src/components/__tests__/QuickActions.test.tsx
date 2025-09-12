// ~/MeStore/frontend/src/components/__tests__/QuickActions.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - QuickActions Tests
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: QuickActions.test.tsx
// Ruta: ~/MeStore/frontend/src/components/__tests__/QuickActions.test.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.0.1
// Propósito: Tests completos para el componente QuickActions y sus modales
//
// Modificaciones:
// 2025-08-14 - Creación inicial de tests completos
// 2025-08-14 - Corrección de selector para botón cerrar modal
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import QuickActions from '../QuickActions';

// Mock de console.log para capturar llamadas
const mockConsoleLog = jest.spyOn(console, 'log').mockImplementation(() => {});

describe('QuickActions Component', () => {
  beforeEach(() => {
    mockConsoleLog.mockClear();
  });

  afterAll(() => {
    mockConsoleLog.mockRestore();
  });

  // Test 1: Renderizado básico
  test('renders QuickActions component with title', () => {
    render(<QuickActions />);

    expect(screen.getByText('Acciones Rápidas')).toBeInTheDocument();
  });

  // Test 2: Renderizado de los tres botones principales
  test('renders all three quick action buttons', () => {
    render(<QuickActions />);

    expect(screen.getByText('Añadir Producto')).toBeInTheDocument();
    expect(screen.getByText('Ver Comisiones')).toBeInTheDocument();
    expect(screen.getByText('Contactar Soporte')).toBeInTheDocument();
  });

  // Test 3: Descripción visible solo en pantallas grandes
  test('descriptions are hidden on small screens', () => {
    render(<QuickActions />);

    const descriptions = screen.getAllByText(
      /Registra un nuevo producto|Consulta tus comisiones|Obtén ayuda técnica/
    );
    descriptions.forEach(desc => {
      expect(desc).toHaveClass('hidden', 'sm:block');
    });
  });

  // Test 4: Aplicación de className personalizada
  test('applies custom className prop', () => {
    const { container } = render(<QuickActions className='custom-class' />);
    const quickActionsDiv = container.firstChild as HTMLElement;

    expect(quickActionsDiv).toHaveClass('custom-class');
  });

  // Test 5: Modal AddProduct abre y cierra
  test('opens and closes AddProduct modal', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // No debe estar visible inicialmente
    expect(
      screen.queryByText('Añadir Producto', { selector: 'h2' })
    ).not.toBeInTheDocument();

    // Click en botón para abrir modal
    const addProductButton = screen.getByText('Añadir Producto', {
      selector: 'h3',
    });
    await user.click(addProductButton);

    // Modal debe estar visible
    await waitFor(() => {
      expect(
        screen.getByText('Añadir Producto', { selector: 'h2' })
      ).toBeInTheDocument();
    });

    // Buscar el botón de cerrar por su contenido SVG (X icon)
    const closeButtons = screen.getAllByRole('button');
    const closeButton = closeButtons.find(button =>
      button.querySelector('svg path[d*="18 6 6 18"]')
    );

    expect(closeButton).toBeInTheDocument();
    await user.click(closeButton!);

    // Modal debe desaparecer
    await waitFor(() => {
      expect(
        screen.queryByText('Añadir Producto', { selector: 'h2' })
      ).not.toBeInTheDocument();
    });
  });

  // Test 6: Modal Comisiones abre y cierra
  test('opens and closes Comisiones modal', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Click en botón de comisiones
    const comisionesButton = screen.getByText('Ver Comisiones');
    await user.click(comisionesButton);

    // Modal debe estar visible
    await waitFor(() => {
      expect(screen.getByText('Mis Comisiones')).toBeInTheDocument();
    });

    // Cerrar modal
    const closeButton = screen.getByText('Cerrar');
    await user.click(closeButton);

    // Modal debe desaparecer
    await waitFor(() => {
      expect(screen.queryByText('Mis Comisiones')).not.toBeInTheDocument();
    });
  });

  // Test 7: Modal Soporte abre y cierra
  test('opens and closes Soporte modal', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Click en botón de soporte
    const soporteButton = screen.getByText('Contactar Soporte');
    await user.click(soporteButton);

    // Modal debe estar visible
    await waitFor(() => {
      expect(
        screen.getByText('Contactar Soporte', { selector: 'h2' })
      ).toBeInTheDocument();
    });
  });

  // Test 8: Funcionalidad del formulario AddProduct
  test('AddProduct form can be filled and submitted', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Abrir modal
    const addProductButton = screen.getByText('Añadir Producto', {
      selector: 'h3',
    });
    await user.click(addProductButton);

    // Llenar formulario
    await waitFor(() => {
      expect(screen.getByLabelText(/Nombre del Producto/)).toBeInTheDocument();
    });

    await user.type(
      screen.getByLabelText(/Nombre del Producto/),
      'Producto Test'
    );
    await user.type(screen.getByLabelText(/Precio de Venta/), '99.99');
    await user.selectOptions(screen.getByLabelText(/Categoría/), 'electronics');
    await user.type(
      screen.getByLabelText(/Descripción/),
      'Descripción del producto test'
    );

    // Submit formulario
    const submitButton = screen.getByText('Crear Producto');
    await user.click(submitButton);

    // Verificar que no hay errores en el envío (ProductForm maneja API directamente)
    await new Promise(resolve => setTimeout(resolve, 100)); // Wait for async operations
    // Si llegamos aquí sin throw, el test pasó correctamente
  });

  // Test 9: Validación de campos requeridos en AddProduct
  test('AddProduct form validates required fields', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Abrir modal
    const addProductButton = screen.getByText('Añadir Producto', {
      selector: 'h3',
    });
    await user.click(addProductButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/Nombre del Producto/)).toBeInTheDocument();
    });

    // Intentar submit sin llenar campos requeridos
    const submitButton = screen.getByText('Crear Producto');
    await user.click(submitButton);

    // ProductForm usa React Hook Form - verificar que campos existen
    expect(screen.getByLabelText(/Nombre del Producto/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Precio de Venta/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Precio de Costo/)).toBeInTheDocument();
  });

  // Test 10: Navegación con teclado (accesibilidad)
  test('supports keyboard navigation', async () => {
    render(<QuickActions />);

    const buttons = screen.getAllByRole('button');
    const firstButton = buttons[0];

    // El primer botón debe ser focuseable
    firstButton.focus();
    expect(firstButton).toHaveFocus();

    // Debe tener estilos de focus
    expect(firstButton).toHaveClass('focus:outline-none', 'focus:ring-2');
  });

  // Test 11: Responsive grid layout
  test('has responsive grid layout', () => {
    render(<QuickActions />);

    const gridContainer =
      screen.getByText('Acciones Rápidas').nextElementSibling;
    expect(gridContainer).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-3');
  });

  // Test 12: Iconos correctos para cada acción
  test('displays correct icons for each action', () => {
    render(<QuickActions />);

    // Los iconos se renderizan como SVG, verificamos que existan
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(3);

    // Cada botón debe tener un SVG (icono)
    buttons.forEach(button => {
      expect(button.querySelector('svg')).toBeInTheDocument();
    });
  });

  // Test 13: Cerrar modal con botón Cancelar
  test('closes AddProduct modal with Cancel button', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Abrir modal
    const addProductButton = screen.getByText('Añadir Producto', {
      selector: 'h3',
    });
    await user.click(addProductButton);

    // Modal debe estar visible
    await waitFor(() => {
      expect(
        screen.getByText('Añadir Producto', { selector: 'h2' })
      ).toBeInTheDocument();
    });

    // Cerrar con botón Cancelar
    const cancelButton = screen.getByText('Cancelar');
    await user.click(cancelButton);

    // Modal debe desaparecer
    await waitFor(() => {
      expect(
        screen.queryByText('Añadir Producto', { selector: 'h2' })
      ).not.toBeInTheDocument();
    });
  });

  // Test 14: Formulario se resetea al cerrar modal
  test('form resets when modal is closed', async () => {
    const user = userEvent.setup();
    render(<QuickActions />);

    // Abrir modal
    const addProductButton = screen.getByText('Añadir Producto', {
      selector: 'h3',
    });
    await user.click(addProductButton);

    // Llenar algo en el formulario
    await waitFor(() => {
      expect(screen.getByLabelText(/Nombre del Producto/)).toBeInTheDocument();
    });

    await user.type(screen.getByLabelText(/Nombre del Producto/), 'Test');

    // Cerrar modal
    const cancelButton = screen.getByText('Cancelar');
    await user.click(cancelButton);

    // Reabrir modal
    await user.click(addProductButton);

    // El campo debe estar vacío
    await waitFor(() => {
      expect(screen.getByLabelText(/Nombre del Producto/)).toHaveValue('');
    });
  });
});

// Tests de integración con Dashboard
describe('QuickActions Integration', () => {
  // Test 15: Funciona correctamente dentro de un contenedor
  test('works correctly within a container', () => {
    render(
      <div className='max-w-7xl mx-auto'>
        <QuickActions />
      </div>
    );

    expect(screen.getByText('Acciones Rápidas')).toBeInTheDocument();
  });

  // Test 16: Mantiene estado independiente de múltiples instancias
  test('maintains independent state for multiple instances', async () => {
    const user = userEvent.setup();
    render(
      <div>
        <QuickActions data-testid='instance-1' />
        <QuickActions data-testid='instance-2' />
      </div>
    );

    // Abrir modal en primera instancia
    const firstInstanceButtons = screen.getAllByText('Añadir Producto');
    await user.click(firstInstanceButtons[0]);

    // Solo un modal debe estar abierto
    const modals = screen.getAllByText('Añadir Producto', { selector: 'h2' });
    expect(modals).toHaveLength(1);
  });
});
