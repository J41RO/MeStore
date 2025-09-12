import React from 'react';
import { Link } from 'react-router-dom';
import { Eye, Store, AlertCircle, Loader2 } from 'lucide-react';

interface Product {
  id: number;
  name: string;
  description: string;
  precio_venta: number;
  categoria: string;
  sku: string;
  estado: string;
  vendor?: {
    business_name: string;
  };
  images?: Array<{
    id: number;
    image_url: string;
    is_primary: boolean;
  }>;
}

interface SearchResultsProps {
  products: Product[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  onLoadMore: () => void;
  searchQuery: string;
}

const ProductSkeleton: React.FC = () => (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden animate-pulse">
    <div className="h-48 bg-gray-200"></div>
    <div className="p-4">
      <div className="h-4 bg-gray-200 rounded mb-2"></div>
      <div className="h-3 bg-gray-200 rounded mb-3 w-2/3"></div>
      <div className="flex justify-between items-center">
        <div className="h-5 bg-gray-200 rounded w-20"></div>
        <div className="h-8 bg-gray-200 rounded w-24"></div>
      </div>
    </div>
  </div>
);

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  const primaryImage = product.images?.find(img => img.is_primary) || product.images?.[0];
  const imageUrl = primaryImage?.image_url || '/placeholder-product.jpg';
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  return (
    <Link 
      to={`/marketplace/product/${product.id}`}
      className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200 group block"
    >
      {/* Product Image */}
      <div className="relative h-48 bg-gray-100">
        <img
          src={imageUrl}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder-product.jpg';
          }}
        />
        {product.images && product.images.length > 1 && (
          <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
            +{product.images.length - 1} más
          </div>
        )}
        
        {/* Quick View Indicator */}
        <div className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="bg-white bg-opacity-90 p-2 rounded-full shadow-sm">
            <Eye className="h-4 w-4 text-gray-600" />
          </div>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Vendor Info */}
        {product.vendor?.business_name && (
          <div className="flex items-center text-xs text-gray-500 mb-2">
            <Store className="h-3 w-3 mr-1" />
            <span className="truncate">{product.vendor.business_name}</span>
          </div>
        )}

        {/* Product Name */}
        <h3 className="font-semibold text-gray-900 text-sm mb-2 line-clamp-2 h-10">
          {truncateText(product.name, 60)}
        </h3>

        {/* Category */}
        {product.categoria && (
          <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full mb-3 capitalize">
            {product.categoria}
          </span>
        )}

        {/* Description */}
        {product.description && (
          <p className="text-gray-600 text-xs mb-3 line-clamp-2 h-8">
            {truncateText(product.description, 80)}
          </p>
        )}

        {/* Price */}
        <div className="flex items-center justify-between">
          <div className="text-lg font-bold text-blue-600">
            {formatPrice(product.precio_venta)}
          </div>
          
          <div className="text-sm text-gray-500">
            Ver detalles →
          </div>
        </div>

        {/* SKU */}
        {product.sku && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <span className="text-xs text-gray-400">SKU: {product.sku}</span>
          </div>
        )}
      </div>
    </Link>
  );
};

const SearchResults: React.FC<SearchResultsProps> = ({
  products,
  loading,
  error,
  hasMore,
  onLoadMore,
  searchQuery
}) => {
  // Loading state
  if (loading && products.length === 0) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <ProductSkeleton key={index} />
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error && products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
          <AlertCircle className="h-8 w-8 text-red-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Error al cargar productos</h3>
        <p className="text-gray-600 max-w-md mx-auto">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    );
  }

  // No results state
  if (!loading && products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          <Store className="h-8 w-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No se encontraron productos
        </h3>
        <p className="text-gray-600 max-w-md mx-auto mb-4">
          {searchQuery 
            ? `No encontramos productos que coincidan con "${searchQuery}". Intenta con otros términos o ajusta los filtros.`
            : 'No hay productos disponibles en este momento.'
          }
        </p>
        <div className="space-x-2">
          <button 
            onClick={() => window.location.href = '/marketplace'}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Ver todos los productos
          </button>
        </div>
      </div>
    );
  }

  // Results display
  return (
    <div className="space-y-6">
      {/* Results Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="text-center pt-6">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md font-medium transition-colors flex items-center space-x-2 mx-auto"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Cargando más...</span>
              </>
            ) : (
              <>
                <span>Ver más productos</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Loading indicator for additional products */}
      {loading && products.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <ProductSkeleton key={`skeleton-${index}`} />
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchResults;