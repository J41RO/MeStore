// ~/src/stores/searchStore.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Store with Zustand
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: searchStore.ts
// Ruta: ~/src/stores/searchStore.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Store Zustand para manejo del estado de búsqueda avanzada
//
// ---------------------------------------------------------------------------------------------

import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  SearchState,
  SearchActions,
  SearchFilters,
  SearchResult,
  SearchParams,
  SearchTerm,
  SavedSearch,
  SearchError,
  SortOption,
  ViewMode,
  SearchType,
  SearchConfig,
  AutocompleteResult,
  SearchHistory,
  LoadingStates,
} from '../types/search.types';

/**
 * Estado inicial de filtros
 */
const initialFilters: SearchFilters = {
  categories: [],
  priceRange: { min: 0, max: 999999 },
  vendors: [],
  inStock: false,
  minRating: 0,
  dateRange: { from: null, to: null },
  customFilters: {},
};

/**
 * Estado inicial de carga
 */
const initialLoadingStates: LoadingStates = {
  searching: false,
  loadingMore: false,
  suggestions: false,
  filters: false,
};

/**
 * Configuración por defecto
 */
const defaultConfig: SearchConfig = {
  debounceMs: 300,
  minQueryLength: 2,
  maxSuggestions: 10,
  maxRecentSearches: 20,
  enableVoiceSearch: false,
  enableSemanticSearch: true,
  enableFacets: true,
  defaultSort: 'relevance',
  defaultLimit: 24,
  infiniteScroll: true,
};

/**
 * Historial inicial
 */
const initialHistory: SearchHistory = {
  recent: [],
  saved: [],
  maxItems: 20,
};

/**
 * Autocomplete inicial
 */
const initialAutocomplete: AutocompleteResult = {
  suggestions: [],
  recentSearches: [],
  popularSearches: [],
  isLoading: false,
};

/**
 * Estado inicial del store
 */
const initialState: SearchState = {
  query: '',
  filters: initialFilters,
  sort: 'relevance',
  viewMode: 'grid',
  results: null,
  loading: initialLoadingStates,
  error: null,
  autocomplete: initialAutocomplete,
  history: initialHistory,
  config: defaultConfig,
  currentPage: 1,
  searchType: 'simple',
  cache: new Map(),
};

/**
 * Store de búsqueda con Zustand
 */
