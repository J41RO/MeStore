import React, { useState } from 'react';
import { CreditCard, Truck, ShoppingCart, Info, Calculator, ArrowRight } from 'lucide-react';

interface CartItem {
  productId: number;
  quantity: number;
  price: number;
  addedAt: string;
}

interface CartSummaryProps {
  items: CartItem[];
  onProceedToCheckout: () => void;
  loading?: boolean;
}

const CartSummary: React.FC<CartSummaryProps> = ({
  items,
  onProceedToCheckout,
  loading = false
}) => {
  const [showDetails, setShowDetails] = useState(false);

  // Cálculos
  const subtotal = items.reduce((total, item) => total + (item.price * item.quantity), 0);
  const totalItems = items.reduce((total, item) => total + item.quantity, 0);
  
  // IVA 19% - Colombia
  const taxRate = 0.19;
  const taxAmount = subtotal * taxRate;
  
  // Envío gratuito para pedidos mayores a $100,000
  const freeShippingThreshold = 100000;
  const baseShippingCost = 15000;
  const shippingCost = subtotal >= freeShippingThreshold ? 0 : baseShippingCost;
  const isFreeShipping = shippingCost === 0;
  
  // Total final
  const total = subtotal + taxAmount + shippingCost;

  // Cuánto falta para envío gratis
  const amountForFreeShipping = freeShippingThreshold - subtotal;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const formatPercentage = (rate: number) => {
    return (rate * 100).toFixed(0) + '%';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-32"></div>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex justify-between">
              <div className="h-4 bg-gray-200 rounded w-24"></div>
              <div className="h-4 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
          <div className="h-12 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
        <Calculator className="h-12 w-12 mx-auto text-gray-300 mb-3" />
        <p className="text-gray-600">El resumen aparecerá cuando agregues productos</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">
          Resumen del pedido
        </h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
        >
          {showDetails ? 'Ocultar' : 'Ver'} detalles
        </button>
      </div>

      {/* Resumen básico */}
      <div className="space-y-4">
        <div className="flex justify-between">
          <span className="text-gray-600">
            Subtotal ({totalItems} {totalItems === 1 ? 'producto' : 'productos'})
          </span>
          <span className="font-medium">{formatPrice(subtotal)}</span>
        </div>

        {/* Detalles expandibles */}
        {showDetails && (
          <div className="space-y-3 pt-3 border-t border-gray-200">
            {items.map((item) => (
              <div key={`${item.productId}-${item.addedAt}`} className="flex justify-between text-sm">
                <span className="text-gray-500">
                  Producto #{item.productId} × {item.quantity}
                </span>
                <span className="text-gray-700">{formatPrice(item.price * item.quantity)}</span>
              </div>
            ))}
          </div>
        )}

        {/* Impuestos */}
        <div className="flex justify-between">
          <div className="flex items-center">
            <span className="text-gray-600">IVA ({formatPercentage(taxRate)})</span>
            <div className="ml-2 group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="invisible group-hover:visible absolute left-0 top-6 z-10 w-48 p-2 bg-gray-900 text-white text-xs rounded shadow-lg">
                Impuesto al Valor Agregado según normativa colombiana
              </div>
            </div>
          </div>
          <span className="font-medium">{formatPrice(taxAmount)}</span>
        </div>

        {/* Envío */}
        <div className="flex justify-between">
          <div className="flex items-center">
            <Truck className="h-4 w-4 text-gray-400 mr-1" />
            <span className="text-gray-600">Envío</span>
            {isFreeShipping && (
              <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                GRATIS
              </span>
            )}
          </div>
          <span className="font-medium">
            {isFreeShipping ? formatPrice(0) : formatPrice(shippingCost)}
          </span>
        </div>

        {/* Alerta envío gratis */}
        {!isFreeShipping && amountForFreeShipping > 0 && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <Truck className="h-5 w-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-blue-800 font-medium">
                  ¡Envío GRATIS comprando {formatPrice(amountForFreeShipping)} más!
                </p>
                <div className="mt-2 w-full bg-blue-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${Math.min((subtotal / freeShippingThreshold) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Total */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-medium text-gray-900">Total</span>
            <span className="text-2xl font-bold text-blue-600">{formatPrice(total)}</span>
          </div>
        </div>
      </div>

      {/* Botones de acción */}
      <div className="mt-6 space-y-3">
        <button
          onClick={onProceedToCheckout}
          disabled={loading || items.length === 0}
          className="w-full flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <CreditCard className="h-5 w-5 mr-2" />
          Proceder al checkout
          <ArrowRight className="h-4 w-4 ml-2" />
        </button>

        <div className="text-center">
          <a
            href="/marketplace"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 transition-colors"
          >
            <ShoppingCart className="h-4 w-4 mr-1" />
            Continuar comprando
          </a>
        </div>
      </div>

      {/* Información adicional */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="space-y-2 text-xs text-gray-500">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span>Compra 100% segura</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
            <span>Garantía de satisfacción</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
            <span>Soporte 24/7</span>
          </div>
        </div>
      </div>

      {/* Métodos de pago aceptados */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 mb-2">Métodos de pago aceptados:</p>
        <div className="flex items-center space-x-2">
          <div className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">VISA</div>
          <div className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">MC</div>
          <div className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">PSE</div>
          <div className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">NEQUI</div>
        </div>
      </div>
    </div>
  );
};

export default CartSummary;