import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddToCartButton from './AddToCartButton';

const mockOnAddToCart = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  
  return {
    getItem: (key: string) => {
      return store[key] || null;
    },
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('AddToCartButton', () => {
  beforeEach(() => {
    mockOnAddToCart.mockClear();
    localStorage.clear();
  });

  it('renders with default quantity', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('Agregar al carrito')).toBeInTheDocument();
    expect(screen.getByText('10 unidades disponibles')).toBeInTheDocument();
  });

  it('displays formatted price', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText(/50\.000/)).toBeInTheDocument();
  });

  it('handles quantity changes', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    const buttons = screen.getAllByRole('button');
    const minusButton = buttons[0]; // First button is minus
    const plusButton = buttons[1]; // Second button is plus
    
    // Increase quantity
    fireEvent.click(plusButton);
    expect(screen.getByText('2')).toBeInTheDocument();
    
    // Decrease quantity
    fireEvent.click(minusButton);
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('prevents quantity below 1', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    const minusButton = screen.getAllByRole('button')[0]; // First button is minus
    expect(minusButton).toBeDisabled();
  });

  it('prevents quantity above stock', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={2}
        onAddToCart={mockOnAddToCart}
      />
    );

    const plusButton = screen.getAllByRole('button')[1]; // Second button is plus
    
    // Increase to max stock
    fireEvent.click(plusButton);
    expect(screen.getByText('2')).toBeInTheDocument();
    
    // Button should be disabled at max stock
    expect(plusButton).toBeDisabled();
  });

  it('adds product to cart', async () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    const addButton = screen.getByText('Agregar al carrito');
    fireEvent.click(addButton);

    // Should show loading state
    expect(screen.getByText('Agregando...')).toBeInTheDocument();

    // Wait for add to complete
    await waitFor(() => {
      expect(screen.getByText('¡Agregado al carrito!')).toBeInTheDocument();
    });

    // Should call callback
    expect(mockOnAddToCart).toHaveBeenCalledWith(1);
    
    // Should save to localStorage
    const cartData = JSON.parse(localStorage.getItem('mestore_cart') || '[]');
    expect(cartData).toHaveLength(1);
    expect(cartData[0]).toEqual(expect.objectContaining({
      productId: 1,
      quantity: 1,
      price: 50000
    }));
  });

  it('shows out of stock state', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={0}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Producto agotado')).toBeInTheDocument();
    expect(screen.getByText('No hay stock disponible')).toBeInTheDocument();
  });

  it('shows disabled state', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
        disabled={true}
      />
    );

    expect(screen.getByText('Producto agotado')).toBeInTheDocument();
  });

  it('handles existing cart items', () => {
    // Pre-populate cart
    const existingCart = [{
      productId: 1,
      quantity: 3,
      price: 50000,
      addedAt: new Date().toISOString()
    }];
    localStorage.setItem('mestore_cart', JSON.stringify(existingCart));

    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Ya tienes 3 unidades en tu carrito')).toBeInTheDocument();
    expect(screen.getByText('7 unidades disponibles')).toBeInTheDocument();
  });

  it('shows already in cart state when all stock is in cart', () => {
    // Pre-populate cart with all available stock
    const existingCart = [{
      productId: 1,
      quantity: 5,
      price: 50000,
      addedAt: new Date().toISOString()
    }];
    localStorage.setItem('mestore_cart', JSON.stringify(existingCart));

    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={5}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Ya en tu carrito')).toBeInTheDocument();
    expect(screen.getByText('5 unidades agregadas')).toBeInTheDocument();
  });

  it('shows buy now button', () => {
    render(
      <AddToCartButton
        productId={1}
        price={50000}
        stock={10}
        onAddToCart={mockOnAddToCart}
      />
    );

    expect(screen.getByText('Comprar ahora')).toBeInTheDocument();
  });
});