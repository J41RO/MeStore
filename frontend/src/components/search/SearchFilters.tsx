// ~/src/components/search/SearchFilters.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - SearchFilters Component with Advanced Filtering
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchFilters.tsx
// Ruta: ~/src/components/search/SearchFilters.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente de filtros avanzados para búsqueda
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useState, useCallback, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  X,
  Filter,
  RotateCcw,
  Check,
  Star,
  Calendar,
  MapPin,
  Tag,
  Building2,
} from 'lucide-react';
import { useSearchFilters } from '../../hooks/search';
import { SearchFiltersProps, SearchFilters as SearchFiltersType } from '../../types/search.types';

interface FilterSectionProps {
  title: string;
  icon: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  badge?: number;
}

/**
 * Componente de sección de filtro colapsible
 */
const FilterSection: React.FC<FilterSectionProps> = memo(({
  title,
  icon,
  isOpen,
  onToggle,
  children,
  badge,
}) => (
  <div className="border-b border-gray-200 last:border-b-0">
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between py-4 px-2 hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center space-x-3">
        {icon}
        <span className="font-medium text-gray-900">{title}</span>
        {badge !== undefined && badge > 0 && (
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
            {badge}
          </span>
        )}
      </div>
      {isOpen ? (
        <ChevronUp className="w-4 h-4 text-gray-500" />
      ) : (
        <ChevronDown className="w-4 h-4 text-gray-500" />
      )}
    </button>
    {isOpen && (
      <div className="pb-4 px-2">
        {children}
      </div>
    )}
  </div>
));

FilterSection.displayName = 'FilterSection';

/**
 * Componente de checkbox personalizado
 */
const FilterCheckbox: React.FC<{
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  count?: number;
}> = memo(({ checked, onChange, label, count }) => (
  <label className="flex items-center space-x-3 py-2 cursor-pointer hover:bg-gray-50 rounded px-2">
    <div className="relative">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      <div
        className={`w-4 h-4 border-2 rounded transition-all ${
          checked
            ? 'bg-blue-600 border-blue-600'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        {checked && (
          <Check className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
        )}
      </div>
    </div>
    <span className="flex-1 text-sm text-gray-700">{label}</span>
    {count !== undefined && (
      <span className="text-xs text-gray-500">({count})</span>
    )}
  </label>
));

FilterCheckbox.displayName = 'FilterCheckbox';

/**
 * Componente de rango de precios
 */
const PriceRangeFilter: React.FC<{
  min: number;
  max: number;
  globalMin: number;
  globalMax: number;
  onChange: (min: number, max: number) => void;
}> = memo(({ min, max, globalMin, globalMax, onChange }) => {
  const [localMin, setLocalMin] = useState(min);
  const [localMax, setLocalMax] = useState(max);

  useEffect(() => {
    setLocalMin(min);
    setLocalMax(max);
  }, [min, max]);

  const handleMinChange = useCallback((value: number) => {
    const newMin = Math.min(value, localMax);
    setLocalMin(newMin);
    onChange(newMin, localMax);
  }, [localMax, onChange]);

  const handleMaxChange = useCallback((value: number) => {
    const newMax = Math.max(value, localMin);
    setLocalMax(newMax);
    onChange(localMin, newMax);
  }, [localMin, onChange]);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Mínimo
          </label>
          <input
            type="number"
            value={localMin}
            onChange={(e) => handleMinChange(Number(e.target.value))}
            min={globalMin}
            max={globalMax}
            className="w-full px-3 py-1 text-sm border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Máximo
          </label>
          <input
            type="number"
            value={localMax}
            onChange={(e) => handleMaxChange(Number(e.target.value))}
            min={globalMin}
            max={globalMax}
            className="w-full px-3 py-1 text-sm border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Range slider */}
      <div className="relative">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">${globalMin.toLocaleString()}</span>
          <div className="flex-1 relative">
            <input
              type="range"
              min={globalMin}
              max={globalMax}
              value={localMin}
              onChange={(e) => handleMinChange(Number(e.target.value))}
              className="absolute w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <input
              type="range"
              min={globalMin}
              max={globalMax}
              value={localMax}
              onChange={(e) => handleMaxChange(Number(e.target.value))}
              className="absolute w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <span className="text-xs text-gray-500">${globalMax.toLocaleString()}</span>
        </div>
      </div>

      <div className="text-center text-sm text-gray-600">
        ${localMin.toLocaleString()} - ${localMax.toLocaleString()}
      </div>
    </div>
  );
});

PriceRangeFilter.displayName = 'PriceRangeFilter';

/**
 * Componente de rating con estrellas
 */
const RatingFilter: React.FC<{
  minRating: number;
  onChange: (rating: number) => void;
}> = memo(({ minRating, onChange }) => {
  const ratings = [1, 2, 3, 4, 5];

  return (
    <div className="space-y-2">
      {ratings.reverse().map((rating) => (
        <label
          key={rating}
          className="flex items-center space-x-2 py-1 cursor-pointer hover:bg-gray-50 rounded px-2"
        >
          <input
            type="radio"
            name="rating"
            checked={minRating === rating}
            onChange={() => onChange(rating)}
            className="text-blue-600 focus:ring-blue-500"
          />
          <div className="flex items-center space-x-1">
            {Array.from({ length: 5 }).map((_, i) => (
              <Star
                key={i}
                className={`w-4 h-4 ${
                  i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                }`}
              />
            ))}
            <span className="text-sm text-gray-700">y más</span>
          </div>
        </label>
      ))}
      {minRating > 0 && (
        <button
          onClick={() => onChange(0)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Limpiar filtro
        </button>
      )}
    </div>
  );
});

RatingFilter.displayName = 'RatingFilter';

/**
 * Componente principal de filtros de búsqueda
 */
const SearchFilters: React.FC<SearchFiltersProps> = memo(({
  className = '',
  collapsible = true,
  showClearAll = true,
  orientation = 'vertical',
}) => {
  // Hooks
  const {
    filters,
    activeFiltersCount,
    categories,
    vendors,
    priceRanges,
    loadingCategories,
    loadingVendors,
    setFilter,
    toggleFilter,
    clearAllFilters,
    isFilterActive,
  } = useSearchFilters();

  // Estado de secciones colapsadas
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    categories: true,
    price: true,
    vendors: false,
    rating: false,
    stock: false,
    date: false,
  });

  /**
   * Toggle de sección
   */
  const toggleSection = useCallback((section: string) => {
    if (!collapsible) return;

    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, [collapsible]);

  /**
   * Filtros activos individuales
   */
  const activeCategoryCount = filters.categories.length;
  const activeVendorCount = filters.vendors.length;
  const activePriceCount = isFilterActive('priceRange') ? 1 : 0;
  const activeRatingCount = isFilterActive('minRating') ? 1 : 0;
  const activeStockCount = isFilterActive('inStock') ? 1 : 0;

  /**
   * Manejar cambio de categoría
   */
  const handleCategoryChange = useCallback((categoryId: string, checked: boolean) => {
    toggleFilter('categories', categoryId);
  }, [toggleFilter]);

  /**
   * Manejar cambio de vendor
   */
  const handleVendorChange = useCallback((vendorId: string, checked: boolean) => {
    toggleFilter('vendors', vendorId);
  }, [toggleFilter]);

  /**
   * Manejar cambio de rango de precios
   */
  const handlePriceRangeChange = useCallback((min: number, max: number) => {
    setFilter('priceRange', { min, max });
  }, [setFilter]);

  /**
   * Manejar cambio de rating
   */
  const handleRatingChange = useCallback((rating: number) => {
    setFilter('minRating', rating);
  }, [setFilter]);

  /**
   * Manejar toggle de stock
   */
  const handleStockToggle = useCallback((checked: boolean) => {
    setFilter('inStock', checked);
  }, [setFilter]);

  /**
   * Classes para orientación
   */
  const containerClasses = orientation === 'horizontal'
    ? 'flex flex-wrap gap-6'
    : 'space-y-0';

  const sectionClasses = orientation === 'horizontal'
    ? 'min-w-64'
    : 'w-full';

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="font-medium text-gray-900">Filtros</h3>
          {activeFiltersCount > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
              {activeFiltersCount}
            </span>
          )}
        </div>

        {showClearAll && activeFiltersCount > 0 && (
          <button
            onClick={clearAllFilters}
            className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Limpiar todo</span>
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className={`p-4 ${containerClasses}`}>
        {/* Categorías */}
        <div className={sectionClasses}>
          <FilterSection
            title="Categorías"
            icon={<Tag className="w-4 h-4 text-gray-600" />}
            isOpen={!collapsible || openSections.categories}
            onToggle={() => toggleSection('categories')}
            badge={activeCategoryCount}
          >
            {loadingCategories ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-8 bg-gray-200 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {categories.map((category) => (
                  <FilterCheckbox
                    key={category.value}
                    checked={filters.categories.includes(category.value)}
                    onChange={(checked) => handleCategoryChange(category.value, checked)}
                    label={category.label}
                    count={category.count}
                  />
                ))}
              </div>
            )}
          </FilterSection>
        </div>

        {/* Rango de precios */}
        <div className={sectionClasses}>
          <FilterSection
            title="Precio"
            icon={<span className="w-4 h-4 text-gray-600">$</span>}
            isOpen={!collapsible || openSections.price}
            onToggle={() => toggleSection('price')}
            badge={activePriceCount}
          >
            <PriceRangeFilter
              min={filters.priceRange.min}
              max={filters.priceRange.max}
              globalMin={priceRanges.min}
              globalMax={priceRanges.max}
              onChange={handlePriceRangeChange}
            />
          </FilterSection>
        </div>

        {/* Vendors */}
        <div className={sectionClasses}>
          <FilterSection
            title="Vendedores"
            icon={<Building2 className="w-4 h-4 text-gray-600" />}
            isOpen={!collapsible || openSections.vendors}
            onToggle={() => toggleSection('vendors')}
            badge={activeVendorCount}
          >
            {loadingVendors ? (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-8 bg-gray-200 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {vendors.slice(0, 10).map((vendor) => (
                  <FilterCheckbox
                    key={vendor.value}
                    checked={filters.vendors.includes(vendor.value)}
                    onChange={(checked) => handleVendorChange(vendor.value, checked)}
                    label={vendor.label}
                    count={vendor.count}
                  />
                ))}
              </div>
            )}
          </FilterSection>
        </div>

        {/* Rating */}
        <div className={sectionClasses}>
          <FilterSection
            title="Calificación"
            icon={<Star className="w-4 h-4 text-gray-600" />}
            isOpen={!collapsible || openSections.rating}
            onToggle={() => toggleSection('rating')}
            badge={activeRatingCount}
          >
            <RatingFilter
              minRating={filters.minRating}
              onChange={handleRatingChange}
            />
          </FilterSection>
        </div>

        {/* Disponibilidad */}
        <div className={sectionClasses}>
          <FilterSection
            title="Disponibilidad"
            icon={<Check className="w-4 h-4 text-gray-600" />}
            isOpen={!collapsible || openSections.stock}
            onToggle={() => toggleSection('stock')}
            badge={activeStockCount}
          >
            <FilterCheckbox
              checked={filters.inStock}
              onChange={handleStockToggle}
              label="Solo productos en stock"
            />
          </FilterSection>
        </div>
      </div>

      {/* Chips de filtros activos */}
      {activeFiltersCount > 0 && (
        <div className="px-4 pb-4">
          <div className="flex flex-wrap gap-2">
            {filters.categories.map((categoryId) => {
              const category = categories.find(c => c.value === categoryId);
              return category ? (
                <span
                  key={categoryId}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {category.label}
                  <button
                    onClick={() => handleCategoryChange(categoryId, false)}
                    className="ml-1 hover:text-blue-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ) : null;
            })}

            {filters.vendors.map((vendorId) => {
              const vendor = vendors.find(v => v.value === vendorId);
              return vendor ? (
                <span
                  key={vendorId}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  {vendor.label}
                  <button
                    onClick={() => handleVendorChange(vendorId, false)}
                    className="ml-1 hover:text-green-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ) : null;
            })}

            {isFilterActive('priceRange') && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                ${filters.priceRange.min.toLocaleString()} - ${filters.priceRange.max.toLocaleString()}
                <button
                  onClick={() => handlePriceRangeChange(0, 999999)}
                  className="ml-1 hover:text-purple-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}

            {isFilterActive('minRating') && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                {filters.minRating}+ estrellas
                <button
                  onClick={() => handleRatingChange(0)}
                  className="ml-1 hover:text-yellow-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}

            {isFilterActive('inStock') && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                En stock
                <button
                  onClick={() => handleStockToggle(false)}
                  className="ml-1 hover:text-green-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

SearchFilters.displayName = 'SearchFilters';

export default SearchFilters;