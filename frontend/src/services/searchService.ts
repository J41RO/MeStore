// ~/src/services/searchService.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Service for API Integration
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: searchService.ts
// Ruta: ~/src/services/searchService.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Servicio para integración con APIs de búsqueda del backend
//
// ---------------------------------------------------------------------------------------------

import axios, { AxiosResponse } from 'axios';
import {
  SearchParams,
  SearchResult,
  SearchSuggestion,
  SearchFacet,
  PaginationMeta,
  SearchError,
} from '../types/search.types';
import { Product } from '../types/api.types';

/**
 * Configuración base del servicio
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Cliente HTTP configurado
 */
const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor para agregar token de autenticación
 */
httpClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Interceptor para manejar respuestas de error
 */
httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const searchError: SearchError = {
      type: 'network',
      message: 'Error de conexión',
      code: error.code,
      details: error.response?.data,
    };

    if (error.response) {
      switch (error.response.status) {
        case 400:
          searchError.type = 'validation';
          searchError.message = 'Parámetros de búsqueda inválidos';
          break;
        case 500:
          searchError.type = 'server';
          searchError.message = 'Error interno del servidor';
          break;
        default:
          searchError.message = error.response.data?.message || 'Error desconocido';
      }
    }

    return Promise.reject(searchError);
  }
);

/**
 * Transformar parámetros de búsqueda para la API
 */
const transformSearchParams = (params: SearchParams) => {
  const apiParams: any = {
    q: params.query,
    page: params.page,
    limit: params.limit,
    sort: params.sort,
    search_type: params.type,
  };

  // Filtros
  if (params.filters.categories.length > 0) {
    apiParams.categories = params.filters.categories.join(',');
  }

  if (params.filters.vendors.length > 0) {
    apiParams.vendors = params.filters.vendors.join(',');
  }

  if (params.filters.priceRange.min > 0) {
    apiParams.min_price = params.filters.priceRange.min;
  }

  if (params.filters.priceRange.max < 999999) {
    apiParams.max_price = params.filters.priceRange.max;
  }

  if (params.filters.inStock) {
    apiParams.in_stock = true;
  }

  if (params.filters.minRating > 0) {
    apiParams.min_rating = params.filters.minRating;
  }

  if (params.filters.dateRange.from) {
    apiParams.date_from = params.filters.dateRange.from.toISOString();
  }

  if (params.filters.dateRange.to) {
    apiParams.date_to = params.filters.dateRange.to.toISOString();
  }

  if (params.filters.location) {
    apiParams.city = params.filters.location.city;
    apiParams.radius = params.filters.location.radius;
  }

  // Facetas
  if (params.facets) {
    apiParams.facets = params.facets.join(',');
  }

  if (params.highlight !== undefined) {
    apiParams.highlight = params.highlight;
  }

  return apiParams;
};

/**
 * Transformar respuesta de la API a nuestro formato
 */
const transformSearchResponse = (response: any): SearchResult => {
  const products: Product[] = response.products.map((item: any) => ({
    id: item.id,
    name: item.name,
    description: item.description,
    price: item.price,
    stock: item.stock,
    category: item.category,
    imageUrl: item.image_url,
    vendorId: item.vendor_id,
    vendorName: item.vendor_name,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    // Campos adicionales para búsqueda
    rating: item.rating || 0,
    reviewCount: item.review_count || 0,
    highlight: item.highlight,
  }));

  const facets: SearchFacet[] = (response.facets || []).map((facet: any) => ({
    key: facet.key,
    label: facet.label,
    count: facet.count,
    selected: facet.selected || false,
    type: facet.type,
    options: facet.options?.map((option: any) => ({
      value: option.value,
      label: option.label,
      count: option.count,
      selected: option.selected || false,
    })),
  }));

  const meta: PaginationMeta = {
    page: response.meta.page,
    limit: response.meta.limit,
    total: response.meta.total,
    totalPages: response.meta.total_pages,
    hasNext: response.meta.has_next,
    hasPrev: response.meta.has_prev,
  };

  return {
    products,
    facets,
    meta,
    searchTime: response.search_time || 0,
    totalFound: response.total_found || products.length,
    query: response.query || '',
    suggestions: response.suggestions || [],
    didYouMean: response.did_you_mean,
  };
};

/**
 * Servicio de búsqueda
 */
export class SearchService {
  /**
   * Búsqueda principal de productos
   */
  async search(params: SearchParams): Promise<SearchResult> {
    try {
      const apiParams = transformSearchParams(params);
      const response: AxiosResponse = await httpClient.get('/search/products', {
        params: apiParams,
      });

      return transformSearchResponse(response.data);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Obtener sugerencias de autocompletado
   */
  async getSuggestions(query: string): Promise<SearchSuggestion[]> {
    try {
      const response: AxiosResponse = await httpClient.get('/search/suggestions', {
        params: { q: query, limit: 10 },
      });

      return response.data.suggestions.map((item: any) => ({
        id: item.id,
        text: item.text,
        type: item.type,
        count: item.count,
        highlight: item.highlight,
        metadata: item.metadata,
      }));
    } catch (error) {
      console.warn('Error getting suggestions:', error);
      return [];
    }
  }

  /**
   * Obtener búsquedas populares
   */
  async getPopularSearches(limit: number = 10): Promise<SearchSuggestion[]> {
    try {
      const response: AxiosResponse = await httpClient.get('/search/popular', {
        params: { limit },
      });

      return response.data.popular.map((item: any) => ({
        id: item.id,
        text: item.text,
        type: 'query',
        count: item.count,
      }));
    } catch (error) {
      console.warn('Error getting popular searches:', error);
      return [];
    }
  }

  /**
   * Obtener categorías disponibles para filtros
   */
  async getCategories(): Promise<Array<{ id: string; name: string; count: number }>> {
    try {
      const response: AxiosResponse = await httpClient.get('/search/categories');
      return response.data.categories;
    } catch (error) {
      console.warn('Error getting categories:', error);
      return [];
    }
  }

  /**
   * Obtener vendors disponibles para filtros
   */
  async getVendors(): Promise<Array<{ id: string; name: string; count: number }>> {
    try {
      const response: AxiosResponse = await httpClient.get('/search/vendors');
      return response.data.vendors;
    } catch (error) {
      console.warn('Error getting vendors:', error);
      return [];
    }
  }

  /**
   * Obtener rangos de precios dinámicos
   */
  async getPriceRanges(): Promise<{ min: number; max: number; ranges: Array<{ min: number; max: number; count: number }> }> {
    try {
      const response: AxiosResponse = await httpClient.get('/search/price-ranges');
      return response.data;
    } catch (error) {
      console.warn('Error getting price ranges:', error);
      return {
        min: 0,
        max: 999999,
        ranges: [],
      };
    }
  }

  /**
   * Buscar productos específicos de un vendor
   */
  async searchVendorProducts(vendorId: string, params: Partial<SearchParams>): Promise<SearchResult> {
    try {
      const apiParams = {
        ...transformSearchParams(params as SearchParams),
        vendor_id: vendorId,
      };

      const response: AxiosResponse = await httpClient.get('/search/vendor-products', {
        params: apiParams,
      });

      return transformSearchResponse(response.data);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Búsqueda semántica (si está habilitada)
   */
  async semanticSearch(query: string, params: Partial<SearchParams>): Promise<SearchResult> {
    try {
      const searchParams: SearchParams = {
        query,
        filters: params.filters || {
          categories: [],
          priceRange: { min: 0, max: 999999 },
          vendors: [],
          inStock: false,
          minRating: 0,
          dateRange: { from: null, to: null },
          customFilters: {},
        },
        sort: params.sort || 'relevance',
        page: params.page || 1,
        limit: params.limit || 24,
        type: 'semantic',
        highlight: true,
      };

      return this.search(searchParams);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Guardar analytics de búsqueda (opcional)
   */
  async trackSearch(params: {
    query: string;
    resultCount: number;
    clickedResults: string[];
    userType: string;
  }): Promise<void> {
    try {
      await httpClient.post('/search/analytics', params);
    } catch (error) {
      // Analytics no críticos, no lanzar error
      console.warn('Error tracking search:', error);
    }
  }

  /**
   * Reportar búsqueda sin resultados
   */
  async reportNoResults(query: string, filters: any): Promise<void> {
    try {
      await httpClient.post('/search/no-results', {
        query,
        filters,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.warn('Error reporting no results:', error);
    }
  }
}

/**
 * Instancia singleton del servicio
 */
export const searchService = new SearchService();

/**
 * Utilidades adicionales
 */
export const searchUtils = {
  /**
   * Debounce function para búsquedas
   */
  debounce: <T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): ((...args: Parameters<T>) => void) => {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  },

  /**
   * Generar URL compartible para búsqueda
   */
  generateShareableUrl: (params: SearchParams): string => {
    const urlParams = new URLSearchParams();

    if (params.query) urlParams.set('q', params.query);
    if (params.filters.categories.length > 0) {
      urlParams.set('categories', params.filters.categories.join(','));
    }
    if (params.filters.vendors.length > 0) {
      urlParams.set('vendors', params.filters.vendors.join(','));
    }
    if (params.filters.priceRange.min > 0) {
      urlParams.set('min_price', params.filters.priceRange.min.toString());
    }
    if (params.filters.priceRange.max < 999999) {
      urlParams.set('max_price', params.filters.priceRange.max.toString());
    }
    if (params.sort !== 'relevance') urlParams.set('sort', params.sort);
    if (params.page > 1) urlParams.set('page', params.page.toString());

    return `/search?${urlParams.toString()}`;
  },

  /**
   * Parsear URL de búsqueda
   */
  parseSearchUrl: (searchParams: URLSearchParams): Partial<SearchParams> => {
    const params: Partial<SearchParams> = {
      query: searchParams.get('q') || '',
      sort: (searchParams.get('sort') as any) || 'relevance',
      page: parseInt(searchParams.get('page') || '1'),
      filters: {
        categories: searchParams.get('categories')?.split(',').filter(Boolean) || [],
        vendors: searchParams.get('vendors')?.split(',').filter(Boolean) || [],
        priceRange: {
          min: parseInt(searchParams.get('min_price') || '0'),
          max: parseInt(searchParams.get('max_price') || '999999'),
        },
        inStock: searchParams.get('in_stock') === 'true',
        minRating: parseInt(searchParams.get('min_rating') || '0'),
        dateRange: { from: null, to: null },
        customFilters: {},
      },
    };

    return params;
  },

  /**
   * Validar query de búsqueda
   */
  validateQuery: (query: string): { isValid: boolean; message?: string } => {
    if (!query || query.trim().length === 0) {
      return { isValid: false, message: 'La búsqueda no puede estar vacía' };
    }

    if (query.length < 2) {
      return { isValid: false, message: 'La búsqueda debe tener al menos 2 caracteres' };
    }

    if (query.length > 100) {
      return { isValid: false, message: 'La búsqueda no puede tener más de 100 caracteres' };
    }

    // Verificar caracteres especiales problemáticos
    const invalidChars = /[<>{}|\\\^`]/;
    if (invalidChars.test(query)) {
      return { isValid: false, message: 'La búsqueda contiene caracteres no permitidos' };
    }

    return { isValid: true };
  },

  /**
   * Highlight de términos en texto
   */
  highlightTerms: (text: string, terms: string[]): string => {
    if (!terms.length) return text;

    let highlightedText = text;
    terms.forEach((term) => {
      const regex = new RegExp(`(${term})`, 'gi');
      highlightedText = highlightedText.replace(
        regex,
        '<mark class="bg-yellow-200 px-1 rounded">$1</mark>'
      );
    });

    return highlightedText;
  },
};