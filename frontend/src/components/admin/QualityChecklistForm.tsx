import * as React from 'react';
import { useState } from 'react';
import { X, Camera, Ruler, CheckCircle, AlertTriangle, Package, FileText } from 'lucide-react';

// Modo producción: fotos requeridas normalmente
const DEVELOPMENT_MODE = false;

interface QualityChecklistFormProps {
  queueId: string;
  onComplete: (checklist: any) => void;
  onCancel: () => void;
}

interface DimensionCheck {
  length_cm: number;
  width_cm: number;
  height_cm: number;
  weight_kg: number;
  matches_declared: boolean;
  variance_percentage?: number;
  measurement_notes?: string;
}

interface QualityPhoto {
  photo_type: string;
  filename: string;
  url: string;
  description?: string;
  is_required: boolean;
  uploaded_at?: string;
}

interface QualityChecklist {
  overall_condition: string;
  has_original_packaging: boolean;
  packaging_condition?: string;
  photos: QualityPhoto[];
  dimensions: DimensionCheck;
  has_damage: boolean;
  damage_description?: string;
  has_missing_parts: boolean;
  missing_parts_description?: string;
  has_defects: boolean;
  defects_description?: string;
  is_functional: boolean;
  functionality_notes?: string;
  has_required_labels: boolean;
  labels_condition?: string;
  has_documentation: boolean;
  documentation_condition?: string;
  quality_score: number;
  inspector_notes: string;
  approved: boolean;
  requires_additional_review: boolean;
  inspector_id?: string;
  inspection_duration_minutes?: number;
}

