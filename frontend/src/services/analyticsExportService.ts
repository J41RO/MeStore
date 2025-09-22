// frontend/src/services/analyticsExportService.ts
// PERFORMANCE_OPTIMIZED: Analytics export service for PDF/Excel
// Target: <2s export generation with large datasets

import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { pdf } from '@react-pdf/renderer';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import React from 'react';

export interface AnalyticsExportData {
  title: string;
  subtitle?: string;
  timestamp: string;
  metrics: {
    totalRevenue: number;
    totalOrders: number;
    totalProducts: number;
    totalCustomers: number;
    growthRate: number;
    period: string;
  };
  charts: {
    revenue: Array<{ month: string; revenue: number; orders: number; customers?: number }>;
    categories: Array<{ category: string; sales: number; revenue: number; percentage: number }>;
    products: Array<{ name: string; sales: number; revenue: number; trend?: string }>;
  };
  filters: {
    timeRange: string;
    category: string;
    dateFrom?: string;
    dateTo?: string;
  };
}

// PDF styles
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 30,
    fontSize: 12,
    fontFamily: 'Helvetica'
  },
  header: {
    marginBottom: 20,
    borderBottom: 1,
    borderBottomColor: '#e5e7eb',
    paddingBottom: 15
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 5
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 10
  },
  timestamp: {
    fontSize: 10,
    color: '#9ca3af'
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 15,
    marginBottom: 25
  },
  metricCard: {
    flex: 1,
    minWidth: 120,
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    border: 1,
    borderColor: '#e5e7eb'
  },
  metricLabel: {
    fontSize: 10,
    color: '#6b7280',
    marginBottom: 5,
    textTransform: 'uppercase'
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827'
  },
  section: {
    marginBottom: 25
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 15,
    borderBottom: 1,
    borderBottomColor: '#e5e7eb',
    paddingBottom: 5
  },
  table: {
    width: '100%'
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    padding: 8,
    borderBottom: 1,
    borderBottomColor: '#d1d5db'
  },
  tableRow: {
    flexDirection: 'row',
    padding: 8,
    borderBottom: 1,
    borderBottomColor: '#e5e7eb'
  },
  tableCell: {
    flex: 1,
    fontSize: 10
  },
  tableCellHeader: {
    flex: 1,
    fontSize: 10,
    fontWeight: 'bold',
    color: '#374151'
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 30,
    right: 30,
    textAlign: 'center',
    fontSize: 10,
    color: '#9ca3af',
    borderTop: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 10
  }
});

