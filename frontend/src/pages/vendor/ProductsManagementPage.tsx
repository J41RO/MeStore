/**
 * ProductsManagementPage - Main container for vendor product management
 * Route: /vendor/products
 *
 * Comprehensive product management interface for Colombian vendors
 * Features: CRUD operations, bulk actions, analytics, responsive design
 */

import React, { useEffect, useState } from 'react';
import { useProductStore, productSelectors } from '../../stores/productStore.new';
import { useAuthStore } from '../../stores/authStore';
import ProductStats from '../../components/vendor/ProductStats';
import ProductFilters from '../../components/vendor/ProductFilters';
import ProductList from '../../components/vendor/ProductList';
import ProductForm from '../../components/vendor/ProductForm';
import BulkActions from '../../components/vendor/BulkActions';
import {
  PlusIcon,
  AdjustmentsHorizontalIcon,
  Squares2X2Icon,
  ListBulletIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { Product } from '../../types';

/**
 * Main Products Management Page Component
 * Handles the complete vendor product management workflow
 */
const ProductsManagementPage: React.FC = () => {
  // Store hooks
  const { user } = useAuthStore();
  const {
    fetchProducts,
    clearErrors,
    setViewMode,
    toggleFiltersPanel,
    reset
  } = useProductStore();

  // Selectors
  const products = useProductStore(productSelectors.products);
  const isLoading = useProductStore(productSelectors.isLoading);
  const error = useProductStore(productSelectors.error);
  const viewMode = useProductStore(productSelectors.viewMode);
  const showFiltersPanel = useProductStore(state => state.showFiltersPanel);
  const showBulkActions = useProductStore(productSelectors.showBulkActions);
  const selectedProductIds = useProductStore(productSelectors.selectedProductIds);
  const totalProducts = useProductStore(productSelectors.productsCount);

  // Local state
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  /**
   * Initialize component - fetch products on mount
   */
  useEffect(() => {
    const initializeProducts = async () => {
      try {
        await fetchProducts();
      } catch (error) {
        console.error('Failed to load products:', error);
      }
    };

    initializeProducts();

    // Cleanup on unmount
    return () => {
      clearErrors();
    };
  }, [fetchProducts, clearErrors]);

  /**
   * Handle creating a new product
   */
  const handleCreateProduct = () => {
    setEditingProduct(null);
    setShowProductForm(true);
  };

  /**
   * Handle editing an existing product
   */
  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setShowProductForm(true);
  };

  /**
   * Handle closing the product form
   */
  const handleCloseForm = () => {
    setShowProductForm(false);
    setEditingProduct(null);
  };

  /**
   * Handle form submission success
   */
  const handleFormSuccess = () => {
    setShowProductForm(false);
    setEditingProduct(null);
    // Refresh products list
    fetchProducts();
  };

  /**
   * Toggle view mode between grid and list
   */
  const handleViewModeToggle = (mode: 'grid' | 'list') => {
    setViewMode(mode);
  };

  /**
   * Handle mobile filters toggle
   */
  const handleMobileFiltersToggle = () => {
    setShowMobileFilters(!showMobileFilters);
  };

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Error al cargar productos
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => {
                clearErrors();
                fetchProducts();
              }}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
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
      {/* Header Section */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            {/* Title and Stats */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">
                Gestión de Productos
              </h1>
              <p className="mt-2 text-gray-600">
                Administra tu catálogo de productos para {user?.business_name || 'tu negocio'}
              </p>

              {/* Quick Stats */}
              <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <span className="font-medium text-gray-900">{totalProducts}</span>
                  <span className="ml-1">productos totales</span>
                </span>
                {selectedProductIds.length > 0 && (
                  <span className="flex items-center text-blue-600">
                    <span className="font-medium">{selectedProductIds.length}</span>
                    <span className="ml-1">seleccionados</span>
                  </span>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 sm:mt-0 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
              {/* Mobile Filters Button */}
              <button
                onClick={handleMobileFiltersToggle}
                className="sm:hidden flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                aria-label="Filtros"
              >
                <FunnelIcon className="w-5 h-5 mr-2" />
                Filtros
              </button>

              {/* View Mode Toggles - Desktop */}
              <div className="hidden sm:flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => handleViewModeToggle('grid')}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  aria-label="Vista de grilla"
                >
                  <Squares2X2Icon className="w-4 h-4 mr-2" />
                  Grilla
                </button>
                <button
                  onClick={() => handleViewModeToggle('list')}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  aria-label="Vista de lista"
                >
                  <ListBulletIcon className="w-4 h-4 mr-2" />
                  Lista
                </button>
              </div>

              {/* Filters Toggle - Desktop */}
              <button
                onClick={toggleFiltersPanel}
                className={`hidden sm:flex items-center px-4 py-2 border rounded-lg text-sm font-medium transition-colors ${
                  showFiltersPanel
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                aria-label="Panel de filtros"
              >
                <AdjustmentsHorizontalIcon className="w-5 h-5 mr-2" />
                Filtros
              </button>

              {/* Add Product Button */}
              <button
                onClick={handleCreateProduct}
                className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                aria-label="Agregar producto"
              >
                <PlusIcon className="w-5 h-5 mr-2" />
                Agregar Producto
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <ProductStats />
      </div>

      {/* Bulk Actions Bar */}
      {showBulkActions && (
        <div className="bg-blue-50 border-b border-blue-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <BulkActions onRefresh={() => fetchProducts()} />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Panel - Desktop */}
          {showFiltersPanel && (
            <div className="hidden lg:block w-80 flex-shrink-0">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <ProductFilters />
              </div>
            </div>
          )}

          {/* Mobile Filters Modal */}
          {showMobileFilters && (
            <div className="lg:hidden fixed inset-0 z-50 overflow-y-auto">
              <div className="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
                <div
                  className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                  onClick={handleMobileFiltersToggle}
                />
                <div className="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-lg sm:w-full sm:p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Filtros</h3>
                    <button
                      onClick={handleMobileFiltersToggle}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <span className="sr-only">Cerrar</span>
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <ProductFilters onApply={handleMobileFiltersToggle} />
                </div>
              </div>
            </div>
          )}

          {/* Products List */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <ProductList
                onEdit={handleEditProduct}
                onRefresh={() => fetchProducts()}
                isLoading={isLoading}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Product Form Modal */}
      {showProductForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
            <div
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={handleCloseForm}
            />
            <div className="relative bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-4xl sm:w-full">
              <ProductForm
                product={editingProduct}
                onSubmit={handleFormSuccess}
                onCancel={handleCloseForm}
              />
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && !products.length && (
        <div className="fixed inset-0 z-40 bg-white bg-opacity-75 flex items-center justify-center">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="text-gray-600 font-medium">Cargando productos...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsManagementPage;