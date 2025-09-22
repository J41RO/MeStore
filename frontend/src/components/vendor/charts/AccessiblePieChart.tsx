/**
 * Accessible Pie Chart Component - WCAG 2.1 AA Compliant
 * Comprehensive accessibility features for pie chart visualization
 */

import React, { useMemo, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { screenReader, keyboardNavigation } from '../../../utils/accessibility';

interface CategoryData {
  category: string;
  sales: number;
  revenue: number;
  color: string;
  percentage: number;
}

interface AccessiblePieChartProps {
  data: CategoryData[];
  className?: string;
  ariaLabel?: string;
  title?: string;
  description?: string;
}

// WCAG compliant color palette with patterns for colorblind users
const ACCESSIBLE_PATTERNS = [
  { id: 'dots', pattern: 'url(#dots)' },
  { id: 'lines', pattern: 'url(#lines)' },
  { id: 'grid', pattern: 'url(#grid)' },
  { id: 'diagonal', pattern: 'url(#diagonal)' },
];

// Custom accessible tooltip
const AccessibleTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;

    const announcement = `${data.category}: ${data.percentage}% del total, ${data.sales} ventas, ingresos de ${new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(data.revenue)}`;

    return (
      <div
        className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg max-w-xs"
        role="tooltip"
        aria-live="polite"
        aria-label={announcement}
      >
        <div className="flex items-center mb-2">
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: data.color }}
            aria-hidden="true"
          />
          <p className="font-semibold text-gray-900">{data.category}</p>
        </div>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Porcentaje:</span>
            <span className="font-medium">{data.percentage}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Ventas:</span>
            <span className="font-medium">{data.sales}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Ingresos:</span>
            <span className="font-medium text-green-600">
              {new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 0,
              }).format(data.revenue)}
            </span>
          </div>
        </div>
        <div className="sr-only">{announcement}</div>
      </div>
    );
  }

  return null;
};

