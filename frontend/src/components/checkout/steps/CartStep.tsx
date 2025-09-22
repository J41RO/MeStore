import React from 'react';
import { useCheckoutStore } from '../../../stores/checkoutStore';

const CartStep: React.FC = () => {
  const {
    cart_items,
    cart_count,
    updateQuantity,
    removeItem,
    goToNextStep,
    setOrderNotes,
    order_notes,
    canProceedToNextStep
  } = useCheckoutStore();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const handleContinue = () => {
    if (canProceedToNextStep()) {
      goToNextStep();
    }
  };

  if (cart_items.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Tu carrito está vacío</h3>
        <p className="text-gray-600 mb-6">Agrega productos para continuar con tu compra</p>
        <button
          onClick={() => window.location.href = '/products'}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors"
        >
          Explorar Productos
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Revisar Productos ({cart_count} {cart_count === 1 ? 'artículo' : 'artículos'})
        </h2>
        <p className="text-gray-600">
          Verifica tu selección antes de continuar al checkout
        </p>
      </div>

      {/* Cart Items */}
      <div className="space-y-4 mb-6">
        {cart_items.map((item) => (
          <div key={item.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-4">
              {/* Product Image */}
              <div className="flex-shrink-0">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-20 h-20 object-cover rounded-md bg-gray-100"
                  />
                ) : (
                  <div className="w-20 h-20 bg-gray-100 rounded-md flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                )}
              </div>

              {/* Product Details */}
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">{item.name}</h3>

                    {item.sku && (
                      <p className="text-sm text-gray-500 mt-1">SKU: {item.sku}</p>
                    )}

                    {item.vendor_name && (
                      <p className="text-sm text-gray-600 mt-1">
                        Vendido por: <span className="font-medium">{item.vendor_name}</span>
                      </p>
                    )}

                    {/* Variant attributes */}
                    {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                      <div className="mt-2 space-y-1">
                        {Object.entries(item.variant_attributes).map(([key, value]) => (
                          <span
                            key={key}
                            className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs mr-2"
                          >
                            {key}: {value}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="mt-3 flex items-center space-x-4">
                      {/* Quantity Selector */}
                      <div className="flex items-center space-x-2">
                        <label htmlFor={`quantity-${item.id}`} className="text-sm text-gray-600">
                          Cantidad:
                        </label>
                        <div className="flex items-center border border-gray-300 rounded-md">
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                            disabled={item.quantity <= 1}
                          >
                            -
                          </button>
                          <input
                            id={`quantity-${item.id}`}
                            type="number"
                            min="1"
                            max={item.stock_available || 999}
                            value={item.quantity}
                            onChange={(e) => {
                              const newQuantity = parseInt(e.target.value) || 1;
                              updateQuantity(item.id, newQuantity);
                            }}
                            className="w-16 px-2 py-1 text-center border-0 focus:ring-0"
                          />
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                            disabled={item.stock_available && item.quantity >= item.stock_available}
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Stock info */}
                      {item.stock_available && (
                        <span className="text-sm text-gray-500">
                          {item.stock_available} disponibles
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Price and Remove */}
                  <div className="text-right ml-4">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatCurrency(item.price * item.quantity)}
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatCurrency(item.price)} c/u
                    </div>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Order Notes */}
      <div className="mb-6">
        <label htmlFor="order-notes" className="block text-sm font-medium text-gray-700 mb-2">
          Notas del pedido (opcional)
        </label>
        <textarea
          id="order-notes"
          rows={3}
          value={order_notes}
          onChange={(e) => setOrderNotes(e.target.value)}
          placeholder="Agregar instrucciones especiales, detalles de entrega, etc..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Continue Button */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={() => window.location.href = '/products'}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          ← Continuar Comprando
        </button>

        <button
          onClick={handleContinue}
          disabled={!canProceedToNextStep()}
          className={`
            px-6 py-3 rounded-md font-medium transition-colors
            ${canProceedToNextStep()
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Continuar al Envío →
        </button>
      </div>
    </div>
  );
};

export default CartStep;