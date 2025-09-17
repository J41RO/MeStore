// ~/src/components/SearchDemo.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Search System Demo Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchDemo.tsx
// Ruta: ~/src/components/SearchDemo.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente de demostración del sistema de búsqueda completo
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useState, useCallback } from 'react';
import {
  Search,
  Settings,
  Filter,
  BarChart3,
  Lightbulb,
  CheckCircle,
  AlertCircle,
  Info,
} from 'lucide-react';
import {
  SearchBar,
  SearchResults,
  SearchFilters,
  SearchFacets,
  SearchSuggestions,
  AdvancedSearchModal,
  useSearch,
  useSearchHistory,
  useSearchAnalytics,
} from './search';
import { Product } from '../types/api.types';
import { SearchParams } from '../types/search.types';

/**
 * Componente de tarjeta de demostración
 */
const DemoCard: React.FC<{
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'implemented' | 'demo' | 'placeholder';
  children: React.ReactNode;
}> = memo(({ title, description, icon, status, children }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusColor = () => {
    switch (status) {
      case 'implemented':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'demo':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'placeholder':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'implemented':
        return <CheckCircle className="w-4 h-4" />;
      case 'demo':
        return <Info className="w-4 h-4" />;
      case 'placeholder':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className={`border rounded-lg ${getStatusColor()}`}>
      <div
        className="p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {icon}
            <div>
              <h3 className="font-medium">{title}</h3>
              <p className="text-sm opacity-80">{description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-xs uppercase font-medium">
              {status}
            </span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t p-4 bg-white rounded-b-lg">
          {children}
        </div>
      )}
    </div>
  );
});

DemoCard.displayName = 'DemoCard';

/**
 * Componente principal de demostración
 */
