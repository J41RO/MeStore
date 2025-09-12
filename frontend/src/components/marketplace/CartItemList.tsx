import React, { useState } from 'react';
import { Plus, Minus, Trash2, ShoppingCart, AlertCircle } from 'lucide-react';

interface CartItem {
  productId: number;
  quantity: number;
  price: number;
  addedAt: string;
}

interface CartItemListProps {
  items: CartItem[];
  onUpdateQuantity: (productId: number, newQuantity: number) => void;
  onRemoveItem: (productId: number) => void;
  onClearCart: () => void;
  loading?: boolean;
}

const CartItemCard: React.FC<{
  item: CartItem;
  onUpdateQuantity: (productId: number, newQuantity: number) => void;
  onRemoveItem: (productId: number) => void;
}> = ({ item, onUpdateQuantity, onRemoveItem }) => {
  const [isUpdating, setIsUpdating] = useState(false);

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity < 0) return;
    
    setIsUpdating(true);
    try {
      onUpdateQuantity(item.productId, newQuantity);
      // Simular delay para UX
      await new Promise(resolve => setTimeout(resolve, 200));
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
      onRemoveItem(item.productId);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const subtotal = item.price * item.quantity;

  return (
    <div className={`flex items-center justify-between p-4 border border-gray-200 rounded-lg transition-all duration-200 ${
      isUpdating ? 'opacity-50' : 'hover:border-gray-300'
    }`}>
      <div className="flex items-center space-x-4">
        {/* Imagen placeholder del producto */}
        <div className="w-16 h-16 lg:w-20 lg:h-20 bg-gray-100 rounded-lg flex items-center justify-center border">
          <ShoppingCart className="h-8 w-8 lg:h-10 lg:w-10 text-gray-400" />
        </div>

        {/* Información del producto */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 truncate">
            Producto #{item.productId}
          </h4>
          <p className="text-sm text-gray-500 mt-1">
            {formatPrice(item.price)} por unidad
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Agregado: {new Date(item.addedAt).toLocaleDateString('es-CO')}
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Controles de cantidad */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleQuantityChange(item.quantity - 1)}
            disabled={isUpdating || item.quantity <= 1}
            className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Reducir cantidad"
          >
            <Minus className="h-4 w-4" />
          </button>
          
          <div className="w-12 text-center">
            {isUpdating ? (
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            ) : (
              <span className="font-medium text-lg">{item.quantity}</span>
            )}
          </div>
          
          <button
            onClick={() => handleQuantityChange(item.quantity + 1)}
            disabled={isUpdating}
            className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Aumentar cantidad"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {/* Subtotal */}
        <div className="text-right min-w-[100px]">
          <p className="font-bold text-lg text-gray-900">
            {formatPrice(subtotal)}
          </p>
          {item.quantity > 1 && (
            <p className="text-xs text-gray-500">
              {item.quantity} × {formatPrice(item.price)}
            </p>
          )}
        </div>

        {/* Botón eliminar */}
        <button
          onClick={handleRemove}
          disabled={isUpdating}
          className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Eliminar producto"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

const CartItemList: React.FC<CartItemListProps> = ({
  items,
  onUpdateQuantity,
  onRemoveItem,
  onClearCart,
  loading = false
}) => {
  const getTotalItems = (): number => {
    return items.reduce((total, item) => total + item.quantity, 0);
  };

  const getTotalValue = (): number => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const handleClearCart = () => {
    if (window.confirm(`¿Estás seguro de que quieres vaciar todo el carrito? Se eliminarán ${getTotalItems()} productos.`)) {
      onClearCart();
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-48"></div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
              <div className="w-16 h-16 bg-gray-200 rounded-lg"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-32"></div>
                <div className="h-3 bg-gray-200 rounded w-24"></div>
              </div>
              <div className="w-24 h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <ShoppingCart className="h-16 w-16 mx-auto text-gray-300 mb-4" />
        <p className="text-gray-600 mb-2">No hay productos en tu carrito</p>
        <p className="text-sm text-gray-500">
          Los productos que agregues aparecerán aquí
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Productos en tu carrito
          </h3>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              {getTotalItems()} {getTotalItems() === 1 ? 'producto' : 'productos'} • {formatPrice(getTotalValue())}
            </div>
            
            <button
              onClick={handleClearCart}
              className="flex items-center px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Vaciar todo
            </button>
          </div>
        </div>
      </div>

      {/* Lista de productos */}
      <div className="p-6">
        <div className="space-y-4">
          {items.map((item) => (
            <CartItemCard
              key={`${item.productId}-${item.addedAt}`}
              item={item}
              onUpdateQuantity={onUpdateQuantity}
              onRemoveItem={onRemoveItem}
            />
          ))}
        </div>

        {/* Información adicional */}
        {items.length > 3 && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-blue-800 font-medium">
                  ¡Tienes {items.length} productos diferentes en tu carrito!
                </p>
                <p className="text-blue-700 mt-1">
                  Revisa las cantidades antes de proceder al checkout.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartItemList;