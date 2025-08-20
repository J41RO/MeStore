// Tipos e interfaces para el sistema de control de inventario

export enum InventoryStatus {
  IN_STOCK = 'in_stock',
  LOW_STOCK = 'low_stock',
  OUT_OF_STOCK = 'out_of_stock',
  RESERVED = 'reserved'
}

export enum LocationZone {
  WAREHOUSE_A = 'warehouse_a',
  WAREHOUSE_B = 'warehouse_b',
  DISPLAY_AREA = 'display_area',
  STORAGE_ROOM = 'storage_room'
}

export interface LocationInfo {
  zone: LocationZone;
  aisle: string;
  shelf: string;
  position: string;
}

export interface InventoryItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  quantity: number;
  minStock: number;
  maxStock: number;
  status: InventoryStatus;
  location: LocationInfo;
  lastUpdated: Date;
  cost: number;
}

export interface InventoryFilters {
  status?: InventoryStatus[];
  location?: LocationZone[];
  searchTerm?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
}