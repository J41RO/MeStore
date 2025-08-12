import { renderHook, act, waitFor } from '@testing-library/react';
import { useApiRequest } from '../useApiRequest';
import { useAppStore } from '../../stores/appStore';
import { AxiosResponse, AxiosError } from 'axios';

// Mock del store
jest.mock('../../stores/appStore');
const mockUseAppStore = useAppStore as jest.MockedFunction<typeof useAppStore>;

// Mock functions
const mockSetAppLoading = jest.fn();

describe('useApiRequest Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAppStore.mockReturnValue({
      setAppLoading: mockSetAppLoading,
    } as any);
  });

  describe('Estado inicial', () => {
    it('debe inicializar con estado correcto', () => {
      const mockApiFunction = jest.fn();
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(typeof result.current.execute).toBe('function');
      expect(typeof result.current.reset).toBe('function');
    });
  });

  describe('execute function', () => {
    it('debe manejar request exitoso correctamente', async () => {
      const mockData = { id: 1, name: 'Test' };
      const mockResponse: AxiosResponse = {
        data: mockData,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      };
      
      const mockApiFunction = jest.fn().mockResolvedValue(mockResponse);
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      await act(async () => {
        const response = await result.current.execute('param1', 'param2');
        expect(response).toEqual(mockData);
      });

      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(mockSetAppLoading).toHaveBeenCalledWith(true);
      expect(mockSetAppLoading).toHaveBeenCalledWith(false);
      expect(mockApiFunction).toHaveBeenCalledWith('param1', 'param2');
    });

    it('debe manejar errores AxiosError correctamente', async () => {
      const errorMessage = 'Request failed';
      const axiosError = new AxiosError(
        errorMessage,
        'ERR_NETWORK',
        {} as any,
        {},
        {
          data: { message: 'Server error' },
          status: 500,
          statusText: 'Internal Server Error',
          headers: {},
          config: {} as any,
        }
      );

      const mockApiFunction = jest.fn().mockRejectedValue(axiosError);
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      await act(async () => {
        const response = await result.current.execute();
        expect(response).toBeNull();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Server error');
      expect(mockSetAppLoading).toHaveBeenCalledWith(true);
      expect(mockSetAppLoading).toHaveBeenCalledWith(false);
    });

    it('debe manejar errores genéricos correctamente', async () => {
      const genericError = new Error('Generic error');
      const mockApiFunction = jest.fn().mockRejectedValue(genericError);
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      await act(async () => {
        const response = await result.current.execute();
        expect(response).toBeNull();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Error desconocido');
    });

    it('debe activar loading states durante request', async () => {
      const mockResponse = { data: { test: true }, status: 200, statusText: 'OK', headers: {}, config: {} };
      const mockApiFunction = jest.fn().mockResolvedValue(mockResponse);
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      // Estado inicial debe ser loading: false
      expect(result.current.loading).toBe(false);

      // Ejecutar request
      await act(async () => {
        await result.current.execute();
      });

      // Verificar que loading vuelve a false después del request
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toEqual({ test: true });
      expect(mockSetAppLoading).toHaveBeenCalledWith(true);
      expect(mockSetAppLoading).toHaveBeenCalledWith(false);
    });
  });

  describe('reset function', () => {
    it('debe resetear estado a valores iniciales', async () => {
      const mockData = { id: 1, name: 'Test' };
      const mockResponse: AxiosResponse = {
        data: mockData,
        status: 200,
        statusText: 'OK', 
        headers: {},
        config: {} as any,
      };

      const mockApiFunction = jest.fn().mockResolvedValue(mockResponse);
      const { result } = renderHook(() => useApiRequest(mockApiFunction));

      // Ejecutar request para tener datos
      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).toEqual(mockData);

      // Reset
      act(() => {
        result.current.reset();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });
});