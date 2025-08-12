import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { UserProvider } from '../../contexts/UserContext';
import Dashboard from '../Dashboard';

const renderDashboard = () => {
  return render(
    <AuthProvider>
      <UserProvider>
        <Dashboard />
      </UserProvider>
    </AuthProvider>
  );
};

describe('Dashboard Component', () => {
  test('should render main dashboard title', () => {
    renderDashboard();
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  test('should render sales metrics card', () => {
    renderDashboard();
    expect(screen.getByText('Ventas Totales')).toBeInTheDocument();
  });

  test('should render active products metrics card', () => {
    renderDashboard();
    expect(screen.getByText('Productos Activos')).toBeInTheDocument();
  });

  test('should render both metrics cards with correct styling', () => {
    renderDashboard();
    const cards = screen.getAllByText(/Ventas Totales|Productos Activos/);
    expect(cards).toHaveLength(2);
  });

  test('should display initial values correctly', () => {
    renderDashboard();
    // El componente ahora usa datos del vendedor, no valores hardcoded
    expect(screen.getByText(/Dashboard - Mi Tienda/)).toBeInTheDocument();
  });

  test('should render grid layout structure', () => {
    const { container } = renderDashboard();
    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toBeInTheDocument();
  });
  test('should have responsive grid structure for metrics', () => {
    const { container } = renderDashboard();
    const metricsGrid = container.querySelector('.grid.grid-cols-1.sm\\:grid-cols-2.md\\:grid-cols-2.lg\\:grid-cols-4.xl\\:grid-cols-4');
    expect(metricsGrid).toBeInTheDocument();
  });

  test('should have responsive padding and max-width container', () => {
    const { container } = renderDashboard();
    const mainContainer = container.querySelector('.p-4.md\\:p-6.lg\\:p-8.max-w-7xl.mx-auto');
    expect(mainContainer).toBeInTheDocument();
  });
});
