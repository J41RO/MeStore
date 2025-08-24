// BarcodeScanner Types
// Enums para modos y estados del scanner
export enum ScanMode {
  MANUAL = 'manual',
  AUTO_SIMULATION = 'auto_simulation',
  BATCH = 'batch',
  LOCATION_BASED = 'location_based'
}

export enum ScanStatus {
  IDLE = 'idle',
  SCANNING = 'scanning',
  SUCCESS = 'success',
  ERROR = 'error',
  VALIDATING = 'validating'
}

export enum PickingOperation {
  ADD_ITEM = 'add_item',
  REMOVE_ITEM = 'remove_item',
  VERIFY_ITEM = 'verify_item',
  COMPLETE_BATCH = 'complete_batch'
}

// Interface para item escaneado
export interface ScannedItem {
  id: string;
  sku: string;
  name: string;
  barcode?: string;
  quantity: number;
  location?: string;
  timestamp: Date;
  status: ScanStatus;
  errors?: string[];
}

// Props del componente BarcodeScanner
export interface BarcodeScannerProps {
  mode?: ScanMode;
  onScan: (item: ScannedItem) => void;
  onError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

// Interface para sesión de picking
export interface PickingSession {
  id: string;
  startTime: Date;
  endTime?: Date;
  items: ScannedItem[];
  totalItems: number;
  completedItems: number;
  mode: ScanMode;
  status: 'active' | 'completed' | 'cancelled';
  location?: string;
  operator?: string;
}

// Resultado de validación de escaneo
export interface ScanValidationResult {
  isValid: boolean;
  item?: ScannedItem;
  errors: string[];
  suggestions?: string[];
}

// Configuración del scanner
export interface ScannerConfig {
  simulationDelay: number;
  autoSubmit: boolean;
  soundEnabled: boolean;
  vibrationEnabled: boolean;
  strictValidation: boolean;
}