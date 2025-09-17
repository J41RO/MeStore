// ~/src/components/search/index.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Components Index
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: index.ts
// Ruta: ~/src/components/search/index.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Exportar todos los componentes de búsqueda
//
// ---------------------------------------------------------------------------------------------

export { default as SearchBar } from './SearchBar';
export { default as SearchResults } from './SearchResults';
export { default as SearchFilters } from './SearchFilters';
export { default as SearchFacets } from './SearchFacets';
export { default as SearchSuggestions } from './SearchSuggestions';
export { default as AdvancedSearchModal } from './AdvancedSearchModal';

// Export hooks for easy access
export {
  useSearch,
  useSearchFilters,
  useSearchHistory,
  useSearchSuggestions,
  useSearchAnalytics,
} from '../../hooks/search';