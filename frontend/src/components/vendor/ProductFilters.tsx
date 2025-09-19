/**
 * ProductFilters - Advanced search and filter controls for vendor products
 *
 * Features:
 * - Text search with debouncing
 * - Category and status filtering
 * - Price range filtering
 * - Stock level filtering
 * - Date range filtering
 * - Quick filter presets
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useProductStore, productSelectors } from '../../stores/productStore.new';
import { useCategoryStore } from '../../stores/categoryStore';
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  AdjustmentsHorizontalIcon,
  FunnelIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  TagIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { ProductFilters as ProductFiltersType } from '../../types';

interface ProductFiltersProps {
  onApply?: () => void; // Callback for mobile filters modal
}

/**
 * Debounced search input hook
 */
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Quick filter preset
 */
interface QuickFilter {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  filters: Partial<ProductFiltersType>;
  color: string;
}

const quickFilters: QuickFilter[] = [
  {
    label: 'Activos',
    icon: EyeIcon,
    filters: { is_active: true },
    color: 'bg-green-100 text-green-800 border-green-200',
  },
  {
    label: 'Inactivos',
    icon: EyeSlashIcon,
    filters: { is_active: false },
    color: 'bg-gray-100 text-gray-800 border-gray-200',
  },
  {
    label: 'Stock Bajo',
    icon: ExclamationTriangleIcon,
    filters: { stock_status: 'low' },
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  },
  {
    label: 'Sin Stock',
    icon: ExclamationTriangleIcon,
    filters: { stock_status: 'out' },
    color: 'bg-red-100 text-red-800 border-red-200',
  },
];

/**
 * Main ProductFilters component
 */
const ProductFilters: React.FC<ProductFiltersProps> = ({ onApply }) => {
  // Store hooks
  const {
    setFilters,
    setSearchQuery,
    clearProducts
  } = useProductStore();

  const searchQuery = useProductStore(productSelectors.searchQuery);
  const filters = useProductStore(productSelectors.filters);
  const { categories, fetchCategories } = useCategoryStore();

  // Local state
  const [localSearchQuery, setLocalSearchQuery] = useState(searchQuery);
  const [localFilters, setLocalFilters] = useState<Partial<ProductFiltersType>>(filters);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [activeQuickFilter, setActiveQuickFilter] = useState<string | null>(null);

  // Debounced search
  const debouncedSearchQuery = useDebounce(localSearchQuery, 300);

  /**
   * Initialize component
   */
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  /**
   * Update search query when debounced value changes
   */
  useEffect(() => {
    if (debouncedSearchQuery !== searchQuery) {
      setSearchQuery(debouncedSearchQuery);
    }
  }, [debouncedSearchQuery, searchQuery, setSearchQuery]);

  /**
   * Handle filter changes
   */
  const handleFilterChange = useCallback((newFilters: Partial<ProductFiltersType>) => {
    const updatedFilters = { ...localFilters, ...newFilters };
    setLocalFilters(updatedFilters);
    setFilters(updatedFilters);
    setActiveQuickFilter(null); // Clear quick filter when manual filter is applied
  }, [localFilters, setFilters]);

  /**
   * Handle quick filter selection
   */
  const handleQuickFilter = (quickFilter: QuickFilter) => {
    if (activeQuickFilter === quickFilter.label) {
      // Deactivate if already active
      setActiveQuickFilter(null);
      setLocalFilters({});
      setFilters({});
    } else {
      setActiveQuickFilter(quickFilter.label);
      setLocalFilters(quickFilter.filters);
      setFilters(quickFilter.filters);
    }
  };

  /**
   * Handle price range filter
   */
  const handlePriceRangeChange = () => {
    const minPrice = priceRange.min ? parseFloat(priceRange.min) : undefined;
    const maxPrice = priceRange.max ? parseFloat(priceRange.max) : undefined;

    handleFilterChange({
      min_price: minPrice,
      max_price: maxPrice,
    });
  };

  /**
   * Handle date range filter
   */
  const handleDateRangeChange = () => {
    handleFilterChange({
      created_after: dateRange.from || undefined,
      created_before: dateRange.to || undefined,
    });
  };

  /**
   * Clear all filters
   */
  const handleClearFilters = () => {
    setLocalSearchQuery('');
    setLocalFilters({});
    setPriceRange({ min: '', max: '' });
    setDateRange({ from: '', to: '' });
    setActiveQuickFilter(null);
    setSearchQuery('');
    setFilters({});
  };

  /**
   * Check if any filters are active
   */
  const hasActiveFilters = localSearchQuery || Object.keys(localFilters).length > 0 || activeQuickFilter;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FunnelIcon className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Filtros</h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
          >
            <XMarkIcon className="w-4 h-4" />
            <span>Limpiar</span>
          </button>
        )}
      </div>

      {/* Search */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Buscar Productos
        </label>
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={localSearchQuery}
            onChange={(e) => setLocalSearchQuery(e.target.value)}
            placeholder="Buscar por nombre, descripción..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {localSearchQuery && (
            <button
              onClick={() => setLocalSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Quick Filters */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Filtros Rápidos
        </label>
        <div className="grid grid-cols-2 gap-2">
          {quickFilters.map((quickFilter) => {
            const Icon = quickFilter.icon;
            const isActive = activeQuickFilter === quickFilter.label;
            return (
              <button
                key={quickFilter.label}
                onClick={() => handleQuickFilter(quickFilter)}
                className={`p-3 text-sm font-medium border rounded-lg transition-colors flex items-center space-x-2 ${
                  isActive
                    ? quickFilter.color
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{quickFilter.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Category Filter */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Categoría
        </label>
        <select
          value={localFilters.category_id || ''}
          onChange={(e) => handleFilterChange({ category_id: e.target.value || undefined })}
          className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Todas las categorías</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      {/* Status Filters */}
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Estado del Producto
        </label>

        {/* Active Status */}
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="is_active"
              checked={localFilters.is_active === true}
              onChange={(e) => handleFilterChange({
                is_active: e.target.checked ? true : undefined
              })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="text-sm text-gray-700">
              Solo productos activos
            </label>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="is_featured"
              checked={localFilters.is_featured === true}
              onChange={(e) => handleFilterChange({
                is_featured: e.target.checked ? true : undefined
              })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_featured" className="text-sm text-gray-700">
              Solo productos destacados
            </label>
          </div>
        </div>
      </div>

      {/* Price Range */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Rango de Precio (COP)
        </label>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <input
              type="number"
              value={priceRange.min}
              onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
              onBlur={handlePriceRangeChange}
              placeholder="Mínimo"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <input
              type="number"
              value={priceRange.max}
              onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
              onBlur={handlePriceRangeChange}
              placeholder="Máximo"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Stock Level */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Nivel de Stock
        </label>
        <select
          value={localFilters.stock_status || ''}
          onChange={(e) => handleFilterChange({ stock_status: e.target.value as any || undefined })}
          className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Todos los niveles</option>
          <option value="in_stock">En stock</option>
          <option value="low">Stock bajo</option>
          <option value="out">Sin stock</option>
        </select>
      </div>

      {/* Date Range */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Fecha de Creación
        </label>
        <div className="grid grid-cols-1 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Desde</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value }))}
              onBlur={handleDateRangeChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Hasta</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value }))}
              onBlur={handleDateRangeChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Apply Button for Mobile */}
      {onApply && (
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={onApply}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Aplicar Filtros
          </button>
        </div>
      )}

      {/* Active Filters Summary */}
      {Object.keys(localFilters).length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Filtros Activos:</h4>
          <div className="space-y-2">
            {Object.entries(localFilters).map(([key, value]) => (
              value !== undefined && (
                <div key={key} className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">
                    {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                  </span>
                  <span className="font-medium text-gray-900">
                    {typeof value === 'boolean' ? (value ? 'Sí' : 'No') : String(value)}
                  </span>
                </div>
              )
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductFilters;