import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Types for cart items
export interface CartItem {
  id: string;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
  sku?: string;
  variant_attributes?: Record<string, string>;
  vendor_id?: string;
  vendor_name?: string;
  stock_available?: number;
}

// Types for shipping address
export interface ShippingAddress {
  id?: string;
  name: string;
  phone: string;
  address: string;
  city: string;
  department?: string;
  postal_code?: string;
  is_default?: boolean;
  additional_info?: string;
}

// Types for payment information
export interface PaymentInfo {
  method: 'pse' | 'credit_card' | 'bank_transfer' | 'cash_on_delivery';

  // PSE specific
  bank_code?: string;
  bank_name?: string;
  user_type?: 'natural' | 'juridical';
  identification_type?: 'CC' | 'CE' | 'NIT' | 'TI' | 'PP';
  identification_number?: string;

  // Credit card specific
  card_number?: string;
  card_holder_name?: string;
  expiry_month?: string;
  expiry_year?: string;
  cvv?: string;

  // Common
  email?: string;
  total_amount?: number;
}

// Types for checkout process
export interface CheckoutState {
  // Cart state
  cart_items: CartItem[];
  cart_total: number;
  cart_count: number;

  // Checkout process state
  current_step: 'cart' | 'shipping' | 'payment' | 'confirmation';
  is_processing: boolean;

  // Shipping information
  shipping_address: ShippingAddress | null;
  saved_addresses: ShippingAddress[];
  shipping_cost: number;

  // Payment information
  payment_info: PaymentInfo | null;

  // Order information
  order_notes: string;
  order_id: string | null;

  // Error handling
  error: string | null;
  validation_errors: Record<string, string>;

  // Cart actions
  addItem: (item: Omit<CartItem, 'id'>) => void;
  removeItem: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;

  // Checkout flow actions
  setCurrentStep: (step: CheckoutState['current_step']) => void;
  goToNextStep: () => boolean;
  goToPreviousStep: () => void;

  // Shipping actions
  setShippingAddress: (address: ShippingAddress) => void;
  addSavedAddress: (address: ShippingAddress) => void;
  removeSavedAddress: (addressId: string) => void;
  setShippingCost: (cost: number) => void;

  // Payment actions
  setPaymentInfo: (payment: PaymentInfo) => void;

  // Order actions
  setOrderNotes: (notes: string) => void;
  setOrderId: (orderId: string) => void;

  // Processing state
  setProcessing: (processing: boolean) => void;

  // Error handling
  setError: (error: string | null) => void;
  setValidationErrors: (errors: Record<string, string>) => void;
  clearErrors: () => void;

  // Utility methods
  getTotalWithShipping: () => number;
  getCartSubtotal: () => number;
  validateCurrentStep: () => boolean;
  canProceedToNextStep: () => boolean;

  // Reset checkout
  resetCheckout: () => void;
}

// Helper function to generate unique IDs
const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Helper function to calculate cart totals
const calculateCartTotals = (items: CartItem[]) => {
  const subtotal = items.reduce((total, item) => total + (item.price * item.quantity), 0);
  const count = items.reduce((total, item) => total + item.quantity, 0);
  return { subtotal, count };
};

