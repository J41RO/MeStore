// ~/src/components/search/SearchFacets.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - SearchFacets Component for Filter Management
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchFacets.tsx
// Ruta: ~/src/components/search/SearchFacets.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente de facetas dinámicas para filtros de búsqueda
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useState, useCallback, useMemo } from 'react';
import {
  Plus,
  Minus,
  BarChart3,
  Filter,
  X,
  ChevronDown,
  ChevronUp,
  Hash,
  Percent,
} from 'lucide-react';
import { useSearch } from '../../hooks/search';
import { SearchFacet, SearchFacetOption } from '../../types/search.types';

interface SearchFacetsProps {
  className?: string;
  showCounts?: boolean;
  maxOptionsPerFacet?: number;
  collapsible?: boolean;
  orientation?: 'horizontal' | 'vertical';
}

interface FacetSectionProps {
  facet: SearchFacet;
  onOptionToggle: (facetKey: string, optionValue: string) => void;
  showCounts: boolean;
  maxOptions: number;
  isCollapsible: boolean;
}

/**
 * Componente individual de faceta
 */
const FacetSection: React.FC<FacetSectionProps> = memo(({
  facet,
  onOptionToggle,
  showCounts,
  maxOptions,
  isCollapsible,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);

  /**
   * Opciones a mostrar
   */
  const visibleOptions = useMemo(() => {
    if (!facet.options) return [];

    const sortedOptions = [...facet.options].sort((a, b) => {
      // Opciones seleccionadas primero
      if (a.selected && !b.selected) return -1;
      if (!a.selected && b.selected) return 1;
      // Luego por cantidad (descendente)
      return b.count - a.count;
    });

    return showAll ? sortedOptions : sortedOptions.slice(0, maxOptions);
  }, [facet.options, showAll, maxOptions]);

  /**
   * Opciones seleccionadas
   */
  const selectedCount = useMemo(() => {
    return facet.options?.filter(option => option.selected).length || 0;
  }, [facet.options]);

  /**
   * Hay más opciones para mostrar
   */
  const hasMoreOptions = (facet.options?.length || 0) > maxOptions;

  /**
   * Toggle de opción
   */
  const handleOptionToggle = useCallback((optionValue: string) => {
    onOptionToggle(facet.key, optionValue);
  }, [facet.key, onOptionToggle]);

  /**
   * Icono de faceta basado en tipo
   */
  const getFacetIcon = () => {
    switch (facet.type) {
      case 'category':
        return <Filter className="w-4 h-4" />;
      case 'vendor':
        return <Hash className="w-4 h-4" />;
      case 'price':
        return <span className="w-4 h-4 flex items-center justify-center text-sm">$</span>;
      case 'rating':
        return <BarChart3 className="w-4 h-4" />;
      default:
        return <Filter className="w-4 h-4" />;
    }
  };

  /**
   * Color basado en tipo de faceta
   */
  const getFacetColor = () => {
    switch (facet.type) {
      case 'category':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'vendor':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'price':
        return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'rating':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      {/* Header de faceta */}
      <div
        className={`p-3 border-b border-gray-200 ${
          isCollapsible ? 'cursor-pointer hover:bg-gray-50' : ''
        }`}
        onClick={() => isCollapsible && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`p-1 rounded ${getFacetColor()}`}>
              {getFacetIcon()}
            </div>
            <span className="font-medium text-gray-900">{facet.label}</span>
            {selectedCount > 0 && (
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
                {selectedCount}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-1">
            {showCounts && (
              <span className="text-xs text-gray-500">
                ({facet.count})
              </span>
            )}
            {isCollapsible && (
              isExpanded ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )
            )}
          </div>
        </div>
      </div>

      {/* Opciones de faceta */}
      {isExpanded && (
        <div className="p-3">
          <div className="space-y-2">
            {visibleOptions.map((option) => (
              <label
                key={option.value}
                className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 rounded p-2 transition-colors"
              >
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={option.selected}
                    onChange={() => handleOptionToggle(option.value)}
                    className="sr-only"
                  />
                  <div
                    className={`w-4 h-4 border-2 rounded transition-all ${
                      option.selected
                        ? 'bg-blue-600 border-blue-600'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {option.selected && (
                      <div className="w-2 h-2 bg-white rounded-sm m-0.5" />
                    )}
                  </div>
                </div>

                <span className="flex-1 text-sm text-gray-700 truncate">
                  {option.label}
                </span>

                {showCounts && (
                  <span className="text-xs text-gray-500 flex items-center">
                    <Hash className="w-3 h-3 mr-1" />
                    {option.count.toLocaleString()}
                  </span>
                )}
              </label>
            ))}
          </div>

          {/* Mostrar más/menos */}
          {hasMoreOptions && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <button
                onClick={() => setShowAll(!showAll)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-1"
              >
                {showAll ? (
                  <>
                    <Minus className="w-4 h-4" />
                    <span>Mostrar menos</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    <span>
                      Mostrar {(facet.options?.length || 0) - maxOptions} más
                    </span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Estadísticas de faceta */}
          {selectedCount > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{selectedCount} seleccionado{selectedCount > 1 ? 's' : ''}</span>
                <div className="flex items-center space-x-1">
                  <Percent className="w-3 h-3" />
                  <span>
                    {Math.round((selectedCount / (facet.options?.length || 1)) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

FacetSection.displayName = 'FacetSection';

/**
 * Chip de filtro activo
 */
const FilterChip: React.FC<{
  facet: SearchFacet;
  option: SearchFacetOption;
  onRemove: () => void;
}> = memo(({ facet, option, onRemove }) => {
  const getChipColor = () => {
    switch (facet.type) {
      case 'category':
        return 'bg-blue-100 text-blue-800 hover:bg-blue-200';
      case 'vendor':
        return 'bg-green-100 text-green-800 hover:bg-green-200';
      case 'price':
        return 'bg-purple-100 text-purple-800 hover:bg-purple-200';
      case 'rating':
        return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors ${getChipColor()}`}
    >
      <span className="truncate max-w-32">{option.label}</span>
      <button
        onClick={onRemove}
        className="ml-2 hover:opacity-70 focus:outline-none"
      >
        <X className="w-3 h-3" />
      </button>
    </span>
  );
});

FilterChip.displayName = 'FilterChip';

/**
 * Componente principal de facetas de búsqueda
 */
const SearchFacets: React.FC<SearchFacetsProps> = memo(({
  className = '',
  showCounts = true,
  maxOptionsPerFacet = 5,
  collapsible = true,
  orientation = 'vertical',
}) => {
  const { results } = useSearch();

  /**
   * Facetas de los resultados
   */
  const facets = useMemo(() => {
    return results?.facets || [];
  }, [results?.facets]);

  /**
   * Facetas con opciones seleccionadas
   */
  const activeFacets = useMemo(() => {
    return facets.filter(facet =>
      facet.options?.some(option => option.selected)
    );
  }, [facets]);

  /**
   * Todas las opciones seleccionadas
   */
  const activeOptions = useMemo(() => {
    const options: Array<{ facet: SearchFacet; option: SearchFacetOption }> = [];

    activeFacets.forEach(facet => {
      facet.options?.forEach(option => {
        if (option.selected) {
          options.push({ facet, option });
        }
      });
    });

    return options;
  }, [activeFacets]);

  /**
   * Toggle de opción de faceta
   */
  const handleOptionToggle = useCallback((facetKey: string, optionValue: string) => {
    // Este método debería disparar una acción en el store
    // Por ahora lo implementamos como placeholder
    console.log('Toggle facet option:', facetKey, optionValue);

    // TODO: Implementar toggle en el store
    // store.toggleFacetOption(facetKey, optionValue);
  }, []);

  /**
   * Remover filtro específico
   */
  const handleRemoveFilter = useCallback((facetKey: string, optionValue: string) => {
    handleOptionToggle(facetKey, optionValue);
  }, [handleOptionToggle]);

  /**
   * Limpiar todos los filtros
   */
  const handleClearAllFilters = useCallback(() => {
    // TODO: Implementar clear all en el store
    console.log('Clear all filters');
  }, []);

  /**
   * Classes para orientación
   */
  const containerClasses = orientation === 'horizontal'
    ? 'flex flex-wrap gap-4'
    : 'space-y-4';

  const facetClasses = orientation === 'horizontal'
    ? 'min-w-64 flex-1'
    : 'w-full';

  if (facets.length === 0) {
    return null;
  }

  return (
    <div className={`${className}`}>
      {/* Chips de filtros activos */}
      {activeOptions.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-900">
              Filtros activos ({activeOptions.length})
            </h4>
            <button
              onClick={handleClearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-800 flex items-center space-x-1"
            >
              <X className="w-4 h-4" />
              <span>Limpiar todo</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {activeOptions.map(({ facet, option }) => (
              <FilterChip
                key={`${facet.key}-${option.value}`}
                facet={facet}
                option={option}
                onRemove={() => handleRemoveFilter(facet.key, option.value)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Facetas */}
      <div className={containerClasses}>
        {facets.map((facet) => (
          <div key={facet.key} className={facetClasses}>
            <FacetSection
              facet={facet}
              onOptionToggle={handleOptionToggle}
              showCounts={showCounts}
              maxOptions={maxOptionsPerFacet}
              isCollapsible={collapsible}
            />
          </div>
        ))}
      </div>

      {/* Estadísticas globales */}
      {facets.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              {facets.length} filtro{facets.length > 1 ? 's' : ''} disponible{facets.length > 1 ? 's' : ''}
            </span>
            <span>
              {activeOptions.length} aplicado{activeOptions.length > 1 ? 's' : ''}
            </span>
          </div>

          {activeOptions.length > 0 && (
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${Math.min((activeOptions.length / facets.length) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

SearchFacets.displayName = 'SearchFacets';

export default SearchFacets;