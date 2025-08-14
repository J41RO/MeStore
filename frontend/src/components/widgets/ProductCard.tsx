import React from 'react';
import { TopProduct } from '../../types/Product';

interface ProductCardProps {
  product: TopProduct;
  className?: string;
  showRank?: boolean;
  showGrowth?: boolean;
  compact?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({ 
  product,
  className = '',
  showRank = true,
  showGrowth = true,
  compact = false
}) => {
  const getRankBadgeColor = (rank: number) => {
    switch (rank) {
      case 1: return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white shadow-lg';
      case 2: return 'bg-gradient-to-r from-gray-300 to-gray-500 text-white shadow-md';  
      case 3: return 'bg-gradient-to-r from-orange-400 to-orange-600 text-white shadow-md';
      default: return 'bg-gradient-to-r from-blue-400 to-blue-600 text-white shadow-sm';
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return '🏆';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '📈';
    }
  };

  const cardSize = compact ? 'p-3' : 'p-4';
  const imageSize = compact ? 'w-12 h-12' : 'w-16 h-16';
  const badgeSize = compact ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm';

  return (
    <div 
      className={`
        bg-white rounded-xl border border-gray-200 hover:border-gray-300 
        hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1
        ${cardSize} ${className}
      `}
    >
      <div className="flex items-center space-x-3">
        {/* Ranking Badge */}
        {showRank && (
          <div className="relative flex-shrink-0">
            <div className={`
              ${badgeSize} rounded-full flex items-center justify-center 
              font-bold ${getRankBadgeColor(product.rank)}
              ring-2 ring-white shadow-sm
            `}>
              {product.rank}
            </div>
            {!compact && (
              <div className="absolute -top-1 -right-1 text-lg">
                {getRankIcon(product.rank)}
              </div>
            )}
          </div>
        )}

        {/* Thumbnail */}
        <div className={`flex-shrink-0 ${imageSize} relative group`}>
          <img
            src={product.thumbnail}
            alt={product.name}
            className="w-full h-full object-cover rounded-lg border border-gray-200 group-hover:border-gray-300 transition-colors"
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = `data:image/svg+xml;base64,${btoa(`
                <svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
                  <rect width="64" height="64" fill="#f3f4f6"/>
                  <text x="32" y="32" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="12" fill="#9ca3af">📦</text>
                </svg>
              `)}`;
            }}
          />
          {/* Overlay de hover */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 rounded-lg transition-all" />
        </div>

        {/* Información del producto */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1 pr-2">
              <h4 className={`
                font-medium text-gray-900 truncate
                ${compact ? 'text-sm' : 'text-base'}
              `}>
                {product.name}
              </h4>
              
              <p className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
                {product.category}
              </p>
              
              <div className="flex items-center space-x-2 mt-1">
                <span className={`
                  font-bold text-green-600
                  ${compact ? 'text-sm' : 'text-base'}
                `}>
                  {formatPrice(product.price)}
                </span>
                
                {product.rating && !compact && (
                  <div className="flex items-center space-x-1">
                    <div className="flex text-yellow-400 text-sm">
                      {`★`.repeat(Math.floor(product.rating))}
                    </div>
                    <span className="text-xs text-gray-500 font-medium">
                      {product.rating}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Métricas de venta */}
            <div className="text-right flex-shrink-0">
              <p className={`
                font-medium text-gray-900
                ${compact ? 'text-xs' : 'text-sm'}
              `}>
                {product.salesCount.toLocaleString()}
              </p>
              <p className={`text-gray-500 ${compact ? 'text-xs' : 'text-xs'}`}>
                ventas
              </p>
              
              {showGrowth && (
                <span className={`
                  inline-flex items-center px-2 py-1 rounded-full font-medium
                  ${compact ? 'text-xs mt-1' : 'text-xs mt-1'}
                  ${product.salesGrowth.startsWith('+') 
                    ? 'bg-green-100 text-green-800' 
                    : product.salesGrowth.startsWith('-')
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                  }
                `}>
                  {product.salesGrowth}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer adicional para modo no compacto */}
      {!compact && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>Posición #{product.rank} en ranking</span>
            {product.rating && (
              <span>★ {product.rating}/5.0</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductCard;
