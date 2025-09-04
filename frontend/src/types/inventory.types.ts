// Tipos e interfaces para el sistema de control de inventario

export enum InventoryStatus {
  IN_STOCK = 'in_stock',
  LOW_STOCK = 'low_stock',
  OUT_OF_STOCK = 'out_of_stock',
  RESERVED = 'reserved',
}

export enum LocationZone {
  WAREHOUSE_A = 'warehouse_a',
  WAREHOUSE_B = 'warehouse_b',
  DISPLAY_AREA = 'display_area',
  STORAGE_ROOM = 'storage_room',
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

// Tipos para movimientos de stock
export enum MovementType {
  ENTRADA = 'entrada',
  SALIDA = 'salida',
  AJUSTE = 'ajuste',
  TRANSFERENCIA = 'transferencia',
}

export enum MovementReason {
  COMPRA = 'compra',
  VENTA = 'venta',
  DEVOLUCION = 'devolucion',
  MERMA = 'merma',
  AJUSTE_INVENTARIO = 'ajuste_inventario',
  TRANSFERENCIA_ALMACEN = 'transferencia_almacen',
}

export interface StockMovement {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  type: MovementType;
  reason: MovementReason;
  quantity: number;
  previousStock: number;
  newStock: number;
  location: LocationInfo;
  userId: string;
  userName: string;
  notes?: string;
  timestamp: Date;
  cost?: number;
  reference?: string; // Número de orden, factura, etc.
}

export interface StockMovementFilters {
  type?: MovementType[];
  reason?: MovementReason[];
  productId?: string;
  location?: LocationZone[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchTerm?: string;
}
