// ~/src/components/discovery/PerformanceMonitor.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Real-time Performance Monitor for Product Discovery
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: PerformanceMonitor.tsx
// Ruta: ~/src/components/discovery/PerformanceMonitor.tsx
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Monitor de rendimiento en tiempo real para el sistema de descubrimiento
//
// Monitoring Features:
// - Core Web Vitals real-time tracking
// - Search performance analytics
// - Memory usage monitoring
// - Bundle size analysis
// - Mobile performance metrics
// - User experience scoring
// ---------------------------------------------------------------------------------------------

import React, { useState, useEffect, useCallback, memo } from 'react';
import {
  Activity,
  Zap,
  Clock,
  Eye,
  Smartphone,
  Gauge,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Monitor,
  Wifi,
  Battery,
  X,
} from 'lucide-react';
import { usePerformanceOptimization } from '../../utils/performanceOptimizer';
import { useProductDiscoveryStore } from '../../stores/productDiscoveryStore';

interface PerformanceMonitorProps {
  enabled?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  showDetails?: boolean;
  onClose?: () => void;
}

interface WebVitalsData {
  lcp: number | null;
  fid: number | null;
  cls: number | null;
  fcp: number | null;
  ttfb: number | null;
}

interface PerformanceScore {
  overall: number;
  lcp: number;
  fid: number;
  cls: number;
  search: number;
  mobile: number;
}

/**
 * Metric Card Component
 */
const MetricCard = memo(({
  title,
  value,
  unit,
  icon: Icon,
  status,
  threshold,
  description,
}: {
  title: string;
  value: number | null;
  unit: string;
  icon: React.ComponentType<any>;
  status: 'good' | 'needs-improvement' | 'poor';
  threshold: number;
  description: string;
}) => {
  const formatValue = (val: number | null) => {
    if (val === null) return '--';
    if (val > 1000) return `${(val / 1000).toFixed(1)}k`;
    return val.toFixed(val < 10 ? 2 : 0);
  };

  const statusColors = {
    good: 'text-green-600 bg-green-50 border-green-200',
    'needs-improvement': 'text-yellow-600 bg-yellow-50 border-yellow-200',
    poor: 'text-red-600 bg-red-50 border-red-200',
  };

  const statusIcons = {
    good: CheckCircle,
    'needs-improvement': AlertTriangle,
    poor: AlertTriangle,
  };

  const StatusIcon = statusIcons[status];

  return (
    <div className={`p-3 rounded-lg border ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Icon className="w-4 h-4" />
          <span className="text-sm font-medium">{title}</span>
        </div>
        <StatusIcon className="w-4 h-4" />
      </div>

      <div className="space-y-1">
        <div className="text-xl font-bold">
          {formatValue(value)}{unit}
        </div>
        <div className="text-xs opacity-75">
          Threshold: {formatValue(threshold)}{unit}
        </div>
        <div className="text-xs">{description}</div>
      </div>
    </div>
  );
});

/**
 * Real-time Chart Component
 */
const RealTimeChart = memo(({
  data,
  label,
  color = '#3B82F6',
  height = 60,
}: {
  data: number[];
  label: string;
  color?: string;
  height?: number;
}) => {
  const maxValue = Math.max(...data, 1);
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = height - (value / maxValue) * height;
    return `${x},${y}`;
  });

  return (
    <div className="bg-white rounded-lg border p-3">
      <div className="text-sm font-medium text-gray-700 mb-2">{label}</div>
      <svg width="100%" height={height} className="overflow-visible">
        <polyline
          points={points.join(' ')}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="transition-all duration-300"
        />
        <defs>
          <linearGradient id={`gradient-${label}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.2 }} />
            <stop offset="100%" style={{ stopColor: color, stopOpacity: 0 }} />
          </linearGradient>
        </defs>
        <polygon
          points={`0,${height} ${points.join(' ')} 100,${height}`}
          fill={`url(#gradient-${label})`}
        />
      </svg>
    </div>
  );
});

/**
 * Main Performance Monitor Component
 */
const PerformanceMonitor: React.FC<PerformanceMonitorProps> = memo(({
  enabled = true,
  position = 'bottom-right',
  showDetails = false,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(enabled);
  const [isExpanded, setIsExpanded] = useState(showDetails);
  const [webVitals, setWebVitals] = useState<WebVitalsData>({
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null,
  });

  const [performanceHistory, setPerformanceHistory] = useState<{
    searchTimes: number[];
    memoryUsage: number[];
    renderTimes: number[];
  }>({
    searchTimes: [],
    memoryUsage: [],
    renderTimes: [],
  });

  const [networkInfo, setNetworkInfo] = useState<{
    effectiveType: string;
    downlink: number;
    rtt: number;
    saveData: boolean;
  }>({
    effectiveType: '4g',
    downlink: 10,
    rtt: 100,
    saveData: false,
  });

  const { getMetrics, getPerformanceReport } = usePerformanceOptimization();
  const performanceMetrics = useProductDiscoveryStore(state => state.performance);

  // Web Vitals collection
  useEffect(() => {
    if (!enabled) return;

    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS((metric) => setWebVitals(prev => ({ ...prev, cls: metric.value })));
      getFID((metric) => setWebVitals(prev => ({ ...prev, fid: metric.value })));
      getFCP((metric) => setWebVitals(prev => ({ ...prev, fcp: metric.value })));
      getLCP((metric) => setWebVitals(prev => ({ ...prev, lcp: metric.value })));
      getTTFB((metric) => setWebVitals(prev => ({ ...prev, ttfb: metric.value })));
    });
  }, [enabled]);

  // Network information
  useEffect(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;

      const updateNetworkInfo = () => {
        setNetworkInfo({
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData,
        });
      };

      connection.addEventListener('change', updateNetworkInfo);
      updateNetworkInfo();

      return () => connection.removeEventListener('change', updateNetworkInfo);
    }
  }, []);

  // Performance history tracking
  useEffect(() => {
    const interval = setInterval(() => {
      const metrics = getMetrics();

      setPerformanceHistory(prev => ({
        searchTimes: [...prev.searchTimes.slice(-19), performanceMetrics.searchLatency.slice(-1)[0] || 0],
        memoryUsage: [...prev.memoryUsage.slice(-19), metrics.memoryUsage],
        renderTimes: [...prev.renderTimes.slice(-19), performanceMetrics.renderTime.slice(-1)[0] || 0],
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [getMetrics, performanceMetrics]);

  // Calculate performance scores
  const performanceScore = useCallback((): PerformanceScore => {
    const thresholds = {
      lcp: 2500,
      fid: 100,
      cls: 0.1,
      fcp: 1800,
      ttfb: 800,
    };

    const calculateScore = (value: number | null, threshold: number, invert = false) => {
      if (value === null) return 0;
      const ratio = invert ? threshold / value : value / threshold;
      return Math.max(0, Math.min(100, ratio * 100));
    };

    const lcpScore = calculateScore(webVitals.lcp, thresholds.lcp, true);
    const fidScore = calculateScore(webVitals.fid, thresholds.fid, true);
    const clsScore = calculateScore(webVitals.cls, thresholds.cls, true);

    const searchScore = performanceMetrics.searchLatency.length > 0
      ? calculateScore(
          performanceMetrics.searchLatency.reduce((a, b) => a + b, 0) / performanceMetrics.searchLatency.length,
          200,
          true
        )
      : 100;

    const mobileScore = networkInfo.effectiveType === '4g' ? 100
      : networkInfo.effectiveType === '3g' ? 80
      : networkInfo.effectiveType === '2g' ? 60 : 40;

    const overall = (lcpScore + fidScore + clsScore + searchScore + mobileScore) / 5;

    return {
      overall,
      lcp: lcpScore,
      fid: fidScore,
      cls: clsScore,
      search: searchScore,
      mobile: mobileScore,
    };
  }, [webVitals, performanceMetrics, networkInfo]);

  const scores = performanceScore();

  const getScoreStatus = (score: number): 'good' | 'needs-improvement' | 'poor' => {
    if (score >= 90) return 'good';
    if (score >= 70) return 'needs-improvement';
    return 'poor';
  };

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
  };

  if (!isVisible) return null;

  return (
    <div className={`fixed ${positionClasses[position]} z-50 transition-all duration-300`}>
      <div
        className={`bg-white rounded-lg shadow-lg border border-gray-200 transition-all duration-300 ${
          isExpanded ? 'w-96' : 'w-64'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">Performance</span>
            <div
              className={`w-2 h-2 rounded-full ${
                scores.overall >= 90 ? 'bg-green-500' :
                scores.overall >= 70 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
            />
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-gray-100 rounded"
              title={isExpanded ? 'Collapse' : 'Expand'}
            >
              <BarChart3 className="w-4 h-4 text-gray-600" />
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-100 rounded"
                title="Close"
              >
                <X className="w-4 h-4 text-gray-600" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-3 space-y-3">
          {/* Overall Score */}
          <div className="text-center">
            <div className={`text-2xl font-bold ${
              scores.overall >= 90 ? 'text-green-600' :
              scores.overall >= 70 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {Math.round(scores.overall)}
            </div>
            <div className="text-sm text-gray-600">Overall Score</div>
          </div>

          {/* Core Metrics */}
          <div className="grid grid-cols-2 gap-2">
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-lg font-semibold">
                {webVitals.lcp ? `${Math.round(webVitals.lcp)}ms` : '--'}
              </div>
              <div className="text-xs text-gray-600">LCP</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-lg font-semibold">
                {webVitals.fid ? `${Math.round(webVitals.fid)}ms` : '--'}
              </div>
              <div className="text-xs text-gray-600">FID</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-lg font-semibold">
                {webVitals.cls ? webVitals.cls.toFixed(3) : '--'}
              </div>
              <div className="text-xs text-gray-600">CLS</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-lg font-semibold">
                {performanceMetrics.searchLatency.length > 0
                  ? `${Math.round(performanceMetrics.searchLatency.slice(-1)[0])}ms`
                  : '--'}
              </div>
              <div className="text-xs text-gray-600">Search</div>
            </div>
          </div>

          {/* Network Info */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <Wifi className="w-4 h-4 text-gray-500" />
              <span>{networkInfo.effectiveType.toUpperCase()}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Monitor className="w-4 h-4 text-gray-500" />
              <span>{window.innerWidth}x{window.innerHeight}</span>
            </div>
          </div>

          {/* Expanded Details */}
          {isExpanded && (
            <div className="space-y-3 border-t border-gray-200 pt-3">
              {/* Web Vitals Details */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-gray-900">Core Web Vitals</h4>

                <MetricCard
                  title="LCP"
                  value={webVitals.lcp}
                  unit="ms"
                  icon={Eye}
                  status={getScoreStatus(scores.lcp)}
                  threshold={2500}
                  description="Largest Contentful Paint"
                />

                <MetricCard
                  title="FID"
                  value={webVitals.fid}
                  unit="ms"
                  icon={Zap}
                  status={getScoreStatus(scores.fid)}
                  threshold={100}
                  description="First Input Delay"
                />

                <MetricCard
                  title="CLS"
                  value={webVitals.cls}
                  unit=""
                  icon={Activity}
                  status={getScoreStatus(scores.cls)}
                  threshold={0.1}
                  description="Cumulative Layout Shift"
                />
              </div>

              {/* Performance Charts */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-gray-900">Performance Trends</h4>

                <RealTimeChart
                  data={performanceHistory.searchTimes}
                  label="Search Response Time (ms)"
                  color="#3B82F6"
                />

                <RealTimeChart
                  data={performanceHistory.memoryUsage}
                  label="Memory Usage (MB)"
                  color="#10B981"
                />

                <RealTimeChart
                  data={performanceHistory.renderTimes}
                  label="Render Time (ms)"
                  color="#F59E0B"
                />
              </div>

              {/* Recommendations */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-gray-900">Recommendations</h4>
                <div className="space-y-1">
                  {scores.overall < 90 && (
                    <div className="text-xs text-gray-600 bg-yellow-50 p-2 rounded">
                      Consider enabling performance mode for better user experience
                    </div>
                  )}
                  {networkInfo.effectiveType === '2g' && (
                    <div className="text-xs text-gray-600 bg-blue-50 p-2 rounded">
                      Slow connection detected - adaptive loading enabled
                    </div>
                  )}
                  {performanceMetrics.cacheHitRate < 0.5 && (
                    <div className="text-xs text-gray-600 bg-green-50 p-2 rounded">
                      Cache hit rate could be improved for faster searches
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

PerformanceMonitor.displayName = 'PerformanceMonitor';

export default PerformanceMonitor;