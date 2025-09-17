// ~/src/components/search/SearchResults.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - SearchResults Component with Infinite Scroll
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchResults.tsx
// Ruta: ~/src/components/search/SearchResults.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente para mostrar resultados de búsqueda con scroll infinito
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useCallback, useEffect, useRef, useState } from 'react';
import {
  Grid,
  List,
  ArrowUpDown,
  Filter,
  Loader2,
  AlertCircle,
  Search,
  RefreshCw,
} from 'lucide-react';
import { useSearch } from '../../hooks/search';
import { SearchResultsProps, SortOption, ViewMode } from '../../types/search.types';
import { Product } from '../../types/api.types';
import ProductCard from '../products/ProductCard';

/**
 * Opciones de ordenamiento con labels
 */
const sortOptions: Array<{ value: SortOption; label: string }> = [
  { value: 'relevance', label: 'Relevancia' },
  { value: 'price_asc', label: 'Precio: Menor a Mayor' },
  { value: 'price_desc', label: 'Precio: Mayor a Menor' },
  { value: 'newest', label: 'Más Recientes' },
  { value: 'rating', label: 'Mejor Calificados' },
  { value: 'popularity', label: 'Más Populares' },
  { value: 'name_asc', label: 'Nombre A-Z' },
  { value: 'name_desc', label: 'Nombre Z-A' },
];

/**
 * Componente de skeleton para loading
 */
const ProductSkeleton: React.FC<{ viewMode: ViewMode }> = memo(({ viewMode }) => {
  if (viewMode === 'list') {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 animate-pulse">
        <div className="flex space-x-4">
          <div className="w-24 h-24 bg-gray-300 rounded"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            <div className="h-3 bg-gray-300 rounded w-1/2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/4"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm animate-pulse">
      <div className="aspect-square bg-gray-300 rounded-t-lg"></div>
      <div className="p-4 space-y-2">
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 rounded w-1/2"></div>
        <div className="h-4 bg-gray-300 rounded w-1/3"></div>
      </div>
    </div>
  );
});

ProductSkeleton.displayName = 'ProductSkeleton';

/**
 * Componente principal de resultados de búsqueda
 */
