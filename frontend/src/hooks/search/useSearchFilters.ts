// ~/src/hooks/search/useSearchFilters.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Filters Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useSearchFilters.ts
// Ruta: ~/src/hooks/search/useSearchFilters.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Hook especializado para gestión de filtros de búsqueda
//
// ---------------------------------------------------------------------------------------------

import { useCallback, useMemo, useEffect, useState } from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { searchService } from '../../services/searchService';
import { SearchFilters, SearchFacet } from '../../types/search.types';

interface FilterOption {
  value: string;
  label: string;
  count: number;
}

interface UseSearchFiltersReturn {
  // Estado de filtros
  filters: SearchFilters;
  activeFiltersCount: number;

  // Opciones disponibles
  categories: FilterOption[];
  vendors: FilterOption[];
  priceRanges: { min: number; max: number; ranges: Array<{ min: number; max: number; count: number }> };

  // Estados de carga
  loadingCategories: boolean;
  loadingVendors: boolean;
  loadingPriceRanges: boolean;

  // Métodos
  setFilter: <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => void;
  toggleFilter: (key: keyof SearchFilters, value: any) => void;
  clearFilter: (key: keyof SearchFilters) => void;
  clearAllFilters: () => void;
  applyFilters: () => void;

  // Validaciones
  isFilterActive: (key: keyof SearchFilters, value?: any) => boolean;
  getFilterCount: (key: keyof SearchFilters) => number;

  // Utilidades
  exportFilters: () => string;
  importFilters: (filtersJson: string) => void;
}

/**
 * Hook para gestión avanzada de filtros de búsqueda
 */
export const useSearchFilters = (): UseSearchFiltersReturn => {
  const store = useSearchStore();
  const [categories, setCategories] = useState<FilterOption[]>([]);
  const [vendors, setVendors] = useState<FilterOption[]>([]);
  const [priceRanges, setPriceRanges] = useState<{
    min: number;
    max: number;
    ranges: Array<{ min: number; max: number; count: number }>
  }>({ min: 0, max: 999999, ranges: [] });

  const [loadingCategories, setLoadingCategories] = useState(false);
  const [loadingVendors, setLoadingVendors] = useState(false);
  const [loadingPriceRanges, setLoadingPriceRanges] = useState(false);

  /**
   * Cargar categorías disponibles
   */
  const loadCategories = useCallback(async () => {
    if (categories.length > 0) return; // Ya cargadas

    setLoadingCategories(true);
    try {
      const categoriesData = await searchService.getCategories();
      setCategories(categoriesData.map(cat => ({
        value: cat.id,
        label: cat.name,
        count: cat.count
      })));
    } catch (error) {
      console.warn('Error loading categories:', error);
    } finally {
      setLoadingCategories(false);
    }
  }, [categories.length]);

  /**
   * Cargar vendors disponibles
   */
  const loadVendors = useCallback(async () => {
    if (vendors.length > 0) return; // Ya cargados

    setLoadingVendors(true);
    try {
      const vendorsData = await searchService.getVendors();
      setVendors(vendorsData.map(vendor => ({
        value: vendor.id,
        label: vendor.name,
        count: vendor.count
      })));
    } catch (error) {
      console.warn('Error loading vendors:', error);
    } finally {
      setLoadingVendors(false);
    }
  }, [vendors.length]);

  /**
   * Cargar rangos de precios
   */
  const loadPriceRanges = useCallback(async () => {
    setLoadingPriceRanges(true);
    try {
      const priceData = await searchService.getPriceRanges();
      setPriceRanges(priceData);
    } catch (error) {
      console.warn('Error loading price ranges:', error);
    } finally {
      setLoadingPriceRanges(false);
    }
  }, []);

  /**
   * Cargar datos iniciales
   */
  useEffect(() => {
    loadCategories();
    loadVendors();
    loadPriceRanges();
  }, [loadCategories, loadVendors, loadPriceRanges]);

  /**
   * Establecer un filtro específico
   */
  const setFilter = useCallback(<K extends keyof SearchFilters>(
    key: K,
    value: SearchFilters[K]
  ) => {
    store.setFilters({ [key]: value });
  }, [store]);

  /**
   * Toggle de filtro (agregar/remover valor)
   */
  const toggleFilter = useCallback((key: keyof SearchFilters, value: any) => {
    store.toggleFilter(key, value);
  }, [store]);

  /**
   * Limpiar un filtro específico
   */
  const clearFilter = useCallback((key: keyof SearchFilters) => {
    const defaultValues: Partial<SearchFilters> = {
      categories: [],
      vendors: [],
      priceRange: { min: 0, max: 999999 },
      inStock: false,
      minRating: 0,
      dateRange: { from: null, to: null },
      customFilters: {},
    };

    if (key in defaultValues) {
      store.setFilters({ [key]: defaultValues[key] });
    }
  }, [store]);

  /**
   * Limpiar todos los filtros
   */
  const clearAllFilters = useCallback(() => {
    store.clearFilters();
  }, [store]);

  /**
   * Aplicar filtros (buscar con filtros actuales)
   */
  const applyFilters = useCallback(() => {
    store.search({});
  }, [store]);

  /**
   * Verificar si un filtro está activo
   */
  const isFilterActive = useCallback((
    key: keyof SearchFilters,
    value?: any
  ): boolean => {
    const filterValue = store.filters[key];

    if (value !== undefined) {
      if (Array.isArray(filterValue)) {
        return filterValue.includes(value);
      }
      return filterValue === value;
    }

    // Verificar si el filtro tiene algún valor activo
    if (Array.isArray(filterValue)) {
      return filterValue.length > 0;
    }

    if (typeof filterValue === 'boolean') {
      return filterValue;
    }

    if (key === 'priceRange') {
      const range = filterValue as SearchFilters['priceRange'];
      return range.min > 0 || range.max < 999999;
    }

    if (key === 'dateRange') {
      const range = filterValue as SearchFilters['dateRange'];
      return range.from !== null || range.to !== null;
    }

    if (key === 'minRating') {
      return (filterValue as number) > 0;
    }

    return filterValue !== null && filterValue !== undefined;
  }, [store.filters]);

  /**
   * Obtener contador de elementos activos en un filtro
   */
  const getFilterCount = useCallback((key: keyof SearchFilters): number => {
    const filterValue = store.filters[key];

    if (Array.isArray(filterValue)) {
      return filterValue.length;
    }

    return isFilterActive(key) ? 1 : 0;
  }, [store.filters, isFilterActive]);

  /**
   * Exportar filtros como JSON
   */
  const exportFilters = useCallback((): string => {
    return JSON.stringify(store.filters, null, 2);
  }, [store.filters]);

  /**
   * Importar filtros desde JSON
   */
  const importFilters = useCallback((filtersJson: string) => {
    try {
      const parsedFilters = JSON.parse(filtersJson);
      store.setFilters(parsedFilters);
    } catch (error) {
      console.error('Error importing filters:', error);
    }
  }, [store]);

  /**
   * Contador total de filtros activos
   */
  const activeFiltersCount = useMemo(() => {
    let count = 0;

    if (store.filters.categories.length > 0) count++;
    if (store.filters.vendors.length > 0) count++;
    if (store.filters.inStock) count++;
    if (store.filters.minRating > 0) count++;
    if (store.filters.priceRange.min > 0 || store.filters.priceRange.max < 999999) count++;
    if (store.filters.dateRange.from || store.filters.dateRange.to) count++;

    return count;
  }, [store.filters]);

  return {
    // Estado
    filters: store.filters,
    activeFiltersCount,

    // Opciones disponibles
    categories,
    vendors,
    priceRanges,

    // Estados de carga
    loadingCategories,
    loadingVendors,
    loadingPriceRanges,

    // Métodos
    setFilter,
    toggleFilter,
    clearFilter,
    clearAllFilters,
    applyFilters,

    // Validaciones
    isFilterActive,
    getFilterCount,

    // Utilidades
    exportFilters,
    importFilters,
  };
};