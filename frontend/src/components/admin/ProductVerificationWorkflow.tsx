import * as React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { CheckCircle, Clock, AlertCircle, Play, RefreshCw, FileText, Package, Star, MapPin, Award, X, QrCode } from 'lucide-react';
import { QualityChecklistForm } from './QualityChecklistForm';
import { ProductRejectionForm } from './ProductRejectionForm';
import { LocationAssignmentForm } from './LocationAssignmentForm';
import { QRGeneratorForm } from './QRGeneratorForm';

interface VerificationStep {
  step: string;
  title: string;
  description: string;
  is_current: boolean;
  is_completed: boolean;
  order: number;
  result?: {
    passed: boolean;
    notes: string;
    issues: string[];
  };
}

interface WorkflowStatus {
  queue_id: string;
  current_step: string;
  progress_percentage: number;
  steps: VerificationStep[];
  can_proceed: boolean;
  verification_attempts: number;
  tracking_number?: string;
}

interface ProductVerificationWorkflowProps {
  queueId: string;
  onStepComplete: (step: string, result: any) => void;
  onClose?: () => void;
}

export const ProductVerificationWorkflow: React.FC<ProductVerificationWorkflowProps> = ({
  queueId,
  onStepComplete,
  onClose
}) => {
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [executingStep, setExecutingStep] = useState<string | null>(null);
  const [showQualityChecklist, setShowQualityChecklist] = useState(false);
  const [showRejectionForm, setShowRejectionForm] = useState(false);
  const [showLocationAssignment, setShowLocationAssignment] = useState(false);
  const [showQRGenerator, setShowQRGenerator] = useState(false);
  const [productInfo, setProductInfo] = useState<any>(null);
  const [stepForm, setStepForm] = useState({
    notes: '',
    passed: true,
    issues: [] as string[],
    metadata: {}
  });

  // Cargar estado actual del workflow
  const loadWorkflowStatus = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`/api/v1/admin/incoming-products/${queueId}/verification/current-step`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setWorkflowStatus(data.data);
        
        // Cargar información del producto si no está disponible
        if (!productInfo) {
          await loadProductInfo();
        }
      } else {
        const errorText = await response.text();
        console.error('Error loading workflow status:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error loading workflow status:', error);
    } finally {
      setLoading(false);
    }
  }, [queueId]);

  // Cargar información del producto
  const loadProductInfo = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/admin/incoming-products/${queueId}/location/suggestions?limit=1`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.data && data.data.product_info) {
          setProductInfo(data.data.product_info);
        }
      }
    } catch (error) {
      console.error('Error loading product info:', error);
    }
  }, [queueId]);

  useEffect(() => {
    loadWorkflowStatus();
  }, [loadWorkflowStatus]);


  // Ejecutar paso del workflow
  const executeStep = async (step: string) => {
    if (!workflowStatus) return;

    setExecutingStep(step);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/admin/incoming-products/${queueId}/verification/execute-step`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step: step,
          passed: stepForm.passed,
          notes: stepForm.notes,
          issues: stepForm.issues,
          metadata: stepForm.metadata
        })
      });

      if (response.ok) {
        const data = await response.json();
        setWorkflowStatus(data.data);
        onStepComplete(step, data.data);
        
        // Resetear formulario
        setStepForm({
          notes: '',
          passed: true,
          issues: [],
          metadata: {}
        });
      } else {
        console.error('Error executing step');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setExecutingStep(null);
    }
  };

  // Manejar completación del checklist de calidad
  const handleQualityChecklistComplete = async (checklistData: any) => {
    try {
      setExecutingStep('quality_assessment');
      
      // Enviar checklist al backend
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `/api/v1/admin/incoming-products/${queueId}/verification/quality-checklist`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            queue_id: parseInt(queueId),
            checklist: checklistData
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        setWorkflowStatus(data.data.workflow_progress);
        setShowQualityChecklist(false);
        onStepComplete('quality_assessment', data.data);
      } else {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        console.error('Error submitting checklist:', response.status, errorData);
        
        if (response.status === 401) {
          alert('Error: Token de autenticación inválido o expirado. Por favor, inicia sesión nuevamente.');
        } else {
          alert('Error enviando checklist: ' + (errorData.detail || `Error ${response.status}`));
        }
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error de conexión al enviar checklist');
    } finally {
      setExecutingStep(null);
    }
  };

  // Manejar asignación de ubicación completada
  const handleLocationAssignmentComplete = async (assignmentData: any) => {
    try {
      setExecutingStep('location_assignment');
      
      // La asignación ya se hizo en el componente LocationAssignmentForm
      // Solo necesitamos actualizar el workflow status y cerrar el modal
      
      console.log('Location assignment completed:', assignmentData);
      
      // Recargar el workflow status para reflejar los cambios
      await loadWorkflowStatus();
      
      setShowLocationAssignment(false);
      onStepComplete('location_assignment', assignmentData);
    } catch (error) {
      console.error('Error handling location assignment completion:', error);
    } finally {
      setExecutingStep(null);
    }
  };

  // Manejar rechazo del producto
  const handleProductRejection = (rejectionResult: any) => {
    setShowRejectionForm(false);
    console.log('Product rejected:', rejectionResult);
    
    // Mostrar mensaje de éxito
    alert(`Producto rechazado exitosamente. Notificación enviada al vendedor.`);
    
    // Refrescar el estado del workflow para mostrar el nuevo estado
    loadWorkflowStatus();
    
    // Cerrar el workflow completo después de un rechazo
    if (onClose) {
      setTimeout(() => {
        onClose();
      }, 2000);
    }
  };

  // Obtener icono para cada paso
  const getStepIcon = (stepName: string, isCompleted: boolean, isCurrent: boolean) => {
    const iconProps = { 
      size: 20, 
      className: isCompleted ? 'text-green-600' : isCurrent ? 'text-blue-600' : 'text-gray-400' 
    };

    switch (stepName) {
      case 'initial_inspection':
        return <Package {...iconProps} />;
      case 'documentation_check':
        return <FileText {...iconProps} />;
      case 'quality_assessment':
        return <Star {...iconProps} />;
      case 'location_assignment':
        return <MapPin {...iconProps} />;
      case 'final_approval':
        return <Award {...iconProps} />;
      case 'completed':
        return <CheckCircle {...iconProps} />;
      default:
        return <Clock {...iconProps} />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Cargando workflow...</span>
      </div>
    );
  }

  if (!workflowStatus) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <span className="text-red-700">Error al cargar el estado del workflow</span>
        </div>
      </div>
    );
  }

  const currentStep = workflowStatus.steps.find(s => s.is_current);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Verificación de Producto</h3>
          <p className="text-sm text-gray-600">ID: {workflowStatus.queue_id}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-gray-600">Progreso</p>
            <p className="text-lg font-bold text-blue-600">
              {Math.round(workflowStatus.progress_percentage)}%
            </p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-1"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="mb-8">
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${workflowStatus.progress_percentage}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>Inicio</span>
          <span>Completado</span>
        </div>
      </div>

      {/* Stepper */}
      <div className="space-y-4 mb-8">
        {workflowStatus.steps.map((step, index) => (
          <div key={step.step} className="flex items-start gap-4">
            {/* Icono y conector */}
            <div className="flex flex-col items-center">
              <div className={`
                flex items-center justify-center w-10 h-10 rounded-full border-2
                ${step.is_completed 
                  ? 'bg-green-100 border-green-500' 
                  : step.is_current 
                    ? 'bg-blue-100 border-blue-500' 
                    : 'bg-gray-100 border-gray-300'
                }
              `}>
                {step.is_completed ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  getStepIcon(step.step, step.is_completed, step.is_current)
                )}
              </div>
              {index < workflowStatus.steps.length - 1 && (
                <div className={`w-0.5 h-8 mt-2 ${
                  step.is_completed ? 'bg-green-300' : 'bg-gray-300'
                }`}></div>
              )}
            </div>

            {/* Contenido del paso */}
            <div className="flex-1 pb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className={`font-semibold ${
                    step.is_current ? 'text-blue-900' : 'text-gray-700'
                  }`}>
                    {step.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {step.description}
                  </p>
                </div>
                
                {/* Estado del paso */}
                <div className="text-right">
                  {step.is_completed && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Completado
                    </span>
                  )}
                  {step.is_current && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Actual
                    </span>
                  )}
                </div>
              </div>

              {/* Resultado del paso si está completado */}
              {step.result && (
                <div className={`mt-3 p-3 rounded-lg border ${
                  step.result.passed 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-red-50 border-red-200'
                }`}>
                  <p className="text-sm font-medium mb-1">
                    {step.result.passed ? '✅ Aprobado' : '❌ Rechazado'}
                  </p>
                  <p className="text-sm text-gray-600">{step.result.notes}</p>
                  {step.result.issues && step.result.issues.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-red-600">Problemas:</p>
                      <ul className="text-sm text-red-600 list-disc list-inside">
                        {step.result.issues.map((issue, i) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>


      {/* Formulario para paso actual */}
      {currentStep && !currentStep.is_completed && (
        <div className="bg-gray-50 rounded-lg p-6">
          {/* Mostrar QualityChecklistForm para quality_assessment */}
          {currentStep.step === 'quality_assessment' && showQualityChecklist ? (
            <QualityChecklistForm
              queueId={queueId}
              onComplete={handleQualityChecklistComplete}
              onCancel={() => setShowQualityChecklist(false)}
            />
          ) : currentStep.step === 'quality_assessment' ? (
            /* Botón para abrir Quality Checklist */
            <div className="text-center py-8">
              <h4 className="text-lg font-semibold mb-4 flex items-center justify-center">
                Evaluación de Calidad
              </h4>
              <p className="text-gray-600 mb-6">
                Este paso requiere un checklist detallado de calidad con evidencia fotográfica y verificación de dimensiones.
              </p>
              <button
                onClick={() => setShowQualityChecklist(true)}
                disabled={executingStep === currentStep.step}
                className="flex items-center justify-center mx-auto px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {executingStep === currentStep.step ? (
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                ) : (
                  <Star className="w-5 h-5 mr-2" />
                )}
                Iniciar Checklist de Calidad
              </button>
            </div>
          ) : currentStep.step === 'location_assignment' && showLocationAssignment ? (
            <LocationAssignmentForm
              queueId={parseInt(queueId)}
              trackingNumber={workflowStatus?.tracking_number || workflowStatus?.queue_id || queueId}
              productInfo={productInfo || {}}
              onAssigned={handleLocationAssignmentComplete}
              onCancel={() => setShowLocationAssignment(false)}
            />
          ) : currentStep.step === 'location_assignment' ? (
            /* Botón para abrir Location Assignment */
            <div className="text-center py-8">
              <h4 className="text-lg font-semibold mb-4 flex items-center justify-center">
                Asignación de Ubicación
                <span className="ml-3 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  NUEVO SISTEMA
                </span>
              </h4>
              <p className="text-gray-600 mb-6">
                Asigne una ubicación óptima en el almacén usando algoritmos inteligentes 
                o selección manual basada en tamaño, categoría y proximidad.
              </p>
              <button
                onClick={() => setShowLocationAssignment(true)}
                disabled={executingStep === currentStep.step}
                className="flex items-center justify-center mx-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {executingStep === currentStep.step ? (
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                ) : (
                  <MapPin className="w-5 h-5 mr-2" />
                )}
                Iniciar Asignación de Ubicación
              </button>
            </div>
          ) : currentStep.step === 'final_approval' ? (
            /* Paso final con opción de generar QR */
            <div className="text-center py-8">
              <h4 className="text-lg font-semibold mb-4 flex items-center justify-center">
                Aprobación Final
                <span className="ml-3 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                  PASO FINAL
                </span>
              </h4>
              <p className="text-gray-600 mb-6">
                Producto verificado completamente. Genere código QR para tracking interno 
                o complete la verificación sin QR.
              </p>
              
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setShowQRGenerator(true)}
                  disabled={executingStep === currentStep.step}
                  className="flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {executingStep === currentStep.step ? (
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <QrCode className="w-5 h-5 mr-2" />
                  )}
                  Generar QR y Finalizar
                </button>
                
                <button
                  onClick={() => onStepComplete(currentStep.step, {
                    passed: true,
                    notes: 'Aprobación final sin QR',
                    metadata: { completed_without_qr: true }
                  })}
                  disabled={executingStep === currentStep.step}
                  className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  <Award className="w-5 h-5 mr-2" />
                  Finalizar sin QR
                </button>
              </div>
            </div>
          ) : (
            /* Formulario estándar para otros pasos */
            <>
              <h4 className="text-lg font-semibold mb-4">Ejecutar: {currentStep.title}</h4>
              
              <div className="space-y-4">
                {/* Resultado del paso */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Resultado
                  </label>
                  <div className="flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="passed"
                        checked={stepForm.passed}
                        onChange={() => setStepForm(prev => ({ ...prev, passed: true }))}
                        className="mr-2"
                      />
                      <span className="text-green-600 font-medium">✅ Aprobado</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="passed"
                        checked={!stepForm.passed}
                        onChange={() => setStepForm(prev => ({ ...prev, passed: false }))}
                        className="mr-2"
                      />
                      <span className="text-red-600 font-medium">❌ Rechazado</span>
                    </label>
                  </div>
                </div>

                {/* Notas */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notas *
                  </label>
                  <textarea
                    value={stepForm.notes}
                    onChange={(e) => setStepForm(prev => ({ ...prev, notes: e.target.value }))}
                    placeholder="Descripción detallada de la verificación..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                {/* Problemas (si no fue aprobado) */}
                {!stepForm.passed && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Problemas encontrados
                    </label>
                    <textarea
                      placeholder="Lista los problemas encontrados, uno por línea..."
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) => {
                        const issues = e.target.value.split('\n').filter(issue => issue.trim());
                        setStepForm(prev => ({ ...prev, issues }));
                      }}
                    />
                  </div>
                )}

                {/* Botones de acción */}
                <div className="flex justify-between items-center pt-4">
                  <div className="flex gap-3">
                    <button
                      onClick={() => executeStep(currentStep.step)}
                      disabled={!stepForm.notes.trim() || executingStep === currentStep.step}
                      className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {executingStep === currentStep.step ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4 mr-2" />
                      )}
                      Ejecutar Paso
                    </button>
                    
                    <button
                      onClick={loadWorkflowStatus}
                      className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Actualizar
                    </button>
                  </div>

                  {/* Botón de rechazo - disponible en cualquier paso */}
                  <button
                    onClick={() => setShowRejectionForm(true)}
                    className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Rechazar Producto
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Información adicional */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Intentos de verificación: {workflowStatus.verification_attempts}</span>
          <span>Puede proceder: {workflowStatus.can_proceed ? 'Sí' : 'No'}</span>
        </div>
      </div>

      {/* Modal de rechazo */}
      {showRejectionForm && (
        <ProductRejectionForm
          queueId={parseInt(queueId)}
          trackingNumber={workflowStatus?.tracking_number || queueId}
          onReject={handleProductRejection}
          onCancel={() => setShowRejectionForm(false)}
        />
      )}

      {/* Modal de asignación de ubicación */}
      {showLocationAssignment && (
        <LocationAssignmentForm
          queueId={parseInt(queueId)}
          trackingNumber={workflowStatus?.tracking_number || workflowStatus?.queue_id || queueId}
          productInfo={productInfo || {}}
          onAssigned={handleLocationAssignmentComplete}
          onCancel={() => setShowLocationAssignment(false)}
        />
      )}

      {/* Modal de generador QR */}
      {showQRGenerator && (
        <QRGeneratorForm
          queueId={parseInt(queueId)}
          trackingNumber={workflowStatus?.tracking_number || workflowStatus?.queue_id || queueId}
          productName={productInfo?.name || 'Producto'}
          onQRGenerated={(result) => {
            setShowQRGenerator(false);
            // Completar workflow automáticamente después de generar QR
            onStepComplete(currentStep?.step || 'final_approval', {
              passed: true,
              notes: `QR generado: ${result.internal_id || 'ID no disponible'}`,
              metadata: {
                qr_generated: true,
                internal_id: result.internal_id,
                qr_filename: result.qr_data?.qr_filename
              }
            });
          }}
          onClose={() => setShowQRGenerator(false)}
        />
      )}
    </div>
  );
};