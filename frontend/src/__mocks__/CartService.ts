// Mock Cart Service for tests
// Prevents real cart operations and localStorage access during testing

export interface CartItem {
  id: string;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
  sku: string;
  vendor_id?: string;
  vendor_name?: string;
  stock_available?: number;
  variant_attributes?: Record<string, any>;
}

export interface CartTotals {
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  total: number;
}

export interface OrderValidation {
  valid: boolean;
  message?: string;
}

class MockCartService {
  private mockCart: CartItem[] = [];

  // Cart calculation methods
  calculateCartTotals = jest.fn().mockImplementation((
    cartItems: CartItem[],
    shippingCost: number = 0
  ): CartTotals => {
    const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax_amount = Math.round(subtotal * 0.19); // 19% Colombian VAT
    const total = subtotal + tax_amount + shippingCost;

    return {
      subtotal,
      tax_amount,
      shipping_cost: shippingCost,
      total,
    };
  });

  // Validation methods
  validateMinimumOrder = jest.fn().mockImplementation((cartItems: CartItem[]): OrderValidation => {
    const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const minimumOrderAmount = 50000; // 50,000 COP

    if (subtotal < minimumOrderAmount) {
      return {
        valid: false,
        message: `Pedido mínimo de $${minimumOrderAmount.toLocaleString('es-CO')} COP`,
      };
    }

    return { valid: true };
  });

  // Cart item management
  addToCart = jest.fn().mockImplementation((item: CartItem) => {
    const existingIndex = this.mockCart.findIndex(cartItem => cartItem.product_id === item.product_id);

    if (existingIndex > -1) {
      this.mockCart[existingIndex].quantity += item.quantity;
    } else {
      this.mockCart.push({ ...item, id: `cart-${Date.now()}` });
    }

    return this.mockCart;
  });

  removeFromCart = jest.fn().mockImplementation((productId: string) => {
    this.mockCart = this.mockCart.filter(item => item.product_id !== productId);
    return this.mockCart;
  });

  updateQuantity = jest.fn().mockImplementation((productId: string, quantity: number) => {
    const item = this.mockCart.find(item => item.product_id === productId);
    if (item) {
      item.quantity = quantity;
      if (quantity <= 0) {
        this.removeFromCart(productId);
      }
    }
    return this.mockCart;
  });

  clearCart = jest.fn().mockImplementation(() => {
    this.mockCart = [];
    return this.mockCart;
  });

  // Storage methods (mocked)
  saveCartToStorage = jest.fn().mockImplementation((cartItems: CartItem[]) => {
    this.mockCart = [...cartItems];
  });

  loadCartFromStorage = jest.fn().mockImplementation((): CartItem[] => {
    return [...this.mockCart];
  });

  // Utility methods
  isProductInCart = jest.fn().mockImplementation((cartItems: CartItem[], productId: string): boolean => {
    return cartItems.some(item => item.product_id === productId);
  });

  getCartItemCount = jest.fn().mockImplementation((cartItems: CartItem[]): number => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  });

  // Static formatting methods
  static formatCurrency = jest.fn().mockImplementation((amount: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(amount);
  });

  static calculateItemTotal = jest.fn().mockImplementation((item: CartItem): number => {
    return item.price * item.quantity;
  });

  // Stock validation
  validateStock = jest.fn().mockImplementation((cartItems: CartItem[]): boolean => {
    return cartItems.every(item =>
      !item.stock_available || item.quantity <= item.stock_available
    );
  });

  getOutOfStockItems = jest.fn().mockImplementation((cartItems: CartItem[]): CartItem[] => {
    return cartItems.filter(item =>
      item.stock_available && item.quantity > item.stock_available
    );
  });

  // Mock helpers for testing
  setMockCart(cartItems: CartItem[]) {
    this.mockCart = [...cartItems];
  }

  getMockCart(): CartItem[] {
    return [...this.mockCart];
  }

  resetMock() {
    this.mockCart = [];
    jest.clearAllMocks();
  }
}

// Create singleton instance
const mockCartService = new MockCartService();

// Export the mock service
export const cartService = mockCartService;
export { MockCartService };
export default mockCartService;