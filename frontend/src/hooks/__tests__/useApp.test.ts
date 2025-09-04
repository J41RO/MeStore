// ~/frontend/src/hooks/__tests__/useApp.test.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - useApp Hook Tests
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { renderHook, act } from '@testing-library/react';
import { useApp } from '../useApp';

describe('useApp Hook', () => {
  test('returns initial state correctly', () => {
    const { result } = renderHook(() => useApp());

    expect(result.current.theme).toBe('auto');
    expect(result.current.sidebar.isOpen).toBe(true);
    expect(result.current.sidebar.isCollapsed).toBe(false);
  });

  test('theme methods work correctly', () => {
    const { result } = renderHook(() => useApp());

    act(() => {
      result.current.enableDarkMode();
    });

    expect(result.current.theme).toBe('dark');
    expect(result.current.isDarkMode).toBe(true);
  });

  test('notification methods work correctly', () => {
    const { result } = renderHook(() => useApp());

    act(() => {
      result.current.showSuccessNotification('Success', 'Test message');
    });

    expect(result.current.notifications.count).toBe(1);
  });
});
