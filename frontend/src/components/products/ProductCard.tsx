// ~/src/components/products/ProductCard.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - ProductCard Genérico para Vista Grid/Lista
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductCard.tsx
// Ruta: ~/src/components/products/ProductCard.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-16
// Última Actualización: 2025-08-17
// Versión: 2.0.0
// Propósito: Componente ProductCard genérico para vista grid/lista en productos
//            Diferente del ProductCard de widgets que es específico para TopProduct
//            ACTUALIZADO: Agregado soporte para botón "Ver detalles"
//
// Modificaciones:
// 2025-08-16 - Creación inicial del componente
// 2025-08-17 - Agregado prop onViewDetails y botón "Ver detalles" en ambas vistas
//
// ---------------------------------------------------------------------------------------------

/**
 * ProductCard genérico para productos
 *
 * Componente reutilizable que soporta:
 * - Vista Grid: Layout vertical con imagen prominente
 * - Vista Lista: Layout horizontal compacto
 * - Props tipadas con interface Product de api.types.ts
 * - Responsive design con Tailwind CSS
 * - Botón "Ver detalles" con manejo de eventos separado del click del card
 */

import React, { useState } from 'react';
import { Product } from '../../types/api.types';
import { Eye } from 'lucide-react';
import AddToCartButton from '../cart/AddToCartButton';

interface ProductCardProps {
  // Existing props (maintain backward compatibility)
  product: Product;
  viewMode: 'grid' | 'list';
  className?: string;
  onProductClick?: (product: Product) => void;
  onViewDetails?: (product: Product) => void;
  showSKU?: boolean;
  showDimensions?: boolean;
  showWeight?: boolean;

