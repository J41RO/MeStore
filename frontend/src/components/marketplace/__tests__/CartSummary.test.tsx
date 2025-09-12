import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CartSummary from '../CartSummary';

const mockItems = [
  { productId: 1, quantity: 2, price: 50000, addedAt: '2023-01-01T00:00:00.000Z' },
  { productId: 2, quantity: 1, price: 30000, addedAt: '2023-01-02T00:00:00.000Z' },
];

const mockProps = {
  items: mockItems,
  onProceedToCheckout: jest.fn(),
  loading: false,
};

describe('CartSummary', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders cart summary correctly', () => {
    render(<CartSummary {...mockProps} />);

    expect(screen.getByText('Resumen del pedido')).toBeInTheDocument();
    expect(screen.getByText('Subtotal (3 productos)')).toBeInTheDocument();
    expect(screen.getByText('$130.000')).toBeInTheDocument(); // Subtotal
  });

  it('calculates tax correctly (19% IVA)', () => {
    render(<CartSummary {...mockProps} />);

    // Subtotal: 130000, Tax: 130000 * 0.19 = 24700
    expect(screen.getByText('IVA (19%)')).toBeInTheDocument();
    expect(screen.getByText('$24.700')).toBeInTheDocument();
  });

  it('shows shipping cost when below free shipping threshold', () => {
    render(<CartSummary {...mockProps} />);

    expect(screen.getByText('Envío')).toBeInTheDocument();
    expect(screen.getByText('$15.000')).toBeInTheDocument(); // Base shipping cost
  });

  it('shows free shipping when above threshold', () => {
    const highValueItems = [
      { productId: 1, quantity: 2, price: 60000, addedAt: '2023-01-01T00:00:00.000Z' },
    ];
    const freeShippingProps = { ...mockProps, items: highValueItems };

    render(<CartSummary {...freeShippingProps} />);

    expect(screen.getByText('GRATIS')).toBeInTheDocument();
    expect(screen.getByText('$0')).toBeInTheDocument(); // Free shipping
  });

  it('calculates total correctly with shipping', () => {
    render(<CartSummary {...mockProps} />);

    // Subtotal: 130000, Tax: 24700, Shipping: 15000 = Total: 169700
    expect(screen.getByText('$169.700')).toBeInTheDocument();
  });

  it('shows free shipping progress bar', () => {
    render(<CartSummary {...mockProps} />);

    expect(screen.getByText(/¡Envío GRATIS comprando/)).toBeInTheDocument();
    expect(document.querySelector('.bg-blue-600')).toBeInTheDocument(); // Progress bar
  });

  it('toggles details view', () => {
    render(<CartSummary {...mockProps} />);

    const toggleButton = screen.getByText('Ver detalles');
    fireEvent.click(toggleButton);

    expect(screen.getByText('Ocultar detalles')).toBeInTheDocument();
    expect(screen.getByText('Producto #1 × 2')).toBeInTheDocument();
    expect(screen.getByText('Producto #2 × 1')).toBeInTheDocument();
  });

  it('shows detailed item breakdown when expanded', () => {
    render(<CartSummary {...mockProps} />);

    const toggleButton = screen.getByText('Ver detalles');
    fireEvent.click(toggleButton);

    expect(screen.getByText('$100.000')).toBeInTheDocument(); // 2 × 50000
    expect(screen.getByText('$30.000')).toBeInTheDocument(); // 1 × 30000
  });

  it('displays loading state correctly', () => {
    const loadingProps = { ...mockProps, loading: true };
    render(<CartSummary {...loadingProps} />);

    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('shows empty state when no items', () => {
    const emptyProps = { ...mockProps, items: [] };
    render(<CartSummary {...emptyProps} />);

    expect(screen.getByText('El resumen aparecerá cuando agregues productos')).toBeInTheDocument();
  });

  it('handles proceed to checkout', () => {
    render(<CartSummary {...mockProps} />);

    const checkoutButton = screen.getByText('Proceder al checkout');
    fireEvent.click(checkoutButton);

    expect(mockProps.onProceedToCheckout).toHaveBeenCalled();
  });

  it('disables checkout button when loading', () => {
    const loadingProps = { ...mockProps, loading: true };
    render(<CartSummary {...loadingProps} />);

    // Should render loading skeleton instead of checkout button
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('disables checkout button when no items', () => {
    const emptyProps = { ...mockProps, items: [] };
    render(<CartSummary {...emptyProps} />);

    // Empty state should not have checkout button
    expect(screen.queryByText('Proceder al checkout')).not.toBeInTheDocument();
  });

  it('shows security and guarantee badges', () => {
    render(<CartSummary {...mockProps} />);

    expect(screen.getByText('Compra 100% segura')).toBeInTheDocument();
    expect(screen.getByText('Garantía de satisfacción')).toBeInTheDocument();
    expect(screen.getByText('Soporte 24/7')).toBeInTheDocument();
  });

  it('shows payment methods', () => {
    render(<CartSummary {...mockProps} />);

    expect(screen.getByText('Métodos de pago aceptados:')).toBeInTheDocument();
    expect(screen.getByText('VISA')).toBeInTheDocument();
    expect(screen.getByText('MC')).toBeInTheDocument();
    expect(screen.getByText('PSE')).toBeInTheDocument();
    expect(screen.getByText('NEQUI')).toBeInTheDocument();
  });

  it('shows tax tooltip information', () => {
    render(<CartSummary {...mockProps} />);

    const infoIcon = document.querySelector('.cursor-help');
    expect(infoIcon).toBeInTheDocument();

    // Hover to show tooltip
    if (infoIcon) {
      fireEvent.mouseEnter(infoIcon);
      expect(screen.getByText('Impuesto al Valor Agregado según normativa colombiana')).toBeInTheDocument();
    }
  });

  it('formats Colombian pesos correctly', () => {
    render(<CartSummary {...mockProps} />);

    // Check currency formatting
    expect(screen.getByText('$130.000')).toBeInTheDocument(); // Subtotal
    expect(screen.getByText('$24.700')).toBeInTheDocument(); // Tax
    expect(screen.getByText('$169.700')).toBeInTheDocument(); // Total
  });

  it('shows correct singular/plural forms', () => {
    const singleItemProps = {
      ...mockProps,
      items: [{ productId: 1, quantity: 1, price: 50000, addedAt: '2023-01-01T00:00:00.000Z' }]
    };

    render(<CartSummary {...singleItemProps} />);

    expect(screen.getByText('Subtotal (1 producto)')).toBeInTheDocument();
  });

  it('calculates free shipping amount correctly', () => {
    render(<CartSummary {...mockProps} />);

    // Free shipping threshold is 100000, current subtotal is 130000
    // Since subtotal > threshold, should already be free
    // But with items totaling 130000, should not show the progress message
    expect(screen.queryByText(/¡Envío GRATIS comprando/)).not.toBeInTheDocument();
  });

  it('shows progress towards free shipping for lower amounts', () => {
    const lowValueItems = [
      { productId: 1, quantity: 1, price: 50000, addedAt: '2023-01-01T00:00:00.000Z' },
    ];
    const lowValueProps = { ...mockProps, items: lowValueItems };

    render(<CartSummary {...lowValueProps} />);

    expect(screen.getByText(/¡Envío GRATIS comprando/)).toBeInTheDocument();
    expect(screen.getByText('$50.000')).toBeInTheDocument(); // Amount needed
  });
});