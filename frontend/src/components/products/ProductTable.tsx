// ~/src/components/products/ProductTable.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente de tabla de productos con paginación y selección múltiple
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductTable.tsx
// Ruta: ~/src/components/products/ProductTable.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-15
// Última Actualización: 2025-08-17
// Versión: 1.1.0
// Propósito: Componente de tabla responsive para mostrar productos con paginación
//            y selección múltiple para bulk actions
//
// Modificaciones:
// 2025-08-15 - Implementación inicial de tabla con paginación
// 2025-08-17 - Agregada funcionalidad de selección múltiple y bulk actions
//
// ---------------------------------------------------------------------------------------------

/**
 * Componente ProductTable
 *
 * Tabla responsive que muestra:
 * - Lista de productos con columnas: Selección, Imagen, Nombre, Categoría, Precio, Stock, Acciones
 * - Paginación en la parte inferior
 * - Estados de carga y datos vacíos
 * - Selección múltiple con checkboxes
 * - Responsive design con Tailwind CSS
 */

import React from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { Product } from '../../types/api.types';

interface ProductTableProps {
  products: Product[];
  loading: boolean;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  onPageChange: (page: number) => void;
  onEdit?: (product: Product) => void;
  onDelete?: (productId: string) => void;
  selectedProducts?: string[];
  onSelectionChange?: (selectedIds: string[]) => void;
}

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const halfVisible = Math.floor(maxVisiblePages / 2);
      let start = Math.max(1, currentPage - halfVisible);
      let end = Math.min(totalPages, start + maxVisiblePages - 1);

      if (end - start + 1 < maxVisiblePages) {
        start = Math.max(1, end - maxVisiblePages + 1);
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }

    return pages;
  };

  return (
    <div className='flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6'>
      <div className='flex justify-between flex-1 sm:hidden'>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className='relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
        >
          Anterior
        </button>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className='relative inline-flex items-center px-4 py-2 ml-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
        >
          Siguiente
        </button>
      </div>

      <div className='hidden sm:flex sm:flex-1 sm:items-center sm:justify-between'>
        <div>
          <p className='text-sm text-gray-700'>
            Página <span className='font-medium'>{currentPage}</span> de{' '}
            <span className='font-medium'>{totalPages}</span>
          </p>
        </div>
        <div>
          <nav
            className='relative z-0 inline-flex -space-x-px rounded-md shadow-sm'
            aria-label='Pagination'
          >
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className='relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
            >
              ‹
            </button>

            {getPageNumbers().map(page => (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={`relative inline-flex items-center px-4 py-2 text-sm font-medium border ${
                  page === currentPage
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className='relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
            >
              ›
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
};

const ProductTable: React.FC<ProductTableProps> = ({
  products,
  loading,
  pagination,
  onPageChange,
  onEdit,
  onDelete,
  selectedProducts = [],
  onSelectionChange,
}) => {
  // Estado y lógica para manejo de selección múltiple  
  const productsList = products || [];
  
  const handleSelectAll = () => {
    if (selectedProducts.length === productsList.length) {
      onSelectionChange?.([]);
    } else {
      onSelectionChange?.(productsList.map(p => p.id));
    }
  };

  const handleSelectProduct = (productId: string) => {
    const newSelection = selectedProducts.includes(productId)
      ? selectedProducts.filter(id => id !== productId)
      : [...selectedProducts, productId];
    onSelectionChange?.(newSelection);
  };

  const isAllSelected =
    productsList.length > 0 && selectedProducts.length === productsList.length;
  const isIndeterminate =
    selectedProducts.length > 0 && selectedProducts.length < productsList.length;

  if (loading) {
    return (
      <div className='bg-white shadow rounded-lg'>
        <div className='px-4 py-8 text-center'>
          <div className='inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600'></div>
          <p className='mt-2 text-gray-600'>Cargando productos...</p>
        </div>
      </div>
    );
  }

  if (productsList.length === 0) {
    return (
      <div className='bg-white shadow rounded-lg'>
        <div className='px-4 py-8 text-center'>
          <div className='text-gray-400 text-6xl mb-4'>📦</div>
          <h3 className='text-lg font-medium text-gray-900 mb-2'>
            No hay productos
          </h3>
          <p className='text-gray-600'>
            No se encontraron productos que coincidan con los filtros aplicados.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className='bg-white shadow rounded-lg overflow-hidden'>
      <div className='overflow-x-auto'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              <th className='relative px-6 py-3'>
                <input
                  type='checkbox'
                  checked={isAllSelected}
                  ref={el => {
                    if (el) el.indeterminate = isIndeterminate;
                  }}
                  onChange={handleSelectAll}
                  className='h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
                />
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Producto
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Categoría
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Precio
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Stock
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {productsList.map(product => (
              <tr key={product.id} className='hover:bg-gray-50'>
                <td className='relative px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900'>
                  <input
                    type='checkbox'
                    checked={selectedProducts.includes(product.id)}
                    onChange={() => handleSelectProduct(product.id)}
                    className='h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
                  />
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='flex items-center'>
                    <div className='flex-shrink-0 h-12 w-12'>
                      {(() => {
                        // Priority order: main_image_url, first image from images array, legacy imageUrl
                        const imageUrl = product.main_image_url || 
                                        (product.images && product.images.length > 0 ? product.images[0]?.public_url : null) || 
                                        product.imageUrl;
                        
                        return imageUrl ? (
                          <img
                            className='h-12 w-12 rounded-lg object-cover border border-gray-200'
                            src={imageUrl}
                            alt={product.name}
                            onError={e => {
                              (e.target as HTMLImageElement).src =
                                'https://via.placeholder.com/48x48/e5e7eb/6b7280?text=📦';
                            }}
                          />
                        ) : (
                          <div className='h-12 w-12 rounded-lg bg-gray-200 flex items-center justify-center text-gray-400 border border-gray-300'>
                            <ImageIcon className="w-6 h-6" />
                          </div>
                        );
                      })()}
                    </div>
                    <div className='ml-4'>
                      <div className='text-sm font-medium text-gray-900'>
                        {product.name}
                        {product.images && product.images.length > 1 && (
                          <span className='ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800'>
                            {product.images.length} fotos
                          </span>
                        )}
                      </div>
                      <div className='text-sm text-gray-500 truncate max-w-xs'>
                        {product.description}
                      </div>
                    </div>
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <span className='inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800'>
                    {product.category}
                  </span>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                  ${product.price.toLocaleString()}
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      product.stock > 10
                        ? 'bg-green-100 text-green-800'
                        : product.stock > 0
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {product.stock > 0
                      ? `${product.stock} unidades`
                      : 'Sin stock'}
                  </span>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium'>
                  <div className='flex space-x-2'>
                    {onEdit && (
                      <button
                        onClick={() => onEdit(product)}
                        className='text-blue-600 hover:text-blue-900 transition-colors'
                      >
                        Editar
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => onDelete(product.id)}
                        className='text-red-600 hover:text-red-900 transition-colors'
                      >
                        Eliminar
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && (
        <Pagination
          currentPage={pagination.page}
          totalPages={pagination.totalPages}
          onPageChange={onPageChange}
        />
      )}
    </div>
  );
};

export default ProductTable;
