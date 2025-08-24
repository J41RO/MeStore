import React, { useState, useEffect } from 'react';
import { StockMovementFilters, MovementType } from '../../../types/inventory.types';

interface MovementFiltersProps {
  filters: StockMovementFilters;
  onFiltersChange: (filters: StockMovementFilters) => void;
  onReset: () => void;
  loading?: boolean;
}

const MovementFilters: React.FC<MovementFiltersProps> = ({
  filters,
  onFiltersChange,
  onReset,
  loading = false
}) => {
  const [localFilters, setLocalFilters] = useState<StockMovementFilters>(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key: keyof StockMovementFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    const newDateRange = { 
      ...localFilters.dateRange,
      [field]: new Date(value)
    };
    handleFilterChange('dateRange', newDateRange);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Fecha Desde */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha Desde
          </label>
          <input
            type="date"
            value={localFilters.dateRange?.start ? new Date(localFilters.dateRange.start).toISOString().split('T')[0] : ''}
            onChange={(e) => handleDateChange('start', e.target.value)}
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Fecha Hasta */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha Hasta
          </label>
          <input
            type="date"
            value={localFilters.dateRange?.end ? new Date(localFilters.dateRange.end).toISOString().split('T')[0] : ''}
            onChange={(e) => handleDateChange('end', e.target.value)}
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Tipo Movimiento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo Movimiento
          </label>
          <select
            value={localFilters.type?.[0] || ''}
            onChange={(e) => handleFilterChange('type', e.target.value ? [e.target.value as MovementType] : [])}
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los tipos</option>
            <option value={MovementType.ENTRADA}>Entrada</option>
            <option value={MovementType.SALIDA}>Salida</option>
            <option value={MovementType.AJUSTE}>Ajuste</option>
            <option value={MovementType.TRANSFERENCIA}>Transferencia</option>
          </select>
        </div>

        {/* Botón Limpiar */}
        <div className="flex items-end">
          <button
            onClick={onReset}
            disabled={loading}
            className="w-full px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
          >
            Limpiar Filtros
          </button>
        </div>
      </div>
    </div>
  );
};

export default MovementFilters;