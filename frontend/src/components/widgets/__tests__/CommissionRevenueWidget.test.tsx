import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CommissionRevenueWidget from '../CommissionRevenueWidget';

// Mock de recharts para tests
jest.mock('recharts', () => ({
  LineChart: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid='line-chart'>{children}</div>
  ),
  Line: () => <div data-testid='line' />,
  XAxis: () => <div data-testid='x-axis' />,
  YAxis: () => <div data-testid='y-axis' />,
  CartesianGrid: () => <div data-testid='grid' />,
  Tooltip: () => <div data-testid='tooltip' />,
  Legend: () => <div data-testid='legend' />,
  ResponsiveContainer: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid='responsive-container'>{children}</div>
  ),
}));

describe('CommissionRevenueWidget', () => {
  it('renders without errors', () => {
    render(<CommissionRevenueWidget />);
    expect(screen.getByText('Ingresos por Comisiones')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<CommissionRevenueWidget />);
    expect(screen.getByText('Cargando datos...')).toBeInTheDocument();
  });

  it('displays correct timeframe text', () => {
    render(<CommissionRevenueWidget timeframe='week' />);
    expect(screen.getByText('Esta Semana')).toBeInTheDocument();
  });

  it('shows metrics after loading', async () => {
    render(<CommissionRevenueWidget />);

    await waitFor(
      () => {
        expect(screen.getByText('Total Actual')).toBeInTheDocument();
        expect(screen.getByText('Proyección Mensual')).toBeInTheDocument();
        expect(screen.getByText('Crecimiento %')).toBeInTheDocument();
      },
      { timeout: 1000 }
    );
  });

  it('renders chart components after loading', async () => {
    render(<CommissionRevenueWidget />);

    await waitFor(
      () => {
        expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
        expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      },
      { timeout: 1000 }
    );
  });
});
