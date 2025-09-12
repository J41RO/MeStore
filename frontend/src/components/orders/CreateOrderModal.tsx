// ~/frontend/src/components/orders/CreateOrderModal.tsx
// PRODUCTION_READY: Modal para crear nuevas órdenes enterprise

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Plus, 
  Minus, 
  Search, 
  Package,
  MapPin,
  ShoppingCart,
  AlertCircle
} from 'lucide-react';
import { orderService } from '../../services/orderService';
import { CreateOrderRequest } from '../../types/orders';

interface Product {
  id: string;
  name: string;
  price: number;
  image_url?: string;
  stock: number;
  sku?: string;
}

interface OrderItem {
  product_id: string;
  product: Product;
  quantity: number;
  variant_attributes?: Record<string, string>;
}

interface CreateOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateOrderModal: React.FC<CreateOrderModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [step, setStep] = useState(1); // 1: Products, 2: Shipping, 3: Review
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form data
  const [items, setItems] = useState<OrderItem[]>([]);
  const [shippingInfo, setShippingInfo] = useState({
    shipping_name: '',
    shipping_address: '',
    shipping_city: '',
    shipping_phone: '',
    notes: ''
  });
  
  // Product search
  const [products, setProducts] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  // const [searchLoading, setSearchLoading] = useState(false); // Future: for API search

  // Mock products for demo - replace with actual API call
  const mockProducts: Product[] = [
    {
      id: '1',
      name: 'Producto Demo 1',
      price: 50000,
      stock: 10,
      sku: 'DEMO-001',
      image_url: undefined
    },
    {
      id: '2', 
      name: 'Producto Demo 2',
      price: 75000,
      stock: 5,
      sku: 'DEMO-002',
      image_url: undefined
    }
  ];

  useEffect(() => {
    if (isOpen) {
      setProducts(mockProducts);
    }
  }, [isOpen]);

  // Reset form
  const resetForm = () => {
    setStep(1);
    setItems([]);
    setShippingInfo({
      shipping_name: '',
      shipping_address: '',
      shipping_city: '',
      shipping_phone: '',
      notes: ''
    });
    setError(null);
  };

  // Handle close
  const handleClose = () => {
    resetForm();
    onClose();
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Add product to order
  const addProduct = (product: Product) => {
    const existingItem = items.find(item => item.product_id === product.id);
    
    if (existingItem) {
      if (existingItem.quantity < product.stock) {
        setItems(items.map(item => 
          item.product_id === product.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        ));
      }
    } else {
      setItems([...items, {
        product_id: product.id,
        product: product,
        quantity: 1,
        variant_attributes: {}
      }]);
    }
  };

  // Update item quantity
  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      setItems(items.filter(item => item.product_id !== productId));
    } else {
      const product = products.find(p => p.id === productId);
      if (product && quantity <= product.stock) {
        setItems(items.map(item => 
          item.product_id === productId 
            ? { ...item, quantity }
            : item
        ));
      }
    }
  };

  // Remove item
  const removeItem = (productId: string) => {
    setItems(items.filter(item => item.product_id !== productId));
  };

  // Calculate total
  const calculateTotal = (): number => {
    return items.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (items.length === 0) {
      setError('Agrega al menos un producto a la orden');
      return;
    }

    if (!shippingInfo.shipping_name.trim() || !shippingInfo.shipping_address.trim()) {
      setError('Complete la información de envío obligatoria');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const orderData: CreateOrderRequest = {
        items: items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          variant_attributes: item.variant_attributes
        })),
        ...shippingInfo
      };

      await orderService.createOrder(orderData);
      onSuccess();
      handleClose();
    } catch (err: any) {
      console.error('Error creating order:', err);
      setError(err.message || 'Error al crear la orden');
    } finally {
      setLoading(false);
    }
  };

  // Filtered products
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <ShoppingCart className="h-6 w-6 text-blue-600 mr-3" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Nueva Orden
              </h2>
              <p className="text-sm text-gray-500">
                Paso {step} de 3
              </p>
            </div>
          </div>
          
          <button
            onClick={handleClose}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            {[1, 2, 3].map((stepNum) => (
              <div key={stepNum} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  stepNum === step 
                    ? 'bg-blue-600 text-white'
                    : stepNum < step
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {stepNum}
                </div>
                
                <span className={`ml-2 text-sm ${
                  stepNum === step ? 'text-blue-600 font-medium' : 'text-gray-500'
                }`}>
                  {stepNum === 1 ? 'Productos' : stepNum === 2 ? 'Envío' : 'Revisar'}
                </span>
                
                {stepNum < 3 && (
                  <div className={`w-12 h-0.5 mx-4 ${
                    stepNum < step ? 'bg-green-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Step 1: Products */}
          {step === 1 && (
            <div className="space-y-6">
              {/* Product Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Buscar Productos
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    placeholder="Buscar por nombre o SKU..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Products Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredProducts.map((product) => (
                  <div key={product.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start space-x-4">
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                          <Package className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                      
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{product.name}</h4>
                        {product.sku && (
                          <p className="text-sm text-gray-500">SKU: {product.sku}</p>
                        )}
                        <p className="text-lg font-semibold text-gray-900 mt-1">
                          {formatCurrency(product.price)}
                        </p>
                        <p className="text-sm text-gray-500">
                          Stock: {product.stock}
                        </p>
                        
                        <button
                          onClick={() => addProduct(product)}
                          className="mt-2 flex items-center px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          Agregar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Selected Items */}
              {items.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">
                    Productos Seleccionados ({items.length})
                  </h3>
                  
                  <div className="space-y-3">
                    {items.map((item) => (
                      <div key={item.product_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {item.product.image_url ? (
                            <img
                              src={item.product.image_url}
                              alt={item.product.name}
                              className="w-10 h-10 object-cover rounded"
                            />
                          ) : (
                            <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                              <Package className="h-5 w-5 text-gray-400" />
                            </div>
                          )}
                          
                          <div>
                            <h5 className="font-medium text-gray-900">{item.product.name}</h5>
                            <p className="text-sm text-gray-500">
                              {formatCurrency(item.product.price)} × {item.quantity}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                              className="p-1 text-gray-400 hover:text-gray-600"
                            >
                              <Minus className="h-4 w-4" />
                            </button>
                            
                            <span className="font-medium">{item.quantity}</span>
                            
                            <button
                              onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                              disabled={item.quantity >= item.product.stock}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                            >
                              <Plus className="h-4 w-4" />
                            </button>
                          </div>
                          
                          <span className="font-semibold text-gray-900 min-w-[80px] text-right">
                            {formatCurrency(item.product.price * item.quantity)}
                          </span>
                          
                          <button
                            onClick={() => removeItem(item.product_id)}
                            className="p-1 text-red-400 hover:text-red-600"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                    
                    {/* Total */}
                    <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                      <span className="text-lg font-medium text-gray-900">Total:</span>
                      <span className="text-xl font-bold text-gray-900">
                        {formatCurrency(calculateTotal())}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Shipping */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="flex items-center mb-4">
                <MapPin className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">
                  Información de Envío
                </h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre del Destinatario *
                  </label>
                  <input
                    type="text"
                    value={shippingInfo.shipping_name}
                    onChange={(e) => setShippingInfo({...shippingInfo, shipping_name: e.target.value})}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Juan Pérez"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ciudad
                  </label>
                  <input
                    type="text"
                    value={shippingInfo.shipping_city}
                    onChange={(e) => setShippingInfo({...shippingInfo, shipping_city: e.target.value})}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Bogotá"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dirección de Envío *
                </label>
                <input
                  type="text"
                  value={shippingInfo.shipping_address}
                  onChange={(e) => setShippingInfo({...shippingInfo, shipping_address: e.target.value})}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Calle 123 #45-67, Barrio Centro"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono de Contacto
                </label>
                <input
                  type="tel"
                  value={shippingInfo.shipping_phone}
                  onChange={(e) => setShippingInfo({...shippingInfo, shipping_phone: e.target.value})}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="+57 300 123 4567"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notas Especiales
                </label>
                <textarea
                  value={shippingInfo.notes}
                  onChange={(e) => setShippingInfo({...shippingInfo, notes: e.target.value})}
                  rows={3}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Instrucciones especiales de entrega..."
                />
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Revisar Orden
              </h3>
              
              {/* Order Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Resumen</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Productos:</span>
                    <span>{items.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total de artículos:</span>
                    <span>{items.reduce((sum, item) => sum + item.quantity, 0)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-semibold pt-2 border-t">
                    <span>Total:</span>
                    <span>{formatCurrency(calculateTotal())}</span>
                  </div>
                </div>
              </div>
              
              {/* Items Review */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Productos</h4>
                <div className="space-y-2">
                  {items.map((item) => (
                    <div key={item.product_id} className="flex justify-between text-sm">
                      <span>{item.product.name} × {item.quantity}</span>
                      <span>{formatCurrency(item.product.price * item.quantity)}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Shipping Review */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Información de Envío</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Destinatario:</strong> {shippingInfo.shipping_name}</p>
                  <p><strong>Dirección:</strong> {shippingInfo.shipping_address}</p>
                  {shippingInfo.shipping_city && (
                    <p><strong>Ciudad:</strong> {shippingInfo.shipping_city}</p>
                  )}
                  {shippingInfo.shipping_phone && (
                    <p><strong>Teléfono:</strong> {shippingInfo.shipping_phone}</p>
                  )}
                  {shippingInfo.notes && (
                    <p><strong>Notas:</strong> {shippingInfo.notes}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
          <div className="flex space-x-3">
            {step > 1 && (
              <button
                onClick={() => setStep(step - 1)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Anterior
              </button>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancelar
            </button>
            
            {step < 3 ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={step === 1 && items.length === 0}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Creando...' : 'Crear Orden'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateOrderModal;