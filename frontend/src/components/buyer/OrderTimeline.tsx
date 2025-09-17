// frontend/src/components/buyer/OrderTimeline.tsx
// PRODUCTION_READY: Timeline visual para tracking de órdenes de compradores

import React from 'react';
import {
  CheckCircle,
  Clock,
  Truck,
  Package,
  MapPin,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { TrackingEvent, TrackingInfo } from '../../types/orders';

interface OrderTimelineProps {
  trackingInfo: TrackingInfo;
  className?: string;
}

export const OrderTimeline: React.FC<OrderTimelineProps> = ({
  trackingInfo,
  className = ''
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (timeString: string) => {
    return new Date(`1970-01-01T${timeString}`).toLocaleTimeString('es-CO', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEventIcon = (eventType: string, isCompleted: boolean) => {
    const iconClass = isCompleted ? 'text-green-600' : 'text-gray-400';

    switch (eventType.toLowerCase()) {
      case 'order_confirmed':
      case 'confirmed':
        return <CheckCircle className={`h-5 w-5 ${iconClass}`} />;
      case 'processing':
      case 'in_processing':
        return <Package className={`h-5 w-5 ${iconClass}`} />;
      case 'shipped':
      case 'in_transit':
        return <Truck className={`h-5 w-5 ${iconClass}`} />;
      case 'out_for_delivery':
        return <MapPin className={`h-5 w-5 ${iconClass}`} />;
      case 'delivered':
        return <CheckCircle className={`h-5 w-5 ${iconClass}`} />;
      default:
        return <Clock className={`h-5 w-5 ${iconClass}`} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return 'text-green-600';
      case 'shipped':
      case 'in_transit':
        return 'text-blue-600';
      case 'processing':
        return 'text-yellow-600';
      case 'cancelled':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const sortedEvents = [...trackingInfo.tracking_events].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  const currentDate = new Date();

  return (
    <div className={`bg-white rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Seguimiento de Orden
            </h3>
            <p className="text-sm text-gray-500">
              #{trackingInfo.order_number}
            </p>
          </div>
          <div className="text-right">
            <p className={`text-sm font-medium ${getStatusColor(trackingInfo.status)}`}>
              {trackingInfo.status.replace('_', ' ').toUpperCase()}
            </p>
            {trackingInfo.current_location && (
              <p className="text-xs text-gray-500">
                {trackingInfo.current_location}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Tracking Summary */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Package className="h-6 w-6 text-blue-600" />
            </div>
            <p className="text-xs text-gray-500">Estado Actual</p>
            <p className="text-sm font-medium text-gray-900">
              {trackingInfo.status.replace('_', ' ')}
            </p>
          </div>

          {trackingInfo.carrier_info && (
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Truck className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-xs text-gray-500">Transportadora</p>
              <p className="text-sm font-medium text-gray-900">
                {trackingInfo.carrier_info.name}
              </p>
            </div>
          )}

          {trackingInfo.estimated_delivery.estimated_date && (
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Calendar className="h-6 w-6 text-purple-600" />
              </div>
              <p className="text-xs text-gray-500">Entrega Estimada</p>
              <p className="text-sm font-medium text-gray-900">
                {formatDate(trackingInfo.estimated_delivery.estimated_date)}
              </p>
            </div>
          )}
        </div>

        {trackingInfo.estimated_delivery.estimated_range && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-blue-600 mr-2" />
              <p className="text-sm text-blue-800">
                Estimado de entrega: {trackingInfo.estimated_delivery.estimated_range}
                {trackingInfo.estimated_delivery.confidence && (
                  <span className="text-xs text-blue-600 ml-1">
                    ({trackingInfo.estimated_delivery.confidence})
                  </span>
                )}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Timeline */}
      <div className="px-6 py-6">
        <div className="flow-root">
          <ul className="-mb-8">
            {sortedEvents.map((event, eventIdx) => {
              const isCompleted = new Date(event.timestamp) <= currentDate && !event.is_estimated;
              const isLast = eventIdx === sortedEvents.length - 1;

              return (
                <li key={eventIdx}>
                  <div className="relative pb-8">
                    {!isLast && (
                      <span
                        className={`absolute top-5 left-5 -ml-px h-full w-0.5 ${
                          isCompleted ? 'bg-green-300' : 'bg-gray-300'
                        }`}
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex items-start space-x-3">
                      <div
                        className={`relative px-1 ${
                          isCompleted
                            ? 'bg-green-100 rounded-full'
                            : event.is_estimated
                            ? 'bg-gray-100 rounded-full'
                            : 'bg-gray-100 rounded-full'
                        }`}
                      >
                        {getEventIcon(event.type, isCompleted)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div>
                          <div className="text-sm">
                            <div className="flex items-center justify-between">
                              <span
                                className={`font-medium ${
                                  isCompleted ? 'text-gray-900' : 'text-gray-500'
                                }`}
                              >
                                {event.description}
                              </span>
                              {event.is_estimated && (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                  Estimado
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="mt-1 text-sm text-gray-500">
                            <div className="flex items-center space-x-4">
                              <span className="flex items-center">
                                <Calendar className="h-3 w-3 mr-1" />
                                {event.date}
                              </span>
                              {event.time && (
                                <span className="flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  {formatTime(event.time)}
                                </span>
                              )}
                              {event.location && (
                                <span className="flex items-center">
                                  <MapPin className="h-3 w-3 mr-1" />
                                  {event.location}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Additional carrier info */}
                          {event.carrier_info && (
                            <div className="mt-2 p-2 bg-gray-50 rounded-md">
                              <p className="text-xs text-gray-600">
                                Información adicional de la transportadora
                              </p>
                              <pre className="text-xs text-gray-500 mt-1">
                                {JSON.stringify(event.carrier_info, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      {/* Tracking URLs */}
      {(trackingInfo.tracking_urls.carrier_url || trackingInfo.carrier_info?.tracking_number) && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Enlaces de Seguimiento</h4>
          <div className="space-y-2">
            {trackingInfo.tracking_urls.carrier_url && (
              <a
                href={trackingInfo.tracking_urls.carrier_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
              >
                <Truck className="h-4 w-4 mr-1" />
                Seguir en {trackingInfo.carrier_info?.name || 'Transportadora'}
              </a>
            )}
            {trackingInfo.carrier_info?.tracking_number && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">Número de guía:</span>{' '}
                {trackingInfo.carrier_info.tracking_number}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-center">
        <p className="text-xs text-gray-500">
          Última actualización: {formatDate(trackingInfo.last_updated)}
        </p>
      </div>
    </div>
  );
};

export default OrderTimeline;