import React from 'react';
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

// Interface para datos de crecimiento temporal
export interface GrowthData {
  month: string;
  currentPeriod: number;
  previousPeriod: number;
  growthRate: number;
}

export interface GrowthChartProps {
  data: GrowthData[];
  title?: string;
  height?: number;
}

const GrowthChart: React.FC<GrowthChartProps> = ({
  data,
  title = 'Gráfico de Crecimiento',
  height = 400,
}) => {
  // Calcular indicador de crecimiento general
  const totalGrowth = data.reduce((acc, item) => acc + item.growthRate, 0) / data.length;
  const isGrowthPositive = totalGrowth > 0;
  
  // Tooltip customizado con variación porcentual
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const currentValue = payload[0]?.value || 0;
      const previousValue = payload[1]?.value || 0;
      const variation = previousValue !== 0 ? ((currentValue - previousValue) / previousValue * 100) : 0;
      
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-medium">{label}</p>
          <p className="text-blue-600">Período Actual: {currentValue}</p>
          <p className="text-gray-600">Período Anterior: {previousValue}</p>
          <p className={variation >= 0 ? 'text-green-600' : 'text-red-600'}>
            Variación: {variation >= 0 ? '+' : ''}{variation.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          <span className="mr-1 text-green-600">
            {isGrowthPositive ? '↗' : '↘'}
          </span>
          {isGrowthPositive ? '+' : ''}{totalGrowth.toFixed(1)}% promedio
        </div>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="currentPeriod"
            stroke="#3B82F6"
            strokeWidth={2}
            name="Período Actual"
          />
          <Line
            type="monotone"
            dataKey="previousPeriod"
            stroke="#6B7280"
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Período Anterior"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default GrowthChart;