// PDF Document Component
const AnalyticsPDFDocument: React.FC<{ data: AnalyticsExportData }> = ({ data }) => {
  const formatCOP = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{data.title}</Text>
          {data.subtitle && <Text style={styles.subtitle}>{data.subtitle}</Text>}
          <Text style={styles.timestamp}>
            Generado el {new Date(data.timestamp).toLocaleString('es-CO')}
          </Text>
        </View>

        {/* Metrics Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumen de Métricas</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Ingresos Totales</Text>
              <Text style={styles.metricValue}>{formatCOP(data.metrics.totalRevenue)}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Órdenes Totales</Text>
              <Text style={styles.metricValue}>{data.metrics.totalOrders.toLocaleString()}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Productos</Text>
              <Text style={styles.metricValue}>{data.metrics.totalProducts}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Clientes</Text>
              <Text style={styles.metricValue}>{data.metrics.totalCustomers}</Text>
            </View>
          </View>
        </View>

        {/* Revenue Trends */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tendencias de Ingresos</Text>
          <View style={styles.table}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableCellHeader}>Mes</Text>
              <Text style={styles.tableCellHeader}>Ingresos</Text>
              <Text style={styles.tableCellHeader}>Órdenes</Text>
              <Text style={styles.tableCellHeader}>Clientes</Text>
            </View>
            {data.charts.revenue.map((item, index) => (
              <View key={index} style={styles.tableRow}>
                <Text style={styles.tableCell}>{item.month}</Text>
                <Text style={styles.tableCell}>{formatCOP(item.revenue)}</Text>
                <Text style={styles.tableCell}>{item.orders}</Text>
                <Text style={styles.tableCell}>{item.customers || 0}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Category Analysis */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Análisis por Categorías</Text>
          <View style={styles.table}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableCellHeader}>Categoría</Text>
              <Text style={styles.tableCellHeader}>Ventas</Text>
              <Text style={styles.tableCellHeader}>Ingresos</Text>
              <Text style={styles.tableCellHeader}>Participación</Text>
            </View>
            {data.charts.categories.map((item, index) => (
              <View key={index} style={styles.tableRow}>
                <Text style={styles.tableCell}>{item.category}</Text>
                <Text style={styles.tableCell}>{item.sales}</Text>
                <Text style={styles.tableCell}>{formatCOP(item.revenue)}</Text>
                <Text style={styles.tableCell}>{item.percentage.toFixed(1)}%</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Top Products */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Productos Más Vendidos</Text>
          <View style={styles.table}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableCellHeader}>Producto</Text>
              <Text style={styles.tableCellHeader}>Ventas</Text>
              <Text style={styles.tableCellHeader}>Ingresos</Text>
              <Text style={styles.tableCellHeader}>Tendencia</Text>
            </View>
            {data.charts.products.slice(0, 10).map((item, index) => (
              <View key={index} style={styles.tableRow}>
                <Text style={styles.tableCell}>{item.name}</Text>
                <Text style={styles.tableCell}>{item.sales}</Text>
                <Text style={styles.tableCell}>{formatCOP(item.revenue)}</Text>
                <Text style={styles.tableCell}>{item.trend || 'N/A'}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Footer */}
        <Text style={styles.footer}>
          MeStore Analytics • {data.filters.timeRange} •
          Generado automáticamente el {new Date().toLocaleDateString('es-CO')}
        </Text>
      </Page>
    </Document>
  );
};

class AnalyticsExportService {
  // Performance tracking
  private exportTimes: number[] = [];

  // Track export performance
  private trackExportTime(time: number, type: string) {
    this.exportTimes.push(time);

    // Keep only last 10 export times
    if (this.exportTimes.length > 10) {
      this.exportTimes.shift();
    }

    console.log(`${type} export completed in ${time.toFixed(2)}ms`);

    // Log warning if export takes too long
    if (time > 2000) {
      console.warn(`Slow ${type} export: ${time.toFixed(2)}ms`);
    }
  }

  // Get average export time
  getAverageExportTime(): number {
    if (this.exportTimes.length === 0) return 0;
    return this.exportTimes.reduce((sum, time) => sum + time, 0) / this.exportTimes.length;
  }

  // Export to Excel
  async exportToExcel(data: AnalyticsExportData, filename?: string): Promise<void> {
    const startTime = performance.now();

    try {
      // Create workbook
      const workbook = XLSX.utils.book_new();

      // Metrics sheet
      const metricsData = [
        ['Métrica', 'Valor'],
        ['Ingresos Totales', data.metrics.totalRevenue],
        ['Órdenes Totales', data.metrics.totalOrders],
        ['Productos', data.metrics.totalProducts],
        ['Clientes', data.metrics.totalCustomers],
        ['Tasa de Crecimiento', `${data.metrics.growthRate.toFixed(1)}%`],
        ['Período', data.metrics.period]
      ];
      const metricsSheet = XLSX.utils.aoa_to_sheet(metricsData);
      XLSX.utils.book_append_sheet(workbook, metricsSheet, 'Métricas');

      // Revenue trends sheet
      const revenueData = [
        ['Mes', 'Ingresos', 'Órdenes', 'Clientes'],
        ...data.charts.revenue.map(item => [
          item.month,
          item.revenue,
          item.orders,
          item.customers || 0
        ])
      ];
      const revenueSheet = XLSX.utils.aoa_to_sheet(revenueData);
      XLSX.utils.book_append_sheet(workbook, revenueSheet, 'Ingresos');

      // Categories sheet
      const categoriesData = [
        ['Categoría', 'Ventas', 'Ingresos', 'Participación (%)'],
        ...data.charts.categories.map(item => [
          item.category,
          item.sales,
          item.revenue,
          item.percentage
        ])
      ];
      const categoriesSheet = XLSX.utils.aoa_to_sheet(categoriesData);
      XLSX.utils.book_append_sheet(workbook, categoriesSheet, 'Categorías');

      // Products sheet
      const productsData = [
        ['Producto', 'Ventas', 'Ingresos', 'Tendencia'],
        ...data.charts.products.map(item => [
          item.name,
          item.sales,
          item.revenue,
          item.trend || 'N/A'
        ])
      ];
      const productsSheet = XLSX.utils.aoa_to_sheet(productsData);
      XLSX.utils.book_append_sheet(workbook, productsSheet, 'Productos');

      // Auto-size columns (performance optimization)
      const sheets = ['Métricas', 'Ingresos', 'Categorías', 'Productos'];
      sheets.forEach(sheetName => {
        const sheet = workbook.Sheets[sheetName];
        if (sheet) {
          const cols = [];
          const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1');

          for (let col = range.s.c; col <= range.e.c; col++) {
            let maxWidth = 10;
            for (let row = range.s.r; row <= range.e.r; row++) {
              const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
              const cell = sheet[cellAddress];
              if (cell && cell.v) {
                const cellLength = cell.v.toString().length;
                maxWidth = Math.max(maxWidth, cellLength + 2);
              }
            }
            cols.push({ width: Math.min(maxWidth, 50) });
          }
          sheet['!cols'] = cols;
        }
      });

      // Generate buffer
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

      // Save file
      const finalFilename = filename || `analytics-${data.filters.timeRange}-${Date.now()}.xlsx`;
      saveAs(blob, finalFilename);

      const exportTime = performance.now() - startTime;
      this.trackExportTime(exportTime, 'Excel');

    } catch (error) {
      console.error('Excel export failed:', error);
      throw new Error('Failed to export Excel file');
    }
  }

  // Export to PDF
  async exportToPDF(data: AnalyticsExportData, filename?: string): Promise<void> {
    const startTime = performance.now();

    try {
      // Generate PDF
      const pdfDoc = <AnalyticsPDFDocument data={data} />;
      const pdfBlob = await pdf(pdfDoc).toBlob();

      // Save file
      const finalFilename = filename || `analytics-${data.filters.timeRange}-${Date.now()}.pdf`;
      saveAs(pdfBlob, finalFilename);

      const exportTime = performance.now() - startTime;
      this.trackExportTime(exportTime, 'PDF');

    } catch (error) {
      console.error('PDF export failed:', error);
      throw new Error('Failed to export PDF file');
    }
  }

  // Export to CSV (lightweight option)
  async exportToCSV(data: AnalyticsExportData, type: 'revenue' | 'categories' | 'products' | 'all' = 'all', filename?: string): Promise<void> {
    const startTime = performance.now();

    try {
      let csvContent = '';
      let finalFilename = '';

      switch (type) {
        case 'revenue':
          csvContent = this.generateRevenueCSV(data);
          finalFilename = filename || `revenue-${data.filters.timeRange}-${Date.now()}.csv`;
          break;
        case 'categories':
          csvContent = this.generateCategoriesCSV(data);
          finalFilename = filename || `categories-${data.filters.timeRange}-${Date.now()}.csv`;
          break;
        case 'products':
          csvContent = this.generateProductsCSV(data);
          finalFilename = filename || `products-${data.filters.timeRange}-${Date.now()}.csv`;
          break;
        default:
          csvContent = this.generateAllDataCSV(data);
          finalFilename = filename || `analytics-all-${data.filters.timeRange}-${Date.now()}.csv`;
      }

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, finalFilename);

      const exportTime = performance.now() - startTime;
      this.trackExportTime(exportTime, 'CSV');

    } catch (error) {
      console.error('CSV export failed:', error);
      throw new Error('Failed to export CSV file');
    }
  }

  // Generate CSV content for revenue data
  private generateRevenueCSV(data: AnalyticsExportData): string {
    const headers = ['Mes', 'Ingresos', 'Órdenes', 'Clientes'];
    const rows = data.charts.revenue.map(item => [
      item.month,
      item.revenue,
      item.orders,
      item.customers || 0
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  // Generate CSV content for categories data
  private generateCategoriesCSV(data: AnalyticsExportData): string {
    const headers = ['Categoría', 'Ventas', 'Ingresos', 'Participación (%)'];
    const rows = data.charts.categories.map(item => [
      item.category,
      item.sales,
      item.revenue,
      item.percentage
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  // Generate CSV content for products data
  private generateProductsCSV(data: AnalyticsExportData): string {
    const headers = ['Producto', 'Ventas', 'Ingresos', 'Tendencia'];
    const rows = data.charts.products.map(item => [
      item.name,
      item.sales,
      item.revenue,
      item.trend || 'N/A'
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  // Generate CSV content for all data
  private generateAllDataCSV(data: AnalyticsExportData): string {
    const sections = [
      '# MÉTRICAS GENERALES',
      'Métrica,Valor',
      `Ingresos Totales,${data.metrics.totalRevenue}`,
      `Órdenes Totales,${data.metrics.totalOrders}`,
      `Productos,${data.metrics.totalProducts}`,
      `Clientes,${data.metrics.totalCustomers}`,
      `Tasa de Crecimiento,${data.metrics.growthRate.toFixed(1)}%`,
      `Período,${data.metrics.period}`,
      '',
      '# TENDENCIAS DE INGRESOS',
      this.generateRevenueCSV(data),
      '',
      '# ANÁLISIS POR CATEGORÍAS',
      this.generateCategoriesCSV(data),
      '',
      '# PRODUCTOS MÁS VENDIDOS',
      this.generateProductsCSV(data)
    ];

    return sections.join('\n');
  }
}

// Singleton instance
export const analyticsExportService = new AnalyticsExportService();

// React hook for export functionality
export const useAnalyticsExport = () => {
  const [isExporting, setIsExporting] = React.useState(false);
  const [exportProgress, setExportProgress] = React.useState(0);

  const exportData = React.useCallback(async (
    data: AnalyticsExportData,
    format: 'pdf' | 'excel' | 'csv',
    filename?: string
  ) => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setExportProgress(prev => Math.min(prev + 10, 90));
      }, 100);

      switch (format) {
        case 'pdf':
          await analyticsExportService.exportToPDF(data, filename);
          break;
        case 'excel':
          await analyticsExportService.exportToExcel(data, filename);
          break;
        case 'csv':
          await analyticsExportService.exportToCSV(data, 'all', filename);
          break;
      }

      clearInterval(progressInterval);
      setExportProgress(100);

      // Reset after completion
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
      }, 500);

    } catch (error) {
      setIsExporting(false);
      setExportProgress(0);
      throw error;
    }
  }, []);

  return {
    isExporting,
    exportProgress,
    exportData,
    getAverageExportTime: () => analyticsExportService.getAverageExportTime()
  };
};

export default analyticsExportService;