// ~/src/hooks/search/useSearch.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Main Search Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useSearch.ts
// Ruta: ~/src/hooks/search/useSearch.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Hook principal para funcionalidad de búsqueda
//
// ---------------------------------------------------------------------------------------------

import { useCallback, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSearchStore } from '../../stores/searchStore';
import { searchUtils } from '../../services/searchService';
import { SearchParams, UseSearchReturn } from '../../types/search.types';

/**
 * Hook principal para búsqueda con sincronización de URL
 */
export const useSearch = (): UseSearchReturn => {
  const [urlSearchParams, setUrlSearchParams] = useSearchParams();
  const store = useSearchStore();

  /**
   * Sincronizar estado con URL al montar el componente
   */
  useEffect(() => {
    const urlParams = searchUtils.parseSearchUrl(urlSearchParams);

    if (urlParams.query || Object.keys(urlParams.filters || {}).length > 0) {
      // Actualizar store con parámetros de URL
      if (urlParams.query && urlParams.query !== store.query) {
        store.search(urlParams as SearchParams);
      }

      if (urlParams.filters) {
        store.setFilters(urlParams.filters);
      }

      if (urlParams.sort && urlParams.sort !== store.sort) {
        store.setSort(urlParams.sort);
      }
    }
  }, []); // Solo al montar

  /**
   * Función de búsqueda con actualización de URL
   */
  const searchWithUrl = useCallback(
    async (params: Partial<SearchParams>) => {
      await store.search(params);

      // Actualizar URL
      const currentParams = {
        query: params.query || store.query,
        filters: { ...store.filters, ...params.filters },
        sort: params.sort || store.sort,
        page: params.page || 1,
      };

      const url = searchUtils.generateShareableUrl(currentParams as SearchParams);
      const newUrlParams = new URL(url, window.location.origin).searchParams;
      setUrlSearchParams(newUrlParams);
    },
    [store, setUrlSearchParams]
  );

  /**
   * Búsqueda rápida solo con query
   */
  const quickSearch = useCallback(
    (query: string) => {
      return searchWithUrl({ query, page: 1 });
    },
    [searchWithUrl]
  );

  /**
   * Búsqueda con filtros
   */
  const searchWithFilters = useCallback(
    (filters: Partial<SearchParams['filters']>) => {
      return searchWithUrl({ filters, page: 1 });
    },
    [searchWithUrl]
  );

  /**
   * Limpiar búsqueda y URL
   */
  const clearSearchWithUrl = useCallback(() => {
    store.clearSearch();
    setUrlSearchParams({});
  }, [store, setUrlSearchParams]);

  /**
   * Selectores memoizados
   */
  const selectors = useMemo(
    () => ({
      isSearching: store.loading.searching,
      hasResults: store.results !== null,
      hasError: store.error !== null,
      activeFiltersCount: Object.values(store.filters).filter(
        (value) =>
          Array.isArray(value) ? value.length > 0 :
          typeof value === 'boolean' ? value :
          value !== null && value !== undefined && value !== 0
      ).length,
      products: store.results?.products || [],
      totalProducts: store.results?.totalFound || 0,
      canLoadMore: store.results?.meta.hasNext && !store.loading.loadingMore,
      hasSuggestions:
        store.autocomplete.suggestions.length > 0 ||
        store.autocomplete.recentSearches.length > 0,
    }),
    [store]
  );

  return {
    // Estado del store
    ...store,

    // Selectores
    ...selectors,

    // Métodos con URL sync
    search: searchWithUrl,
    quickSearch,
    searchWithFilters,
    clearSearch: clearSearchWithUrl,
  };
};