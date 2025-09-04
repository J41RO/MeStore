import React from 'react';
import {
  AlertsFilter,
  AlertType,
  AlertSeverity,
  AlertCategory,
} from '../../types/alerts.types';
import { Filter, X, Check } from 'lucide-react';

interface AlertFiltersProps {
  filters: AlertsFilter;
  onFiltersChange: (filters: AlertsFilter) => void;
  onClose: () => void;
  totalAlerts: number;
  filteredCount: number;
}

/**
 * Componente de filtros avanzados para AlertsPanel
 */
const AlertFilters: React.FC<AlertFiltersProps> = ({
  filters,
  onFiltersChange,
  onClose,
  totalAlerts,
  filteredCount,
}) => {
  const handleTypeToggle = (type: AlertType) => {
    const newTypes = filters.types.includes(type)
      ? filters.types.filter(t => t !== type)
      : [...filters.types, type];

    onFiltersChange({ ...filters, types: newTypes });
  };

  const handleSeverityToggle = (severity: AlertSeverity) => {
    const newSeverities = filters.severities.includes(severity)
      ? filters.severities.filter(s => s !== severity)
      : [...filters.severities, severity];

    onFiltersChange({ ...filters, severities: newSeverities });
  };

  const handleCategoryToggle = (category: AlertCategory) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter(c => c !== category)
      : [...filters.categories, category];

    onFiltersChange({ ...filters, categories: newCategories });
  };

  const resetFilters = () => {
    onFiltersChange({
      types: [AlertType.STOCK, AlertType.QUALITY, AlertType.VENDOR, AlertType.SYSTEM],
      severities: [
        AlertSeverity.HIGH,
        AlertSeverity.CRITICAL,
        AlertSeverity.MEDIUM,
      ],
      categories: Object.values(AlertCategory),
      showRead: false,
      showUnread: true,
    });
  };

  return (
    <div className='absolute top-12 right-0 z-50 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4'>
      {/* Header */}
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-2'>
          <Filter className='h-4 w-4 text-gray-600' />
          <h3 className='font-medium text-gray-900'>Filtros</h3>
        </div>
        <button
          onClick={onClose}
          className='p-1 text-gray-400 hover:text-gray-600 rounded'
        >
          <X className='h-4 w-4' />
        </button>
      </div>

      {/* Results Summary */}
      <div className='mb-4 p-2 bg-blue-50 rounded text-sm text-blue-700'>
        Mostrando {filteredCount} de {totalAlerts} alertas
      </div>

      {/* Tipos de Alerta */}
      <div className='mb-4'>
        <h4 className='text-sm font-medium text-gray-700 mb-2'>
          Tipo de Alerta
        </h4>
        <div className='space-y-2'>
          {Object.values(AlertType).map(type => (
            <label
              key={type}
              className='flex items-center gap-2 cursor-pointer'
            >
              <input
                type='checkbox'
                checked={filters.types.includes(type)}
                onChange={() => handleTypeToggle(type)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='text-sm text-gray-600 capitalize'>{type}</span>
              {filters.types.includes(type) && (
                <Check className='h-3 w-3 text-green-500' />
              )}
            </label>
          ))}
        </div>
      </div>

      {/* Severidad */}
      <div className='mb-4'>
        <h4 className='text-sm font-medium text-gray-700 mb-2'>Severidad</h4>
        <div className='space-y-2'>
          {Object.values(AlertSeverity).map(severity => (
            <label
              key={severity}
              className='flex items-center gap-2 cursor-pointer'
            >
              <input
                type='checkbox'
                checked={filters.severities.includes(severity)}
                onChange={() => handleSeverityToggle(severity)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='text-sm px-2 py-1 rounded-full capitalize'>
                {severity}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Categorías */}
      <div className='mb-4'>
        <h4 className='text-sm font-medium text-gray-700 mb-2'>Categoría</h4>
        <div className='space-y-2 max-h-32 overflow-y-auto'>
          {Object.values(AlertCategory).map(category => (
            <label
              key={category}
              className='flex items-center gap-2 cursor-pointer'
            >
              <input
                type='checkbox'
                checked={filters.categories.includes(category)}
                onChange={() => handleCategoryToggle(category)}
                className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
              />
              <span className='text-sm text-gray-600 capitalize'>
                {category.replace('_', ' ')}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Estado de Lectura */}
      <div className='mb-4'>
        <h4 className='text-sm font-medium text-gray-700 mb-2'>Estado</h4>
        <div className='space-y-2'>
          <label className='flex items-center gap-2 cursor-pointer'>
            <input
              type='checkbox'
              checked={filters.showUnread}
              onChange={e =>
                onFiltersChange({ ...filters, showUnread: e.target.checked })
              }
              className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            />
            <span className='text-sm text-gray-600'>No leídas</span>
          </label>
          <label className='flex items-center gap-2 cursor-pointer'>
            <input
              type='checkbox'
              checked={filters.showRead}
              onChange={e =>
                onFiltersChange({ ...filters, showRead: e.target.checked })
              }
              className='rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            />
            <span className='text-sm text-gray-600'>Leídas</span>
          </label>
        </div>
      </div>

      {/* Actions */}
      <div className='flex gap-2 pt-3 border-t border-gray-200'>
        <button
          onClick={resetFilters}
          className='flex-1 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50 transition-colors'
        >
          Restablecer
        </button>
        <button
          onClick={onClose}
          className='flex-1 px-3 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors'
        >
          Aplicar
        </button>
      </div>
    </div>
  );
};

export default AlertFilters;
