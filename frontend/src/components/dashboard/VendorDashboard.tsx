import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useVendorMetrics } from '../../hooks/useVendorMetrics';
import { MetricsGrid } from './MetricsGrid';
import TopProductsWidget from '../widgets/TopProductsWidget';
import { Link } from 'react-router-dom';
import { 
  PackageIcon, 
 
  ShoppingBagIcon, 
  BarChart3Icon,
  UsersIcon,
  AlertCircleIcon,
  PlusIcon,
  RefreshCwIcon
} from 'lucide-react';

interface VendorMetrics {
  totalProductos?: number;
  productosActivos?: number;
  totalVentas?: number;
  ventasDelMes?: number;
  ingresosTotales?: number;
  ingresosMes?: number;
  ordenesPendientes?: number;
  ordenesCompletadas?: number;
  productosChange?: number;
  ventasChange?: number;
  ingresosChange?: number;
  ordenesChange?: number;
}

interface VendorDashboardProps {
  vendorId?: string;
  className?: string;
}

interface ProductoReciente {
  id: string;
  nombre: string;
  precio: number;
  stock: number;
  estado: string;
  fechaCreacion: string;
  imagen?: string;
}

interface OrdenReciente {
  id: string;
  cliente: string;
  total: number;
  estado: string;
  fecha: string;
  productos: number;
}

const VendorDashboard: React.FC<VendorDashboardProps> = ({
  vendorId,
  className = ""
}) => {
  const [_productosRecientes, setProductosRecientes] = useState<ProductoReciente[]>([]);
  const [ordenesRecientes, setOrdenesRecientes] = useState<OrdenReciente[]>([]);
  const [additionalLoading, setAdditionalLoading] = useState(true);
  const [additionalError, setAdditionalError] = useState('');
  
  const { user, isAuthenticated } = useAuthStore();
  const { metrics, loading, error, refreshMetrics, isRefreshing } = useVendorMetrics(vendorId);

  useEffect(() => {
    const fetchAdditionalData = async () => {
      if (!isAuthenticated) {
        setAdditionalError('Usuario no autenticado');
        setAdditionalLoading(false);
        return;
      }

      try {
        // Datos temporales hasta que la API esté funcionando
        // TODO: Reemplazar con llamada real a la API cuando esté configurada
        const ordenesMapeadas = [
          {
            id: 'ORD-001',
            cliente: 'Juan Pérez',
            total: 125000,
            estado: 'pendiente',
            fecha: new Date().toISOString(),
            productos: 2
          },
          {
            id: 'ORD-002',
            cliente: 'María García',
            total: 85000,
            estado: 'procesando',
            fecha: new Date(Date.now() - 3600000).toISOString(),
            productos: 1
          },
          {
            id: 'ORD-003',
            cliente: 'Carlos López',
            total: 200000,
            estado: 'completado',
            fecha: new Date(Date.now() - 86400000).toISOString(),
            productos: 3
          }
        ];
        
        setOrdenesRecientes(ordenesMapeadas);

        // Fetch productos recientes (simulado por ahora hasta tener API)
        setProductosRecientes([
          {
            id: '1',
            nombre: 'Producto Ejemplo 1',
            precio: 25000,
            stock: 10,
            estado: 'activo',
            fechaCreacion: new Date().toISOString(),
          },
          {
            id: '2', 
            nombre: 'Producto Ejemplo 2',
            precio: 45000,
            stock: 5,
            estado: 'activo',
            fechaCreacion: new Date(Date.now() - 86400000).toISOString(),
          }
        ]);

      } catch (error: any) {
        setAdditionalError(error.response?.data?.message || 'Error cargando datos adicionales');
        console.error('Additional dashboard data error:', error);
        
        // Fallback a datos simulados si la API falla
        setOrdenesRecientes([
          {
            id: 'ORD001',
            cliente: 'Juan Pérez',
            total: 75000,
            estado: 'pendiente',
            fecha: new Date().toISOString(),
            productos: 2
          },
          {
            id: 'ORD002',
            cliente: 'María García',
            total: 45000,
            estado: 'procesando',
            fecha: new Date(Date.now() - 3600000).toISOString(),
            productos: 1
          }
        ]);
      } finally {
        setAdditionalLoading(false);
      }
    };

    fetchAdditionalData();
  }, [isAuthenticated]);

  const isLoading = loading || additionalLoading;
  const hasError = error || additionalError;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircleIcon className="h-5 w-5 text-red-400 mr-2" />
          <span className="text-red-700">Error: {hasError}</span>
        </div>
        <button 
          onClick={refreshMetrics}
          className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Reintentar
        </button>
      </div>
    );
  }

  // Check if vendor is new (no products)
  const isNewVendor = (metrics?.totalProductos || 0) === 0;

  return (
    <div className={`vendor-dashboard space-y-6 ${className}`}>
      {/* Dashboard Header */}
      <DashboardHeader user={user} metrics={metrics} onRefresh={refreshMetrics} isRefreshing={isRefreshing} />

      {/* Welcome Card for New Vendors */}
      {isNewVendor && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <PackageIcon className="h-12 w-12 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                ¡Bienvenido a MeStocker! 🎉
              </h3>
              <p className="text-gray-700 mb-4">
                Comienza tu viaje como vendedor subiendo tu primer producto. Es rápido y fácil.
              </p>
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">✓</span>
                  <span>Agrega fotos y descripciones detalladas</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">✓</span>
                  <span>Define precios competitivos</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">✓</span>
                  <span>Gestiona tu inventario fácilmente</span>
                </div>
              </div>
              <Link
                to="/app/productos"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Subir Mi Primer Producto
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <MetricsGrid metrics={metrics} loading={loading} className="" />

      {/* Charts Section */}
      {!isNewVendor && <ChartsSection metrics={metrics} />}

      {/* Main Content Grid */}
      {!isNewVendor && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopProductsWidget className="" maxProducts={5} />
          <OrdenesBasicaSection ordenes={ordenesRecientes} />
        </div>
      )}

      {/* Quick Actions Footer */}
      <QuickActionsFooter />
    </div>
  );
};

// Dashboard Header Component
const DashboardHeader: React.FC<{ user: any; metrics: any; onRefresh: () => void; isRefreshing: boolean }> = ({ user, metrics, onRefresh, isRefreshing }) => {
  const currentHour = new Date().getHours();
  const greeting = currentHour < 12 ? 'Buenos días' : currentHour < 18 ? 'Buenas tardes' : 'Buenas noches';
  
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow p-6 text-white">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold mb-2">
            {greeting}, {user?.nombre || user?.email}
          </h1>
          <p className="text-blue-100">
            Resumen de tu actividad como vendedor
          </p>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end mb-2">
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="text-blue-200 hover:text-white transition-colors disabled:opacity-50"
              title="Actualizar métricas"
            >
              <RefreshCwIcon className={`h-5 w-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <p className="text-sm text-blue-200">Productos activos</p>
          <p className="text-3xl font-bold">{metrics?.productosActivos || 0}</p>
        </div>
      </div>
    </div>
  );
};


// Charts Section Component
const ChartsSection: React.FC<{ metrics: VendorMetrics | null }> = ({ metrics: _metrics }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Resumen de Ventas</h3>
        <BarChart3Icon className="h-5 w-5 text-gray-400" />
      </div>
      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">Gráfico de ventas (próximamente)</p>
      </div>
    </div>
  );
};

// Productos Recientes Section
/*
const _ProductosRecientesSection: React.FC<{ productos: ProductoReciente[] }> = ({ productos }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Productos Recientes</h3>
        <Link 
          to="/app/productos" 
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Ver todos →
        </Link>
      </div>
      
      <div className="space-y-3">
        {productos.map(producto => (
          <div key={producto.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-gray-900">{producto.nombre}</p>
              <p className="text-sm text-gray-600">
                ${producto.precio.toLocaleString()} • Stock: {producto.stock}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                producto.estado === 'activo' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {producto.estado}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <Link
          to="/app/productos"
          className="inline-flex items-center px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Agregar Producto
        </Link>
      </div>
    </div>
  );
};
*/

// Órdenes Básica Section
const OrdenesBasicaSection: React.FC<{ ordenes: OrdenReciente[] }> = ({ ordenes }) => {
  const getStatusColor = (estado: string) => {
    switch (estado) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800';
      case 'procesando':
        return 'bg-blue-100 text-blue-800';
      case 'completado':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Órdenes Recientes</h3>
        <Link 
          to="/app/ordenes" 
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Ver todas →
        </Link>
      </div>
      
      <div className="space-y-3">
        {ordenes.map(orden => (
          <div key={orden.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-gray-900">#{orden.id}</p>
              <p className="text-sm text-gray-600">
                {orden.cliente} • {orden.productos} producto{orden.productos > 1 ? 's' : ''}
              </p>
            </div>
            <div className="text-right">
              <p className="font-medium text-gray-900">${orden.total.toLocaleString()}</p>
              <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getStatusColor(orden.estado)}`}>
                {orden.estado}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {ordenes.length === 0 && (
        <div className="text-center py-8">
          <UsersIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No hay órdenes recientes</p>
        </div>
      )}
    </div>
  );
};

// Quick Actions Footer
const QuickActionsFooter: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link
          to="/app/productos"
          className="flex flex-col items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
        >
          <PlusIcon className="h-8 w-8 text-blue-600 mb-2" />
          <span className="text-sm font-medium text-blue-700">Nuevo Producto</span>
        </Link>
        
        <Link 
          to="/app/ordenes"
          className="flex flex-col items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
        >
          <ShoppingBagIcon className="h-8 w-8 text-green-600 mb-2" />
          <span className="text-sm font-medium text-green-700">Ver Órdenes</span>
        </Link>
        
        <Link 
          to="/app/productos"
          className="flex flex-col items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
        >
          <PackageIcon className="h-8 w-8 text-purple-600 mb-2" />
          <span className="text-sm font-medium text-purple-700">Mis Productos</span>
        </Link>
        
        <Link 
          to="/app/reportes"
          className="flex flex-col items-center p-4 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors"
        >
          <BarChart3Icon className="h-8 w-8 text-orange-600 mb-2" />
          <span className="text-sm font-medium text-orange-700">Reportes</span>
        </Link>
      </div>
    </div>
  );
};

export default VendorDashboard;