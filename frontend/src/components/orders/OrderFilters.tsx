// ~/frontend/src/components/orders/OrderFilters.tsx
// PRODUCTION_READY: Filtros avanzados para órdenes enterprise

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Calendar, 
  Filter, 
  X, 
  RotateCcw,
  Users
} from 'lucide-react';
import { 
  OrderFilters as OrderFiltersType, 
  OrderStatus, 
  ORDER_STATUS_LABELS 
} from '../../types/orders';

interface OrderFiltersProps {
  filters: OrderFiltersType;
  onFiltersChange: (filters: Partial<OrderFiltersType>) => void;
  onClose: () => void;
  showBuyerFilter?: boolean;
}

export const OrderFilters: React.FC<OrderFiltersProps> = ({
  filters,
  onFiltersChange,
  onClose,
  showBuyerFilter = true
}) => {
  // Local state for form inputs
  const [localFilters, setLocalFilters] = useState<OrderFiltersType>(filters);
  const [hasChanges, setHasChanges] = useState(false);

  // Sync with external filters
  useEffect(() => {
    setLocalFilters(filters);
    setHasChanges(false);
  }, [filters]);

  // Handle input changes
  const handleInputChange = (key: keyof OrderFiltersType, value: any) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setHasChanges(true);
  };

  // Apply filters
  const handleApply = () => {
    onFiltersChange({
      ...localFilters,
      page: 1 // Reset to first page
    });
    setHasChanges(false);
  };

  // Reset filters
  const handleReset = () => {
    const resetFilters: OrderFiltersType = {
      status: 'all',
      search: '',
      date_from: '',
      date_to: '',
      buyer_id: '',
      page: 1,
      limit: 20
    };
    
    setLocalFilters(resetFilters);
    onFiltersChange(resetFilters);
    setHasChanges(false);
  };

  // Quick date ranges
  const getDateRange = (range: 'today' | 'week' | 'month' | 'quarter') => {
    const today = new Date();
    const startDate = new Date();
    
    switch (range) {
      case 'today':
        startDate.setHours(0, 0, 0, 0);
        break;
      case 'week':
        startDate.setDate(today.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(today.getMonth() - 1);
        break;
      case 'quarter':
        startDate.setMonth(today.getMonth() - 3);
        break;
    }
    
    return {
      from: startDate.toISOString().split('T')[0],
      to: today.toISOString().split('T')[0]
    };
  };

  const handleQuickDateRange = (range: 'today' | 'week' | 'month' | 'quarter') => {
    const dateRange = getDateRange(range);
    handleInputChange('date_from', dateRange.from);
    handleInputChange('date_to', dateRange.to);
  };

  return (
    <div className="bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center">
          <Filter className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">
            Filtros de Búsqueda
          </h3>
        </div>
        
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <span className="text-sm text-blue-600 font-medium">
              Cambios sin aplicar
            </span>
          )}
          
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Filters Content */}
      <div className="p-4 space-y-6">
        {/* Search */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
            Búsqueda
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              id="search"
              placeholder="Número de orden, cliente, tracking..."
              value={localFilters.search || ''}
              onChange={(e) => handleInputChange('search', e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Estado
          </label>
          <select
            id="status"
            value={localFilters.status || 'all'}
            onChange={(e) => handleInputChange('status', e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Todos los estados</option>
            {Object.entries(ORDER_STATUS_LABELS).map(([status, label]) => (
              <option key={status} value={status}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rango de Fechas
          </label>
          
          {/* Quick date buttons */}
          <div className="mb-3 flex flex-wrap gap-2">
            {[
              { key: 'today', label: 'Hoy' },
              { key: 'week', label: 'Última semana' },
              { key: 'month', label: 'Último mes' },
              { key: 'quarter', label: 'Últimos 3 meses' }
            ].map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => handleQuickDateRange(key as any)}
                className="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
              >
                {label}
              </button>
            ))}
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="date_from" className="block text-xs font-medium text-gray-500 mb-1">
                Desde
              </label>
              <div className="relative">
                <input
                  type="date"
                  id="date_from"
                  value={localFilters.date_from || ''}
                  onChange={(e) => handleInputChange('date_from', e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <Calendar className="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
            
            <div>
              <label htmlFor="date_to" className="block text-xs font-medium text-gray-500 mb-1">
                Hasta
              </label>
              <div className="relative">
                <input
                  type="date"
                  id="date_to"
                  value={localFilters.date_to || ''}
                  onChange={(e) => handleInputChange('date_to', e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <Calendar className="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        {/* Buyer Filter (for admin/vendor) */}
        {showBuyerFilter && (
          <div>
            <label htmlFor="buyer_id" className="block text-sm font-medium text-gray-700 mb-2">
              Cliente
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Users className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                id="buyer_id"
                placeholder="ID del cliente o email..."
                value={localFilters.buyer_id || ''}
                onChange={(e) => handleInputChange('buyer_id', e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}

        {/* Results per page */}
        <div>
          <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
            Resultados por página
          </label>
          <select
            id="limit"
            value={localFilters.limit || 20}
            onChange={(e) => handleInputChange('limit', parseInt(e.target.value))}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={10}>10 órdenes</option>
            <option value={20}>20 órdenes</option>
            <option value={50}>50 órdenes</option>
            <option value={100}>100 órdenes</option>
          </select>
        </div>
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
        <button
          type="button"
          onClick={handleReset}
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Limpiar
        </button>
        
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancelar
          </button>
          
          <button
            type="button"
            onClick={handleApply}
            disabled={!hasChanges}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Aplicar Filtros
          </button>
        </div>
      </div>

      {/* Filter Summary */}
      {(localFilters.status !== 'all' || 
        localFilters.search || 
        localFilters.date_from || 
        localFilters.date_to || 
        localFilters.buyer_id) && (
        <div className="px-4 py-2 bg-blue-50 border-t border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm">
              <Filter className="h-4 w-4 text-blue-600" />
              <span className="text-blue-800 font-medium">Filtros activos:</span>
              
              <div className="flex flex-wrap gap-1">
                {localFilters.status !== 'all' && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    {ORDER_STATUS_LABELS[localFilters.status as OrderStatus]}
                  </span>
                )}
                
                {localFilters.search && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    "{localFilters.search}"
                  </span>
                )}
                
                {(localFilters.date_from || localFilters.date_to) && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    {localFilters.date_from} - {localFilters.date_to}
                  </span>
                )}
                
                {localFilters.buyer_id && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    Cliente: {localFilters.buyer_id}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderFilters;