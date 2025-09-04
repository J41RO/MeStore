import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MonthlySalesChart from '../MonthlySalesChart';

// Mock de Recharts para testing
jest.mock('recharts', () => ({
  BarChart: ({ children }: any) => (
    <div data-testid='bar-chart'>{children}</div>
  ),
  Bar: () => <div data-testid='bar' />,
  XAxis: () => <div data-testid='x-axis' />,
  YAxis: () => <div data-testid='y-axis' />,
  CartesianGrid: () => <div data-testid='grid' />,
  Tooltip: () => <div data-testid='tooltip' />,
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid='responsive-container'>{children}</div>
  ),
  Legend: () => <div data-testid='legend' />,
  Cell: () => <div data-testid='cell' />,
}));

const mockData = [
  { month: 'Ene', sales: 125, target: 150 },
  { month: 'Feb', sales: 142, target: 150 },
  { month: 'Mar', sales: 108, target: 150 },
];

describe('MonthlySalesChart', () => {
  it('renders correctly with data', () => {
    render(<MonthlySalesChart data={mockData} />);

    expect(
      screen.getByText('Ventas vs Objetivos Mensuales')
    ).toBeInTheDocument();
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders legend indicators', () => {
    render(<MonthlySalesChart data={mockData} />);

    expect(screen.getByText('Objetivo cumplido (≥100%)')).toBeInTheDocument();
    expect(screen.getByText('Cerca del objetivo (≥80%)')).toBeInTheDocument();
    expect(screen.getByText('Necesita mejorar (<80%)')).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    const customTitle = 'Análisis Mensual';
    render(<MonthlySalesChart data={mockData} title={customTitle} />);

    expect(screen.getByText(customTitle)).toBeInTheDocument();
  });
});
