// ~/src/hooks/search/useSearchHistory.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search History Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useSearchHistory.ts
// Ruta: ~/src/hooks/search/useSearchHistory.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Hook para gestión del historial de búsquedas
//
// ---------------------------------------------------------------------------------------------

import { useCallback, useMemo } from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { SearchTerm, SavedSearch, SearchFilters } from '../../types/search.types';

interface UseSearchHistoryReturn {
  // Historial reciente
  recentSearches: SearchTerm[];
  hasRecentSearches: boolean;

  // Búsquedas guardadas
  savedSearches: SavedSearch[];
  hasSavedSearches: boolean;

  // Métodos para historial reciente
  addToHistory: (term: SearchTerm) => void;
  removeFromHistory: (index: number) => void;
  clearHistory: () => void;
  searchFromHistory: (term: SearchTerm) => void;

  // Métodos para búsquedas guardadas
  saveCurrentSearch: (name: string, tags?: string[]) => void;
  saveSearch: (search: Omit<SavedSearch, 'id' | 'createdAt' | 'lastUsed'>) => void;
  loadSavedSearch: (id: string) => void;
  deleteSavedSearch: (id: string) => void;
  updateSavedSearch: (id: string, updates: Partial<SavedSearch>) => void;

  // Utilidades
  getPopularTerms: () => string[];
  getRecentTerms: () => string[];
  exportHistory: () => string;
  importHistory: (historyJson: string) => void;
}

/**
 * Hook para gestión del historial de búsquedas
 */
export const useSearchHistory = (): UseSearchHistoryReturn => {
  const store = useSearchStore();

  /**
   * Agregar término al historial
   */
  const addToHistory = useCallback((term: SearchTerm) => {
    store.addToHistory(term);
  }, [store]);

  /**
   * Remover término del historial por índice
   */
  const removeFromHistory = useCallback((index: number) => {
    const currentHistory = store.history.recent;
    if (index >= 0 && index < currentHistory.length) {
      const newHistory = [...currentHistory];
      newHistory.splice(index, 1);

      // Actualizar el store
      store.setFilters({}); // Trigger para actualizar historial
    }
  }, [store]);

  /**
   * Limpiar historial completo
   */
  const clearHistory = useCallback(() => {
    store.clearHistory();
  }, [store]);

  /**
   * Buscar desde historial
   */
  const searchFromHistory = useCallback((term: SearchTerm) => {
    store.search({
      query: term.query,
      filters: term.filters || {},
      page: 1,
    });
  }, [store]);

  /**
   * Guardar búsqueda actual
   */
  const saveCurrentSearch = useCallback((name: string, tags: string[] = []) => {
    const currentSearch: Omit<SavedSearch, 'id' | 'createdAt' | 'lastUsed'> = {
      name,
      query: store.query,
      filters: store.filters,
      sort: store.sort,
      isPublic: false,
      tags,
    };

    store.saveSearch(currentSearch);
  }, [store]);

  /**
   * Guardar búsqueda personalizada
   */
  const saveSearch = useCallback((search: Omit<SavedSearch, 'id' | 'createdAt' | 'lastUsed'>) => {
    store.saveSearch(search);
  }, [store]);

  /**
   * Cargar búsqueda guardada
   */
  const loadSavedSearch = useCallback((id: string) => {
    const savedSearch = store.history.saved.find(s => s.id === id);

    if (savedSearch) {
      store.search({
        query: savedSearch.query,
        filters: savedSearch.filters,
        sort: savedSearch.sort,
        page: 1,
      });

      // Actualizar lastUsed
      updateSavedSearch(id, { lastUsed: new Date() });
    }
  }, [store]);

  /**
   * Eliminar búsqueda guardada
   */
  const deleteSavedSearch = useCallback((id: string) => {
    store.deleteSavedSearch(id);
  }, [store]);

  /**
   * Actualizar búsqueda guardada
   */
  const updateSavedSearch = useCallback((id: string, updates: Partial<SavedSearch>) => {
    const savedSearches = [...store.history.saved];
    const index = savedSearches.findIndex(s => s.id === id);

    if (index > -1) {
      savedSearches[index] = { ...savedSearches[index], ...updates };

      // Actualizar el store (necesitamos un método para esto)
      // Por ahora, reemplazamos toda la lista
      store.history.saved.splice(0, store.history.saved.length, ...savedSearches);
    }
  }, [store]);

  /**
   * Obtener términos populares basados en frecuencia
   */
  const getPopularTerms = useCallback((): string[] => {
    const termFrequency: Record<string, number> = {};

    store.history.recent.forEach(term => {
      const query = term.query.toLowerCase().trim();
      if (query) {
        termFrequency[query] = (termFrequency[query] || 0) + 1;
      }
    });

    return Object.entries(termFrequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([term]) => term);
  }, [store.history.recent]);

  /**
   * Obtener términos recientes únicos
   */
  const getRecentTerms = useCallback((): string[] => {
    const uniqueTerms = new Set<string>();

    store.history.recent.forEach(term => {
      const query = term.query.toLowerCase().trim();
      if (query) {
        uniqueTerms.add(query);
      }
    });

    return Array.from(uniqueTerms).slice(0, 10);
  }, [store.history.recent]);

  /**
   * Exportar historial como JSON
   */
  const exportHistory = useCallback((): string => {
    return JSON.stringify(store.history, null, 2);
  }, [store.history]);

  /**
   * Importar historial desde JSON
   */
  const importHistory = useCallback((historyJson: string) => {
    try {
      const parsedHistory = JSON.parse(historyJson);

      // Validar estructura
      if (parsedHistory.recent && Array.isArray(parsedHistory.recent)) {
        parsedHistory.recent.forEach((term: SearchTerm) => {
          addToHistory(term);
        });
      }

      if (parsedHistory.saved && Array.isArray(parsedHistory.saved)) {
        parsedHistory.saved.forEach((search: SavedSearch) => {
          store.saveSearch(search);
        });
      }
    } catch (error) {
      console.error('Error importing history:', error);
    }
  }, [addToHistory, store]);

  /**
   * Valores memoizados
   */
  const memoizedValues = useMemo(() => ({
    recentSearches: store.history.recent,
    hasRecentSearches: store.history.recent.length > 0,
    savedSearches: store.history.saved,
    hasSavedSearches: store.history.saved.length > 0,
  }), [store.history]);

  return {
    // Estado
    ...memoizedValues,

    // Métodos para historial reciente
    addToHistory,
    removeFromHistory,
    clearHistory,
    searchFromHistory,

    // Métodos para búsquedas guardadas
    saveCurrentSearch,
    saveSearch,
    loadSavedSearch,
    deleteSavedSearch,
    updateSavedSearch,

    // Utilidades
    getPopularTerms,
    getRecentTerms,
    exportHistory,
    importHistory,
  };
};