export const useSearchStore = create<SearchState & SearchActions>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          ...initialState,

          // Búsqueda principal
          search: async (params: Partial<SearchParams>) => {
            const state = get();
            const searchParams: SearchParams = {
              query: params.query ?? state.query,
              filters: { ...state.filters, ...params.filters },
              sort: params.sort ?? state.sort,
              page: params.page ?? 1,
              limit: params.limit ?? state.config.defaultLimit,
              type: params.type ?? state.searchType,
              facets: params.facets,
              highlight: params.highlight ?? true,
            };

            // Generar clave de cache
            const cacheKey = JSON.stringify(searchParams);

            set((draft) => {
              draft.loading.searching = true;
              draft.error = null;
              draft.query = searchParams.query;
              draft.filters = searchParams.filters as SearchFilters;
              draft.sort = searchParams.sort;
              draft.currentPage = searchParams.page;
              draft.searchType = searchParams.type;
            });

            try {
              // Verificar cache primero
              const cachedResult = state.cache.get(cacheKey);
              if (cachedResult && searchParams.page === 1) {
                set((draft) => {
                  draft.results = cachedResult;
                  draft.loading.searching = false;
                });
                return;
              }

              // Importar dinámicamente el servicio
              const { searchService } = await import('../services/searchService');
              const result = await searchService.search(searchParams);

              set((draft) => {
                if (searchParams.page === 1) {
                  draft.results = result;
                  draft.cache.set(cacheKey, result);
                } else if (draft.results) {
                  // Paginación - agregar productos
                  draft.results.products.push(...result.products);
                  draft.results.meta = result.meta;
                }
                draft.loading.searching = false;

                // Agregar al historial si hay consulta
                if (searchParams.query.trim()) {
                  const searchTerm: SearchTerm = {
                    query: searchParams.query,
                    timestamp: new Date(),
                    resultCount: result.totalFound,
                    filters: searchParams.filters,
                  };
                  draft.history.recent.unshift(searchTerm);
                  draft.history.recent = draft.history.recent.slice(0, draft.config.maxRecentSearches);
                }
              });
            } catch (error) {
              const searchError: SearchError = {
                type: 'network',
                message: error instanceof Error ? error.message : 'Error de búsqueda',
                details: error,
              };

              set((draft) => {
                draft.loading.searching = false;
                draft.error = searchError;
              });
            }
          },

          clearSearch: () => {
            set((draft) => {
              draft.query = '';
              draft.results = null;
              draft.error = null;
              draft.currentPage = 1;
              draft.autocomplete = initialAutocomplete;
            });
          },

          // Filtros
          setFilters: (filters: Partial<SearchFilters>) => {
            set((draft) => {
              draft.filters = { ...draft.filters, ...filters };
              draft.currentPage = 1;
            });

            // Buscar automáticamente si hay consulta
            const { query } = get();
            if (query.trim()) {
              get().search({});
            }
          },

          clearFilters: () => {
            set((draft) => {
              draft.filters = initialFilters;
              draft.currentPage = 1;
            });

            const { query } = get();
            if (query.trim()) {
              get().search({});
            }
          },

          toggleFilter: (key: keyof SearchFilters, value: any) => {
            set((draft) => {
              const currentValue = draft.filters[key];

              if (Array.isArray(currentValue)) {
                const index = currentValue.indexOf(value);
                if (index > -1) {
                  currentValue.splice(index, 1);
                } else {
                  currentValue.push(value);
                }
              } else if (typeof currentValue === 'boolean') {
                (draft.filters as any)[key] = !currentValue;
              } else {
                (draft.filters as any)[key] = value;
              }

              draft.currentPage = 1;
            });

            const { query } = get();
            if (query.trim()) {
              get().search({});
            }
          },

          // Ordenamiento y vista
          setSort: (sort: SortOption) => {
            set((draft) => {
              draft.sort = sort;
              draft.currentPage = 1;
            });

            const { query } = get();
            if (query.trim()) {
              get().search({});
            }
          },

          setViewMode: (mode: ViewMode) => {
            set((draft) => {
              draft.viewMode = mode;
            });
          },

          // Paginación
          loadMore: async () => {
            const state = get();
            if (!state.results?.meta.hasNext || state.loading.loadingMore) return;

            set((draft) => {
              draft.loading.loadingMore = true;
            });

            await get().search({ page: state.currentPage + 1 });

            set((draft) => {
              draft.loading.loadingMore = false;
            });
          },

          goToPage: async (page: number) => {
            await get().search({ page });
          },

          // Autocomplete
          getSuggestions: async (query: string) => {
            if (query.length < get().config.minQueryLength) {
              set((draft) => {
                draft.autocomplete = initialAutocomplete;
              });
              return;
            }

            set((draft) => {
              draft.autocomplete.isLoading = true;
            });

            try {
              const { searchService } = await import('../services/searchService');
              const suggestions = await searchService.getSuggestions(query);
              const { recent } = get().history;

              set((draft) => {
                draft.autocomplete = {
                  suggestions,
                  recentSearches: recent.slice(0, 5),
                  popularSearches: [], // TODO: Implementar popular searches
                  isLoading: false,
                };
              });
            } catch (error) {
              set((draft) => {
                draft.autocomplete.isLoading = false;
              });
            }
          },

          clearSuggestions: () => {
            set((draft) => {
              draft.autocomplete = initialAutocomplete;
            });
          },

          // Historial
          addToHistory: (term: SearchTerm) => {
            set((draft) => {
              const exists = draft.history.recent.findIndex(
                (item) => item.query === term.query
              );

              if (exists > -1) {
                draft.history.recent.splice(exists, 1);
              }

              draft.history.recent.unshift(term);
              draft.history.recent = draft.history.recent.slice(0, draft.history.maxItems);
            });
          },

          clearHistory: () => {
            set((draft) => {
              draft.history.recent = [];
            });
          },

          saveSearch: (search: Omit<SavedSearch, 'id' | 'createdAt' | 'lastUsed'>) => {
            const savedSearch: SavedSearch = {
              ...search,
              id: `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              createdAt: new Date(),
              lastUsed: new Date(),
            };

            set((draft) => {
              draft.history.saved.push(savedSearch);
            });
          },

          deleteSavedSearch: (id: string) => {
            set((draft) => {
              const index = draft.history.saved.findIndex((s) => s.id === id);
              if (index > -1) {
                draft.history.saved.splice(index, 1);
              }
            });
          },

          // Configuración
          updateConfig: (config: Partial<SearchConfig>) => {
            set((draft) => {
              draft.config = { ...draft.config, ...config };
            });
          },

          // Cache
          clearCache: () => {
            set((draft) => {
              draft.cache.clear();
            });
          },

          // Error handling
          setError: (error: SearchError | null) => {
            set((draft) => {
              draft.error = error;
            });
          },

          clearError: () => {
            set((draft) => {
              draft.error = null;
            });
          },
        }))
      ),
      {
        name: 'mestore-search',
        partialize: (state) => ({
          filters: state.filters,
          sort: state.sort,
          viewMode: state.viewMode,
          history: state.history,
          config: state.config,
        }),
        // No persistir cache, loading states, ni resultados
        version: 1,
      }
    ),
    {
      name: 'search-store',
    }
  )
);

/**
 * Selectores útiles para componentes
 */
export const searchSelectors = {
  // Estado de búsqueda
  isSearching: (state: SearchState & SearchActions) => state.loading.searching,
  hasResults: (state: SearchState & SearchActions) => state.results !== null,
  hasError: (state: SearchState & SearchActions) => state.error !== null,

  // Filtros activos
  activeFiltersCount: (state: SearchState & SearchActions) => {
    const { filters } = state;
    let count = 0;

    if (filters.categories.length > 0) count++;
    if (filters.vendors.length > 0) count++;
    if (filters.inStock) count++;
    if (filters.minRating > 0) count++;
    if (filters.priceRange.min > 0 || filters.priceRange.max < 999999) count++;
    if (filters.dateRange.from || filters.dateRange.to) count++;

    return count;
  },

  // Productos
  products: (state: SearchState & SearchActions) => state.results?.products || [],
  totalProducts: (state: SearchState & SearchActions) => state.results?.totalFound || 0,

  // Paginación
  canLoadMore: (state: SearchState & SearchActions) =>
    state.results?.meta.hasNext && !state.loading.loadingMore,

  // Autocomplete
  hasSuggestions: (state: SearchState & SearchActions) =>
    state.autocomplete.suggestions.length > 0 ||
    state.autocomplete.recentSearches.length > 0,
};

/**
 * Hook personalizado con selectores comunes
 */
export const useSearch = () => {
  const store = useSearchStore();

  return {
    ...store,
    ...searchSelectors,
    // Métodos computados adicionales
    isSearching: searchSelectors.isSearching(store),
    hasResults: searchSelectors.hasResults(store),
    hasError: searchSelectors.hasError(store),
    activeFiltersCount: searchSelectors.activeFiltersCount(store),
    products: searchSelectors.products(store),
    totalProducts: searchSelectors.totalProducts(store),
    canLoadMore: searchSelectors.canLoadMore(store),
    hasSuggestions: searchSelectors.hasSuggestions(store),
  };
};