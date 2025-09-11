/**
 * Dashboard de gestión de almacén con visualización de ocupación en tiempo real
 * Archivo: frontend/src/components/admin/StorageManagerDashboard.tsx
 * Autor: Sistema de desarrollo
 * Fecha: 2025-01-15
 * Propósito: Dashboard visual completo para StorageManager con gráficos Recharts
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import { 
  Warehouse, AlertTriangle, TrendingUp, Eye, RefreshCw, 
  Package, MapPin, Gauge
} from 'lucide-react';

interface ZoneData {
  zone: string;
  total_capacity: number;
  occupied_space: number;
  available_space: number;
  utilization_percentage: number;
  status: string;
  total_products: number;
  shelves_count: number;
}

interface StorageOverview {
  zones: ZoneData[];
  summary: {
    total_zones: number;
    total_capacity: number;
    total_occupied: number;
    total_available: number;
    overall_utilization: number;
    status: string;
    last_updated: string;
  };
}

const StorageManagerDashboard: React.FC = () => {
  const [overview, setOverview] = useState<StorageOverview | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [, setSelectedZone] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStorageData();
  }, []);

  const loadStorageData = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      
      // Debug: verificar token
      console.log('🔑 Token encontrado:', token ? 'Sí' : 'No');
      console.log('🔑 Token value (first 20 chars):', token ? token.substring(0, 20) + '...' : 'null');
      
      if (!token) {
        console.error('❌ No se encontró token de acceso');
        setLoading(false);
        setRefreshing(false);
        return;
      }
      
      // Cargar overview
      const overviewResponse = await fetch(
        '/api/v1/admin/storage/overview',
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('📊 Overview response:', overviewResponse.status);
      
      if (overviewResponse.ok) {
        const overviewData = await overviewResponse.json();
        setOverview(overviewData);
        console.log('✅ Overview data loaded');
      } else {
        const errorText = await overviewResponse.text();
        console.error('❌ Overview error:', overviewResponse.status, errorText);
      }

      // Cargar alertas
      const alertsResponse = await fetch(
        '/api/v1/admin/storage/alerts',
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('🚨 Alerts response:', alertsResponse.status);
      
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts);
        console.log('✅ Alerts data loaded');
      } else {
        const errorText = await alertsResponse.text();
        console.error('❌ Alerts error:', alertsResponse.status, errorText);
      }

      // Cargar tendencias
      const trendsResponse = await fetch(
        '/api/v1/admin/storage/trends?days=7',
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('📈 Trends response:', trendsResponse.status);
      
      if (trendsResponse.ok) {
        const trendsData = await trendsResponse.json();
        setTrends(trendsData.trends);
        console.log('✅ Trends data loaded');
      } else {
        const errorText = await trendsResponse.text();
        console.error('❌ Trends error:', trendsResponse.status, errorText);
      }

    } catch (error) {
      console.error('Error loading storage data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      empty: '#e5e7eb',
      low: '#22c55e',
      moderate: '#3b82f6',
      high: '#f59e0b',
      critical: '#ef4444',
      full: '#7c2d12'
    };
    return colors[status] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Warehouse className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">Cargando datos del almacén...</p>
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="w-12 h-12 mx-auto text-red-400 mb-4" />
        <p className="text-red-600">Error cargando datos del almacén</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center">
          <Warehouse className="w-6 h-6 mr-2 text-blue-600" />
          Storage Manager
        </h2>
        <button
          onClick={loadStorageData}
          disabled={refreshing}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>

      {/* Resumen General */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Utilización General</p>
              <p className="text-2xl font-bold">{overview.summary.overall_utilization}%</p>
            </div>
            <Gauge className="w-8 h-8 text-blue-600" />
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${overview.summary.overall_utilization}%` }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Capacidad Total</p>
              <p className="text-2xl font-bold">{overview.summary.total_capacity}</p>
            </div>
            <Package className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {overview.summary.total_available} disponibles
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Zonas Activas</p>
              <p className="text-2xl font-bold">{overview.summary.total_zones}</p>
            </div>
            <MapPin className="w-8 h-8 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Estado: {overview.summary.status}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertas Activas</p>
              <p className="text-2xl font-bold">{alerts.length}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {alerts.filter(a => a.level === 'critical').length} críticas
          </p>
        </div>
      </div>

      {/* Alertas */}
      {alerts.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
            Alertas del Sistema
          </h3>
          <div className="space-y-2">
            {alerts.slice(0, 5).map((alert, index) => (
              <div
                key={index}
                className={`p-3 rounded border-l-4 ${
                  alert.level === 'critical' ? 'bg-red-50 border-red-400' :
                  alert.level === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                  'bg-blue-50 border-blue-400'
                }`}
              >
                <div className="flex justify-between items-center">
                  <p className="font-medium">{alert.message}</p>
                  <span className={`px-2 py-1 rounded text-xs ${
                    alert.level === 'critical' ? 'bg-red-100 text-red-800' :
                    alert.level === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {alert.level.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ocupación por Zona */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Ocupación por Zona</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={overview.zones}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="zone" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'utilization_percentage' ? `${value}%` : value,
                  name === 'utilization_percentage' ? 'Utilización' : 'Capacidad'
                ]}
              />
              <Legend />
              <Bar dataKey="total_capacity" fill="#e5e7eb" name="Capacidad Total" />
              <Bar dataKey="occupied_space" fill="#3b82f6" name="Espacio Ocupado" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribución de Estados */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Distribución por Estado</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={overview.zones.map(zone => ({
                  name: `Zona ${zone.zone}`,
                  value: zone.utilization_percentage,
                  status: zone.status
                }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {overview.zones.map((zone, index) => (
                  <Cell key={`cell-${index}`} fill={getStatusColor(zone.status)} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value}%`, 'Utilización']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tendencias */}
      {trends.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Tendencias de Utilización (7 días)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Utilización']} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="overall_utilization" 
                stroke="#3b82f6" 
                fill="#3b82f6" 
                fillOpacity={0.3}
                name="Utilización General"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Tabla de Zonas Detallada */}
      <div className="bg-white rounded-lg shadow border overflow-hidden">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Detalle por Zonas</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Zona
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utilización
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Capacidad
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Productos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {overview.zones.map((zone) => (
                <tr key={zone.zone} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">Zona {zone.zone}</div>
                    <div className="text-sm text-gray-500">{zone.shelves_count} estantes</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-1 mr-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full transition-all duration-300"
                            style={{ 
                              width: `${zone.utilization_percentage}%`,
                              backgroundColor: getStatusColor(zone.status)
                            }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-medium">
                        {zone.utilization_percentage}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {zone.occupied_space} / {zone.total_capacity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {zone.total_products}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      zone.status === 'critical' ? 'bg-red-100 text-red-800' :
                      zone.status === 'high' ? 'bg-yellow-100 text-yellow-800' :
                      zone.status === 'moderate' ? 'bg-blue-100 text-blue-800' :
                      zone.status === 'low' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {zone.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedZone(zone.zone)}
                      className="text-blue-600 hover:text-blue-900 flex items-center"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Ver Detalles
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StorageManagerDashboard;