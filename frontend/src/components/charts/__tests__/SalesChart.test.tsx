import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SalesChart from '../SalesChart';

// Mock de Recharts para testing
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => (
    <div data-testid='line-chart'>{children}</div>
  ),
  Line: () => <div data-testid='line' />,
  XAxis: () => <div data-testid='x-axis' />,
  YAxis: () => <div data-testid='y-axis' />,
  CartesianGrid: () => <div data-testid='grid' />,
  Tooltip: () => <div data-testid='tooltip' />,
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid='responsive-container'>{children}</div>
  ),
  Legend: () => <div data-testid='legend' />,
}));

const mockData = [
  { date: '2024-01', sales: 125, revenue: 15600 },
  { date: '2024-02', sales: 142, revenue: 18400 },
  { date: '2024-03', sales: 108, revenue: 13200 },
];

describe('SalesChart', () => {
  it('renders correctly with data', () => {
    render(<SalesChart data={mockData} />);

    expect(screen.getByText('Tendencias de Ventas')).toBeInTheDocument();
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    const customTitle = 'Ventas Personalizadas';
    render(<SalesChart data={mockData} title={customTitle} />);

    expect(screen.getByText(customTitle)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <SalesChart data={mockData} className='custom-class' />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });
});
