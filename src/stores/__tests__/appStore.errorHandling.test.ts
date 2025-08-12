import { renderHook, act } from '@testing-library/react';
import { useAppStore } from '../appStore';

describe('AppStore Error Handling', () => {
  beforeEach(() => {
    // Reset store state before each test
    const { result } = renderHook(() => useAppStore());
    act(() => {
      result.current.resetAppState();
    });
  });

  describe('globalError management', () => {
    it('debe inicializar con globalError null', () => {
      const { result } = renderHook(() => useAppStore());
      expect(result.current.globalError).toBeNull();
    });

    it('debe poder setear globalError', () => {
      const { result } = renderHook(() => useAppStore());
      const errorMessage = 'Test error message';

      act(() => {
        result.current.setGlobalError(errorMessage);
      });

      expect(result.current.globalError).toBe(errorMessage);
    });

    it('debe poder limpiar globalError', () => {
      const { result } = renderHook(() => useAppStore());

      // Set error first
      act(() => {
        result.current.setGlobalError('Test error');
      });

      expect(result.current.globalError).toBe('Test error');

      // Clear error
      act(() => {
        result.current.clearGlobalError();
      });

      expect(result.current.globalError).toBeNull();
    });
  });

  describe('activeRequests management', () => {
    it('debe inicializar con activeRequests vacío', () => {
      const { result } = renderHook(() => useAppStore());
      expect(result.current.activeRequests.size).toBe(0);
      expect(result.current.hasActiveRequests).toBe(false);
    });

    it('debe agregar request activo correctamente', () => {
      const { result } = renderHook(() => useAppStore());
      const requestId = 'test-request-1';

      act(() => {
        result.current.setRequestLoading(requestId, true);
      });

      expect(result.current.activeRequests.has(requestId)).toBe(true);
      expect(result.current.hasActiveRequests).toBe(true);
    });

    it('debe remover request activo correctamente', () => {
      const { result } = renderHook(() => useAppStore());
      const requestId = 'test-request-1';

      // Add request
      act(() => {
        result.current.setRequestLoading(requestId, true);
      });

      expect(result.current.hasActiveRequests).toBe(true);

      // Remove request
      act(() => {
        result.current.setRequestLoading(requestId, false);
      });

      expect(result.current.activeRequests.has(requestId)).toBe(false);
      expect(result.current.hasActiveRequests).toBe(false);
    });

    it('debe manejar múltiples requests activos', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setRequestLoading('request-1', true);
        result.current.setRequestLoading('request-2', true);
        result.current.setRequestLoading('request-3', true);
      });

      expect(result.current.activeRequests.size).toBe(3);
      expect(result.current.hasActiveRequests).toBe(true);

      // Remove one request
      act(() => {
        result.current.setRequestLoading('request-2', false);
      });

      expect(result.current.activeRequests.size).toBe(2);
      expect(result.current.hasActiveRequests).toBe(true);

      // Remove remaining requests
      act(() => {
        result.current.setRequestLoading('request-1', false);
        result.current.setRequestLoading('request-3', false);
      });

      expect(result.current.activeRequests.size).toBe(0);
      expect(result.current.hasActiveRequests).toBe(false);
    });
  });

  describe('resetAppState', () => {
    it('debe resetear error handling state', () => {
      const { result } = renderHook(() => useAppStore());

      // Set error and active requests
      act(() => {
        result.current.setGlobalError('Test error');
        result.current.setRequestLoading('request-1', true);
        result.current.setRequestLoading('request-2', true);
      });

      expect(result.current.globalError).toBe('Test error');
      expect(result.current.activeRequests.size).toBe(2);
      expect(result.current.hasActiveRequests).toBe(true);

      // Reset state
      act(() => {
        result.current.resetAppState();
      });

      expect(result.current.globalError).toBeNull();
      expect(result.current.activeRequests.size).toBe(0);
      expect(result.current.hasActiveRequests).toBe(false);
    });
  });

  describe('selectors', () => {
    it('errorState selector debe funcionar correctamente', () => {
      const { result } = renderHook(() => useAppStore());

      // Test initial state
      const initialErrorState = result.current;
      expect(initialErrorState.globalError).toBeNull();

      // Test with error
      act(() => {
        result.current.setGlobalError('Selector test error');
      });

      expect(result.current.globalError).toBe('Selector test error');
    });

    it('loadingState selector debe incluir hasActiveRequests', () => {
      const { result } = renderHook(() => useAppStore());

      // Test initial state
      expect(result.current.hasActiveRequests).toBe(false);

      // Test with active request
      act(() => {
        result.current.setRequestLoading('selector-test', true);
      });

      expect(result.current.hasActiveRequests).toBe(true);
    });
  });
});