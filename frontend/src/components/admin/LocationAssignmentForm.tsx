import * as React from 'react';
import { useState, useEffect } from 'react';
import { X, MapPin, Zap, Target, BarChart, Loader, CheckCircle, AlertTriangle, Info } from 'lucide-react';

interface LocationAssignmentFormProps {
  queueId: number;
  trackingNumber: string;
  productInfo: {
    name?: string;
    category?: string;
    dimensions?: any;
    weight?: number;
  };
  onAssigned: (assignmentData: any) => void;
  onCancel: () => void;
}

interface LocationSuggestion {
  zona: string;
  estante: string;
  posicion: string;
  capacity: number;
  recommendation: string;
}

interface WarehouseData {
  availability_summary: {
    total_locations: number;
    total_capacity: number;
    total_available: number;
    utilization_rate: number;
    zones_count: number;
  };
  zones_detail: Record<string, any>;
  available_locations: any[];
  assignment_strategies: string[];
}

export const LocationAssignmentForm: React.FC<LocationAssignmentFormProps> = ({
  queueId,
  trackingNumber,
  productInfo,
  onAssigned,
  onCancel
}) => {
  const [assignmentMode, setAssignmentMode] = useState<'auto' | 'manual'>('auto');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [warehouseData, setWarehouseData] = useState<WarehouseData | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<LocationSuggestion | null>(null);
  const [manualLocation, setManualLocation] = useState({
    zona: '',
    estante: '',
    posicion: '01'
  });
  const [result, setResult] = useState<{type: 'success' | 'error', message: string, data?: any} | null>(null);

  // Cargar datos del almacén al montar el componente
  useEffect(() => {
    loadWarehouseData();
    if (assignmentMode === 'manual') {
      loadLocationSuggestions();
    }
  }, [assignmentMode]);

  const loadWarehouseData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        'http://192.168.1.137:8000/api/v1/admin/warehouse/availability',
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const result = await response.json();
        setWarehouseData(result.data);
      }
    } catch (error) {
      console.error('Error loading warehouse data:', error);
    }
  };

  const loadLocationSuggestions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/location/suggestions?limit=5`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuggestions(result.data.location_suggestions);
      }
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleAutoAssignment = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/location/auto-assign`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const resultData = await response.json();

      if (response.ok && resultData.status === 'success') {
        setResult({
          type: 'success',
          message: 'Ubicación asignada automáticamente',
          data: resultData.data
        });
        
        // Notificar al componente padre después de un pequeño delay para mostrar el resultado
        setTimeout(() => {
          onAssigned(resultData.data);
        }, 2000);
      } else {
        setResult({
          type: 'error',
          message: resultData.message || 'No se pudo asignar ubicación automáticamente',
          data: resultData.data
        });
      }
    } catch (error) {
      console.error('Error in auto assignment:', error);
      setResult({
        type: 'error',
        message: 'Error de conexión al asignar ubicación'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleManualAssignment = async () => {
    if (!selectedLocation && (!manualLocation.zona || !manualLocation.estante)) {
      alert('Debe seleccionar una ubicación o especificar zona y estante');
      return;
    }

    setLoading(true);
    setResult(null);

    const locationToAssign = selectedLocation || manualLocation;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.137:8000/api/v1/admin/incoming-products/${queueId}/location/manual-assign`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            zona: locationToAssign.zona,
            estante: locationToAssign.estante,
            posicion: locationToAssign.posicion || '01'
          })
        }
      );

      const resultData = await response.json();

      if (response.ok && resultData.status === 'success') {
        setResult({
          type: 'success',
          message: 'Ubicación asignada manualmente',
          data: resultData.data
        });
        
        // Notificar al componente padre después de un pequeño delay para mostrar el resultado
        setTimeout(() => {
          onAssigned(resultData.data);
        }, 2000);
      } else {
        setResult({
          type: 'error',
          message: resultData.detail || 'No se pudo asignar la ubicación',
        });
      }
    } catch (error) {
      console.error('Error in manual assignment:', error);
      setResult({
        type: 'error',
        message: 'Error de conexión al asignar ubicación'
      });
    } finally {
      setLoading(false);
    }
  };

  const getUtilizationColor = (rate: number): string => {
    if (rate < 50) return 'text-green-600';
    if (rate < 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getUtilizationBgColor = (rate: number): string => {
    if (rate < 50) return 'bg-green-100';
    if (rate < 80) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  // Si hay un resultado exitoso, mostrar pantalla de confirmación
  if (result?.type === 'success') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-green-600 mb-2">
              ¡Ubicación Asignada!
            </h3>
            <p className="text-gray-700 mb-4">{result.message}</p>
            
            {result.data && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div className="text-sm space-y-2">
                  <p><strong>Producto:</strong> {trackingNumber}</p>
                  <p><strong>Ubicación:</strong> {result.data.assigned_location?.full_location || `${result.data.assigned_location?.zona}-${result.data.assigned_location?.estante}-${result.data.assigned_location?.posicion}`}</p>
                  <p><strong>Estrategia:</strong> {result.data.assignment_strategy === 'automatic' ? 'Automática' : 'Manual'}</p>
                  <p><strong>Estado:</strong> <span className="text-green-600 font-medium">{result.data.new_status || 'APROBADO'}</span></p>
                </div>
              </div>
            )}
            
            <div className="text-xs text-gray-500">
              Cerrando automáticamente...
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-blue-600 flex items-center">
            <MapPin className="w-5 h-5 mr-2" />
            Asignar Ubicación de Almacén
          </h3>
          <button 
            onClick={onCancel} 
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Información del producto */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-blue-700 font-medium">
                <strong>Tracking:</strong> {trackingNumber}
              </p>
              <p className="text-sm text-blue-700">
                <strong>Producto:</strong> {productInfo.name || 'N/A'}
              </p>
              <p className="text-sm text-blue-700">
                <strong>Categoría:</strong> {productInfo.category || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700">
                <strong>Peso:</strong> {productInfo.weight ? `${productInfo.weight} kg` : 'N/A'}
              </p>
              <p className="text-sm text-blue-700">
                <strong>Dimensiones:</strong> {
                  productInfo.dimensions ? 
                    JSON.stringify(productInfo.dimensions) : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Estado del almacén */}
        {warehouseData && (
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3 flex items-center">
              <BarChart className="w-4 h-4 mr-2" />
              Estado del Almacén
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800">
                  {warehouseData.availability_summary.total_locations}
                </div>
                <div className="text-xs text-gray-600">Total Ubicaciones</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800">
                  {warehouseData.availability_summary.total_available}
                </div>
                <div className="text-xs text-gray-600">Disponibles</div>
              </div>
              <div className="text-center">
                <div className={`text-lg font-bold ${getUtilizationColor(warehouseData.availability_summary.utilization_rate)}`}>
                  {warehouseData.availability_summary.utilization_rate}%
                </div>
                <div className="text-xs text-gray-600">Utilización</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800">
                  {warehouseData.availability_summary.zones_count}
                </div>
                <div className="text-xs text-gray-600">Zonas</div>
              </div>
            </div>
          </div>
        )}

        {/* Selector de modo */}
        <div className="mb-6">
          <div className="flex space-x-1 p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setAssignmentMode('auto')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors flex items-center justify-center ${
                assignmentMode === 'auto'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Zap className="w-4 h-4 mr-2" />
              Asignación Automática
            </button>
            <button
              onClick={() => setAssignmentMode('manual')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors flex items-center justify-center ${
                assignmentMode === 'manual'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Target className="w-4 h-4 mr-2" />
              Asignación Manual
            </button>
          </div>
        </div>

        {/* Contenido según el modo */}
        {assignmentMode === 'auto' ? (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-800 mb-2 flex items-center">
                <Info className="w-4 h-4 mr-2" />
                Asignación Inteligente
              </h4>
              <p className="text-sm text-green-700 mb-4">
                El sistema analizará automáticamente múltiples factores como tamaño del producto, 
                categoría, proximidad a la entrada, distribución de peso y rotación FIFO para 
                encontrar la ubicación óptima.
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Optimización</div>
                  <div className="text-gray-600">Tamaño y espacio</div>
                </div>
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Accesibilidad</div>
                  <div className="text-gray-600">Proximidad entrada</div>
                </div>
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Categorización</div>
                  <div className="text-gray-600">Agrupación similar</div>
                </div>
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Distribución</div>
                  <div className="text-gray-600">Balance de peso</div>
                </div>
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Rotación</div>
                  <div className="text-gray-600">FIFO automático</div>
                </div>
                <div className="bg-white p-2 rounded border">
                  <div className="font-medium text-gray-700">Eficiencia</div>
                  <div className="text-gray-600">Uso óptimo</div>
                </div>
              </div>
            </div>

            {/* Mostrar error si la asignación automática falló */}
            {result?.type === 'error' && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertTriangle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-red-800 mb-1">Error en Asignación Automática</h4>
                    <p className="text-sm text-red-700 mb-3">{result.message}</p>
                    {result.data?.suggestion && (
                      <p className="text-sm text-red-600">
                        <strong>Sugerencia:</strong> {result.data.suggestion}
                      </p>
                    )}
                    {result.data?.manual_assignment_required && (
                      <button
                        onClick={() => setAssignmentMode('manual')}
                        className="mt-2 text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                      >
                        Cambiar a Asignación Manual
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-2 flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Selección Manual de Ubicación
              </h4>
              <p className="text-sm text-blue-700 mb-4">
                Seleccione una ubicación sugerida o especifique manualmente la zona y estante.
              </p>
            </div>

            {/* Sugerencias de ubicación */}
            {suggestions.length > 0 && (
              <div>
                <h5 className="font-medium text-gray-800 mb-3">Ubicaciones Sugeridas</h5>
                <div className="grid gap-3">
                  {suggestions.map((suggestion, index) => (
                    <label
                      key={index}
                      className={`flex items-center p-3 border rounded-lg cursor-pointer transition-all ${
                        selectedLocation === suggestion
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-300 hover:border-blue-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="locationSuggestion"
                        checked={selectedLocation === suggestion}
                        onChange={() => setSelectedLocation(suggestion)}
                        className="sr-only"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-800">
                            {suggestion.zona}-{suggestion.estante}-{suggestion.posicion}
                          </span>
                          <span className="text-sm text-gray-600">
                            Capacidad: {suggestion.capacity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {suggestion.recommendation}
                        </p>
                      </div>
                      {selectedLocation === suggestion && (
                        <div className="ml-3 w-2 h-2 bg-blue-500 rounded-full"></div>
                      )}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Asignación manual personalizada */}
            <div>
              <h5 className="font-medium text-gray-800 mb-3">O Especificar Ubicación Manualmente</h5>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Zona
                  </label>
                  <input
                    type="text"
                    value={manualLocation.zona}
                    onChange={(e) => setManualLocation(prev => ({ ...prev, zona: e.target.value.toUpperCase() }))}
                    placeholder="A, B, C..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estante
                  </label>
                  <input
                    type="text"
                    value={manualLocation.estante}
                    onChange={(e) => setManualLocation(prev => ({ ...prev, estante: e.target.value }))}
                    placeholder="1, 2, 3..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Posición
                  </label>
                  <input
                    type="text"
                    value={manualLocation.posicion}
                    onChange={(e) => setManualLocation(prev => ({ ...prev, posicion: e.target.value }))}
                    placeholder="01, 02..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              {manualLocation.zona && manualLocation.estante && (
                <div className="mt-2 p-2 bg-gray-100 rounded text-sm text-gray-700">
                  <strong>Ubicación:</strong> {manualLocation.zona}-{manualLocation.estante}-{manualLocation.posicion}
                </div>
              )}
            </div>

            {/* Mostrar error si la asignación manual falló */}
            {result?.type === 'error' && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertTriangle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-red-800 mb-1">Error en Asignación Manual</h4>
                    <p className="text-sm text-red-700">{result.message}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Botones de acción */}
        <div className="flex justify-end space-x-3 mt-8 pt-4 border-t">
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            Cancelar
          </button>
          
          {assignmentMode === 'auto' ? (
            <button
              onClick={handleAutoAssignment}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Asignando...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Asignar Automáticamente
                </>
              )}
            </button>
          ) : (
            <button
              onClick={handleManualAssignment}
              disabled={loading || (!selectedLocation && (!manualLocation.zona || !manualLocation.estante))}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Asignando...
                </>
              ) : (
                <>
                  <Target className="w-4 h-4 mr-2" />
                  Asignar Manualmente
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};