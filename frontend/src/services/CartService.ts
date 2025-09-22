/**
 * Cart Service - Frontend Cart Management Integration
 * ==================================================
 *
 * This service provides cart management functionality that works with
 * the backend orders API and integrates with the checkout store.
 *
 * Features:
 * - Local cart management (localStorage persistence)
 * - Product validation with backend
 * - Price and stock verification
 * - Cart synchronization
 * - Shipping cost calculation
 * - Tax calculation for Colombian market
 *
 * Created by: API Architect AI
 * Date: 2025-09-19
 * Purpose: Complete cart management for checkout integration
 */

import api from './api';
import type { CartItem } from '../stores/checkoutStore';

export interface Product {
  id: string;
  name: string;
  precio_venta: number;
  sku: string;
  stock_quantity?: number;
  images?: Array<{ image_url: string; is_primary: boolean }>;
  vendor_id?: string;
  vendor_name?: string;
  estado: string;
}

export interface CartValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  updatedItems: CartItem[];
}

export interface ShippingCost {
  cost: number;
  method: string;
  estimated_days: number;
  free_shipping_threshold?: number;
}

export interface CartTotals {
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  discount_amount: number;
  total: number;
}

export class CartService {
  private static instance: CartService;
  private readonly TAX_RATE = 0.19; // Colombian IVA 19%
  private readonly FREE_SHIPPING_THRESHOLD = 100000; // 100,000 COP

  private constructor() {}

  public static getInstance(): CartService {
    if (!CartService.instance) {
      CartService.instance = new CartService();
    }
    return CartService.instance;
  }

  // ===== PRODUCT VALIDATION =====

  /**
   * Validate cart items against backend product data
   */
  async validateCartItems(cartItems: CartItem[]): Promise<CartValidationResult> {
    const result: CartValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
      updatedItems: [...cartItems]
    };

    if (!cartItems.length) {
      result.valid = false;
      result.errors.push('El carrito está vacío');
      return result;
    }

