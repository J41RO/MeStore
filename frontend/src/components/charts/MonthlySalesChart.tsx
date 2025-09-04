import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';

interface MonthlySalesData {
  month: string;
  sales: number;
  target: number;
}

interface MonthlySalesChartProps {
  data: MonthlySalesData[];
  title?: string;
  className?: string;
}

/**
 * Componente MonthlySalesChart - Gráfico de barras para comparaciones mensuales
 *
 * @param data - Array de datos mensuales con ventas y objetivos
 * @param title - Título opcional para el gráfico
 * @param className - Clases CSS adicionales
 */
const MonthlySalesChart: React.FC<MonthlySalesChartProps> = ({
  data,
  title = 'Ventas vs Objetivos Mensuales',
  className = '',
}) => {
  // Colores para las barras basados en performance
  const getBarColor = (sales: number, target: number) => {
    const percentage = (sales / target) * 100;
    if (percentage >= 100) return '#10b981'; // Verde - Objetivo cumplido
    if (percentage >= 80) return '#f59e0b'; // Amarillo - Cerca del objetivo
    return '#ef4444'; // Rojo - Lejos del objetivo
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {title && (
        <h3 className='text-lg font-semibold text-gray-800 mb-4'>{title}</h3>
      )}

      <div className='h-80 w-full'>
        <ResponsiveContainer width='100%' height='100%'>
          <BarChart
            data={data}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray='3 3' stroke='#f0f0f0' />
            <XAxis
              dataKey='month'
              stroke='#6b7280'
              fontSize={12}
              tickLine={false}
            />
            <YAxis
              stroke='#6b7280'
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              labelStyle={{ color: '#374151', fontWeight: 'bold' }}
              formatter={(value, name) => [
                value,
                name === 'sales' ? 'Ventas Reales' : 'Objetivo',
              ]}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar
              dataKey='target'
              fill='#e5e7eb'
              name='Objetivo'
              radius={[4, 4, 0, 0]}
            />
            <Bar dataKey='sales' name='Ventas Reales' radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={getBarColor(entry.sales, entry.target)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className='mt-4'>
        <div className='flex flex-wrap gap-4 text-sm'>
          <div className='flex items-center gap-2'>
            <div className='w-3 h-3 bg-green-500 rounded'></div>
            <span className='text-gray-600'>Objetivo cumplido (≥100%)</span>
          </div>
          <div className='flex items-center gap-2'>
            <div className='w-3 h-3 bg-yellow-500 rounded'></div>
            <span className='text-gray-600'>Cerca del objetivo (≥80%)</span>
          </div>
          <div className='flex items-center gap-2'>
            <div className='w-3 h-3 bg-red-500 rounded'></div>
            <span className='text-gray-600'>Necesita mejorar (&lt;80%)</span>
          </div>
        </div>
        <p className='text-sm text-gray-600 mt-2'>
          Comparación de ventas reales vs objetivos mensuales
        </p>
      </div>
    </div>
  );
};

export default MonthlySalesChart;
