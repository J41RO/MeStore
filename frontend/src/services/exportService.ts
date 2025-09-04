import axios from 'axios';

// Tipos para el servicio de exportación
export interface ExportRequest {
  tipo_reporte:
    | 'resumen'
    | 'ventas'
    | 'productos_top'
    | 'comisiones'
    | 'inventario'
    | 'completo';
  formato: 'pdf' | 'excel';
  fecha_inicio?: string;
  fecha_fin?: string;
  vendedor_id?: number;
}

export interface ExportResponse {
  success: boolean;
  message: string;
  file_url?: string;
  filename?: string;
}

class ExportService {
  private baseURL = '/api/v1/vendedores';

  /**
   * Exportar reporte llamando al endpoint del backend
   */
  async exportReport(request: ExportRequest): Promise<ExportResponse> {
    try {
      const params = new URLSearchParams();
      params.append('tipo_reporte', request.tipo_reporte);
      params.append('formato', request.formato);

      if (request.fecha_inicio)
        params.append('fecha_inicio', request.fecha_inicio);
      if (request.fecha_fin) params.append('fecha_fin', request.fecha_fin);
      if (request.vendedor_id)
        params.append('vendedor_id', request.vendedor_id.toString());

      const response = await axios.get(
        `${this.baseURL}/dashboard/exportar?${params.toString()}`,
        {
          responseType: 'blob', // Importante para archivos
          timeout: 30000, // 30 segundos timeout
        }
      );

      // Crear URL temporal para descarga
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);

      // Determinar nombre del archivo
      const timestamp = new Date().toISOString().split('T')[0];
      const extension = request.formato === 'pdf' ? 'pdf' : 'xlsx';
      const filename = `reporte_${request.tipo_reporte}_${timestamp}.${extension}`;

      return {
        success: true,
        message: 'Reporte exportado exitosamente',
        file_url: downloadUrl,
        filename,
      };
    } catch (error: any) {
      console.error('Error exportando reporte:', error);

      let message = 'Error desconocido al exportar reporte';
      if (error.response) {
        message =
          error.response.data?.message ||
          `Error del servidor: ${error.response.status}`;
      } else if (error.request) {
        message = 'Error de conexión con el servidor';
      } else {
        message = error.message || 'Error al procesar la solicitud';
      }

      return {
        success: false,
        message,
      };
    }
  }

  /**
   * Descargar archivo usando file-saver
   */
  async downloadFile(fileUrl: string, filename: string): Promise<void> {
    const { saveAs } = await import('file-saver');

    try {
      const response = await fetch(fileUrl);
      const blob = await response.blob();
      saveAs(blob, filename);

      // Limpiar URL temporal
      window.URL.revokeObjectURL(fileUrl);
    } catch (error) {
      console.error('Error descargando archivo:', error);
      throw new Error('Error al descargar el archivo');
    }
  }

  /**
   * Exportar y descargar en un solo paso
   */
  async exportAndDownload(request: ExportRequest): Promise<ExportResponse> {
    const exportResult = await this.exportReport(request);

    if (
      exportResult.success &&
      exportResult.file_url &&
      exportResult.filename
    ) {
      await this.downloadFile(exportResult.file_url, exportResult.filename);
    }

    return exportResult;
  }
}

// Instancia singleton del servicio
export const exportService = new ExportService();
export default exportService;
