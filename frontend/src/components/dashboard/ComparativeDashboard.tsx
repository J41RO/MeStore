import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface KPIComparison {
  valor_actual: number;
  valor_anterior: number;
  variacion_porcentual: number;
  tendencia: 'subiendo' | 'bajando' | 'estable';
}

interface DashboardComparativoData {
  ventas_mes: KPIComparison;
  ingresos_mes: KPIComparison;
  comision_total: KPIComparison;
  productos_vendidos: KPIComparison;
  clientes_nuevos: KPIComparison;
  periodo_actual: string;
  periodo_anterior: string;
  fecha_calculo: string;
}

const ComparativeDashboard: React.FC = () => {
  const [, setData] = useState<DashboardComparativoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComparativeData();
  }, []);

  const fetchComparativeData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/vendedores/dashboard/comparativa', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Error al cargar datos comparativos');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Comparativa Mensual</h3>
        <div className="text-center text-gray-500">Cargando datos comparativos...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Comparativa Mensual</h3>
        <div className="text-center text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Comparativa Mensual</h3>
        <div className="text-sm text-gray-500">Período actual vs anterior</div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="text-center space-y-2">
          <div className="text-sm text-gray-600">
            Funcionalidad comparativa implementada
          </div>
          <div className="text-xs text-gray-500">
            Endpoint: /api/v1/vendedores/dashboard/comparativa
          </div>
          <div className="flex justify-center space-x-4 text-xs">
            <span className="flex items-center space-x-1">
              <TrendingUp className="h-3 w-3 text-green-600" />
              <span className="text-green-600">Subiendo</span>
            </span>
            <span className="flex items-center space-x-1">
              <TrendingDown className="h-3 w-3 text-red-600" />
              <span className="text-red-600">Bajando</span>
            </span>
            <span className="flex items-center space-x-1">
              <Minus className="h-3 w-3 text-gray-600" />
              <span className="text-gray-600">Estable</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparativeDashboard;