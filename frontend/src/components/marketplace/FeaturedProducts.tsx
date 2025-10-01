import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Heart, Eye } from 'lucide-react';
import AddToCartButton from './AddToCartButton';
import type { Product } from '../../types';

interface FeaturedProductsProps {
  products: Product[];
  isLoading: boolean;
}

const FeaturedProducts: React.FC<FeaturedProductsProps> = ({ products, isLoading }) => {
  // No products to display
  if (!isLoading && products.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No hay productos destacados disponibles</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border animate-pulse">
            <div className="h-48 bg-gray-200 rounded-t-lg"></div>
            <div className="p-4 space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product) => {
        // Get main image URL
        const imageUrl = product.main_image_url ||
                        product.images?.[0]?.public_url ||
                        '/images/placeholder-product.jpg';

        // Check if product is new (created within last 7 days)
        const isNew = product.created_at ?
          (new Date().getTime() - new Date(product.created_at).getTime()) < (7 * 24 * 60 * 60 * 1000) :
          false;

        return (
          <div key={product.id} className="group bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100 overflow-hidden">
            {/* Product Image */}
            <div className="relative overflow-hidden">
              <img
                src={imageUrl}
                alt={product.name}
                className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/images/placeholder-product.jpg';
                }}
              />

              {/* Badges */}
              <div className="absolute top-2 left-2 flex flex-col gap-1">
                {isNew && (
                  <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    Nuevo
                  </span>
                )}
                {product.is_featured && (
                  <span className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    Destacado
                  </span>
                )}
                {product.stock <= 5 && product.stock > 0 && (
                  <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    Pocas unidades
                  </span>
                )}
              </div>

              {/* Quick Actions */}
              <div className="absolute top-2 right-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button
                  className="p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors"
                  aria-label="Add to favorites"
                >
                  <Heart className="w-4 h-4 text-gray-600" />
                </button>
                <Link
                  to={`/marketplace/product/${product.id}`}
                  className="p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors"
                  aria-label="View product details"
                >
                  <Eye className="w-4 h-4 text-gray-600" />
                </Link>
              </div>
            </div>

            {/* Product Info */}
            <div className="p-4">
              <Link to={`/marketplace/product/${product.id}`}>
                <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
                  {product.name}
                </h3>
              </Link>

              <p className="text-sm text-gray-500 mb-2">SKU: {product.sku}</p>

              {/* Rating */}
              <div className="flex items-center mb-3">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-4 h-4 ${
                        i < Math.floor(product.rating)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-500 ml-2">
                  {product.rating.toFixed(1)} ({product.review_count})
                </span>
              </div>

              {/* Price */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold text-gray-900">
                    ${product.price.toLocaleString('es-CO')}
                  </span>
                </div>
              </div>

              {/* Stock Info */}
              <div className="text-sm text-gray-600 mb-3">
                {product.stock > 0 ? (
                  <span className="text-green-600">
                    {product.stock} disponible{product.stock !== 1 ? 's' : ''}
                  </span>
                ) : (
                  <span className="text-red-600">Agotado</span>
                )}
              </div>

              {/* Add to Cart Button - Compact version for marketplace */}
              <AddToCartButton product={product} compact={true} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default FeaturedProducts;