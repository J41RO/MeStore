// ~/src/types/search.types.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search System Types
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: search.types.ts
// Ruta: ~/src/types/search.types.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Tipos TypeScript para el sistema de búsqueda avanzada del marketplace
//
// ---------------------------------------------------------------------------------------------

import { Product } from './api.types';

/**
 * Tipos de búsqueda disponibles
 */
export type SearchType = 'simple' | 'advanced' | 'semantic' | 'voice';

/**
 * Modos de vista para resultados
 */
export type ViewMode = 'grid' | 'list';

/**
 * Opciones de ordenamiento
 */
export type SortOption =
  | 'relevance'
  | 'price_asc'
  | 'price_desc'
  | 'newest'
  | 'oldest'
  | 'rating'
  | 'popularity'
  | 'name_asc'
  | 'name_desc';

/**
 * Estados de carga para diferentes operaciones
 */
export interface LoadingStates {
  searching: boolean;
  loadingMore: boolean;
  suggestions: boolean;
  filters: boolean;
}

/**
 * Filtros de búsqueda avanzada
 */
export interface SearchFilters {
  categories: string[];
  priceRange: {
    min: number;
    max: number;
  };
  vendors: string[];
  inStock: boolean;
  minRating: number;
  dateRange: {
    from: Date | null;
    to: Date | null;
  };
  location?: {
    city: string;
    radius: number; // km
  };
  customFilters: Record<string, any>;
}

/**
 * Término de búsqueda con metadatos
 */
export interface SearchTerm {
  query: string;
  timestamp: Date;
  resultCount: number;
  filters?: Partial<SearchFilters>;
}

/**
 * Sugerencia de búsqueda
 */
export interface SearchSuggestion {
  id: string;
  text: string;
  type: 'query' | 'category' | 'product' | 'vendor';
  count?: number;
  highlight?: string;
  metadata?: {
    category?: string;
    vendorId?: string;
    productId?: string;
  };
}

/**
 * Resultado de autocomplete
 */
export interface AutocompleteResult {
  suggestions: SearchSuggestion[];
  recentSearches: SearchTerm[];
  popularSearches: SearchSuggestion[];
  isLoading: boolean;
}

/**
 * Faceta de filtro con contadores
 */
export interface SearchFacet {
  key: string;
  label: string;
  count: number;
  selected: boolean;
  type: 'category' | 'vendor' | 'price' | 'rating' | 'custom';
  options?: SearchFacetOption[];
}

/**
 * Opción dentro de una faceta
 */
export interface SearchFacetOption {
  value: string;
  label: string;
  count: number;
  selected: boolean;
}

/**
 * Metadatos de paginación
 */
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Resultado de búsqueda completo
 */
export interface SearchResult {
  products: Product[];
  facets: SearchFacet[];
  meta: PaginationMeta;
  searchTime: number; // ms
  totalFound: number;
  query: string;
  suggestions?: SearchSuggestion[];
  didYouMean?: string;
}

/**
 * Parámetros de búsqueda para API
 */
export interface SearchParams {
  query: string;
  filters: Partial<SearchFilters>;
  sort: SortOption;
  page: number;
  limit: number;
  type: SearchType;
  facets?: string[];
  highlight?: boolean;
}

/**
 * Estado del historial de búsqueda
 */
export interface SearchHistory {
  recent: SearchTerm[];
  saved: SavedSearch[];
  maxItems: number;
}

/**
 * Búsqueda guardada
 */
export interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters: Partial<SearchFilters>;
  sort: SortOption;
  createdAt: Date;
  lastUsed: Date;
  isPublic: boolean;
  tags: string[];
}

/**
 * Configuración de búsqueda
 */
export interface SearchConfig {
  debounceMs: number;
  minQueryLength: number;
  maxSuggestions: number;
  maxRecentSearches: number;
  enableVoiceSearch: boolean;
  enableSemanticSearch: boolean;
  enableFacets: boolean;
  defaultSort: SortOption;
  defaultLimit: number;
  infiniteScroll: boolean;
}

/**
 * Estado de error de búsqueda
 */
export interface SearchError {
  type: 'network' | 'validation' | 'server' | 'unknown';
  message: string;
  code?: string;
  details?: any;
}

/**
 * Analytics de búsqueda (opcional)
 */
export interface SearchAnalytics {
  query: string;
  timestamp: Date;
  resultCount: number;
  clickedResults: string[]; // product IDs
  filters: Partial<SearchFilters>;
  userType: 'buyer' | 'vendor' | 'admin';
  sessionId: string;
  responseTime: number;
}

/**
 * Estado completo del store de búsqueda
 */
export interface SearchState {
  // Consulta actual
  query: string;

  // Filtros activos
  filters: SearchFilters;

  // Ordenamiento
  sort: SortOption;

  // Modo de vista
  viewMode: ViewMode;

  // Resultados
  results: SearchResult | null;

  // Estados de carga
  loading: LoadingStates;

  // Error actual
  error: SearchError | null;

  // Autocomplete
  autocomplete: AutocompleteResult;

  // Historial
  history: SearchHistory;

  // Configuración
  config: SearchConfig;

  // Paginación
  currentPage: number;

  // Tipo de búsqueda actual
  searchType: SearchType;

  // Cache de resultados
  cache: Map<string, SearchResult>;
}

/**
 * Acciones del store de búsqueda
 */
export interface SearchActions {
  // Búsqueda principal
  search: (params: Partial<SearchParams>) => Promise<void>;
  clearSearch: () => void;

  // Filtros
  setFilters: (filters: Partial<SearchFilters>) => void;
  clearFilters: () => void;
  toggleFilter: (key: keyof SearchFilters, value: any) => void;

  // Ordenamiento y vista
  setSort: (sort: SortOption) => void;
  setViewMode: (mode: ViewMode) => void;

  // Paginación
  loadMore: () => Promise<void>;
  goToPage: (page: number) => Promise<void>;

  // Autocomplete
  getSuggestions: (query: string) => Promise<void>;
  clearSuggestions: () => void;

  // Historial
  addToHistory: (term: SearchTerm) => void;
  clearHistory: () => void;
  saveSearch: (search: Omit<SavedSearch, 'id' | 'createdAt' | 'lastUsed'>) => void;
  deleteSavedSearch: (id: string) => void;

  // Configuración
  updateConfig: (config: Partial<SearchConfig>) => void;

  // Cache
  clearCache: () => void;

  // Error handling
  setError: (error: SearchError | null) => void;
  clearError: () => void;
}

/**
 * Hook personalizado para búsqueda
 */
export type UseSearchReturn = SearchState & SearchActions;

/**
 * Props para componentes de búsqueda
 */
export interface SearchComponentProps {
  className?: string;
  onSearchChange?: (query: string) => void;
  onFilterChange?: (filters: Partial<SearchFilters>) => void;
  onResultClick?: (product: Product) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

/**
 * Props específicas para SearchBar
 */
export interface SearchBarProps extends SearchComponentProps {
  showVoiceSearch?: boolean;
  showAdvancedLink?: boolean;
  enableAutocomplete?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Props para SearchFilters
 */
export interface SearchFiltersProps extends SearchComponentProps {
  availableFilters: SearchFacet[];
  collapsible?: boolean;
  showClearAll?: boolean;
  orientation?: 'horizontal' | 'vertical';
}

/**
 * Props para SearchResults
 */
export interface SearchResultsProps extends SearchComponentProps {
  loading?: boolean;
  error?: SearchError | null;
  emptyStateMessage?: string;
  showSorting?: boolean;
  showViewToggle?: boolean;
  infiniteScroll?: boolean;
}

/**
 * Props para AdvancedSearchModal
 */
export interface AdvancedSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSearch: (params: SearchParams) => void;
  initialFilters?: Partial<SearchFilters>;
  className?: string;
}

/**
 * Utilidades de tipo
 */
export type SearchStore = SearchState & SearchActions;

export type FilterKey = keyof SearchFilters;

export type SearchEventHandler = (event: SearchEvent) => void;

export interface SearchEvent {
  type: 'search' | 'filter' | 'sort' | 'view_change' | 'result_click';
  data: any;
  timestamp: Date;
}