import React, { useState } from 'react';
import { useProductList } from '../hooks/useProductList';
import ProductFilters from '../components/products/ProductFilters';
import ProductTable from '../components/products/ProductTable';
import AddProductModal from '../components/AddProductModal';
import EditProductModal from '../components/EditProductModal';
import { Product } from '../types/api.types';
import ProductCard from '../components/products/ProductCard';

const Productos: React.FC = () => {
  const {
    products,
    loading,
    error,
    pagination,
    filters,
    applyFilters,
    changePage,
    resetFilters,
    refreshProducts,
  } = useProductList();

  // Estados para modales
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  
  const handleEdit = (product: Product) => {
    console.log('Editar producto:', product);
    setSelectedProduct(product);
    setShowEditModal(true);
  };

  const handleDelete = (productId: string) => {
    console.log('Eliminar producto:', productId);
    // TODO: Implementar confirmación y eliminación
  };

  const handleAddProduct = () => {
    console.log('Agregar nuevo producto');
    setShowAddModal(true);
  };

  const handleProductCreated = () => {
    // Refrescar la lista cuando se crea un producto
    refreshProducts();
  };

  const handleProductUpdated = () => {
    // Refrescar la lista cuando se actualiza un producto
    refreshProducts();
    setShowEditModal(false);
    setSelectedProduct(null);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setSelectedProduct(null);
  };

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error al cargar productos</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-3">
        {/* Toggle de Vista */}
        <div className="flex items-center gap-2 mr-4">
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            title="Vista Lista"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 16a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
            </svg>
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            title="Vista Grid"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
        </div>

                <button
                  onClick={refreshProducts}
                  className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 transition-colors"
                >
                  Reintentar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestión de Productos</h1>
          <p className="text-gray-600 mt-1">
            Administra tu catálogo de productos
          </p>
        </div>
        <button
          onClick={handleAddProduct}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors font-medium"
        >
          Agregar Producto
        </button>
      </div>

      {/* Filtros */}
      <ProductFilters
        filters={filters}
        onFiltersChange={applyFilters}
        onReset={resetFilters}
        loading={loading}
      />
      ) : (
        <div className="space-y-4">
          {/* Grid de productos */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {loading ? (
              // Loading placeholders para grid
              Array.from({ length: 8 }).map((_, index) => (
                <div key={index} className="bg-gray-200 animate-pulse rounded-lg h-80" />
              ))
            ) : products.length > 0 ? (
              products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  viewMode="grid"
                  onProductClick={(product) => handleEdit(product)}
                  showSKU={true}
                />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-gray-500">No se encontraron productos</p>
              </div>
            )}
          </div>
          
          {/* Paginación para grid */}
          {pagination && pagination.totalPages > 1 && (
            <div className="flex justify-center items-center space-x-4 mt-6">
              <button
                onClick={() => changePage(pagination.page - 1)}
                disabled={pagination.page <= 1}
                className="px-4 py-2 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Anterior
              </button>
              <span className="text-sm text-gray-600">
                Página {pagination.page} de {pagination.totalPages}
              </span>
              <button
                onClick={() => changePage(pagination.page + 1)}
                disabled={pagination.page >= pagination.totalPages}
                className="px-4 py-2 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </div>
      )

      {/* Vista de productos */}
      {viewMode === 'list' ? (
        <ProductTable
        products={products}
        loading={loading}
        pagination={pagination}
        onPageChange={changePage}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      ) : (
        <div>Grid view placeholder</div>
      )}

      {/* Modal de agregar producto */}
      <AddProductModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onProductCreated={handleProductCreated}
      />

      {/* Modal de editar producto */}
      {showEditModal && selectedProduct && (
        <EditProductModal
          isOpen={showEditModal}
          onClose={handleCloseEditModal}
          product={selectedProduct}
          onProductUpdated={handleProductUpdated}
        />
      )}
    </div>
  );
};

export default Productos;