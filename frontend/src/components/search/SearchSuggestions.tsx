// ~/src/components/search/SearchSuggestions.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - SearchSuggestions Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchSuggestions.tsx
// Ruta: ~/src/components/search/SearchSuggestions.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente de sugerencias de búsqueda y términos populares
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useCallback, useMemo } from 'react';
import {
  Search,
  Clock,
  TrendingUp,
  Hash,
  ChevronRight,
  Star,
  Package,
  Building2,
  Tag,
  Zap,
} from 'lucide-react';
import { useSearchSuggestions, useSearchHistory } from '../../hooks/search';
import { SearchSuggestion } from '../../types/search.types';

interface SearchSuggestionsProps {
  className?: string;
  maxSuggestions?: number;
  showRecentSearches?: boolean;
  showPopularSearches?: boolean;
  showCounts?: boolean;
  onSuggestionClick?: (suggestion: SearchSuggestion) => void;
  compact?: boolean;
}

interface SuggestionItemProps {
  suggestion: SearchSuggestion;
  onClick: (suggestion: SearchSuggestion) => void;
  showCount: boolean;
  compact: boolean;
  highlighted?: boolean;
}

/**
 * Componente individual de sugerencia
 */
const SuggestionItem: React.FC<SuggestionItemProps> = memo(({
  suggestion,
  onClick,
  showCount,
  compact,
  highlighted = false,
}) => {
  /**
   * Icono basado en tipo de sugerencia
   */
  const getIcon = () => {
    switch (suggestion.type) {
      case 'query':
        return <Search className="w-4 h-4 text-gray-500" />;
      case 'category':
        return <Tag className="w-4 h-4 text-blue-500" />;
      case 'product':
        return <Package className="w-4 h-4 text-green-500" />;
      case 'vendor':
        return <Building2 className="w-4 h-4 text-purple-500" />;
      default:
        return <Search className="w-4 h-4 text-gray-500" />;
    }
  };

  /**
   * Color de fondo basado en tipo
   */
  const getBackgroundColor = () => {
    if (highlighted) return 'bg-blue-50 border-blue-200';

    switch (suggestion.type) {
      case 'category':
        return 'hover:bg-blue-50';
      case 'product':
        return 'hover:bg-green-50';
      case 'vendor':
        return 'hover:bg-purple-50';
      default:
        return 'hover:bg-gray-50';
    }
  };

  /**
   * Label de tipo para mostrar
   */
  const getTypeLabel = () => {
    switch (suggestion.type) {
      case 'category':
        return 'Categoría';
      case 'product':
        return 'Producto';
      case 'vendor':
        return 'Vendedor';
      default:
        return null;
    }
  };

  return (
    <div
      onClick={() => onClick(suggestion)}
      className={`
        flex items-center space-x-3 p-3 cursor-pointer transition-all duration-150 border-l-2 border-transparent
        ${getBackgroundColor()}
        ${compact ? 'py-2' : 'py-3'}
      `}
    >
      {/* Icono */}
      <div className="flex-shrink-0">
        {getIcon()}
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2">
          <span
            className="text-gray-900 truncate"
            dangerouslySetInnerHTML={{
              __html: suggestion.highlight || suggestion.text
            }}
          />
          {getTypeLabel() && (
            <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
              {getTypeLabel()}
            </span>
          )}
        </div>

        {/* Información adicional */}
        {!compact && suggestion.metadata && (
          <div className="mt-1 text-xs text-gray-500">
            {suggestion.type === 'product' && suggestion.metadata.category && (
              <span>en {suggestion.metadata.category}</span>
            )}
            {suggestion.type === 'vendor' && suggestion.metadata.vendorId && (
              <span>Vendedor</span>
            )}
          </div>
        )}
      </div>

      {/* Contador y flecha */}
      <div className="flex items-center space-x-2 flex-shrink-0">
        {showCount && suggestion.count && (
          <span className="text-xs text-gray-500 flex items-center">
            <Hash className="w-3 h-3 mr-1" />
            {suggestion.count}
          </span>
        )}
        <ChevronRight className="w-4 h-4 text-gray-400" />
      </div>
    </div>
  );
});

SuggestionItem.displayName = 'SuggestionItem';

/**
 * Sección de sugerencias con header
 */
const SuggestionsSection: React.FC<{
  title: string;
  icon: React.ReactNode;
  suggestions: SearchSuggestion[];
  onSuggestionClick: (suggestion: SearchSuggestion) => void;
  showCount: boolean;
  compact: boolean;
  emptyMessage?: string;
}> = memo(({
  title,
  icon,
  suggestions,
  onSuggestionClick,
  showCount,
  compact,
  emptyMessage,
}) => {
  if (suggestions.length === 0) {
    return emptyMessage ? (
      <div className="p-4 text-center text-gray-500 text-sm">
        {emptyMessage}
      </div>
    ) : null;
  }

  return (
    <div>
      {/* Header de sección */}
      <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 border-b border-gray-200">
        {icon}
        <span className="text-sm font-medium text-gray-700">{title}</span>
        <span className="text-xs text-gray-500">({suggestions.length})</span>
      </div>

      {/* Lista de sugerencias */}
      <div>
        {suggestions.map((suggestion, index) => (
          <SuggestionItem
            key={`${suggestion.type}_${suggestion.id}_${index}`}
            suggestion={suggestion}
            onClick={onSuggestionClick}
            showCount={showCount}
            compact={compact}
          />
        ))}
      </div>
    </div>
  );
});

SuggestionsSection.displayName = 'SuggestionsSection';

