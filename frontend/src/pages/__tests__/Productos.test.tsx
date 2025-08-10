import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Productos from '../Productos';

const renderProductos = () => {
  return render(<Productos />);
};

describe('Productos Component', () => {
  test('should render main productos title', () => {
    renderProductos();
    
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('Gestión de Productos')).toBeInTheDocument();
  });

  test('should render productos description text', () => {
    renderProductos();
    
    expect(screen.getByText('Lista de productos del vendedor')).toBeInTheDocument();
  });

  test('should render add product button', () => {
    renderProductos();
    
    const addButton = screen.getByRole('button', { name: /agregar producto/i });
    expect(addButton).toBeInTheDocument();
    expect(addButton).toHaveTextContent('Agregar Producto');
  });

  test('should have correct styling for add product button', () => {
    renderProductos();
    
    const addButton = screen.getByRole('button', { name: /agregar producto/i });
    expect(addButton).toHaveClass('bg-blue-500', 'text-white', 'px-4', 'py-2', 'rounded');
  });

  test('should render card structure with shadow', () => {
    const { container } = renderProductos();
    
    // Verificar que existe un contenedor con shadow
    const cardElement = container.querySelector('.shadow');
    expect(cardElement).toBeInTheDocument();
    
    // Verificar que tiene clase rounded-lg
    const roundedElement = container.querySelector('.rounded-lg');
    expect(roundedElement).toBeInTheDocument();
  });

  test('should allow button interaction', () => {
    renderProductos();
    
    const addButton = screen.getByRole('button', { name: /agregar producto/i });
    
    // Verificar que el botón es clickeable (no disabled)
    expect(addButton).not.toBeDisabled();
    
    // Simular click (no debería generar error)
    fireEvent.click(addButton);
    
    // El botón debería seguir presente después del click
    expect(addButton).toBeInTheDocument();
  });

  test('should render complete layout structure', () => {
    const { container } = renderProductos();
    
    // Verificar estructura principal con padding
    const mainContainer = container.querySelector('.p-6');
    expect(mainContainer).toBeInTheDocument();
    
    // Verificar que el título tiene margen bottom
    const title = screen.getByText('Gestión de Productos');
    expect(title).toHaveClass('mb-4');
  });
});
