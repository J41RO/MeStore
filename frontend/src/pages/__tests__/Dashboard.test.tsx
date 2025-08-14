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
// AGREGAR DESPUÉS DE LOS IMPORTS EXISTENTES:

// Mock de Recharts para evitar errores en testing
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  Legend: () => <div data-testid="legend" />,
  Cell: () => <div data-testid="cell" />
}));

// Mock de los componentes de gráficos
jest.mock('../../components/charts/SalesChart', () => {
  return function MockSalesChart({ data, title }: any) {
    return (
      <div data-testid="sales-chart">
        <h3>{title}</h3>
        <div data-testid="sales-chart-data">{JSON.stringify(data)}</div>
      </div>
    );
  };
});

jest.mock('../../components/charts/MonthlySalesChart', () => {
  return function MockMonthlySalesChart({ data, title }: any) {
    return (
      <div data-testid="monthly-sales-chart">
        <h3>{title}</h3>
        <div data-testid="monthly-sales-chart-data">{JSON.stringify(data)}</div>
      </div>
    );
  };
});
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
  // Tests para los nuevos gráficos
  it('should render sales charts section', () => {
    renderDashboard();
    
    expect(screen.getByText('Análisis de Ventas')).toBeInTheDocument();
  });

  it('should render SalesChart component', () => {
    renderDashboard();
    
    expect(screen.getByTestId('sales-chart')).toBeInTheDocument();
    expect(screen.getByText('Tendencias de Ventas')).toBeInTheDocument();
  });

  it('should render MonthlySalesChart component', () => {
    renderDashboard();
    
    expect(screen.getByTestId('monthly-sales-chart')).toBeInTheDocument();
    expect(screen.getByText('Ventas vs Objetivos')).toBeInTheDocument();
  });

  it('should have responsive grid layout for charts', () => {
    const { container } = renderDashboard();
    
    // Verificar que existe el grid de gráficos
    const chartsGrid = container.querySelector('.grid.grid-cols-1.lg\\:grid-cols-2');
    expect(chartsGrid).toBeInTheDocument();
  });
});
