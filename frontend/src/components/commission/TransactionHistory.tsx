// ~/frontend/src/components/commission/TransactionHistory.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Transaction History Component (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Transaction History para trazabilidad de pagos
 * 
 * Componente que muestra:
 * - Historial detallado de transacciones de comisiones
 * - Filtros por estado, fecha y monto
 * - Trazabilidad completa de pagos
 * - Integración con gateway de pagos
 */

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Search,
  Filter,
  Download,
  ExternalLink,
  RefreshCw,
  Calendar,
  DollarSign
} from 'lucide-react';
import CommissionService, { TransactionHistoryItem } from '../../services/commissionService';

interface TransactionHistoryProps {
  commissionId?: string;
  vendorId?: string;
  showFilters?: boolean;
  maxItems?: number;
  className?: string;
  onTransactionClick?: (transaction: TransactionHistoryItem) => void;
}

interface TransactionFilters {
  status?: string;
  transaction_type?: string;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
}

export const TransactionHistory: React.FC<TransactionHistoryProps> = ({
  commissionId,
  vendorId,
  showFilters = true,
  maxItems = 50,
  className = '',
  onTransactionClick
}) => {
  const [transactions, setTransactions] = useState<TransactionHistoryItem[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<TransactionHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [showFiltersPanel, setShowFiltersPanel] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  // =============================================================================
  // DATA LOADING
  // =============================================================================

  const loadTransactions = async () => {
    try {
      setIsLoading(true);
      setError('');

      const data = await CommissionService.getTransactionHistory(
        commissionId,
        maxItems,
        0
      );

      setTransactions(data);
      setFilteredTransactions(data);

    } catch (err: any) {
      console.error('Error loading transaction history:', err);
      setError(err.message || 'Error al cargar historial de transacciones');
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadTransactions();
  };

  useEffect(() => {
    loadTransactions();
  }, [commissionId, maxItems]);

  // =============================================================================
  // FILTERING LOGIC
  // =============================================================================

  useEffect(() => {
    let filtered = [...transactions];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(t => 
        t.transaction_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.commission.commission_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.gateway_reference?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (filters.status) {
      filtered = filtered.filter(t => t.status === filters.status);
    }

    // Apply transaction type filter
    if (filters.transaction_type) {
      filtered = filtered.filter(t => t.transaction_type === filters.transaction_type);
    }

    // Apply date range filter
    if (filters.date_from) {
      filtered = filtered.filter(t => new Date(t.processed_at) >= new Date(filters.date_from!));
    }
    if (filters.date_to) {
      filtered = filtered.filter(t => new Date(t.processed_at) <= new Date(filters.date_to!));
    }

    // Apply amount range filters
    if (filters.min_amount) {
      filtered = filtered.filter(t => t.amount >= filters.min_amount!);
    }
    if (filters.max_amount) {
      filtered = filtered.filter(t => t.amount <= filters.max_amount!);
    }

    setFilteredTransactions(filtered);
  }, [transactions, searchTerm, filters]);

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleFilterChange = (key: keyof TransactionFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleClearFilters = () => {
    setFilters({});
    setSearchTerm('');
  };

  const handleExportCSV = () => {
    const csvContent = [
      'Número Transacción,Fecha,Estado,Tipo,Monto,Comisión,Referencia Gateway',
      ...filteredTransactions.map(t => [
        t.transaction_number,
        new Date(t.processed_at).toLocaleDateString(),
        t.status,
        t.transaction_type,
        t.amount,
        t.commission.commission_number,
        t.gateway_reference || 'N/A'
      ].join(','))
    ].join('\\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `transacciones-${Date.now()}.csv`;
    link.click();
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'paid':
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'failed':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'paid':
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTransactionTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'COMMISSION_PAYMENT': 'Pago de Comisión',
      'COMMISSION_REFUND': 'Reembolso de Comisión',
      'COMMISSION_ADJUSTMENT': 'Ajuste de Comisión',
      'PLATFORM_FEE': 'Tarifa de Plataforma',
      'VENDOR_PAYOUT': 'Pago a Vendedor'
    };
    return labels[type] || type;
  };

  const renderFiltersPanel = () => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Estado</label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Todos los estados</option>
            <option value="completed">Completadas</option>
            <option value="pending">Pendientes</option>
            <option value="failed">Fallidas</option>
          </select>
        </div>

        {/* Transaction Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
          <select
            value={filters.transaction_type || ''}
            onChange={(e) => handleFilterChange('transaction_type', e.target.value || undefined)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Todos los tipos</option>
            <option value="COMMISSION_PAYMENT">Pago de Comisión</option>
            <option value="COMMISSION_REFUND">Reembolso</option>
            <option value="COMMISSION_ADJUSTMENT">Ajuste</option>
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

      {/* Date Range */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Fecha inicial</label>
          <input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => handleFilterChange('date_from', e.target.value || undefined)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Fecha final</label>
          <input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => handleFilterChange('date_to', e.target.value || undefined)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* Clear Filters */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleClearFilters}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
  );

  // =============================================================================
  // LOADING & ERROR STATES
  // =============================================================================

  if (isLoading && !transactions.length) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="bg-gray-200 h-16 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center text-red-600 mb-2">
          <AlertCircle className="w-5 h-5 mr-2" />
          <span className="font-medium">Error al cargar transacciones</span>
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

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Historial de Transacciones</h3>
          <p className="text-gray-600 mt-1">
            {filteredTransactions.length} de {transactions.length} transacciones
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar transacciones..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64"
            />
          </div>

          {/* Filters */}
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

          {/* Export */}
          <button
            onClick={handleExportCSV}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            CSV
          </button>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFiltersPanel && renderFiltersPanel()}

      {/* Transactions List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {filteredTransactions.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {filteredTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className={`p-6 hover:bg-gray-50 transition-colors ${
                  onTransactionClick ? 'cursor-pointer' : ''
                }`}
                onClick={() => onTransactionClick?.(transaction)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    {/* Status Icon */}
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(transaction.status)}
                    </div>

                    {/* Transaction Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-sm font-medium text-gray-900">
                          {transaction.transaction_number}
                        </h4>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeClass(transaction.status)}`}>
                          {transaction.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <div className="flex items-center space-x-4">
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {new Date(transaction.processed_at).toLocaleDateString('es-ES', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          
                          <span className="flex items-center">
                            <DollarSign className="w-4 h-4 mr-1" />
                            {CommissionService.formatCurrency(transaction.amount)}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <span>Tipo: {getTransactionTypeLabel(transaction.transaction_type)}</span>
                          <span>Comisión: {transaction.commission.commission_number}</span>
                        </div>

                        {transaction.gateway_reference && (
                          <div className="flex items-center">
                            <ExternalLink className="w-4 h-4 mr-1" />
                            <span>Referencia: {transaction.gateway_reference}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Amount */}
                  <div className="text-right">
                    <p className={`text-lg font-semibold ${
                      transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.amount >= 0 ? '+' : ''}
                      {CommissionService.formatCurrency(Math.abs(transaction.amount))}
                    </p>
                    <p className="text-sm text-gray-500">
                      Orden #{transaction.commission.order_id}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">
              {transactions.length === 0 
                ? 'No hay transacciones registradas' 
                : 'No hay transacciones que coincidan con los filtros'
              }
            </p>
            {Object.keys(filters).length > 0 || searchTerm && (
              <button
                onClick={handleClearFilters}
                className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
              >
                Limpiar filtros
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionHistory;