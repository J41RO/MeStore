/**
 * Componente para generar, visualizar y gestionar códigos QR
 * Archivo: frontend/src/components/admin/QRGeneratorForm.tsx
 * Autor: Sistema de desarrollo
 * Fecha: 2025-01-15
 * Propósito: Interfaz completa para generación de QRs de tracking interno
 */

import React, { useState, useEffect } from 'react';
import { QrCode, Download, Eye, Printer, RefreshCw, Camera, CheckCircle, AlertCircle } from 'lucide-react';

interface QRGeneratorFormProps {
  queueId: number;
  trackingNumber: string;
  productName: string;
  onQRGenerated: (result: any) => void;
  onClose: () => void;
}

interface QRInfo {
  has_qr: boolean;
  internal_id?: string;
  qr_filename?: string;
  generation_date?: string;
}

export const QRGeneratorForm: React.FC<QRGeneratorFormProps> = ({
  queueId,
  trackingNumber,
  productName,
  onQRGenerated,
  onClose
}) => {
  const [qrInfo, setQrInfo] = useState<QRInfo | null>(null);
  const [generating, setGenerating] = useState(false);
  const [qrStyle, setQrStyle] = useState('standard');
  const [showScanner, setShowScanner] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQRInfo();
  }, [queueId]);

  const loadQRInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/qr-info`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setQrInfo(data);
      } else if (response.status === 403) {
        setError('No tienes permisos para acceder a esta funcionalidad');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error al cargar información del QR');
      }
    } catch (error) {
      console.error('Error loading QR info:', error);
      setError('Error de conexión al cargar información del QR');
    } finally {
      setLoading(false);
    }
  };

  const generateQR = async () => {
    setGenerating(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/generate-qr?style=${qrStyle}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await loadQRInfo();
          onQRGenerated(result);
          setError(null);
        } else {
          setError(result.message || 'Error al generar QR');
        }
      } else if (response.status === 403) {
        setError('No tienes permisos para generar códigos QR');
      } else {
        const error = await response.json();
        setError(error.detail || 'No se pudo generar QR');
      }
    } catch (error) {
      console.error('Error generating QR:', error);
      setError('Error de conexión al generar QR');
    } finally {
      setGenerating(false);
    }
  };

  const downloadQR = async (filename: string, type: 'qr' | 'label') => {
    try {
      const token = localStorage.getItem('access_token');
      const endpoint = type === 'qr' ? 'qr-codes' : 'labels';
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/${endpoint}/${filename}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('Error al descargar archivo');
      }
    } catch (error) {
      console.error('Error downloading file:', error);
      setError('Error de conexión al descargar archivo');
    }
  };

  const regenerateQR = async () => {
    setGenerating(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/regenerate-qr?style=${qrStyle}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await loadQRInfo();
          setError(null);
          alert('QR regenerado exitosamente');
        } else {
          setError(result.message || 'Error al regenerar QR');
        }
      } else {
        const error = await response.json();
        setError(error.detail || 'Error al regenerar QR');
      }
    } catch (error) {
      console.error('Error regenerating QR:', error);
      setError('Error de conexión al regenerar QR');
    } finally {
      setGenerating(false);
    }
  };

  const testQRDecoding = async () => {
    if (!qrInfo?.internal_id) return;
    
    try {
      const mockQRContent = `MESTORE:${qrInfo.internal_id}|${trackingNumber}|http://192.168.1.137:5173/admin-secure-portal/product/${qrInfo.internal_id}`;
      
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/qr/decode`,
        {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: `qr_content=${encodeURIComponent(mockQRContent)}`
        }
      );

      if (response.ok) {
        const result = await response.json();
        alert(`QR decodificado exitosamente:\nProducto encontrado: ${result.found}\nTracking: ${result.decoded_data.tracking_number}`);
      } else {
        setError('Error al probar decodificación del QR');
      }
    } catch (error) {
      console.error('Error testing QR decode:', error);
      setError('Error al probar decodificación');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <span className="ml-3">Cargando información del QR...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold flex items-center">
            <QrCode className="w-5 h-5 mr-2 text-purple-600" />
            Generador de Códigos QR
          </h3>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded">
          <p><strong>Producto:</strong> {trackingNumber} - {productName}</p>
          {qrInfo?.internal_id && (
            <p><strong>ID Interno:</strong> {qrInfo.internal_id}</p>
          )}
        </div>

        {!qrInfo?.has_qr ? (
          <div className="space-y-4">
            <h4 className="font-medium">Generar Nuevo Código QR</h4>
            
            <div>
              <label className="block text-sm font-medium mb-2">Estilo del QR</label>
              <select
                value={qrStyle}
                onChange={(e) => setQrStyle(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="standard">Estándar (blanco y negro)</option>
                <option value="styled">Estilizado (redondeado con efectos)</option>
              </select>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded p-4">
              <h5 className="font-medium text-blue-800 mb-2">¿Qué incluye el QR?</h5>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• ID interno único para tracking</li>
                <li>• Número de tracking original</li>
                <li>• URL directa al producto</li>
                <li>• Información de verificación</li>
              </ul>
            </div>

            <button
              onClick={generateQR}
              disabled={generating}
              className="w-full px-6 py-3 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
            >
              <QrCode className="w-4 h-4 mr-2" />
              {generating ? 'Generando QR...' : 'Generar Código QR'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="font-medium">Código QR Existente</h4>
              <span className="text-sm text-green-600 bg-green-100 px-2 py-1 rounded flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Generado
              </span>
            </div>

            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600 mb-2">
                <strong>Generado:</strong> {qrInfo.generation_date ? new Date(qrInfo.generation_date).toLocaleString() : 'Fecha no disponible'}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Archivo:</strong> {qrInfo.qr_filename || 'Nombre no disponible'}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => downloadQR(qrInfo.qr_filename!, 'qr')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                Descargar QR
              </button>
              
              <button
                onClick={() => {
                  const labelFilename = qrInfo.qr_filename!.replace('qr_', 'label_');
                  downloadQR(labelFilename, 'label');
                }}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center justify-center transition-colors"
              >
                <Printer className="w-4 h-4 mr-2" />
                Descargar Etiqueta
              </button>
            </div>

            <div className="border-t pt-4">
              <h5 className="font-medium mb-3">Regenerar QR</h5>
              <div className="flex space-x-3">
                <select
                  value={qrStyle}
                  onChange={(e) => setQrStyle(e.target.value)}
                  className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="standard">Estándar</option>
                  <option value="styled">Estilizado</option>
                </select>
                <button
                  onClick={regenerateQR}
                  disabled={generating}
                  className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Regenerar
                </button>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={testQRDecoding}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 flex items-center justify-center transition-colors"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Probar Decodificación
                </button>
                
                <button
                  onClick={() => setShowScanner(!showScanner)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center justify-center transition-colors"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  {showScanner ? 'Cerrar Escáner' : 'Escáner QR'}
                </button>
              </div>
              
              {showScanner && (
                <div className="mt-4 p-4 border border-gray-300 rounded bg-gray-50">
                  <p className="text-sm text-gray-600 text-center">
                    📱 Funcionalidad de escáner disponible en producción
                  </p>
                  <p className="text-xs text-gray-500 text-center mt-2">
                    En ambiente de desarrollo, use "Probar Decodificación" para simular
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="mt-6 pt-4 border-t">
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
            >
              Cerrar
            </button>
            {qrInfo?.has_qr && (
              <button
                onClick={() => onQRGenerated({ success: true, message: 'QR ya generado' })}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
              >
                Continuar con QR Existente
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};