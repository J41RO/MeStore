import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Users, Package, ShoppingCart, DollarSign } from 'lucide-react';

interface GlobalKPIs {
  gmv_total: number;
  vendedores_activos: number;
  total_productos: number;
  total_ordenes: number;
  fecha_calculo: string;
}

interface AdminDashboardResponse {
  kpis_globales: GlobalKPIs;
  ultimo_update: string;
}

const GlobalKPIs: React.FC = () => {
  const [kpis, setKpis] = useState<GlobalKPIs | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchKPIs();
  }, []);

  const fetchKPIs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('/api/v1/admin/dashboard/kpis', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: AdminDashboardResponse = await response.json();
      setKpis(data.kpis_globales);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('es-CO').format(num);
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 bg-gray-300 rounded w-1/2"></div>
              <div className="h-6 w-6 bg-gray-300 rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-300 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-300 rounded w-full"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error al cargar KPIs: </strong>
        <span className="block sm:inline">{error}</span>
        <button
          onClick={fetchKPIs}
          className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-sm"
        >
          Reintentar
        </button>
      </div>
    );
  }

    return <div>No hay datos disponibles</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* GMV Total */}
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            GMV Total
          </CardTitle>
          <DollarSign className="h-6 w-6 text-green-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(kpis.gmv_total)}
          </div>
          <CardDescription className="text-xs text-gray-500 mt-1">
            Gross Merchandise Value
          </CardDescription>
        </CardContent>
      </Card>

      {/* Vendedores Activos */}
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            Vendedores Activos
          </CardTitle>
          <Users className="h-6 w-6 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-600">
            {formatNumber(kpis.vendedores_activos)}
          </div>
          <CardDescription className="text-xs text-gray-500 mt-1">
            Últimos 30 días
          </CardDescription>
        </CardContent>
      </Card>

      {/* Total Productos */}
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            Total Productos
          </CardTitle>
          <Package className="h-6 w-6 text-purple-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-purple-600">
            {formatNumber(kpis.total_productos)}
          </div>
          <CardDescription className="text-xs text-gray-500 mt-1">
            Productos activos
          </CardDescription>
        </CardContent>
      </Card>

      {/* Total Órdenes */}
      <Card className="hover:shadow-lg transition-shadow duration-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            Total Órdenes
          </CardTitle>
          <ShoppingCart className="h-6 w-6 text-orange-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">
            {formatNumber(kpis.total_ordenes)}
          </div>
          <CardDescription className="text-xs text-gray-500 mt-1">
            Todas las transacciones
          </CardDescription>
        </CardContent>
      </Card>
    </div>
  );
};

export default GlobalKPIs;