  // NEW: Marketplace features (all optional)
  variant?: 'default' | 'compact' | 'featured';
  showVendor?: boolean;
  showRating?: boolean;
  showAddToCart?: boolean;
  showDiscount?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  viewMode,
  className = '',
  onProductClick,
  onViewDetails,
  showSKU = false,
  // showDimensions = false, // Futuro: mostrar dimensiones del producto
  // showWeight = false // Futuro: mostrar peso del producto
  // NEW: Marketplace features (default to false for backward compatibility)
  variant = 'default',
  showVendor = false,
  showRating = false,
  showAddToCart = false,
  showDiscount = false,
}) => {
  const [imageError, setImageError] = useState(false);

  const handleClick = () => {
    if (onProductClick) {
      onProductClick(product);
    }
  };

  // Helper functions for marketplace features
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const hasDiscount = showDiscount && product.discount_percentage && product.original_price;
  const isOutOfStock = product.stock !== undefined && product.stock <= 0;
  const isLowStock = product.stock !== undefined && product.stock <= 5 && product.stock > 0;

  // Vista Grid - Layout vertical
  if (viewMode === 'grid') {
    return (
      <div
        className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer overflow-hidden ${className}`}
        onClick={handleClick}
      >
        {/* Imagen */}
        <div className='relative aspect-square bg-gray-100 flex items-center justify-center group'>
          {!imageError && product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className='w-full h-full object-cover transition-transform duration-500 group-hover:scale-110'
              onError={() => setImageError(true)}
              loading='lazy'
            />
          ) : (
            <div className='text-gray-400 text-4xl'>📦</div>
          )}

          {/* Discount Badge */}
          {hasDiscount && (
            <div className='absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold z-10'>
              -{product.discount_percentage}%
            </div>
          )}

          {/* Out of Stock Overlay */}
          {isOutOfStock && (
            <div className='absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center z-10'>
              <span className='bg-white text-gray-900 px-3 py-1 rounded-full text-sm font-semibold'>
                Sin Stock
              </span>
            </div>
          )}
        </div>

        {/* Información del producto */}
        <div className='p-4'>
          {/* Vendor Name (NEW) */}
          {showVendor && product.vendor_name && (
            <div className='text-xs text-gray-500 mb-1'>
              por <span className='font-medium text-gray-700'>{product.vendor_name}</span>
            </div>
          )}

          <h3 className='font-semibold text-gray-900 mb-2 line-clamp-2'>
            {product.name}
          </h3>

          {/* Rating Stars (NEW) */}
          {showRating && product.rating && (
            <div className='flex items-center mb-2'>
              <div className='flex items-center'>
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className={`w-4 h-4 ${
                      i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                    fill='currentColor'
                    viewBox='0 0 20 20'
                  >
                    <path d='M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z' />
                  </svg>
                ))}
              </div>
              <span className='text-sm text-gray-600 ml-1'>
                ({product.reviews_count || 0})
              </span>
            </div>
          )}

          <div className='space-y-2'>
            <div className='flex justify-between items-center'>
              <div className='flex flex-col'>
                <span className='text-2xl font-bold text-blue-600'>
                  ${product.price.toLocaleString()}
                </span>
                {/* Discounted Price Display (NEW) */}
                {hasDiscount && (
                  <span className='text-sm text-gray-500 line-through'>
                    ${product.original_price!.toLocaleString()}
                  </span>
                )}
              </div>
              <span
                className={`px-2 py-1 rounded text-xs ${
                  product.stock > 10
                    ? 'bg-green-100 text-green-800'
                    : product.stock > 0
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                }`}
              >
                {product.stock > 0 ? `${product.stock} disponibles` : 'Agotado'}
              </span>
            </div>

            {/* Low Stock Warning (NEW) */}
            {isLowStock && (
              <div className='text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-md'>
                ¡Solo quedan {product.stock}!
              </div>
            )}

            <div className='text-sm text-gray-600'>
              <span className='bg-gray-100 px-2 py-1 rounded'>
                {product.category}
              </span>
            </div>

            {showSKU && (
              <div className='text-xs text-gray-500'>SKU: {product.id}</div>
            )}

            {/* Add to Cart Button (NEW) */}
            {showAddToCart && (
              <div className='mt-2'>
                <AddToCartButton
                  product={product}
                  disabled={isOutOfStock}
                  size={variant === 'compact' ? 'sm' : 'md'}
                  className='w-full'
                />
              </div>
            )}

            {onViewDetails && (
              <button
                onClick={e => {
                  e.stopPropagation();
                  onViewDetails(product);
                }}
                className='mt-2 w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm flex items-center justify-center space-x-1 transition-colors'
              >
                <Eye className='w-4 h-4' />
                <span>Ver detalles</span>
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Vista Lista - Layout horizontal
  return (
    <div
      className={`bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300 cursor-pointer overflow-hidden ${className}`}
      onClick={handleClick}
    >
      <div className='flex'>
        {/* Imagen */}
        <div className='relative w-24 h-24 sm:w-32 sm:h-32 bg-gray-100 flex items-center justify-center flex-shrink-0 group'>
          {!imageError && product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className='w-full h-full object-cover transition-transform duration-500 group-hover:scale-110'
              onError={() => setImageError(true)}
              loading='lazy'
            />
          ) : (
            <div className='text-gray-400 text-2xl'>📦</div>
          )}

          {/* Discount Badge */}
          {hasDiscount && (
            <div className='absolute top-1 left-1 bg-red-500 text-white px-1.5 py-0.5 rounded-full text-xs font-bold z-10'>
              -{product.discount_percentage}%
            </div>
          )}

          {/* Out of Stock Overlay */}
          {isOutOfStock && (
            <div className='absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center z-10'>
              <span className='bg-white text-gray-900 px-2 py-0.5 rounded-full text-xs font-semibold'>
                Sin Stock
              </span>
            </div>
          )}
        </div>

        {/* Información del producto */}
        <div className='flex-1 p-4'>
          <div className='flex flex-col sm:flex-row sm:justify-between'>
            <div className='flex-1'>
              {/* Vendor Name (NEW) */}
              {showVendor && product.vendor_name && (
                <div className='text-xs text-gray-500 mb-1'>
                  por <span className='font-medium text-gray-700'>{product.vendor_name}</span>
                </div>
              )}

              <h3 className='font-semibold text-gray-900 mb-1'>
                {product.name}
              </h3>

              {/* Rating Stars (NEW) */}
              {showRating && product.rating && (
                <div className='flex items-center mb-1'>
                  <div className='flex items-center'>
                    {[...Array(5)].map((_, i) => (
                      <svg
                        key={i}
                        className={`w-3 h-3 ${
                          i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'
                        }`}
                        fill='currentColor'
                        viewBox='0 0 20 20'
                      >
                        <path d='M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z' />
                      </svg>
                    ))}
                  </div>
                  <span className='text-xs text-gray-600 ml-1'>
                    ({product.reviews_count || 0})
                  </span>
                </div>
              )}

              <p className='text-sm text-gray-600 mb-2 line-clamp-2'>
                {product.description}
              </p>

              <div className='flex flex-wrap items-center gap-2 text-sm'>
                <span className='bg-gray-100 px-2 py-1 rounded text-xs'>
                  {product.category}
                </span>
                {showSKU && (
                  <span className='text-xs text-gray-500'>
                    SKU: {product.id}
                  </span>
                )}
                {/* Low Stock Warning (NEW) */}
                {isLowStock && (
                  <span className='text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-md'>
                    ¡Solo quedan {product.stock}!
                  </span>
                )}
              </div>
            </div>

            <div className='mt-2 sm:mt-0 sm:ml-4 flex flex-col items-end'>
              <div className='flex flex-col items-end mb-1'>
                <span className='text-xl font-bold text-blue-600'>
                  ${product.price.toLocaleString()}
                </span>
                {/* Discounted Price Display (NEW) */}
                {hasDiscount && (
                  <span className='text-xs text-gray-500 line-through'>
                    ${product.original_price!.toLocaleString()}
                  </span>
                )}
              </div>
              <span
                className={`px-2 py-1 rounded text-xs ${
                  product.stock > 10
                    ? 'bg-green-100 text-green-800'
                    : product.stock > 0
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                }`}
              >
                {product.stock > 0 ? `${product.stock} disponibles` : 'Agotado'}
              </span>

              {/* Add to Cart Button (NEW) */}
              {showAddToCart && (
                <div className='mt-2 w-full sm:w-auto'>
                  <AddToCartButton
                    product={product}
                    disabled={isOutOfStock}
                    size='sm'
                    className='w-full sm:w-auto'
                  />
                </div>
              )}

              {onViewDetails && (
                <button
                  onClick={e => {
                    e.stopPropagation();
                    onViewDetails(product);
                  }}
                  className='mt-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs flex items-center space-x-1 transition-colors'
                >
                  <Eye className='w-3 h-3' />
                  <span>Ver</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
