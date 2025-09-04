import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface SalesData {
  date: string;
  sales: number;
  revenue: number;
}

interface SalesChartProps {
  data: SalesData[];
  title?: string;
  className?: string;
}

/**
 * Componente SalesChart - Gráfico de líneas para tendencias de ventas
 *
 * @param data - Array de datos de ventas con fecha, ventas y revenue
 * @param title - Título opcional para el gráfico
 * @param className - Clases CSS adicionales
 */
const SalesChart: React.FC<SalesChartProps> = ({
  data,
  title = 'Tendencias de Ventas',
  className = '',
}) => {
  // Formatear datos para el gráfico
  const formattedData = data.map(item => ({
    ...item,
    // Formatear fecha para mejor visualización
    month: new Date(item.date + '-01').toLocaleDateString('es-ES', {
      month: 'short',
      year: '2-digit',
    }),
  }));

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {title && (
        <h3 className='text-lg font-semibold text-gray-800 mb-4'>{title}</h3>
      )}

      <div className='h-80 w-full'>
        <ResponsiveContainer width='100%' height='100%'>
          <LineChart
            data={formattedData}
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
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Line
              type='monotone'
              dataKey='sales'
              stroke='#3b82f6'
              strokeWidth={3}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              name='Ventas'
            />
            <Line
              type='monotone'
              dataKey='revenue'
              stroke='#10b981'
              strokeWidth={3}
              dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2 }}
              name='Ingresos'
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className='mt-4 text-sm text-gray-600'>
        <p>Tendencias de ventas e ingresos por mes</p>
      </div>
    </div>
  );
};

export default SalesChart;
