import React from 'react';
import { render, screen } from '@testing-library/react';
import TopProductsWidget from '../TopProductsWidget';
import { useVendor } from '../../../hooks/useVendor';

// Mock del hook useVendor
jest.mock('../../../hooks/useVendor');
const mockUseVendor = useVendor as jest.MockedFunction<typeof useVendor>;

const mockTopProducts = [
  {
    id: "1",
    name: "Smartphone Pro Max",
    price: 899,
    thumbnail: "https://picsum.photos/64/64?random=1",
    salesCount: 150,
    category: "Electrónicos",
    rating: 4.8,
    rank: 1,
    salesGrowth: "+15%"
  },
  {
    id: "2",
    name: "Laptop Gaming RGB",
    price: 1299,
    thumbnail: "https://picsum.photos/64/64?random=2",
    salesCount: 89,
    category: "Computadoras",
    rating: 4.6,
    rank: 2,
    salesGrowth: "+8%"
  }
];

describe('TopProductsWidget', () => {
  beforeEach(() => {
    mockUseVendor.mockReturnValue({
      topProducts: mockTopProducts,
      vendorProfile: null,
      isLoading: false,
      error: null,
      metrics: {
        totalSales: 100,
        totalRevenue: 5000,
        totalCommissions: 500,
        activeProducts: 10,
        stockLevel: 50
      },
      storeName: 'Test Store',
      completionStatus: { isComplete: true, percentage: 100, missingFields: [] },
      businessSummary: { totalSales: 100, revenue: '$5,000', products: 10, growth: '+10%' },
      refreshMetrics: jest.fn(),
      loadVendorProfile: jest.fn(),
      updateVendorProfile: jest.fn()
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders widget title correctly', () => {
    render(<TopProductsWidget />);
    expect(screen.getByText('Productos Más Vendidos')).toBeInTheDocument();
  });

  test('displays correct number of products', () => {
    render(<TopProductsWidget maxProducts={2} />);
    expect(screen.getByText('Top 2')).toBeInTheDocument();
  });

  test('renders product information correctly', () => {
    render(<TopProductsWidget />);
    
    expect(screen.getByText('Smartphone Pro Max')).toBeInTheDocument();
    expect(screen.getByText('Laptop Gaming RGB')).toBeInTheDocument();
    expect(screen.getByText('Electrónicos')).toBeInTheDocument();
    expect(screen.getByText('Computadoras')).toBeInTheDocument();
  });

  test('displays sales count and growth correctly', () => {
    render(<TopProductsWidget />);
    
    expect(screen.getByText('150 ventas')).toBeInTheDocument();
    expect(screen.getByText('89 ventas')).toBeInTheDocument();
    expect(screen.getByText('+15%')).toBeInTheDocument();
    expect(screen.getByText('+8%')).toBeInTheDocument();
  });

  test('limits products displayed when maxProducts is set', () => {
    render(<TopProductsWidget maxProducts={1} />);
    
    expect(screen.getByText('Smartphone Pro Max')).toBeInTheDocument();
    expect(screen.queryByText('Laptop Gaming RGB')).not.toBeInTheDocument();
    expect(screen.getByText('Top 1')).toBeInTheDocument();
  });

  test('applies custom className correctly', () => {
    const { container } = render(<TopProductsWidget className="custom-class" />);
    const widget = container.firstChild as HTMLElement;
    
    expect(widget).toHaveClass('custom-class');
    expect(widget).toHaveClass('bg-white');
  });
});