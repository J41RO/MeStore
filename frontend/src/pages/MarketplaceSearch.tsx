/**
 * MarketplaceSearch - Main Search Implementation for MeStore Marketplace
 *
 * This is the OFFICIAL search page implementation for the marketplace.
 *
 * Route: /marketplace/search
 * API: /api/v1/products
 *
 * Features:
 * - Text search with URL params (?q=)
 * - Category, price range, and sorting filters
 * - Pagination with "Load More" functionality
 * - Deep linking support (shareable URLs)
 * - Approved products only filter
 *
 * Decision History (2025-10-01):
 * - Consolidated from 2 implementations (MarketplaceSearch + SearchPage)
 * - Chose this implementation as it's in production, functional, and integrated
 * - SearchPage.tsx removed (was not connected to routes/navigation)
 * - Future enhancements can be added incrementally to this component
 *
 * Connected Components:
 * - MarketplaceNavbar (search submission)
 * - Mobile components (MobileHeader, BottomNavigation, MobileSidebar)
 *
 * @author React Specialist AI
 * @version 2.0.0
 * @date 2025-10-01
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import MarketplaceLayout from '../components/marketplace/MarketplaceLayout';
import SearchFilters from '../components/marketplace/SearchFilters';
import SearchResults from '../components/marketplace/SearchResults';

interface Product {
  id: number;
  name: string;
  description: string;
  precio_venta: number;
  categoria: string;
  sku: string;
  estado: string;
  vendor?: {
    business_name: string;
  };
  images?: Array<{
    id: number;
    image_url: string;
    is_primary: boolean;
  }>;
}

interface SearchFilters {
  search: string;
  categoria: string;
  precio_min: string;
  precio_max: string;
  sort_by: string;
  sort_order: string;
}

const MarketplaceSearch: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 12;

  const [filters, setFilters] = useState<SearchFilters>({
    search: searchParams.get('q') || '',
    categoria: searchParams.get('categoria') || '',
    precio_min: searchParams.get('precio_min') || '',
    precio_max: searchParams.get('precio_max') || '',
    sort_by: searchParams.get('sort_by') || 'created_at',
    sort_order: searchParams.get('sort_order') || 'desc'
  });

  const searchProducts = async (page: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      
      if (filters.search.trim()) params.append('search', filters.search.trim());
      if (filters.categoria) params.append('categoria', filters.categoria);
      if (filters.precio_min) params.append('precio_min', filters.precio_min);
      if (filters.precio_max) params.append('precio_max', filters.precio_max);
      
      params.append('sort_by', filters.sort_by);
      params.append('sort_order', filters.sort_order);
      params.append('skip', ((page - 1) * productsPerPage).toString());
      params.append('limit', productsPerPage.toString());
      params.append('estado', 'aprobado');

      const response = await fetch(`/api/v1/products?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Error al buscar productos');
      }

      const data = await response.json();
      
      if (page === 1) {
        setProducts(data.products || data);
      } else {
        setProducts(prev => [...prev, ...(data.products || data)]);
      }
      
      setTotalCount(data.total || (data.products ? data.products.length : data.length));
      setCurrentPage(page);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al buscar productos');
      if (page === 1) {
        setProducts([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFiltersChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
    
    // Update URL params
    const params = new URLSearchParams();
    if (newFilters.search.trim()) params.set('q', newFilters.search.trim());
    if (newFilters.categoria) params.set('categoria', newFilters.categoria);
    if (newFilters.precio_min) params.set('precio_min', newFilters.precio_min);
    if (newFilters.precio_max) params.set('precio_max', newFilters.precio_max);
    if (newFilters.sort_by !== 'created_at') params.set('sort_by', newFilters.sort_by);
    if (newFilters.sort_order !== 'desc') params.set('sort_order', newFilters.sort_order);
    
    setSearchParams(params);
    setCurrentPage(1);
  };

  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    searchProducts(nextPage);
  };

  const handleSearch = (searchTerm: string) => {
    const newFilters = { ...filters, search: searchTerm };
    handleFiltersChange(newFilters);
  };

  // Search on filters change
  useEffect(() => {
    searchProducts(1);
  }, [filters]);

  // Initial search from URL params
  useEffect(() => {
    const urlSearch = searchParams.get('q') || '';
    if (urlSearch && urlSearch !== filters.search) {
      setFilters(prev => ({ ...prev, search: urlSearch }));
    }
  }, []);

  const hasMoreProducts = products.length < totalCount;
  const searchQuery = filters.search || searchParams.get('q') || '';

  return (
    <MarketplaceLayout>
      <div className="container mx-auto px-4 py-6">
        {/* Search Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Resultados de búsqueda
          </h1>
          {searchQuery && (
            <p className="text-gray-600">
              Mostrando resultados para: <span className="font-semibold">"{searchQuery}"</span>
            </p>
          )}
          {totalCount > 0 && (
            <p className="text-sm text-gray-500 mt-1">
              {totalCount} producto{totalCount !== 1 ? 's' : ''} encontrado{totalCount !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          <div className="lg:w-1/4">
            <SearchFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onSearch={handleSearch}
            />
          </div>

          {/* Results Section */}
          <div className="lg:w-3/4">
            <SearchResults
              products={products}
              loading={loading}
              error={error}
              hasMore={hasMoreProducts}
              onLoadMore={handleLoadMore}
              searchQuery={searchQuery}
            />
          </div>
        </div>
      </div>
    </MarketplaceLayout>
  );
};

export default MarketplaceSearch;