/**
 * Componente principal de sugerencias de búsqueda
 */
const SearchSuggestions: React.FC<SearchSuggestionsProps> = memo(({
  className = '',
  maxSuggestions = 10,
  showRecentSearches = true,
  showPopularSearches = true,
  showCounts = true,
  onSuggestionClick,
  compact = false,
}) => {
  // Hooks
  const {
    suggestions,
    recentSearches,
    popularSearches,
    isLoading,
    selectSuggestion,
    groupedSuggestions,
  } = useSearchSuggestions();

  const {
    getPopularTerms,
    getRecentTerms,
  } = useSearchHistory();

  /**
   * Manejar click en sugerencia
   */
  const handleSuggestionClick = useCallback((suggestion: SearchSuggestion) => {
    selectSuggestion(suggestion);
    onSuggestionClick?.(suggestion);
  }, [selectSuggestion, onSuggestionClick]);

  /**
   * Sugerencias limitadas por tipo
   */
  const limitedSuggestions = useMemo(() => {
    const limit = Math.floor(maxSuggestions / 4);

    return {
      queries: groupedSuggestions.queries.slice(0, limit),
      categories: groupedSuggestions.categories.slice(0, limit),
      products: groupedSuggestions.products.slice(0, limit),
      vendors: groupedSuggestions.vendors.slice(0, limit),
    };
  }, [groupedSuggestions, maxSuggestions]);

  /**
   * Búsquedas recientes como sugerencias
   */
  const recentAsSuggestions = useMemo(() => {
    return getRecentTerms().slice(0, 5).map((term, index) => ({
      id: `recent_${index}`,
      text: term,
      type: 'query' as const,
    }));
  }, [getRecentTerms]);

  /**
   * Búsquedas populares como sugerencias
   */
  const popularAsSuggestions = useMemo(() => {
    return getPopularTerms().slice(0, 5).map((term, index) => ({
      id: `popular_${index}`,
      text: term,
      type: 'query' as const,
    }));
  }, [getPopularTerms]);

  /**
   * Hay contenido para mostrar
   */
  const hasContent = suggestions.length > 0 ||
                     (showRecentSearches && recentAsSuggestions.length > 0) ||
                     (showPopularSearches && popularAsSuggestions.length > 0);

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 shadow-lg ${className}`}>
        <div className="p-4">
          <div className="animate-pulse space-y-3">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-gray-300 rounded"></div>
                <div className="flex-1 h-4 bg-gray-300 rounded"></div>
                <div className="w-8 h-3 bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!hasContent) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-lg max-h-96 overflow-y-auto ${className}`}>
      {/* Sugerencias de consultas */}
      {limitedSuggestions.queries.length > 0 && (
        <SuggestionsSection
          title="Búsquedas sugeridas"
          icon={<Zap className="w-4 h-4 text-yellow-500" />}
          suggestions={limitedSuggestions.queries}
          onSuggestionClick={handleSuggestionClick}
          showCount={showCounts}
          compact={compact}
        />
      )}

      {/* Sugerencias de categorías */}
      {limitedSuggestions.categories.length > 0 && (
        <SuggestionsSection
          title="Categorías"
          icon={<Tag className="w-4 h-4 text-blue-500" />}
          suggestions={limitedSuggestions.categories}
          onSuggestionClick={handleSuggestionClick}
          showCount={showCounts}
          compact={compact}
        />
      )}

      {/* Sugerencias de productos */}
      {limitedSuggestions.products.length > 0 && (
        <SuggestionsSection
          title="Productos"
          icon={<Package className="w-4 h-4 text-green-500" />}
          suggestions={limitedSuggestions.products}
          onSuggestionClick={handleSuggestionClick}
          showCount={showCounts}
          compact={compact}
        />
      )}

      {/* Sugerencias de vendedores */}
      {limitedSuggestions.vendors.length > 0 && (
        <SuggestionsSection
          title="Vendedores"
          icon={<Building2 className="w-4 h-4 text-purple-500" />}
          suggestions={limitedSuggestions.vendors}
          onSuggestionClick={handleSuggestionClick}
          showCount={showCounts}
          compact={compact}
        />
      )}

      {/* Búsquedas recientes */}
      {showRecentSearches && recentAsSuggestions.length > 0 && (
        <SuggestionsSection
          title="Búsquedas recientes"
          icon={<Clock className="w-4 h-4 text-gray-500" />}
          suggestions={recentAsSuggestions}
          onSuggestionClick={handleSuggestionClick}
          showCount={false}
          compact={compact}
        />
      )}

      {/* Búsquedas populares */}
      {showPopularSearches && popularAsSuggestions.length > 0 && (
        <SuggestionsSection
          title="Búsquedas populares"
          icon={<TrendingUp className="w-4 h-4 text-red-500" />}
          suggestions={popularAsSuggestions}
          onSuggestionClick={handleSuggestionClick}
          showCount={false}
          compact={compact}
        />
      )}

      {/* Footer con estadísticas */}
      {!compact && (
        <div className="p-3 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>
              {suggestions.length + recentAsSuggestions.length + popularAsSuggestions.length} sugerencias
            </span>
            <div className="flex items-center space-x-3">
              {recentAsSuggestions.length > 0 && (
                <span className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{recentAsSuggestions.length} recientes</span>
                </span>
              )}
              {popularAsSuggestions.length > 0 && (
                <span className="flex items-center space-x-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>{popularAsSuggestions.length} populares</span>
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

SearchSuggestions.displayName = 'SearchSuggestions';

export default SearchSuggestions;