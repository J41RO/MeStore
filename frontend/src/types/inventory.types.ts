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

// Tipos para incidentes de inventario
export enum TipoIncidente {
  PERDIDO = 'PERDIDO',
  DAÑADO = 'DAÑADO',
}

export enum EstadoIncidente {
  REPORTADO = 'REPORTADO',
  EN_INVESTIGACION = 'EN_INVESTIGACION',
  RESUELTO = 'RESUELTO',
  CERRADO = 'CERRADO',
}

export interface Incidente {
  id: string;
  inventory_id: string;
  tipo_incidente: TipoIncidente;
  estado: EstadoIncidente;
  descripcion: string;
  reportado_por: string;
  fecha_incidente?: Date;
  created_at: Date;
  updated_at: Date;
}

export interface IncidenteCreate {
  inventory_id: string;
  tipo_incidente: TipoIncidente;
  descripcion: string;
  fecha_incidente?: Date;
}
