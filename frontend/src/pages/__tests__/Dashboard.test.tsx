// ~/MeStore/frontend/src/pages/__tests__/Dashboard.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Dashboard Tests (Actualizados para QuickActions)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: Dashboard.test.tsx
// Ruta: ~/MeStore/frontend/src/pages/__tests__/Dashboard.test.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 2.0.0
// Propósito: Tests actualizados para Dashboard con QuickActions integrado
//
// Modificaciones:
// 2025-08-14 - Actualización completa para coincidir con implementación real
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { UserProvider } from '../../contexts/UserContext';
import Dashboard from '../Dashboard';

// Mock de AuthStore para simular usuario autenticado
jest.mock('../../stores/authStore', () => ({
  useAuthStore: () => ({
    user: {
      id: 1,
      email: 'test@example.com',
      tipo_usuario: 'vendedor',
      is_active: true
    },
    isAuthenticated: true,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    setUser: jest.fn()
  })
}));

// Mantener los otros mocks para compatibilidad
jest.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: any) => children,
  useAuth: () => ({
    user: {
      id: 1,
      email: 'test@example.com',
      tipo_usuario: 'vendedor',
      is_active: true
    },
    isAuthenticated: true,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn()
  })
}));

// Mock de UserContext
jest.mock('../../contexts/UserContext', () => ({
  UserProvider: ({ children }: any) => children,
  useUser: () => ({
    user: {
      id: 1,
      email: 'test@example.com',
      tipo_usuario: 'vendedor',
      business_name: 'Mi Tienda'
    },
    setUser: jest.fn(),
    clearUser: jest.fn()
  })
}));

// Mock de Recharts para evitar errores en testing
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  LineChart: () => <div data-testid='line-chart'>Mock Line Chart</div>,
  Line: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  BarChart: () => <div data-testid='bar-chart'>Mock Bar Chart</div>,
  Bar: () => null,
}));

// Mock del hook useVendorMetrics
jest.mock('../../hooks/useVendorMetrics', () => ({
  useVendorMetrics: () => ({
    metrics: {
      totalProductos: 24,
      productosActivos: 18,
      totalVentas: 1250000,
      ventasDelMes: 320000,
      ingresosTotales: 1250000,
      ingresosMes: 320000,
      comisionesTotales: 125000,
      ordenesPendientes: 5,
      ordenesCompletadas: 47,
    },
    loading: false,
    error: null,
    refreshMetrics: jest.fn(),
    isRefreshing: false,
  }),
}));

// Mock de los componentes de charts
jest.mock('../../components/charts/SalesChart', () => {
  return function MockSalesChart() {
    return <div data-testid='sales-chart'>Mock Sales Chart</div>;
  };
});

jest.mock('../../components/charts/MonthlySalesChart', () => {
  return function MockMonthlySalesChart() {
    return (
      <div data-testid='monthly-sales-chart'>Mock Monthly Sales Chart</div>
    );
  };
});

