// ~/frontend/src/stores/__tests__/appStore.test.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - AppStore Tests
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { renderHook, act } from '@testing-library/react';

// Import después de que setupTests.ts configure los mocks
import { useAppStore } from '../appStore';

describe('AppStore', () => {
  beforeEach(() => {
    // Reset store antes de cada test
    const store = useAppStore.getState();
    store.resetAppState();
  });

  test('initial state is correct', () => {
    const store = useAppStore.getState();

    expect(store.theme).toBe('auto');
    expect(store.sidebarOpen).toBe(true);
    expect(store.sidebarCollapsed).toBe(false);
    expect(store.isAppLoading).toBe(false);
    expect(store.notifications).toEqual([]);
    expect(store.alerts).toEqual([]);
    expect(store.activeModal).toBe(null);
  });

  test('theme changes work correctly', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setTheme('dark');
    });

    expect(result.current.theme).toBe('dark');
    expect(result.current.isDarkMode).toBe(true);
  });

  test('sidebar controls work correctly - toggleSidebar FIXED', () => {
    const { result } = renderHook(() => useAppStore());

    // Verificar estado inicial
    expect(result.current.sidebarOpen).toBe(true);

    // Test setSidebarOpen
    act(() => {
      result.current.setSidebarOpen(false);
    });
    expect(result.current.sidebarOpen).toBe(false);

    // Test toggleSidebar (BUG CORREGIDO)
    act(() => {
      result.current.toggleSidebar();
    });
    expect(result.current.sidebarOpen).toBe(true);

    // Test otra vez para confirmar toggle
    act(() => {
      result.current.toggleSidebar();
    });
    expect(result.current.sidebarOpen).toBe(false);
  });

  test('notifications work correctly', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.addNotification({
        type: 'success',
        title: 'Test',
        message: 'Test message',
      });
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('success');
    expect(result.current.notifications[0].title).toBe('Test');

    // Test remove notification
    const notificationId = result.current.notifications[0].id;
    act(() => {
      result.current.removeNotification(notificationId);
    });

    expect(result.current.notifications).toHaveLength(0);
  });
});
