import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Star } from 'lucide-react';
import AddToCartButton from './AddToCartButton';
import type { Product } from '../../types';
import axios from 'axios';

const TrendingProducts: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTrendingProducts = async () => {
      try {
        setIsLoading(true);
        // Fetch recent products sorted by creation date (simulating trending)
        const response = await axios.get<{ data: Product[] }>('/api/v1/productos/', {
          params: {
            sort_by: 'created_at',
            sort_order: 'desc',
            limit: 4,
            is_active: true,
          }
        });
        setProducts(response.data.data || []);
      } catch (error) {
        console.error('Error fetching trending products:', error);
        setProducts([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrendingProducts();
  }, []);

  // Helper function to safely get rating value
  const getRating = (product: Product): number => {
    return product.rating ?? 0;
  };

  // Calculate sales growth percentage (mock calculation based on product index/newness)
  const getSalesGrowth = (index: number): string => {
    // Simulate growth based on how recent the product is
    if (index === 0) return '+230%';
    if (index === 1) return '+180%';
    if (index === 2) return '+150%';
    return '+120%';
  };

  // Calculate trending score based on newness and rating
  const getTrendingScore = (product: Product, index: number): number => {
    const newnessWeight = 0.7;
    const ratingWeight = 0.3;
    // Newer products (lower index) get higher newness score
    const newnessScore = (4 - index) * 25; // 100, 75, 50, 25
    const normalizedRating = (getRating(product) / 5) * 100;
    return Math.round(newnessWeight * newnessScore + ratingWeight * normalizedRating);
  };

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

  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No hay productos en tendencia disponibles</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product, index) => {
        // Get main image URL
        const imageUrl = product.main_image_url ||
                        product.images?.[0]?.public_url ||
                        '/images/placeholder-product.jpg';

        return (
          <div key={product.id} className="group bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 overflow-hidden relative">
            {/* Trending Badge */}
            <div className="absolute top-2 left-2 z-10">
              <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium flex items-center">
                <TrendingUp className="w-3 h-3 mr-1" />
                #{index + 1}
              </div>
            </div>

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
            </div>

            {/* Product Info */}
            <div className="p-4">
              <Link
                to={`/marketplace/product/${product.id}`}
                className="block"
                style={{ contain: 'layout' }}
              >
                <h3
                  className="font-medium text-gray-900 mb-2 overflow-hidden"
                  style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    height: '3rem',
                    lineHeight: '1.5rem',
                    wordBreak: 'break-word',
                    willChange: 'auto',
                    transform: 'translateZ(0)',
                    backfaceVisibility: 'hidden',
                    contain: 'layout style paint'
                  }}
                >
                  {product.name}
                </h3>
              </Link>

              {/* Trending Metrics */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3 h-3 ${
                          i < Math.floor(getRating(product))
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-xs text-gray-500">{getRating(product).toFixed(1)}</span>
                </div>
                <div className="text-xs text-green-600 font-medium">
                  {getSalesGrowth(index)}
                </div>
              </div>

              {/* Price */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-lg font-bold text-gray-900">
                  ${product.price.toLocaleString('es-CO')}
                </span>
                <div className="text-xs text-gray-500">
                  Trending: {getTrendingScore(product, index)}%
                </div>
              </div>

              {/* Stock Info */}
              <div className="text-sm text-gray-600 mb-3">
                {(product.stock ?? 0) > 0 ? (
                  <span className="text-green-600">
                    {product.stock} disponible{product.stock !== 1 ? 's' : ''}
                  </span>
                ) : (
                  <span className="text-red-600">Agotado</span>
                )}
              </div>

              {/* Add to Cart Button - Now using the real AddToCartButton component */}
              <AddToCartButton product={product} compact={true} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TrendingProducts;