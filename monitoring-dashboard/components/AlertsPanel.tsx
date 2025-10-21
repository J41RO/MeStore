'use client';

import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  Info,
  X,
  Bell,
  CheckCircle,
} from 'lucide-react';
import { backendClient } from '@/lib/backend-client';

export type AlertSeverity = 'critical' | 'warning' | 'info';

export interface Alert {
  id: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  timestamp: Date;
  dismissed: boolean;
  source?: string;
}

interface AlertsPanelProps {
  refreshInterval?: number;
}

export default function AlertsPanel({
  refreshInterval = 10000,
}: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Generate alerts based on system health
  const generateAlerts = async (): Promise<Alert[]> => {
    const newAlerts: Alert[] = [];

    try {
      // Check health
      const health = await backendClient.healthCheck();

      if (health.uptime > 1000) {
        newAlerts.push({
          id: `health-slow-${Date.now()}`,
          severity: 'warning',
          title: 'Slow Response Time',
          message: `Health check took ${health.uptime}ms. This is above the 1000ms threshold.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'Health Check',
        });
      }

      if (health.database !== 'connected' && health.database !== 'healthy') {
        newAlerts.push({
          id: `db-disconnected-${Date.now()}`,
          severity: 'critical',
          title: 'Database Connection Issue',
          message: `Database status: ${health.database}. Immediate attention required.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'Database',
        });
      }

      if (health.redis && health.redis !== 'connected') {
        newAlerts.push({
          id: `redis-disconnected-${Date.now()}`,
          severity: 'warning',
          title: 'Redis Connection Issue',
          message: `Redis status: ${health.redis}. Cache functionality may be impaired.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'Redis',
        });
      }

      // Check API stats
      const apiStats = await backendClient.getAPIStats();

      if (apiStats.failed_5xx > 10) {
        newAlerts.push({
          id: `api-errors-${Date.now()}`,
          severity: 'critical',
          title: 'High 5xx Error Rate',
          message: `${apiStats.failed_5xx} server errors detected. System stability may be compromised.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'API Monitoring',
        });
      }

      if (apiStats.failed_4xx > 50) {
        newAlerts.push({
          id: `api-client-errors-${Date.now()}`,
          severity: 'warning',
          title: 'High 4xx Error Rate',
          message: `${apiStats.failed_4xx} client errors detected. Review API usage patterns.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'API Monitoring',
        });
      }

      if (apiStats.avg_response_time > 500) {
        newAlerts.push({
          id: `api-slow-${Date.now()}`,
          severity: 'warning',
          title: 'Slow API Response Time',
          message: `Average response time is ${Math.round(
            apiStats.avg_response_time
          )}ms. Performance optimization recommended.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'Performance',
        });
      }

      // Check Redis stats
      try {
        const redisStats = await backendClient.getRedisStats();

        if (redisStats.rate_limit_violations > 100) {
          newAlerts.push({
            id: `rate-limit-${Date.now()}`,
            severity: 'warning',
            title: 'High Rate Limit Violations',
            message: `${redisStats.rate_limit_violations} rate limit violations detected. Possible abuse or misconfiguration.`,
            timestamp: new Date(),
            dismissed: false,
            source: 'Security',
          });
        }

        if (redisStats.total_keys > 10000) {
          newAlerts.push({
            id: `redis-keys-${Date.now()}`,
            severity: 'info',
            title: 'Redis Key Count High',
            message: `Redis has ${redisStats.total_keys} keys. Consider implementing cleanup policies.`,
            timestamp: new Date(),
            dismissed: false,
            source: 'Redis',
          });
        }
      } catch {
        // Redis stats might not be available
      }

      // Check user stats
      const userStats = await backendClient.getUserStats();

      if (userStats.active_today > 1000) {
        newAlerts.push({
          id: `high-traffic-${Date.now()}`,
          severity: 'info',
          title: 'High Traffic',
          message: `${userStats.active_today} active users today. System performing well under load.`,
          timestamp: new Date(),
          dismissed: false,
          source: 'Analytics',
        });
      }
    } catch (error) {
      newAlerts.push({
        id: `monitoring-error-${Date.now()}`,
        severity: 'critical',
        title: 'Monitoring System Error',
        message: `Failed to fetch system metrics. Error: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`,
        timestamp: new Date(),
        dismissed: false,
        source: 'Monitoring',
      });
    }

    return newAlerts;
  };

  // Fetch alerts
  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const newAlerts = await generateAlerts();

      // Merge with existing alerts, keeping dismissed ones
      setAlerts((prev) => {
        const dismissedIds = prev
          .filter((a) => a.dismissed)
          .map((a) => a.id);

        // Filter out old undismissed alerts and add new ones
        const filteredNew = newAlerts.filter(
          (alert) => !dismissedIds.includes(alert.id)
        );

        return [...prev.filter((a) => a.dismissed), ...filteredNew];
      });
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Dismiss alert
  const dismissAlert = (alertId: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === alertId ? { ...alert, dismissed: true } : alert
      )
    );
  };

  // Clear all dismissed alerts
  const clearDismissed = () => {
    setAlerts((prev) => prev.filter((alert) => !alert.dismissed));
  };

  // Get icon based on severity
  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  // Get badge color based on severity
  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 dark:bg-red-900/30 border-red-200 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800';
      case 'info':
        return 'bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
  };

  // Get severity badge
  const getSeverityBadge = (severity: AlertSeverity) => {
    const colors = {
      critical: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-white',
      info: 'bg-blue-500 text-white',
    };

    return (
      <span
        className={`px-2 py-0.5 rounded-full text-xs font-semibold uppercase ${colors[severity]}`}
      >
        {severity}
      </span>
    );
  };

  const activeAlerts = alerts.filter((a) => !a.dismissed);
  const criticalCount = activeAlerts.filter(
    (a) => a.severity === 'critical'
  ).length;
  const warningCount = activeAlerts.filter(
    (a) => a.severity === 'warning'
  ).length;
  const infoCount = activeAlerts.filter((a) => a.severity === 'info').length;

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Bell className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                System Alerts
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Active: {activeAlerts.length}
              </p>
            </div>
          </div>

          {alerts.some((a) => a.dismissed) && (
            <button
              onClick={clearDismissed}
              className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
            >
              Clear Dismissed
            </button>
          )}
        </div>

        {/* Summary Badges */}
        <div className="mt-4 flex gap-3">
          {criticalCount > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm font-semibold text-red-700 dark:text-red-300">
                {criticalCount} Critical
              </span>
            </div>
          )}
          {warningCount > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-semibold text-yellow-700 dark:text-yellow-300">
                {warningCount} Warning
              </span>
            </div>
          )}
          {infoCount > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Info className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">
                {infoCount} Info
              </span>
            </div>
          )}
          {activeAlerts.length === 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm font-semibold text-green-700 dark:text-green-300">
                All Clear
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading && alerts.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            Loading alerts...
          </div>
        ) : activeAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <CheckCircle className="w-16 h-16 mb-4 text-green-500" />
            <p className="text-lg font-semibold">No Active Alerts</p>
            <p className="text-sm">System is running smoothly</p>
          </div>
        ) : (
          activeAlerts
            .sort((a, b) => {
              // Sort by severity first (critical > warning > info)
              const severityOrder = { critical: 0, warning: 1, info: 2 };
              if (severityOrder[a.severity] !== severityOrder[b.severity]) {
                return severityOrder[a.severity] - severityOrder[b.severity];
              }
              // Then by timestamp (newest first)
              return b.timestamp.getTime() - a.timestamp.getTime();
            })
            .map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border-2 ${getSeverityColor(
                  alert.severity
                )} transition-all hover:shadow-md`}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-0.5">
                    {getSeverityIcon(alert.severity)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {getSeverityBadge(alert.severity)}
                          {alert.source && (
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              [{alert.source}]
                            </span>
                          )}
                        </div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {alert.title}
                        </h3>
                      </div>
                      <button
                        onClick={() => dismissAlert(alert.id)}
                        className="flex-shrink-0 p-1 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                        title="Dismiss alert"
                      >
                        <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                      </button>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                      {alert.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {alert.timestamp.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>
            {activeAlerts.length} active alert{activeAlerts.length !== 1 ? 's' : ''}
          </span>
          <span>Updated {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}
