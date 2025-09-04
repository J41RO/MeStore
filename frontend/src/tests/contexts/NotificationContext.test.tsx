import { render, screen, act } from '@testing-library/react';
import {
  NotificationProvider,
  useNotifications,
} from '../../contexts/NotificationContext';
import * as React from 'react';

// Mock del store Zustand
const mockStore = {
  notifications: [],
  alerts: [],
  addNotification: jest.fn(),
  showAlert: jest.fn(),
  removeNotification: jest.fn(),
  hideAlert: jest.fn(),
};

jest.mock('../../stores/appStore', () => ({
  useAppStore: () => mockStore,
}));

// Componente de prueba para usar el hook
const TestComponent = () => {
  const {
    notifications,
    alerts,
    unreadCount,
    showNotification,
    showAlert,
    removeNotification,
    hideAlert,
  } = useNotifications();

  return (
    <div>
      <div data-testid='notifications-count'>{notifications.length}</div>
      <div data-testid='alerts-count'>{alerts.length}</div>
      <div data-testid='unread-count'>{unreadCount}</div>
      <button
        onClick={() =>
          showNotification({
            type: 'success',
            title: 'Test',
            message: 'Test message',
            category: 'system',
          })
        }
      >
        Add Notification
      </button>
      <button
        onClick={() =>
          showAlert({
            type: 'warning',
            title: 'Test Alert',
            message: 'Test alert message',
            category: 'user',
          })
        }
      >
        Show Alert
      </button>
      <button onClick={() => removeNotification('test-id')}>
        Remove Notification
      </button>
      <button onClick={() => hideAlert('alert-id')}>Hide Alert</button>
    </div>
  );
};

describe('NotificationContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockStore.notifications = [];
    mockStore.alerts = [];
  });

  test('provides notification context values', () => {
    render(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );

    expect(screen.getByTestId('notifications-count')).toHaveTextContent('0');
    expect(screen.getByTestId('alerts-count')).toHaveTextContent('0');
    expect(screen.getByTestId('unread-count')).toHaveTextContent('0');
  });

  test('calculates unread count correctly', () => {
    mockStore.notifications = [
      {
        id: '1',
        type: 'success',
        title: 'Test',
        message: 'Test',
        category: 'system',
        timestamp: Date.now(),
        isRead: false,
      },
      {
        id: '2',
        type: 'info',
        title: 'Test',
        message: 'Test',
        category: 'system',
        timestamp: Date.now(),
        isRead: true,
      },
      {
        id: '3',
        type: 'error',
        title: 'Test',
        message: 'Test',
        category: 'system',
        timestamp: Date.now(),
        isRead: false,
      },
    ];

    render(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );

    expect(screen.getByTestId('unread-count')).toHaveTextContent('2');
  });

  test('calls store methods when context methods are called', () => {
    render(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );

    act(() => {
      screen.getByText('Add Notification').click();
    });
    expect(mockStore.addNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Test',
      message: 'Test message',
      category: 'system',
    });

    act(() => {
      screen.getByText('Show Alert').click();
    });
    expect(mockStore.showAlert).toHaveBeenCalledWith({
      type: 'warning',
      title: 'Test Alert',
      message: 'Test alert message',
      category: 'user',
    });

    act(() => {
      screen.getByText('Remove Notification').click();
    });
    expect(mockStore.removeNotification).toHaveBeenCalledWith('test-id');

    act(() => {
      screen.getByText('Hide Alert').click();
    });
    expect(mockStore.hideAlert).toHaveBeenCalledWith('alert-id');
  });

  test('throws error when used outside provider', () => {
    const consoleSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useNotifications must be used within a NotificationProvider');

    consoleSpy.mockRestore();
  });
});
