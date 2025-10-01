/**
 * WompiCheckout Component
 *
 * Integrates Wompi payment widget for secure payment processing.
 * Handles payment initialization, widget management, and result callbacks.
 *
 * Features:
 * - PCI compliant (Wompi handles card data)
 * - 3D Secure automatic handling
 * - PSE bank transfer support
 * - Real-time payment status updates
 *
 * @author payment-systems-ai
 * @date 2025-10-01
 */

import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, CheckCircle, Loader } from 'lucide-react';

// Declare Wompi widget on window object
declare global {
  interface Window {
    WidgetCheckout: any;
  }
}

interface WompiCheckoutProps {
  /** Order ID for payment processing */
  orderId: number | string;

  /** Amount in COP (Colombian Pesos) */
  amount: number;

  /** Customer email for payment notifications */
  customerEmail: string;

  /** Payment reference (e.g., ORDER-123-20251001) */
  reference: string;

  /** Wompi public key */
  publicKey: string;

  /** URL to redirect after payment completion */
  redirectUrl?: string;

  /** Callback when payment succeeds */
  onSuccess?: (transaction: any) => void;

  /** Callback when payment fails */
  onError?: (error: string) => void;

  /** Callback when payment is closed/cancelled */
  onClose?: () => void;

  /** Currency code (default: COP) */
  currency?: string;

  /** Payment methods to enable */
  paymentMethods?: ('CARD' | 'PSE' | 'NEQUI')[];
}

const WompiCheckout: React.FC<WompiCheckoutProps> = ({
  orderId,
  amount,
  customerEmail,
  reference,
  publicKey,
  redirectUrl,
  onSuccess,
  onError,
  onClose,
  currency = 'COP',
  paymentMethods = ['CARD', 'PSE']
}) => {
  const widgetRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [widgetStatus, setWidgetStatus] = useState<'initializing' | 'ready' | 'processing' | 'completed' | 'failed'>('initializing');

  useEffect(() => {
    // Validate required props
    if (!publicKey) {
      setError('Wompi public key not configured');
      setLoading(false);
      return;
    }

    if (amount <= 0) {
      setError('Invalid payment amount');
      setLoading(false);
      return;
    }

    if (!customerEmail || !reference) {
      setError('Missing required payment information');
      setLoading(false);
      return;
    }

    // Wait for Wompi widget to load
    const checkWidget = setInterval(() => {
      if (window.WidgetCheckout) {
        clearInterval(checkWidget);
        initializeWidget();
      }
    }, 100);

    // Timeout after 10 seconds
    const timeout = setTimeout(() => {
      if (!window.WidgetCheckout) {
        clearInterval(checkWidget);
        setError('Payment widget failed to load. Please refresh the page.');
        setLoading(false);
      }
    }, 10000);

    return () => {
      clearInterval(checkWidget);
      clearTimeout(timeout);

      // Clean up widget on unmount
      if (widgetRef.current && typeof widgetRef.current.close === 'function') {
        widgetRef.current.close();
      }
    };
  }, [publicKey, amount, customerEmail, reference]);

  const initializeWidget = () => {
    try {
      setLoading(true);
      setError(null);

      // Convert amount to cents (Wompi requires cents)
      const amountInCents = Math.round(amount * 100);

      // Build redirect URL
      const finalRedirectUrl = redirectUrl || `${window.location.origin}/checkout/confirmation?order_id=${orderId}`;

      // Initialize Wompi widget
      const widget = new window.WidgetCheckout({
        currency: currency,
        amountInCents: amountInCents,
        reference: reference,
        publicKey: publicKey,
        redirectUrl: finalRedirectUrl,
        customerData: {
          email: customerEmail
        }
      });

      widgetRef.current = widget;

      // Open widget and handle result
      widget.open((result: any) => {
        console.log('Wompi widget result:', result);

        if (result.transaction) {
          const transaction = result.transaction;
          setWidgetStatus('completed');

          // Handle different transaction statuses
          switch (transaction.status) {
            case 'APPROVED':
              console.log('Payment approved:', transaction.id);
              if (onSuccess) {
                onSuccess(transaction);
              }
              break;

            case 'PENDING':
              console.log('Payment pending:', transaction.id);
              setWidgetStatus('processing');
              // Redirect to confirmation page for status polling
              if (redirectUrl) {
                window.location.href = finalRedirectUrl;
              }
              break;

            case 'DECLINED':
            case 'ERROR':
              console.error('Payment failed:', transaction.status_message);
              setWidgetStatus('failed');
              setError(transaction.status_message || 'Payment declined');
              if (onError) {
                onError(transaction.status_message || 'Payment failed');
              }
              break;

            case 'VOIDED':
              console.log('Payment cancelled by user');
              setWidgetStatus('failed');
              if (onClose) {
                onClose();
              }
              break;

            default:
              console.warn('Unknown transaction status:', transaction.status);
              setWidgetStatus('processing');
          }
        } else {
          // Widget closed without transaction
          console.log('Widget closed without completing transaction');
          setWidgetStatus('failed');
          if (onClose) {
            onClose();
          }
        }
      });

      setLoading(false);
      setWidgetStatus('ready');

    } catch (err) {
      console.error('Error initializing Wompi widget:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize payment widget');
      setLoading(false);
      setWidgetStatus('failed');
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(value);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <Loader className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-700 font-medium">Cargando pasarela de pago segura...</p>
        <p className="text-sm text-gray-500 mt-2">Un momento por favor</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-red-900 font-semibold mb-1">Error al procesar el pago</h3>
            <p className="text-red-700 text-sm mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render success state (after widget processes)
  if (widgetStatus === 'completed') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-green-900 font-semibold mb-1">Pago procesado exitosamente</h3>
            <p className="text-green-700 text-sm">
              Tu pago de {formatCurrency(amount)} ha sido procesado correctamente.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render processing state
  if (widgetStatus === 'processing') {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <Loader className="w-6 h-6 text-blue-600 animate-spin flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-blue-900 font-semibold mb-1">Procesando pago...</h3>
            <p className="text-blue-700 text-sm">
              Tu pago de {formatCurrency(amount)} está siendo procesado. Esto puede tomar unos momentos.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Widget container (hidden - Wompi creates its own modal)
  return (
    <div ref={containerRef} className="wompi-checkout-container">
      {/* Widget renders in modal/overlay */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <div className="flex-1">
            <h3 className="text-blue-900 font-semibold mb-2">Pago Seguro con Wompi</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p><strong>Monto:</strong> {formatCurrency(amount)}</p>
              <p><strong>Referencia:</strong> {reference}</p>
              <p className="text-xs text-gray-500 mt-4">
                Tu información de pago está protegida con encriptación de nivel bancario.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WompiCheckout;
