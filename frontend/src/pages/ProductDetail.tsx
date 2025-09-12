import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Loader2 } from 'lucide-react';
import MarketplaceLayout from '../components/marketplace/MarketplaceLayout';
import ProductImageGallery from '../components/marketplace/ProductImageGallery';
import VendorInfo from '../components/marketplace/VendorInfo';
import AddToCartButton from '../components/marketplace/AddToCartButton';

interface ProductImage {
  id: number;
  image_url: string;
  is_primary: boolean;
}

interface Vendor {
  id: number;
  business_name: string;
  email?: string;
  created_at?: string;
}

interface Product {
  id: number;
  name: string;
  description: string;
  precio_venta: number;
  categoria: string;
  sku: string;
  estado: string;
  stock_quantity?: number;
  vendor?: Vendor;
  images?: ProductImage[];
  created_at: string;
  updated_at: string;
}

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError('ID del producto no válido');
      setLoading(false);
      return;
    }

    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`/api/v1/productos/${id}`);
        
        if (response.status === 404) {
          setError('Producto no encontrado');
          setLoading(false);
          return;
        }

        if (!response.ok) {
          throw new Error('Error al cargar el producto');
        }

        const data = await response.json();
        
        // Solo mostrar productos aprobados en el marketplace público
        if (data.estado !== 'aprobado') {
          setError('Este producto no está disponible');
          setLoading(false);
          return;
        }

        setProduct(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar el producto');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleGoBack = () => {
    // Try to go back in history, or fallback to search
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/marketplace/search');
    }
  };

  const handleAddToCart = (quantity: number) => {
    // This will be handled by the AddToCartButton component
    console.log(`Added ${quantity} of product ${id} to cart`);
  };

  // Loading state
  if (loading) {
    return (
      <MarketplaceLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Cargando producto...</p>
            </div>
          </div>
        </div>
      </MarketplaceLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MarketplaceLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {error.includes('no encontrado') ? 'Producto no encontrado' : 'Error'}
              </h2>
              <p className="text-gray-600 mb-6">{error}</p>
              <div className="space-x-4">
                <button
                  onClick={handleGoBack}
                  className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Volver
                </button>
                <button
                  onClick={() => navigate('/marketplace')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Ir al Marketplace
                </button>
              </div>
            </div>
          </div>
        </div>
      </MarketplaceLayout>
    );
  }

  // Product not found (shouldn't happen due to error handling above, but just in case)
  if (!product) {
    return (
      <MarketplaceLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Producto no encontrado</h2>
            <button
              onClick={handleGoBack}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver
            </button>
          </div>
        </div>
      </MarketplaceLayout>
    );
  }

  return (
    <MarketplaceLayout>
      <div className="container mx-auto px-4 py-6">
        {/* Breadcrumb / Back Button */}
        <button
          onClick={handleGoBack}
          className="inline-flex items-center text-gray-600 hover:text-blue-600 transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Product Images */}
          <div>
            <ProductImageGallery 
              images={product.images || []} 
              productName={product.name} 
            />
          </div>

          {/* Product Information */}
          <div className="space-y-6">
            {/* Basic Product Info */}
            <div>
              <div className="flex items-start justify-between mb-2">
                <h1 className="text-3xl font-bold text-gray-900 pr-4">
                  {product.name}
                </h1>
                {product.categoria && (
                  <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full capitalize">
                    {product.categoria}
                  </span>
                )}
              </div>

              <div className="text-4xl font-bold text-blue-600 mb-4">
                {formatPrice(product.precio_venta)}
              </div>

              {product.sku && (
                <p className="text-sm text-gray-500 mb-4">
                  SKU: {product.sku}
                </p>
              )}
            </div>

            {/* Description */}
            {product.description && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Descripción</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                    {product.description}
                  </p>
                </div>
              </div>
            )}

            {/* Stock Info */}
            {product.stock_quantity !== undefined && (
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Stock disponible:</span>
                <span className={`text-sm font-semibold ${
                  product.stock_quantity > 10 
                    ? 'text-green-600' 
                    : product.stock_quantity > 0 
                      ? 'text-yellow-600' 
                      : 'text-red-600'
                }`}>
                  {product.stock_quantity > 0 
                    ? `${product.stock_quantity} unidades`
                    : 'Agotado'
                  }
                </span>
              </div>
            )}

            {/* Add to Cart */}
            <div className="pt-4 border-t border-gray-200">
              <AddToCartButton
                productId={product.id}
                price={product.precio_venta}
                stock={product.stock_quantity || 0}
                onAddToCart={handleAddToCart}
                disabled={product.stock_quantity === 0}
              />
            </div>

            {/* Product Meta */}
            <div className="pt-4 border-t border-gray-200 text-sm text-gray-500 space-y-1">
              <p>Agregado el: {formatDate(product.created_at)}</p>
              {product.updated_at !== product.created_at && (
                <p>Actualizado el: {formatDate(product.updated_at)}</p>
              )}
            </div>
          </div>
        </div>

        {/* Vendor Information */}
        {product.vendor && (
          <div className="mt-12">
            <VendorInfo 
              vendorId={product.vendor.id}
              vendorName={product.vendor.business_name}
              vendorInfo={product.vendor}
            />
          </div>
        )}
      </div>
    </MarketplaceLayout>
  );
};

export default ProductDetail;