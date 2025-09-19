/**
 * ProductCard - Individual product display component
 *
 * Features:
 * - Responsive grid/list view support
 * - Image gallery with fallback
 * - Quick actions (edit, delete, toggle status)
 * - Stock level indicators
 * - Selection for bulk operations
 * - Colombian peso formatting
 * - Accessibility support
 */

import React, { useState } from 'react';
import {
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  StarIcon,
  ExclamationTriangleIcon,
  PhotoIcon,
  CubeIcon,
  ShoppingBagIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import { Product } from '../../types';

interface ProductCardProps {
  product: Product;
  viewMode: 'grid' | 'list';
  isSelected?: boolean;
  onSelect?: (productId: string) => void;
  onEdit?: (product: Product) => void;
  onDelete?: (productId: string) => void;
  onToggleActive?: (productId: string, isActive: boolean) => void;
  onToggleFeatured?: (productId: string, isFeatured: boolean) => void;
  showSelection?: boolean;
}

/**
 * Stock status indicator component
 */
interface StockIndicatorProps {
  stock: number;
  lowStockThreshold: number;
}

const StockIndicator: React.FC<StockIndicatorProps> = ({ stock, lowStockThreshold }) => {
  let status: 'good' | 'low' | 'out';
  let color: string;
  let text: string;

  if (stock === 0) {
    status = 'out';
    color = 'bg-red-100 text-red-800 border-red-200';
    text = 'Sin stock';
  } else if (stock <= lowStockThreshold) {
    status = 'low';
    color = 'bg-yellow-100 text-yellow-800 border-yellow-200';
    text = `Stock bajo (${stock})`;
  } else {
    status = 'good';
    color = 'bg-green-100 text-green-800 border-green-200';
    text = `En stock (${stock})`;
  }

  return (
    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {status === 'out' || status === 'low' ? (
        <ExclamationTriangleIcon className="w-3 h-3 mr-1" />
      ) : (
        <CubeIcon className="w-3 h-3 mr-1" />
      )}
      {text}
    </div>
  );
};

/**
 * Product image component with fallback
 */
interface ProductImageProps {
  product: Product;
  className?: string;
}

const ProductImage: React.FC<ProductImageProps> = ({ product, className = '' }) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const primaryImage = product.images?.[0]?.url || product.image_url;

  const handleImageLoad = () => {
    setIsLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setIsLoading(false);
  };

  if (!primaryImage || imageError) {
    return (
      <div className={`bg-gray-100 flex items-center justify-center ${className}`}>
        <PhotoIcon className="w-12 h-12 text-gray-400" />
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-100 animate-pulse flex items-center justify-center">
          <PhotoIcon className="w-12 h-12 text-gray-400" />
        </div>
      )}
      <img
        src={primaryImage}
        alt={product.name}
        className={`w-full h-full object-cover ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity`}
        onLoad={handleImageLoad}
        onError={handleImageError}
      />
      {product.images && product.images.length > 1 && (
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
          +{product.images.length - 1}
        </div>
      )}
    </div>
  );
};

/**
 * Main ProductCard component
 */
const ProductCard: React.FC<ProductCardProps> = ({
  product,
  viewMode,
  isSelected = false,
  onSelect,
  onEdit,
  onDelete,
  onToggleActive,
  onToggleFeatured,
  showSelection = false,
}) => {
  const [showActions, setShowActions] = useState(false);

  /**
   * Format price in Colombian pesos
   */
  const formatPrice = (price: number | string): string => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numPrice);
  };

  /**
   * Handle product selection
   */
  const handleSelect = () => {
    if (onSelect) {
      onSelect(product.id);
    }
  };

  /**
   * Handle quick actions
   */
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(product);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && window.confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      onDelete(product.id);
    }
  };

  const handleToggleActive = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleActive) {
      onToggleActive(product.id, !product.is_active);
    }
  };

  const handleToggleFeatured = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleFeatured) {
      onToggleFeatured(product.id, !product.is_featured);
    }
  };

  /**
   * Grid view layout
   */
  if (viewMode === 'grid') {
    return (
      <div
        className={`bg-white rounded-lg border transition-all duration-200 hover:shadow-md ${
          isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200'
        }`}
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
      >
        {/* Image Section */}
        <div className="relative">
          <ProductImage product={product} className="w-full h-48 rounded-t-lg" />

          {/* Selection Checkbox */}
          {showSelection && (
            <div className="absolute top-3 left-3">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={handleSelect}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          )}

          {/* Status Badges */}
          <div className="absolute top-3 right-3 flex flex-col space-y-1">
            {!product.is_active && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                <EyeSlashIcon className="w-3 h-3 mr-1" />
                Inactivo
              </span>
            )}
            {product.is_featured && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <StarIconSolid className="w-3 h-3 mr-1" />
                Destacado
              </span>
            )}
          </div>

          {/* Quick Actions Overlay */}
          {(showActions || isSelected) && (
            <div className="absolute inset-0 bg-black bg-opacity-40 rounded-t-lg flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
              <div className="flex space-x-2">
                <button
                  onClick={handleEdit}
                  className="p-2 bg-white rounded-full text-gray-600 hover:text-blue-600 transition-colors"
                  title="Editar producto"
                >
                  <PencilIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={handleToggleActive}
                  className="p-2 bg-white rounded-full text-gray-600 hover:text-green-600 transition-colors"
                  title={product.is_active ? 'Desactivar' : 'Activar'}
                >
                  {product.is_active ? (
                    <EyeSlashIcon className="w-4 h-4" />
                  ) : (
                    <EyeIcon className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={handleDelete}
                  className="p-2 bg-white rounded-full text-gray-600 hover:text-red-600 transition-colors"
                  title="Eliminar producto"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Content Section */}
        <div className="p-4">
          {/* Title and Price */}
          <div className="mb-3">
            <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
              {product.name}
            </h3>
            <p className="text-2xl font-bold text-blue-600">
              {formatPrice(product.price)}
            </p>
          </div>

          {/* Description */}
          {product.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {product.description}
            </p>
          )}

          {/* Stock Indicator */}
          <div className="mb-3">
            <StockIndicator
              stock={product.stock_quantity || 0}
              lowStockThreshold={product.low_stock_threshold || 10}
            />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>SKU: {product.sku || 'N/A'}</span>
            <div className="flex items-center space-x-2">
              {product.is_featured && (
                <StarIconSolid className="w-4 h-4 text-yellow-500" />
              )}
              <span>{product.views || 0} vistas</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /**
   * List view layout
   */
  return (
    <div
      className={`bg-white border rounded-lg transition-all duration-200 hover:shadow-md ${
        isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200'
      }`}
    >
      <div className="p-4">
        <div className="flex items-center space-x-4">
          {/* Selection Checkbox */}
          {showSelection && (
            <div className="flex-shrink-0">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={handleSelect}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          )}

          {/* Product Image */}
          <div className="flex-shrink-0">
            <ProductImage product={product} className="w-16 h-16 rounded-lg" />
          </div>

          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0 mr-4">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {product.name}
                </h3>
                <p className="text-sm text-gray-600 truncate">
                  SKU: {product.sku || 'N/A'}
                </p>
                {product.description && (
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {product.description}
                  </p>
                )}
              </div>

              {/* Price */}
              <div className="text-right flex-shrink-0">
                <p className="text-xl font-bold text-blue-600">
                  {formatPrice(product.price)}
                </p>
              </div>
            </div>

            {/* Status and Stock */}
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center space-x-3">
                <StockIndicator
                  stock={product.stock_quantity || 0}
                  lowStockThreshold={product.low_stock_threshold || 10}
                />

                {/* Status Badges */}
                <div className="flex items-center space-x-2">
                  {!product.is_active && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      <EyeSlashIcon className="w-3 h-3 mr-1" />
                      Inactivo
                    </span>
                  )}
                  {product.is_featured && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      <StarIconSolid className="w-3 h-3 mr-1" />
                      Destacado
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleEdit}
                  className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Editar producto"
                >
                  <PencilIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={handleToggleActive}
                  className={`p-2 transition-colors ${
                    product.is_active
                      ? 'text-gray-400 hover:text-yellow-600'
                      : 'text-gray-400 hover:text-green-600'
                  }`}
                  title={product.is_active ? 'Desactivar' : 'Activar'}
                >
                  {product.is_active ? (
                    <EyeSlashIcon className="w-4 h-4" />
                  ) : (
                    <EyeIcon className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={handleToggleFeatured}
                  className={`p-2 transition-colors ${
                    product.is_featured
                      ? 'text-yellow-500 hover:text-yellow-600'
                      : 'text-gray-400 hover:text-yellow-600'
                  }`}
                  title={product.is_featured ? 'Quitar destacado' : 'Destacar'}
                >
                  <StarIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={handleDelete}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Eliminar producto"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;