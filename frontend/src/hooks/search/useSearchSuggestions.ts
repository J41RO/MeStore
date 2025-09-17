// ~/src/hooks/search/useSearchSuggestions.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Suggestions Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useSearchSuggestions.ts
// Ruta: ~/src/hooks/search/useSearchSuggestions.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Hook para autocompletado y sugerencias de búsqueda
//
// ---------------------------------------------------------------------------------------------

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { searchUtils } from '../../services/searchService';
import { SearchSuggestion, AutocompleteResult } from '../../types/search.types';

interface UseSearchSuggestionsReturn {
  // Estado de sugerencias
  suggestions: SearchSuggestion[];
  recentSearches: SearchSuggestion[];
  popularSearches: SearchSuggestion[];
  isLoading: boolean;
  hasResults: boolean;

  // Métodos principales
  getSuggestions: (query: string) => void;
  clearSuggestions: () => void;
  selectSuggestion: (suggestion: SearchSuggestion) => void;

  // Navegación con teclado
  highlightedIndex: number;
  handleKeyboardNavigation: (event: KeyboardEvent) => void;
  setHighlightedIndex: (index: number) => void;

  // Utilidades
  formatSuggestion: (suggestion: SearchSuggestion) => string;
  getSuggestionIcon: (type: SearchSuggestion['type']) => string;
  groupedSuggestions: {
    queries: SearchSuggestion[];
    categories: SearchSuggestion[];
    products: SearchSuggestion[];
    vendors: SearchSuggestion[];
  };
}

/**
 * Hook para gestión de sugerencias y autocompletado
 */
export const useSearchSuggestions = (): UseSearchSuggestionsReturn => {
  const store = useSearchStore();
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const debounceRef = useRef<NodeJS.Timeout>();

  /**
   * Obtener sugerencias con debounce
   */
  const getSuggestions = useCallback((query: string) => {
    // Limpiar timeout anterior
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Limpiar si query es muy corto
    if (query.length < store.config.minQueryLength) {
      store.clearSuggestions();
      setHighlightedIndex(-1);
      return;
    }

    // Debounce para evitar muchas consultas
    debounceRef.current = setTimeout(() => {
      store.getSuggestions(query);
    }, store.config.debounceMs);
  }, [store]);

  /**
   * Limpiar sugerencias
   */
  const clearSuggestions = useCallback(() => {
    store.clearSuggestions();
    setHighlightedIndex(-1);
  }, [store]);

  /**
   * Seleccionar una sugerencia
   */
  const selectSuggestion = useCallback((suggestion: SearchSuggestion) => {
    switch (suggestion.type) {
      case 'query':
        store.search({ query: suggestion.text, page: 1 });
        break;

      case 'category':
        store.search({
          query: '',
          filters: { categories: [suggestion.text] },
          page: 1
        });
        break;

      case 'product':
        if (suggestion.metadata?.productId) {
          // Navegar directamente al producto
          window.location.href = `/product/${suggestion.metadata.productId}`;
        } else {
          store.search({ query: suggestion.text, page: 1 });
        }
        break;

      case 'vendor':
        if (suggestion.metadata?.vendorId) {
          store.search({
            query: '',
            filters: { vendors: [suggestion.metadata.vendorId] },
            page: 1
          });
        } else {
          store.search({ query: suggestion.text, page: 1 });
        }
        break;

      default:
        store.search({ query: suggestion.text, page: 1 });
    }

    clearSuggestions();
  }, [store, clearSuggestions]);

  /**
   * Navegación con teclado
   */
  const handleKeyboardNavigation = useCallback((event: KeyboardEvent) => {
    const { suggestions, recentSearches, popularSearches } = store.autocomplete;
    const allSuggestions = [...suggestions, ...recentSearches, ...popularSearches];

    if (allSuggestions.length === 0) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setHighlightedIndex(prev =>
          prev < allSuggestions.length - 1 ? prev + 1 : prev
        );
        break;

      case 'ArrowUp':
        event.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;

      case 'Enter':
        event.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < allSuggestions.length) {
          selectSuggestion(allSuggestions[highlightedIndex]);
        }
        break;

      case 'Escape':
        clearSuggestions();
        break;
    }
  }, [store.autocomplete, highlightedIndex, selectSuggestion, clearSuggestions]);

  /**
   * Formatear texto de sugerencia
   */
  const formatSuggestion = useCallback((suggestion: SearchSuggestion): string => {
    if (suggestion.highlight) {
      return suggestion.highlight;
    }

    return suggestion.text;
  }, []);

  /**
   * Obtener icono para tipo de sugerencia
   */
  const getSuggestionIcon = useCallback((type: SearchSuggestion['type']): string => {
    switch (type) {
      case 'query':
        return '🔍';
      case 'category':
        return '📂';
      case 'product':
        return '📦';
      case 'vendor':
        return '🏪';
      default:
        return '🔍';
    }
  }, []);

  /**
   * Sugerencias agrupadas por tipo
   */
  const groupedSuggestions = useMemo(() => {
    const suggestions = store.autocomplete.suggestions;

    return {
      queries: suggestions.filter(s => s.type === 'query'),
      categories: suggestions.filter(s => s.type === 'category'),
      products: suggestions.filter(s => s.type === 'product'),
      vendors: suggestions.filter(s => s.type === 'vendor'),
    };
  }, [store.autocomplete.suggestions]);

  /**
   * Limpiar timeout al desmontar
   */
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  /**
   * Resetear índice cuando cambian las sugerencias
   */
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [store.autocomplete.suggestions]);

  /**
   * Convertir términos recientes a formato de sugerencia
   */
  const recentSearches = useMemo(() => {
    return store.autocomplete.recentSearches.map(term => ({
      id: `recent_${term.timestamp.getTime()}`,
      text: term.query,
      type: 'query' as const,
      count: term.resultCount,
    }));
  }, [store.autocomplete.recentSearches]);

  /**
   * Valores calculados
   */
  const calculatedValues = useMemo(() => ({
    hasResults: store.autocomplete.suggestions.length > 0 ||
                recentSearches.length > 0 ||
                store.autocomplete.popularSearches.length > 0,
  }), [store.autocomplete, recentSearches.length]);

  return {
    // Estado
    suggestions: store.autocomplete.suggestions,
    recentSearches,
    popularSearches: store.autocomplete.popularSearches,
    isLoading: store.autocomplete.isLoading,
    hasResults: calculatedValues.hasResults,

    // Métodos principales
    getSuggestions,
    clearSuggestions,
    selectSuggestion,

    // Navegación con teclado
    highlightedIndex,
    handleKeyboardNavigation,
    setHighlightedIndex,

    // Utilidades
    formatSuggestion,
    getSuggestionIcon,
    groupedSuggestions,
  };
};