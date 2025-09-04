import React from 'react';
import { render, screen } from '@testing-library/react';
import ProductCard from '../ProductCard';
import { TopProduct } from '../../../types/Product';

const mockProduct: TopProduct = {
  id: '1',
  name: 'Smartphone Pro Max',
  price: 899,
  thumbnail: 'https://picsum.photos/64/64?random=1',
  salesCount: 150,
  category: 'Electrónicos',
  rating: 4.8,
  rank: 1,
  salesGrowth: '+15%',
};

const mockProductNegativeGrowth: TopProduct = {
  id: '2',
  name: 'Tablet Basic',
  price: 299,
  thumbnail: 'https://picsum.photos/64/64?random=2',
  salesCount: 45,
  category: 'Tablets',
  rating: 3.5,
  rank: 5,
  salesGrowth: '-5%',
};

describe('ProductCard', () => {
  test('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} />);

    expect(screen.getByText('Smartphone Pro Max')).toBeInTheDocument();
    expect(screen.getByText('Electrónicos')).toBeInTheDocument();
    expect(screen.getByText('899,00 €')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('ventas')).toBeInTheDocument();
  });

  test('displays ranking badge correctly', () => {
    render(<ProductCard product={mockProduct} />);
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  test('displays sales growth correctly', () => {
    render(<ProductCard product={mockProduct} />);
    expect(screen.getByText('+15%')).toBeInTheDocument();
  });

  test('hides growth when showGrowth is false', () => {
    render(<ProductCard product={mockProduct} showGrowth={false} />);
    expect(screen.queryByText('+15%')).not.toBeInTheDocument();
  });

  test('shows negative growth with red styling', () => {
    render(<ProductCard product={mockProductNegativeGrowth} />);

    const growthElement = screen.getByText('-5%');
    expect(growthElement).toBeInTheDocument();
    expect(growthElement).toHaveClass('text-red-800');
  });

  test('shows positive growth with green styling', () => {
    render(<ProductCard product={mockProduct} />);

    const growthElement = screen.getByText('+15%');
    expect(growthElement).toBeInTheDocument();
    expect(growthElement).toHaveClass('text-green-800');
  });

  test('applies compact mode correctly', () => {
    const { container } = render(<ProductCard product={mockProduct} compact />);
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('p-3');
  });

  test('applies custom className correctly', () => {
    const { container } = render(
      <ProductCard product={mockProduct} className='custom-class' />
    );
    const cardElement = container.firstChild as HTMLElement;

    expect(cardElement).toHaveClass('custom-class');
    expect(cardElement).toHaveClass('bg-white');
  });
});
