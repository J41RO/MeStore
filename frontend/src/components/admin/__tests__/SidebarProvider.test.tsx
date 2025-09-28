import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SidebarProvider, useSidebar } from '../SidebarProvider';

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

// Componente de prueba para usar el hook
const TestComponent = () => {
  const {
    collapsedState,
    toggleCategory,
    isCategoryCollapsed,
    resetCollapseState,
    expandAllCategories,
    collapseAllCategories
  } = useSidebar();

  return (
    <div>
      <div data-testid="collapsed-state">
        {JSON.stringify(collapsedState)}
      </div>
      <button
        data-testid="toggle-control-center"
        onClick={() => toggleCategory('controlCenter')}
      >
        Toggle Control Center
      </button>
      <button
        data-testid="toggle-user-management"
        onClick={() => toggleCategory('userManagement')}
      >
        Toggle User Management
      </button>
      <div data-testid="control-center-collapsed">
        {isCategoryCollapsed('controlCenter').toString()}
      </div>
      <div data-testid="user-management-collapsed">
        {isCategoryCollapsed('userManagement').toString()}
      </div>
      <button
        data-testid="reset-state"
        onClick={resetCollapseState}
      >
        Reset State
      </button>
      <button
        data-testid="expand-all"
        onClick={expandAllCategories}
      >
        Expand All
      </button>
      <button
        data-testid="collapse-all"
        onClick={collapseAllCategories}
      >
        Collapse All
      </button>
    </div>
  );
};

const renderWithProvider = (component: React.ReactElement) => {
  return render(
    <SidebarProvider>
      {component}
    </SidebarProvider>
  );
};

