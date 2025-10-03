import React, { useEffect, useState } from 'react';
import { Copy, Check, MapPin, Clock, AlertTriangle, Banknote, Info } from 'lucide-react';

interface EfectyInstructionsProps {
  orderId: string;
  amount: number;
  customerEmail: string;
  customerPhone?: string;
}

interface EfectyPaymentData {
  success: boolean;
  payment_code: string;
  barcode_data: string | null;
  expires_at: string;
  transaction_id: string;
  message?: string;
}

export const EfectyInstructions: React.FC<EfectyInstructionsProps> = ({
  orderId,
  amount,
  customerEmail,
  customerPhone
}) => {
  const [paymentCode, setPaymentCode] = useState<string | null>(null);
  const [barcode, setBarcode] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    generateEfectyCode();
  }, []);

  const generateEfectyCode = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get auth token
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

      const response = await fetch('http://192.168.1.137:8000/api/v1/payments/process/efecty', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          order_id: orderId,
          amount,
          customer_email: customerEmail,
          customer_phone: customerPhone || '',
          expiration_hours: 72 // 3 days
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.message || 'Error al generar código Efecty');
      }

      const result: EfectyPaymentData = await response.json();

      if (result.success) {
        setPaymentCode(result.payment_code);
        setBarcode(result.barcode_data);
        setExpiresAt(result.expires_at);
      } else {
        throw new Error(result.message || 'No se pudo generar el código de pago');
      }
    } catch (err) {
      console.error('Failed to generate Efecty code:', err);
      const errorMsg = err instanceof Error ? err.message : 'Error al generar código Efecty';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (paymentCode) {
      navigator.clipboard.writeText(paymentCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const openEfectyLocator = () => {
    window.open('https://www.efecty.com.co/localizador-de-oficinas/', '_blank');
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mx-auto mb-4"></div>
          <p className="text-gray-700 font-medium">Generando código de pago...</p>
          <p className="text-sm text-gray-500 mt-2">Por favor espera un momento</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="text-red-600 mr-2" size={24} />
          <h3 className="text-lg font-semibold text-red-700">Error al Generar Código</h3>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
        <button
          onClick={generateEfectyCode}
          className="w-full bg-yellow-600 text-white p-3 rounded-lg hover:bg-yellow-700 transition-colors"
        >
          Intentar Nuevamente
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-center mb-4">
        <Banknote className="text-yellow-600 mr-2" size={28} />
        <h2 className="text-2xl font-bold text-gray-900">Pago en Efectivo - Efecty</h2>
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-r-lg">
        <div className="flex items-start">
          <Info className="text-yellow-700 mr-2 mt-0.5 flex-shrink-0" size={20} />
          <p className="text-yellow-800 font-semibold">
            Paga en efectivo en cualquiera de los 20,000+ puntos Efecty en toda Colombia
          </p>
        </div>
      </div>

      {/* Payment code */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 mb-6 border-2 border-yellow-300">
        <label className="block text-sm font-medium text-gray-700 mb-3 text-center">
          Código de Pago
        </label>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-white p-4 border-2 border-yellow-500 rounded-lg text-center shadow-inner">
            <span className="text-3xl font-mono font-bold text-gray-900">{paymentCode}</span>
          </div>
          <button
            onClick={copyCode}
            className="p-4 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors shadow-md"
            title="Copiar código"
          >
            {copied ? <Check size={24} /> : <Copy size={24} />}
          </button>
        </div>
        {copied && (
          <p className="text-center text-green-600 text-sm mt-2 font-medium">
            Código copiado al portapapeles
          </p>
        )}
      </div>

      {/* Barcode */}
      {barcode && (
        <div className="mb-6 bg-white p-6 rounded-lg border-2 border-gray-200">
          <p className="text-center text-sm font-medium text-gray-700 mb-3">
            Código de Barras (para escanear en el punto Efecty)
          </p>
          <div className="bg-white p-4 flex justify-center">
            <img
              src={`data:image/png;base64,${barcode}`}
              alt="Código de barras Efecty"
              className="max-w-full h-auto"
              style={{ maxHeight: '120px' }}
            />
          </div>
        </div>
      )}

      {/* Amount */}
      <div className="bg-blue-50 rounded-lg p-5 mb-6 border-2 border-blue-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Banknote className="text-blue-600 mr-2" size={24} />
            <span className="text-gray-700 font-medium">Monto a pagar:</span>
          </div>
          <span className="text-3xl font-bold text-blue-600">
            ${amount.toLocaleString('es-CO')} COP
          </span>
        </div>
      </div>

      {/* Expiration */}
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <Clock className="text-red-600 mr-2 mt-0.5 flex-shrink-0" size={20} />
          <div>
            <p className="text-red-800 font-semibold">
              Válido hasta: {new Date(expiresAt!).toLocaleString('es-CO', {
                dateStyle: 'full',
                timeStyle: 'short'
              })}
            </p>
            <p className="text-sm text-red-600 mt-1">
              Debes pagar antes de esta fecha o el código expirará
            </p>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="space-y-4 mb-6">
        <h3 className="font-semibold text-lg text-gray-900 flex items-center">
          <Info className="mr-2 text-blue-600" size={20} />
          Instrucciones de Pago
        </h3>
        <ol className="list-decimal list-inside space-y-3 text-gray-700 bg-gray-50 p-4 rounded-lg">
          <li className="pl-2">
            <strong>Dirígete</strong> a cualquier punto Efecty con el código de pago o captura de pantalla
          </li>
          <li className="pl-2">
            <strong>Presenta</strong> el código de pago al cajero: <span className="font-mono bg-yellow-100 px-2 py-1 rounded">{paymentCode}</span>
          </li>
          <li className="pl-2">
            <strong>El cajero</strong> escaneará el código de barras o ingresará el código manualmente
          </li>
          <li className="pl-2">
            <strong>Paga</strong> el monto en efectivo: <span className="font-semibold">${amount.toLocaleString('es-CO')} COP</span>
          </li>
          <li className="pl-2">
            <strong>Guarda</strong> el recibo como comprobante de pago
          </li>
          <li className="pl-2">
            <strong>Tu orden</strong> será procesada automáticamente en <span className="font-semibold">10-30 minutos</span> después del pago
          </li>
        </ol>
      </div>

      {/* Additional Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h4 className="font-semibold text-gray-900 mb-2">Información Adicional</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• No se requiere cuenta bancaria</li>
          <li>• Sin costos adicionales ni comisiones</li>
          <li>• Confirmación por email una vez procesado el pago</li>
          <li>• Soporte disponible en {customerEmail}</li>
        </ul>
      </div>

      {/* Find location button */}
      <button
        onClick={openEfectyLocator}
        className="w-full bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-semibold shadow-md"
      >
        <MapPin size={20} />
        Encontrar Punto Efecty Cercano
      </button>

      {/* Security notice */}
      <div className="mt-6 text-center text-xs text-gray-500">
        <p>Este código de pago es válido únicamente para esta transacción</p>
        <p className="mt-1">No compartas este código con terceros</p>
      </div>
    </div>
  );
};

export default EfectyInstructions;
