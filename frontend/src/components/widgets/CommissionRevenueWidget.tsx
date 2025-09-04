import React, { useState, useEffect } from 'react';
import { CommissionType } from '../../types/commission.types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface CommissionRevenueData {
  period: string;
  actualRevenue: number;
  projectedRevenue: number;
  commissionRate: number;
  commissionType: CommissionType;
}

interface CommissionMetrics {
  totalActual: number;
  totalProjected: number;
  growthPercentage: number;
  averageRate: number;
}

interface CommissionRevenueWidgetProps {
  className?: string;
  timeframe?: 'week' | 'month' | 'quarter' | 'year';
  showProjections?: boolean;
}

const CommissionRevenueWidget: React.FC<CommissionRevenueWidgetProps> = ({
  className = '',
  timeframe = 'month',
  showProjections = true,
}) => {
  const [revenueData, setRevenueData] = useState<CommissionRevenueData[]>([]);
  const [metrics, setMetrics] = useState<CommissionMetrics>({
    totalActual: 0,
    totalProjected: 0,
    growthPercentage: 0,
    averageRate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCommissionData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulación de carga de datos
        await new Promise(resolve => setTimeout(resolve, 800));

        const mockData: CommissionRevenueData[] = [
          {
            period: 'Ene 2024',
            actualRevenue: 15420,
            projectedRevenue: 18500,
            commissionRate: 8.5,
            commissionType: CommissionType.SALE,
          },
          {
            period: 'Feb 2024',
            actualRevenue: 18750,
            projectedRevenue: 20200,
            commissionRate: 9.2,
            commissionType: CommissionType.PRODUCT,
          },
          {
            period: 'Mar 2024',
            actualRevenue: 22100,
            projectedRevenue: 24800,
            commissionRate: 8.8,
            commissionType: CommissionType.VOLUME,
          },
        ];

        // Cálculo de métricas
        const totalActual = mockData.reduce(
          (sum, item) => sum + item.actualRevenue,
          0
        );
        const totalProjected = mockData.reduce(
          (sum, item) => sum + item.projectedRevenue,
          0
        );
        const averageRate =
          mockData.reduce((sum, item) => sum + item.commissionRate, 0) /
          mockData.length;
        const growthPercentage =
          ((totalProjected - totalActual) / totalActual) * 100;

        setRevenueData(mockData);
        setMetrics({
          totalActual,
          totalProjected,
          growthPercentage,
          averageRate,
        });
      } catch (err) {
        setError('Error al cargar datos de comisiones');
      } finally {
        setLoading(false);
      }
    };

    loadCommissionData();
  }, [timeframe]);

  return (
    <div className={`bg-white p-6 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className='flex items-center justify-between mb-6'>
        <h3 className='text-lg font-semibold text-gray-900'>
          Ingresos por Comisiones
        </h3>
        <div className='text-sm text-gray-500'>
          {timeframe === 'week' && 'Esta Semana'}
          {timeframe === 'month' && 'Este Mes'}
          {timeframe === 'quarter' && 'Este Trimestre'}
          {timeframe === 'year' && 'Este Año'}
        </div>
      </div>

      {/* Estados de carga */}
      {loading ? (
        <div className='flex items-center justify-center py-8'>
          <div className='text-gray-500'>Cargando datos...</div>
        </div>
      ) : error ? (
        <div className='bg-red-50 border border-red-200 rounded-lg p-4 mb-4'>
          <p className='text-red-800 text-sm'>{error}</p>
        </div>
      ) : (
        <>
          {/* Tarjetas de métricas */}
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-6'>
            <div className='bg-blue-50 p-4 rounded-lg'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-blue-600'>
                    Total Actual
                  </p>
                  <p className='text-2xl font-bold text-blue-900'>
                    ${metrics.totalActual.toLocaleString()}
                  </p>
                </div>
                <div className='text-blue-500'>💰</div>
              </div>
            </div>

            <div className='bg-green-50 p-4 rounded-lg'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-green-600'>
                    Proyección Mensual
                  </p>
                  <p className='text-2xl font-bold text-green-900'>
                    ${metrics.totalProjected.toLocaleString()}
                  </p>
                </div>
                <div className='text-green-500'>📈</div>
              </div>
            </div>

            <div className='bg-purple-50 p-4 rounded-lg'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-purple-600'>
                    Crecimiento %
                  </p>
                  <p className='text-2xl font-bold text-purple-900'>
                    {metrics.growthPercentage > 0 ? '⬆️' : '⬇️'}
                    {Math.abs(metrics.growthPercentage).toFixed(1)}%
                  </p>
                </div>
                <div className='text-purple-500'>📊</div>
              </div>
            </div>
          </div>

          {/* Gráfico de Recharts */}
          <div className='mb-6'>
            <ResponsiveContainer width='100%' height={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray='3 3' />
                <XAxis dataKey='period' />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    `$${Number(value).toLocaleString()}`,
                    name === 'actualRevenue'
                      ? 'Ingresos Actuales'
                      : 'Proyección',
                  ]}
                />
                <Legend />
                <Line
                  type='monotone'
                  dataKey='actualRevenue'
                  stroke='#2563eb'
                  strokeWidth={3}
                  name='Ingresos Actuales'
                />
                {showProjections && (
                  <Line
                    type='monotone'
                    dataKey='projectedRevenue'
                    stroke='#10b981'
                    strokeWidth={2}
                    strokeDasharray='5 5'
                    name='Proyección'
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
};

export default React.memo(CommissionRevenueWidget);
