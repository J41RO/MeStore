import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Filter, RotateCcw } from 'lucide-react';

interface FilterOption {
  value: string;
  label: string;
  count?: number;
}

interface CategoryFiltersProps {
  categorySlug: string;
  filters: {
    precio_min: string;
    precio_max: string;
    sort_by: string;
    sort_order: string;
    brand?: string;
    size?: string;
    color?: string;
    condition?: string;
    availability?: string;
  };
  onFiltersChange: (filters: any) => void;
  availableFilters?: {
    brands?: FilterOption[];
    sizes?: FilterOption[];
    colors?: FilterOption[];
    priceRanges?: FilterOption[];
  };
  productCount?: number;
}

// Filtros específicos por categoría
const CATEGORY_SPECIFIC_FILTERS: Record<string, string[]> = {
  'electronics': ['brand', 'condition', 'warranty'],
  'fashion': ['brand', 'size', 'color', 'material'],
  'home': ['brand', 'room', 'material', 'style'],
  'sports': ['brand', 'size', 'sport_type', 'level'],
  'books': ['author', 'genre', 'language', 'format'],
  'beauty': ['brand', 'skin_type', 'category_type'],
  'baby': ['brand', 'age_range', 'safety_certified'],
  'automotive': ['brand', 'vehicle_type', 'compatibility', 'condition']
};

// Opciones predefinidas por filtro
const FILTER_OPTIONS: Record<string, FilterOption[]> = {
  brand: [
    { value: 'apple', label: 'Apple', count: 45 },
    { value: 'samsung', label: 'Samsung', count: 38 },
    { value: 'nike', label: 'Nike', count: 67 },
    { value: 'adidas', label: 'Adidas', count: 52 },
    { value: 'sony', label: 'Sony', count: 29 }
  ],
  size: [
    { value: 'xs', label: 'XS', count: 12 },
    { value: 's', label: 'S', count: 25 },
    { value: 'm', label: 'M', count: 38 },
    { value: 'l', label: 'L', count: 35 },
    { value: 'xl', label: 'XL', count: 28 },
    { value: 'xxl', label: 'XXL', count: 15 }
  ],
  color: [
    { value: 'black', label: 'Negro', count: 45 },
    { value: 'white', label: 'Blanco', count: 38 },
    { value: 'blue', label: 'Azul', count: 32 },
    { value: 'red', label: 'Rojo', count: 28 },
    { value: 'green', label: 'Verde', count: 22 }
  ],
  condition: [
    { value: 'new', label: 'Nuevo', count: 156 },
    { value: 'like_new', label: 'Como nuevo', count: 45 },
    { value: 'good', label: 'Buen estado', count: 32 },
    { value: 'fair', label: 'Estado regular', count: 18 }
  ]
};

// Rangos de precio sugeridos por categoría
const PRICE_RANGES: Record<string, FilterOption[]> = {
  'electronics': [
    { value: '0-100000', label: 'Hasta $100.000' },
    { value: '100000-500000', label: '$100.000 - $500.000' },
    { value: '500000-1000000', label: '$500.000 - $1.000.000' },
    { value: '1000000-5000000', label: '$1.000.000 - $5.000.000' },
    { value: '5000000-', label: 'Más de $5.000.000' }
  ],
  'fashion': [
    { value: '0-50000', label: 'Hasta $50.000' },
    { value: '50000-100000', label: '$50.000 - $100.000' },
    { value: '100000-200000', label: '$100.000 - $200.000' },
    { value: '200000-500000', label: '$200.000 - $500.000' },
    { value: '500000-', label: 'Más de $500.000' }
  ],
  default: [
    { value: '0-50000', label: 'Hasta $50.000' },
    { value: '50000-200000', label: '$50.000 - $200.000' },
    { value: '200000-500000', label: '$200.000 - $500.000' },
    { value: '500000-1000000', label: '$500.000 - $1.000.000' },
    { value: '1000000-', label: 'Más de $1.000.000' }
  ]
};

const CategoryFilters: React.FC<CategoryFiltersProps> = ({
  categorySlug,
  filters,
  onFiltersChange,
  productCount = 0
}) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    price: true,
    brand: true,
    attributes: false
  });

  const specificFilters = CATEGORY_SPECIFIC_FILTERS[categorySlug] || ['brand', 'condition'];
  const priceRanges = PRICE_RANGES[categorySlug] || PRICE_RANGES.default;

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handlePriceRangeSelect = (range: string) => {
    if (range.includes('-')) {
      const [min, max] = range.split('-');
      onFiltersChange({
        precio_min: min || '',
        precio_max: max || ''
      });
    } else if (range.endsWith('-')) {
      onFiltersChange({
        precio_min: range.replace('-', ''),
        precio_max: ''
      });
    }
  };

  const clearAllFilters = () => {
    onFiltersChange({
      precio_min: '',
      precio_max: '',
      brand: '',
      size: '',
      color: '',
      condition: '',
      availability: ''
    });
  };

  const hasActiveFilters = () => {
    return !!(filters.precio_min || filters.precio_max || filters.brand || 
              filters.size || filters.color || filters.condition);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Filter Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Filtros</h3>
          {productCount > 0 && (
            <span className="text-sm text-gray-500">
              ({productCount.toLocaleString()} productos)
            </span>
          )}
        </div>
        
        {hasActiveFilters() && (
          <button
            onClick={clearAllFilters}
            className="flex items-center space-x-1 text-sm text-red-600 hover:text-red-700"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Limpiar filtros</span>
          </button>
        )}
      </div>

      <div className="p-4 space-y-6">
        {/* Price Filter */}
        <div>
          <button
            onClick={() => toggleSection('price')}
            className="flex items-center justify-between w-full text-left"
          >
            <h4 className="font-medium text-gray-900">Precio</h4>
            {expandedSections.price ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </button>

          {expandedSections.price && (
            <div className="mt-3 space-y-3">
              {/* Custom Price Range */}
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  placeholder="Mín"
                  value={filters.precio_min}
                  onChange={(e) => onFiltersChange({ precio_min: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-gray-500">-</span>
                <input
                  type="number"
                  placeholder="Máx"
                  value={filters.precio_max}
                  onChange={(e) => onFiltersChange({ precio_max: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Predefined Price Ranges */}
              <div className="space-y-2">
                {priceRanges?.map((range) => (
                  <button
                    key={range.value}
                    onClick={() => handlePriceRangeSelect(range.value)}
                    className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
                  >
                    {range.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Brand Filter */}
        {specificFilters.includes('brand') && (
          <div>
            <button
              onClick={() => toggleSection('brand')}
              className="flex items-center justify-between w-full text-left"
            >
              <h4 className="font-medium text-gray-900">Marca</h4>
              {expandedSections.brand ? (
                <ChevronUp className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              )}
            </button>

            {expandedSections.brand && (
              <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
                {FILTER_OPTIONS.brand?.map((option) => (
                  <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.brand === option.value}
                      onChange={(e) => onFiltersChange({
                        brand: e.target.checked ? option.value : ''
                      })}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{option.label}</span>
                    {option.count && (
                      <span className="text-xs text-gray-500">({option.count})</span>
                    )}
                  </label>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Size Filter (for fashion) */}
        {specificFilters.includes('size') && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Talla</h4>
            <div className="flex flex-wrap gap-2">
              {FILTER_OPTIONS.size?.map((option) => (
                <button
                  key={option.value}
                  onClick={() => onFiltersChange({
                    size: filters.size === option.value ? '' : option.value
                  })}
                  className={`px-3 py-1 text-sm border rounded-md transition-colors ${
                    filters.size === option.value
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Color Filter (for fashion) */}
        {specificFilters.includes('color') && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Color</h4>
            <div className="space-y-2">
              {FILTER_OPTIONS.color?.map((option) => (
                <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="color"
                    checked={filters.color === option.value}
                    onChange={() => onFiltersChange({ color: option.value })}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{option.label}</span>
                  {option.count && (
                    <span className="text-xs text-gray-500">({option.count})</span>
                  )}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Condition Filter */}
        {specificFilters.includes('condition') && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Estado</h4>
            <div className="space-y-2">
              {FILTER_OPTIONS.condition?.map((option) => (
                <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="condition"
                    checked={filters.condition === option.value}
                    onChange={() => onFiltersChange({ condition: option.value })}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{option.label}</span>
                  {option.count && (
                    <span className="text-xs text-gray-500">({option.count})</span>
                  )}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Availability Filter */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Disponibilidad</h4>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.availability === 'in_stock'}
                onChange={(e) => onFiltersChange({
                  availability: e.target.checked ? 'in_stock' : ''
                })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Solo productos en stock</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CategoryFilters;