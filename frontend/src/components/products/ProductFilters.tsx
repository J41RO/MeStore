// ~/src/components/products/ProductFilters.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente de filtros de productos
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductFilters.tsx
// Ruta: ~/src/components/products/ProductFilters.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-15
// Última Actualización: 2025-08-15
// Versión: 1.0.0
// Propósito: Componente de filtros para búsqueda y ordenamiento de productos
//
// Modificaciones:
// 2025-08-15 - Implementación inicial de filtros
//
// ---------------------------------------------------------------------------------------------

/**
 * Componente ProductFilters
 *
 * Barra de filtros que incluye:
 * - Barra de búsqueda por nombre
 * - Filtro dropdown por categoría
 * - Filtros de rango de precio (min/max)
 * - Selector de ordenamiento
 * - Botón para limpiar filtros
 */

import React, { useState, useEffect } from 'react';
import { ProductFilters as IProductFilters } from '../../types/api.types';
import { Category } from '../../types/category.types';
import api from '../../services/api';

interface ProductFiltersProps {
  filters: IProductFilters;
  onFiltersChange: (filters: IProductFilters) => void;
  onReset: () => void;
  loading?: boolean;
}

const SORT_OPTIONS = [
  { value: 'name', label: 'Nombre' },
  { value: 'price', label: 'Precio' },
  { value: 'salesCount', label: 'Ventas' },
  { value: 'rating', label: 'Rating' },
];

const ProductFilters: React.FC<ProductFiltersProps> = ({
  filters,
  onFiltersChange,
  onReset,
  loading = false,
}) => {
  const [localFilters, setLocalFilters] = useState<IProductFilters>(filters);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);

  // Fetch categories from backend
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setCategoriesLoading(true);
        setCategoriesError(null);
        const response = await api.products.getCategories();

        // Filter only active categories and sort by name
        // Extract categories from paginated response
        const activeCategories = (response.data.categories || [])
          .filter((cat: Category) => cat.is_active)
          .sort((a: Category, b: Category) => a.name.localeCompare(b.name));

        setCategories(activeCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setCategoriesError('Error al cargar categorías');
        // Set empty array as fallback
        setCategories([]);
      } finally {
        setCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key: keyof IProductFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleReset = () => {
    onReset();
  };

  const hasActiveFilters =
    filters.search ||
    filters.category ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.sortBy !== 'name' ||
    filters.sortOrder !== 'asc';

  return (
    <div className='bg-white shadow rounded-lg p-6 mb-6'>
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4'>
        {/* Búsqueda por nombre */}
        <div className='col-span-1 md:col-span-2'>
          <label
            htmlFor='search'
            className='block text-sm font-medium text-gray-700 mb-2'
          >
            Buscar productos
          </label>
          <div className='relative'>
            <input
              type='text'
              id='search'
              placeholder='Buscar por nombre...'
              value={localFilters.search || ''}
              onChange={e => handleFilterChange('search', e.target.value)}
              disabled={loading}
              className='w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
            />
            <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
              <svg
                className='h-5 w-5 text-gray-400'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Filtro por categoría */}
        <div>
          <label
            htmlFor='category'
            className='block text-sm font-medium text-gray-700 mb-2'
          >
            Categoría
          </label>
          <select
            id='category'
            value={localFilters.category || ''}
            onChange={e => handleFilterChange('category', e.target.value)}
            disabled={loading || categoriesLoading}
            className='w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
          >
            <option value=''>
              {categoriesLoading ? 'Cargando categorías...' : 'Todas las categorías'}
            </option>
            {categoriesError && (
              <option value='' disabled>
                Error al cargar categorías
              </option>
            )}
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
                {category.product_count ? ` (${category.product_count})` : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Ordenamiento */}
        <div>
          <label
            htmlFor='sortBy'
            className='block text-sm font-medium text-gray-700 mb-2'
          >
            Ordenar por
          </label>
          <div className='flex space-x-2'>
            <select
              id='sortBy'
              value={localFilters.sortBy || 'name'}
              onChange={e => handleFilterChange('sortBy', e.target.value)}
              disabled={loading}
              className='flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
            >
              {SORT_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={localFilters.sortOrder || 'asc'}
              onChange={e =>
                handleFilterChange(
                  'sortOrder',
                  e.target.value as 'asc' | 'desc'
                )
              }
              disabled={loading}
              className='px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
            >
              <option value='asc'>A-Z / Menor</option>
              <option value='desc'>Z-A / Mayor</option>
            </select>
          </div>
        </div>
      </div>

      {/* Filtros de precio */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
        <div>
          <label
            htmlFor='minPrice'
            className='block text-sm font-medium text-gray-700 mb-2'
          >
            Precio mínimo
          </label>
          <input
            type='number'
            id='minPrice'
            placeholder='0'
            min='0'
            value={localFilters.minPrice || ''}
            onChange={e =>
              handleFilterChange(
                'minPrice',
                e.target.value ? parseFloat(e.target.value) : undefined
              )
            }
            disabled={loading}
            className='w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
          />
        </div>

        <div>
          <label
            htmlFor='maxPrice'
            className='block text-sm font-medium text-gray-700 mb-2'
          >
            Precio máximo
          </label>
          <input
            type='number'
            id='maxPrice'
            placeholder='Sin límite'
            min='0'
            value={localFilters.maxPrice || ''}
            onChange={e =>
              handleFilterChange(
                'maxPrice',
                e.target.value ? parseFloat(e.target.value) : undefined
              )
            }
            disabled={loading}
            className='w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed'
          />
        </div>

        <div className='flex items-end'>
          <button
            onClick={handleReset}
            className='w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors'
          >
            {loading ? 'Cargando...' : 'Limpiar filtros'}
          </button>
        </div>
      </div>

      {/* Indicador de filtros activos */}
      {hasActiveFilters && (
        <div className='flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-md'>
          <div className='flex items-center space-x-2'>
            <svg
              className='h-5 w-5 text-blue-600'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.707A1 1 0 013 7V4z'
              />
            </svg>
            <span className='text-sm font-medium text-blue-800'>
              Filtros aplicados
            </span>
          </div>
          <button
            onClick={handleReset}
            disabled={loading}
            className='text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors'
          >
            Limpiar todos
          </button>
        </div>
      )}
    </div>
  );
};

export default ProductFilters;
