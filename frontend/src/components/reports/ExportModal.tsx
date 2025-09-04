import React, { useState } from 'react';
import { Loader2, Download, FileText, Table, X } from 'lucide-react';
import { exportService, ExportRequest } from '../../services/exportService';

interface ExportModalProps {
  trigger?: React.ReactNode;
  defaultTipoReporte?: string;
  vendedorId?: number;
}

const ExportModal: React.FC<ExportModalProps> = ({
  trigger,
  defaultTipoReporte = 'comisiones',
  vendedorId,
}) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ExportRequest>({
    tipo_reporte: defaultTipoReporte as ExportRequest['tipo_reporte'],
    formato: 'pdf',
    fecha_inicio: '',
    fecha_fin: '',
    vendedor_id: vendedorId,
  });

  const tiposReporte = [
    { value: 'resumen', label: 'Resumen General' },
    { value: 'ventas', label: 'Reporte de Ventas' },
    { value: 'productos_top', label: 'Productos Top' },
    { value: 'comisiones', label: 'Comisiones' },
    { value: 'inventario', label: 'Inventario' },
    { value: 'completo', label: 'Reporte Completo' },
  ];

  const showToast = (
    message: string,
    type: 'success' | 'error' = 'success'
  ) => {
    // Toast simple usando alert por ahora - puede ser mejorado después
    if (type === 'error') {
      alert(`Error: ${message}`);
    } else {
      alert(`Éxito: ${message}`);
    }
  };

  const handleInputChange = (field: keyof ExportRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleExport = async () => {
    setLoading(true);

    try {
      // Validar fechas si están presentes
      if (formData.fecha_inicio && formData.fecha_fin) {
        const fechaInicio = new Date(formData.fecha_inicio);
        const fechaFin = new Date(formData.fecha_fin);

        if (fechaInicio > fechaFin) {
          showToast(
            'La fecha de inicio no puede ser posterior a la fecha fin',
            'error'
          );
          return;
        }
      }

      const result = await exportService.exportAndDownload(formData);

      if (result.success) {
        showToast(
          `Reporte ${formData.tipo_reporte} exportado como ${formData.formato.toUpperCase()}`
        );
        setOpen(false);
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      console.error('Error durante exportación:', error);
      showToast('Ocurrió un error al exportar el reporte', 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderFormatIcon = (formato: string) => {
    return formato === 'pdf' ? (
      <FileText className='w-4 h-4 text-red-500' />
    ) : (
      <Table className='w-4 h-4 text-green-500' />
    );
  };

  if (!open) {
    return (
      <div onClick={() => setOpen(true)}>
        {trigger || (
          <button className='flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700'>
            <Download className='w-4 h-4' />
            Exportar
          </button>
        )}
      </div>
    );
  }

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto'>
        {/* Header */}
        <div className='flex items-center justify-between mb-4'>
          <h2 className='text-lg font-semibold flex items-center gap-2'>
            <Download className='w-5 h-5' />
            Exportar Reporte
          </h2>
          <button
            onClick={() => setOpen(false)}
            className='text-gray-400 hover:text-gray-600'
            disabled={loading}
          >
            <X className='w-5 h-5' />
          </button>
        </div>

        <div className='space-y-4'>
          {/* Tipo de Reporte */}
          <div className='space-y-2'>
            <label
              htmlFor='tipo_reporte'
              className='block text-sm font-medium text-gray-700'
            >
              Tipo de Reporte
            </label>
            <select
              id='tipo_reporte'
              value={formData.tipo_reporte}
              onChange={e => handleInputChange('tipo_reporte', e.target.value)}
              className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
              disabled={loading}
            >
              {tiposReporte.map(tipo => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>

          {/* Formato */}
          <div className='space-y-2'>
            <label
              htmlFor='formato'
              className='block text-sm font-medium text-gray-700'
            >
              Formato de Exportación
            </label>
            <select
              id='formato'
              value={formData.formato}
              onChange={e => handleInputChange('formato', e.target.value)}
              className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
              disabled={loading}
            >
              <option value='pdf'>📄 PDF</option>
              <option value='excel'>📊 Excel</option>
            </select>
          </div>

          {/* Rango de Fechas */}
          <div className='grid grid-cols-2 gap-4'>
            <div className='space-y-2'>
              <label
                htmlFor='fecha_inicio'
                className='block text-sm font-medium text-gray-700'
              >
                Fecha Inicio (opcional)
              </label>
              <input
                type='date'
                id='fecha_inicio'
                value={formData.fecha_inicio}
                onChange={e =>
                  handleInputChange('fecha_inicio', e.target.value)
                }
                className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                disabled={loading}
              />
            </div>
            <div className='space-y-2'>
              <label
                htmlFor='fecha_fin'
                className='block text-sm font-medium text-gray-700'
              >
                Fecha Fin (opcional)
              </label>
              <input
                type='date'
                id='fecha_fin'
                value={formData.fecha_fin}
                onChange={e => handleInputChange('fecha_fin', e.target.value)}
                className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                disabled={loading}
              />
            </div>
          </div>

          {/* Botones de Acción */}
          <div className='flex justify-end gap-2 pt-4'>
            <button
              onClick={() => setOpen(false)}
              disabled={loading}
              className='px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50'
            >
              Cancelar
            </button>
            <button
              onClick={handleExport}
              disabled={loading}
              className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 min-w-[120px] flex items-center justify-center'
            >
              {loading ? (
                <>
                  <Loader2 className='w-4 h-4 mr-2 animate-spin' />
                  Exportando...
                </>
              ) : (
                <>
                  {renderFormatIcon(formData.formato)}
                  <span className='ml-2'>
                    Exportar {formData.formato.toUpperCase()}
                  </span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;
