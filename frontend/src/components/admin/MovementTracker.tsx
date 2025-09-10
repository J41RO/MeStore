import React, { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { es } from 'date-fns/locale';

interface MovementTracker {
  id: string;
  movement_id: string;
  user_id: string;
  user_name: string;
  action_type: string;
  previous_data: any;
  new_data: any;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  location_from?: any;
  location_to?: any;
  batch_id?: string;
  notes?: string;
  action_timestamp: string;
  is_create_action: boolean;
  is_update_action: boolean;
  is_system_action: boolean;
  has_location_change: boolean;
  changes: Record<string, any>;
}

interface MovementAnalytics {
  date_range: {
    start_date: string | null;
    end_date: string | null;
  };
  total_movements: number;
  movements_by_type: Record<string, number>;
  movements_by_user: Record<string, number>;
  movements_by_date: Record<string, number>;
  filters_applied: {
    start_date: string | null;
    end_date: string | null;
    movement_type: string | null;
    user_id: string | null;
  };
}

interface MovementTrackerProps {
  movementId?: string;
  showAnalytics?: boolean;
}

const MovementTracker: React.FC<MovementTrackerProps> = ({ 
  movementId, 
  showAnalytics = true 
}) => {
  const [trackingHistory, setTrackingHistory] = useState<MovementTracker[]>([]);
  const [analytics, setAnalytics] = useState<MovementAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'history' | 'analytics'>('history');
  
  // Filtros para analytics
  const [dateFilter, setDateFilter] = useState({
    start_date: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end_date: format(new Date(), 'yyyy-MM-dd')
  });
  const [movementTypeFilter, setMovementTypeFilter] = useState('');
  const [userFilter] = useState('');

  useEffect(() => {
    if (movementId) {
      fetchMovementHistory();
    }
    if (showAnalytics) {
      fetchAnalytics();
    }
  }, [movementId]);

  const fetchMovementHistory = async () => {
    if (!movementId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/inventory/movements/tracker/${movementId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener historial de movimiento');
      }
      
      const data = await response.json();
      setTrackingHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      if (dateFilter.start_date) params.append('start_date', dateFilter.start_date);
      if (dateFilter.end_date) params.append('end_date', dateFilter.end_date);
      if (movementTypeFilter) params.append('movement_type', movementTypeFilter);
      if (userFilter) params.append('user_id', userFilter);
      
      const response = await fetch(`/api/v1/inventory/movements/analytics?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener analytics de movimientos');
      }
      
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'excel' | 'json') => {
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      params.append('format', format);
      if (dateFilter.start_date) params.append('start_date', dateFilter.start_date);
      if (dateFilter.end_date) params.append('end_date', dateFilter.end_date);
      if (movementTypeFilter) params.append('movement_type', movementTypeFilter);
      if (userFilter) params.append('user_id', userFilter);
      params.append('include_tracker', 'true');
      
      const response = await fetch(`/api/v1/inventory/movements/export?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al exportar datos');
      }
      
      // Obtener el nombre del archivo del header
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `movimientos_export_${Date.now()}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }
      
      // Crear blob y descargar
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al exportar datos');
    }
  };

  const getActionTypeColor = (actionType: string): string => {
    switch (actionType) {
      case 'CREATE': return 'bg-green-100 text-green-800';
      case 'UPDATE': return 'bg-blue-100 text-blue-800';
      case 'CANCEL': return 'bg-red-100 text-red-800';
      case 'APPROVE': return 'bg-purple-100 text-purple-800';
      case 'REJECT': return 'bg-orange-100 text-orange-800';
      case 'BATCH_CREATE': return 'bg-teal-100 text-teal-800';
      case 'BATCH_UPDATE': return 'bg-indigo-100 text-indigo-800';
      case 'SYSTEM_AUTO': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderChanges = (changes: Record<string, any>) => {
    if (!changes || Object.keys(changes).length === 0) {
      return <span className="text-gray-500">Sin cambios</span>;
    }
    
    return (
      <div className="space-y-1">
        {Object.entries(changes).map(([field, change]) => (
          <div key={field} className="text-xs">
            <span className="font-medium">{field}:</span>
            <span className="text-red-600 line-through ml-1">{String(change.old)}</span>
            <span className="text-green-600 ml-1">→ {String(change.new)}</span>
          </div>
        ))}
      </div>
    );
  };

  const renderHistoryTab = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Historial de Movimiento</h3>
        {movementId && (
          <button
            onClick={fetchMovementHistory}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Actualizar
          </button>
        )}
      </div>
      
      {loading && <div className="text-center py-4">Cargando historial...</div>}
      {error && <div className="text-red-600 text-center py-4">{error}</div>}
      
      {trackingHistory.length === 0 && !loading && !error && (
        <div className="text-gray-500 text-center py-4">
          {movementId ? 'No hay historial disponible para este movimiento' : 'Seleccione un movimiento para ver su historial'}
        </div>
      )}
      
      <div className="space-y-3">
        {trackingHistory.map((track) => (
          <div key={track.id} className="border rounded-lg p-4 bg-white shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionTypeColor(track.action_type)}`}>
                  {track.action_type}
                </span>
                {track.is_system_action && (
                  <span className="px-2 py-1 rounded-full text-xs bg-gray-200 text-gray-600">
                    Sistema
                  </span>
                )}
              </div>
              <span className="text-xs text-gray-500">
                {format(new Date(track.action_timestamp), 'dd/MM/yyyy HH:mm:ss', { locale: es })}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm">
                  <span className="font-medium">Usuario: </span>
                  {track.user_name}
                </div>
                {track.ip_address && (
                  <div className="text-sm">
                    <span className="font-medium">IP: </span>
                    {track.ip_address}
                  </div>
                )}
                {track.session_id && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Sesión: </span>
                    {track.session_id.substring(0, 8)}...
                  </div>
                )}
              </div>
              
              <div>
                {track.has_location_change && (
                  <div className="text-sm">
                    <span className="font-medium">Ubicación: </span>
                    <span className="text-blue-600">
                      {track.location_from?.name || 'Origen'} → {track.location_to?.name || 'Destino'}
                    </span>
                  </div>
                )}
                {track.notes && (
                  <div className="text-sm">
                    <span className="font-medium">Notas: </span>
                    {track.notes}
                  </div>
                )}
              </div>
            </div>
            
            {track.changes && Object.keys(track.changes).length > 0 && (
              <div className="mt-3 pt-3 border-t">
                <div className="font-medium text-sm mb-2">Cambios realizados:</div>
                {renderChanges(track.changes)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Analytics de Movimientos</h3>
        <div className="flex space-x-2">
          <div className="relative group">
            <button className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600">
              Exportar ▼
            </button>
            <div className="absolute right-0 mt-1 bg-white border border-gray-300 rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
              <button
                onClick={() => handleExport('csv')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              >
                CSV
              </button>
              <button
                onClick={() => handleExport('excel')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              >
                Excel
              </button>
              <button
                onClick={() => handleExport('json')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              >
                JSON
              </button>
            </div>
          </div>
          <button
            onClick={fetchAnalytics}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Actualizar
          </button>
        </div>
      </div>
      
      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
        <div>
          <label className="block text-sm font-medium mb-1">Fecha Inicio</label>
          <input
            type="date"
            value={dateFilter.start_date}
            onChange={(e) => setDateFilter(prev => ({ ...prev, start_date: e.target.value }))}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Fecha Fin</label>
          <input
            type="date"
            value={dateFilter.end_date}
            onChange={(e) => setDateFilter(prev => ({ ...prev, end_date: e.target.value }))}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tipo Movimiento</label>
          <select
            value={movementTypeFilter}
            onChange={(e) => setMovementTypeFilter(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">Todos</option>
            <option value="INGRESO">Ingreso</option>
            <option value="SALIDA">Salida</option>
            <option value="AJUSTE_POSITIVO">Ajuste Positivo</option>
            <option value="AJUSTE_NEGATIVO">Ajuste Negativo</option>
            <option value="TRANSFERENCIA">Transferencia</option>
            <option value="DEVOLUCION">Devolución</option>
            <option value="MERMA">Merma</option>
            <option value="RESERVA">Reserva</option>
            <option value="LIBERACION">Liberación</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={fetchAnalytics}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Aplicar Filtros
          </button>
        </div>
      </div>
      
      {loading && <div className="text-center py-4">Cargando analytics...</div>}
      {error && <div className="text-red-600 text-center py-4">{error}</div>}
      
      {analytics && (
        <div className="space-y-6">
          {/* Resumen */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{analytics.total_movements}</div>
              <div className="text-sm text-blue-800">Total de Movimientos</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {Object.keys(analytics.movements_by_type).length}
              </div>
              <div className="text-sm text-green-800">Tipos de Movimiento</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Object.keys(analytics.movements_by_user).length}
              </div>
              <div className="text-sm text-purple-800">Usuarios Activos</div>
            </div>
          </div>
          
          {/* Movimientos por tipo */}
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold mb-3">Movimientos por Tipo</h4>
            <div className="space-y-2">
              {Object.entries(analytics.movements_by_type).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="text-sm">{type}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ 
                          width: `${(count / Math.max(...Object.values(analytics.movements_by_type))) * 100}%` 
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Actividad por fecha */}
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold mb-3">Actividad por Fecha (Últimos 10 días)</h4>
            <div className="space-y-2">
              {Object.entries(analytics.movements_by_date)
                .sort(([a], [b]) => b.localeCompare(a))
                .slice(0, 10)
                .map(([date, count]) => (
                  <div key={date} className="flex justify-between items-center">
                    <span className="text-sm">{format(new Date(date), 'dd/MM/yyyy', { locale: es })}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ 
                            width: `${(count / Math.max(...Object.values(analytics.movements_by_date))) * 100}%` 
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow">
      {showAnalytics && (
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setSelectedTab('history')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Historial
            </button>
            <button
              onClick={() => setSelectedTab('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'analytics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>
      )}
      
      <div className="p-6">
        {!showAnalytics || selectedTab === 'history' ? renderHistoryTab() : renderAnalyticsTab()}
      </div>
    </div>
  );
};

export default MovementTracker;