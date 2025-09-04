import React, { useState, useMemo } from 'react';
import {
  InventoryItem,
  InventoryStatus,
  LocationZone,
} from '../../../types/inventory.types';
import type { InventoryFilters } from '../../../types/inventory.types';
import InventoryTable from './InventoryTable';

interface InventoryFiltersProps {
  onFilterChange: (filters: InventoryFilters) => void;
  currentFilters: InventoryFilters;
}

const InventoryFilters: React.FC<InventoryFiltersProps> = ({
  onFilterChange,
  currentFilters,
}) => {
  return (
    <div className='mb-4 p-4 bg-gray-50 rounded-lg'>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Estado
          </label>
          <select
            className='w-full border border-gray-300 rounded-md px-3 py-2'
            onChange={e =>
              onFilterChange({
                ...currentFilters,
                status: e.target.value
                  ? [e.target.value as InventoryStatus]
                  : undefined,
              })
            }
          >
            <option value=''>Todos los estados</option>
            <option value={InventoryStatus.IN_STOCK}>En Stock</option>
            <option value={InventoryStatus.LOW_STOCK}>Stock Bajo</option>
            <option value={InventoryStatus.OUT_OF_STOCK}>Sin Stock</option>
          </select>
        </div>
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Ubicación
          </label>
          <select
            className='w-full border border-gray-300 rounded-md px-3 py-2'
            onChange={e =>
              onFilterChange({
                ...currentFilters,
                location: e.target.value
                  ? [e.target.value as LocationZone]
                  : undefined,
              })
            }
          >
            <option value=''>Todas las ubicaciones</option>
            <option value={LocationZone.WAREHOUSE_A}>Almacén A</option>
            <option value={LocationZone.WAREHOUSE_B}>Almacén B</option>
            <option value={LocationZone.DISPLAY_AREA}>
              Área de Exhibición
            </option>
            <option value={LocationZone.STORAGE_ROOM}>
              Sala de Almacenamiento
            </option>
          </select>
        </div>
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Buscar
          </label>
          <input
            type='text'
            placeholder='Buscar por nombre o SKU'
            className='w-full border border-gray-300 rounded-md px-3 py-2'
            onChange={e =>
              onFilterChange({
                ...currentFilters,
                searchTerm: e.target.value || undefined,
              })
            }
          />
        </div>
      </div>
    </div>
  );
};

interface InventoryTableWithFiltersProps {
  data?: InventoryItem[];
}

export const InventoryTableWithFilters: React.FC<
  InventoryTableWithFiltersProps
> = ({ data }) => {
  const [filters, setFilters] = useState<InventoryFilters>({});

  const filteredData = useMemo(() => {
    return (data || []).filter(item => {
      // Filtro por estado
      if (filters.status && filters.status.length > 0) {
        if (!filters.status.includes(item.status)) {
          return false;
        }
      }

      // Filtro por ubicación
      if (filters.location && filters.location.length > 0) {
        if (!filters.location.includes(item.location.zone)) {
          return false;
        }
      }

      // Filtro por búsqueda de texto
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase();
        if (
          item.productName.toLowerCase().indexOf(searchLower) === -1 &&
          item.sku.toLowerCase().indexOf(searchLower) === -1
        )
          return false;
      }

      return true;
    });
  }, [data, filters]);

  return (
    <div className='w-full'>
      <InventoryFilters currentFilters={filters} onFilterChange={setFilters} />
      <InventoryTable data={filteredData} />
    </div>
  );
};

export default InventoryTableWithFilters;
