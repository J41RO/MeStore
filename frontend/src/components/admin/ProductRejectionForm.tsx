import * as React from 'react';
import { ENV } from "../../utils/env";
import { useState } from 'react';
import { X, AlertTriangle, Send, FileText, Clock, Shield } from 'lucide-react';

interface ProductRejectionFormProps {
  queueId: number;
  trackingNumber: string;
  onReject: (rejectionData: any) => void;
  onCancel: () => void;
}

const rejectionReasons = [
  { value: 'quality_issues', label: 'Problemas de calidad detectados', icon: '🔍' },
  { value: 'missing_documentation', label: 'Documentación faltante o incompleta', icon: '📋' },
  { value: 'damaged_product', label: 'Producto dañado durante envío', icon: '📦' },
  { value: 'incorrect_dimensions', label: 'Dimensiones no coinciden con lo declarado', icon: '📏' },
  { value: 'counterfeit_suspected', label: 'Sospecha de producto falsificado', icon: '⚠️' },
  { value: 'safety_concerns', label: 'Preocupaciones de seguridad', icon: '🛡️' },
  { value: 'other', label: 'Otras razones', icon: '❓' }
];

export const ProductRejectionForm: React.FC<ProductRejectionFormProps> = ({
  queueId,
  trackingNumber,
  onReject,
  onCancel
}) => {
  const [rejectionData, setRejectionData] = useState({
    reason: '',
    description: '',
    quality_score: 1,
    evidence_photos: [],
    inspector_notes: '',
    can_appeal: true
  });

  const [submitting, setSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const validateForm = (): boolean => {
    const errors: string[] = [];
    
    if (!rejectionData.reason) {
      errors.push('Debe seleccionar una razón de rechazo');
    }
    
    if (!rejectionData.description.trim()) {
      errors.push('Debe proporcionar una descripción detallada');
    }
    
    if (rejectionData.description.trim().length < 10) {
      errors.push('La descripción debe tener al menos 10 caracteres');
    }
    
    if (rejectionData.quality_score < 1 || rejectionData.quality_score > 10) {
      errors.push('La puntuación de calidad debe estar entre 1 y 10');
    }
    
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${ENV.API_BASE_URL}/api/v1/admin/incoming-products/${queueId}/verification/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            ...rejectionData,
            appeal_deadline: rejectionData.can_appeal ? 
              new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString() : null
          })
        }
      );

      if (response.ok) {
        const result = await response.json();
        onReject(result);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'No se pudo rechazar el producto'}`);
      }
    } catch (error) {
      console.error('Error rejecting product:', error);
      alert('Error de conexión al rechazar producto');
    } finally {
      setSubmitting(false);
    }
  };

  const getQualityScoreColor = (score: number): string => {
    if (score <= 3) return 'text-red-600';
    if (score <= 6) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getQualityScoreLabel = (score: number): string => {
    if (score <= 3) return 'Muy Bajo';
    if (score <= 5) return 'Bajo';
    if (score <= 7) return 'Regular';
    if (score <= 8) return 'Bueno';
    return 'Excelente';
  };

  const selectedReason = rejectionReasons.find(r => r.value === rejectionData.reason);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-red-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Rechazar Producto
          </h3>
          <button 
            onClick={onCancel} 
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Información del producto */}
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-700 font-medium">
                <strong>Tracking:</strong> {trackingNumber}
              </p>
              <p className="text-sm text-red-700 mt-1 flex items-center">
                <Shield className="w-4 h-4 mr-1" />
                El vendedor será notificado automáticamente por email y SMS
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-red-600">Queue ID: {queueId}</p>
              <p className="text-xs text-red-600 flex items-center mt-1">
                <Clock className="w-3 h-3 mr-1" />
                Acción irreversible
              </p>
            </div>
          </div>
        </div>

        {/* Errores de validación */}
        {validationErrors.length > 0 && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg">
            <h4 className="text-sm font-medium text-red-800 mb-2">
              Por favor corrija los siguientes errores:
            </h4>
            <ul className="text-sm text-red-700 space-y-1">
              {validationErrors.map((error, index) => (
                <li key={index} className="flex items-center">
                  <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="space-y-6">
          {/* Razón principal */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Razón del Rechazo <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 gap-2">
              {rejectionReasons.map(reason => (
                <label
                  key={reason.value}
                  className={`flex items-center p-3 border rounded-lg cursor-pointer transition-all ${
                    rejectionData.reason === reason.value
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-300 hover:border-red-300 hover:bg-red-25'
                  }`}
                >
                  <input
                    type="radio"
                    name="reason"
                    value={reason.value}
                    checked={rejectionData.reason === reason.value}
                    onChange={(e) => setRejectionData(prev => ({ ...prev, reason: e.target.value }))}
                    className="sr-only"
                  />
                  <span className="text-lg mr-3">{reason.icon}</span>
                  <span className={`text-sm ${
                    rejectionData.reason === reason.value ? 'font-medium text-red-700' : 'text-gray-700'
                  }`}>
                    {reason.label}
                  </span>
                  {rejectionData.reason === reason.value && (
                    <div className="ml-auto w-2 h-2 bg-red-500 rounded-full"></div>
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Descripción detallada */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción Detallada <span className="text-red-500">*</span>
            </label>
            <textarea
              value={rejectionData.description}
              onChange={(e) => setRejectionData(prev => ({ ...prev, description: e.target.value }))}
              placeholder={selectedReason ? 
                `Explique específicamente los problemas relacionados con: ${selectedReason.label.toLowerCase()}...` :
                "Explique específicamente por qué se rechaza el producto..."
              }
              className="w-full border border-gray-300 rounded-lg px-3 py-2 h-28 focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
              maxLength={500}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Mínimo 10 caracteres</span>
              <span>{rejectionData.description.length}/500</span>
            </div>
          </div>

          {/* Puntuación de calidad */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Puntuación de Calidad (1-10)
            </label>
            <div className="space-y-3">
              <input
                type="range"
                min="1"
                max="10"
                value={rejectionData.quality_score}
                onChange={(e) => setRejectionData(prev => ({ 
                  ...prev, 
                  quality_score: parseInt(e.target.value) 
                }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between items-center">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${getQualityScoreColor(rejectionData.quality_score)}`}>
                    {rejectionData.quality_score}/10
                  </div>
                  <div className={`text-sm ${getQualityScoreColor(rejectionData.quality_score)}`}>
                    {getQualityScoreLabel(rejectionData.quality_score)}
                  </div>
                </div>
                <div className="text-xs text-gray-500 max-w-xs">
                  <span className="font-medium">Criterio:</span> Puntuaciones bajas (1-5) indican problemas graves, 
                  mientras que puntuaciones altas (6-10) sugieren problemas menores o mejorables.
                </div>
              </div>
            </div>
          </div>

          {/* Notas del inspector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notas del Inspector (Internas)
            </label>
            <textarea
              value={rejectionData.inspector_notes}
              onChange={(e) => setRejectionData(prev => ({ ...prev, inspector_notes: e.target.value }))}
              placeholder="Observaciones adicionales para el equipo interno (no visibles para el vendedor)..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 h-20 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              maxLength={300}
            />
            <div className="text-xs text-gray-500 mt-1">
              Solo visible internamente • {rejectionData.inspector_notes.length}/300
            </div>
          </div>

          {/* Opciones de apelación */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="can_appeal"
                checked={rejectionData.can_appeal}
                onChange={(e) => setRejectionData(prev => ({ ...prev, can_appeal: e.target.checked }))}
                className="mt-1 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <div className="flex-1">
                <label htmlFor="can_appeal" className="text-sm font-medium text-gray-700 cursor-pointer">
                  Permitir apelación del vendedor
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  {rejectionData.can_appeal ? 
                    "El vendedor tendrá 48 horas para apelar esta decisión con evidencia adicional." :
                    "El rechazo será definitivo sin posibilidad de apelación."
                  }
                </p>
              </div>
            </div>
          </div>

          {/* Vista previa del mensaje */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-800 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Vista Previa del Mensaje al Vendedor
            </h4>
            <div className="text-sm text-gray-700 space-y-2 bg-white p-3 rounded border">
              <p><strong>Producto:</strong> {trackingNumber}</p>
              <p><strong>Estado:</strong> <span className="text-red-600 font-medium">Rechazado</span></p>
              <p><strong>Razón:</strong> {selectedReason?.label || 'No seleccionada'}</p>
              {rejectionData.description && (
                <p><strong>Detalles:</strong> {rejectionData.description}</p>
              )}
              <p><strong>Calificación:</strong> {rejectionData.quality_score}/10</p>
              <p><strong>Puede apelar:</strong> {rejectionData.can_appeal ? 
                <span className="text-green-600">Sí (48 horas)</span> : 
                <span className="text-red-600">No</span>
              }</p>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex justify-end space-x-3 mt-8 pt-4 border-t">
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={submitting}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || !rejectionData.reason || !rejectionData.description.trim()}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
          >
            <Send className="w-4 h-4 mr-2" />
            {submitting ? 'Rechazando...' : 'Rechazar y Notificar'}
          </button>
        </div>
      </div>
    </div>
  );
};