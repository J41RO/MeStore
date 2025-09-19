// ~/src/pages/SearchPage.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Search Page with Integrated Components
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchPage.tsx
// Ruta: ~/src/pages/SearchPage.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Página principal de búsqueda integrando todos los componentes
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useState, useCallback, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Filter,
  Settings,
  X,
  Menu,
  ArrowLeft,
} from 'lucide-react';
import {
  SearchBar,
  SearchResults,
  SearchFilters,
  SearchFacets,
  AdvancedSearchModal,
  useSearch,
  useSearchAnalytics,
} from '../components/search';
import { Product } from '../types/api.types';
import { SearchParams } from '../types/search.types';

/**
 * Página principal de búsqueda del marketplace
 */
const SearchPage: React.FC = memo(() => {
  // Estado local
  const [showFilters, setShowFilters] = useState(false);
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Hooks de navegación
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Hooks de búsqueda
  const {
    query,
    results,
    isSearching,
    hasResults,
    hasError,
    error,
    totalProducts,
    activeFiltersCount,
    search,
    clearSearch,
  } = useSearch();

  // Analytics
  const { trackClick, trackPerformance } = useSearchAnalytics();

  /**
   * Detectar pantalla móvil
   */
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  /**
   * Inicializar búsqueda desde URL
   */
  useEffect(() => {
    const queryParam = searchParams.get('q');
    if (queryParam && queryParam !== query) {
      const startTime = performance.now();
      search({ query: queryParam }).then(() => {
        const endTime = performance.now();
        trackPerformance('search_from_url', endTime - startTime);
      });
    }
  }, [searchParams, query, search, trackPerformance]);

  /**
   * Auto-abrir filtros en desktop si hay resultados
   */
  useEffect(() => {
    if (!isMobile && hasResults && !showFilters) {
      setShowFilters(true);
    }
  }, [isMobile, hasResults, showFilters]);

  /**
   * Manejar click en producto
   */
  const handleProductClick = useCallback((product: Product) => {
    trackClick(product.id, 0); // TODO: Calcular posición real
    navigate(`/product/${product.id}`);
  }, [trackClick, navigate]);

  /**
   * Manejar búsqueda avanzada
   */
  const handleAdvancedSearch = useCallback((params: SearchParams) => {
    const startTime = performance.now();
    search(params).then(() => {
      const endTime = performance.now();
      trackPerformance('advanced_search', endTime - startTime);
    });
  }, [search, trackPerformance]);

  /**
   * Toggle de filtros móvil
   */
  const handleToggleFilters = useCallback(() => {
    setShowFilters(!showFilters);
  }, [showFilters]);

  /**
   * Volver a página anterior
   */
  const handleGoBack = useCallback(() => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  }, [navigate]);

  /**
   * Limpiar búsqueda y volver al inicio
   */
  const handleClearAndHome = useCallback(() => {
    clearSearch();
    navigate('/');
  }, [clearSearch, navigate]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header de búsqueda */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-4 py-4">
            {/* Botón de volver (móvil) */}
            {isMobile && (
              <button
                onClick={handleGoBack}
                className="p-2 text-gray-600 hover:text-gray-800"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
            )}

            {/* Barra de búsqueda */}
            <div className="flex-1">
              <SearchBar
                placeholder="Buscar productos en MeStore..."
                showVoiceSearch={true}
                showAdvancedLink={true}
                enableAutocomplete={true}
                size="md"
                autoFocus={!query}
              />
            </div>

            {/* Controles de filtros */}
            <div className="flex items-center space-x-2">
              {/* Botón de filtros (móvil) */}
              {isMobile && (
                <button
                  onClick={handleToggleFilters}
                  className={`
                    relative p-2 rounded-lg transition-colors
                    ${showFilters
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                    }
                  `}
                >
                  <Filter className="w-5 h-5" />
                  {activeFiltersCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {activeFiltersCount}
                    </span>
                  )}
                </button>
              )}

              {/* Búsqueda avanzada */}
              <button
                onClick={() => setShowAdvancedModal(true)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar de filtros (desktop) o Modal (móvil) */}
          {!isMobile ? (
            // Desktop sidebar
            <div className={`
              lg:w-80 flex-shrink-0 transition-all duration-300
              ${showFilters ? 'w-80' : 'w-0 overflow-hidden'}
            `}>
              {showFilters && (
                <div className="space-y-6">
                  <SearchFilters
                    showClearAll={true}
                    collapsible={true}
                    orientation="vertical"
                  />

                  {hasResults && (
                    <SearchFacets
                      showCounts={true}
                      maxOptionsPerFacet={5}
                      collapsible={true}
                      orientation="vertical"
                    />
                  )}
                </div>
              )}
            </div>
          ) : (
            // Mobile overlay
            showFilters && (
              <div className="fixed inset-0 z-50 lg:hidden">
                <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowFilters(false)} />
                <div className="absolute right-0 top-0 h-full w-80 bg-white shadow-xl overflow-y-auto">
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-medium text-gray-900">Filtros</h2>
                      <button
                        onClick={() => setShowFilters(false)}
                        className="p-2 text-gray-600 hover:text-gray-800"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="space-y-6">
                      <SearchFilters
                        showClearAll={true}
                        collapsible={true}
                        orientation="vertical"
                      />

                      {hasResults && (
                        <SearchFacets
                          showCounts={true}
                          maxOptionsPerFacet={5}
                          collapsible={true}
                          orientation="vertical"
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          )}

          {/* Área de resultados */}
          <div className="flex-1 min-w-0">
            {/* Breadcrumb/Estado actual */}
            {query && (
              <div className="mb-6">
                <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                  <button
                    onClick={handleClearAndHome}
                    className="hover:text-gray-800"
                  >
                    Inicio
                  </button>
                  <span>›</span>
                  <span>Búsqueda</span>
                  {query && (
                    <>
                      <span>›</span>
                      <span className="font-medium text-gray-900">"{query}"</span>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Filtros activos (horizontal en móvil) */}
            {isMobile && activeFiltersCount > 0 && (
              <div className="mb-4">
                <SearchFacets
                  showCounts={false}
                  maxOptionsPerFacet={3}
                  collapsible={false}
                  orientation="horizontal"
                />
              </div>
            )}

            {/* Resultados de búsqueda */}
            <SearchResults
              onResultClick={handleProductClick}
              showSorting={true}
              showViewToggle={true}
              infiniteScroll={true}
              emptyStateMessage={
                query
                  ? `No se encontraron productos para "${query}"`
                  : 'Ingresa un término de búsqueda para encontrar productos'
              }
            />

            {/* Información adicional */}
            {hasResults && !isSearching && (
              <div className="mt-8 p-6 bg-white rounded-lg border border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  ¿No encuentras lo que buscas?
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Consejos de búsqueda:</h4>
                    <ul className="space-y-1">
                      <li>• Revisa la ortografía</li>
                      <li>• Usa términos más generales</li>
                      <li>• Prueba sinónimos</li>
                      <li>• Reduce el número de filtros</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Opciones adicionales:</h4>
                    <ul className="space-y-1">
                      <li>
                        <button
                          onClick={() => setShowAdvancedModal(true)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          • Usar búsqueda avanzada
                        </button>
                      </li>
                      <li>• Contactar soporte técnico</li>
                      <li>• Ver categorías populares</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de búsqueda avanzada */}
      <AdvancedSearchModal
        isOpen={showAdvancedModal}
        onClose={() => setShowAdvancedModal(false)}
        onSearch={handleAdvancedSearch}
      />

      {/* Debug info (solo en desarrollo) */}
      {import.meta.env.MODE === 'development' && (
        <div className="fixed bottom-4 right-4 bg-black bg-opacity-80 text-white text-xs p-2 rounded font-mono">
          Query: {query || 'none'} | Results: {totalProducts} | Filters: {activeFiltersCount}
        </div>
      )}
    </div>
  );
});

SearchPage.displayName = 'SearchPage';

export default SearchPage;