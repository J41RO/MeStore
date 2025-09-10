import React, { useState, useEffect } from 'react';
import { format, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';

// Interfaces para tipos de datos
interface DiscrepancyReport {
  id: string;
  audit_id: string;
  report_type: string;
  report_name: string;
  description?: string;
  generated_by_id: string;
  generated_by_name: string;
  date_range_start: string;
  date_range_end: string;
  total_discrepancies: number;
  total_adjustments: number;
  financial_impact: number;
  accuracy_percentage: number;
  items_analyzed: number;
  file_path?: string;
  file_format: string;
  file_size?: number;
  status: string;
  generation_time_seconds?: number;
  expiry_date?: string;
  download_count: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  is_completed: boolean;
  is_expired: boolean;
  file_exists: boolean;
  days_since_generation: number;
}

interface ReportStats {
  total_reports: number;
  reports_by_type: Record<string, number>;
  reports_by_status: Record<string, number>;
  avg_generation_time: number;
  total_downloads: number;
  disk_space_used: number;
  reports_this_month: number;
}

interface Audit {
  id: string;
  nombre: string;
  status: string;
  fecha_inicio: string;
  fecha_fin?: string;
  total_items_auditados: number;
  discrepancias_encontradas: number;
  valor_discrepancias: number;
}

interface ReporteDiscrepanciasProps {
  auditId?: string;
  dateRange?: {
    start_date: string;
    end_date: string;
  };
}

const ReporteDiscrepancias: React.FC<ReporteDiscrepanciasProps> = ({
  auditId
}) => {
  const [reports, setReports] = useState<DiscrepancyReport[]>([]);
  const [audits, setAudits] = useState<Audit[]>([]);
  const [reportStats, setReportStats] = useState<ReportStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'dashboard' | 'generate' | 'reports'>('dashboard');
  
  // Estado para generación de reportes
  const [selectedAuditId, setSelectedAuditId] = useState<string>(auditId || '');
  const [reportType, setReportType] = useState<string>('DISCREPANCIES');
  const [fileFormat, setFileFormat] = useState<string>('PDF');
  const [includeCharts, setIncludeCharts] = useState<boolean>(true);
  const [includeRecommendations, setIncludeRecommendations] = useState<boolean>(true);
  const [groupByLocation, setGroupByLocation] = useState<boolean>(false);
  const [groupByCategory, setGroupByCategory] = useState<boolean>(false);
  
  // Filtros para listado de reportes
  const [filters, setFilters] = useState({
    audit_id: auditId || '',
    report_type: '',
    status: '',
    start_date: format(subMonths(new Date(), 1), 'yyyy-MM-dd'),
    end_date: format(new Date(), 'yyyy-MM-dd')
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedTab === 'reports') {
      fetchReports();
    }
  }, [selectedTab, filters]);

  const fetchInitialData = async () => {
    await Promise.all([
      fetchAudits(),
      fetchReportStats()
    ]);
  };

  const fetchAudits = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/inventory/audits', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener auditorías');
      }
      
      const data = await response.json();
      setAudits(Array.isArray(data) ? data : data.audits || []);
    } catch (err) {
      console.error('Error fetching audits:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
    }
  };

  const fetchReportStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/inventory/reports/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener estadísticas');
      }
      
      const data = await response.json();
      setReportStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });
      
      const response = await fetch(`/api/v1/inventory/reports/discrepancies?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error al obtener reportes');
      }
      
      const data = await response.json();
      setReports(data.reports || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    if (!selectedAuditId) {
      setError('Debe seleccionar una auditoría');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const reportData = {
        audit_id: selectedAuditId,
        report_type: reportType,
        file_format: fileFormat,
        include_charts: includeCharts,
        include_recommendations: includeRecommendations,
        group_by_location: groupByLocation,
        group_by_category: groupByCategory
      };

      const response = await fetch(`/api/v1/inventory/audits/${selectedAuditId}/reports`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reportData)
      });

      if (!response.ok) {
        throw new Error('Error al generar reporte');
      }

      await response.json();
      
      // Actualizar estadísticas y cambiar a pestaña de reportes
      await fetchReportStats();
      setSelectedTab('reports');
      await fetchReports();
      
      // Limpiar form
      setSelectedAuditId('');
      setReportType('DISCREPANCIES');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (reportId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/inventory/reports/${reportId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al descargar reporte');
      }

      // Crear blob y descargar
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reporte_discrepancias_${reportId}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Actualizar estadísticas
      await fetchReportStats();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al descargar');
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800';
      case 'GENERATING': return 'bg-blue-100 text-blue-800';
      case 'FAILED': return 'bg-red-100 text-red-800';
      case 'EXPIRED': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getReportTypeLabel = (type: string): string => {
    const typeLabels: Record<string, string> = {
      'DISCREPANCIES': 'Discrepancias',
      'ADJUSTMENTS': 'Ajustes',
      'ACCURACY': 'Precisión',
      'FINANCIAL_IMPACT': 'Impacto Financiero',
      'LOCATION_ANALYSIS': 'Análisis por Ubicación',
      'CATEGORY_ANALYSIS': 'Análisis por Categoría',
      'TREND_ANALYSIS': 'Análisis de Tendencias',
      'COMPREHENSIVE': 'Comprensivo'
    };
    return typeLabels[type] || type;
  };

  const renderDashboardTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Métricas principales */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <div className="w-6 h-6 bg-blue-600 rounded"></div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Reportes</h3>
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats?.total_reports || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <div className="w-6 h-6 bg-green-600 rounded"></div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Descargas</h3>
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats?.total_downloads || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <div className="w-6 h-6 bg-purple-600 rounded"></div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Este Mes</h3>
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats?.reports_this_month || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <div className="w-6 h-6 bg-orange-600 rounded"></div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Tiempo Prom.</h3>
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats?.avg_generation_time ? Math.round(reportStats.avg_generation_time) + 's' : '0s'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos de estadísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reportes por tipo */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Reportes por Tipo</h3>
          <div className="space-y-3">
            {reportStats?.reports_by_type && Object.entries(reportStats.reports_by_type).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{getReportTypeLabel(type)}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ 
                        width: `${Math.min(100, (count / Math.max(...Object.values(reportStats.reports_by_type))) * 100)}%` 
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Reportes por estado */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Reportes por Estado</h3>
          <div className="space-y-3">
            {reportStats?.reports_by_status && Object.entries(reportStats.reports_by_status).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{status}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ 
                        width: `${Math.min(100, (count / Math.max(...Object.values(reportStats.reports_by_status))) * 100)}%` 
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Información de almacenamiento */}
      {reportStats && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Información de Almacenamiento</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(reportStats.disk_space_used / (1024 * 1024))} MB
              </p>
              <p className="text-sm text-gray-600">Espacio Utilizado</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats.total_reports > 0 ? Math.round(reportStats.disk_space_used / reportStats.total_reports / 1024) : 0} KB
              </p>
              <p className="text-sm text-gray-600">Tamaño Promedio</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold text-gray-900">
                {reportStats.total_downloads > 0 ? (reportStats.total_downloads / reportStats.total_reports).toFixed(1) : '0.0'}
              </p>
              <p className="text-sm text-gray-600">Descargas por Reporte</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderGenerateTab = () => (
    <div className="bg-white rounded-lg shadow border">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Generar Nuevo Reporte de Discrepancias</h3>
        <p className="mt-1 text-sm text-gray-600">
          Configure las opciones del reporte y genere un análisis detallado de discrepancias
        </p>
      </div>
      
      <div className="p-6 space-y-6">
        {/* Selección de auditoría */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Auditoría *
          </label>
          <select
            value={selectedAuditId}
            onChange={(e) => setSelectedAuditId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Seleccionar auditoría...</option>
            {audits.filter(audit => audit.status === 'COMPLETADA' || audit.status === 'RECONCILIADA').map((audit) => (
              <option key={audit.id} value={audit.id}>
                {audit.nombre} - {audit.discrepancias_encontradas} discrepancias ({format(new Date(audit.fecha_inicio), 'dd/MM/yyyy')})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tipo de reporte */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Reporte
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="DISCREPANCIES">Discrepancias</option>
              <option value="ADJUSTMENTS">Ajustes</option>
              <option value="ACCURACY">Precisión</option>
              <option value="FINANCIAL_IMPACT">Impacto Financiero</option>
              <option value="LOCATION_ANALYSIS">Análisis por Ubicación</option>
              <option value="CATEGORY_ANALYSIS">Análisis por Categoría</option>
              <option value="COMPREHENSIVE">Comprensivo</option>
            </select>
          </div>

          {/* Formato de archivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Formato de Archivo
            </label>
            <select
              value={fileFormat}
              onChange={(e) => setFileFormat(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="PDF">PDF</option>
              <option value="EXCEL">Excel</option>
              <option value="CSV">CSV</option>
              <option value="JSON">JSON</option>
            </select>
          </div>
        </div>

        {/* Opciones avanzadas */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Opciones del Reporte</h4>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeCharts}
                onChange={(e) => setIncludeCharts(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600">Incluir gráficos y visualizaciones</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeRecommendations}
                onChange={(e) => setIncludeRecommendations(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600">Incluir recomendaciones automáticas</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={groupByLocation}
                onChange={(e) => setGroupByLocation(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600">Agrupar análisis por ubicación</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={groupByCategory}
                onChange={(e) => setGroupByCategory(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-600">Agrupar análisis por categoría</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <div className="flex justify-end">
          <button
            onClick={generateReport}
            disabled={loading || !selectedAuditId}
            className={`px-6 py-2 rounded-md font-medium ${
              loading || !selectedAuditId
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? 'Generando...' : 'Generar Reporte'}
          </button>
        </div>
      </div>
    </div>
  );

  const renderReportsTab = () => (
    <div className="space-y-6">
      {/* Filtros */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filtrar Reportes</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Auditoría
            </label>
            <select
              value={filters.audit_id}
              onChange={(e) => setFilters(prev => ({ ...prev, audit_id: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">Todas</option>
              {audits.map((audit) => (
                <option key={audit.id} value={audit.id}>
                  {audit.nombre}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              value={filters.report_type}
              onChange={(e) => setFilters(prev => ({ ...prev, report_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">Todos</option>
              <option value="DISCREPANCIES">Discrepancias</option>
              <option value="ADJUSTMENTS">Ajustes</option>
              <option value="ACCURACY">Precisión</option>
              <option value="FINANCIAL_IMPACT">Impacto Financiero</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">Todos</option>
              <option value="COMPLETED">Completado</option>
              <option value="GENERATING">Generando</option>
              <option value="FAILED">Fallido</option>
            </select>
          </div>

          <div>
            <button
              onClick={fetchReports}
              className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de reportes */}
      <div className="bg-white rounded-lg shadow border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Reportes Generados</h3>
        </div>
        
        {loading && (
          <div className="p-6 text-center text-gray-500">
            Cargando reportes...
          </div>
        )}

        {error && (
          <div className="p-6 text-center text-red-600">
            {error}
          </div>
        )}

        {!loading && !error && reports.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            No hay reportes que coincidan con los filtros
          </div>
        )}

        {!loading && !error && reports.length > 0 && (
          <div className="divide-y divide-gray-200">
            {reports.map((report) => (
              <div key={report.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-medium text-gray-900">
                        {report.report_name}
                      </h4>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                        {report.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        {getReportTypeLabel(report.report_type)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3 text-sm">
                      <div>
                        <span className="text-gray-500">Discrepancias:</span>
                        <span className="ml-1 font-medium">{report.total_discrepancies}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Ajustes:</span>
                        <span className="ml-1 font-medium">{report.total_adjustments}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Precisión:</span>
                        <span className="ml-1 font-medium">{report.accuracy_percentage.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Impacto:</span>
                        <span className="ml-1 font-medium">${report.financial_impact.toFixed(2)}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>Por: {report.generated_by_name}</span>
                      <span>•</span>
                      <span>{format(new Date(report.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}</span>
                      <span>•</span>
                      <span>{report.download_count} descargas</span>
                      <span>•</span>
                      <span>{report.file_format}</span>
                      {report.file_size && (
                        <>
                          <span>•</span>
                          <span>{Math.round(report.file_size / 1024)} KB</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    {report.is_completed && report.file_exists && (
                      <button
                        onClick={() => downloadReport(report.id)}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        Descargar
                      </button>
                    )}
                    
                    {report.is_expired && (
                      <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                        Expirado
                      </span>
                    )}
                  </div>
                </div>

                {report.description && (
                  <p className="mt-2 text-sm text-gray-600">{report.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Reportes de Discrepancias</h1>
            <p className="mt-1 text-sm text-gray-600">
              Genere y gestione reportes detallados de discrepancias en auditorías de inventario
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={fetchReportStats}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Actualizar
            </button>
          </div>
        </div>
      </div>

      {/* Navegación por tabs */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setSelectedTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setSelectedTab('generate')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'generate'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Generar Reporte
            </button>
            <button
              onClick={() => setSelectedTab('reports')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'reports'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Reportes Generados
            </button>
          </nav>
        </div>
        
        <div className="p-6">
          {selectedTab === 'dashboard' && renderDashboardTab()}
          {selectedTab === 'generate' && renderGenerateTab()}
          {selectedTab === 'reports' && renderReportsTab()}
        </div>
      </div>
    </div>
  );
};

export default ReporteDiscrepancias;