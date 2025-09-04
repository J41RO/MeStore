import React from 'react';
import { TrendingUp, DollarSign, ShoppingBag, Award } from 'lucide-react';
import { CommissionBreakdown } from '../../types/commission.types';

interface CommissionSummaryProps {
  breakdown: CommissionBreakdown;
  totalCommissions: number;
  totalSales: number;
}

const CommissionSummary: React.FC<CommissionSummaryProps> = ({
  breakdown,
  totalCommissions,
  totalSales,
}) => {
  const topProducts = breakdown.byProduct
    .sort((a, b) => b.totalCommissions - a.totalCommissions)
    .slice(0, 5);

  const topCategories = Object.entries(breakdown.byCategory)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div className='space-y-6'>
      {/* Métricas principales */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        <div className='bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg text-white'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-green-100 text-sm'>Total Comisiones</p>
              <p className='text-2xl font-bold'>
                ${totalCommissions.toFixed(2)}
              </p>
            </div>
            <DollarSign size={32} className='text-green-200' />
          </div>
        </div>

        <div className='bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg text-white'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-blue-100 text-sm'>Total Ventas</p>
              <p className='text-2xl font-bold'>${totalSales.toFixed(2)}</p>
            </div>
            <ShoppingBag size={32} className='text-blue-200' />
          </div>
        </div>

        <div className='bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg text-white'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-purple-100 text-sm'>Tasa Promedio</p>
              <p className='text-2xl font-bold'>
                {(breakdown.totals.averageCommissionRate * 100).toFixed(2)}%
              </p>
            </div>
            <TrendingUp size={32} className='text-purple-200' />
          </div>
        </div>

        <div className='bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-lg text-white'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-orange-100 text-sm'>Total Registros</p>
              <p className='text-2xl font-bold'>
                {breakdown.totals.commissionCount}
              </p>
            </div>
            <Award size={32} className='text-orange-200' />
          </div>
        </div>
      </div>

      {/* Breakdown detallado */}
      <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
        {/* Top productos */}
        <div className='bg-white p-6 rounded-lg border border-gray-200'>
          <h3 className='text-lg font-semibold text-gray-900 mb-4'>
            Top 5 Productos
          </h3>
          <div className='space-y-3'>
            {topProducts.map((product, index) => (
              <div
                key={product.productId}
                className='flex items-center justify-between p-3 bg-gray-50 rounded-lg'
              >
                <div className='flex items-center space-x-3'>
                  <div className='flex-shrink-0'>
                    <span className='inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-600 text-white text-sm font-medium'>
                      {index + 1}
                    </span>
                  </div>
                  <div>
                    <p className='text-sm font-medium text-gray-900'>
                      {product.productName}
                    </p>
                    <p className='text-sm text-gray-500'>{product.category}</p>
                  </div>
                </div>
                <div className='text-right'>
                  <p className='text-sm font-medium text-green-600'>
                    ${product.totalCommissions.toFixed(2)}
                  </p>
                  <p className='text-xs text-gray-500'>
                    {product.commissionCount} ventas
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top categorías */}
        <div className='bg-white p-6 rounded-lg border border-gray-200'>
          <h3 className='text-lg font-semibold text-gray-900 mb-4'>
            Top Categorías
          </h3>
          <div className='space-y-3'>
            {topCategories.map(([category, amount], index) => {
              const percentage =
                totalCommissions > 0 ? (amount / totalCommissions) * 100 : 0;
              return (
                <div key={category} className='space-y-2'>
                  <div className='flex justify-between items-center'>
                    <span className='text-sm font-medium text-gray-900'>
                      {category}
                    </span>
                    <span className='text-sm text-gray-500'>
                      ${amount.toFixed(2)}
                    </span>
                  </div>
                  <div className='w-full bg-gray-200 rounded-full h-2'>
                    <div
                      className={`h-2 rounded-full ${
                        index === 0
                          ? 'bg-blue-600'
                          : index === 1
                            ? 'bg-green-600'
                            : 'bg-purple-600'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <p className='text-xs text-gray-500'>
                    {percentage.toFixed(1)}% del total
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Estadísticas por tipo */}
      <div className='bg-white p-6 rounded-lg border border-gray-200'>
        <h3 className='text-lg font-semibold text-gray-900 mb-4'>
          Breakdown por Tipo de Comisión
        </h3>
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4'>
          {breakdown.byType.map(type => (
            <div
              key={type.type}
              className='text-center p-4 bg-gray-50 rounded-lg'
            >
              <p className='text-sm font-medium text-gray-900 capitalize'>
                {type.type}
              </p>
              <p className='text-2xl font-bold text-blue-600'>
                ${type.totalCommissions.toFixed(2)}
              </p>
              <p className='text-sm text-gray-500'>
                {type.commissionCount} registros
              </p>
              <p className='text-xs text-gray-400'>
                {type.percentage.toFixed(1)}% del total
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CommissionSummary;
