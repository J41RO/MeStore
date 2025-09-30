// ~/src/hooks/useProductList.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Hook para gestión de productos con paginación y filtros
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useProductList.ts
// Ruta: ~/src/hooks/useProductList.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-15
// Última Actualización: 2025-08-15
// Versión: 1.0.0
// Propósito: Hook personalizado para manejar estado de productos, paginación y filtros
//            con integración completa a la API de productos
//
// Modificaciones:
// 2025-08-15 - Implementación inicial del hook con paginación y filtros
//
// ---------------------------------------------------------------------------------------------

/**
 * Hook useProductList
 *
 * Hook personalizado que maneja:
 * - Estado de productos con paginación
 * - Filtros de búsqueda y ordenamiento
 * - Gestión de estados de carga y errores
 * - Integración con API de productos
 */

import { useState, useEffect, useCallback } from 'react';
import { Product, ProductFilters, PaginatedResponse } from '../types/api.types';
import api from '../services/api';

interface UseProductListState {
  products: Product[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  filters: ProductFilters;
}

interface UseProductListReturn extends UseProductListState {
  applyFilters: (newFilters: ProductFilters) => void;
  changePage: (page: number) => void;
  resetFilters: () => void;
  refreshProducts: () => void;
}

const initialFilters: ProductFilters = {
  search: '',
  category: '',
  sortBy: 'name',
  sortOrder: 'asc',
};

const initialPagination = {
  page: 1,
  limit: 10,
  total: 0,
  totalPages: 0,
};

export const useProductList = (): UseProductListReturn => {
  const [state, setState] = useState<UseProductListState>({
    products: [],
    loading: false,
    error: null,
    pagination: initialPagination,
    filters: initialFilters,
  });

  const fetchProducts = useCallback(
    async (filters: ProductFilters, page: number) => {
      console.log('📥 useProductList.fetchProducts llamado');
      console.log('🔍 Filters:', filters);
      console.log('🔍 Page:', page);

      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const currentLimit = state.pagination?.limit || 10;
        console.log('📤 Llamando a api.products.getWithFilters...');
        console.log('📦 Params:', { ...filters, page, limit: currentLimit });

        const response = await api.products.getWithFilters({
          ...filters,
          page: page,
          limit: currentLimit
        });

        console.log('✅ Response recibida:', response);
        const data: PaginatedResponse<Product> = response.data;
        console.log('📊 Data parseada:', data);
        console.log('🔢 Productos encontrados:', data.data?.length || 0);

        setState(prev => ({
          ...prev,
          products: data.data,
          pagination: data.pagination,
          loading: false,
        }));

        console.log('✅ Estado actualizado con productos');
      } catch (error) {
        console.error('❌ Error en fetchProducts:', error);
        console.error('📍 Error details:', error instanceof Error ? error.message : error);

        setState(prev => ({
          ...prev,
          error:
            error instanceof Error
              ? error.message
              : 'Error al cargar productos',
          loading: false,
        }));
      }
    },
    [state.pagination?.limit]
  );

  const applyFilters = useCallback((newFilters: ProductFilters) => {
    setState(prev => ({
      ...prev,
      filters: newFilters,
      pagination: { ...(prev.pagination || initialPagination), page: 1 },
    }));
  }, []);

  const changePage = useCallback((page: number) => {
    setState(prev => ({
      ...prev,
      pagination: { ...(prev.pagination || initialPagination), page },
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setState(prev => ({
      ...prev,
      filters: initialFilters,
      pagination: { ...(prev.pagination || initialPagination), page: 1 },
    }));
  }, []);

  const refreshProducts = useCallback(() => {
    console.log('🔄 useProductList.refreshProducts llamado');
    console.log('🔍 Current filters:', state.filters);
    console.log('🔍 Current page:', state.pagination?.page || 1);
    console.log('📞 Llamando a fetchProducts...');
    fetchProducts(state.filters, state.pagination?.page || 1);
  }, [fetchProducts, state.filters, state.pagination?.page]);

  useEffect(() => {
    fetchProducts(state.filters, state.pagination?.page || 1);
  }, [fetchProducts, state.filters, state.pagination?.page]);

  return {
    ...state,
    applyFilters,
    changePage,
    resetFilters,
    refreshProducts,
  };
};
