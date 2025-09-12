import React from 'react';
import { ShoppingBag, Truck, Calculator, Tag } from 'lucide-react';

interface OrderSummaryProps {
  order: {
    id: number;
    order_number: string;
    total_amount: number;
    items: Array<{
      id: number;
      product_name: string;
      quantity: number;
      unit_price: number;
      total_price: number;
      product_image_url?: string;
    }>;
  };
  shippingCost: number;
  taxAmount: number;
}

const OrderSummary: React.FC<OrderSummaryProps> = ({
  order,
  shippingCost,
  taxAmount
}) => {
  const subtotal = order.items.reduce((sum, item) => sum + item.total_price, 0);
  const total = subtotal + shippingCost + taxAmount;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <ShoppingBag className="w-5 h-5 mr-2" />
          Resumen del pedido
        </h2>
        <p className="text-sm text-gray-600 mt-1">Orden #{order.order_number}</p>
      </div>

      {/* Order Items */}
      <div className="px-6 py-4">
        <h3 className="text-sm font-medium text-gray-900 mb-4">
          Productos ({order.items.length})
        </h3>
        <div className="space-y-4">
          {order.items.map((item) => (
            <div key={item.id} className="flex items-start space-x-3">
              {/* Product Image */}
              <div className="flex-shrink-0">
                {item.product_image_url ? (
                  <img
                    src={item.product_image_url}
                    alt={item.product_name}
                    className="w-12 h-12 object-cover rounded-lg border border-gray-200"
                  />
                ) : (
                  <div className="w-12 h-12 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
                    <ShoppingBag className="w-6 h-6 text-gray-400" />
                  </div>
                )}
              </div>

              {/* Product Details */}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {item.product_name}
                </h4>
                <p className="text-sm text-gray-600">
                  Cantidad: {item.quantity}
                </p>
                <p className="text-sm text-gray-600">
                  ${item.unit_price.toLocaleString()} c/u
                </p>
              </div>

              {/* Item Total */}
              <div className="text-sm font-medium text-gray-900">
                ${item.total_price.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Price Breakdown */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="space-y-3">
          {/* Subtotal */}
          <div className="flex justify-between items-center">
            <div className="flex items-center text-sm text-gray-600">
              <Calculator className="w-4 h-4 mr-2" />
              Subtotal
            </div>
            <span className="text-sm font-medium text-gray-900">
              ${subtotal.toLocaleString()}
            </span>
          </div>

          {/* Tax */}
          <div className="flex justify-between items-center">
            <div className="flex items-center text-sm text-gray-600">
              <Tag className="w-4 h-4 mr-2" />
              IVA (19%)
            </div>
            <span className="text-sm font-medium text-gray-900">
              ${taxAmount.toLocaleString()}
            </span>
          </div>

          {/* Shipping */}
          <div className="flex justify-between items-center">
            <div className="flex items-center text-sm text-gray-600">
              <Truck className="w-4 h-4 mr-2" />
              Envío
            </div>
            <span className="text-sm font-medium text-gray-900">
              {shippingCost > 0 ? `$${shippingCost.toLocaleString()}` : 'GRATIS'}
            </span>
          </div>

          {/* Free Shipping Notice */}
          {shippingCost === 0 && (
            <div className="flex items-center text-xs text-green-600 bg-green-50 rounded-lg p-2">
              <Truck className="w-4 h-4 mr-2" />
              ¡Envío gratuito en tu pedido!
            </div>
          )}
        </div>
      </div>

      {/* Total */}
      <div className="px-6 py-4 border-t-2 border-gray-200 bg-gray-50 rounded-b-lg">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900">Total</span>
          <span className="text-lg font-bold text-gray-900">
            ${total.toLocaleString()}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-1">Incluye todos los impuestos</p>
      </div>

      {/* Guarantees */}
      <div className="px-6 py-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Tu compra incluye:</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Garantía de satisfacción
          </li>
          <li className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Soporte al cliente 24/7
          </li>
          <li className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Política de devoluciones
          </li>
          <li className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Pago 100% seguro
          </li>
        </ul>
      </div>
    </div>
  );
};

export default OrderSummary;