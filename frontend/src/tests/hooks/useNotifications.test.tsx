import { renderHook } from '@testing-library/react';
import { useNotifications, NotificationProvider } from '../../contexts/NotificationContext';
import * as React from 'react';

// Mock del store Zustand
const mockStore = {
  notifications: [
    {
      id: '1',
      type: 'success' as const,
      title: 'Test',
      message: 'Test message',
      category: 'system' as const,
      timestamp: Date.now(),
      isRead: false
    }
  ],
  alerts: [],
  addNotification: jest.fn(),
  showAlert: jest.fn(),
  removeNotification: jest.fn(),
  hideAlert: jest.fn()
};

jest.mock('../../stores/appStore', () => ({
  useAppStore: () => mockStore
}));

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <NotificationProvider>{children}</NotificationProvider>
);

describe('useNotifications Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('returns correct notification data', () => {
    const { result } = renderHook(() => useNotifications(), { wrapper });

    expect(result.current.notifications).toEqual(mockStore.notifications);
    expect(result.current.alerts).toEqual(mockStore.alerts);
    expect(result.current.unreadCount).toBe(1);
  });

  test('provides correct method references', () => {
    const { result } = renderHook(() => useNotifications(), { wrapper });

    expect(result.current.showNotification).toBe(mockStore.addNotification);
    expect(result.current.showAlert).toBe(mockStore.showAlert);
    expect(result.current.removeNotification).toBe(mockStore.removeNotification);
    expect(result.current.hideAlert).toBe(mockStore.hideAlert);
  });

  test('calculates unread count correctly', () => {
    mockStore.notifications = [
      { id: '1', type: 'success', title: 'Test', message: 'Test', category: 'system', timestamp: Date.now(), isRead: false },
      { id: '2', type: 'info', title: 'Test', message: 'Test', category: 'system', timestamp: Date.now(), isRead: true },
      { id: '3', type: 'error', title: 'Test', message: 'Test', category: 'system', timestamp: Date.now(), isRead: false }
    ];

    const { result } = renderHook(() => useNotifications(), { wrapper });

    expect(result.current.unreadCount).toBe(2);
  });

  test('throws error when used outside provider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      renderHook(() => useNotifications());
    }).toThrow('useNotifications must be used within a NotificationProvider');

    consoleSpy.mockRestore();
  });
});