import React, { useState, useEffect } from 'react';
import GrowthChart, { GrowthData } from '../../components/charts/GrowthChart';
import MonthlyComparisonChart, {
  MonthlyComparisonData,
} from '../../components/charts/MonthlyComparisonChart';
import { useNavigate } from 'react-router-dom';

interface AlertasMetadata {
  total_alertas: number;
  stock_bajo: number;
  sin_movimiento: number;
  stock_agotado: number;
  criticos: number;
  perdidos: number;
  danados: number;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [alertasData, setAlertasData] = useState<AlertasMetadata | null>(null);

  // Cargar datos de alertas
  useEffect(() => {
    const fetchAlertas = async () => {
      try {
        const response = await fetch('/api/v1/inventory/alertas', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setAlertasData(data.metadata);
        }
      } catch (error) {
        console.error('Error fetching alertas:', error);
      }
    };
    fetchAlertas();
  }, []);

  // Datos de ejemplo para gráficos de crecimiento
  const growthData: GrowthData[] = [
    {
      month: 'Ene',
      currentPeriod: 12000,
      previousPeriod: 10000,
      growthRate: 20,
    },
    {
      month: 'Feb',
      currentPeriod: 15000,
      previousPeriod: 12000,
      growthRate: 25,
    },
    {
      month: 'Mar',
      currentPeriod: 18000,
      previousPeriod: 14000,
      growthRate: 28.6,
    },
    {
      month: 'Abr',
      currentPeriod: 22000,
      previousPeriod: 16000,
      growthRate: 37.5,
    },
    {
      month: 'May',
      currentPeriod: 25000,
      previousPeriod: 18000,
      growthRate: 38.9,
    },
    {
      month: 'Jun',
      currentPeriod: 28000,
      previousPeriod: 20000,
      growthRate: 40,
    },
  ];

  const comparisonData: MonthlyComparisonData[] = [
    {
      month: 'Ene',
      currentPeriod: 12000,
      previousPeriod: 10000,
      category: 'ventas',
    },
    {
      month: 'Feb',
      currentPeriod: 15000,
      previousPeriod: 12000,
      category: 'ventas',
    },
    {
      month: 'Mar',
      currentPeriod: 18000,
      previousPeriod: 14000,
      category: 'ventas',
    },
    {
      month: 'Abr',
      currentPeriod: 22000,
      previousPeriod: 16000,
      category: 'ventas',
    },
    {
      month: 'May',
      currentPeriod: 25000,
      previousPeriod: 18000,
      category: 'ventas',
    },
    {
      month: 'Jun',
      currentPeriod: 28000,
      previousPeriod: 20000,
      category: 'ventas',
    },
  ];
  return (
    <div className='space-y-6'>
      <div className='bg-white shadow rounded-lg p-6'>
        <h1 className='text-2xl font-bold text-gray-900 mb-4'>
          Dashboard Administrativo
        </h1>
        <p className='text-gray-600 mb-6'>
          Panel de control general para administradores del sistema.
        </p>

        {/* Sección de Alertas de Inventario */}
        <div className='bg-white shadow rounded-lg p-6 mb-6'>
          <div className='flex items-center justify-between mb-4'>
            <h2 className='text-xl font-semibold text-gray-900'>Alertas de Inventario</h2>
            <button
              onClick={() => navigate('/admin-secure-portal/alertas-incidentes')}
              className='px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm'
            >
              Ver Todas las Alertas
            </button>
          </div>
          
          {alertasData ? (
            <div className='grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-4'>
              <div className='bg-blue-50 p-3 rounded-lg text-center border-l-4 border-blue-500'>
                <div className='text-2xl font-bold text-blue-600'>{alertasData.total_alertas}</div>
                <div className='text-sm text-blue-600'>Total Alertas</div>
              </div>
              <div className='bg-yellow-50 p-3 rounded-lg text-center border-l-4 border-yellow-500'>
                <div className='text-2xl font-bold text-yellow-600'>{alertasData.stock_bajo}</div>
                <div className='text-sm text-yellow-600'>Stock Bajo</div>
              </div>
              <div className='bg-red-50 p-3 rounded-lg text-center border-l-4 border-red-500'>
                <div className='text-2xl font-bold text-red-600'>{alertasData.stock_agotado}</div>
                <div className='text-sm text-red-600'>Agotado</div>
              </div>
              <div className='bg-purple-50 p-3 rounded-lg text-center border-l-4 border-purple-500'>
                <div className='text-2xl font-bold text-purple-600'>{alertasData.sin_movimiento}</div>
                <div className='text-sm text-purple-600'>Sin Movimiento</div>
              </div>
              <div className='bg-orange-50 p-3 rounded-lg text-center border-l-4 border-orange-500'>
                <div className='text-2xl font-bold text-orange-600'>{alertasData.criticos}</div>
                <div className='text-sm text-orange-600'>Críticos</div>
              </div>
              <div className='bg-red-100 p-3 rounded-lg text-center border-l-4 border-red-600'>
                <div className='text-2xl font-bold text-red-700'>{alertasData.perdidos}</div>
                <div className='text-sm text-red-700'>🔍 Perdidos</div>
              </div>
              <div className='bg-red-200 p-3 rounded-lg text-center border-l-4 border-red-700'>
                <div className='text-2xl font-bold text-red-800'>{alertasData.danados}</div>
                <div className='text-sm text-red-800'>⚠️ Dañados</div>
              </div>
            </div>
          ) : (
            <div className='bg-gray-50 p-4 rounded-lg text-center'>
              <div className='text-gray-500'>Cargando datos de alertas...</div>
            </div>
          )}

          {/* Alertas críticas destacadas */}
          {alertasData && (alertasData.perdidos > 0 || alertasData.danados > 0) && (
            <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
              <div className='flex items-center'>
                <div className='flex-shrink-0'>
                  <div className='h-6 w-6 bg-red-100 rounded-full flex items-center justify-center'>
                    <span className='text-red-600 text-sm'>⚠️</span>
                  </div>
                </div>
                <div className='ml-3'>
                  <h3 className='text-sm font-medium text-red-800'>
                    Atención: Incidentes de Inventario Detectados
                  </h3>
                  <div className='mt-2 text-sm text-red-700'>
                    <p>
                      Se han reportado {alertasData.perdidos + alertasData.danados} incidentes 
                      ({alertasData.perdidos} productos perdidos, {alertasData.danados} productos dañados).
                      <button 
                        onClick={() => navigate('/admin-secure-portal/alertas-incidentes')}
                        className='ml-2 underline hover:no-underline'
                      >
                        Revisar incidentes →
                      </button>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className='grid grid-cols-1 md:grid-cols-4 gap-4 mb-6'>
          <div className='bg-red-50 p-4 rounded-lg border-l-4 border-red-500'>
            <h3 className='font-semibold text-red-900'>Sistema</h3>
            <p className='text-lg font-bold text-red-700'>Operativo</p>
          </div>

          {/* Sección de Análisis de Crecimiento */}
          <div className='mt-8'>
            <h2 className='text-xl font-semibold text-gray-900 mb-6'>
              Análisis de Crecimiento
            </h2>

            {/* Grid de gráficos */}
            <div className='grid grid-cols-1 xl:grid-cols-2 gap-6'>
              {/* Gráfico de Crecimiento Temporal */}
              <div className='bg-white shadow rounded-lg p-6'>
                <GrowthChart
                  data={growthData}
                  title='Tendencia de Crecimiento'
                  height={350}
                />
              </div>

              {/* Gráfico de Comparación Mensual */}
              <div className='bg-white shadow rounded-lg p-6'>
                <MonthlyComparisonChart
                  data={comparisonData}
                  title='Comparativa Período Actual vs Anterior'
                  height={350}
                />
              </div>
            </div>
          </div>
          <div className='bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500'>
            <h3 className='font-semibold text-blue-900'>Usuarios Online</h3>
            <p className='text-lg font-bold text-blue-700'>0</p>
          </div>
          <div className='bg-green-50 p-4 rounded-lg border-l-4 border-green-500'>
            <h3 className='font-semibold text-green-900'>Transacciones</h3>
            <p className='text-lg font-bold text-green-700'>0</p>
          </div>
          <div className='bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500'>
            <h3 className='font-semibold text-yellow-900'>Alertas</h3>
            <p className='text-lg font-bold text-yellow-700'>{alertasData?.total_alertas || 0}</p>
          </div>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <div className='border rounded-lg p-4'>
            <h3 className='font-semibold text-gray-900 mb-2'>Acceso Rápido</h3>
            <div className='space-y-2'>
              <button 
                onClick={() => navigate('/admin-secure-portal/users')}
                className='w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200'
              >
                Gestión de Usuarios
              </button>
              <button 
                onClick={() => navigate('/admin-secure-portal/alertas-incidentes')}
                className='w-full text-left px-3 py-2 bg-red-100 rounded hover:bg-red-200 text-red-700 font-medium'
              >
                🔍 Alertas e Incidentes
              </button>
              <button 
                onClick={() => navigate('/admin-secure-portal/reportes-discrepancias')}
                className='w-full text-left px-3 py-2 bg-green-100 rounded hover:bg-green-200 text-green-700 font-medium'
              >
                📊 Reportes de Discrepancias
              </button>
              <button 
                onClick={() => navigate('/admin-secure-portal/system-config')}
                className='w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200'
              >
                Configuración del Sistema
              </button>
              <button 
                onClick={() => navigate('/admin-secure-portal/reports')}
                className='w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200'
              >
                Reportes
              </button>
            </div>
          </div>

          <div className='border rounded-lg p-4'>
            <h3 className='font-semibold text-gray-900 mb-2'>
              Actividad Reciente
            </h3>
            <div className='text-sm text-gray-600 space-y-2'>
              <p>• Sistema iniciado correctamente</p>
              <p>• AdminLayout configurado</p>
              <p>• Rutas administrativas listas</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
