import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useApiRequest } from '../useApiRequest';

// Mock del store
vi.mock('../../stores/appStore', () => ({
  useAppStore: () => ({
    setAppLoading: vi.fn(),
    globalError: null,
    activeRequests: new Set(),
    hasActiveRequests: false,
  })
}));

describe('useApiRequest Simple Tests', () => {
  it('should initialize with correct default state', () => {
    const mockApiFunction = vi.fn();
    const { result } = renderHook(() => useApiRequest(mockApiFunction));

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.execute).toBe('function');
    expect(typeof result.current.reset).toBe('function');
  });

  it('should reset state correctly', () => {
    const mockApiFunction = vi.fn();
    const { result } = renderHook(() => useApiRequest(mockApiFunction));

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });
});
