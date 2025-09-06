import React, { useEffect, useState } from 'react';
import { vendorApi } from '../../services/api_vendor';
import { useAuthStore } from '../../stores/authStore';

interface DashboardData {
  total_productos?: number;
  total_ventas?: number;
  ingresos_mes?: number;
  pedidos_pendientes?: number;
}

const VendorDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!isAuthenticated) {
        setError('Usuario no autenticado');
        setLoading(false);
        return;
      }

      try {
        const response = await vendorApi.auth.dashboard();
        setDashboardData(response.data);
      } catch (error: any) {
        setError(error.response?.data?.message || 'Error cargando dashboard');
        console.error('Dashboard error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [isAuthenticated]);

  if (loading) {
    return <div>Cargando dashboard...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="vendor-dashboard">
      <h1>Dashboard Vendedor</h1>
      {user && <p>Bienvenido, {user.name || user.email}</p>}
      
      {dashboardData && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Productos</h3>
            <p>{dashboardData.total_productos || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Ventas Totales</h3>
            <p>${dashboardData.total_ventas || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Ingresos del Mes</h3>
            <p>${dashboardData.ingresos_mes || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Pedidos Pendientes</h3>
            <p>{dashboardData.pedidos_pendientes || 0}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorDashboard;