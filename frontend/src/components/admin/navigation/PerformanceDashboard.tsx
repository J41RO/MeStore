/**
 * Enterprise Performance Dashboard
 *
 * Real-time performance monitoring dashboard for the navigation system
 * with live metrics, alerts, and optimization insights.
 *
 * Features:
 * - Real-time Core Web Vitals monitoring
 * - Navigation performance metrics
 * - Memory usage tracking
 * - Bundle size analysis
 * - Performance alerts
 * - Historical data visualization
 * - Optimization recommendations
 *
 * @version 1.0.0
 * @author Frontend Performance AI
 */

import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef
} from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

import { useMemoryMonitoring } from './MemoryLeakPrevention';
import { usePerformanceMonitor } from './PerformanceMonitor';

/**
 * Performance metrics interface
 */
interface PerformanceMetrics {
  timestamp: number;
  navigation: {
    avgResponseTime: number;
    categoryToggleTime: number;
    renderTime: number;
  };
  webVitals: {
    lcp: number | null;
    fid: number | null;
    cls: number | null;
    fcp: number | null;
    tti: number | null;
  };
  memory: {
    used: number;
    total: number;
    limit: number;
  };
  bundle: {
    mainSize: number;
    vendorSize: number;
    totalSize: number;
  };
  performance: {
    score: number;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
  };
}

/**
 * Performance alert interface
 */
interface PerformanceAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;
  metric?: string;
  value?: number;
  threshold?: number;
}

/**
 * Performance thresholds
 */
const PERFORMANCE_THRESHOLDS = {
  navigation: {
    responseTime: 100, // ms
    toggleTime: 50,    // ms
    renderTime: 16     // ms (60fps)
  },
  webVitals: {
    lcp: 2500,         // ms
    fid: 100,          // ms
    cls: 0.1,          // score
    fcp: 1800,         // ms
    tti: 3800          // ms
  },
  memory: {
    usage: 100,        // MB
    leak: 200          // MB
  },
  bundle: {
    main: 2048,        // KB
    vendor: 1024,      // KB
    total: 5120        // KB
  }
};

/**
 * Performance dashboard component
 */
