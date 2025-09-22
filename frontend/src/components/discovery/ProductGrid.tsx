// ~/src/components/discovery/ProductGrid.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - High-Performance Product Grid with Virtual Scrolling
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductGrid.tsx
// Ruta: ~/src/components/discovery/ProductGrid.tsx
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Grid de productos de alto rendimiento con virtual scrolling
//
// Performance Features:
// - Virtual scrolling for 1000+ products
// - Image lazy loading with intersection observer
// - Memoized product cards
// - Batch rendering for smooth scrolling
// - Mobile-optimized touch interactions
// - Progressive image loading
// ---------------------------------------------------------------------------------------------

import React, { useState, useCallback, useMemo, memo, useRef, useEffect } from 'react';
import { FixedSizeGrid as Grid, VariableSizeGrid } from 'react-window';
import { FixedSizeList as List } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';
import {
  Heart,
  Star,
  ShoppingCart,
  Eye,
  Share2,
  MapPin,
  Truck,
  Zap,
  Tag,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

// Hooks
import { useIntersectionObserver } from '../../hooks/useIntersectionObserver';
import { useImageLazyLoading } from '../../hooks/useImageLazyLoading';
import { usePerformanceOptimization } from '../../hooks/usePerformanceOptimization';
import { useMobileOptimization } from '../../hooks/useMobileOptimization';
import { useProductActions } from '../../hooks/useProductActions';

// Types
interface ProductGridProps {
  products: Product[];
  viewMode: 'grid' | 'list';
  isLoading?: boolean;
  enableVirtualScrolling?: boolean;
  mobileOptimized?: boolean;
  performanceMode?: 'balanced' | 'performance' | 'quality';
  onProductClick?: (product: Product) => void;
  onLoadMore?: () => void;
  hasNextPage?: boolean;
  className?: string;
  itemsPerRow?: number;
  itemHeight?: number;
  totalCount?: number;
}

interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  images: string[];
  rating: number;
  reviewCount: number;
  brand: string;
  category: string;
  location: string;
  shipping: {
    free: boolean;
    express: boolean;
    estimatedDays: number;
  };
  stock: number;
  badges: string[];
  vendor: {
    id: string;
    name: string;
    rating: number;
    verified: boolean;
  };
  createdAt: string;
  position?: number;
}

/**
 * Componente de imagen optimizada con lazy loading
 */