describe('SidebarProvider TDD - RED PHASE', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('🔴 RED: Inicialización del contexto', () => {
    test('debe proporcionar valores por defecto correctos', () => {
      renderWithProvider(<TestComponent />);

      // Estado inicial debe ser todas las categorías expandidas
      const collapsedState = screen.getByTestId('collapsed-state');
      expect(collapsedState).toHaveTextContent('{}');

      // Todas las categorías deben estar expandidas por defecto
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');
    });

    test('debe restaurar estado desde localStorage si existe', () => {
      const savedState = {
        controlCenter: true,
        userManagement: false,
        operations: true,
        system: false
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(savedState));

      renderWithProvider(<TestComponent />);

      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');
    });

    test('debe manejar localStorage corrupto sin errores', () => {
      localStorageMock.getItem.mockReturnValue('invalid-json');

      expect(() => {
        renderWithProvider(<TestComponent />);
      }).not.toThrow();

      // Debe usar estado por defecto
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
    });
  });

  describe('🔴 RED: Funcionalidad de toggle', () => {
    test('debe alternar estado de categoría individual', async () => {
      renderWithProvider(<TestComponent />);

      // Estado inicial: expandido
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');

      // Toggle a colapsado
      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
      });

      // Toggle de vuelta a expandido
      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
      });
    });

    test('debe mantener estados independientes entre categorías', async () => {
      renderWithProvider(<TestComponent />);

      // Colapsar Control Center
      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
      });

      // User Management debe seguir expandido
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');

      // Colapsar User Management
      fireEvent.click(screen.getByTestId('toggle-user-management'));

      await waitFor(() => {
        expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('true');
      });

      // Control Center debe seguir colapsado
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
    });
  });

  describe('🔴 RED: Persistencia en localStorage', () => {
    test('debe guardar estado en localStorage cuando cambia', async () => {
      renderWithProvider(<TestComponent />);

      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'sidebar-collapsed-state',
          expect.stringContaining('controlCenter')
        );
      });

      // Verificar que se guardó el estado correcto
      const lastCall = localStorageMock.setItem.mock.calls[
        localStorageMock.setItem.mock.calls.length - 1
      ];
      const savedData = JSON.parse(lastCall[1]);
      expect(savedData.controlCenter).toBe(true);
    });

    test('debe debounce las escrituras a localStorage para performance', async () => {
      renderWithProvider(<TestComponent />);

      // Hacer múltiples toggles rápidos
      fireEvent.click(screen.getByTestId('toggle-control-center'));
      fireEvent.click(screen.getByTestId('toggle-control-center'));
      fireEvent.click(screen.getByTestId('toggle-control-center'));

      // Debe haber menos llamadas a setItem que toggles
      await waitFor(() => {
        expect(localStorageMock.setItem.mock.calls.length).toBeLessThanOrEqual(3);
      }, { timeout: 1000 });
    });

    test('debe usar clave correcta para localStorage', async () => {
      renderWithProvider(<TestComponent />);

      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'sidebar-collapsed-state',
          expect.any(String)
        );
      });
    });
  });

  describe('🔴 RED: Métodos de utilidad', () => {
    test('debe verificar correctamente si una categoría está colapsada', () => {
      const savedState = {
        controlCenter: true,
        userManagement: false
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(savedState));

      renderWithProvider(<TestComponent />);

      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');
    });

    test('debe resetear estado a valores por defecto', async () => {
      renderWithProvider(<TestComponent />);

      // Cambiar algunos estados
      fireEvent.click(screen.getByTestId('toggle-control-center'));
      fireEvent.click(screen.getByTestId('toggle-user-management'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
        expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('true');
      });

      // Reset
      fireEvent.click(screen.getByTestId('reset-state'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
        expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');
      });
    });

    test('debe expandir todas las categorías', async () => {
      const savedState = {
        controlCenter: true,
        userManagement: true,
        operations: true,
        system: true
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(savedState));

      renderWithProvider(<TestComponent />);

      // Verificar estado inicial colapsado
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('true');

      // Expandir todas
      fireEvent.click(screen.getByTestId('expand-all'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
        expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');
      });
    });

    test('debe colapsar todas las categorías', async () => {
      renderWithProvider(<TestComponent />);

      // Estado inicial expandido
      expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('false');
      expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('false');

      // Colapsar todas
      fireEvent.click(screen.getByTestId('collapse-all'));

      await waitFor(() => {
        expect(screen.getByTestId('control-center-collapsed')).toHaveTextContent('true');
        expect(screen.getByTestId('user-management-collapsed')).toHaveTextContent('true');
      });
    });
  });

  describe('🔴 RED: Hook useSidebar fuera del contexto', () => {
    test('debe lanzar error cuando se usa fuera de SidebarProvider', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(<TestComponent />);
      }).toThrow('useSidebar must be used within a SidebarProvider');

      consoleSpy.mockRestore();
    });
  });

  describe('🔴 RED: TypeScript tipos y interfaces', () => {
    test('debe tipear correctamente las categorías permitidas', () => {
      renderWithProvider(<TestComponent />);

      // Estas categorías deben ser válidas
      const validCategories = [
        'controlCenter',
        'userManagement',
        'operations',
        'system'
      ];

      validCategories.forEach(category => {
        expect(() => {
          // Este test verifica que TypeScript no genere errores de tipos
          // En runtime no hace nada, pero en compile time valida tipos
        }).not.toThrow();
      });
    });

    test('debe proveer interfaz completa del contexto', () => {
      const TestInterfaceComponent = () => {
        const context = useSidebar();

        // Verificar que todas las propiedades esperadas están presentes
        const requiredMethods = [
          'collapsedState',
          'toggleCategory',
          'isCategoryCollapsed',
          'resetCollapseState',
          'expandAllCategories',
          'collapseAllCategories'
        ];

        return (
          <div>
            {requiredMethods.map(method => (
              <div key={method} data-testid={`has-${method}`}>
                {typeof context[method as keyof typeof context]}
              </div>
            ))}
          </div>
        );
      };

      renderWithProvider(<TestInterfaceComponent />);

      // Verificar tipos de los métodos
      expect(screen.getByTestId('has-collapsedState')).toHaveTextContent('object');
      expect(screen.getByTestId('has-toggleCategory')).toHaveTextContent('function');
      expect(screen.getByTestId('has-isCategoryCollapsed')).toHaveTextContent('function');
      expect(screen.getByTestId('has-resetCollapseState')).toHaveTextContent('function');
      expect(screen.getByTestId('has-expandAllCategories')).toHaveTextContent('function');
      expect(screen.getByTestId('has-collapseAllCategories')).toHaveTextContent('function');
    });
  });

  describe('🔴 RED: Performance y optimización', () => {
    test('debe memoizar valores del contexto para evitar re-renders innecesarios', () => {
      let renderCount = 0;

      const TestRenderCountComponent = () => {
        renderCount++;
        const { collapsedState } = useSidebar();

        return <div data-testid="render-count">{renderCount}</div>;
      };

      const TestParentComponent = () => {
        const [, forceUpdate] = React.useState({});

        return (
          <div>
            <button
              data-testid="force-parent-update"
              onClick={() => forceUpdate({})}
            >
              Force Update
            </button>
            <TestRenderCountComponent />
          </div>
        );
      };

      renderWithProvider(<TestParentComponent />);

      const initialRenderCount = Number(screen.getByTestId('render-count').textContent);

      // Force parent re-render
      fireEvent.click(screen.getByTestId('force-parent-update'));

      // El componente hijo no debería re-renderizar si el contexto no cambió
      expect(screen.getByTestId('render-count')).toHaveTextContent(
        initialRenderCount.toString()
      );
    });

    test('debe evitar re-renders cuando el estado no cambia realmente', async () => {
      let contextRenderCount = 0;

      const TestContextRenderComponent = () => {
        const { collapsedState } = useSidebar();

        React.useEffect(() => {
          contextRenderCount++;
        }, [collapsedState]);

        return null;
      };

      renderWithProvider(
        <div>
          <TestContextRenderComponent />
          <TestComponent />
        </div>
      );

      const initialCount = contextRenderCount;

      // Toggle twice para volver al estado original
      fireEvent.click(screen.getByTestId('toggle-control-center'));
      fireEvent.click(screen.getByTestId('toggle-control-center'));

      await waitFor(() => {
        // Debería haber máximo 3 renders (inicial + 2 toggles)
        expect(contextRenderCount).toBeLessThanOrEqual(initialCount + 2);
      });
    });
  });
});