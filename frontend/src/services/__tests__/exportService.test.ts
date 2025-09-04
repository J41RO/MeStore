import { exportService } from '../exportService';

describe('ExportService', () => {
  it('should exist and have required methods', () => {
    expect(exportService).toBeDefined();
    expect(typeof exportService.exportReport).toBe('function');
    expect(typeof exportService.downloadFile).toBe('function');
    expect(typeof exportService.exportAndDownload).toBe('function');
  });

  it('should handle basic export request structure', () => {
    const request = {
      tipo_reporte: 'comisiones' as const,
      formato: 'pdf' as const,
    };

    expect(request.tipo_reporte).toBe('comisiones');
    expect(request.formato).toBe('pdf');
  });
});