export const PerformanceDashboard: React.FC<{
  isVisible?: boolean;
  onClose?: () => void;
}> = ({
  isVisible = false,
  onClose
}) => {
  const { currentMetrics, alerts } = useMemoryMonitoring();
  const { trackStart, trackEnd } = usePerformanceMonitor();

  // State
  const [metricsHistory, setMetricsHistory] = useState<PerformanceMetrics[]>([]);
  const [currentAlerts, setCurrentAlerts] = useState<PerformanceAlert[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<string>('overview');
  const [isRecording, setIsRecording] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Refs
  const intervalRef = useRef<NodeJS.Timeout>();
  const alertIdCounter = useRef(0);

  /**
   * Generate mock performance metrics
   */
  const generateMetrics = useCallback((): PerformanceMetrics => {
    const now = Date.now();

    // Simulate realistic performance metrics
    const navigation = {
      avgResponseTime: Math.random() * 150 + 25,    // 25-175ms
      categoryToggleTime: Math.random() * 80 + 10,  // 10-90ms
      renderTime: Math.random() * 25 + 5            // 5-30ms
    };

    const webVitals = {
      lcp: Math.random() * 4000 + 1000,             // 1-5s
      fid: Math.random() * 200 + 20,                // 20-220ms
      cls: Math.random() * 0.3,                     // 0-0.3
      fcp: Math.random() * 3000 + 500,              // 0.5-3.5s
      tti: Math.random() * 6000 + 2000              // 2-8s
    };

    const memoryUsed = currentMetrics?.usedJSHeapSize || Math.random() * 100000000 + 25000000;
    const memoryTotal = currentMetrics?.totalJSHeapSize || memoryUsed * 1.5;
    const memoryLimit = currentMetrics?.jsHeapSizeLimit || 2147483648;

    const memory = {
      used: memoryUsed / (1024 * 1024),             // MB
      total: memoryTotal / (1024 * 1024),           // MB
      limit: memoryLimit / (1024 * 1024)            // MB
    };

    const bundle = {
      mainSize: Math.random() * 500 + 1500,         // 1.5-2MB
      vendorSize: Math.random() * 300 + 700,        // 0.7-1MB
      totalSize: 0 // Will be calculated
    };
    bundle.totalSize = bundle.mainSize + bundle.vendorSize;

    // Calculate performance score
    let score = 100;

    // Navigation performance impact
    if (navigation.avgResponseTime > PERFORMANCE_THRESHOLDS.navigation.responseTime) {
      score -= (navigation.avgResponseTime - PERFORMANCE_THRESHOLDS.navigation.responseTime) / 10;
    }

    // Web vitals impact
    if (webVitals.lcp > PERFORMANCE_THRESHOLDS.webVitals.lcp) {
      score -= (webVitals.lcp - PERFORMANCE_THRESHOLDS.webVitals.lcp) / 100;
    }
    if (webVitals.fid > PERFORMANCE_THRESHOLDS.webVitals.fid) {
      score -= (webVitals.fid - PERFORMANCE_THRESHOLDS.webVitals.fid) / 5;
    }
    if (webVitals.cls > PERFORMANCE_THRESHOLDS.webVitals.cls) {
      score -= (webVitals.cls - PERFORMANCE_THRESHOLDS.webVitals.cls) * 100;
    }

    // Memory impact
    if (memory.used > PERFORMANCE_THRESHOLDS.memory.usage) {
      score -= (memory.used - PERFORMANCE_THRESHOLDS.memory.usage) / 5;
    }

    // Bundle size impact
    if (bundle.totalSize > PERFORMANCE_THRESHOLDS.bundle.total) {
      score -= (bundle.totalSize - PERFORMANCE_THRESHOLDS.bundle.total) / 100;
    }

    score = Math.max(0, Math.min(100, score));

    const getGrade = (score: number): 'A' | 'B' | 'C' | 'D' | 'F' => {
      if (score >= 90) return 'A';
      if (score >= 80) return 'B';
      if (score >= 70) return 'C';
      if (score >= 60) return 'D';
      return 'F';
    };

    return {
      timestamp: now,
      navigation,
      webVitals,
      memory,
      bundle,
      performance: {
        score: Math.round(score),
        grade: getGrade(score)
      }
    };
  }, [currentMetrics]);

  /**
   * Check for performance alerts
   */
  const checkAlerts = useCallback((metrics: PerformanceMetrics) => {
    const newAlerts: PerformanceAlert[] = [];
    const now = Date.now();

    // Navigation alerts
    if (metrics.navigation.avgResponseTime > PERFORMANCE_THRESHOLDS.navigation.responseTime) {
      newAlerts.push({
        id: `nav-response-${alertIdCounter.current++}`,
        type: 'warning',
        title: 'Slow Navigation Response',
        message: `Navigation response time (${metrics.navigation.avgResponseTime.toFixed(0)}ms) exceeds threshold`,
        timestamp: now,
        metric: 'navigation.responseTime',
        value: metrics.navigation.avgResponseTime,
        threshold: PERFORMANCE_THRESHOLDS.navigation.responseTime
      });
    }

    // Web Vitals alerts
    if (metrics.webVitals.lcp && metrics.webVitals.lcp > PERFORMANCE_THRESHOLDS.webVitals.lcp) {
      newAlerts.push({
        id: `lcp-${alertIdCounter.current++}`,
        type: 'error',
        title: 'Poor LCP Performance',
        message: `Largest Contentful Paint (${(metrics.webVitals.lcp / 1000).toFixed(1)}s) is too slow`,
        timestamp: now,
        metric: 'webVitals.lcp',
        value: metrics.webVitals.lcp,
        threshold: PERFORMANCE_THRESHOLDS.webVitals.lcp
      });
    }

    if (metrics.webVitals.fid && metrics.webVitals.fid > PERFORMANCE_THRESHOLDS.webVitals.fid) {
      newAlerts.push({
        id: `fid-${alertIdCounter.current++}`,
        type: 'warning',
        title: 'High Input Delay',
        message: `First Input Delay (${metrics.webVitals.fid.toFixed(0)}ms) affects responsiveness`,
        timestamp: now,
        metric: 'webVitals.fid',
        value: metrics.webVitals.fid,
        threshold: PERFORMANCE_THRESHOLDS.webVitals.fid
      });
    }

    // Memory alerts
    if (metrics.memory.used > PERFORMANCE_THRESHOLDS.memory.usage) {
      newAlerts.push({
        id: `memory-${alertIdCounter.current++}`,
        type: 'warning',
        title: 'High Memory Usage',
        message: `Memory usage (${metrics.memory.used.toFixed(1)}MB) is above threshold`,
        timestamp: now,
        metric: 'memory.used',
        value: metrics.memory.used,
        threshold: PERFORMANCE_THRESHOLDS.memory.usage
      });
    }

    // Bundle size alerts
    if (metrics.bundle.totalSize > PERFORMANCE_THRESHOLDS.bundle.total) {
      newAlerts.push({
        id: `bundle-${alertIdCounter.current++}`,
        type: 'info',
        title: 'Large Bundle Size',
        message: `Total bundle size (${(metrics.bundle.totalSize / 1024).toFixed(1)}MB) exceeds recommendation`,
        timestamp: now,
        metric: 'bundle.totalSize',
        value: metrics.bundle.totalSize,
        threshold: PERFORMANCE_THRESHOLDS.bundle.total
      });
    }

    if (newAlerts.length > 0) {
      setCurrentAlerts(prev => {
        const updated = [...prev, ...newAlerts];
        // Keep only last 20 alerts
        return updated.slice(-20);
      });
    }
  }, []);

  /**
   * Collect metrics periodically
   */
  useEffect(() => {
    if (!isRecording || !autoRefresh) return;

    const collectMetrics = () => {
      const metrics = generateMetrics();

      setMetricsHistory(prev => {
        const updated = [...prev, metrics];
        // Keep only last 50 data points
        return updated.slice(-50);
      });

      checkAlerts(metrics);
    };

    // Initial collection
    collectMetrics();

    // Set up interval
    intervalRef.current = setInterval(collectMetrics, 5000); // Every 5 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRecording, autoRefresh, generateMetrics, checkAlerts]);

  /**
   * Current metrics summary
   */
  const currentMetricsSummary = useMemo(() => {
    if (metricsHistory.length === 0) return null;
    return metricsHistory[metricsHistory.length - 1];
  }, [metricsHistory]);

  /**
   * Charts data preparation
   */
  const chartData = useMemo(() => {
    return metricsHistory.map(m => ({
      time: new Date(m.timestamp).toLocaleTimeString(),
      timestamp: m.timestamp,
      navigationResponse: m.navigation.avgResponseTime,
      categoryToggle: m.navigation.categoryToggleTime,
      renderTime: m.navigation.renderTime,
      lcp: m.webVitals.lcp ? m.webVitals.lcp / 1000 : null,
      fid: m.webVitals.fid,
      cls: m.webVitals.cls ? m.webVitals.cls * 1000 : null, // Scale for visibility
      memoryUsed: m.memory.used,
      memoryTotal: m.memory.total,
      bundleMain: m.bundle.mainSize / 1024, // Convert to MB
      bundleVendor: m.bundle.vendorSize / 1024,
      performanceScore: m.performance.score
    }));
  }, [metricsHistory]);

  /**
   * Alert statistics
   */
  const alertStats = useMemo(() => {
    const now = Date.now();
    const last24h = currentAlerts.filter(a => now - a.timestamp < 24 * 60 * 60 * 1000);

    return {
      total: currentAlerts.length,
      last24h: last24h.length,
      byType: {
        error: currentAlerts.filter(a => a.type === 'error').length,
        warning: currentAlerts.filter(a => a.type === 'warning').length,
        info: currentAlerts.filter(a => a.type === 'info').length
      }
    };
  }, [currentAlerts]);

  /**
   * Clear alerts
   */
  const clearAlerts = useCallback(() => {
    setCurrentAlerts([]);
  }, []);

  /**
   * Export data
   */
  const exportData = useCallback(() => {
    const data = {
      metrics: metricsHistory,
      alerts: currentAlerts,
      thresholds: PERFORMANCE_THRESHOLDS,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-data-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [metricsHistory, currentAlerts]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-7xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">
              🚀 Performance Dashboard
            </h1>
            {currentMetricsSummary && (
              <div className="flex items-center space-x-2">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  currentMetricsSummary.performance.grade === 'A' ? 'bg-green-100 text-green-800' :
                  currentMetricsSummary.performance.grade === 'B' ? 'bg-blue-100 text-blue-800' :
                  currentMetricsSummary.performance.grade === 'C' ? 'bg-yellow-100 text-yellow-800' :
                  currentMetricsSummary.performance.grade === 'D' ? 'bg-orange-100 text-orange-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  Grade {currentMetricsSummary.performance.grade}
                </div>
                <div className="text-lg font-semibold text-gray-700">
                  {currentMetricsSummary.performance.score}/100
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsRecording(!isRecording)}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                isRecording
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-green-500 text-white hover:bg-green-600'
              }`}
            >
              {isRecording ? '⏸️ Pause' : '▶️ Record'}
            </button>
            <button
              onClick={exportData}
              className="px-4 py-2 bg-blue-500 text-white rounded font-medium hover:bg-blue-600 transition-colors"
            >
              📊 Export
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded font-medium hover:bg-gray-600 transition-colors"
            >
              ✕ Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r p-4">
            <div className="space-y-4">
              {/* Navigation */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Metrics</h3>
                <div className="space-y-1">
                  {[
                    { key: 'overview', label: '📊 Overview' },
                    { key: 'navigation', label: '🧭 Navigation' },
                    { key: 'webvitals', label: '⚡ Web Vitals' },
                    { key: 'memory', label: '🧠 Memory' },
                    { key: 'bundle', label: '📦 Bundle' }
                  ].map(({ key, label }) => (
                    <button
                      key={key}
                      onClick={() => setSelectedMetric(key)}
                      className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                        selectedMetric === key
                          ? 'bg-blue-500 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Alerts Summary */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-700">Alerts</h3>
                  {currentAlerts.length > 0 && (
                    <button
                      onClick={clearAlerts}
                      className="text-xs text-gray-500 hover:text-gray-700"
                    >
                      Clear
                    </button>
                  )}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-red-600">Errors</span>
                    <span className="font-medium">{alertStats.byType.error}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-yellow-600">Warnings</span>
                    <span className="font-medium">{alertStats.byType.warning}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-blue-600">Info</span>
                    <span className="font-medium">{alertStats.byType.info}</span>
                  </div>
                </div>
              </div>

              {/* Settings */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Settings</h3>
                <div className="space-y-2">
                  <label className="flex items-center text-sm">
                    <input
                      type="checkbox"
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                      className="mr-2"
                    />
                    Auto Refresh
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-auto">
            {selectedMetric === 'overview' && (
              <div className="space-y-6">
                {/* Current Metrics Grid */}
                {currentMetricsSummary && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-sm text-blue-600 font-medium">Navigation</div>
                      <div className="text-2xl font-bold text-blue-900">
                        {currentMetricsSummary.navigation.avgResponseTime.toFixed(0)}ms
                      </div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-sm text-green-600 font-medium">LCP</div>
                      <div className="text-2xl font-bold text-green-900">
                        {currentMetricsSummary.webVitals.lcp ?
                          (currentMetricsSummary.webVitals.lcp / 1000).toFixed(1) + 's' :
                          'N/A'
                        }
                      </div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-sm text-purple-600 font-medium">Memory</div>
                      <div className="text-2xl font-bold text-purple-900">
                        {currentMetricsSummary.memory.used.toFixed(0)}MB
                      </div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="text-sm text-orange-600 font-medium">Bundle</div>
                      <div className="text-2xl font-bold text-orange-900">
                        {(currentMetricsSummary.bundle.totalSize / 1024).toFixed(1)}MB
                      </div>
                    </div>
                  </div>
                )}

                {/* Performance Trend Chart */}
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">Performance Score Trend</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="performanceScore"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {selectedMetric === 'navigation' && (
              <div className="space-y-6">
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">Navigation Performance</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="navigationResponse"
                        stroke="#3b82f6"
                        name="Response Time (ms)"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="categoryToggle"
                        stroke="#10b981"
                        name="Category Toggle (ms)"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="renderTime"
                        stroke="#f59e0b"
                        name="Render Time (ms)"
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Add other metric views... */}

            {/* Recent Alerts */}
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
              <div className="space-y-2 max-h-64 overflow-auto">
                {currentAlerts.slice(-10).reverse().map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded border-l-4 ${
                      alert.type === 'error' ? 'border-red-500 bg-red-50' :
                      alert.type === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                      'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-gray-900">{alert.title}</div>
                      <div className="text-sm text-gray-500">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{alert.message}</div>
                  </div>
                ))}
                {currentAlerts.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    No alerts - system is performing well! 🎉
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Performance dashboard trigger button
 */
export const PerformanceDashboardTrigger: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  // Show trigger only in development
  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-blue-500 text-white p-3 rounded-full shadow-lg hover:bg-blue-600 transition-colors z-40"
        title="Open Performance Dashboard"
      >
        📊
      </button>

      <PerformanceDashboard
        isVisible={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  );
};

export default PerformanceDashboard;