import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Breadcrumb } from '../components/ui/Breadcrumb/Breadcrumb';
import PaymentMethods from '../components/payments/PaymentMethods';
import OrderSummary from '../components/payments/OrderSummary';
import ShippingForm from '../components/payments/ShippingForm';
import { ShoppingCart, CreditCard, Truck, CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface CheckoutStep {
  id: string;
  title: string;
  icon: React.ReactNode;
  completed: boolean;
}

interface Order {
  id: number;
  order_number: string;
  total_amount: number;
  items: OrderItem[];
  shipping_address?: string;
  shipping_city?: string;
  shipping_state?: string;
}

interface OrderItem {
  id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product_image_url?: string;
}

interface ShippingData {
  name: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
}

const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuthStore();
  
  const [currentStep, setCurrentStep] = useState('shipping');
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  
  const [shippingData, setShippingData] = useState<ShippingData>({
    name: user?.full_name || user?.name || `${user?.nombre || ''} ${user?.apellido || ''}`.trim() || '',
    phone: user?.telefono || '',
    email: user?.email || '',
    address: '',
    city: '',
    state: '',
    postal_code: ''
  });

  const orderId = searchParams.get('order_id');

  const steps: CheckoutStep[] = [
    {
      id: 'shipping',
      title: 'Información de envío',
      icon: <Truck className="w-5 h-5" />,
      completed: currentStep !== 'shipping'
    },
    {
      id: 'payment',
      title: 'Método de pago',
      icon: <CreditCard className="w-5 h-5" />,
      completed: currentStep === 'confirmation'
    },
    {
      id: 'confirmation',
      title: 'Confirmación',
      icon: <CheckCircle className="w-5 h-5" />,
      completed: false
    }
  ];

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    if (!orderId) {
      navigate('/cart');
      return;
    }

    loadOrder();
  }, [orderId, user, navigate]);

  const loadOrder = async () => {
    if (!orderId) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/v1/orders/${orderId}`, {
        headers: {
          'Authorization': `Bearer ${user?.token || localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Orden no encontrada');
        }
        throw new Error('Error al cargar la orden');
      }

      const orderData = await response.json();
      setOrder(orderData);
    } catch (error) {
      console.error('Error loading order:', error);
      setError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const handleShippingSubmit = (data: ShippingData) => {
    setShippingData(data);
    setCurrentStep('payment');
  };

  const handlePaymentSuccess = (transactionData: any) => {
    setCurrentStep('confirmation');
    // Navigate to order confirmation page
    navigate(`/orders/${order?.id}/confirmation?transaction=${transactionData.reference}`);
  };

  const handlePaymentError = (error: string) => {
    setError(error);
    setProcessing(false);
  };

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando información de la orden...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-sm p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/cart')}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Volver al carrito
              </button>
              <button
                onClick={loadOrder}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Orden no encontrada</h2>
          <p className="text-gray-600 mb-6">La orden que buscas no existe o no tienes acceso a ella.</p>
          <button
            onClick={() => navigate('/marketplace')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Continuar comprando
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Breadcrumb />
          <h1 className="text-2xl font-bold text-gray-900 mt-4">Finalizar compra</h1>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep === step.id
                    ? 'border-blue-600 bg-blue-600 text-white'
                    : step.completed
                    ? 'border-green-600 bg-green-600 text-white'
                    : 'border-gray-300 text-gray-400'
                }`}>
                  {step.completed ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    step.icon
                  )}
                </div>
                <span className={`ml-3 text-sm font-medium ${
                  currentStep === step.id
                    ? 'text-blue-600'
                    : step.completed
                    ? 'text-green-600'
                    : 'text-gray-500'
                }`}>
                  {step.title}
                </span>
                {index < steps.length - 1 && (
                  <div className={`ml-6 w-12 h-0.5 ${
                    step.completed ? 'bg-green-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content Area */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm p-6">
                {currentStep === 'shipping' && (
                  <ShippingForm
                    initialData={shippingData}
                    onSubmit={handleShippingSubmit}
                    loading={processing}
                  />
                )}

                {currentStep === 'payment' && order && (
                  <PaymentMethods
                    order={order}
                    shippingData={shippingData}
                    onSuccess={handlePaymentSuccess}
                    onError={handlePaymentError}
                    loading={processing}
                    setLoading={setProcessing}
                  />
                )}

                {currentStep === 'confirmation' && (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      ¡Pago procesado correctamente!
                    </h2>
                    <p className="text-gray-600 mb-6">
                      Tu orden #{order.order_number} ha sido confirmada.
                    </p>
                    <button
                      onClick={() => navigate(`/orders/${order.id}`)}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      Ver detalles de la orden
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Order Summary Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-4">
                <OrderSummary
                  order={order}
                  shippingCost={0} // Free shipping for now
                  taxAmount={order.total_amount * 0.19} // 19% IVA
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Processing Overlay */}
      {processing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-sm w-full mx-4">
            <div className="text-center">
              <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Procesando pago
              </h3>
              <p className="text-gray-600">
                Por favor espera mientras procesamos tu pago de forma segura.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Checkout;