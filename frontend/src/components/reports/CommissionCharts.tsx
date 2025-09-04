import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { CommissionBreakdown } from '../../types/commission.types';

interface CommissionChartsProps {
  breakdown: CommissionBreakdown;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const CommissionCharts: React.FC<CommissionChartsProps> = ({ breakdown }) => {
  // Preparar datos para gráfico de barras por categorías
  const categoryData = Object.entries(breakdown.byCategory).map(
    ([category, amount]) => ({
      name: category,
      amount: amount,
    })
  );

  // Preparar datos para gráfico de pie por tipos
  const typeData = breakdown.byType.map(item => ({
    name: item.type,
    value: item.totalCommissions,
    percentage: item.percentage,
  }));

  // Preparar datos para gráfico de tendencia por período
  const periodData = breakdown.byPeriod.map(item => ({
    period: item.period,
    commissions: item.totalCommissions,
    count: item.commissionCount,
  }));

  return (
    <div className='space-y-8'>
      <div>
        <h3 className='text-lg font-medium text-gray-900 mb-4'>
          Comisiones por Categoría
        </h3>
        <div className='h-80 w-full'>
          <ResponsiveContainer width='100%' height='100%'>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis
                dataKey='name'
                angle={-45}
                textAnchor='end'
                height={80}
                interval={0}
              />
              <YAxis />
              <Tooltip
                formatter={value => [
                  `$${Number(value).toFixed(2)}`,
                  'Comisiones',
                ]}
              />
              <Bar dataKey='amount' fill='#3B82F6' />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
        <div>
          <h3 className='text-lg font-medium text-gray-900 mb-4'>
            Distribución por Tipo
          </h3>
          <div className='h-64 w-full'>
            <ResponsiveContainer width='100%' height='100%'>
              <PieChart>
                <Pie
                  data={typeData}
                  cx='50%'
                  cy='50%'
                  labelLine={false}
                  label={({ name, percentage }) =>
                    `${name} (${percentage.toFixed(1)}%)`
                  }
                  outerRadius={80}
                  fill='#8884d8'
                  dataKey='value'
                >
                  {typeData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={value => [
                    `$${Number(value).toFixed(2)}`,
                    'Comisiones',
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div>
          <h3 className='text-lg font-medium text-gray-900 mb-4'>
            Tendencia por Período
          </h3>
          <div className='h-64 w-full'>
            <ResponsiveContainer width='100%' height='100%'>
              <BarChart data={periodData}>
                <CartesianGrid strokeDasharray='3 3' />
                <XAxis dataKey='period' />
                <YAxis />
                <Tooltip
                  formatter={value => [
                    `$${Number(value).toFixed(2)}`,
                    'Comisiones',
                  ]}
                />
                <Bar dataKey='commissions' fill='#10B981' />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className='bg-gray-50 p-4 rounded-lg'>
        <h4 className='text-md font-medium text-gray-900 mb-2'>
          Resumen de Gráficos
        </h4>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 text-sm'>
          <div>
            <p className='text-gray-600'>Categoría Principal:</p>
            <p className='font-semibold'>
              {breakdown.totals.topCategory || 'N/A'}
            </p>
          </div>
          <div>
            <p className='text-gray-600'>Producto Principal:</p>
            <p className='font-semibold'>
              {breakdown.totals.topProduct || 'N/A'}
            </p>
          </div>
          <div>
            <p className='text-gray-600'>Tasa Promedio:</p>
            <p className='font-semibold'>
              {(breakdown.totals.averageCommissionRate * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommissionCharts;
