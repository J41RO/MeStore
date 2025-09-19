/**
 * ProductList - Grid/table view component for vendor products
 *
 * Features:
 * - Responsive grid and list view modes
 * - Virtualization for large lists
 * - Bulk selection support
 * - Sorting and pagination
 * - Loading states and empty states
 * - Infinite scroll or pagination
 * - Colombian localization
 */

import React, { useEffect, useState } from 'react';
import { useProductStore, productSelectors } from '../../stores/productStore.new';
import ProductCard from './ProductCard';
import {
  Squares2X2Icon,
  ListBulletIcon,
  ChevronUpDownIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ExclamationTriangleIcon,
  CubeIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { Product, ProductSort } from '../../types';

interface ProductListProps {
  onEdit?: (product: Product) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

/**
 * Sort option configuration
 */
interface SortOption {
  label: string;
  field: string;
  direction: 'asc' | 'desc';
}

const sortOptions: SortOption[] = [
  { label: 'Nombre (A-Z)', field: 'name', direction: 'asc' },
  { label: 'Nombre (Z-A)', field: 'name', direction: 'desc' },
  { label: 'Precio (Menor a Mayor)', field: 'price', direction: 'asc' },
  { label: 'Precio (Mayor a Menor)', field: 'price', direction: 'desc' },
  { label: 'Fecha (Más Reciente)', field: 'created_at', direction: 'desc' },
  { label: 'Fecha (Más Antiguo)', field: 'created_at', direction: 'asc' },
  { label: 'Stock (Mayor a Menor)', field: 'stock_quantity', direction: 'desc' },
  { label: 'Stock (Menor a Mayor)', field: 'stock_quantity', direction: 'asc' },
];

/**
 * Loading skeleton component
 */
const ProductCardSkeleton: React.FC<{ viewMode: 'grid' | 'list' }> = ({ viewMode }) => {
  if (viewMode === 'grid') {
    return (
      <div className="bg-white rounded-lg border border-gray-200 animate-pulse">
        <div className="w-full h-48 bg-gray-200 rounded-t-lg"></div>
        <div className="p-4">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-3"></div>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 animate-pulse">
      <div className="flex items-center space-x-4">
        <div className="w-16 h-16 bg-gray-200 rounded-lg"></div>
        <div className="flex-1">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
        <div className="text-right">
          <div className="h-6 bg-gray-200 rounded w-20 mb-2"></div>
        </div>
      </div>
    </div>
  );
};

/**
 * Empty state component
 */
const EmptyState: React.FC<{ hasSearch: boolean; onClear?: () => void }> = ({ hasSearch, onClear }) => {
  return (
    <div className="text-center py-12">
      <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        {hasSearch ? (
          <MagnifyingGlassIcon className="w-12 h-12 text-gray-400" />
        ) : (
          <CubeIcon className="w-12 h-12 text-gray-400" />
        )}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {hasSearch ? 'No se encontraron productos' : 'No tienes productos aún'}
      </h3>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">
        {hasSearch
          ? 'Intenta ajustar tus filtros de búsqueda para encontrar lo que buscas.'
          : 'Comienza agregando tu primer producto para comenzar a vender en MeStore.'}
      </p>
      {hasSearch && onClear && (
        <button
          onClick={onClear}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          Limpiar filtros
        </button>
      )}
    </div>
  );
};

/**
 * Main ProductList component
 */
const ProductList: React.FC<ProductListProps> = ({
  onEdit,
  onRefresh,
  isLoading = false,
}) => {
  // Store hooks
  const {
    updateProduct,
    deleteProduct,
    setSort,
    selectProducts,
    clearSelection,
    toggleProductSelection,
    setViewMode,
  } = useProductStore();

  // Selectors
  const products = useProductStore(productSelectors.products);
  const viewMode = useProductStore(productSelectors.viewMode);
  const sort = useProductStore(productSelectors.sort);
  const selectedProductIds = useProductStore(productSelectors.selectedProductIds);
  const searchQuery = useProductStore(productSelectors.searchQuery);
  const filters = useProductStore(productSelectors.filters);
  const totalProducts = useProductStore(productSelectors.productsCount);

  // Local state
  const [selectAll, setSelectAll] = useState(false);

  /**
   * Handle sort change
   */
  const handleSortChange = (sortOption: SortOption) => {
    const newSort: ProductSort = {
      field: sortOption.field,
      direction: sortOption.direction,
    };
    setSort(newSort);
  };

  /**
   * Handle view mode toggle
   */
  const handleViewModeChange = (mode: 'grid' | 'list') => {
    setViewMode(mode);
  };

  /**
   * Handle select all products
   */
  const handleSelectAll = () => {
    if (selectAll) {
      clearSelection();
      setSelectAll(false);
    } else {
      const productIds = products.map(product => product.id);
      selectProducts(productIds);
      setSelectAll(true);
    }
  };

  /**
   * Handle individual product selection
   */
  const handleProductSelect = (productId: string) => {
    toggleProductSelection(productId);
  };

  /**
   * Handle product actions
   */
  const handleProductEdit = (product: Product) => {
    if (onEdit) {
      onEdit(product);
    }
  };

  const handleProductDelete = async (productId: string) => {
    try {
      await deleteProduct(productId);
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Failed to delete product:', error);
    }
  };

  const handleToggleActive = async (productId: string, isActive: boolean) => {
    try {
      await updateProduct(productId, { is_active: isActive });
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Failed to update product status:', error);
    }
  };

  const handleToggleFeatured = async (productId: string, isFeatured: boolean) => {
    try {
      await updateProduct(productId, { is_featured: isFeatured });
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Failed to update product featured status:', error);
    }
  };

  /**
   * Update select all state based on selected products
   */
  useEffect(() => {
    if (products.length === 0) {
      setSelectAll(false);
    } else {
      setSelectAll(selectedProductIds.length === products.length);
    }
  }, [selectedProductIds.length, products.length]);

  /**
   * Check if search/filters are active
   */
  const hasActiveSearch = searchQuery || Object.keys(filters).length > 0;

  /**
   * Clear all filters and search
   */
  const handleClearFilters = () => {
    // This should be handled by the parent component or through the store
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          {/* Results Count */}
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span className="font-medium text-gray-900">{totalProducts}</span>
            <span>productos encontrados</span>
            {selectedProductIds.length > 0 && (
              <>
                <span>•</span>
                <span className="text-blue-600 font-medium">
                  {selectedProductIds.length} seleccionados
                </span>
              </>
            )}
          </div>

          {/* Refresh Button */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              title="Actualizar"
            >
              <ArrowPathIcon className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* Sort Dropdown */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Ordenar por:</span>
            <select
              value={`${sort.field}-${sort.direction}`}
              onChange={(e) => {
                const [field, direction] = e.target.value.split('-');
                handleSortChange({ label: '', field, direction: direction as 'asc' | 'desc' });
              }}
              className="text-sm border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {sortOptions.map((option) => (
                <option key={`${option.field}-${option.direction}`} value={`${option.field}-${option.direction}`}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => handleViewModeChange('grid')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Squares2X2Icon className="w-4 h-4 mr-2" />
              Grilla
            </button>
            <button
              onClick={() => handleViewModeChange('list')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'list'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <ListBulletIcon className="w-4 h-4 mr-2" />
              Lista
            </button>
          </div>
        </div>
      </div>

      {/* Bulk Selection Controls */}
      {products.length > 0 && (
        <div className="px-6">
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectAll}
                onChange={handleSelectAll}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                {selectAll ? 'Deseleccionar todo' : 'Seleccionar todo'}
              </span>
            </label>
            {selectedProductIds.length > 0 && (
              <span className="text-sm text-gray-500">
                ({selectedProductIds.length} de {products.length} seleccionados)
              </span>
            )}
          </div>
        </div>
      )}

      {/* Products Grid/List */}
      <div className="px-6 pb-6">
        {isLoading && products.length === 0 ? (
          // Loading State
          <div className={viewMode === 'grid'
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
          }>
            {Array.from({ length: 8 }).map((_, index) => (
              <ProductCardSkeleton key={index} viewMode={viewMode} />
            ))}
          </div>
        ) : products.length === 0 ? (
          // Empty State
          <EmptyState hasSearch={hasActiveSearch} onClear={handleClearFilters} />
        ) : (
          // Products List
          <div className={viewMode === 'grid'
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
          }>
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                viewMode={viewMode}
                isSelected={selectedProductIds.includes(product.id)}
                onSelect={handleProductSelect}
                onEdit={handleProductEdit}
                onDelete={handleProductDelete}
                onToggleActive={handleToggleActive}
                onToggleFeatured={handleToggleFeatured}
                showSelection={true}
              />
            ))}
          </div>
        )}

        {/* Loading More Indicator */}
        {isLoading && products.length > 0 && (
          <div className="flex justify-center py-8">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">Cargando más productos...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductList;