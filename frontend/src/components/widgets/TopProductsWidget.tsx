import React from 'react';
import { useVendor } from '../../hooks/useVendor';
import { TopProduct } from '../../types/Product';

interface TopProductsWidgetProps {
  className?: string;
  maxProducts?: number;
}

const TopProductsWidget: React.FC<TopProductsWidgetProps> = ({
  className = '',
  maxProducts = 5,
}) => {
  const { topProducts } = useVendor();

  // Limitar productos mostrados
  const displayProducts = topProducts.slice(0, maxProducts);

  const getRankBadgeColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-500 text-white';
      case 2:
        return 'bg-gray-400 text-white';
      case 3:
        return 'bg-orange-500 text-white';
      default:
        return 'bg-blue-500 text-white';
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {/* Header */}
      <div className='flex items-center justify-between mb-6'>
        <h3 className='text-lg font-semibold text-gray-900'>
          Productos Más Vendidos
        </h3>
        <div className='text-sm text-gray-500'>
          Top {displayProducts.length}
        </div>
      </div>

      {/* Lista de productos */}
      <div className='space-y-4'>
        {displayProducts.map((product: TopProduct) => (
          <div
            key={product.id}
            className='flex items-center space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors'
          >
            {/* Ranking Badge */}
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${getRankBadgeColor(product.rank)}`}
            >
              {product.rank}
            </div>

            {/* Thumbnail */}
            <div className='flex-shrink-0 w-16 h-16'>
              <img
                src={product.thumbnail}
                alt={product.name}
                className='w-full h-full object-cover rounded-lg border border-gray-200'
                loading='lazy'
              />
            </div>

            {/* Información del producto */}
            <div className='flex-1 min-w-0'>
              <div className='flex items-start justify-between'>
                <div className='flex-1'>
                  <p className='text-sm font-medium text-gray-900 truncate'>
                    {product.name}
                  </p>
                  <p className='text-sm text-gray-500'>{product.category}</p>
                  <div className='flex items-center space-x-2 mt-1'>
                    <span className='text-sm font-semibold text-green-600'>
                      {formatPrice(product.price)}
                    </span>
                    {product.rating && (
                      <div className='flex items-center space-x-1'>
                        <span className='text-yellow-400'>★</span>
                        <span className='text-xs text-gray-500'>
                          {product.rating}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Métricas de venta */}
                <div className='text-right ml-4'>
                  <p className='text-sm font-medium text-gray-900'>
                    {product.salesCount} ventas
                  </p>
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      product.salesGrowth.startsWith('+')
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {product.salesGrowth}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer con estadísticas */}
      <div className='mt-6 pt-4 border-t border-gray-200'>
        <div className='flex justify-between text-sm text-gray-500'>
          <span>Total de productos activos</span>
          <span className='font-medium'>{topProducts.length}</span>
        </div>
      </div>
    </div>
  );
};

export default TopProductsWidget;
