import React, { useState, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { SidebarProvider } from './SidebarProvider';
import { HierarchicalSidebar } from './HierarchicalSidebar';
import {
  SidebarPerformanceDisplay,
  withSidebarPerformanceMonitoring,
  type SidebarPerformanceMetrics
} from './SidebarPerformanceMonitor';

// Sidebar optimizado con monitoreo de performance
const OptimizedSidebar = withSidebarPerformanceMonitoring(HierarchicalSidebar);

// Componente de validación de performance
export const PerformanceValidation: React.FC = () => {
  const [metrics, setMetrics] = useState<SidebarPerformanceMetrics | null>(null);
  const [validationResults, setValidationResults] = useState<{
    passed: number;
    failed: number;
    details: string[];
  }>({
    passed: 0,
    failed: 0,
    details: []
  });

  // Validar métricas contra objetivos
  const validateMetrics = (newMetrics: SidebarPerformanceMetrics) => {
    const results = {
      passed: 0,
      failed: 0,
      details: [] as string[]
    };

    // Objetivo: Sidebar render < 100ms
    if (newMetrics.renderTime < 100) {
      results.passed++;
      results.details.push(`✅ Render Time: ${newMetrics.renderTime.toFixed(2)}ms < 100ms`);
    } else {
      results.failed++;
      results.details.push(`❌ Render Time: ${newMetrics.renderTime.toFixed(2)}ms >= 100ms`);
    }

    // Objetivo: Category expansion < 200ms
    if (newMetrics.categoryExpansionTime < 200) {
      results.passed++;
      results.details.push(`✅ Category Expansion: ${newMetrics.categoryExpansionTime.toFixed(2)}ms < 200ms`);
    } else {
      results.failed++;
      results.details.push(`❌ Category Expansion: ${newMetrics.categoryExpansionTime.toFixed(2)}ms >= 200ms`);
    }

    // Objetivo: Icon loading < 50ms
    if (newMetrics.iconLoadTime < 50) {
      results.passed++;
      results.details.push(`✅ Icon Load Time: ${newMetrics.iconLoadTime.toFixed(2)}ms < 50ms`);
    } else {
      results.failed++;
      results.details.push(`❌ Icon Load Time: ${newMetrics.iconLoadTime.toFixed(2)}ms >= 50ms`);
    }

    // Objetivo: Bundle impact < 10KB (estimado como tiempo de carga)
    if (newMetrics.bundleImpact < 100) {
      results.passed++;
      results.details.push(`✅ Bundle Impact: ${newMetrics.bundleImpact.toFixed(2)}ms (optimized)`);
    } else {
      results.failed++;
      results.details.push(`❌ Bundle Impact: ${newMetrics.bundleImpact.toFixed(2)}ms (needs optimization)`);
    }

    // Objetivo: Memory usage reasonable (< 5MB for sidebar)
    const memoryMB = newMetrics.memoryUsage / 1024 / 1024;
    if (memoryMB < 5) {
      results.passed++;
      results.details.push(`✅ Memory Usage: ${memoryMB.toFixed(2)}MB < 5MB`);
    } else {
      results.failed++;
      results.details.push(`❌ Memory Usage: ${memoryMB.toFixed(2)}MB >= 5MB`);
    }

    setValidationResults(results);
  };

  // Manejar actualización de métricas
  const handleMetricsUpdate = (newMetrics: SidebarPerformanceMetrics) => {
    setMetrics(newMetrics);
    validateMetrics(newMetrics);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        🚀 Sidebar Performance Validation Dashboard
      </h2>

      {/* Resumen de validación */}
      <div className="bg-white border rounded-lg p-4 mb-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-3">Performance Validation Results</h3>

        {validationResults.passed + validationResults.failed > 0 ? (
          <div>
            <div className="flex gap-4 mb-3">
              <span className="text-green-600 font-medium">
                ✅ Passed: {validationResults.passed}
              </span>
              <span className="text-red-600 font-medium">
                ❌ Failed: {validationResults.failed}
              </span>
              <span className="text-blue-600 font-medium">
                📊 Success Rate: {(
                  (validationResults.passed / (validationResults.passed + validationResults.failed)) * 100
                ).toFixed(1)}%
              </span>
            </div>

            <div className="space-y-1">
              {validationResults.details.map((detail, index) => (
                <div key={index} className="text-sm font-mono">
                  {detail}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">
            Interacting with the sidebar to collect performance metrics...
          </p>
        )}
      </div>

      {/* Optimizaciones implementadas */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-3 text-blue-800">
          🎯 Performance Optimizations Implemented
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div>
            <h4 className="font-medium text-blue-700 mb-2">Icon Optimization</h4>
            <ul className="space-y-1 text-blue-600">
              <li>• Tree shaking for @heroicons/react</li>
              <li>• Individual icon imports</li>
              <li>• Complete iconography integration</li>
              <li>• Icon fallback system</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-blue-700 mb-2">React Performance</h4>
            <ul className="space-y-1 text-blue-600">
              <li>• React.memo optimization</li>
              <li>• useMemo for expensive calculations</li>
              <li>• useCallback for event handlers</li>
              <li>• Component memoization</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-blue-700 mb-2">Animation Optimization</h4>
            <ul className="space-y-1 text-blue-600">
              <li>• GPU acceleration with transform3d</li>
              <li>• will-change properties</li>
              <li>• CSS transitions optimization</li>
              <li>• Layout shift prevention</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-blue-700 mb-2">Memory Management</h4>
            <ul className="space-y-1 text-blue-600">
              <li>• Debounced localStorage saves</li>
              <li>• Event listener cleanup</li>
              <li>• Lazy loading implementation</li>
              <li>• Performance monitoring</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Sidebar de prueba */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">
          🧪 Interactive Sidebar Test Environment
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Interact with the sidebar below to see real-time performance metrics.
          Click categories to expand/collapse and observe the optimization results.
        </p>

        <div className="border rounded bg-white" style={{ height: '500px' }}>
          <BrowserRouter>
            <SidebarProvider>
              <div className="flex h-full">
                <div className="w-64 border-r bg-gray-50 overflow-y-auto">
                  <OptimizedSidebar
                    enablePerformanceMonitoring={true}
                    onMetricsUpdate={handleMetricsUpdate}
                  />
                </div>
                <div className="flex-1 p-4">
                  <div className="text-center text-gray-500">
                    <h4 className="font-medium mb-2">Sidebar Performance Demo</h4>
                    <p className="text-sm">
                      Use the sidebar on the left to test the performance optimizations.
                      Metrics will appear in real-time in the dashboard above.
                    </p>

                    {metrics && (
                      <div className="mt-4 text-left">
                        <h5 className="font-medium mb-2">Current Metrics:</h5>
                        <div className="bg-gray-100 p-3 rounded text-xs font-mono">
                          <div>Render Time: {metrics.renderTime.toFixed(2)}ms</div>
                          <div>Category Expansion: {metrics.categoryExpansionTime.toFixed(2)}ms</div>
                          <div>Icon Load: {metrics.iconLoadTime.toFixed(2)}ms</div>
                          <div>Memory: {(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB</div>
                          <div>Last Updated: {new Date(metrics.timestamp).toLocaleTimeString()}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </SidebarProvider>
          </BrowserRouter>
        </div>
      </div>

      {/* Display de métricas en desarrollo */}
      <SidebarPerformanceDisplay
        metrics={metrics}
        showDetails={true}
      />
    </div>
  );
};

export default PerformanceValidation;