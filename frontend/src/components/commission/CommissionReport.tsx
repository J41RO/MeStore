// ~/frontend/src/components/commission/CommissionReport.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Commission Report Component (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Commission Report con analytics y gráficos
 * 
 * Componente que muestra:
 * - Gráficos de tendencias de comisiones
 * - Reportes filtrados por fechas y estados
 * - Exportación de datos en formatos múltiples
 * - Analytics detallados para toma de decisiones
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, 
  Download, 
  Filter, 
  Calendar,
  TrendingUp,
  TrendingDown,
  Minus,
  FileText,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import CommissionService, { 
  Commission, 
  CommissionListFilters, 
  VendorEarningsReport 
} from '../../services/commissionService';

interface CommissionReportProps {
  vendorId?: string;
  showFilters?: boolean;
  defaultDateRange?: { start: string; end: string };
  onExport?: (data: Commission[], format: 'csv' | 'excel' | 'pdf') => void;
  className?: string;
}

interface DateRange {
  start: string;
  end: string;
  label: string;
}

export const CommissionReport: React.FC<CommissionReportProps> = ({
  vendorId,
  showFilters = true,
  defaultDateRange,
  onExport,
  className = ''
}) => {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [earnings, setEarnings] = useState<VendorEarningsReport | null>(null);
  const [filters, setFilters] = useState<CommissionListFilters>({
    vendor_id: vendorId,
    page_size: 100,
    sort_by: 'calculated_at',
    sort_order: 'desc'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [showFiltersPanel, setShowFiltersPanel] = useState(false);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>(() => {
    if (defaultDateRange) {
      return { ...defaultDateRange, label: 'Personalizado' };
    }
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 1);
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
      label: 'Último mes'
    };
  });

  // =============================================================================
  // PREDEFINED DATE RANGES
  // =============================================================================

  const dateRanges: DateRange[] = [
    {
      start: new Date(new Date().setDate(new Date().getDate() - 7)).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'Últimos 7 días'
    },
    {
      start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'Último mes'
    },
    {
      start: new Date(new Date().setMonth(new Date().getMonth() - 3)).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'Últimos 3 meses'
    },
    {
      start: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'Este año'
    }
  ];

  // =============================================================================
  // DATA LOADING
  // =============================================================================

  const loadReportData = async () => {
    try {
      setIsLoading(true);

      const updatedFilters = {
        ...filters,
        date_from: selectedDateRange.start,
        date_to: selectedDateRange.end
      };

      // Load commissions
      const commissionsData = await CommissionService.getCommissions(updatedFilters);
      setCommissions(commissionsData.commissions);

      // Load earnings summary
      if (vendorId || !filters.vendor_id) {
        const earningsData = await CommissionService.getVendorEarnings(
          vendorId || filters.vendor_id,
          selectedDateRange.start,
          selectedDateRange.end,
          'custom'
        );
        setEarnings(earningsData);
      }

    } catch (error) {
      console.error('Error loading report data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReportData();
  }, [filters, selectedDateRange]);

  // =============================================================================
  // COMPUTED ANALYTICS
  // =============================================================================

  const analytics = useMemo(() => {
    if (!commissions.length) {
      return {
        totalCommissions: 0,
        totalEarnings: 0,
        avgCommissionRate: 0,
        topCommissionMonth: '',
        growthRate: 0,
        statusBreakdown: {}
      };
    }

    const totalEarnings = commissions.reduce((sum, c) => sum + c.vendor_amount, 0);
    const totalCommissions = commissions.length;
    const avgCommissionRate = commissions.reduce((sum, c) => sum + c.commission_rate, 0) / totalCommissions;

    // Group by month for growth calculation
    const monthlyData: { [key: string]: { earnings: number; count: number } } = {};
    commissions.forEach(commission => {
      const month = new Date(commission.calculated_at).toISOString().substr(0, 7);
      if (!monthlyData[month]) monthlyData[month] = { earnings: 0, count: 0 };
      monthlyData[month].earnings += commission.vendor_amount;
      monthlyData[month].count += 1;
    });

    const months = Object.keys(monthlyData).sort();
    const topCommissionMonth = months.reduce((top, month) => 
      monthlyData[month].earnings > (monthlyData[top]?.earnings || 0) ? month : top, 
      months[0] || ''
    );

    // Calculate growth rate (last month vs previous)
    let growthRate = 0;
    if (months.length >= 2) {
      const lastMonth = monthlyData[months[months.length - 1]].earnings;
      const prevMonth = monthlyData[months[months.length - 2]].earnings;
      growthRate = prevMonth > 0 ? ((lastMonth - prevMonth) / prevMonth) * 100 : 0;
    }

    // Status breakdown
    const statusBreakdown = commissions.reduce((acc, c) => {
      acc[c.status] = (acc[c.status] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    return {
      totalCommissions,
      totalEarnings,
      avgCommissionRate,
      topCommissionMonth,
      growthRate,
      statusBreakdown
    };
  }, [commissions]);

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleDateRangeChange = (range: DateRange) => {
    setSelectedDateRange(range);
  };

  const handleFilterChange = (key: keyof CommissionListFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    if (onExport) {
      onExport(commissions, format);
    } else {
      // Default export logic
      const csvContent = [
        'Número,Fecha,Estado,Monto Orden,Comisión,Ganancias,Tasa',
        ...commissions.map(c => [
          c.commission_number,
          new Date(c.calculated_at).toLocaleDateString(),
          CommissionService.getStatusLabel(c.status),
          c.order_amount,
          c.commission_amount,
          c.vendor_amount,
          CommissionService.formatCommissionRate(c.commission_rate)
        ].join(','))
      ].join('\\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `comisiones-${selectedDateRange.start}-${selectedDateRange.end}.csv`;
      link.click();
    }
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderMetricCard = (
    title: string, 
    value: string | number, 
    trend?: number, 
    icon: React.ReactNode
  ) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-xl font-bold text-gray-900 mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {trend !== undefined && (
            <div className={`flex items-center mt-1 text-xs ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? <ArrowUp className="w-3 h-3 mr-1" /> : 
               trend < 0 ? <ArrowDown className="w-3 h-3 mr-1" /> :
               <Minus className="w-3 h-3 mr-1" />}
              {Math.abs(trend).toFixed(1)}%
            </div>
          )}
        </div>
        <div className="text-gray-400">
          {icon}
        </div>
      </div>
    </div>
  );

  const renderFiltersPanel = () => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Período</label>
          <select 
            value={selectedDateRange.label}
            onChange={(e) => {
              const selected = dateRanges.find(r => r.label === e.target.value);
              if (selected) handleDateRangeChange(selected);
            }}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            {dateRanges.map(range => (
              <option key={range.label} value={range.label}>{range.label}</option>
            ))}
            <option value="Personalizado">Personalizado</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Estado</label>
          <select
            value={filters.status?.join(',') || ''}
            onChange={(e) => handleFilterChange('status', e.target.value ? e.target.value.split(',') : undefined)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Todos los estados</option>
            <option value="PENDING">Pendientes</option>
            <option value="APPROVED">Aprobadas</option>
            <option value="PAID">Pagadas</option>
            <option value="DISPUTED">En Disputa</option>
          </select>
        </div>

        {/* Amount Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Monto Mínimo</label>
          <input
            type="number"
            value={filters.min_amount || ''}
            onChange={(e) => handleFilterChange('min_amount', e.target.value ? Number(e.target.value) : undefined)}
            placeholder="0"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* Custom date range */}
      {selectedDateRange.label === 'Personalizado' && (
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Fecha inicial</label>
            <input
              type="date"
              value={selectedDateRange.start}
              onChange={(e) => setSelectedDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Fecha final</label>
            <input
              type="date"
              value={selectedDateRange.end}
              onChange={(e) => setSelectedDateRange(prev => ({ ...prev, end: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>
      )}
    </div>
  );

  // =============================================================================
  // LOADING STATE
  // =============================================================================

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
          ))}
        </div>
        <div className="bg-gray-200 h-64 rounded-lg"></div>
      </div>
    );
  }

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Reporte de Comisiones</h2>
          <p className="text-gray-600 mt-1">
            {selectedDateRange.start} - {selectedDateRange.end}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {showFilters && (
            <button
              onClick={() => setShowFiltersPanel(!showFiltersPanel)}
              className={`flex items-center px-4 py-2 border rounded-lg text-sm transition-colors ${
                showFiltersPanel 
                  ? 'bg-blue-50 border-blue-300 text-blue-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filtros
            </button>
          )}
          
          <div className="relative">
            <button
              onClick={() => handleExport('csv')}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar CSV
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFiltersPanel && renderFiltersPanel()}

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {renderMetricCard(
          'Total Comisiones',
          analytics.totalCommissions,
          undefined,
          <FileText className="w-6 h-6" />
        )}
        
        {renderMetricCard(
          'Ganancias Totales',
          CommissionService.formatCurrency(analytics.totalEarnings),
          analytics.growthRate,
          <TrendingUp className="w-6 h-6" />
        )}
        
        {renderMetricCard(
          'Tasa Promedio',
          CommissionService.formatCommissionRate(analytics.avgCommissionRate),
          undefined,
          <BarChart3 className="w-6 h-6" />
        )}
        
        {renderMetricCard(
          'Mejor Mes',
          analytics.topCommissionMonth ? new Date(analytics.topCommissionMonth + '-01').toLocaleDateString('es-ES', { year: 'numeric', month: 'long' }) : 'N/A',
          undefined,
          <Calendar className="w-6 h-6" />
        )}
      </div>

      {/* Commissions Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Detalle de Comisiones ({commissions.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Comisión
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Orden
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Comisión
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ganancias
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasa
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {commissions.map((commission) => (
                <tr key={commission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {commission.commission_number}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(commission.calculated_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      commission.status === 'PAID' ? 'bg-green-100 text-green-800' :
                      commission.status === 'APPROVED' ? 'bg-blue-100 text-blue-800' :
                      commission.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {CommissionService.getStatusLabel(commission.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {CommissionService.formatCurrency(commission.order_amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {CommissionService.formatCurrency(commission.commission_amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                    {CommissionService.formatCurrency(commission.vendor_amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {CommissionService.formatCommissionRate(commission.commission_rate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {commissions.length === 0 && (
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No hay comisiones en el período seleccionado</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommissionReport;