// ~/src/components/discovery/ProductSearchInterface.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Performance-Optimized Product Discovery Interface
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductSearchInterface.tsx
// Ruta: ~/src/components/discovery/ProductSearchInterface.tsx
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Interfaz principal de descubrimiento de productos con optimización avanzada
//
// Performance Targets:
// - Search Response: <200ms
// - Auto-complete: <100ms
// - Virtual Scrolling: 1000+ products
// - Mobile Performance: 90+ Lighthouse score
// - Bundle Size: <50KB additional
// ---------------------------------------------------------------------------------------------

import React, { useState, useCallback, useMemo, useRef, memo, Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import {
  Search,
  Filter,
  Grid,
  List,
  TrendingUp,
  Clock,
  Star,
  MapPin,
  Heart,
  Share2,
  Sliders,
  SortAsc,
  Eye,
  Zap,
} from 'lucide-react';

// Lazy imports for performance
const SearchBar = React.lazy(() => import('../search/SearchBar'));
const ProductFilters = React.lazy(() => import('./ProductFilters'));
const ProductGrid = React.lazy(() => import('./ProductGrid'));
const RecommendationsEngine = React.lazy(() => import('./RecommendationsEngine'));
const VoiceSearch = React.lazy(() => import('./VoiceSearch'));
const AdvancedSearchModal = React.lazy(() => import('./AdvancedSearchModal'));

// Hooks and services
import { useProductDiscovery } from '../../hooks/useProductDiscovery';
import { usePerformanceOptimization } from '../../hooks/usePerformanceOptimization';
import { useMobileOptimization } from '../../hooks/useMobileOptimization';
import { useSearchCache } from '../../hooks/useSearchCache';
import { useIntersectionObserver } from '../../hooks/useIntersectionObserver';

// Types
interface ProductSearchInterfaceProps {
  className?: string;
  initialQuery?: string;
  showRecommendations?: boolean;
  enableVoiceSearch?: boolean;
  enableAdvancedFilters?: boolean;
  enableVirtualScrolling?: boolean;
  mobileOptimized?: boolean;
  performanceMode?: 'balanced' | 'performance' | 'quality';
}

interface SearchState {
  query: string;
  filters: Record<string, any>;
  sortBy: string;
  viewMode: 'grid' | 'list';
  showFilters: boolean;
  showAdvanced: boolean;
  showVoice: boolean;
  isSearching: boolean;
  hasResults: boolean;
  totalResults: number;
  selectedCategories: string[];
  priceRange: [number, number];
  ratingFilter: number;
  locationFilter: string | null;
}

/**
 * Componente de Loading optimizado para performance
 */
const SearchLoadingSkeleton = memo(() => (
  <div className="animate-pulse space-y-4">
    <div className="h-12 bg-gray-200 rounded-lg"></div>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="space-y-3">
          <div className="h-48 bg-gray-200 rounded-lg"></div>
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      ))}
    </div>
  </div>
));

/**
 * Componente principal de interfaz de descubrimiento de productos
 */
const ProductSearchInterface: React.FC<ProductSearchInterfaceProps> = memo(({
  className = '',
  initialQuery = '',
  showRecommendations = true,
  enableVoiceSearch = true,
  enableAdvancedFilters = true,
  enableVirtualScrolling = true,
  mobileOptimized = true,
  performanceMode = 'balanced',
}) => {
  // Performance monitoring
  const {
    trackSearchPerformance,
    trackRenderPerformance,
    optimizeBundle,
    preloadResources
  } = usePerformanceOptimization(performanceMode);

  // Mobile optimization
  const {
    isMobile,
    isTablet,
    touchOptimizations,
    gestureHandlers,
    viewportOptimizations
  } = useMobileOptimization(mobileOptimized);

  // Search cache for performance
  const {
    getCachedResults,
    setCachedResults,
    clearCache,
    cacheStats
  } = useSearchCache();

  // Product discovery hook
  const {
    products,
    recommendations,
    searchHistory,
    popularSearches,
    trendingProducts,
    searchResults,
    isLoading,
    error,
    pagination,
    searchProducts,
    getRecommendations,
    trackSearchBehavior,
    optimizeSearchQuery,
  } = useProductDiscovery();

  // Referencias para optimización
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const resultsContainerRef = useRef<HTMLDivElement>(null);
  const filtersContainerRef = useRef<HTMLDivElement>(null);

  // Intersection Observer para lazy loading
  const { observeElement } = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '50px',
  });

  // Estado principal
  const [searchState, setSearchState] = useState<SearchState>({
    query: initialQuery,
    filters: {},
    sortBy: 'relevance',
    viewMode: isMobile ? 'list' : 'grid',
    showFilters: !isMobile,
    showAdvanced: false,
    showVoice: false,
    isSearching: false,
    hasResults: false,
    totalResults: 0,
    selectedCategories: [],
    priceRange: [0, 1000000],
    ratingFilter: 0,
    locationFilter: null,
  });

  /**
   * Optimized search handler with performance tracking
   */
  const handleSearch = useCallback(async (query: string, options: any = {}) => {
    const startTime = performance.now();

    setSearchState(prev => ({ ...prev, isSearching: true, query }));

    try {
      // Check cache first
      const cacheKey = `${query}_${JSON.stringify(options)}`;
      let results = getCachedResults(cacheKey);

      if (!results) {
        // Optimize query for better performance
        const optimizedQuery = optimizeSearchQuery(query);

        // Perform search
        results = await searchProducts(optimizedQuery, {
          ...options,
          cache: true,
          debounce: 300,
          limit: enableVirtualScrolling ? 50 : 20,
        });

        // Cache results
        setCachedResults(cacheKey, results);
      }

      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasResults: results.length > 0,
        totalResults: results.total || results.length,
      }));

      // Track search behavior
      trackSearchBehavior({
        query,
        results: results.length,
        responseTime: performance.now() - startTime,
        cached: !!getCachedResults(cacheKey),
      });

      // Track performance
      trackSearchPerformance({
        query,
        responseTime: performance.now() - startTime,
        resultsCount: results.length,
        cacheHit: !!getCachedResults(cacheKey),
      });

    } catch (error) {
      console.error('Search error:', error);
      setSearchState(prev => ({ ...prev, isSearching: false, hasResults: false }));
    }
  }, [
    searchProducts,
    optimizeSearchQuery,
    trackSearchBehavior,
    trackSearchPerformance,
    getCachedResults,
    setCachedResults,
    enableVirtualScrolling
  ]);

  /**
   * Handle filter changes with debouncing
   */
  const handleFilterChange = useCallback((filters: Record<string, any>) => {
    setSearchState(prev => ({ ...prev, filters }));

    // Debounced search with new filters
    const timeoutId = setTimeout(() => {
      handleSearch(searchState.query, { filters });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchState.query, handleSearch]);

  /**
   * Mobile-optimized gesture handlers
   */
  const mobileGestureHandlers = useMemo(() => {
    if (!isMobile) return {};

    return {
      onTouchStart: gestureHandlers.onTouchStart,
      onTouchMove: gestureHandlers.onTouchMove,
      onTouchEnd: gestureHandlers.onTouchEnd,
      ...touchOptimizations,
    };
  }, [isMobile, gestureHandlers, touchOptimizations]);

  /**
   * Performance-optimized sort handler
   */
  const handleSortChange = useCallback((sortBy: string) => {
    setSearchState(prev => ({ ...prev, sortBy }));

    // Use cached results if available and re-sort client-side for performance
    const cacheKey = `${searchState.query}_${JSON.stringify(searchState.filters)}`;
    const cachedResults = getCachedResults(cacheKey);

    if (cachedResults && cachedResults.length < 100) {
      // Client-side sort for better performance on small result sets
      const sortedResults = [...cachedResults].sort((a, b) => {
        switch (sortBy) {
          case 'price_asc': return a.price - b.price;
          case 'price_desc': return b.price - a.price;
          case 'rating': return b.rating - a.rating;
          case 'newest': return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          default: return 0;
        }
      });

      setCachedResults(`${cacheKey}_${sortBy}`, sortedResults);
    } else {
      // Server-side sort for large result sets
      handleSearch(searchState.query, {
        ...searchState.filters,
        sortBy
      });
    }
  }, [searchState.query, searchState.filters, getCachedResults, setCachedResults, handleSearch]);

  /**
   * Performance-optimized view mode toggle
   */
  const toggleViewMode = useCallback(() => {
    setSearchState(prev => ({
      ...prev,
      viewMode: prev.viewMode === 'grid' ? 'list' : 'grid'
    }));

    // Track view mode preference
    trackRenderPerformance({
      component: 'ProductSearchInterface',
      viewMode: searchState.viewMode === 'grid' ? 'list' : 'grid',
      productsCount: searchState.totalResults,
    });
  }, [searchState.viewMode, searchState.totalResults, trackRenderPerformance]);

  /**
   * Initialize search on mount
   */
  React.useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery);
    } else if (showRecommendations) {
      getRecommendations('homepage');
    }

    // Preload critical resources
    preloadResources(['search-icons', 'product-images']);
  }, [initialQuery, showRecommendations, handleSearch, getRecommendations, preloadResources]);

  /**
   * Performance monitoring
   */
  React.useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure' && entry.name.includes('search')) {
          console.log(`Search performance: ${entry.name} took ${entry.duration}ms`);
        }
      }
    });

    observer.observe({ entryTypes: ['measure'] });

    return () => observer.disconnect();
  }, []);

  /**
   * Error boundary fallback
   */
  const ErrorFallback = useCallback(({ error, resetErrorBoundary }: any) => (
    <div className="p-8 text-center bg-red-50 rounded-lg border border-red-200">
      <h2 className="text-lg font-semibold text-red-800 mb-2">
        Error en el sistema de búsqueda
      </h2>
      <p className="text-red-600 mb-4">
        {error.message || 'Ocurrió un error inesperado'}
      </p>
      <button
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
      >
        Reintentar
      </button>
    </div>
  ), []);

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <div
        ref={searchContainerRef}
        className={`product-search-interface ${className}`}
        {...mobileGestureHandlers}
      >
        {/* Header con búsqueda principal */}
        <div className="search-header bg-white border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center space-x-4">
              {/* Barra de búsqueda principal */}
              <div className="flex-1">
                <Suspense fallback={<div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>}>
                  <SearchBar
                    placeholder="Buscar productos en MeStore..."
                    onSearchChange={(query) => handleSearch(query)}
                    showVoiceSearch={enableVoiceSearch}
                    autoFocus={!isMobile}
                    size={isMobile ? 'md' : 'lg'}
                    className="w-full"
                  />
                </Suspense>
              </div>

              {/* Controles de vista */}
              <div className="flex items-center space-x-2">
                {/* Toggle de vista */}
                <button
                  onClick={toggleViewMode}
                  className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                  aria-label={`Cambiar a vista ${searchState.viewMode === 'grid' ? 'lista' : 'cuadrícula'}`}
                >
                  {searchState.viewMode === 'grid' ?
                    <List className="w-5 h-5" /> :
                    <Grid className="w-5 h-5" />
                  }
                </button>

                {/* Toggle de filtros */}
                <button
                  onClick={() => setSearchState(prev => ({ ...prev, showFilters: !prev.showFilters }))}
                  className={`
                    p-2 rounded-lg transition-colors
                    ${searchState.showFilters
                      ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }
                  `}
                  aria-label="Mostrar/ocultar filtros"
                >
                  <Filter className="w-5 h-5" />
                </button>

                {/* Ordenamiento */}
                <select
                  value={searchState.sortBy}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="relevance">Relevancia</option>
                  <option value="price_asc">Precio: Menor a Mayor</option>
                  <option value="price_desc">Precio: Mayor a Menor</option>
                  <option value="rating">Mejor Calificados</option>
                  <option value="newest">Más Recientes</option>
                  <option value="popular">Más Populares</option>
                </select>
              </div>
            </div>

            {/* Estadísticas de búsqueda */}
            {searchState.hasResults && (
              <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center space-x-4">
                  <span>
                    {searchState.totalResults.toLocaleString()} productos encontrados
                  </span>
                  {cacheStats.hitRate > 0 && (
                    <span className="text-green-600">
                      <Zap className="w-4 h-4 inline mr-1" />
                      Resultado optimizado (cache: {Math.round(cacheStats.hitRate * 100)}%)
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>Búsqueda en {performance.now()}ms</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Contenido principal */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Panel de filtros */}
            {searchState.showFilters && (
              <div
                ref={filtersContainerRef}
                className={`
                  ${isMobile ? 'order-last' : 'lg:w-64 flex-shrink-0'}
                `}
              >
                <Suspense fallback={<div className="h-96 bg-gray-100 rounded-lg animate-pulse"></div>}>
                  <ProductFilters
                    onFilterChange={handleFilterChange}
                    initialFilters={searchState.filters}
                    mobileOptimized={isMobile}
                    enableAdvanced={enableAdvancedFilters}
                    className="lg:sticky lg:top-24"
                  />
                </Suspense>
              </div>
            )}

            {/* Área de resultados */}
            <div className="flex-1 min-w-0">
              <div ref={resultsContainerRef}>
                {/* Recomendaciones */}
                {showRecommendations && !searchState.query && (
                  <Suspense fallback={<SearchLoadingSkeleton />}>
                    <RecommendationsEngine
                      type="discovery"
                      limit={isMobile ? 6 : 12}
                      performanceMode={performanceMode}
                      className="mb-8"
                    />
                  </Suspense>
                )}

                {/* Grid de productos */}
                {(searchState.hasResults || searchState.isSearching) && (
                  <Suspense fallback={<SearchLoadingSkeleton />}>
                    <ProductGrid
                      products={searchResults}
                      viewMode={searchState.viewMode}
                      isLoading={searchState.isSearching}
                      enableVirtualScrolling={enableVirtualScrolling}
                      mobileOptimized={isMobile}
                      performanceMode={performanceMode}
                      onProductClick={(product) => {
                        trackSearchBehavior({
                          action: 'product_click',
                          productId: product.id,
                          position: product.position,
                          query: searchState.query,
                        });
                      }}
                    />
                  </Suspense>
                )}

                {/* Estado vacío */}
                {!searchState.isSearching && !searchState.hasResults && searchState.query && (
                  <div className="text-center py-12">
                    <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No se encontraron productos
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Intenta con términos diferentes o ajusta los filtros
                    </p>
                    <button
                      onClick={() => {
                        setSearchState(prev => ({ ...prev, filters: {}, query: '' }));
                        clearCache();
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Limpiar búsqueda
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Modales */}
        {enableVoiceSearch && searchState.showVoice && (
          <Suspense fallback={null}>
            <VoiceSearch
              onResult={(text) => {
                handleSearch(text);
                setSearchState(prev => ({ ...prev, showVoice: false }));
              }}
              onClose={() => setSearchState(prev => ({ ...prev, showVoice: false }))}
            />
          </Suspense>
        )}

        {searchState.showAdvanced && (
          <Suspense fallback={null}>
            <AdvancedSearchModal
              onSearch={(query, filters) => {
                handleSearch(query, filters);
                setSearchState(prev => ({ ...prev, showAdvanced: false }));
              }}
              onClose={() => setSearchState(prev => ({ ...prev, showAdvanced: false }))}
            />
          </Suspense>
        )}
      </div>
    </ErrorBoundary>
  );
});

ProductSearchInterface.displayName = 'ProductSearchInterface';

export default ProductSearchInterface;