export const useCheckoutStore = create<CheckoutState>()(
  persist(
    (set, get) => ({
      // Initial state
      cart_items: [],
      cart_total: 0,
      cart_count: 0,
      current_step: 'cart',
      is_processing: false,
      shipping_address: null,
      saved_addresses: [],
      shipping_cost: 0,
      payment_info: null,
      order_notes: '',
      order_id: null,
      error: null,
      validation_errors: {},

      // Cart actions
      addItem: (item) => {
        const state = get();
        const existingItemIndex = state.cart_items.findIndex(
          cartItem => cartItem.product_id === item.product_id &&
          JSON.stringify(cartItem.variant_attributes || {}) === JSON.stringify(item.variant_attributes || {})
        );

        let newItems: CartItem[];

        if (existingItemIndex >= 0) {
          // Update existing item quantity
          newItems = state.cart_items.map((cartItem, index) =>
            index === existingItemIndex
              ? { ...cartItem, quantity: cartItem.quantity + item.quantity }
              : cartItem
          );
        } else {
          // Add new item
          const newItem: CartItem = {
            ...item,
            id: generateId()
          };
          newItems = [...state.cart_items, newItem];
        }

        const { subtotal, count } = calculateCartTotals(newItems);

        set({
          cart_items: newItems,
          cart_total: subtotal,
          cart_count: count
        });
      },

      removeItem: (itemId) => {
        const state = get();
        const newItems = state.cart_items.filter(item => item.id !== itemId);
        const { subtotal, count } = calculateCartTotals(newItems);

        set({
          cart_items: newItems,
          cart_total: subtotal,
          cart_count: count
        });
      },

      updateQuantity: (itemId, quantity) => {
        if (quantity <= 0) {
          get().removeItem(itemId);
          return;
        }

        const state = get();
        const newItems = state.cart_items.map(item =>
          item.id === itemId ? { ...item, quantity } : item
        );
        const { subtotal, count } = calculateCartTotals(newItems);

        set({
          cart_items: newItems,
          cart_total: subtotal,
          cart_count: count
        });
      },

      clearCart: () => {
        set({
          cart_items: [],
          cart_total: 0,
          cart_count: 0
        });
      },

      // Checkout flow actions
      setCurrentStep: (step) => {
        set({ current_step: step });
      },

      goToNextStep: () => {
        const state = get();
        if (!state.canProceedToNextStep()) {
          return false;
        }

        const steps: CheckoutState['current_step'][] = ['cart', 'shipping', 'payment', 'confirmation'];
        const currentIndex = steps.indexOf(state.current_step);

        if (currentIndex < steps.length - 1) {
          set({ current_step: steps[currentIndex + 1] });
          return true;
        }

        return false;
      },

      goToPreviousStep: () => {
        const state = get();
        const steps: CheckoutState['current_step'][] = ['cart', 'shipping', 'payment', 'confirmation'];
        const currentIndex = steps.indexOf(state.current_step);

        if (currentIndex > 0) {
          set({ current_step: steps[currentIndex - 1] });
        }
      },

      // Shipping actions
      setShippingAddress: (address) => {
        set({ shipping_address: address });
      },

      addSavedAddress: (address) => {
        const state = get();
        const newAddress = { ...address, id: address.id || generateId() };

        // If this is the default address, unset others
        let savedAddresses = state.saved_addresses;
        if (newAddress.is_default) {
          savedAddresses = savedAddresses.map(addr => ({ ...addr, is_default: false }));
        }

        // Check if address already exists
        const existingIndex = savedAddresses.findIndex(addr => addr.id === newAddress.id);
        if (existingIndex >= 0) {
          savedAddresses[existingIndex] = newAddress;
        } else {
          savedAddresses.push(newAddress);
        }

        set({ saved_addresses: savedAddresses });
      },

      removeSavedAddress: (addressId) => {
        const state = get();
        const newAddresses = state.saved_addresses.filter(addr => addr.id !== addressId);
        set({ saved_addresses: newAddresses });
      },

      setShippingCost: (cost) => {
        set({ shipping_cost: cost });
      },

      // Payment actions
      setPaymentInfo: (payment) => {
        set({ payment_info: payment });
      },

      // Order actions
      setOrderNotes: (notes) => {
        set({ order_notes: notes });
      },

      setOrderId: (orderId) => {
        set({ order_id: orderId });
      },

      // Processing state
      setProcessing: (processing) => {
        set({ is_processing: processing });
      },

      // Error handling
      setError: (error) => {
        set({ error });
      },

      setValidationErrors: (errors) => {
        set({ validation_errors: errors });
      },

      clearErrors: () => {
        set({ error: null, validation_errors: {} });
      },

      // Utility methods
      getTotalWithShipping: () => {
        const state = get();
        return state.cart_total + state.shipping_cost;
      },

      getCartSubtotal: () => {
        const state = get();
        return state.cart_total;
      },

      validateCurrentStep: () => {
        const state = get();

        switch (state.current_step) {
          case 'cart':
            return state.cart_items.length > 0;

          case 'shipping':
            return !!state.shipping_address &&
                   !!state.shipping_address.name &&
                   !!state.shipping_address.address &&
                   !!state.shipping_address.city &&
                   !!state.shipping_address.phone;

          case 'payment':
            return !!state.payment_info && !!state.payment_info.method;

          case 'confirmation':
            return !!state.order_id;

          default:
            return false;
        }
      },

      canProceedToNextStep: () => {
        const state = get();
        return state.validateCurrentStep() && !state.is_processing;
      },

      // Reset checkout
      resetCheckout: () => {
        set({
          current_step: 'cart',
          is_processing: false,
          shipping_address: null,
          shipping_cost: 0,
          payment_info: null,
          order_notes: '',
          order_id: null,
          error: null,
          validation_errors: {}
        });
      }
    }),
    {
      name: 'checkout-storage',
      partialize: (state: CheckoutState) => ({
        cart_items: state.cart_items,
        cart_total: state.cart_total,
        cart_count: state.cart_count,
        saved_addresses: state.saved_addresses,
        order_notes: state.order_notes
      }),
    }
  )
);

// Export types for use in components
export type { CartItem, ShippingAddress, PaymentInfo };