// Custom accessible legend
const AccessibleLegend = ({ payload, onItemClick, activeIndex }: any) => {
  return (
    <div
      className="flex flex-wrap gap-2 justify-center mt-4"
      role="list"
      aria-label="Leyenda del gráfico de categorías"
    >
      {payload.map((entry: any, index: number) => (
        <button
          key={entry.value}
          className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            activeIndex === index
              ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
              : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
          }`}
          onClick={() => onItemClick(index)}
          role="listitem"
          aria-pressed={activeIndex === index}
          aria-describedby={`legend-${index}-desc`}
        >
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: entry.color }}
            aria-hidden="true"
          />
          <span>{entry.value}</span>
          <div id={`legend-${index}-desc`} className="sr-only">
            Categoría {entry.value}, haz clic para resaltar en el gráfico
          </div>
        </button>
      ))}
    </div>
  );
};

export const AccessiblePieChart: React.FC<AccessiblePieChartProps> = ({
  data,
  className = '',
  ariaLabel = 'Gráfico circular de ventas por categoría',
  title = 'Distribución de Ventas por Categoría',
  description = 'Gráfico circular que muestra el porcentaje de ventas y ingresos por categoría de productos'
}) => {
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const [focusedIndex, setFocusedIndex] = useState<number>(0);

  // Generate accessible data summary
  const dataSummary = useMemo(() => {
    if (!data || data.length === 0) return '';

    const totalSales = data.reduce((sum, item) => sum + item.sales, 0);
    const totalRevenue = data.reduce((sum, item) => sum + item.revenue, 0);
    const topCategory = data.reduce((max, item) =>
      item.revenue > max.revenue ? item : max, data[0]
    );

    return `Resumen: ${data.length} categorías. Total ventas: ${totalSales}. Ingresos total: ${new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(totalRevenue)}. Categoría principal: ${topCategory.category} con ${topCategory.percentage}% (${new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(topCategory.revenue)}).`;
  }, [data]);

  // Keyboard navigation handler
  const handleKeyDown = (event: React.KeyboardEvent) => {
    const handler = keyboardNavigation.createKeyboardHandler({
      'ArrowRight': () => setFocusedIndex((prev) => (prev + 1) % data.length),
      'ArrowLeft': () => setFocusedIndex((prev) => (prev - 1 + data.length) % data.length),
      'Enter': () => setActiveIndex(focusedIndex),
      'Space': () => setActiveIndex(focusedIndex),
      'Escape': () => setActiveIndex(-1),
    });

    handler(event.nativeEvent);
  };

  if (!data || data.length === 0) {
    return (
      <div
        className={`p-6 text-center ${className}`}
        role="img"
        aria-label="Sin datos disponibles para mostrar"
      >
        <p className="text-gray-500">No hay datos disponibles</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Chart Header */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>

      {/* Visual Chart */}
      <div
        role="img"
        aria-label={`${ariaLabel}. ${dataSummary}`}
        aria-describedby="pie-chart-description pie-chart-table"
        className="relative"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        {/* SVG Pattern Definitions for Accessibility */}
        <svg width="0" height="0" className="absolute">
          <defs>
            <pattern id="dots" patternUnits="userSpaceOnUse" width="4" height="4">
              <circle cx="2" cy="2" r="1" fill="currentColor" fillOpacity="0.3" />
            </pattern>
            <pattern id="lines" patternUnits="userSpaceOnUse" width="4" height="4">
              <path d="M0,0 L4,4 M4,0 L0,4" stroke="currentColor" strokeWidth="1" strokeOpacity="0.3" />
            </pattern>
            <pattern id="grid" patternUnits="userSpaceOnUse" width="4" height="4">
              <path d="M0,0 L4,0 M0,0 L0,4" stroke="currentColor" strokeWidth="1" strokeOpacity="0.3" />
            </pattern>
            <pattern id="diagonal" patternUnits="userSpaceOnUse" width="4" height="4">
              <path d="M0,4 L4,0" stroke="currentColor" strokeWidth="1" strokeOpacity="0.3" />
            </pattern>
          </defs>
        </svg>

        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={80}
              fill="#8884d8"
              dataKey="percentage"
              animationBegin={0}
              animationDuration={800}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke={activeIndex === index ? '#1f2937' : 'none'}
                  strokeWidth={activeIndex === index ? 3 : 0}
                  style={{
                    filter: activeIndex === index ? 'brightness(1.1)' : 'none',
                    cursor: 'pointer'
                  }}
                  onClick={() => setActiveIndex(index)}
                  onMouseEnter={() => setActiveIndex(index)}
                  onMouseLeave={() => setActiveIndex(-1)}
                />
              ))}
            </Pie>
            <Tooltip content={<AccessibleTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Custom Legend */}
        <AccessibleLegend
          payload={data.map(item => ({ value: item.category, color: item.color }))}
          onItemClick={setActiveIndex}
          activeIndex={activeIndex}
        />

        {/* Chart keyboard instructions */}
        <div className="sr-only" id="pie-chart-description">
          Gráfico circular interactivo. Usa las teclas de flecha izquierda y derecha para navegar entre las categorías.
          Presiona Enter o Espacio para resaltar una categoría. Presiona Escape para deseleccionar.
          Usa Tab para acceder a la tabla de datos detallada.
        </div>
      </div>

      {/* Accessible Data Table */}
      <details className="border border-gray-200 rounded-lg">
        <summary className="p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors">
          <span className="font-medium">Ver datos en tabla</span>
          <span className="text-sm text-gray-500 ml-2">(accesible para lectores de pantalla)</span>
        </summary>

        <div className="p-3">
          <table
            id="pie-chart-table"
            className="w-full text-sm"
            role="table"
            aria-label="Tabla de datos del gráfico de categorías"
          >
            <caption className="sr-only">
              Datos tabulares del gráfico de distribución de ventas por categoría.
              {dataSummary}
            </caption>
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-900" scope="col">
                  Categoría
                </th>
                <th className="text-right py-2 px-3 font-medium text-gray-900" scope="col">
                  Porcentaje
                </th>
                <th className="text-right py-2 px-3 font-medium text-gray-900" scope="col">
                  Ventas
                </th>
                <th className="text-right py-2 px-3 font-medium text-gray-900" scope="col">
                  Ingresos
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr
                  key={row.category}
                  className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
                >
                  <td className="py-2 px-3">
                    <div className="flex items-center">
                      <div
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: row.color }}
                        aria-hidden="true"
                      />
                      <span className="font-medium text-gray-900">{row.category}</span>
                    </div>
                  </td>
                  <td className="py-2 px-3 text-right font-medium text-blue-600">
                    {row.percentage}%
                  </td>
                  <td className="py-2 px-3 text-right text-gray-700">
                    {row.sales}
                  </td>
                  <td className="py-2 px-3 text-right text-green-600 font-medium">
                    {new Intl.NumberFormat('es-CO', {
                      style: 'currency',
                      currency: 'COP',
                      minimumFractionDigits: 0,
                    }).format(row.revenue)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Summary statistics */}
          <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
            <h4 className="font-medium text-blue-900 mb-1">Resumen estadístico</h4>
            <p className="text-sm text-blue-800">{dataSummary}</p>
          </div>
        </div>
      </details>

      {/* Sonification alternative (placeholder for future implementation) */}
      <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
        <h4 className="font-medium text-gray-900 mb-1 flex items-center">
          <span className="mr-2" aria-hidden="true">🔊</span>
          Audio Description (Experimental)
        </h4>
        <p className="text-sm text-gray-600 mb-2">
          Próximamente: representación sonora de los datos para mejor accesibilidad.
        </p>
        <button
          className="text-sm text-blue-600 hover:text-blue-800 underline"
          onClick={() => {
            // Future: Implement sonification
            screenReader.announce(`Datos del gráfico: ${dataSummary}`);
          }}
        >
          Leer resumen en voz alta
        </button>
      </div>

      {/* Screen reader summary */}
      <div className="sr-only" aria-live="polite">
        Gráfico circular cargado exitosamente. {dataSummary}
      </div>
    </div>
  );
};

export default AccessiblePieChart;