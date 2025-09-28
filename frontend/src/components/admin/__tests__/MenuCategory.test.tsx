import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { MenuCategory } from '../MenuCategory';
import { SidebarProvider } from '../SidebarProvider';

const mockMenuItems = [
  { id: 'dashboard', name: 'Dashboard', href: '/admin-secure-portal/dashboard', icon: 'ChartBarIcon' },
  { id: 'kpis', name: 'KPIs', href: '/admin-secure-portal/kpis', icon: 'PresentationChartLineIcon' },
  { id: 'overview', name: 'System Overview', href: '/admin-secure-portal/overview', icon: 'EyeIcon' },
];

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

describe('MenuCategory TDD - RED PHASE', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('🔴 RED: Estructura y renderizado básico', () => {
    test('debe renderizar el título de la categoría correctamente', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      expect(screen.getByText('Control Center')).toBeInTheDocument();
    });

    test('debe renderizar el ícono de la categoría', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      // Verificar que el ícono está presente
      const categoryHeader = screen.getByRole('button', { name: /toggle control center/i });
      expect(categoryHeader).toBeInTheDocument();

      // Verificar que el ícono de categoría está presente (por data-testid)
      expect(screen.getByTestId('category-icon-HomeIcon')).toBeInTheDocument();
    });

    test('debe renderizar el botón de toggle con ícono chevron', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });
      expect(toggleButton).toBeInTheDocument();

      // Verificar que el chevron está presente
      expect(screen.getByTestId('chevron-icon')).toBeInTheDocument();
    });

    test('debe renderizar todos los items cuando no está colapsado', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('KPIs')).toBeInTheDocument();
      expect(screen.getByText('System Overview')).toBeInTheDocument();
    });

    test('debe ocultar los items cuando está colapsado', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={true}
          onToggleCollapse={jest.fn()}
        />
      );

      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('KPIs')).not.toBeInTheDocument();
      expect(screen.queryByText('System Overview')).not.toBeInTheDocument();
    });
  });

  describe('🔴 RED: Funcionalidad de toggle', () => {
    test('debe llamar onToggleCollapse cuando se hace click en el header', () => {
      const mockToggle = jest.fn();

      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={mockToggle}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });
      fireEvent.click(toggleButton);

      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    test('debe cambiar la dirección del chevron según estado collapsed', () => {
      const { rerender } = renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const chevronIcon = screen.getByTestId('chevron-icon');

      // Cuando no está colapsado, chevron debe apuntar hacia abajo
      expect(chevronIcon).toHaveClass('rotate-90');

      rerender(
        <BrowserRouter>
          <SidebarProvider>
            <MenuCategory
              title="Control Center"
              items={mockMenuItems}
              icon="HomeIcon"
              isCollapsed={true}
              onToggleCollapse={jest.fn()}
            />
          </SidebarProvider>
        </BrowserRouter>
      );

      // Cuando está colapsado, chevron debe apuntar hacia la derecha
      expect(chevronIcon).not.toHaveClass('rotate-90');
    });

    test('debe tener transiciones CSS suaves para animaciones', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const chevronIcon = screen.getByTestId('chevron-icon');
      expect(chevronIcon).toHaveClass('transition-transform', 'duration-200');

      // Solo verificar transiciones cuando está expandido
      const itemsContainer = screen.getByTestId('menu-items-container');
      expect(itemsContainer).toHaveClass('transition-all', 'duration-300');
    });
  });

  describe('🔴 RED: Accesibilidad y ARIA', () => {
    test('debe tener atributos ARIA correctos en el botón toggle', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });

      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
      expect(toggleButton).toHaveAttribute('aria-controls', expect.stringMatching(/menu-items/));
    });

    test('debe actualizar aria-expanded según estado collapsed', () => {
      const { rerender } = renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });
      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');

      rerender(
        <BrowserRouter>
          <SidebarProvider>
            <MenuCategory
              title="Control Center"
              items={mockMenuItems}
              icon="HomeIcon"
              isCollapsed={true}
              onToggleCollapse={jest.fn()}
            />
          </SidebarProvider>
        </BrowserRouter>
      );

      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
    });

    test('debe ser navegable por teclado', () => {
      const mockToggle = jest.fn();

      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={mockToggle}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });

      // Debe ser focuseable
      expect(toggleButton).toHaveAttribute('tabIndex', '0');

      // Debe responder a Enter
      fireEvent.keyDown(toggleButton, { key: 'Enter', code: 'Enter' });
      expect(mockToggle).toHaveBeenCalledTimes(1);

      // Debe responder a Space
      fireEvent.keyDown(toggleButton, { key: ' ', code: 'Space' });
      expect(mockToggle).toHaveBeenCalledTimes(2);
    });
  });

  describe('🔴 RED: Integración con MenuItem', () => {
    test('debe pasar props correctas a cada MenuItem', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      // Verificar que cada item se renderiza con sus props
      mockMenuItems.forEach(item => {
        const menuItem = screen.getByText(item.name);
        expect(menuItem).toBeInTheDocument();

        // Verificar que el item tiene el href correcto
        const button = menuItem.closest('button');
        expect(button).toHaveAttribute('data-href', item.href);
      });
    });

    test('debe manejar categorías vacías sin errores', () => {
      renderWithProviders(
        <MenuCategory
          title="Empty Category"
          items={[]}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      expect(screen.getByText('Empty Category')).toBeInTheDocument();

      // No debe haber items de menú cuando está expandido
      const itemsContainer = screen.getByTestId('menu-items-container');
      expect(itemsContainer.children).toHaveLength(0);
    });

    test('debe pasar callback onItemClick a los MenuItem', () => {
      const mockOnItemClick = jest.fn();

      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
          onItemClick={mockOnItemClick}
        />
      );

      const dashboardItem = screen.getByText('Dashboard').closest('button');
      fireEvent.click(dashboardItem!);

      expect(mockOnItemClick).toHaveBeenCalledWith(mockMenuItems[0]);
    });
  });

  describe('🔴 RED: Estilos y clases CSS', () => {
    test('debe aplicar clases CSS correctas para el contenedor principal', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const container = screen.getByTestId('menu-category-container');
      expect(container).toHaveClass('mb-6');
    });

    test('debe aplicar estilos hover correctos al header', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const toggleButton = screen.getByRole('button', { name: /toggle control center/i });
      expect(toggleButton).toHaveClass('hover:bg-gray-50');
    });

    test('debe mostrar bordes y separadores visuales adecuados', () => {
      renderWithProviders(
        <MenuCategory
          title="Control Center"
          items={mockMenuItems}
          icon="HomeIcon"
          isCollapsed={false}
          onToggleCollapse={jest.fn()}
        />
      );

      const header = screen.getByRole('button', { name: /toggle control center/i });
      expect(header).toHaveClass('border-b', 'border-gray-200');
    });
  });
});