export const QualityChecklistForm: React.FC<QualityChecklistFormProps> = ({
  queueId,
  onComplete,
  onCancel
}) => {
  const [checklist, setChecklist] = useState<QualityChecklist>({
    overall_condition: '',
    has_original_packaging: false,
    packaging_condition: '',
    photos: [],
    dimensions: {
      length_cm: 0,
      width_cm: 0,
      height_cm: 0,
      weight_kg: 0,
      matches_declared: false,
      variance_percentage: 0,
      measurement_notes: ''
    },
    has_damage: false,
    damage_description: '',
    has_missing_parts: false,
    missing_parts_description: '',
    has_defects: false,
    defects_description: '',
    is_functional: true,
    functionality_notes: '',
    has_required_labels: true,
    labels_condition: 'good',
    has_documentation: true,
    documentation_condition: 'good',
    quality_score: 8,
    inspector_notes: '',
    approved: false,
    requires_additional_review: false,
    inspector_id: '',
    inspection_duration_minutes: 0
  });

  const [uploadedFiles, setUploadedFiles] = useState<QualityPhoto[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');

  const conditionOptions = [
    { value: 'new', label: 'Nuevo' },
    { value: 'like_new', label: 'Como Nuevo' },
    { value: 'good', label: 'Bueno' },
    { value: 'fair', label: 'Regular' },
    { value: 'poor', label: 'Malo' },
    { value: 'damaged', label: 'Dañado' }
  ];

  const requiredPhotoTypes = [
    { type: 'general', label: 'Vista General', required: true },
    { type: 'damage', label: 'Daños (si aplica)', required: false },
    { type: 'label', label: 'Etiquetas/Códigos', required: true },
    { type: 'packaging', label: 'Empaque', required: false },
    { type: 'documentation', label: 'Documentación', required: false }
  ];

  const handleFileUpload = async (files: FileList, photoType: string) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadProgress(`Subiendo fotos de ${photoType}...`);

    const formData = new FormData();
    
    // Añadir archivos
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    // Añadir tipos de foto (uno por cada archivo)
    Array.from(files).forEach(() => {
      formData.append('photo_types', photoType);
    });

    // Añadir descripciones vacías por defecto
    Array.from(files).forEach(() => {
      formData.append('descriptions', `Foto ${photoType}`);
    });

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `/api/v1/admin/incoming-products/${queueId}/verification/upload-photos`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (response.ok) {
        const result = await response.json();
        const newPhotos = result.uploaded_photos;
        
        setUploadedFiles(prev => [...prev, ...newPhotos]);
        setChecklist(prev => ({
          ...prev,
          photos: [...prev.photos, ...newPhotos]
        }));

        setUploadProgress(`✅ ${newPhotos.length} fotos subidas exitosamente`);
        
        if (result.failed_uploads && result.failed_uploads.length > 0) {
          console.warn('Algunos archivos fallaron:', result.failed_uploads);
        }
      } else {
        const error = await response.json();
        setUploadProgress(`❌ Error: ${error.detail || 'Error subiendo fotos'}`);
      }
    } catch (error) {
      console.error('Error uploading photos:', error);
      setUploadProgress('❌ Error subiendo fotos');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(''), 3000);
    }
  };

  const removePhoto = async (photo: QualityPhoto) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `/api/v1/admin/verification-photos/${photo.filename}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        setUploadedFiles(prev => prev.filter(p => p.filename !== photo.filename));
        setChecklist(prev => ({
          ...prev,
          photos: prev.photos.filter(p => p.filename !== photo.filename)
        }));
      }
    } catch (error) {
      console.error('Error removing photo:', error);
    }
  };

  const updateDimensions = (field: keyof DimensionCheck, value: number | boolean | string) => {
    setChecklist(prev => ({
      ...prev,
      dimensions: {
        ...prev.dimensions,
        [field]: value
      }
    }));
  };

  const calculateQualityScore = () => {
    let score = 10;
    
    // Reducir por daños
    if (checklist.has_damage) score -= 2;
    if (checklist.has_missing_parts) score -= 2;
    if (checklist.has_defects) score -= 3;
    if (!checklist.is_functional) score -= 4;
    
    // Reducir por condición
    switch (checklist.overall_condition) {
      case 'damaged': score -= 4; break;
      case 'poor': score -= 3; break;
      case 'fair': score -= 2; break;
      case 'good': score -= 1; break;
      case 'like_new': score -= 0.5; break;
      case 'new': break;
    }

    // Reducir por falta de documentación
    if (!checklist.has_required_labels) score -= 1;
    if (!checklist.has_documentation) score -= 1;
    
    return Math.max(1, Math.min(10, Math.round(score * 10) / 10));
  };

  const validateChecklist = (): string[] => {
    const errors: string[] = [];
    
    if (!checklist.overall_condition) {
      errors.push('Debe seleccionar la condición general del producto');
    }
    
    // Solo validar fotos en modo producción
    if (!DEVELOPMENT_MODE) {
      if (checklist.photos.length === 0) {
        errors.push('Debe subir al menos una foto');
      }
      
      // Verificar fotos requeridas
      const requiredTypes = requiredPhotoTypes.filter(pt => pt.required).map(pt => pt.type);
      const uploadedTypes = checklist.photos.map(p => p.photo_type);
      const missingTypes = requiredTypes.filter(type => !uploadedTypes.includes(type));
      
      if (missingTypes.length > 0) {
        errors.push(`Faltan fotos requeridas: ${missingTypes.join(', ')}`);
      }
    }
    
    if (checklist.dimensions.length_cm <= 0 || 
        checklist.dimensions.width_cm <= 0 || 
        checklist.dimensions.height_cm <= 0 || 
        checklist.dimensions.weight_kg <= 0) {
      errors.push('Todas las dimensiones deben ser mayores a 0');
    }
    
    if (!checklist.inspector_notes.trim()) {
      errors.push('Debe incluir notas del inspector');
    }
    
    if (checklist.has_damage && !checklist.damage_description?.trim()) {
      errors.push('Debe describir los daños encontrados');
    }
    
    if (checklist.has_missing_parts && !checklist.missing_parts_description?.trim()) {
      errors.push('Debe describir las partes faltantes');
    }

    return errors;
  };

  const handleSubmit = () => {
    const errors = validateChecklist();
    
    if (errors.length > 0) {
      alert('Errores en el checklist:\n' + errors.join('\n'));
      return;
    }

    // Calcular score automáticamente
    const calculatedScore = calculateQualityScore();
    
    const finalChecklist = {
      ...checklist,
      quality_score: calculatedScore,
      approved: calculatedScore >= 6 && !checklist.requires_additional_review,
      inspector_id: localStorage.getItem('user_id') || '',
      inspection_duration_minutes: Math.round((Date.now() - startTime) / 60000)
    };

    onComplete(finalChecklist);
  };

  // Tiempo de inicio para calcular duración
  const [startTime] = useState(Date.now());

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6 bg-white rounded-lg shadow-lg">
      <div className="border-b pb-4">
        <h3 className="text-xl font-bold text-gray-900">Checklist de Calidad</h3>
        <p className="text-sm text-gray-600 mt-1">
          Verificación detallada del producto #{queueId}
        </p>
      </div>
      
      {uploadProgress && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800">{uploadProgress}</p>
        </div>
      )}

      {/* Sección de Fotos */}
      <div className="border rounded-lg p-4 bg-gray-50">
        <h4 className="font-semibold flex items-center mb-4 text-gray-900">
          <Camera className="w-5 h-5 mr-2 text-blue-600" />
          Evidencia Fotográfica
          {DEVELOPMENT_MODE && (
            <span className="ml-3 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
              MODO DESARROLLO - OPCIONAL
            </span>
          )}
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {requiredPhotoTypes.map(photoType => (
            <div key={photoType.type} 
                 className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors
                           ${(photoType.required && !DEVELOPMENT_MODE) ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'}`}>
              <label className="block text-sm font-medium mb-2">
                {photoType.label}
                {(photoType.required && !DEVELOPMENT_MODE) && <span className="text-red-500 ml-1">*</span>}
                {DEVELOPMENT_MODE && <span className="text-gray-500 ml-1">(opcional)</span>}
              </label>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files, photoType.type)}
                className="w-full text-sm"
                disabled={uploading}
              />
              <p className="text-xs text-gray-500 mt-1">JPG, PNG, WebP (max 10MB)</p>
            </div>
          ))}
        </div>

        {/* Preview de fotos subidas */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6">
            <h5 className="font-medium mb-3 text-gray-900">Fotos Subidas ({uploadedFiles.length})</h5>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {uploadedFiles.map((photo, index) => (
                <div key={index} className="relative group">
                  <img 
                    src={photo.url} 
                    alt={photo.photo_type}
                    className="w-full h-20 object-cover rounded border"
                  />
                  <button
                    onClick={() => removePhoto(photo)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  <span className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs px-1 py-0.5 rounded-b">
                    {photo.photo_type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sección de Dimensiones */}
      <div className="border rounded-lg p-4 bg-gray-50">
        <h4 className="font-semibold flex items-center mb-4 text-gray-900">
          <Ruler className="w-5 h-5 mr-2 text-green-600" />
          Verificación de Dimensiones Físicas
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Largo (cm) *</label>
            <input
              type="number"
              step="0.1"
              min="0"
              value={checklist.dimensions.length_cm}
              onChange={(e) => updateDimensions('length_cm', parseFloat(e.target.value) || 0)}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Ancho (cm) *</label>
            <input
              type="number"
              step="0.1"
              min="0"
              value={checklist.dimensions.width_cm}
              onChange={(e) => updateDimensions('width_cm', parseFloat(e.target.value) || 0)}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Alto (cm) *</label>
            <input
              type="number"
              step="0.1"
              min="0"
              value={checklist.dimensions.height_cm}
              onChange={(e) => updateDimensions('height_cm', parseFloat(e.target.value) || 0)}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Peso (kg) *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={checklist.dimensions.weight_kg}
              onChange={(e) => updateDimensions('weight_kg', parseFloat(e.target.value) || 0)}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div className="mt-4 flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={checklist.dimensions.matches_declared}
              onChange={(e) => updateDimensions('matches_declared', e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Coincide con dimensiones declaradas</span>
          </label>
        </div>

        {!checklist.dimensions.matches_declared && (
          <div className="mt-3">
            <label className="block text-sm font-medium mb-1 text-gray-700">Variación (%)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="100"
              value={checklist.dimensions.variance_percentage || 0}
              onChange={(e) => updateDimensions('variance_percentage', parseFloat(e.target.value))}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}
      </div>

      {/* Sección de Estado y Condición */}
      <div className="border rounded-lg p-4 bg-gray-50">
        <h4 className="font-semibold flex items-center mb-4 text-gray-900">
          <Package className="w-5 h-5 mr-2 text-purple-600" />
          Estado del Producto
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Condición General *</label>
              <select
                value={checklist.overall_condition}
                onChange={(e) => setChecklist(prev => ({ ...prev, overall_condition: e.target.value }))}
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Seleccionar condición</option>
                {conditionOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checklist.has_original_packaging}
                  onChange={(e) => setChecklist(prev => ({ ...prev, has_original_packaging: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Empaque original</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checklist.has_damage}
                  onChange={(e) => setChecklist(prev => ({ ...prev, has_damage: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Tiene daños visibles</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checklist.has_missing_parts}
                  onChange={(e) => setChecklist(prev => ({ ...prev, has_missing_parts: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Faltan partes/accesorios</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checklist.has_defects}
                  onChange={(e) => setChecklist(prev => ({ ...prev, has_defects: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Defectos de fabricación</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checklist.is_functional}
                  onChange={(e) => setChecklist(prev => ({ ...prev, is_functional: e.target.checked }))}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Funciona correctamente</span>
              </label>
            </div>
          </div>

          <div className="space-y-4">
            {checklist.has_damage && (
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Descripción de daños *</label>
                <textarea
                  value={checklist.damage_description || ''}
                  onChange={(e) => setChecklist(prev => ({ ...prev, damage_description: e.target.value }))}
                  placeholder="Describa los daños encontrados..."
                  className="w-full border rounded px-3 py-2 h-20 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            )}

            {checklist.has_missing_parts && (
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Partes faltantes *</label>
                <textarea
                  value={checklist.missing_parts_description || ''}
                  onChange={(e) => setChecklist(prev => ({ ...prev, missing_parts_description: e.target.value }))}
                  placeholder="Describa las partes faltantes..."
                  className="w-full border rounded px-3 py-2 h-20 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            )}

            {checklist.has_defects && (
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Descripción de defectos *</label>
                <textarea
                  value={checklist.defects_description || ''}
                  onChange={(e) => setChecklist(prev => ({ ...prev, defects_description: e.target.value }))}
                  placeholder="Describa los defectos encontrados..."
                  className="w-full border rounded px-3 py-2 h-20 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Evaluación Final */}
      <div className="border rounded-lg p-4 bg-gray-50">
        <h4 className="font-semibold flex items-center mb-4 text-gray-900">
          <FileText className="w-5 h-5 mr-2 text-indigo-600" />
          Evaluación Final
        </h4>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">
              Puntuación de Calidad Calculada: {calculateQualityScore()}/10
            </label>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  calculateQualityScore() >= 8 ? 'bg-green-500' :
                  calculateQualityScore() >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${calculateQualityScore() * 10}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {calculateQualityScore() >= 8 ? 'Excelente calidad' :
               calculateQualityScore() >= 6 ? 'Calidad aceptable' : 'Requiere revisión'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Notas del Inspector *</label>
            <textarea
              value={checklist.inspector_notes}
              onChange={(e) => setChecklist(prev => ({ ...prev, inspector_notes: e.target.value }))}
              placeholder="Observaciones adicionales del proceso de verificación..."
              className="w-full border rounded px-3 py-2 h-24 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={checklist.requires_additional_review}
                onChange={(e) => setChecklist(prev => ({ ...prev, requires_additional_review: e.target.checked }))}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Requiere revisión adicional</span>
            </label>
          </div>
        </div>
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <button
          onClick={onCancel}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          disabled={uploading}
        >
          Cancelar
        </button>
        <button
          onClick={handleSubmit}
          disabled={uploading || validateChecklist().length > 0}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center transition-colors"
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          {uploading ? 'Procesando...' : 'Completar Checklist'}
        </button>
      </div>

      {/* Indicadores de validación */}
      {validateChecklist().length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" />
            <div>
              <h5 className="font-medium text-yellow-800">Completar antes de enviar:</h5>
              <ul className="text-sm text-yellow-700 mt-1 space-y-1">
                {validateChecklist().map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};