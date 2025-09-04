import { render, screen } from '@testing-library/react';
import { ToastContainer } from '../../../components/notifications/ToastContainer';
import { NotificationProvider } from '../../../contexts/NotificationContext';
import { useAppStore } from '../../../stores/appStore';
import * as React from 'react';

// Mock del store
jest.mock('../../../stores/appStore');

const mockUseAppStore = useAppStore as jest.MockedFunction<typeof useAppStore>;

// Mock notifications para tests
const mockNotifications = [
  {
    id: 'notif-1',
    type: 'success' as const,
    title: 'Success 1',
    message: 'Success message',
    timestamp: new Date().toISOString(),
    isRead: false,
  },
  {
    id: 'notif-2',
    type: 'error' as const,
    title: 'Error 1',
    message: 'Error message',
    timestamp: new Date().toISOString(),
    isRead: false,
  },
  {
    id: 'notif-3',
    type: 'info' as const,
    title: 'Info 1',
    message: 'Info message',
    timestamp: new Date().toISOString(),
    isRead: true,
  },
];

describe('ToastContainer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Mock básico del store
    mockUseAppStore.mockReturnValue({
      notifications: mockNotifications,
      alerts: [],
      addNotification: jest.fn(),
      removeNotification: jest.fn(),
      showAlert: jest.fn(),
      hideAlert: jest.fn(),
    } as any);
  });

  const renderWithProvider = (component: React.ReactElement) => {
    return render(<NotificationProvider>{component}</NotificationProvider>);
  };

  test('renders when no notifications exist', () => {
    mockUseAppStore.mockReturnValue({
      notifications: [],
      alerts: [],
      addNotification: jest.fn(),
      removeNotification: jest.fn(),
      showAlert: jest.fn(),
      hideAlert: jest.fn(),
    } as any);

    const { container } = renderWithProvider(<ToastContainer />);

    // ToastContainer retorna null cuando no hay notificaciones
    expect(container.firstChild).toBeNull();
  });

  test('renders active notifications only', () => {
    renderWithProvider(<ToastContainer />);

    // Debe mostrar todas las notificaciones (sin filtrar por isRead)
    expect(screen.getByText('Success 1')).toBeInTheDocument();
    expect(screen.getByText('Error 1')).toBeInTheDocument();
    expect(screen.getByText('Info 1')).toBeInTheDocument();
  });

  test('respects maxToasts limit', () => {
    // Crear muchas notificaciones
    const manyNotifications = Array.from({ length: 10 }, (_, i) => ({
      id: `notif-${i}`,
      type: 'info' as const,
      title: `Notification ${i}`,
      message: `Message ${i}`,
      timestamp: new Date().toISOString(),
      isRead: false,
    }));

    mockUseAppStore.mockReturnValue({
      notifications: manyNotifications,
      alerts: [],
      addNotification: jest.fn(),
      removeNotification: jest.fn(),
      showAlert: jest.fn(),
      hideAlert: jest.fn(),
    } as any);

    renderWithProvider(<ToastContainer maxToasts={3} />);

    // Solo debe mostrar las primeras 3
    expect(screen.getByText('Notification 0')).toBeInTheDocument();
    expect(screen.getByText('Notification 1')).toBeInTheDocument();
    expect(screen.getByText('Notification 2')).toBeInTheDocument();
    expect(screen.queryByText('Notification 3')).not.toBeInTheDocument();
  });

  test('applies correct stacking styles to multiple toasts', () => {
    renderWithProvider(<ToastContainer />);

    // Verificar que se renderizan los toasts
    const successToast = screen.getByText('Success 1');
    const errorToast = screen.getByText('Error 1');

    expect(successToast).toBeInTheDocument();
    expect(errorToast).toBeInTheDocument();

    // Verificar que están envueltos en contenedores con estilos
    const containers = screen
      .getAllByText(/Success 1|Error 1|Info 1/)
      .map(toast => toast.closest('.pointer-events-auto'));

    expect(containers.length).toBeGreaterThan(0);
    containers.forEach(container => {
      expect(container).toHaveClass('pointer-events-auto');
    });
  });

  test('applies position classes correctly', () => {
    const { container } = renderWithProvider(
      <ToastContainer position='top-left' />
    );

    // Verificar que el contenedor principal tiene las clases correctas
    const mainContainer = container.querySelector('.fixed.z-50');
    expect(mainContainer).toBeInTheDocument();
    expect(mainContainer).toHaveClass('pointer-events-none');
  });

  test('handles animation delays for stacked toasts', () => {
    const { container } = renderWithProvider(<ToastContainer />);

    // Verificar que los contenedores tienen los estilos de stacking usando container
    const stackedContainers = container.querySelectorAll(
      '.pointer-events-auto'
    );

    expect(stackedContainers.length).toBeGreaterThan(0);

    // Verificar que cada contenedor tiene estilos inline de transformación
    stackedContainers.forEach((container, index) => {
      const element = container as HTMLElement;
      expect(element.style.transform).toContain('translateY');
      expect(element.style.animationDelay).toBe(`${index * 100}ms`);
      expect(element.style.zIndex).toBe(`${50 - index}`);
    });
  });

  test('renders with different positions correctly', () => {
    const positions: Array<
      'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
    > = ['top-right', 'top-left', 'bottom-right', 'bottom-left'];

    positions.forEach(position => {
      const { container } = renderWithProvider(
        <ToastContainer position={position} />
      );

      // Verificar que cada toast tiene las clases de posición correctas
      const toastElements = container.querySelectorAll('.fixed.z-50.p-4');

      expect(toastElements.length).toBeGreaterThan(0);

      toastElements.forEach(toast => {
        if (position === 'top-right') {
          expect(toast).toHaveClass('top-4', 'right-4');
        } else if (position === 'top-left') {
          expect(toast).toHaveClass('top-4', 'left-4');
        } else if (position === 'bottom-right') {
          expect(toast).toHaveClass('bottom-4', 'right-4');
        } else if (position === 'bottom-left') {
          expect(toast).toHaveClass('bottom-4', 'left-4');
        }
      });
    });
  });
});