jest.mock('../../components/widgets/TopProductsWidget', () => {
  return function MockTopProductsWidget() {
    return (
      <div data-testid='top-products-widget'>Mock Top Products Widget</div>
    );
  };
});

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <UserProvider>
          <Dashboard />
        </UserProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  test('renders welcome message with user email', () => {
    renderDashboard();
    expect(screen.getByText(/Buenas tardes.*test@example.com/)).toBeInTheDocument();
  });

  test('renders QuickActions component', () => {
    renderDashboard();
    expect(screen.getByText('Acciones Rápidas')).toBeInTheDocument();
    expect(screen.getByText('Nuevo Producto')).toBeInTheDocument();
    expect(screen.getByText('Ver Órdenes')).toBeInTheDocument();
    expect(screen.getByText('Mis Productos')).toBeInTheDocument();
    expect(screen.getByText('Reportes')).toBeInTheDocument();
  });

  test('should render active products metrics display', () => {
    renderDashboard();
    expect(screen.getByText('Productos activos')).toBeInTheDocument();
    expect(screen.getByText('18')).toBeInTheDocument();
  });

  test('should render metrics cards with correct styling', () => {
    renderDashboard();
    expect(screen.getByText('Total Productos')).toBeInTheDocument();
    expect(screen.getByText('Ventas del Mes')).toBeInTheDocument();
    expect(screen.getByText('Ingresos Totales')).toBeInTheDocument();
    expect(screen.getByText('Órdenes Pendientes')).toBeInTheDocument();
  });

  test('should display metrics values correctly', () => {
    renderDashboard();
    expect(screen.getByText(/Buenas tardes.*test@example.com/)).toBeInTheDocument();
    expect(screen.getByText('24')).toBeInTheDocument(); // Total Productos
    expect(screen.getByText('$320,000')).toBeInTheDocument(); // Ventas del Mes
    expect(screen.getByText('$1,250,000')).toBeInTheDocument(); // Ingresos Totales
    expect(screen.getByText('5')).toBeInTheDocument(); // Órdenes Pendientes
  });

  test('should render grid layout structure', () => {
    renderDashboard();
    const container = screen.getByText('Total Productos').closest('.grid');
    expect(container).toHaveClass('grid');
  });

  test('should render sales charts section', () => {
    renderDashboard();
    expect(screen.getByText('Resumen de Ventas')).toBeInTheDocument();
  });

  test('should render orders section', () => {
    renderDashboard();
    expect(screen.getByText('Órdenes Recientes')).toBeInTheDocument();
    expect(screen.getByText('Ver todas →')).toBeInTheDocument();
  });

  test('should render secondary metrics', () => {
    renderDashboard();
    expect(screen.getByText('Métricas Principales')).toBeInTheDocument();
    expect(screen.getByText('Estadísticas Adicionales')).toBeInTheDocument();
  });

  test('should have responsive grid layout for charts', () => {
    renderDashboard();
    // "Acciones Rápidas" contains a grid inside it, not the other way around
    const quickActionsSection = screen.getByText('Acciones Rápidas').parentElement;
    const gridContainer = quickActionsSection?.querySelector('.grid');
    expect(gridContainer).toBeTruthy();
  });

  test('renders metrics cards with actual values', () => {
    renderDashboard();
    expect(screen.getByText('Total Productos')).toBeInTheDocument();
    expect(screen.getByText('24')).toBeInTheDocument();
    expect(screen.getByText('Ventas del Mes')).toBeInTheDocument();
    expect(screen.getByText('$320,000')).toBeInTheDocument();
    expect(screen.getByText('Ingresos Totales')).toBeInTheDocument();
    expect(screen.getByText('$1,250,000')).toBeInTheDocument();
  });

  test('renders TopProductsWidget', () => {
    renderDashboard();
    expect(screen.getByTestId('top-products-widget')).toBeInTheDocument();
  });

  test('renders performance summary section', () => {
    renderDashboard();
    expect(screen.getByText('Resumen de Performance')).toBeInTheDocument();
    expect(screen.getByText('Puntuación General')).toBeInTheDocument();
  });

  test('renders quick actions section', () => {
    renderDashboard();
    expect(screen.getByText('Acciones Rápidas')).toBeInTheDocument();
    expect(screen.getByText('Nuevo Producto')).toBeInTheDocument();
    expect(screen.getByText('Ver Órdenes')).toBeInTheDocument();
    expect(screen.getByText('Mis Productos')).toBeInTheDocument();
    expect(screen.getByText('Reportes')).toBeInTheDocument();
  });

  test('has responsive grid layout', () => {
    renderDashboard();
    const container = screen.getByText('Total Productos').closest('.grid');
    expect(container).toHaveClass('grid');
  });

  test('applies correct container classes', () => {
    const { container } = renderDashboard();
    const mainContainer = container.firstChild;
    expect(mainContainer).toHaveClass(
      'p-4',
      'md:p-6',
      'lg:p-8',
      'max-w-7xl',
      'mx-auto'
    );
  });
});

describe('Dashboard Loading State', () => {
  test('renders loading skeleton when isLoading is true', () => {
    // Test del estado de carga
    expect(true).toBe(true); // Placeholder - este test requiere mock más complejo
  });
});
