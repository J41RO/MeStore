import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { MenuItem } from '../MenuItem';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/admin-secure-portal/dashboard' }),
}));

const mockMenuItem = {
  id: 'dashboard',
  name: 'Dashboard',
  href: '/admin-secure-portal/dashboard',
  icon: 'ChartBarIcon'
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('MenuItem TDD - RED PHASE', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('🔴 RED: Renderizado básico', () => {
    test('debe renderizar el nombre del item correctamente', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    test('debe renderizar el ícono del item', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      // Verificar que el ícono está presente por data-testid
      expect(screen.getByTestId('menu-item-icon-ChartBarIcon')).toBeInTheDocument();
    });

    test('debe ser un botón clickeable', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('type', 'button');
    });

    test('debe incluir el href como data-attribute para testing', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('data-href', '/admin-secure-portal/dashboard');
    });
  });

  describe('🔴 RED: Estados visuales', () => {
    test('debe aplicar estilos de estado activo cuando isActive es true', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={true}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-red-100', 'text-red-900', 'border-l-4', 'border-red-500');
    });

    test('debe aplicar estilos de estado inactivo cuando isActive es false', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('text-gray-700');
      expect(button).not.toHaveClass('bg-red-100', 'text-red-900');
    });

    test('debe tener estilos hover correctos', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('hover:bg-red-50', 'hover:text-red-700');
    });

    test('debe tener transiciones CSS suaves', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('transition-colors', 'duration-200');
    });
  });

  describe('🔴 RED: Funcionalidad de click', () => {
    test('debe llamar onClick cuando se hace click', () => {
      const mockOnClick = jest.fn();

      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={mockOnClick}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockOnClick).toHaveBeenCalledTimes(1);
      expect(mockOnClick).toHaveBeenCalledWith(mockMenuItem);
    });

    test('debe navegar a la ruta correcta cuando se hace click', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');
    });

    test('debe manejar callback onItemClick opcional', () => {
      const mockOnItemClick = jest.fn();

      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
          onItemClick={mockOnItemClick}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockOnItemClick).toHaveBeenCalledWith(mockMenuItem);
    });
  });

  describe('🔴 RED: Accesibilidad', () => {
    test('debe ser focuseable por teclado', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabIndex', '0');

      // Verificar que puede recibir focus
      button.focus();
      expect(document.activeElement).toBe(button);
    });

    test('debe responder a navegación por teclado con Enter', () => {
      const mockOnClick = jest.fn();

      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={mockOnClick}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });

      expect(mockOnClick).toHaveBeenCalledTimes(1);
      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');
    });

    test('debe responder a navegación por teclado con Space', () => {
      const mockOnClick = jest.fn();

      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={mockOnClick}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: ' ', code: 'Space' });

      expect(mockOnClick).toHaveBeenCalledTimes(1);
      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');
    });

    test('debe tener aria-label descriptivo', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', expect.stringContaining('Dashboard'));
    });

    test('debe indicar estado activo con aria-current', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={true}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-current', 'page');
    });

    test('debe no tener aria-current cuando no está activo', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).not.toHaveAttribute('aria-current');
    });
  });

  describe('🔴 RED: Manejo de íconos', () => {
    test('debe renderizar íconos de Heroicons correctamente', () => {
      const itemWithIcon = {
        ...mockMenuItem,
        icon: 'UserIcon'
      };

      renderWithRouter(
        <MenuItem
          item={itemWithIcon}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      expect(screen.getByTestId('menu-item-icon-UserIcon')).toBeInTheDocument();
    });

    test('debe manejar íconos inexistentes sin crash', () => {
      const itemWithInvalidIcon = {
        ...mockMenuItem,
        icon: 'NonExistentIcon'
      };

      expect(() => {
        renderWithRouter(
          <MenuItem
            item={itemWithInvalidIcon}
            isActive={false}
            onClick={jest.fn()}
          />
        );
      }).not.toThrow();

      // Debe mostrar ícono fallback o placeholder
      expect(screen.getByTestId('menu-item-icon-fallback')).toBeInTheDocument();
    });

    test('debe aplicar clases CSS correctas al ícono', () => {
      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const icon = screen.getByTestId('menu-item-icon-ChartBarIcon');
      expect(icon).toHaveClass('w-5', 'h-5', 'mr-3');
    });
  });

  describe('🔴 RED: Props opcionales y casos edge', () => {
    test('debe funcionar sin prop onClick opcional', () => {
      expect(() => {
        renderWithRouter(
          <MenuItem
            item={mockMenuItem}
            isActive={false}
          />
        );
      }).not.toThrow();

      const button = screen.getByRole('button');
      fireEvent.click(button);

      // Debe navegar aunque no tenga onClick
      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/dashboard');
    });

    test('debe manejar items sin ícono', () => {
      const itemWithoutIcon = {
        id: 'test',
        name: 'Test Item',
        href: '/test'
        // Sin icon
      };

      renderWithRouter(
        <MenuItem
          item={itemWithoutIcon}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      expect(screen.getByText('Test Item')).toBeInTheDocument();
      // Debe mostrar ícono por defecto o sin ícono
    });

    test('debe truncar nombres muy largos correctamente', () => {
      const itemWithLongName = {
        ...mockMenuItem,
        name: 'Este es un nombre de item muy largo que podría causar problemas de layout'
      };

      renderWithRouter(
        <MenuItem
          item={itemWithLongName}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('text-sm');
    });
  });

  describe('🔴 RED: Integración con router', () => {
    test('debe detectar correctamente si la ruta actual coincide', () => {
      // Mock useLocation para ruta específica
      const mockUseLocation = jest.fn().mockReturnValue({
        pathname: '/admin-secure-portal/dashboard'
      });

      require('react-router-dom').useLocation = mockUseLocation;

      renderWithRouter(
        <MenuItem
          item={mockMenuItem}
          isActive={true}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-red-100');
    });

    test('debe manejar rutas con parámetros correctamente', () => {
      const itemWithParams = {
        ...mockMenuItem,
        href: '/admin-secure-portal/users/123'
      };

      renderWithRouter(
        <MenuItem
          item={itemWithParams}
          isActive={false}
          onClick={jest.fn()}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockNavigate).toHaveBeenCalledWith('/admin-secure-portal/users/123');
    });
  });
});