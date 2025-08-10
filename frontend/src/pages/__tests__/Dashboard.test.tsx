import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../Dashboard';

const renderDashboard = () => {
  return render(<Dashboard />);
};

describe('Dashboard Component', () => {
  test('should render main dashboard title', () => {
    renderDashboard();
    
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('Dashboard de Vendedor')).toBeInTheDocument();
  });

  test('should render sales metrics card', () => {
    renderDashboard();
    
    expect(screen.getByText('Ventas del día')).toBeInTheDocument();
    expect(screen.getByText('$0')).toBeInTheDocument();
  });

  test('should render active products metrics card', () => {
    renderDashboard();
    
    expect(screen.getByText('Productos activos')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  test('should render both metrics cards with correct styling', () => {
    renderDashboard();
    
    const cards = screen.getAllByText(/Ventas del día|Productos activos/);
    expect(cards).toHaveLength(2);
    
    // Verificar que ambas cards están presentes
    expect(screen.getByText('Ventas del día')).toBeInTheDocument();
    expect(screen.getByText('Productos activos')).toBeInTheDocument();
  });

  test('should display initial values correctly', () => {
    renderDashboard();
    
    // Verificar valores iniciales
    const salesValue = screen.getByText('$0');
    const productsValue = screen.getByText('0');
    
    expect(salesValue).toBeInTheDocument();
    expect(productsValue).toBeInTheDocument();
    
    // Verificar que están en elementos con clases correctas
    expect(salesValue).toHaveClass('text-green-600');
    expect(productsValue).toHaveClass('text-blue-600');
  });

  test('should render grid layout structure', () => {
    const { container } = renderDashboard();
    
    // Verificar que existe un contenedor con grid
    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toBeInTheDocument();
    
    // Verificar que hay elementos con clase shadow (las cards)
    const shadowElements = container.querySelectorAll('.shadow');
    expect(shadowElements).toHaveLength(2);
  });
});
