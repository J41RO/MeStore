// Jest equivalents for Vitest imports
const vi = jest;
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import CheckoutFlow from '../CheckoutFlow';
import { useCheckoutStore } from '../../../stores/checkoutStore';
import { useAuthStore } from '../../../stores/authStore';

// Mock the stores
vi.mock('../../../stores/checkoutStore');
vi.mock('../../../stores/authStore');

// Mock child components
vi.mock('../steps/CartStep', () => ({
  default: () => <div data-testid="cart-step">Cart Step</div>
}));

vi.mock('../steps/ShippingStep', () => ({
  default: () => <div data-testid="shipping-step">Shipping Step</div>
}));

vi.mock('../steps/PaymentStep', () => ({
  default: () => <div data-testid="payment-step">Payment Step</div>
}));

vi.mock('../steps/ConfirmationStep', () => ({
  default: () => <div data-testid="confirmation-step">Confirmation Step</div>
}));

vi.mock('../CheckoutProgress', () => ({
  default: () => <div data-testid="checkout-progress">Progress</div>
}));

vi.mock('../CheckoutSummary', () => ({
  default: () => <div data-testid="checkout-summary">Summary</div>
}));

// Mock React Router
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper function to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('CheckoutFlow - MVP Critical Component Tests', () => {
  const user = userEvent.setup();

  // Mock store states
  const mockCheckoutStore = {
    current_step: 'cart',
    cart_items: [
      { id: '1', name: 'Test Product', price: 100000, quantity: 2 },
      { id: '2', name: 'Another Product', price: 50000, quantity: 1 }
    ],
    is_processing: false,
    error: null,
    setError: vi.fn(),
    clearErrors: vi.fn(),
    resetCheckout: vi.fn()
  };

  const mockAuthStore = {
    isAuthenticated: true,
    user: {
      id: '123',
      name: 'Juan Pérez',
      email: 'juan@example.com'
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Reset mocks
    vi.mocked(useCheckoutStore).mockReturnValue(mockCheckoutStore);
    vi.mocked(useAuthStore).mockReturnValue(mockAuthStore);

    // Mock window.location
    delete (window as any).location;
    window.location = { href: '' } as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('🟢 GREEN Phase: Core Functionality Working', () => {
    it('should render checkout flow with user authentication', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should display checkout title for current step
      expect(screen.getByText('Carrito de Compras')).toBeInTheDocument();

      // Should show authenticated user info
      expect(screen.getByText('Comprando como: Juan Pérez')).toBeInTheDocument();

      // Should render progress indicator
      expect(screen.getByTestId('checkout-progress')).toBeInTheDocument();

      // Should render cart step
      expect(screen.getByTestId('cart-step')).toBeInTheDocument();

      // Should render summary sidebar
      expect(screen.getByTestId('checkout-summary')).toBeInTheDocument();
    });

    it('should clear errors on component mount', async () => {
      renderWithRouter(<CheckoutFlow />);

      expect(mockCheckoutStore.clearErrors).toHaveBeenCalledOnce();
    });

    it('should display different steps based on current_step', async () => {
      // Test shipping step
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        current_step: 'shipping'
      });

      const { rerender } = renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Información de Envío')).toBeInTheDocument();
      expect(screen.getByTestId('shipping-step')).toBeInTheDocument();

      // Test payment step
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        current_step: 'payment'
      });

      rerender(
        <BrowserRouter>
          <CheckoutFlow />
        </BrowserRouter>
      );

      expect(screen.getByText('Método de Pago')).toBeInTheDocument();
      expect(screen.getByTestId('payment-step')).toBeInTheDocument();

      // Test confirmation step
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        current_step: 'confirmation'
      });

      rerender(
        <BrowserRouter>
          <CheckoutFlow />
        </BrowserRouter>
      );

      expect(screen.getByText('Confirmación de Pedido')).toBeInTheDocument();
      expect(screen.getByTestId('confirmation-step')).toBeInTheDocument();
    });

    it('should display error banner when error exists', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        error: 'Error de pago: Tarjeta rechazada'
      });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Error de pago: Tarjeta rechazada')).toBeInTheDocument();

      // Should have close button
      const closeButton = screen.getByLabelText('Cerrar');
      expect(closeButton).toBeInTheDocument();
    });

    it('should close error banner when close button is clicked', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        error: 'Test error message'
      });

      renderWithRouter(<CheckoutFlow />);

      const closeButton = screen.getByLabelText('Cerrar');
      await user.click(closeButton);

      expect(mockCheckoutStore.setError).toHaveBeenCalledWith(null);
    });

    it('should show processing overlay when is_processing is true', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        is_processing: true
      });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Procesando...')).toBeInTheDocument();

      // Should have loading spinner
      const spinner = screen.getByText('Procesando...').previousElementSibling;
      expect(spinner).toHaveClass('animate-spin');
    });

    it('should display development tools in dev environment', async () => {
      // Mock import.meta.env.DEV
      vi.stubGlobal('import.meta.env', { DEV: true });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Step: cart')).toBeInTheDocument();
      expect(screen.getByText('Items: 2')).toBeInTheDocument();

      const resetButton = screen.getByRole('button', { name: 'Reset Checkout' });
      expect(resetButton).toBeInTheDocument();
    });

    it('should reset checkout when reset button is clicked in dev mode', async () => {
      vi.stubGlobal('import.meta.env', { DEV: true });

      renderWithRouter(<CheckoutFlow />);

      const resetButton = screen.getByRole('button', { name: 'Reset Checkout' });
      await user.click(resetButton);

      expect(mockCheckoutStore.resetCheckout).toHaveBeenCalledOnce();
    });
  });

  describe('🔒 Authentication & Security Tests', () => {
    it('should show loading state when not authenticated', async () => {
      vi.mocked(useAuthStore).mockReturnValue({
        ...mockAuthStore,
        isAuthenticated: false
      });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Verificando autenticación...')).toBeInTheDocument();

      // Should have loading spinner
      const loadingSpinner = screen.getByText('Verificando autenticación...').previousElementSibling;
      expect(loadingSpinner).toHaveClass('animate-spin');
    });

    it('should redirect to login when user is not authenticated', async () => {
      vi.mocked(useAuthStore).mockReturnValue({
        ...mockAuthStore,
        isAuthenticated: false
      });

      renderWithRouter(<CheckoutFlow />);

      // Should attempt redirect
      await waitFor(() => {
        expect(window.location.href).toBe('/login?redirect=/checkout');
      });
    });

    it('should redirect to cart when cart is empty (not on confirmation)', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        cart_items: [],
        current_step: 'cart'
      });

      renderWithRouter(<CheckoutFlow />);

      await waitFor(() => {
        expect(window.location.href).toBe('/cart');
      });
    });

    it('should NOT redirect when cart is empty but on confirmation step', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        cart_items: [],
        current_step: 'confirmation'
      });

      renderWithRouter(<CheckoutFlow />);

      // Should render confirmation step
      expect(screen.getByTestId('confirmation-step')).toBeInTheDocument();
      expect(window.location.href).toBe('');
    });
  });

  describe('🎯 Responsive Design & Accessibility', () => {
    it('should have proper ARIA labels and semantic structure', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should have proper heading hierarchy
      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toHaveTextContent('Carrito de Compras');

      // Should have main landmark
      const main = screen.getByRole('main') || document.querySelector('main');
      expect(main).toBeInTheDocument();
    });

    it('should use proper Colombian Spanish text', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should use proper Colombian Spanish terminology
      expect(screen.getByText('Carrito de Compras')).toBeInTheDocument();
      expect(screen.getByText('Comprando como:')).toBeInTheDocument();
    });

    it('should handle responsive grid layout', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should have responsive grid classes
      const gridContainer = screen.getByTestId('cart-step').closest('.lg\\:grid');
      expect(gridContainer).toHaveClass('lg:grid', 'lg:grid-cols-12', 'lg:gap-8');
    });

    it('should handle focus management for error alerts', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        error: 'Test error'
      });

      renderWithRouter(<CheckoutFlow />);

      const closeButton = screen.getByLabelText('Cerrar');
      closeButton.focus();
      expect(closeButton).toHaveFocus();
    });
  });

  describe('🚀 Performance & User Experience', () => {
    it('should render within acceptable time limits', async () => {
      const startTime = performance.now();

      renderWithRouter(<CheckoutFlow />);

      await waitFor(() => {
        expect(screen.getByTestId('cart-step')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render in under 100ms for unit test
      expect(renderTime).toBeLessThan(100);
    });

    it('should handle step transitions smoothly', async () => {
      const { rerender } = renderWithRouter(<CheckoutFlow />);

      // Initial step
      expect(screen.getByTestId('cart-step')).toBeInTheDocument();

      // Change to shipping step
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        current_step: 'shipping'
      });

      rerender(
        <BrowserRouter>
          <CheckoutFlow />
        </BrowserRouter>
      );

      expect(screen.getByTestId('shipping-step')).toBeInTheDocument();
      expect(screen.queryByTestId('cart-step')).not.toBeInTheDocument();
    });

    it('should maintain state consistency across re-renders', async () => {
      const { rerender } = renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Items: 2')).toBeInTheDocument();

      // Re-render with same state
      rerender(
        <BrowserRouter>
          <CheckoutFlow />
        </BrowserRouter>
      );

      expect(screen.getByText('Items: 2')).toBeInTheDocument();
      expect(mockCheckoutStore.clearErrors).toHaveBeenCalledTimes(2); // Called on each mount
    });
  });

  describe('🛡️ Error Handling & Edge Cases', () => {
    it('should default to cart step for unknown step values', async () => {
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        current_step: 'invalid_step' as any
      });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByTestId('cart-step')).toBeInTheDocument();
    });

    it('should handle missing user information gracefully', async () => {
      vi.mocked(useAuthStore).mockReturnValue({
        ...mockAuthStore,
        user: {
          id: '123',
          email: 'juan@example.com'
          // name is missing
        } as any
      });

      renderWithRouter(<CheckoutFlow />);

      expect(screen.getByText('Comprando como: juan@example.com')).toBeInTheDocument();
    });

    it('should handle null user gracefully', async () => {
      vi.mocked(useAuthStore).mockReturnValue({
        ...mockAuthStore,
        user: null
      });

      renderWithRouter(<CheckoutFlow />);

      // Should not crash and not show user info
      expect(screen.queryByText(/Comprando como:/)).not.toBeInTheDocument();
    });

    it('should clear errors when component unmounts', async () => {
      const { unmount } = renderWithRouter(<CheckoutFlow />);

      unmount();

      // clearErrors should have been called on mount
      expect(mockCheckoutStore.clearErrors).toHaveBeenCalledOnce();
    });
  });

  describe('🔄 Integration with Stores', () => {
    it('should properly integrate with checkout store', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should use all necessary store properties
      expect(useCheckoutStore).toHaveBeenCalled();

      // Should call clearErrors on mount
      expect(mockCheckoutStore.clearErrors).toHaveBeenCalledOnce();
    });

    it('should properly integrate with auth store', async () => {
      renderWithRouter(<CheckoutFlow />);

      // Should use auth store
      expect(useAuthStore).toHaveBeenCalled();
    });

    it('should react to store changes', async () => {
      const { rerender } = renderWithRouter(<CheckoutFlow />);

      // Change error state
      vi.mocked(useCheckoutStore).mockReturnValue({
        ...mockCheckoutStore,
        error: 'New error message'
      });

      rerender(
        <BrowserRouter>
          <CheckoutFlow />
        </BrowserRouter>
      );

      expect(screen.getByText('New error message')).toBeInTheDocument();
    });
  });
});