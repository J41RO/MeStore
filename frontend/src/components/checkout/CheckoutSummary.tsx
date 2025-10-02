import React from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';

const CheckoutSummary: React.FC = () => {
  const {
    cart_items,
    cart_total,
    shipping_cost,
    shipping_address,
    payment_info,
    order_notes,
    getTotalWithShipping,
    getSubtotal,
    getIVA,
    getShipping,
    getTotal
  } = useCheckoutStore();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Use store methods for consistent calculations (same as Cart page)
  const subtotal = getSubtotal();
  const tax_amount = getIVA();
  const shipping = getShipping(); // Always calculate shipping based on subtotal
  const final_total = getTotal(); // subtotal + IVA + shipping

  return (
    <div className="space-y-6">
      {/* Order Summary */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Resumen del Pedido
        </h3>

        {/* Items */}
        <div className="space-y-4">
          {cart_items.map((item) => (
            <div key={item.id} className="flex items-start space-x-4">
              {item.image_url && (
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-16 h-16 object-cover rounded-md bg-gray-100"
                />
              )}

              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {item.name}
                </h4>
                {item.sku && (
                  <p className="text-xs text-gray-500">SKU: {item.sku}</p>
                )}
                {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                  <div className="text-xs text-gray-500">
                    {Object.entries(item.variant_attributes).map(([key, value]) => (
                      <span key={key} className="mr-2">
                        {key}: {value}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className="text-sm text-gray-600">
                    Cantidad: {item.quantity}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(item.price * item.quantity)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order Notes */}
        {order_notes && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900">Notas del pedido:</h4>
            <p className="text-sm text-gray-600 mt-1">{order_notes}</p>
          </div>
        )}

        {/* Totals */}
        <div className="mt-6 pt-4 border-t border-gray-200 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Subtotal</span>
            <span className="text-gray-900">{formatCurrency(subtotal)}</span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">IVA (19%)</span>
            <span className="text-gray-900">{formatCurrency(tax_amount)}</span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Envío</span>
            <span className={`font-semibold ${shipping === 0 ? 'text-green-600' : 'text-gray-900'}`}>
              {shipping === 0 ? 'GRATIS' : formatCurrency(shipping)}
            </span>
          </div>

          <div className="flex justify-between text-base font-medium pt-2 border-t border-gray-200">
            <span className="text-gray-900">Total</span>
            <span className="text-gray-900">{formatCurrency(final_total)}</span>
          </div>
        </div>
      </div>

      {/* Shipping Information */}
      {shipping_address && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Información de Envío
          </h3>

          <div className="text-sm space-y-1">
            <p className="font-medium text-gray-900">{shipping_address.name}</p>
            <p className="text-gray-600">{shipping_address.address}</p>
            <p className="text-gray-600">
              {shipping_address.city}
              {shipping_address.department && `, ${shipping_address.department}`}
            </p>
            {shipping_address.postal_code && (
              <p className="text-gray-600">CP: {shipping_address.postal_code}</p>
            )}
            <p className="text-gray-600">{shipping_address.phone}</p>
            {shipping_address.additional_info && (
              <p className="text-gray-600 text-xs italic">
                {shipping_address.additional_info}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Payment Information */}
      {payment_info && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Método de Pago
          </h3>

          <div className="text-sm space-y-2">
            <div className="flex items-center space-x-2">
              {payment_info.method === 'pse' && (
                <>
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4zM18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">PSE</p>
                    {payment_info.bank_name && (
                      <p className="text-gray-600 text-xs">{payment_info.bank_name}</p>
                    )}
                  </div>
                </>
              )}

              {payment_info.method === 'credit_card' && (
                <>
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4zM18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Tarjeta de Crédito</p>
                    {payment_info.card_number && (
                      <p className="text-gray-600 text-xs">
                        **** **** **** {payment_info.card_number.slice(-4)}
                      </p>
                    )}
                  </div>
                </>
              )}

              {payment_info.method === 'bank_transfer' && (
                <>
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm5 3a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM7.5 11H9v2H7.5v-2zm2.5-1h3.5v2H10v-2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Transferencia Bancaria</p>
                  </div>
                </>
              )}

              {payment_info.method === 'cash_on_delivery' && (
                <>
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.51-1.31c-.562-.649-1.413-1.076-2.353-1.253V5z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Pago Contraentrega</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Security Badge */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Compra 100% segura</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Tus datos están protegidos con encriptación SSL
        </p>
      </div>
    </div>
  );
};

export default CheckoutSummary;