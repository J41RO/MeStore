import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DashboardLayout from '../DashboardLayout';

// Mock useLocation
const mockLocation = {
  pathname: '/app/dashboard',
};

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => mockLocation,
  useNavigate: () => mockNavigate,
}));

const DashboardLayoutWrapper = ({
  children,
}: {
  children: React.ReactNode;
}) => (
  <BrowserRouter>
    <DashboardLayout>{children}</DashboardLayout>
  </BrowserRouter>
);

describe('DashboardLayout', () => {
  test('renders main structure correctly', () => {
    render(
      <DashboardLayoutWrapper>
        <div>Test content</div>
      </DashboardLayoutWrapper>
    );

    // Verificar elementos principales
    expect(screen.getAllByText('MeStore')).toHaveLength(2); // Desktop + Mobile
    expect(screen.getByText('Dashboard Principal')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  test('renders navigation items', () => {
    render(
      <DashboardLayoutWrapper>
        <div>Content</div>
      </DashboardLayoutWrapper>
    );

    // Verificar items de navegación reales según DashboardLayout.tsx
    expect(screen.getAllByText('Dashboard')).toHaveLength(2); // Desktop y mobile
    expect(screen.getAllByText('Productos')).toHaveLength(2);
    expect(screen.getAllByText('Órdenes')).toHaveLength(2);
    expect(screen.getAllByText('Reportes')).toHaveLength(2);
    expect(screen.getAllByText('Comisiones')).toHaveLength(2);
    expect(screen.getAllByText('Mi Perfil')).toHaveLength(2);
  });

  test('mobile menu toggle works', () => {
    render(
      <DashboardLayoutWrapper>
        <div>Content</div>
      </DashboardLayoutWrapper>
    );

    // Encontrar botón hamburger
    const mobileMenuButton = screen.getByRole('button');

    // Verificar que el overlay no está visible inicialmente
    expect(screen.queryByTestId('mobile-overlay')).not.toBeInTheDocument();

    // Hacer click en el botón
    fireEvent.click(mobileMenuButton);

    // Verificar que se puede interactuar con el sidebar mobile
    const mobileSidebar = document.querySelector('.translate-x-0');
    expect(mobileSidebar).toBeInTheDocument();
  });

  test('active navigation state works', () => {
    render(
      <DashboardLayoutWrapper>
        <div>Content</div>
      </DashboardLayoutWrapper>
    );

    // Buscar links activos (debería haber Dashboard activo)
    const activeLinks = document.querySelectorAll('.bg-blue-100');
    expect(activeLinks.length).toBeGreaterThan(0);
  });

  test('navigation click calls navigate', () => {
    render(
      <DashboardLayoutWrapper>
        <div>Content</div>
      </DashboardLayoutWrapper>
    );

    const productosLink = screen.getAllByText('Productos')[0];
    fireEvent.click(productosLink);

    // El click debería llamar navigate con la ruta completa
    expect(mockNavigate).toHaveBeenCalledWith('/app/productos');
  });
});
