// ~/src/hooks/search/index.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Hooks Index
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: index.ts
// Ruta: ~/src/hooks/search/index.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Exportar todos los hooks de búsqueda
//
// ---------------------------------------------------------------------------------------------

export { useSearch } from './useSearch';
export { useSearchFilters } from './useSearchFilters';
export { useSearchHistory } from './useSearchHistory';
export { useSearchSuggestions } from './useSearchSuggestions';
export { useSearchAnalytics } from './useSearchAnalytics';

// Re-export store hooks
export { useSearchStore, searchSelectors } from '../../stores/searchStore';