const SearchResults: React.FC<SearchResultsProps> = memo(({
  className = '',
  onResultClick,
  emptyStateMessage = 'No se encontraron productos',
  showSorting = true,
  showViewToggle = true,
  infiniteScroll = true,
}) => {
  // Hooks
  const {
    products,
    totalProducts,
    isSearching,
    canLoadMore,
    loadMore,
    sort,
    setSort,
    viewMode,
    setViewMode,
    query,
    error,
    clearError,
    search,
    loading,
  } = useSearch();

  // Estado local
  const [isIntersecting, setIsIntersecting] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Manejar click en producto
   */
  const handleProductClick = useCallback((product: Product) => {
    onResultClick?.(product);
  }, [onResultClick]);

  /**
   * Cambiar ordenamiento
   */
  const handleSortChange = useCallback((newSort: SortOption) => {
    setSort(newSort);
  }, [setSort]);

  /**
   * Cambiar modo de vista
   */
  const handleViewModeChange = useCallback((newViewMode: ViewMode) => {
    setViewMode(newViewMode);
  }, [setViewMode]);

  /**
   * Retry en caso de error
   */
  const handleRetry = useCallback(() => {
    clearError();
    search({});
  }, [clearError, search]);

  /**
   * Intersection Observer para infinite scroll
   */
  useEffect(() => {
    if (!infiniteScroll || !canLoadMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        setIsIntersecting(entry.isIntersecting);
      },
      {
        root: null,
        rootMargin: '100px',
        threshold: 0.1,
      }
    );

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [infiniteScroll, canLoadMore]);

  /**
   * Cargar más cuando intersecting
   */
  useEffect(() => {
    if (isIntersecting && canLoadMore && !loading.loadingMore) {
      loadMore();
    }
  }, [isIntersecting, canLoadMore, loading.loadingMore, loadMore]);

  /**
   * Scroll to top cuando cambia la búsqueda
   */
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [query]);

  /**
   * Renderizar estado de error
   */
  const renderError = () => (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        Error al cargar resultados
      </h3>
      <p className="text-gray-600 mb-4 max-w-md">
        {error?.message || 'Ocurrió un error inesperado. Por favor, intenta nuevamente.'}
      </p>
      <button
        onClick={handleRetry}
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <RefreshCw className="w-4 h-4 mr-2" />
        Reintentar
      </button>
    </div>
  );

  /**
   * Renderizar estado vacío
   */
  const renderEmpty = () => (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <Search className="w-16 h-16 text-gray-400 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {query ? 'Sin resultados' : 'Realiza una búsqueda'}
      </h3>
      <p className="text-gray-600 max-w-md">
        {query
          ? `No encontramos productos para "${query}". Intenta con otros términos o ajusta los filtros.`
          : 'Ingresa un término de búsqueda para encontrar productos.'
        }
      </p>
    </div>
  );

  /**
   * Renderizar barra de herramientas
   */
  const renderToolbar = () => (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      {/* Información de resultados */}
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">
          {totalProducts > 0 && (
            <>
              <span className="font-medium">{totalProducts.toLocaleString()}</span>
              {' '}resultados
              {query && (
                <>
                  {' '}para{' '}
                  <span className="font-medium">"{query}"</span>
                </>
              )}
            </>
          )}
        </span>

        {isSearching && (
          <div className="flex items-center text-sm text-blue-600">
            <Loader2 className="w-4 h-4 mr-1 animate-spin" />
            Buscando...
          </div>
        )}
      </div>

      {/* Controles */}
      <div className="flex items-center space-x-4">
        {/* Ordenamiento */}
        {showSorting && products.length > 0 && (
          <div className="flex items-center space-x-2">
            <ArrowUpDown className="w-4 h-4 text-gray-500" />
            <select
              value={sort}
              onChange={(e) => handleSortChange(e.target.value as SortOption)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Toggle de vista */}
        {showViewToggle && products.length > 0 && (
          <div className="flex border border-gray-300 rounded-md">
            <button
              onClick={() => handleViewModeChange('grid')}
              className={`p-2 ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleViewModeChange('list')}
              className={`p-2 ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );

  /**
   * Renderizar grid de productos
   */
  const renderProductGrid = () => {
    const gridCols = viewMode === 'grid'
      ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'
      : 'grid-cols-1';

    return (
      <div className={`grid ${gridCols} gap-4`}>
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            viewMode={viewMode}
            onProductClick={handleProductClick}
            onViewDetails={handleProductClick}
            showSKU={false}
          />
        ))}

        {/* Skeletons para loading más */}
        {loading.loadingMore && (
          <>
            {Array.from({ length: 8 }).map((_, index) => (
              <ProductSkeleton
                key={`skeleton-${index}`}
                viewMode={viewMode}
              />
            ))}
          </>
        )}
      </div>
    );
  };

  /**
   * Renderizar loading inicial
   */
  const renderInitialLoading = () => {
    const gridCols = viewMode === 'grid'
      ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'
      : 'grid-cols-1';

    return (
      <div className={`grid ${gridCols} gap-4`}>
        {Array.from({ length: 12 }).map((_, index) => (
          <ProductSkeleton
            key={`initial-skeleton-${index}`}
            viewMode={viewMode}
          />
        ))}
      </div>
    );
  };

  return (
    <div ref={containerRef} className={`w-full ${className}`}>
      {/* Barra de herramientas */}
      {!error && renderToolbar()}

      {/* Contenido principal */}
      <div className="min-h-96">
        {error ? (
          renderError()
        ) : isSearching && products.length === 0 ? (
          renderInitialLoading()
        ) : products.length === 0 ? (
          renderEmpty()
        ) : (
          <>
            {renderProductGrid()}

            {/* Trigger para infinite scroll */}
            {infiniteScroll && canLoadMore && (
              <div
                ref={loadMoreRef}
                className="flex justify-center py-8"
              >
                <div className="flex items-center text-gray-500">
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Cargando más productos...
                </div>
              </div>
            )}

            {/* Botón manual para cargar más (fallback) */}
            {!infiniteScroll && canLoadMore && (
              <div className="flex justify-center py-8">
                <button
                  onClick={() => loadMore()}
                  disabled={loading.loadingMore}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading.loadingMore ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Cargando...
                    </>
                  ) : (
                    'Cargar más productos'
                  )}
                </button>
              </div>
            )}

            {/* Mensaje de final */}
            {!canLoadMore && products.length > 0 && (
              <div className="text-center py-8">
                <p className="text-gray-500">
                  Has visto todos los {totalProducts.toLocaleString()} productos
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
});

SearchResults.displayName = 'SearchResults';

export default SearchResults;