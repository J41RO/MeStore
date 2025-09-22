import React, { useState, useCallback } from 'react';
import AddToCartButton from '../cart/AddToCartButton';

interface Product {
  id: string;
  name: string;
  price: number;
  image_url?: string;
  images?: string[];
  sku?: string;
  stock_available?: number;
  vendor_id?: string;
  vendor_name?: string;
  description?: string;
  category?: string;
  rating?: number;
  reviews_count?: number;
  discount_percentage?: number;
  original_price?: number;
}

interface ProductCardProps {
  product: Product;
  variant?: 'default' | 'compact' | 'featured';
  showVendor?: boolean;
  showRating?: boolean;
  showAddToCart?: boolean;
  onProductClick?: (product: Product) => void;
  className?: string;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  variant = 'default',
  showVendor = true,
  showRating = true,
  showAddToCart = true,
  onProductClick,
  className = ''
}) => {
  const [imageError, setImageError] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }, []);

  const handleProductClick = useCallback(() => {
    if (onProductClick) {
      onProductClick(product);
    }
  }, [onProductClick, product]);

  const getImageUrl = () => {
    if (product.images && product.images.length > 0) {
      return product.images[0];
    }
    return product.image_url;
  };

  const hasDiscount = product.discount_percentage && product.original_price;
  const isOutOfStock = product.stock_available !== undefined && product.stock_available <= 0;
  const isLowStock = product.stock_available !== undefined && product.stock_available <= 5 && product.stock_available > 0;

  const getCardClasses = () => {
    const baseClasses = `
      bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden
      transition-all duration-300 hover:shadow-lg hover:-translate-y-1
      ${isHovered ? 'ring-2 ring-blue-100' : ''}
      ${className}
    `;

    switch (variant) {
      case 'compact':
        return `${baseClasses} max-w-xs`;
      case 'featured':
        return `${baseClasses} max-w-sm ring-2 ring-blue-200`;
      default:
        return baseClasses;
    }
  };

  const getImageClasses = () => {
    switch (variant) {
      case 'compact':
        return 'h-40';
      case 'featured':
        return 'h-64';
      default:
        return 'h-48';
    }
  };

  return (
    <div
      className={getCardClasses()}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Image Section */}
      <div
        className={`relative overflow-hidden cursor-pointer group ${getImageClasses()}`}
        onClick={handleProductClick}
      >
        {!imageError && getImageUrl() ? (
          <img
            src={getImageUrl()}
            alt={product.name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            onError={() => setImageError(true)}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Overlay with discount badge */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300" />

        {/* Discount Badge */}
        {hasDiscount && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold z-10">
            -{product.discount_percentage}%
          </div>
        )}

        {/* Stock Status */}
        {isOutOfStock && (
          <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center z-10">
            <span className="bg-white text-gray-900 px-3 py-1 rounded-full text-sm font-semibold">
              Sin Stock
            </span>
          </div>
        )}

        {/* Quick view button */}
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleProductClick();
            }}
            className="bg-white text-gray-700 p-2 rounded-full shadow-lg hover:bg-gray-50 transition-colors"
            title="Vista rápida"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-4">
        {/* Vendor */}
        {showVendor && product.vendor_name && (
          <div className="text-xs text-gray-500 mb-1">
            por <span className="font-medium text-gray-700">{product.vendor_name}</span>
          </div>
        )}

        {/* Product Name */}
        <h3
          className="font-semibold text-gray-900 line-clamp-2 leading-tight mb-2 cursor-pointer hover:text-blue-600 transition-colors"
          onClick={handleProductClick}
          title={product.name}
        >
          {product.name}
        </h3>

        {/* Rating */}
        {showRating && product.rating && (
          <div className="flex items-center mb-2">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <svg
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="text-sm text-gray-600 ml-1">
              ({product.reviews_count || 0})
            </span>
          </div>
        )}

        {/* Price */}
        <div className="mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold text-gray-900">
              {formatCurrency(product.price)}
            </span>
            {hasDiscount && (
              <span className="text-sm text-gray-500 line-through">
                {formatCurrency(product.original_price!)}
              </span>
            )}
          </div>
        </div>

        {/* Stock Warning */}
        {isLowStock && (
          <div className="mb-3 text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-md">
            ¡Solo quedan {product.stock_available}!
          </div>
        )}

        {/* Add to Cart Button */}
        {showAddToCart && (
          <div className="mt-auto">
            <AddToCartButton
              product={product}
              disabled={isOutOfStock}
              size={variant === 'compact' ? 'sm' : 'md'}
              className="w-full group"
            />
          </div>
        )}

        {/* SKU */}
        {product.sku && variant === 'featured' && (
          <div className="text-xs text-gray-400 mt-2">
            SKU: {product.sku}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;