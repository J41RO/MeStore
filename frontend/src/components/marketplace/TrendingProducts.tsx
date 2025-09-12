import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Star, ShoppingCart } from 'lucide-react';

interface TrendingProduct {
  id: string;
  name: string;
  price: number;
  image: string;
  trendingScore: number;
  salesGrowth: string;
  rating: number;
}

const TrendingProducts: React.FC = () => {
  const trendingProducts: TrendingProduct[] = [
    {
      id: '1',
      name: 'Café Orgánico Santander',
      price: 35000,
      image: '/images/trending/coffee.jpg',
      trendingScore: 95,
      salesGrowth: '+230%',
      rating: 4.9
    },
    {
      id: '2',
      name: 'Bolso Artesanal Guane',
      price: 120000,
      image: '/images/trending/bag.jpg',
      trendingScore: 88,
      salesGrowth: '+180%',
      rating: 4.7
    },
    {
      id: '3',
      name: 'Miel de Abejas Chicamocha',
      price: 25000,
      image: '/images/trending/honey.jpg',
      trendingScore: 82,
      salesGrowth: '+150%',
      rating: 4.8
    },
    {
      id: '4',
      name: 'Artesanía Cerámica Local',
      price: 80000,
      image: '/images/trending/ceramics.jpg',
      trendingScore: 76,
      salesGrowth: '+120%',
      rating: 4.6
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {trendingProducts.map((product, index) => (
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
              src={product.image}
              alt={product.name}
              className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/images/placeholder-product.jpg';
              }}
            />
          </div>

          {/* Product Info */}
          <div className="p-4">
            <Link to={`/marketplace/product/${product.id}`}>
              <h3 className="font-medium text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
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
                        i < Math.floor(product.rating)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-gray-500">{product.rating}</span>
              </div>
              <div className="text-xs text-green-600 font-medium">
                {product.salesGrowth}
              </div>
            </div>

            {/* Price */}
            <div className="flex items-center justify-between mb-3">
              <span className="text-lg font-bold text-gray-900">
                ${product.price.toLocaleString()}
              </span>
              <div className="text-xs text-gray-500">
                Trending: {product.trendingScore}%
              </div>
            </div>

            {/* Add to Cart Button */}
            <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center space-x-2">
              <ShoppingCart className="w-4 h-4" />
              <span>Comprar Ahora</span>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TrendingProducts;