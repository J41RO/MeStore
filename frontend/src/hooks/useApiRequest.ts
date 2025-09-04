import { useState, useCallback } from 'react';
import { AxiosResponse, AxiosError } from 'axios';
import { useAppStore } from '../stores/appStore';

interface UseApiRequestState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiRequestReturn<T> extends UseApiRequestState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export const useApiRequest = <T = any>(
  apiFunction: (...args: any[]) => Promise<AxiosResponse<T>>
): UseApiRequestReturn<T> => {
  const [state, setState] = useState<UseApiRequestState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const { setAppLoading } = useAppStore();

  // Función execute se agregará en micro-fase 2
  const execute = useCallback(
    async (...args: any[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }));
      setAppLoading(true);

      try {
        const response = await apiFunction(...args);
        const responseData = response.data;

        setState({
          data: responseData,
          loading: false,
          error: null,
        });

        setAppLoading(false);
        return responseData;
      } catch (error) {
        const errorMessage =
          error instanceof AxiosError
            ? error.response?.data?.message || error.message
            : 'Error desconocido';

        setState({
          data: null,
          loading: false,
          error: errorMessage,
        });

        setAppLoading(false);
        return null;
      }
    },
    [apiFunction, setAppLoading]
  );

  // Función reset se agregará en micro-fase 3
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
};

export default useApiRequest;