const SearchDemo: React.FC = memo(() => {
  // Estado local
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Hooks de búsqueda
  const {
    query,
    results,
    isSearching,
    hasResults,
    totalProducts,
    activeFiltersCount,
    search,
    clearSearch,
  } = useSearch();

  const {
    savedSearches,
    recentSearches,
    saveCurrentSearch,
  } = useSearchHistory();

  const { trackSearch, trackClick } = useSearchAnalytics();

  /**
   * Demo data para mostrar funcionalidades
   */
  const demoProducts: Product[] = [
    {
      id: 'demo-1',
      name: 'MacBook Pro 16" M3',
      description: 'Laptop profesional con chip M3, 16GB RAM, 512GB SSD',
      price: 2500,
      stock: 5,
      category: 'Electrónicos',
      imageUrl: '/api/placeholder/300/300',
      vendorId: 'vendor-1',
      vendorName: 'TechStore',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: 'demo-2',
      name: 'iPhone 15 Pro',
      description: 'Smartphone Apple con chip A17 Pro, 128GB',
      price: 1200,
      stock: 12,
      category: 'Electrónicos',
      imageUrl: '/api/placeholder/300/300',
      vendorId: 'vendor-2',
      vendorName: 'MobileWorld',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: 'demo-3',
      name: 'Mesa de Oficina Ergonómica',
      description: 'Mesa ajustable en altura para trabajo',
      price: 450,
      stock: 8,
      category: 'Muebles',
      imageUrl: '/api/placeholder/300/300',
      vendorId: 'vendor-3',
      vendorName: 'OfficeMax',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  /**
   * Manejar click en producto demo
   */
  const handleProductClick = useCallback((product: Product) => {
    trackClick(product.id, 0);
    alert(`Navegando a producto: ${product.name}`);
  }, [trackClick]);

  /**
   * Manejar búsqueda avanzada demo
   */
  const handleAdvancedSearch = useCallback((params: SearchParams) => {
    console.log('Advanced search params:', params);
    trackSearch(params.query, demoProducts.length);
    setShowAdvancedModal(false);
  }, [trackSearch]);

  /**
   * Demo de búsqueda rápida
   */
  const handleDemoSearch = useCallback((demoQuery: string) => {
    search({ query: demoQuery });
  }, [search]);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">
          Sistema de Búsqueda Avanzada MeStore
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Demostración completa del sistema de búsqueda con React 18, TypeScript,
          Zustand, autocomplete, filtros avanzados, y optimizaciones de performance.
        </p>

        {/* Estado actual */}
        <div className="flex justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Query: {query || 'ninguna'}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Resultados: {totalProducts}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span>Filtros: {activeFiltersCount}</span>
          </div>
        </div>
      </div>

      {/* Demostración de componentes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SearchBar Demo */}
        <DemoCard
          title="SearchBar Component"
          description="Barra de búsqueda con autocomplete, voice search, y búsqueda avanzada"
          icon={<Search className="w-5 h-5" />}
          status="implemented"
        >
          <div className="space-y-4">
            <SearchBar
              placeholder="Prueba buscar 'laptop', 'iphone', 'mesa'..."
              showVoiceSearch={true}
              showAdvancedLink={true}
              enableAutocomplete={true}
              size="md"
            />

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleDemoSearch('laptop')}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200"
              >
                Demo: laptop
              </button>
              <button
                onClick={() => handleDemoSearch('iphone')}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200"
              >
                Demo: iphone
              </button>
              <button
                onClick={() => handleDemoSearch('mesa')}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200"
              >
                Demo: mesa
              </button>
              <button
                onClick={clearSearch}
                className="px-3 py-1 bg-gray-100 text-gray-800 rounded text-sm hover:bg-gray-200"
              >
                Limpiar
              </button>
            </div>
          </div>
        </DemoCard>

        {/* SearchSuggestions Demo */}
        <DemoCard
          title="SearchSuggestions Component"
          description="Sugerencias inteligentes, búsquedas recientes, y términos populares"
          icon={<Lightbulb className="w-5 h-5" />}
          status="implemented"
        >
          <div className="space-y-4">
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {showSuggestions ? 'Ocultar' : 'Mostrar'} Sugerencias
            </button>

            {showSuggestions && (
              <SearchSuggestions
                maxSuggestions={8}
                showRecentSearches={true}
                showPopularSearches={true}
                showCounts={true}
                compact={false}
              />
            )}

            <div className="text-sm text-gray-600">
              <p><strong>Funcionalidades:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Sugerencias por tipo (query, categoría, producto, vendor)</li>
                <li>Highlighting de términos coincidentes</li>
                <li>Navegación con teclado</li>
                <li>Búsquedas recientes y populares</li>
              </ul>
            </div>
          </div>
        </DemoCard>

        {/* SearchFilters Demo */}
        <DemoCard
          title="SearchFilters Component"
          description="Filtros avanzados con categorías, precios, ratings, y más"
          icon={<Filter className="w-5 h-5" />}
          status="implemented"
        >
          <div className="space-y-4">
            <SearchFilters
              showClearAll={true}
              collapsible={true}
              orientation="vertical"
            />

            <div className="text-sm text-gray-600">
              <p><strong>Características:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Filtros colapsibles por sección</li>
                <li>Multi-selección con contadores</li>
                <li>Rango de precios con sliders</li>
                <li>Chips de filtros activos</li>
                <li>Responsive design</li>
              </ul>
            </div>
          </div>
        </DemoCard>

        {/* SearchResults Demo */}
        <DemoCard
          title="SearchResults Component"
          description="Resultados con infinite scroll, sorting, y vista grid/list"
          icon={<BarChart3 className="w-5 h-5" />}
          status="demo"
        >
          <div className="space-y-4">
            {demoProducts.length > 0 && (
              <div className="border rounded p-4 bg-gray-50">
                <h4 className="font-medium mb-3">Productos Demo:</h4>
                <div className="grid grid-cols-1 gap-3">
                  {demoProducts.map((product) => (
                    <div
                      key={product.id}
                      onClick={() => handleProductClick(product)}
                      className="flex items-center space-x-3 p-3 bg-white rounded border hover:border-blue-300 cursor-pointer"
                    >
                      <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
                        📦
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{product.name}</div>
                        <div className="text-sm text-gray-600">{product.category}</div>
                        <div className="text-lg font-bold text-blue-600">
                          ${product.price.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-sm text-gray-600">
              <p><strong>Funcionalidades:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Vista grid y lista responsive</li>
                <li>Infinite scroll optimizado</li>
                <li>Sorting por múltiples criterios</li>
                <li>Loading skeletons</li>
                <li>Estados de error y vacío</li>
              </ul>
            </div>
          </div>
        </DemoCard>

        {/* AdvancedSearchModal Demo */}
        <DemoCard
          title="AdvancedSearchModal Component"
          description="Modal completo para búsquedas avanzadas y gestión de filtros"
          icon={<Settings className="w-5 h-5" />}
          status="implemented"
        >
          <div className="space-y-4">
            <button
              onClick={() => setShowAdvancedModal(true)}
              className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              Abrir Búsqueda Avanzada
            </button>

            <div className="text-sm text-gray-600">
              <p><strong>Características:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Búsqueda semántica y avanzada</li>
                <li>Gestión de búsquedas guardadas</li>
                <li>Exportar/importar configuraciones</li>
                <li>Formulario completo de filtros</li>
                <li>Responsive modal</li>
              </ul>
            </div>
          </div>
        </DemoCard>

        {/* Analytics Demo */}
        <DemoCard
          title="Search Analytics"
          description="Tracking y analytics de comportamiento de búsqueda"
          icon={<BarChart3 className="w-5 h-5" />}
          status="implemented"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-blue-50 rounded">
                <div className="font-medium text-blue-900">Búsquedas guardadas</div>
                <div className="text-xl font-bold text-blue-600">
                  {savedSearches.length}
                </div>
              </div>
              <div className="p-3 bg-green-50 rounded">
                <div className="font-medium text-green-900">Búsquedas recientes</div>
                <div className="text-xl font-bold text-green-600">
                  {recentSearches.length}
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-600">
              <p><strong>Métricas tracked:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Queries y tiempo de respuesta</li>
                <li>Clicks en resultados</li>
                <li>Uso de filtros</li>
                <li>Búsquedas sin resultados</li>
                <li>Conversiones</li>
              </ul>
            </div>
          </div>
        </DemoCard>
      </div>

      {/* Performance Metrics */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Performance y Optimizaciones
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">< 300ms</div>
            <div className="text-sm text-gray-600">Debounce Search</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">Virtual Scroll</div>
            <div className="text-sm text-gray-600">Miles de productos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">Memoized</div>
            <div className="text-sm text-gray-600">Componentes optimizados</div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Optimizaciones React:</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>React.memo para componentes pesados</li>
              <li>useMemo y useCallback para cálculos</li>
              <li>Lazy loading de imágenes</li>
              <li>Code splitting por rutas</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 mb-2">State Management:</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Zustand con middleware persistence</li>
              <li>Cache inteligente de resultados</li>
              <li>Optimistic updates</li>
              <li>URL state synchronization</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Modal de búsqueda avanzada */}
      <AdvancedSearchModal
        isOpen={showAdvancedModal}
        onClose={() => setShowAdvancedModal(false)}
        onSearch={handleAdvancedSearch}
      />
    </div>
  );
});

SearchDemo.displayName = 'SearchDemo';

export default SearchDemo;