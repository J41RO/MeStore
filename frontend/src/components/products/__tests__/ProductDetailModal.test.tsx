import { render, screen, fireEvent } from '@testing-library/react';
import ProductDetailModal from '../../ProductDetailModal';
import { Product } from '../../../types/api.types';

const mockProduct: Product = {
  id: '1',
  name: 'Producto de Prueba',
  description: 'Descripción del producto de prueba',
  price: 29.99,
  stock: 10,
  category: 'Electrónicos',
  imageUrl: 'https://example.com/image.jpg',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-15T00:00:00Z'
};

describe('ProductDetailModal', () => {
  const mockOnClose = jest.fn();
  const mockOnEdit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders modal when isOpen is true', () => {
    render(
      <ProductDetailModal
        isOpen={true}
        onClose={mockOnClose}
        product={mockProduct}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Detalles del Producto')).toBeInTheDocument();
    expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
  });

  test('does not render when isOpen is false', () => {
    render(
      <ProductDetailModal
        isOpen={false}
        onClose={mockOnClose}
        product={mockProduct}
      />
    );

    expect(screen.queryByText('Detalles del Producto')).not.toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', () => {
    render(
      <ProductDetailModal
        isOpen={true}
        onClose={mockOnClose}
        product={mockProduct}
      />
    );

    const closeButton = screen.getByLabelText('Cerrar modal');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('calls onEdit when edit button is clicked', () => {
    render(
      <ProductDetailModal
        isOpen={true}
        onClose={mockOnClose}
        product={mockProduct}
        onEdit={mockOnEdit}
      />
    );

    const editButton = screen.getByText('Editar');
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledTimes(1);
  });

  test('displays product information correctly', () => {
    render(
      <ProductDetailModal
        isOpen={true}
        onClose={mockOnClose}
        product={mockProduct}
      />
    );

    expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
    expect(screen.getByText('Descripción del producto de prueba')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByText('10 unidades')).toBeInTheDocument();
    expect(screen.getByText('Electrónicos')).toBeInTheDocument();
  });
});
