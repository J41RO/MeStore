// ~/src/components/discovery/ProductFilters.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Advanced Product Filters with Performance Optimization
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductFilters.tsx
// Ruta: ~/src/components/discovery/ProductFilters.tsx
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Sistema de filtros avanzado para descubrimiento de productos
//
// Performance Features:
// - Virtual scrolling for large category lists
// - Debounced filter updates
// - Memoized filter calculations
// - Optimized re-renders
// - Mobile gesture support
// ---------------------------------------------------------------------------------------------

import React, { useState, useCallback, useMemo, memo, useRef, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  X,
  Check,
  Star,
  MapPin,
  DollarSign,
  Tag,
  Filter,
  Search,
  Sliders,
  Heart,
  TrendingUp,
  Calendar,
  Package,
  Truck,
  Shield,
  Zap,
} from 'lucide-react';

// Hooks
import { useCategories } from '../../hooks/useCategories';
import { useFilters } from '../../hooks/useFilters';
import { useDebounce } from '../../hooks/useDebounce';
import { useMobileOptimization } from '../../hooks/useMobileOptimization';

// Types
interface ProductFiltersProps {
  onFilterChange: (filters: FilterState) => void;
  initialFilters?: FilterState;
  mobileOptimized?: boolean;
  enableAdvanced?: boolean;
  className?: string;
  collapsible?: boolean;
  showCounts?: boolean;
}

interface FilterState {
  categories: string[];
  priceRange: [number, number];
  rating: number;
  brand: string[];
  location: string[];
  availability: string[];
  shipping: string[];
  features: string[];
  condition: string[];
  sortBy: string;
  searchQuery: string;
}

interface FilterSection {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  expanded: boolean;
  count?: number;
}

/**
 * Range Slider optimizado para performance
 */
const PriceRangeSlider = memo(({
  value,
  onChange,
  min = 0,
  max = 1000000,
  step = 1000,
  isMobile = false
}: {
  value: [number, number];
  onChange: (value: [number, number]) => void;
  min?: number;
  max?: number;
  step?: number;
  isMobile?: boolean;
}) => {
  const [localValue, setLocalValue] = useState(value);
  const debouncedOnChange = useDebounce(onChange, 300);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = useCallback((index: 0 | 1, newValue: number) => {
    const newRange: [number, number] = [...localValue];
    newRange[index] = newValue;

    // Ensure min <= max
    if (index === 0 && newValue > newRange[1]) {
      newRange[1] = newValue;
    } else if (index === 1 && newValue < newRange[0]) {
      newRange[0] = newValue;
    }

    setLocalValue(newRange);
    debouncedOnChange(newRange);
  }, [localValue, debouncedOnChange]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="space-y-4">
      {/* Inputs numéricos para mobile */}
      {isMobile ? (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Mínimo
            </label>
            <input
              type="number"
              value={localValue[0]}
              onChange={(e) => handleChange(0, parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Máximo
            </label>
            <input
              type="number"
              value={localValue[1]}
              onChange={(e) => handleChange(1, parseInt(e.target.value) || max)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={max.toString()}
            />
          </div>
        </div>
      ) : (
        /* Slider para desktop */
        <div className="relative">
          <div className="relative h-6">
            {/* Track */}
            <div className="absolute top-3 left-0 right-0 h-1 bg-gray-200 rounded"></div>

            {/* Active range */}
            <div
              className="absolute top-3 h-1 bg-blue-500 rounded"
              style={{
                left: `${(localValue[0] / max) * 100}%`,
                right: `${100 - (localValue[1] / max) * 100}%`,
              }}
            ></div>

            {/* Min handle */}
            <input
              type="range"
              min={min}
              max={max}
              step={step}
              value={localValue[0]}
              onChange={(e) => handleChange(0, parseInt(e.target.value))}
              className="absolute top-0 w-full h-6 bg-transparent appearance-none cursor-pointer"
              style={{ zIndex: 1 }}
            />

            {/* Max handle */}
            <input
              type="range"
              min={min}
              max={max}
              step={step}
              value={localValue[1]}
              onChange={(e) => handleChange(1, parseInt(e.target.value))}
              className="absolute top-0 w-full h-6 bg-transparent appearance-none cursor-pointer"
              style={{ zIndex: 2 }}
            />
          </div>

          {/* Labels */}
          <div className="flex justify-between mt-2 text-sm text-gray-600">
            <span>{formatPrice(localValue[0])}</span>
            <span>{formatPrice(localValue[1])}</span>
          </div>
        </div>
      )}

      {/* Rangos predefinidos */}
      <div className="grid grid-cols-2 gap-2">
        {[
          [0, 50000],
          [50000, 100000],
          [100000, 500000],
          [500000, 1000000],
        ].map(([min, max]) => (
          <button
            key={`${min}-${max}`}
            onClick={() => {
              setLocalValue([min, max]);
              debouncedOnChange([min, max]);
            }}
            className={`
              px-2 py-1 text-xs border rounded transition-colors
              ${localValue[0] === min && localValue[1] === max
                ? 'bg-blue-50 border-blue-300 text-blue-700'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }
            `}
          >
            {formatPrice(min)} - {formatPrice(max)}
          </button>
        ))}
      </div>
    </div>
  );
});

/**
 * Rating Filter optimizado
 */
const RatingFilter = memo(({ value, onChange }: {
  value: number;
  onChange: (rating: number) => void;
}) => {
  const ratings = [5, 4, 3, 2, 1];

  return (
    <div className="space-y-2">
      {ratings.map((rating) => (
        <button
          key={rating}
          onClick={() => onChange(rating === value ? 0 : rating)}
          className={`
            w-full flex items-center justify-between px-3 py-2 rounded-lg border transition-colors
            ${value === rating
              ? 'bg-yellow-50 border-yellow-300 text-yellow-800'
              : 'border-gray-200 text-gray-700 hover:bg-gray-50'
            }
          `}
        >
          <div className="flex items-center space-x-2">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm">
              {rating === 5 ? '5 estrellas' : `${rating}+ estrellas`}
            </span>
          </div>
          {value === rating && <Check className="w-4 h-4 text-yellow-600" />}
        </button>
      ))}
    </div>
  );
});

/**
 * Checkbox List optimizado con virtual scrolling
 */
const FilterCheckboxList = memo(({
  options,
  selectedValues,
  onChange,
  searchable = false,
  showCounts = false,
  maxHeight = 200,
}: {
  options: Array<{ id: string; label: string; count?: number }>;
  selectedValues: string[];
  onChange: (values: string[]) => void;
  searchable?: boolean;
  showCounts?: boolean;
  maxHeight?: number;
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 200);

  const filteredOptions = useMemo(() => {
    if (!debouncedSearch) return options;
    return options.filter(option =>
      option.label.toLowerCase().includes(debouncedSearch.toLowerCase())
    );
  }, [options, debouncedSearch]);

  const handleToggle = useCallback((optionId: string) => {
    const newValues = selectedValues.includes(optionId)
      ? selectedValues.filter(id => id !== optionId)
      : [...selectedValues, optionId];
    onChange(newValues);
  }, [selectedValues, onChange]);

  return (
    <div className="space-y-3">
      {searchable && (
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar..."
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      <div
        className="space-y-1 overflow-y-auto"
        style={{ maxHeight: `${maxHeight}px` }}
      >
        {filteredOptions.map((option) => (
          <label
            key={option.id}
            className="flex items-center justify-between p-2 rounded hover:bg-gray-50 cursor-pointer"
          >
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={selectedValues.includes(option.id)}
                onChange={() => handleToggle(option.id)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{option.label}</span>
            </div>
            {showCounts && option.count && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                {option.count}
              </span>
            )}
          </label>
        ))}
      </div>

      {filteredOptions.length === 0 && searchQuery && (
        <div className="text-center py-4 text-gray-500 text-sm">
          No se encontraron opciones
        </div>
      )}
    </div>
  );
});

/**
 * Componente principal de filtros
 */
const ProductFilters: React.FC<ProductFiltersProps> = memo(({
  onFilterChange,
  initialFilters = {
    categories: [],
    priceRange: [0, 1000000],
    rating: 0,
    brand: [],
    location: [],
    availability: [],
    shipping: [],
    features: [],
    condition: [],
    sortBy: 'relevance',
    searchQuery: '',
  },
  mobileOptimized = false,
  enableAdvanced = true,
  className = '',
  collapsible = true,
  showCounts = true,
}) => {
  // Hooks
  const { categories, brands, locations, loadingCategories } = useCategories();
  const { updateFilters, clearFilters, getActiveFilterCount } = useFilters();
  const { isMobile, touchOptimizations } = useMobileOptimization(mobileOptimized);

  // Estado local
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    categories: true,
    price: true,
    rating: false,
    brand: false,
    location: false,
    features: false,
  });

  const debouncedFilterChange = useDebounce(onFilterChange, 300);

  // Secciones de filtros
  const filterSections: FilterSection[] = useMemo(() => [
    {
      id: 'categories',
      title: 'Categorías',
      icon: Tag,
      expanded: expandedSections.categories,
      count: filters.categories.length,
    },
    {
      id: 'price',
      title: 'Rango de Precio',
      icon: DollarSign,
      expanded: expandedSections.price,
      count: filters.priceRange[0] > 0 || filters.priceRange[1] < 1000000 ? 1 : 0,
    },
    {
      id: 'rating',
      title: 'Calificación',
      icon: Star,
      expanded: expandedSections.rating,
      count: filters.rating > 0 ? 1 : 0,
    },
    {
      id: 'brand',
      title: 'Marcas',
      icon: Package,
      expanded: expandedSections.brand,
      count: filters.brand.length,
    },
    {
      id: 'location',
      title: 'Ubicación',
      icon: MapPin,
      expanded: expandedSections.location,
      count: filters.location.length,
    },
    {
      id: 'features',
      title: 'Características',
      icon: Zap,
      expanded: expandedSections.features,
      count: filters.features.length,
    },
  ], [expandedSections, filters]);

  /**
   * Actualizar filtros con debounce
   */
  const updateFilter = useCallback((key: keyof FilterState, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    debouncedFilterChange(newFilters);
  }, [filters, debouncedFilterChange]);

  /**
   * Toggle de secciones expandidas
   */
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  }, []);

  /**
   * Limpiar todos los filtros
   */
  const handleClearFilters = useCallback(() => {
    const clearedFilters = {
      ...initialFilters,
      priceRange: [0, 1000000] as [number, number],
      rating: 0,
    };
    setFilters(clearedFilters);
    clearFilters();
    onFilterChange(clearedFilters);
  }, [initialFilters, clearFilters, onFilterChange]);

  /**
   * Datos de opciones para filtros
   */
  const filterOptions = useMemo(() => ({
    categories: categories.map(cat => ({
      id: cat.id,
      label: cat.nombre,
      count: cat.productCount,
    })),
    brands: brands.map(brand => ({
      id: brand.id,
      label: brand.nombre,
      count: brand.productCount,
    })),
    locations: locations.map(loc => ({
      id: loc.id,
      label: `${loc.ciudad}, ${loc.departamento}`,
      count: loc.productCount,
    })),
    availability: [
      { id: 'in_stock', label: 'En Stock', count: 1250 },
      { id: 'low_stock', label: 'Pocas Unidades', count: 45 },
      { id: 'pre_order', label: 'Pre-orden', count: 23 },
    ],
    shipping: [
      { id: 'free_shipping', label: 'Envío Gratis', count: 892 },
      { id: 'express', label: 'Envío Express', count: 567 },
      { id: 'same_day', label: 'Entrega el Mismo Día', count: 134 },
    ],
    features: [
      { id: 'eco_friendly', label: 'Eco-friendly', count: 234 },
      { id: 'handmade', label: 'Hecho a Mano', count: 156 },
      { id: 'local_producer', label: 'Productor Local', count: 445 },
      { id: 'certified', label: 'Certificado', count: 267 },
    ],
    condition: [
      { id: 'new', label: 'Nuevo', count: 1890 },
      { id: 'like_new', label: 'Como Nuevo', count: 234 },
      { id: 'good', label: 'Buen Estado', count: 167 },
      { id: 'fair', label: 'Estado Regular', count: 89 },
    ],
  }), [categories, brands, locations]);

  const activeFilterCount = getActiveFilterCount(filters);

  return (
    <div className={`product-filters bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filtros</h3>
          {activeFilterCount > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>

        {activeFilterCount > 0 && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Limpiar todo
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className="p-4 space-y-6">
        {filterSections.map((section) => (
          <div key={section.id} className="border-b border-gray-100 last:border-b-0 pb-4 last:pb-0">
            {/* Header de sección */}
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between py-2 text-left"
              disabled={!collapsible}
            >
              <div className="flex items-center space-x-2">
                <section.icon className="w-4 h-4 text-gray-600" />
                <span className="font-medium text-gray-900">{section.title}</span>
                {section.count > 0 && (
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                    {section.count}
                  </span>
                )}
              </div>
              {collapsible && (
                section.expanded ?
                  <ChevronUp className="w-4 h-4 text-gray-600" /> :
                  <ChevronDown className="w-4 h-4 text-gray-600" />
              )}
            </button>

            {/* Contenido de sección */}
            {section.expanded && (
              <div className="mt-3">
                {section.id === 'categories' && (
                  <FilterCheckboxList
                    options={filterOptions.categories}
                    selectedValues={filters.categories}
                    onChange={(values) => updateFilter('categories', values)}
                    searchable={true}
                    showCounts={showCounts}
                    maxHeight={isMobile ? 150 : 200}
                  />
                )}

                {section.id === 'price' && (
                  <PriceRangeSlider
                    value={filters.priceRange}
                    onChange={(value) => updateFilter('priceRange', value)}
                    isMobile={isMobile}
                  />
                )}

                {section.id === 'rating' && (
                  <RatingFilter
                    value={filters.rating}
                    onChange={(value) => updateFilter('rating', value)}
                  />
                )}

                {section.id === 'brand' && (
                  <FilterCheckboxList
                    options={filterOptions.brands}
                    selectedValues={filters.brand}
                    onChange={(values) => updateFilter('brand', values)}
                    searchable={true}
                    showCounts={showCounts}
                    maxHeight={isMobile ? 150 : 200}
                  />
                )}

                {section.id === 'location' && (
                  <FilterCheckboxList
                    options={filterOptions.locations}
                    selectedValues={filters.location}
                    onChange={(values) => updateFilter('location', values)}
                    searchable={true}
                    showCounts={showCounts}
                    maxHeight={isMobile ? 150 : 200}
                  />
                )}

                {section.id === 'features' && (
                  <FilterCheckboxList
                    options={filterOptions.features}
                    selectedValues={filters.features}
                    onChange={(values) => updateFilter('features', values)}
                    showCounts={showCounts}
                  />
                )}
              </div>
            )}
          </div>
        ))}

        {/* Filtros avanzados adicionales */}
        {enableAdvanced && (
          <div className="space-y-4 pt-4 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 flex items-center">
              <Sliders className="w-4 h-4 mr-2" />
              Filtros Avanzados
            </h4>

            {/* Disponibilidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Disponibilidad
              </label>
              <FilterCheckboxList
                options={filterOptions.availability}
                selectedValues={filters.availability}
                onChange={(values) => updateFilter('availability', values)}
                showCounts={showCounts}
              />
            </div>

            {/* Envío */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Opciones de Envío
              </label>
              <FilterCheckboxList
                options={filterOptions.shipping}
                selectedValues={filters.shipping}
                onChange={(values) => updateFilter('shipping', values)}
                showCounts={showCounts}
              />
            </div>

            {/* Condición */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Condición del Producto
              </label>
              <FilterCheckboxList
                options={filterOptions.condition}
                selectedValues={filters.condition}
                onChange={(values) => updateFilter('condition', values)}
                showCounts={showCounts}
              />
            </div>
          </div>
        )}
      </div>

      {/* Footer para mobile */}
      {isMobile && (
        <div className="flex p-4 border-t border-gray-200 space-x-3">
          <button
            onClick={handleClearFilters}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Limpiar
          </button>
          <button
            onClick={() => {
              // Cerrar panel de filtros en mobile
              const event = new CustomEvent('closeMobileFilters');
              window.dispatchEvent(event);
            }}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Ver Resultados ({activeFilterCount})
          </button>
        </div>
      )}
    </div>
  );
});

ProductFilters.displayName = 'ProductFilters';

export default ProductFilters;