const LazyProductImage = memo(({
  src,
  alt,
  className = '',
  width,
  height,
  placeholder = '/placeholder-product.jpg',
  priority = false
}: {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  placeholder?: string;
  priority?: boolean;
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  const { isVisible } = useIntersectionObserver({
    elementRef: imgRef,
    threshold: 0.1,
    rootMargin: '50px',
  });

  const shouldLoad = priority || isVisible;

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  const handleError = useCallback(() => {
    setHasError(true);
  }, []);

  return (
    <div
      ref={imgRef}
      className={`relative overflow-hidden bg-gray-100 ${className}`}
      style={{ width, height }}
    >
      {/* Placeholder */}
      <div
        className={`absolute inset-0 bg-gray-200 transition-opacity duration-300 ${
          isLoaded ? 'opacity-0' : 'opacity-100'
        }`}
      >
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-8 h-8 bg-gray-300 rounded animate-pulse"></div>
        </div>
      </div>

      {/* Imagen real */}
      {shouldLoad && (
        <img
          src={hasError ? placeholder : src}
          alt={alt}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={handleLoad}
          onError={handleError}
          loading={priority ? 'eager' : 'lazy'}
        />
      )}
    </div>
  );
});

/**
 * Card de producto optimizada
 */
const ProductCard = memo(({
  product,
  viewMode,
  index,
  onClick,
  mobileOptimized = false,
  performanceMode = 'balanced'
}: {
  product: Product;
  viewMode: 'grid' | 'list';
  index: number;
  onClick?: (product: Product) => void;
  mobileOptimized?: boolean;
  performanceMode?: 'balanced' | 'performance' | 'quality';
}) => {
  const {
    addToCart,
    addToWishlist,
    removeFromWishlist,
    shareProduct,
    viewProduct,
    isInWishlist,
    isInCart,
  } = useProductActions();

  const cardRef = useRef<HTMLDivElement>(null);

  const formatPrice = useCallback((price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(price);
  }, []);

  const handleCardClick = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    onClick?.(product);
    viewProduct(product.id);
  }, [product, onClick, viewProduct]);

  const handleAddToCart = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    addToCart(product.id);
  }, [product.id, addToCart]);

  const handleWishlistToggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (isInWishlist(product.id)) {
      removeFromWishlist(product.id);
    } else {
      addToWishlist(product.id);
    }
  }, [product.id, isInWishlist, addToWishlist, removeFromWishlist]);

  const handleShare = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    shareProduct(product);
  }, [product, shareProduct]);

  // Grid view
  if (viewMode === 'grid') {
    return (
      <div
        ref={cardRef}
        className="group bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer"
        onClick={handleCardClick}
      >
        {/* Imagen */}
        <div className="relative aspect-square">
          <LazyProductImage
            src={product.images[0]}
            alt={product.name}
            className="w-full h-full"
            priority={index < 8}
          />

          {/* Badges */}
          <div className="absolute top-2 left-2 space-y-1">
            {product.badges.map((badge) => (
              <span
                key={badge}
                className="inline-block px-2 py-1 text-xs font-medium bg-blue-500 text-white rounded"
              >
                {badge}
              </span>
            ))}
          </div>

          {/* Acciones rápidas */}
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity space-y-1">
            <button
              onClick={handleWishlistToggle}
              className={`
                p-2 rounded-full shadow-sm transition-colors
                ${isInWishlist(product.id)
                  ? 'bg-red-500 text-white'
                  : 'bg-white text-gray-600 hover:text-red-500'
                }
              `}
            >
              <Heart className={`w-4 h-4 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
            </button>

            <button
              onClick={handleShare}
              className="p-2 bg-white text-gray-600 hover:text-blue-500 rounded-full shadow-sm transition-colors"
            >
              <Share2 className="w-4 h-4" />
            </button>
          </div>

          {/* Stock bajo */}
          {product.stock < 5 && product.stock > 0 && (
            <div className="absolute bottom-2 left-2">
              <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded">
                <AlertCircle className="w-3 h-3 mr-1" />
                Pocas unidades
              </span>
            </div>
          )}

          {/* Sin stock */}
          {product.stock === 0 && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <span className="px-4 py-2 bg-gray-800 text-white rounded-lg font-medium">
                Agotado
              </span>
            </div>
          )}
        </div>

        {/* Contenido */}
        <div className="p-4">
          {/* Título y marca */}
          <div className="mb-2">
            <h3 className="font-medium text-gray-900 line-clamp-2 text-sm mb-1">
              {product.name}
            </h3>
            <p className="text-xs text-gray-600">{product.brand}</p>
          </div>

          {/* Rating */}
          <div className="flex items-center mb-2">
            <div className="flex">
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
            <span className="text-xs text-gray-600 ml-1">
              ({product.reviewCount})
            </span>
          </div>

          {/* Precio */}
          <div className="mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold text-gray-900">
                {formatPrice(product.price)}
              </span>
              {product.originalPrice && product.originalPrice > product.price && (
                <span className="text-sm text-gray-500 line-through">
                  {formatPrice(product.originalPrice)}
                </span>
              )}
            </div>
            {product.originalPrice && product.originalPrice > product.price && (
              <span className="text-xs text-green-600 font-medium">
                Ahorro: {formatPrice(product.originalPrice - product.price)}
              </span>
            )}
          </div>

          {/* Información adicional */}
          <div className="space-y-1 mb-3">
            {product.shipping.free && (
              <div className="flex items-center text-xs text-green-600">
                <Truck className="w-3 h-3 mr-1" />
                Envío gratis
              </div>
            )}
            <div className="flex items-center text-xs text-gray-600">
              <MapPin className="w-3 h-3 mr-1" />
              {product.location}
            </div>
          </div>

          {/* Botón de acción */}
          <button
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className={`
              w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors
              ${product.stock === 0
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : isInCart(product.id)
                ? 'bg-green-100 text-green-800 border border-green-300'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {product.stock === 0
              ? 'Agotado'
              : isInCart(product.id)
              ? 'En el carrito'
              : 'Agregar al carrito'
            }
          </button>
        </div>
      </div>
    );
  }

  // List view
  return (
    <div
      ref={cardRef}
      className="group bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="flex">
        {/* Imagen */}
        <div className="relative w-32 h-32 flex-shrink-0">
          <LazyProductImage
            src={product.images[0]}
            alt={product.name}
            className="w-full h-full"
            priority={index < 5}
          />

          {/* Badges */}
          <div className="absolute top-1 left-1">
            {product.badges.slice(0, 1).map((badge) => (
              <span
                key={badge}
                className="inline-block px-1 py-0.5 text-xs font-medium bg-blue-500 text-white rounded"
              >
                {badge}
              </span>
            ))}
          </div>
        </div>

        {/* Contenido */}
        <div className="flex-1 p-4">
          <div className="flex justify-between">
            <div className="flex-1 min-w-0">
              {/* Título y marca */}
              <h3 className="font-medium text-gray-900 line-clamp-2 mb-1">
                {product.name}
              </h3>
              <p className="text-sm text-gray-600 mb-2">{product.brand}</p>

              {/* Rating y reseñas */}
              <div className="flex items-center mb-2">
                <div className="flex">
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
                <span className="text-sm text-gray-600 ml-2">
                  {product.rating} ({product.reviewCount} reseñas)
                </span>
              </div>

              {/* Información adicional */}
              <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  {product.location}
                </div>
                {product.shipping.free && (
                  <div className="flex items-center text-green-600">
                    <Truck className="w-4 h-4 mr-1" />
                    Envío gratis
                  </div>
                )}
              </div>
            </div>

            {/* Precio y acciones */}
            <div className="flex flex-col items-end justify-between ml-4">
              {/* Precio */}
              <div className="text-right mb-2">
                <div className="text-xl font-bold text-gray-900">
                  {formatPrice(product.price)}
                </div>
                {product.originalPrice && product.originalPrice > product.price && (
                  <div className="text-sm text-gray-500 line-through">
                    {formatPrice(product.originalPrice)}
                  </div>
                )}
              </div>

              {/* Acciones */}
              <div className="flex space-x-2">
                <button
                  onClick={handleWishlistToggle}
                  className={`
                    p-2 rounded-lg transition-colors
                    ${isInWishlist(product.id)
                      ? 'text-red-500 bg-red-50'
                      : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                    }
                  `}
                >
                  <Heart className={`w-5 h-5 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
                </button>

                <button
                  onClick={handleAddToCart}
                  disabled={product.stock === 0}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-colors
                    ${product.stock === 0
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : isInCart(product.id)
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                    }
                  `}
                >
                  {product.stock === 0
                    ? 'Agotado'
                    : isInCart(product.id)
                    ? 'En carrito'
                    : 'Agregar'
                  }
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

/**
 * Skeleton loader para productos
 */
const ProductSkeleton = memo(({ viewMode }: { viewMode: 'grid' | 'list' }) => {
  if (viewMode === 'grid') {
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
        <div className="aspect-square bg-gray-200"></div>
        <div className="p-4 space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
      <div className="flex">
        <div className="w-32 h-32 bg-gray-200 flex-shrink-0"></div>
        <div className="flex-1 p-4 space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>
    </div>
  );
});

/**
 * Componente principal ProductGrid
 */
const ProductGrid: React.FC<ProductGridProps> = memo(({
  products,
  viewMode,
  isLoading = false,
  enableVirtualScrolling = true,
  mobileOptimized = false,
  performanceMode = 'balanced',
  onProductClick,
  onLoadMore,
  hasNextPage = false,
  className = '',
  itemsPerRow = 4,
  itemHeight = 400,
  totalCount = products.length,
}) => {
  const gridRef = useRef<any>(null);
  const listRef = useRef<any>(null);

  const { trackRenderPerformance } = usePerformanceOptimization(performanceMode);
  const { isMobile, isTablet } = useMobileOptimization(mobileOptimized);

  // Ajustar columnas basado en el dispositivo
  const responsiveColumns = useMemo(() => {
    if (viewMode === 'list') return 1;
    if (isMobile) return 1;
    if (isTablet) return 2;
    return itemsPerRow;
  }, [viewMode, isMobile, isTablet, itemsPerRow]);

  const responsiveHeight = useMemo(() => {
    if (viewMode === 'list') return 140;
    if (isMobile) return 350;
    return itemHeight;
  }, [viewMode, isMobile, itemHeight]);

  // Grid item renderer
  const GridItem = useCallback(({ columnIndex, rowIndex, style }: any) => {
    const index = rowIndex * responsiveColumns + columnIndex;
    const product = products[index];

    if (!product) {
      return (
        <div style={style} className="p-2">
          <ProductSkeleton viewMode={viewMode} />
        </div>
      );
    }

    return (
      <div style={style} className="p-2">
        <ProductCard
          product={product}
          viewMode={viewMode}
          index={index}
          onClick={onProductClick}
          mobileOptimized={mobileOptimized}
          performanceMode={performanceMode}
        />
      </div>
    );
  }, [products, responsiveColumns, viewMode, onProductClick, mobileOptimized, performanceMode]);

  // List item renderer
  const ListItem = useCallback(({ index, style }: any) => {
    const product = products[index];

    if (!product) {
      return (
        <div style={style} className="p-2">
          <ProductSkeleton viewMode={viewMode} />
        </div>
      );
    }

    return (
      <div style={style} className="p-2">
        <ProductCard
          product={product}
          viewMode={viewMode}
          index={index}
          onClick={onProductClick}
          mobileOptimized={mobileOptimized}
          performanceMode={performanceMode}
        />
      </div>
    );
  }, [products, viewMode, onProductClick, mobileOptimized, performanceMode]);

  // Track performance
  useEffect(() => {
    trackRenderPerformance({
      component: 'ProductGrid',
      viewMode,
      productsCount: products.length,
      virtualScrolling: enableVirtualScrolling,
      mobileOptimized,
    });
  }, [trackRenderPerformance, viewMode, products.length, enableVirtualScrolling, mobileOptimized]);

  // Loading state
  if (isLoading && products.length === 0) {
    return (
      <div className={`grid gap-4 ${
        viewMode === 'grid'
          ? `grid-cols-1 md:grid-cols-2 lg:grid-cols-${responsiveColumns}`
          : 'grid-cols-1'
      } ${className}`}>
        {Array.from({ length: 12 }).map((_, i) => (
          <ProductSkeleton key={i} viewMode={viewMode} />
        ))}
      </div>
    );
  }

  // No products
  if (!isLoading && products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-200 rounded-lg mx-auto mb-4 flex items-center justify-center">
          <Tag className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No se encontraron productos
        </h3>
        <p className="text-gray-600">
          Intenta ajustar tus filtros o términos de búsqueda
        </p>
      </div>
    );
  }

  // Virtual scrolling for large lists
  if (enableVirtualScrolling && products.length > 50) {
    const rowCount = Math.ceil(products.length / responsiveColumns);

    if (viewMode === 'grid') {
      return (
        <div className={className}>
          <Grid
            ref={gridRef}
            columnCount={responsiveColumns}
            columnWidth={(width) => Math.floor(width / responsiveColumns)}
            height={600}
            rowCount={rowCount}
            rowHeight={responsiveHeight + 16} // +16 for padding
            width="100%"
            overscanRowCount={2}
            overscanColumnCount={1}
          >
            {GridItem}
          </Grid>
        </div>
      );
    } else {
      return (
        <div className={className}>
          <List
            ref={listRef}
            height={600}
            itemCount={products.length}
            itemSize={responsiveHeight + 16}
            width="100%"
            overscanCount={5}
          >
            {ListItem}
          </List>
        </div>
      );
    }
  }

  // Standard grid/list for smaller sets
  return (
    <div className={`space-y-4 ${className}`}>
      <div className={`grid gap-4 ${
        viewMode === 'grid'
          ? `grid-cols-1 md:grid-cols-2 lg:grid-cols-${responsiveColumns}`
          : 'grid-cols-1'
      }`}>
        {products.map((product, index) => (
          <ProductCard
            key={product.id}
            product={product}
            viewMode={viewMode}
            index={index}
            onClick={onProductClick}
            mobileOptimized={mobileOptimized}
            performanceMode={performanceMode}
          />
        ))}
      </div>

      {/* Loading more indicator */}
      {isLoading && products.length > 0 && (
        <div className="text-center py-4">
          <div className="inline-flex items-center space-x-2 text-gray-600">
            <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span>Cargando más productos...</span>
          </div>
        </div>
      )}

      {/* Load more button */}
      {hasNextPage && !isLoading && onLoadMore && (
        <div className="text-center py-4">
          <button
            onClick={onLoadMore}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Cargar más productos
          </button>
        </div>
      )}
    </div>
  );
});

ProductGrid.displayName = 'ProductGrid';

export default ProductGrid;