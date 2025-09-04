import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Interface para datos comparativos mensuales
export interface MonthlyComparisonData {
  month: string;
  currentPeriod: number;
  previousPeriod: number;
  category: string;
}

export interface MonthlyComparisonChartProps {
  data: MonthlyComparisonData[];
  title?: string;
  height?: number;
}

const MonthlyComparisonChart: React.FC<MonthlyComparisonChartProps> = ({
  data,
  title = 'Comparativa Mensual',
  height = 400,
}) => {
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar
            dataKey="currentPeriod"
            fill="#3B82F6"
            name="Período Actual"
          />
          <Bar
            dataKey="previousPeriod"
            fill="#9CA3AF"
            name="Período Anterior"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MonthlyComparisonChart;