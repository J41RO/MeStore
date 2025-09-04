// Tipos centralizados para funcionalidad de exportación

// Enum para tipos de reporte disponibles
export enum TipoReporte {
  RESUMEN = 'resumen',
  VENTAS = 'ventas',
  PRODUCTOS_TOP = 'productos_top',
  COMISIONES = 'comisiones',
  INVENTARIO = 'inventario',
  COMPLETO = 'completo',
}

// Enum para formatos de exportación
export enum FormatoExport {
  PDF = 'pdf',
  EXCEL = 'excel',
}

// Interface para request de exportación
export interface ExportRequest {
  tipo_reporte: TipoReporte | string;
  formato: FormatoExport | string;
  fecha_inicio?: string;
  fecha_fin?: string;
  vendedor_id?: number;
}

// Interface para response de exportación
export interface ExportResponse {
  success: boolean;
  message: string;
  file_url?: string;
  filename?: string;
  file_size?: number;
  export_timestamp?: string;
}

// Interface para configuración de exportación
export interface ExportConfig {
  defaultTipoReporte?: TipoReporte;
  allowedFormatos?: FormatoExport[];
  maxFileSize?: number;
  timeout?: number;
}

// Interface para metadata de archivo exportado
export interface ExportedFileMetadata {
  filename: string;
  size: number;
  format: FormatoExport;
  created_at: Date;
  download_url: string;
}

// Tipos para el estado de exportación
export type ExportStatus = 'idle' | 'loading' | 'success' | 'error';

// Interface para manejo de estado en componentes
export interface ExportState {
  status: ExportStatus;
  progress?: number;
  error?: string;
  result?: ExportResponse;
}

// Labels para UI
export const TIPO_REPORTE_LABELS: Record<TipoReporte, string> = {
  [TipoReporte.RESUMEN]: 'Resumen General',
  [TipoReporte.VENTAS]: 'Reporte de Ventas',
  [TipoReporte.PRODUCTOS_TOP]: 'Productos Top',
  [TipoReporte.COMISIONES]: 'Comisiones',
  [TipoReporte.INVENTARIO]: 'Inventario',
  [TipoReporte.COMPLETO]: 'Reporte Completo',
};

export const FORMATO_LABELS: Record<FormatoExport, string> = {
  [FormatoExport.PDF]: 'PDF',
  [FormatoExport.EXCEL]: 'Excel',
};

// Utility types
export type ExportRequestPayload = Omit<ExportRequest, 'vendedor_id'> & {
  vendedor_id?: number;
};

export type ExportModalProps = {
  trigger?: React.ReactNode;
  defaultTipoReporte?: TipoReporte | string;
  vendedorId?: number;
  onExportSuccess?: (result: ExportResponse) => void;
  onExportError?: (error: string) => void;
};

// Validadores
export const isValidTipoReporte = (tipo: string): tipo is TipoReporte => {
  return Object.values(TipoReporte).includes(tipo as TipoReporte);
};

export const isValidFormato = (formato: string): formato is FormatoExport => {
  return Object.values(FormatoExport).includes(formato as FormatoExport);
};

// Configuración por defecto
export const DEFAULT_EXPORT_CONFIG: ExportConfig = {
  defaultTipoReporte: TipoReporte.COMISIONES,
  allowedFormatos: [FormatoExport.PDF, FormatoExport.EXCEL],
  maxFileSize: 50 * 1024 * 1024, // 50MB
  timeout: 30000, // 30 segundos
};
