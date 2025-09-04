// ~/src/hooks/useInventory.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Hook para gestión de inventario con estado y filtros
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { useState, useMemo } from 'react';
import {
  InventoryItem,
  InventoryStatus,
  LocationZone,
} from '../types/inventory.types';
import type { InventoryFilters } from '../types/inventory.types';

// Datos mock para desarrollo
const mockInventoryData: InventoryItem[] = [
  {
    id: '1',
    productId: 'PROD001',
    productName: 'Laptop Dell XPS',
    sku: 'LT-DELL-001',
    quantity: 25,
    minStock: 10,
    maxStock: 50,
    status: InventoryStatus.IN_STOCK,
    location: {
      zone: LocationZone.WAREHOUSE_A,
      aisle: 'A1',
      shelf: 'S1',
      position: 'P1',
    },
    lastUpdated: new Date(),
    cost: 1200,
  },
  {
    id: '2',
    productId: 'PROD002',
    productName: 'Mouse Logitech',
    sku: 'MS-LOG-002',
    quantity: 5,
    minStock: 15,
    maxStock: 100,
    status: InventoryStatus.LOW_STOCK,
    location: {
      zone: LocationZone.DISPLAY_AREA,
      aisle: 'B2',
      shelf: 'S3',
      position: 'P2',
    },
    lastUpdated: new Date(),
    cost: 45,
  },
  {
    id: '3',
    productId: 'PROD003',
    productName: 'Teclado Mecánico',
    sku: 'KB-MEC-003',
    quantity: 0,
    minStock: 8,
    maxStock: 30,
    status: InventoryStatus.OUT_OF_STOCK,
    location: {
      zone: LocationZone.STORAGE_ROOM,
      aisle: 'C1',
      shelf: 'S2',
      position: 'P1',
    },
    lastUpdated: new Date(),
    cost: 85,
  },
];

export interface UseInventoryReturn {
  items: InventoryItem[];
  filteredItems: InventoryItem[];
  filters: InventoryFilters;
  setFilters: (filters: InventoryFilters) => void;
  totalItems: number;
  lowStockItems: number;
  outOfStockItems: number;
  isLoading: boolean;
}

export const useInventory = (): UseInventoryReturn => {
  const [filters, setFilters] = useState<InventoryFilters>({});
  const [isLoading] = useState(false); // Para futuras implementaciones async

  const filteredItems = useMemo(() => {
    return mockInventoryData.filter(item => {
      // Filtro por estado
      if (filters.status && filters.status.length > 0) {
        if (filters.status.indexOf(item.status) === -1) return false;
      }

      // Filtro por ubicación
      if (filters.location && filters.location.length > 0) {
        if (filters.location.indexOf(item.location.zone) === -1) return false;
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
  }, [filters]);

  const stats = useMemo(() => {
    const lowStock = mockInventoryData.filter(
      item => item.status === InventoryStatus.LOW_STOCK
    ).length;
    const outOfStock = mockInventoryData.filter(
      item => item.status === InventoryStatus.OUT_OF_STOCK
    ).length;

    return {
      totalItems: mockInventoryData.length,
      lowStockItems: lowStock,
      outOfStockItems: outOfStock,
    };
  }, []);

  return {
    items: mockInventoryData,
    filteredItems,
    filters,
    setFilters,
    isLoading,
    ...stats,
  };
};
