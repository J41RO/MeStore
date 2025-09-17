// ~/frontend/src/components/commission/CommissionDashboard.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Commission Dashboard Component (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Commission Dashboard para vendors y admins
 * 
 * Componente principal que muestra:
 * - Resumen de earnings del vendor
 * - Métricas de comisiones en tiempo real
 * - Gráficos de tendencias financieras
 * - Accesos rápidos a funciones clave
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Calendar,
  Download,
  Eye,
  RefreshCw
} from 'lucide-react';
import CommissionService, { VendorEarningsReport, Commission } from '../../services/commissionService';

interface CommissionDashboardProps {
  vendorId?: string;
  onViewDetails?: (commissionId: string) => void;
  onNavigateToHistory?: () => void;
  className?: string;
}

export const CommissionDashboard: React.FC<CommissionDashboardProps> = ({
  vendorId,
  onViewDetails,
  onNavigateToHistory,
  className = ''
}) => {
  const [earnings, setEarnings] = useState<VendorEarningsReport | null>(null);
  const [recentCommissions, setRecentCommissions] = useState<Commission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [selectedPeriod, setSelectedPeriod] = useState<'weekly' | 'monthly' | 'quarterly'>('monthly');
  const [refreshing, setRefreshing] = useState(false);

  // =============================================================================
  // DATA LOADING
  // =============================================================================

  const loadDashboardData = async () => {
    if (refreshing) return;
    
    try {
      setIsLoading(true);
      setError('');

      // Cargar earnings report
      const earningsData = await CommissionService.getVendorEarnings(
        vendorId, 
        undefined, 
        undefined, 
        selectedPeriod
      );
      setEarnings(earningsData);

      // Cargar comisiones recientes
      const commissionsData = await CommissionService.getCommissions({
        vendor_id: vendorId,
        page_size: 5,
        sort_by: 'calculated_at',
        sort_order: 'desc'
      });
      setRecentCommissions(commissionsData.commissions);

    } catch (err: any) {
      console.error('Error loading commission dashboard:', err);
      setError(err.message || 'Error al cargar datos de comisiones');
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
  };

  useEffect(() => {
    loadDashboardData();
  }, [vendorId, selectedPeriod]);

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderMetricCard = (
    title: string, 
    value: string, 
    change?: string, 
    icon: React.ReactNode,
    color: string = 'blue'
  ) => (
    <div className="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {change && (
            <p className="text-xs text-green-600 mt-1 flex items-center">
              <TrendingUp className="w-3 h-3 mr-1" />
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 bg-${color}-50 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );

  const renderCommissionItem = (commission: Commission) => (
    <div key={commission.id} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
      <div className="flex-1">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-900">
            {commission.commission_number}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(commission.status)}`}>
            {CommissionService.getStatusLabel(commission.status)}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Orden #{commission.order_id} • {new Date(commission.calculated_at).toLocaleDateString()}
        </p>
      </div>
      <div className="text-right">
        <p className="text-sm font-semibold text-gray-900">
          {CommissionService.formatCurrency(commission.vendor_amount)}
        </p>
        <p className="text-xs text-gray-500">
          Comisión: {CommissionService.formatCurrency(commission.commission_amount)}
        </p>
      </div>
      {onViewDetails && (
        <button
          onClick={() => onViewDetails(commission.id)}
          className="ml-3 p-1 text-gray-400 hover:text-blue-600 transition-colors"
          title="Ver detalles"
        >
          <Eye className="w-4 h-4" />
        </button>
      )}
    </div>
  );

  const getStatusBadgeClass = (status: Commission['status']) => {
    const classes = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      APPROVED: 'bg-green-100 text-green-800', 
      PAID: 'bg-emerald-100 text-emerald-800',
      DISPUTED: 'bg-red-100 text-red-800',
      REFUNDED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-gray-100 text-gray-800'
    };
    return classes[status] || classes.PENDING;
  };

  // =============================================================================
  // LOADING & ERROR STATES
  // =============================================================================

  if (isLoading && !earnings) {
    return (
      <div className={`bg-gray-50 rounded-xl p-8 ${className}`}>
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-gray-200 h-32 rounded-xl"></div>
            ))}
          </div>
          <div className="bg-gray-200 h-64 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-xl p-6 ${className}`}>
        <div className="flex items-center text-red-600 mb-2">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <span className="font-medium">Error al cargar dashboard</span>
        </div>
        <p className="text-red-600 text-sm mb-4">{error}</p>
        <button
          onClick={handleRefresh}
          className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!earnings) {
    return (
      <div className={`bg-gray-50 rounded-xl p-8 text-center ${className}`}>
        <div className="text-gray-400 mb-4">
          <DollarSign className="w-16 h-16 mx-auto" />
        </div>
        <p className="text-gray-600">No hay datos de comisiones disponibles</p>
      </div>
    );
  }

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard de Comisiones</h2>
        <div className="flex items-center space-x-3">
          {/* Period selector */}
          <select 
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as any)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value="weekly">Semanal</option>
            <option value="monthly">Mensual</option>
            <option value="quarterly">Trimestral</option>
          </select>
          
          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>
      </div>

      {/* Metrics cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {renderMetricCard(
          'Ganancias Totales',
          CommissionService.formatCurrency(earnings.summary.total_vendor_earnings),
          undefined,
          <DollarSign className="w-6 h-6 text-blue-600" />,
          'blue'
        )}
        
        {renderMetricCard(
          'Comisiones Pagadas',
          CommissionService.formatCurrency(earnings.summary.paid_earnings),
          undefined,
          <CheckCircle className="w-6 h-6 text-green-600" />,
          'green'
        )}
        
        {renderMetricCard(
          'Pendientes de Pago',
          CommissionService.formatCurrency(earnings.summary.pending_earnings),
          undefined,
          <Clock className="w-6 h-6 text-yellow-600" />,
          'yellow'
        )}
        
        {renderMetricCard(
          'Tasa Promedio',
          CommissionService.formatCommissionRate(earnings.summary.average_commission_rate),
          undefined,
          <TrendingUp className="w-6 h-6 text-purple-600" />,
          'purple'
        )}
      </div>

      {/* Recent commissions and period info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Commissions */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Comisiones Recientes</h3>
            {onNavigateToHistory && (
              <button
                onClick={onNavigateToHistory}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Ver historial completo →
              </button>
            )}
          </div>
          
          <div className="space-y-1">
            {recentCommissions.length > 0 ? (
              recentCommissions.map(renderCommissionItem)
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No hay comisiones recientes</p>
              </div>
            )}
          </div>
        </div>

        {/* Period Summary */}
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen del Período</h3>
          
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Período:</span>
              <span className="font-medium text-gray-900">
                {new Date(earnings.period.start_date).toLocaleDateString()} - {new Date(earnings.period.end_date).toLocaleDateString()}
              </span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total Comisiones:</span>
              <span className="font-medium text-gray-900">{earnings.summary.total_commissions}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Volumen Total:</span>
              <span className="font-medium text-gray-900">
                {CommissionService.formatCurrency(earnings.summary.total_order_amount)}
              </span>
            </div>

            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Por Estado</h4>
              <div className="space-y-2">
                {Object.entries(earnings.breakdown_by_status).map(([status, data]) => (
                  <div key={status} className="flex justify-between text-xs">
                    <span className="text-gray-600">{CommissionService.getStatusLabel(status as any)}:</span>
                    <span className="font-medium">{data.count} ({CommissionService.formatCurrency(data.total_amount)})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommissionDashboard;