import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { HierarchicalSidebar } from '../HierarchicalSidebar';
import { SidebarProvider } from '../SidebarProvider';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock para react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/admin-secure-portal/dashboard' }),
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <SidebarProvider>
        {component}
      </SidebarProvider>
    </BrowserRouter>
  );
};

describe('HierarchicalSidebar TDD - RED PHASE', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('🔴 RED: Estructura jerárquica de 4 categorías principales', () => {
    test('debe renderizar las 4 categorías principales: Control Center, User Management, Operations, System', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // Verificar que las 4 categorías principales estén presentes
      expect(screen.getByText('Control Center')).toBeInTheDocument();
      expect(screen.getByText('User Management')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
      expect(screen.getByText('System')).toBeInTheDocument();
    });

    test('debe mostrar subcategorías correctas para Control Center', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // Control Center debe tener: Dashboard, KPIs, System Overview
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('KPIs')).toBeInTheDocument();
      expect(screen.getByText('System Overview')).toBeInTheDocument();
    });

    test('debe mostrar subcategorías correctas para User Management', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // User Management debe tener: Users, Roles, Authentication
      expect(screen.getByText('Users')).toBeInTheDocument();
      expect(screen.getByText('Roles')).toBeInTheDocument();
      expect(screen.getByText('Authentication')).toBeInTheDocument();
    });

    test('debe mostrar subcategorías correctas para Operations', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // Operations debe tener: Inventory, Orders, Warehouse, Tracking
      expect(screen.getByText('Inventory')).toBeInTheDocument();
      expect(screen.getByText('Orders')).toBeInTheDocument();
      expect(screen.getByText('Warehouse')).toBeInTheDocument();
      expect(screen.getByText('Tracking')).toBeInTheDocument();
    });

    test('debe mostrar subcategorías correctas para System', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // System debe tener: Config, Reports, Audit, Alerts
      expect(screen.getByText('Config')).toBeInTheDocument();
      expect(screen.getByText('Reports')).toBeInTheDocument();
      expect(screen.getByText('Audit')).toBeInTheDocument();
      expect(screen.getByText('Alerts')).toBeInTheDocument();
    });
  });

  describe('🔴 RED: Funcionalidad collapse/expand', () => {
    test('debe permitir colapsar y expandir categorías mediante click', async () => {
      renderWithProviders(<HierarchicalSidebar />);

      // Buscar el botón de collapse para Control Center
      const controlCenterToggle = screen.getByRole('button', { name: /toggle control center/i });

      // Inicialmente las subcategorías deben estar visibles
      expect(screen.getByText('Dashboard')).toBeInTheDocument();

      // Al hacer click, las subcategorías deben ocultarse
      fireEvent.click(controlCenterToggle);

      await waitFor(() => {
        expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
      });

      // Al hacer click nuevamente, las subcategorías deben mostrarse
      fireEvent.click(controlCenterToggle);

      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
      });
    });

    test('debe mantener estado de collapse independiente por categoría', async () => {
      renderWithProviders(<HierarchicalSidebar />);

      const controlCenterToggle = screen.getByRole('button', { name: /toggle control center/i });
      const userManagementToggle = screen.getByRole('button', { name: /toggle user management/i });

      // Colapsar Control Center
      fireEvent.click(controlCenterToggle);

      await waitFor(() => {
        expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
      });

      // User Management debe seguir expandido
      expect(screen.getByText('Users')).toBeInTheDocument();

      // Colapsar User Management
      fireEvent.click(userManagementToggle);

      await waitFor(() => {
        expect(screen.queryByText('Users')).not.toBeInTheDocument();
      });
    });

    test('debe mostrar íconos de chevron correctos según estado collapse', () => {
      renderWithProviders(<HierarchicalSidebar />);

      // Buscar íconos de chevron (asumiendo que usan heroicons)
      const chevronIcons = screen.getAllByTestId(/chevron/i);
      expect(chevronIcons.length).toBeGreaterThan(0);

      // Verificar que muestran dirección correcta (down cuando expandido, right cuando colapsado)
      chevronIcons.forEach(icon => {
        expect(icon).toHaveClass('transition-transform');
      });
    });
  });

  describe('🔴 RED: Estado activo de rutas', () => {
    test('debe marcar como activo el item que coincide con la ruta actual', () => {
      // Mock useLocation para ruta específica
      const mockUseLocation = jest.fn().mockReturnValue({
        pathname: '/admin-secure-portal/dashboard'
      });

      require('react-router-dom').useLocation = mockUseLocation;

      renderWithProviders(<HierarchicalSidebar />);

      const dashboardItem = screen.getByText('Dashboard');
      expect(dashboardItem.closest('button')).toHaveClass('bg-red-100', 'text-red-900');
    });

    test('debe mantener solo un item activo a la vez', () => {
      renderWithProviders(<HierarchicalSidebar />);

      const activeItems = screen.getAllByRole('button').filter(button =>
        button.classList.contains('bg-red-100')
      );

      expect(activeItems.length).toBeLessThanOrEqual(1);
    });
  });

  describe('🔴 RED: Persistencia en localStorage', () => {
    test('debe guardar estado de collapse en localStorage', async () => {
      renderWithProviders(<HierarchicalSidebar />);

      const controlCenterToggle = screen.getByRole('button', { name: /toggle control center/i });

      fireEvent.click(controlCenterToggle);

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'sidebar-collapsed-state',
          expect.stringContaining('controlCenter')
        );
      });
    });

    test('debe restaurar estado de collapse desde localStorage al cargar', () => {
      // Mock localStorage con estado previamente guardado
      localStorageMock.getItem.mockReturnValue(
        JSON.stringify({ controlCenter: true, userManagement: false })
      );

      renderWithProviders(<HierarchicalSidebar />);

      // Control Center debe estar colapsado
      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();

      // User Management debe estar expandido
      expect(screen.getByText('Users')).toBeInTheDocument();
    });
  });

  describe('🔴 RED: Comportamiento responsive', () => {
    test('debe ser responsive y adaptarse a diferentes tamaños de pantalla', () => {
      renderWithProviders(<HierarchicalSidebar />);

      const sidebar = screen.getByRole('navigation');
      expect(sidebar).toHaveClass('transition-transform');
    });

    test('debe permitir cerrar sidebar en móvil mediante prop onClose', () => {
      const mockOnClose = jest.fn();

      renderWithProviders(<HierarchicalSidebar onClose={mockOnClose} />);

      // Simular click en item (debería cerrar sidebar en móvil)
      const dashboardItem = screen.getByText('Dashboard');
      fireEvent.click(dashboardItem);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('🔴 RED: Navegación por teclado', () => {
    test('debe permitir navegación por teclado con Tab', () => {
      renderWithProviders(<HierarchicalSidebar />);

      const buttons = screen.getAllByRole('button');

      // Todos los botones deben ser focalizables
      buttons.forEach(button => {
        expect(button).toHaveAttribute('tabIndex', '0');
      });
    });

    test('debe permitir activar items con Enter o Space', () => {
      renderWithProviders(<HierarchicalSidebar />);

      const dashboardItem = screen.getByText('Dashboard').closest('button');

      // Simular Enter
      fireEvent.keyDown(dashboardItem!, { key: 'Enter', code: 'Enter' });
      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');

      // Simular Space
      fireEvent.keyDown(dashboardItem!, { key: ' ', code: 'Space' });
      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');
    });

    test('debe permitir colapsar/expandir con Enter o Space en toggles', () => {
      renderWithProviders(<HierarchicalSidebar />);

      const controlCenterToggle = screen.getByRole('button', { name: /toggle control center/i });

      fireEvent.keyDown(controlCenterToggle, { key: 'Enter', code: 'Enter' });

      // Verificar que se activó el toggle
      expect(controlCenterToggle).toHaveAttribute('aria-expanded');
    });
  });
});