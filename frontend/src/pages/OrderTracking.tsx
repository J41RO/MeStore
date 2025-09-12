// ~/frontend/src/pages/OrderTracking.tsx
// PRODUCTION_READY: Página pública de tracking de órdenes

import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { 
  Package, 
  MapPin, 
  Clock, 
  Check, 
  Truck,
  Home,
  AlertCircle,
  RefreshCw,
  Eye,
  Mail
} from 'lucide-react';
import { orderService } from '../services/orderService';
import { TrackingInfo } from '../types/orders';

const OrderTracking: React.FC = () => {
  const { orderNumber } = useParams<{ orderNumber: string }>();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [trackingInfo, setTrackingInfo] = useState<TrackingInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [requestingToken, setRequestingToken] = useState(false);
  const [tokenRequested, setTokenRequested] = useState(false);

  // Load tracking information
  useEffect(() => {
    if (orderNumber) {
      loadTrackingInfo();
    }
  }, [orderNumber]);

  const loadTrackingInfo = async () => {
    if (!orderNumber) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await orderService.getPublicTracking(orderNumber);
      setTrackingInfo(response.data);
    } catch (err: any) {
      console.error('Error loading tracking info:', err);
      setError(err.message || 'Error al cargar la información de tracking');
      setTrackingInfo(null);
    } finally {
      setLoading(false);
    }
  };

  // Request tracking token
  const handleRequestToken = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderNumber || !email.trim()) return;

    try {
      setRequestingToken(true);
      setError(null);
      
      await orderService.generateTrackingToken(orderNumber, email);
      setTokenRequested(true);
    } catch (err: any) {
      console.error('Error requesting tracking token:', err);
      setError(err.message || 'Error al solicitar el token de tracking');
    } finally {
      setRequestingToken(false);
    }
  };

  // Format date
  const formatDateTime = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get status icon
  const getStatusIcon = (type: string, isEstimated: boolean) => {
    const iconClass = `h-5 w-5 ${isEstimated ? 'text-gray-400' : 'text-blue-600'}`;
    
    switch (type.toLowerCase()) {
      case 'order_created':
      case 'created':
        return <Package className={iconClass} />;
      case 'confirmed':
        return <Check className={iconClass} />;
      case 'shipped':
      case 'in_transit':
        return <Truck className={iconClass} />;
      case 'delivered':
        return <Home className={iconClass} />;
      default:
        return <MapPin className={iconClass} />;
    }
  };

  if (!orderNumber) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            Número de orden inválido
          </h1>
          <p className="text-gray-600">
            Por favor verifica el enlace de tracking.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Seguimiento de Orden
                </h1>
                <p className="text-gray-600">
                  {orderNumber}
                </p>
              </div>
            </div>
            
            <button
              onClick={loadTrackingInfo}
              disabled={loading}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualizar
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando información...</p>
          </div>
        )}

        {/* Error State - No tracking info and no token */}
        {error && !trackingInfo && !token && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="text-center mb-8">
              <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Acceso Restringido
              </h2>
              <p className="text-gray-600">
                Esta orden requiere verificación. Ingresa tu email para recibir un enlace de acceso.
              </p>
            </div>

            {!tokenRequested ? (
              <form onSubmit={handleRequestToken} className="max-w-md mx-auto">
                <div className="mb-4">
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email del Cliente
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <input
                      type="email"
                      id="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="tu@email.com"
                      required
                      className="block w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                
                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}
                
                <button
                  type="submit"
                  disabled={requestingToken}
                  className="w-full flex items-center justify-center px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {requestingToken ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Mail className="h-4 w-4 mr-2" />
                      Solicitar Acceso
                    </>
                  )}
                </button>
              </form>
            ) : (
              <div className="text-center">
                <div className="inline-flex items-center px-4 py-2 bg-green-50 text-green-800 rounded-lg mb-4">
                  <Check className="h-5 w-5 mr-2" />
                  Enlace enviado a tu email
                </div>
                <p className="text-sm text-gray-600">
                  Revisa tu bandeja de entrada y haz clic en el enlace para acceder al tracking.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Tracking Information */}
        {trackingInfo && !loading && (
          <div className="space-y-6">
            {/* Status Summary */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Estado de la Orden
                </h2>
                <span className="inline-flex px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full">
                  {trackingInfo.status}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="flex items-center mb-2">
                    <MapPin className="h-5 w-5 text-gray-400 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Ubicación Actual</span>
                  </div>
                  <p className="text-lg font-semibold text-gray-900">
                    {trackingInfo.current_location}
                  </p>
                </div>
                
                <div>
                  <div className="flex items-center mb-2">
                    <Clock className="h-5 w-5 text-gray-400 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Entrega Estimada</span>
                  </div>
                  <p className="text-lg font-semibold text-gray-900">
                    {trackingInfo.estimated_delivery.estimated_date || 'Por confirmar'}
                  </p>
                  {trackingInfo.estimated_delivery.estimated_range && (
                    <p className="text-sm text-gray-600">
                      {trackingInfo.estimated_delivery.estimated_range}
                    </p>
                  )}
                </div>
                
                <div>
                  <div className="flex items-center mb-2">
                    <Truck className="h-5 w-5 text-gray-400 mr-2" />
                    <span className="text-sm font-medium text-gray-600">Transportadora</span>
                  </div>
                  <p className="text-lg font-semibold text-gray-900">
                    {trackingInfo.carrier_info?.name || 'MeStore Express'}
                  </p>
                </div>
              </div>
            </div>

            {/* Tracking Timeline */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Historial de Tracking
              </h3>
              
              <div className="relative">
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                
                <div className="space-y-6">
                  {trackingInfo.tracking_events.map((event, index) => (
                    <div key={index} className="relative flex items-start">
                      <div className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 ${
                        event.is_estimated 
                          ? 'bg-gray-50 border-gray-200' 
                          : 'bg-white border-blue-200'
                      }`}>
                        {getStatusIcon(event.type, event.is_estimated)}
                      </div>
                      
                      <div className="ml-6 flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className={`text-sm font-medium ${
                            event.is_estimated ? 'text-gray-500' : 'text-gray-900'
                          }`}>
                            {event.description}
                          </p>
                          
                          {event.is_estimated && (
                            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                              Estimado
                            </span>
                          )}
                        </div>
                        
                        <div className="mt-1 flex items-center text-sm text-gray-500 space-x-4">
                          <span>{event.date}</span>
                          <span>{event.time}</span>
                          {event.location && (
                            <>
                              <span>•</span>
                              <span>{event.location}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Delivery Address */}
            {trackingInfo.delivery_address && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center mb-4">
                  <MapPin className="h-5 w-5 text-gray-400 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Dirección de Entrega
                  </h3>
                </div>
                
                <div className="text-gray-600">
                  <p>{trackingInfo.delivery_address.city}</p>
                </div>
              </div>
            )}

            {/* Carrier Info */}
            {trackingInfo.carrier_info && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Truck className="h-5 w-5 text-gray-400 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      Información de Transportadora
                    </h3>
                  </div>
                  
                  {trackingInfo.tracking_urls.carrier_url && (
                    <a
                      href={trackingInfo.tracking_urls.carrier_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100"
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      Ver en {trackingInfo.carrier_info.name}
                    </a>
                  )}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Transportadora:</span>
                    <p className="font-medium">{trackingInfo.carrier_info.name}</p>
                  </div>
                  
                  <div>
                    <span className="text-gray-600">Número de tracking:</span>
                    <p className="font-mono font-medium">{trackingInfo.carrier_info.tracking_number}</p>
                  </div>
                  
                  <div>
                    <span className="text-gray-600">Teléfono:</span>
                    <p className="font-medium">{trackingInfo.carrier_info.contact.phone}</p>
                  </div>
                  
                  <div>
                    <span className="text-gray-600">Sitio web:</span>
                    <a 
                      href={trackingInfo.carrier_info.contact.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {trackingInfo.carrier_info.contact.website}
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Last Updated */}
            <div className="text-center text-sm text-gray-500">
              Última actualización: {formatDateTime(trackingInfo.last_updated)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTracking;