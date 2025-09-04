// ~/MeStore/frontend/src/components/ProductDetailModal.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ProductDetailModal Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductDetailModal.tsx
// Ruta: ~/MeStore/frontend/src/components/ProductDetailModal.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-17
// Última Actualización: 2025-08-17
// Versión: 1.1.0
// Propósito: Modal para mostrar detalles completos de un producto
//
// Modificaciones:
// 2025-08-17 - Creación inicial del modal de detalles
// 2025-08-17 - Reparación de estructura JSX corrupta
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { X, Eye, Edit } from 'lucide-react';
import { Product } from '../types/api.types';

interface ProductDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product;
  onEdit?: () => void;
}

const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  isOpen,
  onClose,
  product,
  onEdit,
}) => {
  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'>
      <div className='bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
        <div className='flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700'>
          <div className='flex items-center space-x-3'>
            <Eye className='w-6 h-6 text-blue-600' />
            <h2 className='text-xl font-semibold text-gray-900 dark:text-white'>
              Detalles del Producto
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label='Cerrar modal'
            className='text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors'
          >
            <X className='w-6 h-6' />
          </button>
        </div>

        <div className='p-6'>
          {/* Layout de información detallada */}
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            {/* Imagen del producto */}
            <div className='aspect-square bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden'>
              {product.imageUrl ? (
                <img
                  src={product.imageUrl}
                  alt={product.name}
                  className='w-full h-full object-cover'
                />
              ) : (
                <div className='text-gray-400 text-6xl'>📦</div>
              )}
            </div>

            {/* Información principal */}
            <div className='space-y-4'>
              <div>
                <h3 className='text-2xl font-bold text-gray-900 dark:text-white mb-2'>
                  {product.name}
                </h3>
                <p className='text-gray-600 dark:text-gray-300 leading-relaxed'>
                  {product.description}
                </p>
              </div>

              <div className='flex items-center space-x-2'>
                <span className='px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium'>
                  {product.category}
                </span>
              </div>

              {/* Información comercial */}
              <div className='bg-gray-50 dark:bg-gray-700 rounded-lg p-4'>
                <div className='grid grid-cols-2 gap-4'>
                  <div>
                    <label className='text-sm font-medium text-gray-500 dark:text-gray-400'>
                      Precio
                    </label>
                    <p className='text-2xl font-bold text-green-600 dark:text-green-400'>
                      ${product.price.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className='text-sm font-medium text-gray-500 dark:text-gray-400'>
                      Stock
                    </label>
                    <p
                      className={`text-xl font-semibold ${product.stock > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}
                    >
                      {product.stock > 0
                        ? `${product.stock} unidades`
                        : 'Agotado'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Metadatos */}
              <div className='border-t border-gray-200 dark:border-gray-600 pt-4'>
                <div className='grid grid-cols-1 gap-2 text-sm text-gray-500 dark:text-gray-400'>
                  <div className='flex justify-between'>
                    <span>Creado:</span>
                    <span>
                      {new Date(product.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                  <div className='flex justify-between'>
                    <span>Actualizado:</span>
                    <span>
                      {new Date(product.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className='flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700'>
          {onEdit && (
            <button
              onClick={onEdit}
              className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2'
            >
              <Edit className='w-4 h-4' />
              <span>Editar</span>
            </button>
          )}
          <button
            onClick={onClose}
            className='px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors'
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;
