// frontend/src/components/buyer/OrderTrackingModal.tsx
// Modal component for displaying order tracking information

import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { orderService } from '../../services/orderService';
import { TrackingInfo } from '../../types/orders';
import { OrderTimeline } from './OrderTimeline';

interface OrderTrackingModalProps {
  orderId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const OrderTrackingModal: React.FC<OrderTrackingModalProps> = ({
  orderId,
  isOpen,
  onClose
}) => {
  const [tracking, setTracking] = useState<TrackingInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && orderId) {
      loadTracking();
    }
  }, [isOpen, orderId]);

  const loadTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderService.getBuyerOrderTracking(orderId);
      if (response.success && response.data) {
        setTracking(response.data);
      } else {
        setError('No se pudo cargar la información de seguimiento');
      }
    } catch (err: any) {
      console.error('Error loading tracking:', err);
      setError(err.message || 'Error al cargar el seguimiento');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal Panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Seguimiento de Orden
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-500 mt-4">Cargando información de seguimiento...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-red-800">{error}</p>
                </div>
                <button
                  onClick={loadTracking}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Reintentar
                </button>
              </div>
            ) : tracking ? (
              <OrderTimeline trackingInfo={tracking} />
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">No hay información de seguimiento disponible</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderTrackingModal;
