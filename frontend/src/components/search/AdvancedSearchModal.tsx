// ~/src/components/search/AdvancedSearchModal.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - AdvancedSearchModal Component for Power Users
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: AdvancedSearchModal.tsx
// Ruta: ~/src/components/search/AdvancedSearchModal.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Modal de búsqueda avanzada para usuarios avanzados
//
// ---------------------------------------------------------------------------------------------

import React, { memo, useState, useCallback, useEffect } from 'react';
import {
  X,
  Search,
  Settings,
  Save,
  Download,
  Upload,
  Trash2,
  Star,
  Calendar,
  DollarSign,
  Package,
  Building2,
  Filter,
  Zap,
  Brain,
  Clock,
  Tag,
  MapPin,
} from 'lucide-react';
import { useSearch, useSearchHistory, useSearchFilters } from '../../hooks/search';
import { AdvancedSearchModalProps, SearchParams, SearchFilters, SavedSearch } from '../../types/search.types';
import Modal from '../ui/Modal/Modal';

interface AdvancedSearchForm {
  query: string;
  searchType: 'simple' | 'advanced' | 'semantic';
  filters: SearchFilters;
  sort: string;
  saveSearch: boolean;
  searchName: string;
  searchTags: string[];
}

/**
 * Componente de campo de formulario
 */
const FormField: React.FC<{
  label: string;
  icon?: React.ReactNode;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}> = memo(({ label, icon, required, children, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
      {icon}
      <span>
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </span>
    </label>
    {children}
  </div>
));

FormField.displayName = 'FormField';

/**
 * Componente de campo de rango
 */
const RangeField: React.FC<{
  label: string;
  min: number;
  max: number;
  value: { min: number; max: number };
  onChange: (value: { min: number; max: number }) => void;
  step?: number;
  prefix?: string;
}> = memo(({ label, min, max, value, onChange, step = 1, prefix = '' }) => (
  <FormField label={label} icon={<DollarSign className="w-4 h-4" />}>
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="block text-xs text-gray-500 mb-1">Mínimo</label>
        <input
          type="number"
          value={value.min}
          onChange={(e) => onChange({ ...value, min: Number(e.target.value) })}
          min={min}
          max={max}
          step={step}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder={`${prefix}${min}`}
        />
      </div>
      <div>
        <label className="block text-xs text-gray-500 mb-1">Máximo</label>
        <input
          type="number"
          value={value.max}
          onChange={(e) => onChange({ ...value, max: Number(e.target.value) })}
          min={min}
          max={max}
          step={step}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder={`${prefix}${max}`}
        />
      </div>
    </div>
    <div className="text-center text-sm text-gray-600">
      {prefix}{value.min.toLocaleString()} - {prefix}{value.max.toLocaleString()}
    </div>
  </FormField>
));

RangeField.displayName = 'RangeField';

/**
 * Componente de selección múltiple
 */
const MultiSelect: React.FC<{
  options: Array<{ value: string; label: string; count?: number }>;
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder: string;
  maxHeight?: string;
}> = memo(({ options, selected, onChange, placeholder, maxHeight = 'max-h-32' }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleToggle = (value: string) => {
    const newSelected = selected.includes(value)
      ? selected.filter(item => item !== value)
      : [...selected, value];
    onChange(newSelected);
  };

  return (
    <div className="relative">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md cursor-pointer bg-white focus:ring-blue-500 focus:border-blue-500"
      >
        {selected.length === 0 ? (
          <span className="text-gray-500">{placeholder}</span>
        ) : (
          <span className="text-gray-900">
            {selected.length} seleccionado{selected.length > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {isOpen && (
        <div className={`absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 ${maxHeight} overflow-y-auto`}>
          {options.map((option) => (
            <label
              key={option.value}
              className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selected.includes(option.value)}
                onChange={() => handleToggle(option.value)}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="flex-1">{option.label}</span>
              {option.count && (
                <span className="text-xs text-gray-500">({option.count})</span>
              )}
            </label>
          ))}
        </div>
      )}
    </div>
  );
});

MultiSelect.displayName = 'MultiSelect';

/**
 * Componente principal del modal de búsqueda avanzada
 */
const AdvancedSearchModal: React.FC<AdvancedSearchModalProps> = memo(({
  isOpen,
  onClose,
  onSearch,
  initialFilters,
  className = '',
}) => {
  // Hooks
  const { query, filters: currentFilters, sort: currentSort, config } = useSearch();
  const { categories, vendors, priceRanges } = useSearchFilters();
  const {
    savedSearches,
    saveCurrentSearch,
    loadSavedSearch,
    deleteSavedSearch,
  } = useSearchHistory();

  // Estado del formulario
  const [form, setForm] = useState<AdvancedSearchForm>({
    query: query || '',
    searchType: 'advanced',
    filters: initialFilters || currentFilters,
    sort: currentSort,
    saveSearch: false,
    searchName: '',
    searchTags: [],
  });

  /**
   * Inicializar formulario cuando se abre el modal
   */
  useEffect(() => {
    if (isOpen) {
      setForm({
        query: query || '',
        searchType: 'advanced',
        filters: initialFilters || currentFilters,
        sort: currentSort,
        saveSearch: false,
        searchName: '',
        searchTags: [],
      });
    }
  }, [isOpen, query, currentFilters, currentSort, initialFilters]);

  /**
   * Actualizar campo del formulario
   */
  const updateForm = useCallback(<K extends keyof AdvancedSearchForm>(
    key: K,
    value: AdvancedSearchForm[K]
  ) => {
    setForm(prev => ({ ...prev, [key]: value }));
  }, []);

  /**
   * Actualizar filtro específico
   */
  const updateFilter = useCallback(<K extends keyof SearchFilters>(
    key: K,
    value: SearchFilters[K]
  ) => {
    setForm(prev => ({
      ...prev,
      filters: { ...prev.filters, [key]: value }
    }));
  }, []);

  /**
   * Ejecutar búsqueda
   */
  const handleSearch = useCallback(() => {
    const searchParams: SearchParams = {
      query: form.query,
      filters: form.filters,
      sort: form.sort as any,
      page: 1,
      limit: config.defaultLimit,
      type: form.searchType as any,
    };

    // Guardar búsqueda si está habilitado
    if (form.saveSearch && form.searchName.trim()) {
      saveCurrentSearch(form.searchName, form.searchTags);
    }

    onSearch(searchParams);
    onClose();
  }, [form, config.defaultLimit, saveCurrentSearch, onSearch, onClose]);

  /**
   * Cargar búsqueda guardada
   */
  const handleLoadSavedSearch = useCallback((savedSearch: SavedSearch) => {
    setForm({
      query: savedSearch.query,
      searchType: 'advanced',
      filters: savedSearch.filters as SearchFilters,
      sort: savedSearch.sort,
      saveSearch: false,
      searchName: savedSearch.name,
      searchTags: savedSearch.tags,
    });
  }, []);

  /**
   * Limpiar formulario
   */
  const handleClear = useCallback(() => {
    setForm({
      query: '',
      searchType: 'simple',
      filters: {
        categories: [],
        priceRange: { min: 0, max: 999999 },
        vendors: [],
        inStock: false,
        minRating: 0,
        dateRange: { from: null, to: null },
        customFilters: {},
      },
      sort: 'relevance',
      saveSearch: false,
      searchName: '',
      searchTags: [],
    });
  }, []);

  /**
   * Exportar configuración de búsqueda
   */
  const handleExport = useCallback(() => {
    const exportData = {
      query: form.query,
      filters: form.filters,
      sort: form.sort,
      searchType: form.searchType,
      timestamp: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `search-config-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [form]);

  /**
   * Importar configuración de búsqueda
   */
  const handleImport = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        setForm(prev => ({
          ...prev,
          query: data.query || '',
          filters: data.filters || prev.filters,
          sort: data.sort || 'relevance',
          searchType: data.searchType || 'advanced',
        }));
      } catch (error) {
        alert('Error al importar configuración');
      }
    };
    reader.readAsText(file);
  }, []);

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Búsqueda Avanzada"
      size="xl"
      className={className}
    >
      <div className="space-y-6 max-h-[80vh] overflow-y-auto">
        {/* Consulta principal */}
        <FormField
          label="Términos de búsqueda"
          icon={<Search className="w-4 h-4" />}
        >
          <input
            type="text"
            value={form.query}
            onChange={(e) => updateForm('query', e.target.value)}
            placeholder="Buscar productos, categorías, vendedores..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </FormField>

        {/* Tipo de búsqueda */}
        <FormField
          label="Tipo de búsqueda"
          icon={<Brain className="w-4 h-4" />}
        >
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'simple', label: 'Simple', icon: <Search className="w-4 h-4" /> },
              { value: 'advanced', label: 'Avanzada', icon: <Settings className="w-4 h-4" /> },
              { value: 'semantic', label: 'Semántica', icon: <Brain className="w-4 h-4" /> },
            ].map((type) => (
              <label
                key={type.value}
                className={`
                  flex items-center space-x-2 p-3 border rounded-md cursor-pointer transition-colors
                  ${form.searchType === type.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <input
                  type="radio"
                  name="searchType"
                  value={type.value}
                  checked={form.searchType === type.value}
                  onChange={(e) => updateForm('searchType', e.target.value as any)}
                  className="sr-only"
                />
                {type.icon}
                <span>{type.label}</span>
              </label>
            ))}
          </div>
        </FormField>

        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Categorías */}
          <FormField
            label="Categorías"
            icon={<Tag className="w-4 h-4" />}
          >
            <MultiSelect
              options={categories}
              selected={form.filters.categories}
              onChange={(selected) => updateFilter('categories', selected)}
              placeholder="Seleccionar categorías"
            />
          </FormField>

          {/* Vendedores */}
          <FormField
            label="Vendedores"
            icon={<Building2 className="w-4 h-4" />}
          >
            <MultiSelect
              options={vendors}
              selected={form.filters.vendors}
              onChange={(selected) => updateFilter('vendors', selected)}
              placeholder="Seleccionar vendedores"
            />
          </FormField>
        </div>

        {/* Rango de precios */}
        <RangeField
          label="Rango de precios"
          min={priceRanges.min}
          max={priceRanges.max}
          value={form.filters.priceRange}
          onChange={(value) => updateFilter('priceRange', value)}
          prefix="$"
        />

        {/* Filtros adicionales */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Calificación mínima */}
          <FormField
            label="Calificación mínima"
            icon={<Star className="w-4 h-4" />}
          >
            <select
              value={form.filters.minRating}
              onChange={(e) => updateFilter('minRating', Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={0}>Cualquier calificación</option>
              <option value={1}>1+ estrellas</option>
              <option value={2}>2+ estrellas</option>
              <option value={3}>3+ estrellas</option>
              <option value={4}>4+ estrellas</option>
              <option value={5}>5 estrellas</option>
            </select>
          </FormField>

          {/* Disponibilidad */}
          <FormField
            label="Disponibilidad"
            icon={<Package className="w-4 h-4" />}
          >
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={form.filters.inStock}
                onChange={(e) => updateFilter('inStock', e.target.checked)}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span>Solo productos en stock</span>
            </label>
          </FormField>
        </div>

        {/* Ordenamiento */}
        <FormField
          label="Ordenar por"
          icon={<Filter className="w-4 h-4" />}
        >
          <select
            value={form.sort}
            onChange={(e) => updateForm('sort', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="relevance">Relevancia</option>
            <option value="price_asc">Precio: Menor a Mayor</option>
            <option value="price_desc">Precio: Mayor a Menor</option>
            <option value="newest">Más Recientes</option>
            <option value="rating">Mejor Calificados</option>
            <option value="popularity">Más Populares</option>
            <option value="name_asc">Nombre A-Z</option>
            <option value="name_desc">Nombre Z-A</option>
          </select>
        </FormField>

        {/* Guardar búsqueda */}
        <FormField
          label="Guardar búsqueda"
          icon={<Save className="w-4 h-4" />}
        >
          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={form.saveSearch}
                onChange={(e) => updateForm('saveSearch', e.target.checked)}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span>Guardar esta búsqueda para usar después</span>
            </label>

            {form.saveSearch && (
              <div className="space-y-3 pl-6">
                <input
                  type="text"
                  value={form.searchName}
                  onChange={(e) => updateForm('searchName', e.target.value)}
                  placeholder="Nombre de la búsqueda"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <input
                  type="text"
                  value={form.searchTags.join(', ')}
                  onChange={(e) => updateForm('searchTags', e.target.value.split(',').map(tag => tag.trim()).filter(Boolean))}
                  placeholder="Tags (separados por comas)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}
          </div>
        </FormField>

        {/* Búsquedas guardadas */}
        {savedSearches.length > 0 && (
          <FormField
            label="Búsquedas guardadas"
            icon={<Clock className="w-4 h-4" />}
          >
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {savedSearches.map((savedSearch) => (
                <div
                  key={savedSearch.id}
                  className="flex items-center justify-between p-2 border border-gray-200 rounded hover:bg-gray-50"
                >
                  <div
                    onClick={() => handleLoadSavedSearch(savedSearch)}
                    className="flex-1 cursor-pointer"
                  >
                    <div className="font-medium text-sm">{savedSearch.name}</div>
                    <div className="text-xs text-gray-500">
                      {savedSearch.query} • {savedSearch.tags.join(', ')}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteSavedSearch(savedSearch.id)}
                    className="p-1 text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </FormField>
        )}
      </div>

      {/* Acciones del modal */}
      <div className="flex items-center justify-between pt-6 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          {/* Exportar/Importar */}
          <button
            onClick={handleExport}
            className="inline-flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            <Download className="w-4 h-4 mr-1" />
            Exportar
          </button>

          <label className="inline-flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800 cursor-pointer">
            <Upload className="w-4 h-4 mr-1" />
            Importar
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="sr-only"
            />
          </label>

          <button
            onClick={handleClear}
            className="inline-flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            <Trash2 className="w-4 h-4 mr-1" />
            Limpiar
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancelar
          </button>
          <button
            onClick={handleSearch}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Search className="w-4 h-4 mr-2" />
            Buscar
          </button>
        </div>
      </div>
    </Modal>
  );
});

AdvancedSearchModal.displayName = 'AdvancedSearchModal';

export default AdvancedSearchModal;