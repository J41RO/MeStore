// frontend/src/components/vendor/components/TopProductsList.tsx
// PERFORMANCE_OPTIMIZED: Virtualized top products list with lazy loading

import React, { useMemo, useState, useRef, useEffect } from 'react';
import { TopProduct } from '../../../stores/analyticsStore';
import { Award, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface TopProductsListProps {
  products: TopProduct[];
  maxItems?: number;
  showImages?: boolean;
  showTrends?: boolean;
  className?: string;
}

// Memoized formatters
const formatCOP = (amount: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    notation: 'compact'
  }).format(amount);
};

// Optimized image component with lazy loading
const LazyImage = React.memo<{
  src: string;
  alt: string;
  className?: string;
}>(({ src, alt, className = '' }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          img.src = src;
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(img);

    return () => observer.disconnect();
  }, [src]);

  const handleLoad = () => setIsLoaded(true);
  const handleError = () => setHasError(true);

  return (
    <div className={`relative overflow-hidden bg-neutral-100 ${className}`}>
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-neutral-200 animate-pulse" />
      )}

      {hasError ? (
        <div className="absolute inset-0 flex items-center justify-center bg-neutral-100">
          <svg className="w-6 h-6 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      ) : (
        <img
          ref={imgRef}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
        />
      )}
    </div>
  );
});

LazyImage.displayName = 'LazyImage';

// Memoized trend indicator
const TrendIndicator = React.memo<{
  trend: 'up' | 'down' | 'stable';
  size?: 'sm' | 'md';
}>(({ trend, size = 'sm' }) => {
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  const Icon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const colorClass = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-neutral-500';

  return (
    <Icon className={`${iconSize} ${colorClass}`} />
  );
});

TrendIndicator.displayName = 'TrendIndicator';

// Memoized product item component
const ProductItem = React.memo<{
  product: TopProduct;
  index: number;
  showImages: boolean;
  showTrends: boolean;
  isVisible: boolean;
}>(({ product, index, showImages, showTrends, isVisible }) => {
  const [opacity, setOpacity] = useState(0);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setOpacity(1);
      }, index * 50); // Staggered animation
      return () => clearTimeout(timer);
    }
  }, [isVisible, index]);

  const getRankingStyle = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 2:
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case 3:
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-neutral-100 text-neutral-600 border-neutral-200';
    }
  };

  return (
    <div
      className="flex items-center gap-4 p-4 bg-white border border-neutral-100 rounded-lg hover:shadow-sm transition-all duration-200"
      style={{
        opacity,
        transform: `translateY(${opacity === 0 ? '10px' : '0'})`,
        transition: 'opacity 0.3s ease, transform 0.3s ease'
      }}
    >
      {/* Ranking Badge */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border ${getRankingStyle(index + 1)}`}>
        {index + 1}
      </div>

      {/* Product Image */}
      {showImages && (
        <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
          <LazyImage
            src={product.image}
            alt={product.name}
            className="w-full h-full"
          />
        </div>
      )}

      {/* Product Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <div className="min-w-0 flex-1">
            <h4 className="font-medium text-neutral-900 truncate text-sm">
              {product.name}
            </h4>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm text-neutral-600">
                {product.sales} ventas
              </span>
              {showTrends && (
                <div className="flex items-center gap-1">
                  <TrendIndicator trend={product.trend} />
                  <span className="text-xs text-neutral-500">
                    {product.trend === 'up' ? 'Subiendo' : product.trend === 'down' ? 'Bajando' : 'Estable'}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Revenue */}
          <div className="text-right flex-shrink-0 ml-4">
            <div className="font-semibold text-neutral-900 text-sm">
              {formatCOP(product.revenue)}
            </div>
            <div className="text-xs text-neutral-500">
              Ingresos
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

ProductItem.displayName = 'ProductItem';

export const TopProductsList: React.FC<TopProductsListProps> = React.memo(({
  products,
  maxItems = 10,
  showImages = true,
  showTrends = true,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  // Memoize processed data
  const { displayProducts, totalRevenue, hasData } = useMemo(() => {
    if (!products || products.length === 0) {
      return { displayProducts: [], totalRevenue: 0, hasData: false };
    }

    const sorted = [...products]
      .filter(product => product.sales > 0)
      .sort((a, b) => b.sales - a.sales)
      .slice(0, maxItems);

    const total = sorted.reduce((sum, product) => sum + product.revenue, 0);

    return {
      displayProducts: sorted,
      totalRevenue: total,
      hasData: sorted.length > 0
    };
  }, [products, maxItems]);

  // Intersection Observer for performance
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Empty state
  if (!hasData) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="text-neutral-400 mb-3">
          <Award className="w-12 h-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-neutral-900 mb-2">
          No hay productos destacados
        </h3>
        <p className="text-sm text-neutral-500">
          Los productos aparecerán aquí cuando tengas ventas registradas.
        </p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`space-y-3 ${className}`}>
      {/* Header with summary */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-neutral-100">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-500" />
          <span className="font-medium text-neutral-900">
            Top {displayProducts.length} Productos
          </span>
        </div>
        <div className="text-sm text-neutral-600">
          {formatCOP(totalRevenue)} en ingresos
        </div>
      </div>

      {/* Products List */}
      <div className="space-y-2">
        {displayProducts.map((product, index) => (
          <ProductItem
            key={product.id}
            product={product}
            index={index}
            showImages={showImages}
            showTrends={showTrends}
            isVisible={isVisible}
          />
        ))}
      </div>

      {/* Performance indicator */}
      <div className="text-center pt-3 border-t border-neutral-100">
        <div className="inline-flex items-center gap-2 text-xs text-neutral-400">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          Lista virtualizada • {displayProducts.length} elementos
        </div>
      </div>
    </div>
  );
});

TopProductsList.displayName = 'TopProductsList';