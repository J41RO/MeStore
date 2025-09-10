import React, { useState, useEffect } from 'react';
import { InventoryTable } from '../../components/ui/InventoryTable/InventoryTable';
import { InventoryItem, TipoIncidente, EstadoIncidente } from '../../types/inventory.types';

interface AlertasMetadata {
  total_alertas: number;
  stock_bajo: number;
  sin_movimiento: number;
  stock_agotado: number;
  criticos: number;
  perdidos: number;
  danados: number;
}

interface AlertasStats {
  alertas: InventoryItem[];
  metadata: AlertasMetadata;
}

interface IncidentesList {
  id: string;
  inventory_id: string;
  tipo_incidente: TipoIncidente;
  estado: EstadoIncidente;
  descripcion: string;
  reportado_por: string;
  created_at: string;
}

export const AlertasIncidentes: React.FC = () => {
  const [alertasData, setAlertasData] = useState<AlertasStats | null>(null);
  const [incidentes, setIncidentes] = useState<IncidentesList[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'alertas' | 'incidentes'>('alertas');

  const fetchAlertasData = async () => {
    try {
      const response = await fetch('/api/v1/inventory/alertas', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAlertasData(data);
      }
    } catch (error) {
      console.error('Error fetching alertas:', error);
    }
  };

  const fetchIncidentes = async () => {
    try {
      const response = await fetch('/api/v1/inventory/incidentes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setIncidentes(data);
      }
    } catch (error) {
      console.error('Error fetching incidentes:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchAlertasData(), fetchIncidentes()]);
      setLoading(false);
    };
    loadData();
  }, []);

  const getEstadoBadgeColor = (estado: EstadoIncidente) => {
    switch (estado) {
      case EstadoIncidente.REPORTADO:
        return 'bg-red-100 text-red-800';
      case EstadoIncidente.EN_INVESTIGACION:
        return 'bg-yellow-100 text-yellow-800';
      case EstadoIncidente.RESUELTO:
        return 'bg-blue-100 text-blue-800';
      case EstadoIncidente.CERRADO:
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Cargando datos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Alertas e Incidentes de Inventario</h1>
          <p className="mt-1 text-sm text-gray-600">
            Monitoreo y gestión de alertas de stock y incidentes de productos perdidos o dañados.
          </p>
        </div>

        {/* Estadísticas de Alertas */}
        {alertasData && (
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumen de Alertas</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              <div className="bg-blue-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">{alertasData.metadata.total_alertas}</div>
                <div className="text-sm text-blue-600">Total</div>
              </div>
              <div className="bg-yellow-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-600">{alertasData.metadata.stock_bajo}</div>
                <div className="text-sm text-yellow-600">Stock Bajo</div>
              </div>
              <div className="bg-red-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-600">{alertasData.metadata.stock_agotado}</div>
                <div className="text-sm text-red-600">Agotado</div>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">{alertasData.metadata.sin_movimiento}</div>
                <div className="text-sm text-purple-600">Sin Movimiento</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-orange-600">{alertasData.metadata.criticos}</div>
                <div className="text-sm text-orange-600">Críticos</div>
              </div>
              <div className="bg-red-100 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-700">{alertasData.metadata.perdidos}</div>
                <div className="text-sm text-red-700">Perdidos</div>
              </div>
              <div className="bg-red-200 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-800">{alertasData.metadata.danados}</div>
                <div className="text-sm text-red-800">Dañados</div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="px-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('alertas')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'alertas'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Productos con Alertas ({alertasData?.alertas.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('incidentes')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'incidentes'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Incidentes Reportados ({incidentes.length})
              </button>
            </nav>
          </div>
        </div>

        {/* Contenido de Tabs */}
        <div className="px-6 py-4">
          {activeTab === 'alertas' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Inventario con Alertas</h3>
              {alertasData?.alertas.length ? (
                <InventoryTable data={alertasData.alertas} />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No hay productos con alertas actualmente.
                </div>
              )}
            </div>
          )}

          {activeTab === 'incidentes' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Incidentes Reportados</h3>
              {incidentes.length ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Tipo
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Estado
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Descripción
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Reportado por
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Fecha
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {incidentes.map((incidente) => (
                        <tr key={incidente.id} className="hover:bg-gray-50">
                          <td className="px-4 py-4 text-sm">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              incidente.tipo_incidente === TipoIncidente.PERDIDO
                                ? 'bg-red-100 text-red-800'
                                : 'bg-orange-100 text-orange-800'
                            }`}>
                              {incidente.tipo_incidente}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm">
                            <span className={`px-2 py-1 text-xs rounded-full ${getEstadoBadgeColor(incidente.estado)}`}>
                              {incidente.estado.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-900 max-w-xs truncate">
                            {incidente.descripcion}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-500">
                            {incidente.reportado_por}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-500">
                            {new Date(incidente.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No hay incidentes reportados actualmente.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertasIncidentes;