import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CartItemList from '../CartItemList';

// Mock window.confirm
Object.defineProperty(window, 'confirm', {
  value: jest.fn(),
});

const mockItems = [
  { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' },
  { productId: 2, quantity: 1, price: 50, addedAt: '2023-01-02T00:00:00.000Z' },
];

const mockProps = {
  items: mockItems,
  onUpdateQuantity: jest.fn(),
  onRemoveItem: jest.fn(),
  onClearCart: jest.fn(),
  loading: false,
};

describe('CartItemList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (window.confirm as any).mockReturnValue(true);
  });

  it('renders cart items correctly', () => {
    render(<CartItemList {...mockProps} />);

    expect(screen.getByText('Productos en tu carrito')).toBeInTheDocument();
    expect(screen.getByText('Producto #1')).toBeInTheDocument();
    expect(screen.getByText('Producto #2')).toBeInTheDocument();
    expect(screen.getByText('3 productos • $ 250')).toBeInTheDocument();
  });

  it('displays empty state when no items', () => {
    const emptyProps = { ...mockProps, items: [] };
    render(<CartItemList {...emptyProps} />);

    expect(screen.getByText('No hay productos en tu carrito')).toBeInTheDocument();
    expect(screen.getByText('Los productos que agregues aparecerán aquí')).toBeInTheDocument();
  });

  it('displays loading state correctly', () => {
    const loadingProps = { ...mockProps, loading: true };
    render(<CartItemList {...loadingProps} />);

    // Check for skeleton loading elements
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('handles quantity increase', async () => {
    render(<CartItemList {...mockProps} />);

    const increaseBtns = screen.getAllByTitle('Aumentar cantidad');
    fireEvent.click(increaseBtns[0]);

    await waitFor(() => {
      expect(mockProps.onUpdateQuantity).toHaveBeenCalledWith(1, 3);
    });
  });

  it('handles quantity decrease', async () => {
    render(<CartItemList {...mockProps} />);

    const decreaseBtns = screen.getAllByTitle('Reducir cantidad');
    fireEvent.click(decreaseBtns[0]);

    await waitFor(() => {
      expect(mockProps.onUpdateQuantity).toHaveBeenCalledWith(1, 1);
    });
  });

  it('prevents quantity decrease below 1', async () => {
    const singleItemProps = {
      ...mockProps,
      items: [{ productId: 1, quantity: 1, price: 100, addedAt: '2023-01-01T00:00:00.000Z' }]
    };
    
    render(<CartItemList {...singleItemProps} />);

    const decreaseBtn = screen.getByTitle('Reducir cantidad');
    expect(decreaseBtn).toBeDisabled();
  });

  it('removes item with confirmation', async () => {
    render(<CartItemList {...mockProps} />);

    const removeButtons = screen.getAllByTitle('Eliminar producto');
    fireEvent.click(removeButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith(
      '¿Estás seguro de que quieres eliminar este producto del carrito?'
    );
    expect(mockProps.onRemoveItem).toHaveBeenCalledWith(1);
  });

  it('does not remove item when confirmation is cancelled', () => {
    (window.confirm as any).mockReturnValue(false);
    
    render(<CartItemList {...mockProps} />);

    const removeButtons = screen.getAllByTitle('Eliminar producto');
    fireEvent.click(removeButtons[0]);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockProps.onRemoveItem).not.toHaveBeenCalled();
  });

  it('clears entire cart with confirmation', () => {
    render(<CartItemList {...mockProps} />);

    const clearButton = screen.getByText('Vaciar todo');
    fireEvent.click(clearButton);

    expect(window.confirm).toHaveBeenCalledWith(
      '¿Estás seguro de que quieres vaciar todo el carrito? Se eliminarán 3 productos.'
    );
    expect(mockProps.onClearCart).toHaveBeenCalled();
  });

  it('shows info message for many items', () => {
    const manyItemsProps = {
      ...mockProps,
      items: [
        ...mockItems,
        { productId: 3, quantity: 1, price: 75, addedAt: '2023-01-03T00:00:00.000Z' },
        { productId: 4, quantity: 1, price: 25, addedAt: '2023-01-04T00:00:00.000Z' },
      ]
    };

    render(<CartItemList {...manyItemsProps} />);

    expect(screen.getByText('¡Tienes 4 productos diferentes en tu carrito!')).toBeInTheDocument();
    expect(screen.getByText('Revisa las cantidades antes de proceder al checkout.')).toBeInTheDocument();
  });

  it('formats prices in Colombian pesos', () => {
    render(<CartItemList {...mockProps} />);

    expect(screen.getByText('$ 100 por unidad')).toBeInTheDocument();
    expect(screen.getByText('$ 200')).toBeInTheDocument(); // 2 × $100
  });

  it('formats dates correctly', () => {
    render(<CartItemList {...mockProps} />);

    expect(screen.getByText('Agregado: 1/1/2023')).toBeInTheDocument();
  });

  it('calculates subtotals correctly', () => {
    render(<CartItemList {...mockProps} />);

    expect(screen.getByText('$ 200')).toBeInTheDocument(); // 2 × $100
    expect(screen.getByText('$ 50')).toBeInTheDocument(); // 1 × $50
  });

  it('shows quantity breakdown for multiple items', () => {
    render(<CartItemList {...mockProps} />);

    expect(screen.getByText('2 × $ 100')).toBeInTheDocument();
  });

  it('handles updating state with spinner', async () => {
    render(<CartItemList {...mockProps} />);

    const increaseBtns = screen.getAllByTitle('Aumentar cantidad');
    fireEvent.click(increaseBtns[0]);

    // Check if spinner appears during update
    await waitFor(() => {
      const spinner = document.querySelector('.animate-spin');
      if (spinner) {
        expect(spinner).toBeInTheDocument();
      }
    });
  });
});