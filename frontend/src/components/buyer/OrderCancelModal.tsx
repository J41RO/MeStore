// frontend/src/components/buyer/OrderCancelModal.tsx
// Modal component for cancelling orders with reason

import React, { useState } from 'react';
import { X, AlertTriangle, CheckCircle } from 'lucide-react';
import { orderService } from '../../services/orderService';

interface OrderCancelModalProps {
  orderId: string;
  orderNumber: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const OrderCancelModal: React.FC<OrderCancelModalProps> = ({
  orderId,
  orderNumber,
  isOpen,
  onClose,
  onSuccess
}) => {
  const [reason, setReason] = useState('');
  const [refundRequested, setRefundRequested] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleCancel = async () => {
    if (!reason.trim()) {
      setError('Por favor proporciona un motivo para la cancelación');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await orderService.cancelBuyerOrder(orderId, reason, refundRequested);

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      } else {
        setError('No se pudo cancelar la orden. Intenta nuevamente.');
      }
    } catch (err: any) {
      console.error('Error cancelling order:', err);
      setError(err.message || 'Error al cancelar la orden');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setReason('');
    setRefundRequested(true);
    setError(null);
    setSuccess(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={handleClose}
        />

        {/* Modal Panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="h-6 w-6 text-red-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">
                Cancelar Orden
              </h3>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
              disabled={loading}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            {success ? (
              <div className="text-center py-8">
                <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  Orden Cancelada Exitosamente
                </h4>
                <p className="text-gray-600">
                  La orden #{orderNumber} ha sido cancelada.
                  {refundRequested && ' Se procesará el reembolso en breve.'}
                </p>
              </div>
            ) : (
              <>
                <div className="mb-4">
                  <p className="text-gray-700">
                    Estás a punto de cancelar la orden <strong>#{orderNumber}</strong>.
                    Esta acción no se puede deshacer.
                  </p>
                </div>

                {error && (
                  <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}

                <div className="mb-4">
                  <label
                    htmlFor="cancellation-reason"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Motivo de cancelación <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="cancellation-reason"
                    rows={4}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Por favor explica el motivo de la cancelación..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    disabled={loading}
                    required
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Mínimo 10 caracteres
                  </p>
                </div>

                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={refundRequested}
                      onChange={(e) => setRefundRequested(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      disabled={loading}
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Solicitar reembolso
                    </span>
                  </label>
                  <p className="ml-6 mt-1 text-xs text-gray-500">
                    El reembolso se procesará según la política de la tienda
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                  <div className="flex">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0" />
                    <div className="text-sm text-yellow-800">
                      <p className="font-medium">Importante:</p>
                      <ul className="mt-2 list-disc list-inside space-y-1">
                        <li>La cancelación es irreversible</li>
                        <li>El reembolso puede tardar 3-5 días hábiles</li>
                        <li>Los productos en tránsito deben ser devueltos</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          {!success && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end space-x-3">
              <button
                onClick={handleClose}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
                disabled={loading}
              >
                Volver
              </button>
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center"
                disabled={loading || reason.trim().length < 10}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Cancelando...
                  </>
                ) : (
                  'Confirmar Cancelación'
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderCancelModal;
