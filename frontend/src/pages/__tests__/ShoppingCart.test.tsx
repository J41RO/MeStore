import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ShoppingCart from '../ShoppingCart';

// Mock MarketplaceLayout
jest.mock('../../components/marketplace/MarketplaceLayout', () => {
  return function MockMarketplaceLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="marketplace-layout">{children}</div>;
  };
});

// Mock CartItemList
jest.mock('../../components/marketplace/CartItemList', () => {
  return function MockCartItemList({ items, onUpdateQuantity, onRemoveItem, onClearCart }: any) {
    return (
      <div data-testid="cart-item-list">
        <div>Items count: {items.length}</div>
        <button onClick={() => onUpdateQuantity(1, 2)} data-testid="update-quantity">Update Quantity</button>
        <button onClick={() => onRemoveItem(1)} data-testid="remove-item">Remove Item</button>
        <button onClick={onClearCart} data-testid="clear-cart">Clear Cart</button>
      </div>
    );
  };
});

// Mock CartSummary
jest.mock('../../components/marketplace/CartSummary', () => {
  return function MockCartSummary({ items, onProceedToCheckout }: any) {
    return (
      <div data-testid="cart-summary">
        <div>Summary items: {items.length}</div>
        <button onClick={onProceedToCheckout} data-testid="checkout-button">Checkout</button>
      </div>
    );
  };
});

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock window.alert
Object.defineProperty(window, 'alert', {
  value: jest.fn(),
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ShoppingCart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders the shopping cart page correctly', async () => {
    mockLocalStorage.getItem.mockReturnValue('[]');

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      expect(screen.getByTestId('marketplace-layout')).toBeInTheDocument();
      expect(screen.getByText('Mi Carrito')).toBeInTheDocument();
    });
  });

  it('loads cart items from localStorage on mount', async () => {
    const mockCartData = JSON.stringify([
      { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' }
    ]);
    mockLocalStorage.getItem.mockReturnValue(mockCartData);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('mestore_cart');
      expect(screen.getByText('Items count: 1')).toBeInTheDocument();
    });
  });

  it('displays empty cart message when no items', async () => {
    mockLocalStorage.getItem.mockReturnValue(null);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      expect(screen.getByText('Tu carrito está vacío')).toBeInTheDocument();
      expect(screen.getByText('Explorar productos')).toBeInTheDocument();
    });
  });

  it('updates cart quantity correctly', async () => {
    const mockCartData = JSON.stringify([
      { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' }
    ]);
    mockLocalStorage.getItem.mockReturnValue(mockCartData);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      const updateButton = screen.getByTestId('update-quantity');
      fireEvent.click(updateButton);
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'mestore_cart',
        expect.stringContaining('"quantity":2')
      );
    });
  });

  it('removes item from cart correctly', async () => {
    const mockCartData = JSON.stringify([
      { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' },
      { productId: 2, quantity: 1, price: 50, addedAt: '2023-01-01T00:00:00.000Z' }
    ]);
    mockLocalStorage.getItem.mockReturnValue(mockCartData);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      const removeButton = screen.getByTestId('remove-item');
      fireEvent.click(removeButton);
      
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
    });
  });

  it('clears cart correctly', async () => {
    const mockCartData = JSON.stringify([
      { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' }
    ]);
    mockLocalStorage.getItem.mockReturnValue(mockCartData);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      const clearButton = screen.getByTestId('clear-cart');
      fireEvent.click(clearButton);
      
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('mestore_cart');
    });
  });

  it('handles checkout process', async () => {
    const mockCartData = JSON.stringify([
      { productId: 1, quantity: 2, price: 100, addedAt: '2023-01-01T00:00:00.000Z' }
    ]);
    mockLocalStorage.getItem.mockReturnValue(mockCartData);

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      const checkoutButton = screen.getByTestId('checkout-button');
      fireEvent.click(checkoutButton);
      
      expect(window.alert).toHaveBeenCalledWith(
        expect.stringContaining('Funcionalidad de checkout en desarrollo')
      );
    });
  });

  it('handles localStorage errors gracefully', async () => {
    mockLocalStorage.getItem.mockImplementation(() => {
      throw new Error('localStorage error');
    });

    renderWithRouter(<ShoppingCart />);

    await waitFor(() => {
      expect(screen.getByText('Error al cargar el carrito. Por favor, recarga la página.')).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    mockLocalStorage.getItem.mockReturnValue('[]');

    renderWithRouter(<ShoppingCart />);

    expect(screen.getByTestId('marketplace-layout')).toBeInTheDocument();
  });
});