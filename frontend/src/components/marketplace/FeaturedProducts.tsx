import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Heart, ShoppingCart, Eye } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  image: string;
  vendor: string;
  rating: number;
  reviewCount: number;
  discount?: number;
  isFeatured: boolean;
  isNew?: boolean;
}

interface FeaturedProductsProps {
  products: Product[];
  isLoading: boolean;
}

const FeaturedProducts: React.FC<FeaturedProductsProps> = ({ products, isLoading }) => {
  // Productos mock si no hay datos de la API
  const mockProducts: Product[] = [
    {
      id: '1',
      name: 'iPhone 14 Pro Max',
      price: 4500000,
      originalPrice: 5000000,
      image: '/images/products/iphone14.jpg',
      vendor: 'TechStore BGA',
      rating: 4.8,
      reviewCount: 124,
      discount: 10,
      isFeatured: true,
      isNew: false
    },
    {
      id: '2',
      name: 'Laptop Gaming ASUS ROG',
      price: 3200000,
      image: '/images/products/laptop-gaming.jpg',
      vendor: 'Gaming Zone',
      rating: 4.6,
      reviewCount: 89,
      isFeatured: true,
      isNew: true
    },
    {
      id: '3',
      name: 'Auriculares Sony WH-1000XM4',
      price: 890000,
      originalPrice: 1200000,
      image: '/images/products/sony-headphones.jpg',
      vendor: 'Audio Pro',
      rating: 4.9,
      reviewCount: 203,
      discount: 25,
      isFeatured: true
    },
    {
      id: '4',
      name: 'Smartwatch Apple Watch Series 8',
      price: 1800000,
      image: '/images/products/apple-watch.jpg',
      vendor: 'Apple Store BGA',
      rating: 4.7,
      reviewCount: 156,
      isFeatured: true,
      isNew: true
    }
  ];

  const displayProducts = products.length > 0 ? products : mockProducts;

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
      {displayProducts.map((product) => (
        <div key={product.id} className="group bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100 overflow-hidden">
          {/* Product Image */}
          <div className="relative overflow-hidden">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/images/placeholder-product.jpg';
              }}
            />
            
            {/* Badges */}
            <div className="absolute top-2 left-2 flex flex-col gap-1">
              {product.isNew && (
                <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                  Nuevo
                </span>
              )}
              {product.discount && (
                <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                  -{product.discount}%
                </span>
              )}
            </div>

            {/* Quick Actions */}
            <div className="absolute top-2 right-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <button className="p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors">
                <Heart className="w-4 h-4 text-gray-600" />
              </button>
              <Link
                to={`/marketplace/product/${product.id}`}
                className="p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors"
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
            
            <p className="text-sm text-gray-500 mb-2">{product.vendor}</p>
            
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
                {product.rating} ({product.reviewCount})
              </span>
            </div>

            {/* Price */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold text-gray-900">
                  ${product.price.toLocaleString()}
                </span>
                {product.originalPrice && (
                  <span className="text-sm text-gray-500 line-through">
                    ${product.originalPrice.toLocaleString()}
                  </span>
                )}
              </div>
            </div>

            {/* Add to Cart Button */}
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center space-x-2">
              <ShoppingCart className="w-4 h-4" />
              <span>Agregar al Carrito</span>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeaturedProducts;