import React, { useState, useEffect } from 'react';
import { Search, Filter, X, ChevronDown } from 'lucide-react';

interface SearchFiltersProps {
  filters: {
    search: string;
    categoria: string;
    precio_min: string;
    precio_max: string;
    sort_by: string;
    sort_order: string;
  };
  onFiltersChange: (filters: any) => void;
  onSearch: (searchTerm: string) => void;
}

const CATEGORIES = [
  { value: '', label: 'Todas las categorías' },
  { value: 'electronica', label: 'Electrónica' },
  { value: 'ropa', label: 'Ropa y Accesorios' },
  { value: 'hogar', label: 'Hogar y Jardín' },
  { value: 'deportes', label: 'Deportes y Aire Libre' },
  { value: 'belleza', label: 'Belleza y Cuidado Personal' },
  { value: 'automotriz', label: 'Automotriz' },
  { value: 'libros', label: 'Libros y Medios' },
  { value: 'juguetes', label: 'Juguetes y Juegos' },
  { value: 'alimentacion', label: 'Alimentación' },
  { value: 'mascotas', label: 'Mascotas' },
  { value: 'otros', label: 'Otros' }
];

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Más recientes', order: 'desc' },
  { value: 'created_at', label: 'Más antiguos', order: 'asc' },
  { value: 'precio_venta', label: 'Precio: menor a mayor', order: 'asc' },
  { value: 'precio_venta', label: 'Precio: mayor a menor', order: 'desc' },
  { value: 'name', label: 'Nombre: A-Z', order: 'asc' },
  { value: 'name', label: 'Nombre: Z-A', order: 'desc' }
];

const SearchFilters: React.FC<SearchFiltersProps> = ({
  filters,
  onFiltersChange,
  onSearch
}) => {
  const [searchTerm, setSearchTerm] = useState(filters.search);
  const [isExpanded, setIsExpanded] = useState(false);

  // Sync search term with props
  useEffect(() => {
    setSearchTerm(filters.search);
  }, [filters.search]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchTerm);
  };

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    onFiltersChange(newFilters);
  };

  const handleSortChange = (value: string) => {
    const sortOption = SORT_OPTIONS.find(option => 
      `${option.value}-${option.order}` === value
    );
    
    if (sortOption) {
      const newFilters = {
        ...filters,
        sort_by: sortOption.value,
        sort_order: sortOption.order
      };
      onFiltersChange(newFilters);
    }
  };

  const clearFilters = () => {
    const clearedFilters = {
      search: '',
      categoria: '',
      precio_min: '',
      precio_max: '',
      sort_by: 'created_at',
      sort_order: 'desc'
    };
    setSearchTerm('');
    onFiltersChange(clearedFilters);
  };

  const hasActiveFilters = filters.categoria || filters.precio_min || filters.precio_max || 
    (filters.sort_by !== 'created_at' || filters.sort_order !== 'desc');

  const currentSortValue = `${filters.sort_by}-${filters.sort_order}`;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Search Bar */}
      <form onSubmit={handleSearchSubmit} className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar productos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          <Search className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" />
          <button
            type="submit"
            className="absolute right-2 top-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Buscar
          </button>
        </div>
      </form>

      {/* Mobile Filter Toggle */}
      <div className="lg:hidden mb-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg text-gray-700 font-medium"
        >
          <span className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filtros {hasActiveFilters && '(activos)'}
          </span>
          <ChevronDown className={`h-5 w-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Filters Content */}
      <div className={`space-y-6 ${!isExpanded ? 'hidden lg:block' : ''}`}>
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Categoría
          </label>
          <select
            value={filters.categoria}
            onChange={(e) => handleFilterChange('categoria', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            {CATEGORIES.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
        </div>

        {/* Price Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rango de precio
          </label>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <input
                type="number"
                placeholder="Min"
                value={filters.precio_min}
                onChange={(e) => handleFilterChange('precio_min', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                min="0"
                step="0.01"
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="Max"
                value={filters.precio_max}
                onChange={(e) => handleFilterChange('precio_max', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>

        {/* Sort Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ordenar por
          </label>
          <select
            value={currentSortValue}
            onChange={(e) => handleSortChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            {SORT_OPTIONS.map((option, index) => (
              <option key={index} value={`${option.value}-${option.order}`}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            <X className="h-4 w-4 mr-2" />
            Limpiar filtros
          </button>
        )}

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Filtros activos:</h4>
            <div className="space-y-1">
              {filters.categoria && (
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>Categoría: {CATEGORIES.find(c => c.value === filters.categoria)?.label}</span>
                  <button
                    onClick={() => handleFilterChange('categoria', '')}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
              {filters.precio_min && (
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>Precio mín: ${parseFloat(filters.precio_min).toLocaleString()}</span>
                  <button
                    onClick={() => handleFilterChange('precio_min', '')}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
              {filters.precio_max && (
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>Precio máx: ${parseFloat(filters.precio_max).toLocaleString()}</span>
                  <button
                    onClick={() => handleFilterChange('precio_max', '')}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchFilters;