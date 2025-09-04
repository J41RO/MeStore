import { render, screen, fireEvent, act } from '@testing-library/react';
import { Toast } from '../../../components/notifications/Toast';
import { NotificationItem } from '../../../types/app.types';
import * as React from 'react';

// Mock correcto con tipos reales
const mockNotification: NotificationItem = {
  id: 'test-1',
  type: 'success',
  title: 'Test Notification',
  message: 'This is a test message',
  timestamp: new Date().toISOString(),
  isRead: false,
};

const mockOnRemove = jest.fn();

describe('Toast Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('renders notification content correctly', () => {
    render(<Toast notification={mockNotification} onRemove={mockOnRemove} />);

    expect(screen.getByText('Test Notification')).toBeInTheDocument();
    expect(screen.getByText('This is a test message')).toBeInTheDocument();
    expect(screen.getByLabelText('Cerrar notificación')).toBeInTheDocument();
  });

  test('applies correct CSS classes for success type', () => {
    const { container } = render(
      <Toast notification={mockNotification} onRemove={mockOnRemove} />
    );

    // Buscar el div principal que tiene las clases de estilo
    const toastElement = container.querySelector('.fixed.z-50.p-4');

    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass('bg-green-500');
    expect(toastElement).toHaveClass('text-white');
  });

  test('applies correct CSS classes for error type', () => {
    const errorNotification: NotificationItem = {
      ...mockNotification,
      type: 'error',
    };

    const { container } = render(
      <Toast notification={errorNotification} onRemove={mockOnRemove} />
    );

    const toastElement = container.querySelector('.fixed.z-50.p-4');

    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass('bg-red-500');
    expect(toastElement).toHaveClass('text-white');
  });

  test('applies correct position classes', () => {
    const { container } = render(
      <Toast
        notification={mockNotification}
        onRemove={mockOnRemove}
        position='bottom-left'
      />
    );

    const toastElement = container.querySelector('.fixed.z-50.p-4');

    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass('bottom-4');
    expect(toastElement).toHaveClass('left-4');
  });

  test('calls onRemove when close button is clicked', () => {
    render(<Toast notification={mockNotification} onRemove={mockOnRemove} />);

    const closeButton = screen.getByLabelText('Cerrar notificación');

    act(() => {
      fireEvent.click(closeButton);
    });

    // Avanzar timers para la animación de salida
    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(mockOnRemove).toHaveBeenCalledWith('test-1');
  });

  test('auto-removes success notifications after 5 seconds', () => {
    render(<Toast notification={mockNotification} onRemove={mockOnRemove} />);

    // Avanzar 5 segundos
    act(() => {
      jest.advanceTimersByTime(5000);
    });

    // Avanzar tiempo de animación de salida
    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(mockOnRemove).toHaveBeenCalledWith('test-1');
  });

  test('applies visibility animation classes correctly', () => {
    const { container } = render(
      <Toast notification={mockNotification} onRemove={mockOnRemove} />
    );

    const toastElement = container.querySelector('.fixed.z-50.p-4');

    // Initially should be hidden
    expect(toastElement).toHaveClass('opacity-0');
    expect(toastElement).toHaveClass('translate-x-full');

    // After animation delay should be visible
    act(() => {
      jest.advanceTimersByTime(100);
    });

    // Re-query después del update
    const updatedToastElement = container.querySelector('.fixed.z-50.p-4');
    expect(updatedToastElement).toHaveClass('opacity-100');
    expect(updatedToastElement).toHaveClass('translate-x-0');
  });

  test('does not auto-remove error notifications', () => {
    const errorNotification: NotificationItem = {
      ...mockNotification,
      type: 'error',
    };

    render(<Toast notification={errorNotification} onRemove={mockOnRemove} />);

    // Avanzar 5 segundos
    act(() => {
      jest.advanceTimersByTime(5000);
    });

    // Error notifications should not auto-remove
    expect(mockOnRemove).not.toHaveBeenCalled();
  });

  test('applies warning type styles correctly', () => {
    const warningNotification: NotificationItem = {
      ...mockNotification,
      type: 'warning',
    };

    const { container } = render(
      <Toast notification={warningNotification} onRemove={mockOnRemove} />
    );

    const toastElement = container.querySelector('.fixed.z-50.p-4');

    expect(toastElement).toHaveClass('bg-yellow-500');
    expect(toastElement).toHaveClass('text-black');
  });

  test('applies info type styles correctly', () => {
    const infoNotification: NotificationItem = {
      ...mockNotification,
      type: 'info',
    };

    const { container } = render(
      <Toast notification={infoNotification} onRemove={mockOnRemove} />
    );

    const toastElement = container.querySelector('.fixed.z-50.p-4');

    expect(toastElement).toHaveClass('bg-blue-500');
    expect(toastElement).toHaveClass('text-white');
  });
});
