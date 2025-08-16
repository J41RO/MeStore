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
// Última Actualización: 2025-08-16
// Versión: 1.0.0
// Propósito: Componente ProductCard genérico para vista grid/lista en productos
//            Diferente del ProductCard de widgets que es específico para TopProduct
//
// Modificaciones:
// 2025-08-16 - Creación inicial del componente
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
*/

import React from 'react';
import { Product } from '../../types/api.types';

interface ProductCardProps {
  product: Product;
  viewMode: 'grid' | 'list';
  className?: string;
  onProductClick?: (product: Product) => void;
  showSKU?: boolean;
  showDimensions?: boolean;
  showWeight?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  viewMode,
  className = '',
  onProductClick,
  showSKU = false,
  // showDimensions = false, // Futuro: mostrar dimensiones del producto
  // showWeight = false // Futuro: mostrar peso del producto
}) => {
  const handleClick = () => {
    if (onProductClick) {
      onProductClick(product);
    }
  };

  // Vista Grid - Layout vertical
  if (viewMode === 'grid') {
    return (
      <div
        className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer overflow-hidden ${className}`}
        onClick={handleClick}
      >
        {/* Imagen */}
        <div className="aspect-square bg-gray-100 flex items-center justify-center">
          {product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-gray-400 text-4xl">📦</div>
          )}
        </div>
        
        {/* Información del producto */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{product.name}</h3>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold text-blue-600">
                ${product.price.toLocaleString()}
              </span>
              <span className={`px-2 py-1 rounded text-xs ${
                product.stock > 10 
                  ? 'bg-green-100 text-green-800' 
                  : product.stock > 0 
                  ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {product.stock > 0 ? `${product.stock} disponibles` : 'Agotado'}
              </span>
            </div>
            
            <div className="text-sm text-gray-600">
              <span className="bg-gray-100 px-2 py-1 rounded">{product.category}</span>
            </div>
            
            {showSKU && (
              <div className="text-xs text-gray-500">
                SKU: {product.id}
              </div>
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
      <div className="flex">
        {/* Imagen */}
        <div className="w-24 h-24 sm:w-32 sm:h-32 bg-gray-100 flex items-center justify-center flex-shrink-0">
          {product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-gray-400 text-2xl">📦</div>
          )}
        </div>
        
        {/* Información del producto */}
        <div className="flex-1 p-4">
          <div className="flex flex-col sm:flex-row sm:justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">{product.name}</h3>
              <p className="text-sm text-gray-600 mb-2 line-clamp-2">{product.description}</p>
              
              <div className="flex flex-wrap items-center gap-2 text-sm">
                <span className="bg-gray-100 px-2 py-1 rounded text-xs">{product.category}</span>
                {showSKU && (
                  <span className="text-xs text-gray-500">SKU: {product.id}</span>
                )}
              </div>
            </div>
            
            <div className="mt-2 sm:mt-0 sm:ml-4 flex flex-col items-end">
              <span className="text-xl font-bold text-blue-600 mb-1">
                ${product.price.toLocaleString()}
              </span>
              <span className={`px-2 py-1 rounded text-xs ${
                product.stock > 10 
                  ? 'bg-green-100 text-green-800' 
                  : product.stock > 0 
                  ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {product.stock > 0 ? `${product.stock} disponibles` : 'Agotado'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;