    try {
      // Get all unique product IDs
      const productIds = [...new Set(cartItems.map(item => item.product_id))];

      // Fetch current product data from backend
      const productPromises = productIds.map(id =>
        api.products.getById(id).catch(() => null)
      );

      const productResponses = await Promise.all(productPromises);
      const products: Record<string, Product> = {};

      productResponses.forEach((response, index) => {
        if (response?.data) {
          products[productIds[index]] = response.data;
        }
      });

      // Validate each cart item
      result.updatedItems = cartItems.map(item => {
        const product = products[item.product_id];

        if (!product) {
          result.errors.push(`Producto ${item.name} ya no está disponible`);
          result.valid = false;
          return { ...item, stock_available: 0 };
        }

        if (product.estado !== 'aprobado') {
          result.errors.push(`Producto ${product.name} ya no está disponible para compra`);
          result.valid = false;
          return { ...item, stock_available: 0 };
        }

        // Check stock availability
        if (product.stock_quantity !== undefined && item.quantity > product.stock_quantity) {
          result.warnings.push(
            `Stock limitado para ${product.name}. Cantidad ajustada de ${item.quantity} a ${product.stock_quantity}`
          );
          return {
            ...item,
            quantity: product.stock_quantity,
            stock_available: product.stock_quantity
          };
        }

        // Check price changes
        if (Math.abs(item.price - product.precio_venta) > 0.01) {
          result.warnings.push(
            `El precio de ${product.name} ha cambiado de $${item.price.toLocaleString()} a $${product.precio_venta.toLocaleString()}`
          );
          return {
            ...item,
            price: product.precio_venta,
            stock_available: product.stock_quantity
          };
        }

        return {
          ...item,
          stock_available: product.stock_quantity
        };
      }).filter(item => item.stock_available !== 0); // Remove unavailable items

      return result;

    } catch (error) {
      console.error('Cart validation failed:', error);
      result.valid = false;
      result.errors.push('Error validando el carrito. Intente de nuevo.');
      return result;
    }
  }

  /**
   * Add product to cart with validation
   */
  async addToCart(productId: string, quantity: number = 1, variantAttributes?: Record<string, string>): Promise<CartItem | null> {
    try {
      // Fetch product data
      const response = await api.products.getById(productId);
      const product: Product = response.data;

      if (!product) {
        throw new Error('Producto no encontrado');
      }

      if (product.estado !== 'aprobado') {
        throw new Error('Producto no disponible para compra');
      }

      if (product.stock_quantity !== undefined && quantity > product.stock_quantity) {
        throw new Error(`Stock insuficiente. Disponible: ${product.stock_quantity}`);
      }

      // Get primary image
      let primaryImage = '';
      if (product.images?.length) {
        const primary = product.images.find(img => img.is_primary);
        primaryImage = primary?.image_url || product.images[0]?.image_url || '';
      }

      // Create cart item
      const cartItem: CartItem = {
        id: '', // Will be set by store
        product_id: productId,
        name: product.name,
        price: product.precio_venta,
        quantity,
        image_url: primaryImage,
        sku: product.sku,
        variant_attributes: variantAttributes,
        vendor_id: product.vendor_id,
        vendor_name: product.vendor_name,
        stock_available: product.stock_quantity
      };

      return cartItem;

    } catch (error: any) {
      console.error('Add to cart failed:', error);
      throw new Error(error.response?.data?.detail || error.message || 'Error agregando producto al carrito');
    }
  }

  // ===== CART CALCULATIONS =====

  /**
   * Calculate cart totals with Colombian tax rules
   */
  calculateCartTotals(cartItems: CartItem[], shippingCost: number = 0): CartTotals {
    const subtotal = cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);

    // Colombian IVA (19%)
    const tax_amount = subtotal * this.TAX_RATE;

    // No discount for now (can be extended)
    const discount_amount = 0;

    const total = subtotal + tax_amount + shippingCost - discount_amount;

    return {
      subtotal,
      tax_amount,
      shipping_cost: shippingCost,
      discount_amount,
      total
    };
  }

  /**
   * Calculate shipping cost based on cart and destination
   */
  async calculateShippingCost(
    cartItems: CartItem[],
    destinationCity: string,
    destinationState: string
  ): Promise<ShippingCost> {
    const subtotal = cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);

    // Free shipping for orders over threshold
    if (subtotal >= this.FREE_SHIPPING_THRESHOLD) {
      return {
        cost: 0,
        method: 'Envío gratis',
        estimated_days: 3,
        free_shipping_threshold: this.FREE_SHIPPING_THRESHOLD
      };
    }

    // Basic shipping calculation (can be enhanced with real shipping API)
    let baseCost = 15000; // Base shipping cost 15,000 COP

    // Adjust based on destination (simplified)
    const majorCities = ['bogotá', 'medellín', 'cali', 'barranquilla', 'cartagena'];
    if (!majorCities.some(city => destinationCity.toLowerCase().includes(city))) {
      baseCost += 5000; // Additional cost for smaller cities
    }

    // Add weight-based cost (simplified)
    const itemCount = cartItems.reduce((total, item) => total + item.quantity, 0);
    if (itemCount > 5) {
      baseCost += (itemCount - 5) * 2000;
    }

    return {
      cost: baseCost,
      method: 'Envío estándar',
      estimated_days: destinationState.toLowerCase() === 'cundinamarca' ? 2 : 4,
      free_shipping_threshold: this.FREE_SHIPPING_THRESHOLD
    };
  }

  // ===== CART PERSISTENCE =====

  /**
   * Save cart to localStorage
   */
  saveCartToStorage(cartItems: CartItem[]): void {
    try {
      localStorage.setItem('mestore_cart', JSON.stringify({
        items: cartItems,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.error('Failed to save cart to storage:', error);
    }
  }

  /**
   * Load cart from localStorage
   */
  loadCartFromStorage(): CartItem[] {
    try {
      const stored = localStorage.getItem('mestore_cart');
      if (!stored) return [];

      const cartData = JSON.parse(stored);

      // Check if cart is not too old (7 days)
      const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
      if (Date.now() - cartData.timestamp > maxAge) {
        this.clearCartStorage();
        return [];
      }

      return cartData.items || [];
    } catch (error) {
      console.error('Failed to load cart from storage:', error);
      return [];
    }
  }

  /**
   * Clear cart from localStorage
   */
  clearCartStorage(): void {
    try {
      localStorage.removeItem('mestore_cart');
    } catch (error) {
      console.error('Failed to clear cart storage:', error);
    }
  }

  // ===== CART UTILITIES =====

  /**
   * Check if product is already in cart
   */
  isProductInCart(cartItems: CartItem[], productId: string, variantAttributes?: Record<string, string>): boolean {
    return cartItems.some(item =>
      item.product_id === productId &&
      JSON.stringify(item.variant_attributes || {}) === JSON.stringify(variantAttributes || {})
    );
  }

  /**
   * Get cart item by product ID and variant
   */
  getCartItem(cartItems: CartItem[], productId: string, variantAttributes?: Record<string, string>): CartItem | undefined {
    return cartItems.find(item =>
      item.product_id === productId &&
      JSON.stringify(item.variant_attributes || {}) === JSON.stringify(variantAttributes || {})
    );
  }

  /**
   * Get cart summary for display
   */
  getCartSummary(cartItems: CartItem[]): {
    itemCount: number;
    uniqueProducts: number;
    subtotal: number;
    isEmpty: boolean;
  } {
    return {
      itemCount: cartItems.reduce((total, item) => total + item.quantity, 0),
      uniqueProducts: cartItems.length,
      subtotal: cartItems.reduce((total, item) => total + (item.price * item.quantity), 0),
      isEmpty: cartItems.length === 0
    };
  }

  /**
   * Format currency for Colombian pesos
   */
  static formatCurrency(amount: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }

  /**
   * Check if cart meets minimum order requirements
   */
  validateMinimumOrder(cartItems: CartItem[]): { valid: boolean; message?: string } {
    const subtotal = cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    const minOrder = 10000; // Minimum order 10,000 COP

    if (subtotal < minOrder) {
      return {
        valid: false,
        message: `Pedido mínimo: ${CartService.formatCurrency(minOrder)}`
      };
    }

    return { valid: true };
  }

  /**
   * Get shipping methods available
   */
  getShippingMethods(): Array<{ id: string; name: string; description: string }> {
    return [
      {
        id: 'standard',
        name: 'Envío estándar',
        description: '2-4 días hábiles'
      },
      {
        id: 'express',
        name: 'Envío express',
        description: '1-2 días hábiles (+$10,000)'
      }
    ];
  }
}

// Export singleton instance
export const cartService = CartService.getInstance();
export default cartService;