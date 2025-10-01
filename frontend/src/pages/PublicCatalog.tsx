// ~/src/pages/PublicCatalog.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Public Product Catalog Page
// Copyright (c) 2025 Jairo. All rights reserved.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// File Name: PublicCatalog.tsx
// Path: ~/src/pages/PublicCatalog.tsx
// Author: React Specialist AI
// Created: 2025-10-01
// Last Updated: 2025-10-01
// Version: 1.0.0
// Purpose: Public product catalog page with filters, search, and pagination
//
// Modifications:
// 2025-10-01 - Initial implementation of public catalog
//
// ---------------------------------------------------------------------------------------------

/**
 * PublicCatalog - Public product catalog page
 *
 * Features:
 * - Responsive product grid (3-4 columns desktop, 1-2 mobile)
 * - Advanced filters with search, category, price range
 * - Pagination with page size selector
 * - Loading states and error handling
 * - Empty states for no products
 * - Click to view product details
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import ProductCard from '../components/products/ProductCard';
import ProductFilters from '../components/products/ProductFilters';
import { productApiService } from '../services/productApiService';
import type { Product, ProductSearchRequest, ProductListResponse } from '../types';
import { Loader2, Package, AlertCircle, Grid3x3, List } from 'lucide-react';

// Default filters
const DEFAULT_FILTERS = {
  search: '',
  category: '',
  minPrice: undefined,
  maxPrice: undefined,
  sortBy: 'name' as const,
  sortOrder: 'asc' as const,
};

const PublicCatalog: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // State management
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Filters state
  const [filters, setFilters] = useState(DEFAULT_FILTERS);

  // Calculate pagination
  const totalPages = Math.ceil(totalCount / pageSize);

  /**
   * Fetch products from API
   */
  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Build request parameters
      const params: ProductSearchRequest = {
        query: filters.search || undefined,
        category_id: filters.category || undefined,
        min_price: filters.minPrice,
        max_price: filters.maxPrice,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
        page: currentPage,
        limit: pageSize,
        // in_stock: true, // Removed - show all APPROVED products regardless of stock
      };

      // Fetch products from API
      const response: ProductListResponse = await productApiService.getProducts(params);

      // Update state with response data
      setProducts(response.data || []);
      setTotalCount(response.pagination?.total || 0);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Error al cargar los productos. Por favor, intente nuevamente.');
    } finally {
      setLoading(false);
    }
  }, [filters, currentPage, pageSize]);

  /**
   * Effect: Fetch products when dependencies change
   */
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  /**
   * Effect: Update URL params when filters change
   */
  useEffect(() => {
    const params = new URLSearchParams();

    if (filters.search) params.set('search', filters.search);
    if (filters.category) params.set('category', filters.category);
    if (filters.minPrice) params.set('minPrice', filters.minPrice.toString());
    if (filters.maxPrice) params.set('maxPrice', filters.maxPrice.toString());
    if (filters.sortBy !== 'name') params.set('sortBy', filters.sortBy);
    if (filters.sortOrder !== 'asc') params.set('sortOrder', filters.sortOrder);
    if (currentPage > 1) params.set('page', currentPage.toString());

    setSearchParams(params, { replace: true });
  }, [filters, currentPage, setSearchParams]);

  /**
   * Effect: Initialize filters from URL params on mount
   */
  useEffect(() => {
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';
    const minPrice = searchParams.get('minPrice');
    const maxPrice = searchParams.get('maxPrice');
    const sortBy = (searchParams.get('sortBy') || 'name') as any;
    const sortOrder = (searchParams.get('sortOrder') || 'asc') as 'asc' | 'desc';
    const page = parseInt(searchParams.get('page') || '1', 10);

    setFilters({
      search,
      category,
      minPrice: minPrice ? parseFloat(minPrice) : undefined,
      maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
      sortBy,
      sortOrder,
    });
    setCurrentPage(page);
  }, []); // Only run on mount

  /**
   * Handle filter changes
   */
  const handleFiltersChange = (newFilters: typeof DEFAULT_FILTERS) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page on filter change
  };

  /**
   * Handle filter reset
   */
  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS);
    setCurrentPage(1);
  };

  /**
   * Handle product click - navigate to detail page
   */
  const handleProductClick = (product: Product) => {
    navigate(`/marketplace/product/${product.id}`);
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Handle page size change
   */
  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  /**
   * Render loading state
   */
  if (loading && products.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-gray-600 text-lg">Cargando productos...</p>
          </div>
        </div>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error && products.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col items-center justify-center py-20">
            <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Error al cargar productos</h3>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={fetchProducts}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">Catálogo de Productos</h1>
          <p className="mt-2 text-gray-600">
            Descubre todos nuestros productos disponibles
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <ProductFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onReset={handleResetFilters}
          loading={loading}
        />

        {/* Results header with view toggle */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div className="flex items-center gap-2">
            <p className="text-gray-700">
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Cargando...
                </span>
              ) : (
                <>
                  Mostrando <span className="font-semibold">{products.length}</span> de{' '}
                  <span className="font-semibold">{totalCount}</span> productos
                </>
              )}
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* View mode toggle */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-700 mr-1">Vista:</span>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title="Vista de cuadrícula"
                disabled={loading}
              >
                <Grid3x3 className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title="Vista de lista"
                disabled={loading}
              >
                <List className="h-5 w-5" />
              </button>
            </div>

            {/* Page size selector */}
            <div className="flex items-center gap-2">
              <label htmlFor="pageSize" className="text-sm text-gray-700">
                Productos por página:
              </label>
              <select
                id="pageSize"
                value={pageSize}
                onChange={(e) => handlePageSizeChange(parseInt(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="12">12</option>
                <option value="24">24</option>
                <option value="48">48</option>
              </select>
            </div>
          </div>
        </div>

        {/* Products grid or list */}
        {products.length > 0 ? (
          <>
            <div
              className={
                viewMode === 'grid'
                  ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8'
                  : 'flex flex-col gap-4 mb-8'
              }
            >
              {products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  viewMode={viewMode}
                  onProductClick={handleProductClick}
                  onViewDetails={handleProductClick}
                  showSKU={false}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8">
                {/* Page info */}
                <p className="text-sm text-gray-700">
                  Página <span className="font-semibold">{currentPage}</span> de{' '}
                  <span className="font-semibold">{totalPages}</span>
                </p>

                {/* Pagination buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1 || loading}
                    className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Primera
                  </button>
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1 || loading}
                    className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Anterior
                  </button>

                  {/* Page numbers */}
                  <div className="hidden sm:flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          disabled={loading}
                          className={`px-3 py-2 border rounded-md transition-colors ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'border-gray-300 hover:bg-gray-50'
                          } disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages || loading}
                    className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Siguiente
                  </button>
                  <button
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages || loading}
                    className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Última
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          /* Empty state */
          <div className="flex flex-col items-center justify-center py-20 bg-white rounded-lg shadow-sm">
            <Package className="w-20 h-20 text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No se encontraron productos
            </h3>
            <p className="text-gray-600 mb-6 text-center max-w-md">
              No hay productos que coincidan con tus criterios de búsqueda.
              Intenta ajustar los filtros o realizar una nueva búsqueda.
            </p>
            <button
              onClick={handleResetFilters}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicCatalog;
