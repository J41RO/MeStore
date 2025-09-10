import React, { useState, useEffect } from 'react';
import MovementTracker from '../../components/admin/MovementTracker';

interface Movement {
  id: string;
  inventory_id: string;
  tipo_movimiento: string;
  cantidad_anterior: number;
  cantidad_nueva: number;
  observaciones: string;
  fecha_movimiento: string;
  referencia_externa?: string;
  lote?: string;
  ubicacion_origen?: string;
  ubicacion_destino?: string;
  user_id?: string;
}

const MovementTrackerPage: React.FC = () => {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [selectedMovementId, setSelectedMovementId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(true);

  useEffect(() => {
    fetchRecentMovements();
  }, []);

  const fetchRecentMovements = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/inventory/movements/recent?limit=20', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener movimientos recientes');
      }
      
      const data = await response.json();
      setMovements(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const formatMovementType = (type: string): string => {
    const typeMap: Record<string, string> = {
      'INGRESO': 'Ingreso',
      'SALIDA': 'Salida',
      'AJUSTE_POSITIVO': 'Ajuste Positivo',
      'AJUSTE_NEGATIVO': 'Ajuste Negativo',
      'TRANSFERENCIA': 'Transferencia',
      'DEVOLUCION': 'Devolución',
      'MERMA': 'Merma',
      'RESERVA': 'Reserva',
      'LIBERACION': 'Liberación'
    };
    return typeMap[type] || type;
  };

  const getMovementTypeColor = (type: string): string => {
    switch (type) {
      case 'INGRESO': return 'bg-green-100 text-green-800';
      case 'SALIDA': return 'bg-red-100 text-red-800';
      case 'AJUSTE_POSITIVO': return 'bg-blue-100 text-blue-800';
      case 'AJUSTE_NEGATIVO': return 'bg-orange-100 text-orange-800';
      case 'TRANSFERENCIA': return 'bg-purple-100 text-purple-800';
      case 'DEVOLUCION': return 'bg-yellow-100 text-yellow-800';
      case 'MERMA': return 'bg-gray-100 text-gray-800';
      case 'RESERVA': return 'bg-indigo-100 text-indigo-800';
      case 'LIBERACION': return 'bg-teal-100 text-teal-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Movement Tracker</h1>
            <p className="mt-1 text-sm text-gray-600">
              Sistema completo de seguimiento y auditoría de movimientos de inventario
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className={`px-4 py-2 rounded-md font-medium ${
                showAnalytics 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              Analytics {showAnalytics ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={fetchRecentMovements}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Actualizar
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Movimientos Recientes */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Movimientos Recientes</h2>
              <p className="text-sm text-gray-600">Últimos 20 movimientos de inventario</p>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {loading && (
                <div className="p-4 text-center text-gray-500">
                  Cargando movimientos...
                </div>
              )}
              
              {error && (
                <div className="p-4 text-center text-red-600">
                  {error}
                </div>
              )}
              
              {movements.length === 0 && !loading && !error && (
                <div className="p-4 text-center text-gray-500">
                  No hay movimientos disponibles
                </div>
              )}
              
              <div className="divide-y divide-gray-200">
                {movements.map((movement) => (
                  <div
                    key={movement.id}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                      selectedMovementId === movement.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                    onClick={() => setSelectedMovementId(movement.id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getMovementTypeColor(movement.tipo_movimiento)}`}>
                        {formatMovementType(movement.tipo_movimiento)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(movement.fecha_movimiento).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="text-sm">
                        <span className="font-medium">Cantidad:</span>
                        <span className="ml-1">
                          {movement.cantidad_anterior} → {movement.cantidad_nueva}
                          <span className={`ml-1 ${
                            movement.cantidad_nueva > movement.cantidad_anterior 
                              ? 'text-green-600' 
                              : 'text-red-600'
                          }`}>
                            ({movement.cantidad_nueva > movement.cantidad_anterior ? '+' : ''}{movement.cantidad_nueva - movement.cantidad_anterior})
                          </span>
                        </span>
                      </div>
                      
                      {movement.observaciones && (
                        <div className="text-xs text-gray-600 truncate">
                          <span className="font-medium">Obs:</span> {movement.observaciones}
                        </div>
                      )}
                      
                      {movement.referencia_externa && (
                        <div className="text-xs text-gray-600">
                          <span className="font-medium">Ref:</span> {movement.referencia_externa}
                        </div>
                      )}
                      
                      {(movement.ubicacion_origen || movement.ubicacion_destino) && (
                        <div className="text-xs text-blue-600">
                          {movement.ubicacion_origen} → {movement.ubicacion_destino}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Movement Tracker Component */}
        <div className="lg:col-span-2">
          <MovementTracker 
            movementId={selectedMovementId || undefined}
            showAnalytics={showAnalytics}
          />
        </div>
      </div>

      {/* Información de Ayuda */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">ℹ️ Cómo usar Movement Tracker</h3>
        <div className="text-xs text-blue-800 space-y-1">
          <p>• <strong>Seleccionar movimiento:</strong> Haz clic en cualquier movimiento de la lista para ver su historial detallado</p>
          <p>• <strong>Analytics:</strong> Activa/desactiva el modo analytics para ver estadísticas y métricas</p>
          <p>• <strong>Exportación:</strong> En la pestaña Analytics puedes exportar datos en formato CSV, Excel o JSON</p>
          <p>• <strong>Filtros:</strong> Usa los filtros de fecha y tipo para refinar los analytics</p>
          <p>• <strong>Historial:</strong> Cada movimiento muestra su tracking completo con cambios, usuarios y timestamps</p>
        </div>
      </div>
    </div>
  );
};

export default MovementTrackerPage;