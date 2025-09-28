/**
 * AuthenticationLogsPage Component
 *
 * Advanced authentication monitoring and security analytics interface.
 * Provides comprehensive tracking of authentication events and security incidents.
 *
 * Features:
 * - Real-time authentication event monitoring
 * - Security threat detection and alerts
 * - Failed login attempt tracking
 * - Geographic login analysis
 * - Session management and monitoring
 * - Security audit trails
 * - Automated threat response
 * - Compliance reporting
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, {
  useState,
  useCallback,
  useMemo,
  useEffect
} from 'react';
import {
  Shield,
  Lock,
  Unlock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Globe,
  Smartphone,
  Monitor,
  Clock,
  Filter,
  Download,
  RefreshCw,
  Search,
  Activity,
  TrendingUp,
  Users,
  MapPin,
  Wifi,
  Ban,
  User
} from 'lucide-react';

import {
  DashboardCard,
  DataTable,
  StatusBadge,
  FilterPanel,
  commonComponentUtils
} from '../../../components/admin/common';

import type {
  TableColumn,
  FilterDefinition,
  ActiveFilter,
  SortConfig,
  PaginationConfig
} from '../../../components/admin/common';

/**
 * Authentication log entry interface
 */
interface AuthLog {
  id: string;
  userId: string;
  userEmail: string;
  userName: string;
  eventType: 'login_success' | 'login_failed' | 'logout' | 'password_change' | 'account_locked' | 'session_expired' | 'suspicious_activity';
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  deviceType: 'desktop' | 'mobile' | 'tablet';
  browser: string;
  location?: {
    country: string;
    city: string;
    coordinates?: [number, number];
  };
  sessionId?: string;
  riskScore: number;
  failureReason?: string;
  additionalData?: Record<string, any>;
}

/**
 * Security metrics interface
 */
interface SecurityMetrics {
  totalEvents: number;
  successfulLogins: number;
  failedLogins: number;
  suspiciousActivities: number;
  uniqueUsers: number;
  activeSessions: number;
  averageRiskScore: number;
  eventsToday: number;
  failureRate: number;
  topFailureReasons: Array<{ reason: string; count: number }>;
  topCountries: Array<{ country: string; count: number }>;
  deviceBreakdown: Array<{ device: string; count: number }>;
}

/**
 * Security alert interface
 */
interface SecurityAlert {
  id: string;
  type: 'multiple_failures' | 'suspicious_location' | 'unusual_time' | 'brute_force' | 'account_takeover';
  severity: 'low' | 'medium' | 'high' | 'critical';
  userId: string;
  userEmail: string;
  description: string;
  timestamp: string;
  isAcknowledged: boolean;
  actionTaken?: string;
}

/**
 * AuthenticationLogsPage Component
 */
export const AuthenticationLogsPage: React.FC = () => {
  // State management
  const [authLogs, setAuthLogs] = useState<AuthLog[]>([]);
  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLogs, setSelectedLogs] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [viewMode, setViewMode] = useState<'logs' | 'alerts'>('logs');

  // Pagination and sorting
  const [sort, setSort] = useState<SortConfig>({ column: 'timestamp', direction: 'desc' });
  const [pagination, setPagination] = useState<PaginationConfig>({
    page: 1,
    pageSize: 50,
    total: 0
  });

  /**
   * Authentication logs table columns
   */
  const logColumns: TableColumn<AuthLog>[] = useMemo(() => [
    {
      id: 'user',
      header: 'User',
      accessor: 'userEmail',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600" />
          </div>
          <div>
            <div className="font-medium text-gray-900">{row.userName}</div>
            <div className="text-sm text-gray-500">{value}</div>
          </div>
        </div>
      )
    },
    {
      id: 'event',
      header: 'Event',
      accessor: 'eventType',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <StatusBadge
            variant={
              value === 'login_success' ? 'success' :
              value === 'login_failed' ? 'error' :
              value === 'suspicious_activity' || value === 'account_locked' ? 'warning' :
              'info'
            }
            size="sm"
          >
            {value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </StatusBadge>
          {row.riskScore > 70 && (
            <div className="flex items-center space-x-1">
              <AlertTriangle className="w-3 h-3 text-red-500" />
              <span className="text-xs text-red-600">High Risk</span>
            </div>
          )}
        </div>
      )
    },
    {
      id: 'timestamp',
      header: 'Time',
      accessor: 'timestamp',
      sortable: true,
      cell: (value) => (
        <div className="text-sm">
          <div className="text-gray-900">
            {new Date(value).toLocaleDateString('es-CO', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
          <div className="text-gray-500">{commonComponentUtils.getRelativeTime(value)}</div>
        </div>
      )
    },
    {
      id: 'location',
      header: 'Location & Device',
      accessor: 'ipAddress',
      cell: (value, row) => (
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-900">
              {row.location ? `${row.location.city}, ${row.location.country}` : 'Unknown'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            {row.deviceType === 'mobile' && <Smartphone className="w-4 h-4 text-gray-400" />}
            {row.deviceType === 'desktop' && <Monitor className="w-4 h-4 text-gray-400" />}
            {row.deviceType === 'tablet' && <Monitor className="w-4 h-4 text-gray-400" />}
            <span className="text-sm text-gray-500">
              {row.browser} • {value}
            </span>
          </div>
        </div>
      )
    },
    {
      id: 'riskScore',
      header: 'Risk Score',
      accessor: 'riskScore',
      sortable: true,
      align: 'center',
      cell: (value) => (
        <div className="flex items-center justify-center">
          <div className={`px-2 py-1 text-xs font-medium rounded-full ${
            value >= 80 ? 'bg-red-100 text-red-800' :
            value >= 60 ? 'bg-orange-100 text-orange-800' :
            value >= 40 ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {value}/100
          </div>
        </div>
      )
    },
    {
      id: 'session',
      header: 'Session',
      accessor: 'sessionId',
      hideOnMobile: true,
      cell: (value, row) => (
        <div className="text-sm">
          {value ? (
            <div>
              <div className="text-gray-900 font-mono text-xs">
                {value.substring(0, 8)}...
              </div>
              {row.eventType === 'login_success' && (
                <StatusBadge variant="active" size="xs">Active</StatusBadge>
              )}
            </div>
          ) : (
            <span className="text-gray-400">No session</span>
          )}
        </div>
      )
    }
  ], []);

  /**
   * Security alerts table columns
   */
  const alertColumns: TableColumn<SecurityAlert>[] = useMemo(() => [
    {
      id: 'alert',
      header: 'Alert',
      accessor: 'type',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-start space-x-3">
          <div className={`w-2 h-2 rounded-full mt-2 ${
            row.severity === 'critical' ? 'bg-red-500' :
            row.severity === 'high' ? 'bg-orange-500' :
            row.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
          }`} />
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">
                {value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              <StatusBadge
                variant={
                  row.severity === 'critical' ? 'error' :
                  row.severity === 'high' ? 'warning' :
                  row.severity === 'medium' ? 'info' : 'default'
                }
                size="xs"
              >
                {row.severity.toUpperCase()}
              </StatusBadge>
            </div>
            <p className="text-sm text-gray-500 mt-1">{row.description}</p>
          </div>
        </div>
      )
    },
    {
      id: 'user',
      header: 'Affected User',
      accessor: 'userEmail',
      sortable: true,
      cell: (value) => (
        <div className="text-sm">
          <div className="text-gray-900">{value}</div>
        </div>
      )
    },
    {
      id: 'timestamp',
      header: 'Time',
      accessor: 'timestamp',
      sortable: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">
          {commonComponentUtils.getRelativeTime(value)}
        </span>
      )
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'isAcknowledged',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <StatusBadge variant={value ? 'success' : 'warning'} size="sm">
            {value ? 'Acknowledged' : 'Pending'}
          </StatusBadge>
          {row.actionTaken && (
            <div className="text-xs text-gray-500">{row.actionTaken}</div>
          )}
        </div>
      )
    }
  ], []);

  /**
   * Row actions for logs
   */
  const logActions = useMemo(() => [
    {
      id: 'view',
      label: 'View Details',
      icon: Eye,
      action: (log: AuthLog) => {
        console.log('View log details:', log.id);
      }
    },
    {
      id: 'block-ip',
      label: 'Block IP Address',
      icon: Ban,
      variant: 'danger' as const,
      action: (log: AuthLog) => {
        if (confirm(`Block IP address ${log.ipAddress}?`)) {
          handleBlockIP(log.ipAddress);
        }
      },
      hidden: (log: AuthLog) => log.eventType === 'login_success' && log.riskScore < 70
    }
  ], []);

  /**
   * Row actions for alerts
   */
  const alertActions = useMemo(() => [
    {
      id: 'acknowledge',
      label: 'Acknowledge',
      icon: CheckCircle,
      action: (alert: SecurityAlert) => {
        handleAcknowledgeAlert(alert.id);
      },
      hidden: (alert: SecurityAlert) => alert.isAcknowledged
    },
    {
      id: 'investigate',
      label: 'Investigate',
      icon: Search,
      action: (alert: SecurityAlert) => {
        console.log('Investigate alert:', alert.id);
      }
    }
  ], []);

  /**
   * Filter definitions for logs
   */
  const logFilterDefinitions: FilterDefinition[] = useMemo(() => [
    {
      id: 'eventType',
      label: 'Event Type',
      type: 'select',
      field: 'eventType',
      options: [
        { value: 'login_success', label: 'Successful Login' },
        { value: 'login_failed', label: 'Failed Login' },
        { value: 'logout', label: 'Logout' },
        { value: 'password_change', label: 'Password Change' },
        { value: 'account_locked', label: 'Account Locked' },
        { value: 'session_expired', label: 'Session Expired' },
        { value: 'suspicious_activity', label: 'Suspicious Activity' }
      ]
    },
    {
      id: 'riskScore',
      label: 'Risk Score',
      type: 'numberrange',
      field: 'riskScore',
      min: 0,
      max: 100
    },
    {
      id: 'deviceType',
      label: 'Device Type',
      type: 'select',
      field: 'deviceType',
      options: [
        { value: 'desktop', label: 'Desktop' },
        { value: 'mobile', label: 'Mobile' },
        { value: 'tablet', label: 'Tablet' }
      ]
    },
    {
      id: 'country',
      label: 'Country',
      type: 'text',
      field: 'location.country'
    },
    {
      id: 'ipAddress',
      label: 'IP Address',
      type: 'text',
      field: 'ipAddress'
    },
    {
      id: 'timestamp',
      label: 'Time Range',
      type: 'daterange',
      field: 'timestamp'
    }
  ], []);

  /**
   * Filter definitions for alerts
   */
  const alertFilterDefinitions: FilterDefinition[] = useMemo(() => [
    {
      id: 'type',
      label: 'Alert Type',
      type: 'select',
      field: 'type',
      options: [
        { value: 'multiple_failures', label: 'Multiple Failures' },
        { value: 'suspicious_location', label: 'Suspicious Location' },
        { value: 'unusual_time', label: 'Unusual Time' },
        { value: 'brute_force', label: 'Brute Force' },
        { value: 'account_takeover', label: 'Account Takeover' }
      ]
    },
    {
      id: 'severity',
      label: 'Severity',
      type: 'select',
      field: 'severity',
      options: [
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' }
      ]
    },
    {
      id: 'isAcknowledged',
      label: 'Status',
      type: 'boolean',
      field: 'isAcknowledged'
    }
  ], []);

  /**
   * Load data
   */
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API calls
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock data
      const mockLogs: AuthLog[] = [
        {
          id: '1',
          userId: 'user1',
          userEmail: 'admin@mestocker.com',
          userName: 'Admin User',
          eventType: 'login_success',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          ipAddress: '192.168.1.100',
          userAgent: 'Mozilla/5.0...',
          deviceType: 'desktop',
          browser: 'Chrome 119',
          location: { country: 'Colombia', city: 'Bogotá' },
          sessionId: 'sess_abc123456789',
          riskScore: 25
        },
        {
          id: '2',
          userId: 'user2',
          userEmail: 'suspicious@example.com',
          userName: 'Unknown User',
          eventType: 'login_failed',
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          ipAddress: '187.123.45.67',
          userAgent: 'Bot/1.0',
          deviceType: 'desktop',
          browser: 'Unknown',
          location: { country: 'Unknown', city: 'Unknown' },
          riskScore: 85,
          failureReason: 'Invalid credentials'
        },
        {
          id: '3',
          userId: 'user3',
          userEmail: 'manager@mestocker.com',
          userName: 'Maria Rodriguez',
          eventType: 'login_success',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          ipAddress: '10.0.1.50',
          userAgent: 'Mobile Safari',
          deviceType: 'mobile',
          browser: 'Safari 17',
          location: { country: 'Colombia', city: 'Medellín' },
          sessionId: 'sess_def987654321',
          riskScore: 15
        },
        {
          id: '4',
          userId: 'user4',
          userEmail: 'test@example.com',
          userName: 'Test User',
          eventType: 'suspicious_activity',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          ipAddress: '203.45.67.89',
          userAgent: 'Automated Tool',
          deviceType: 'desktop',
          browser: 'Unknown',
          location: { country: 'Russia', city: 'Moscow' },
          riskScore: 95
        }
      ];

      const mockAlerts: SecurityAlert[] = [
        {
          id: '1',
          type: 'brute_force',
          severity: 'high',
          userId: 'user2',
          userEmail: 'suspicious@example.com',
          description: 'Multiple failed login attempts detected from same IP address',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          isAcknowledged: false
        },
        {
          id: '2',
          type: 'suspicious_location',
          severity: 'medium',
          userId: 'user3',
          userEmail: 'manager@mestocker.com',
          description: 'Login from unusual geographic location detected',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          isAcknowledged: true,
          actionTaken: 'User verified via 2FA'
        }
      ];

      const mockMetrics: SecurityMetrics = {
        totalEvents: mockLogs.length,
        successfulLogins: mockLogs.filter(l => l.eventType === 'login_success').length,
        failedLogins: mockLogs.filter(l => l.eventType === 'login_failed').length,
        suspiciousActivities: mockLogs.filter(l => l.eventType === 'suspicious_activity' || l.riskScore > 70).length,
        uniqueUsers: new Set(mockLogs.map(l => l.userId)).size,
        activeSessions: mockLogs.filter(l => l.sessionId).length,
        averageRiskScore: Math.round(mockLogs.reduce((sum, l) => sum + l.riskScore, 0) / mockLogs.length),
        eventsToday: mockLogs.filter(l => new Date(l.timestamp).toDateString() === new Date().toDateString()).length,
        failureRate: 25,
        topFailureReasons: [
          { reason: 'Invalid credentials', count: 5 },
          { reason: 'Account locked', count: 2 }
        ],
        topCountries: [
          { country: 'Colombia', count: 8 },
          { country: 'Unknown', count: 2 }
        ],
        deviceBreakdown: [
          { device: 'Desktop', count: 6 },
          { device: 'Mobile', count: 3 },
          { device: 'Tablet', count: 1 }
        ]
      };

      setAuthLogs(mockLogs);
      setSecurityAlerts(mockAlerts);
      setMetrics(mockMetrics);
      setPagination(prev => ({ ...prev, total: mockLogs.length }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load authentication data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle block IP
   */
  const handleBlockIP = useCallback(async (ipAddress: string) => {
    try {
      // TODO: Replace with actual API call
      console.log('Blocking IP:', ipAddress);
    } catch (err) {
      console.error('Failed to block IP:', err);
    }
  }, []);

  /**
   * Handle acknowledge alert
   */
  const handleAcknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      // TODO: Replace with actual API call
      setSecurityAlerts(prev => prev.map(alert =>
        alert.id === alertId ? { ...alert, isAcknowledged: true } : alert
      ));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  }, []);

  /**
   * Get current data based on view mode
   */
  const currentData = useMemo(() => {
    return viewMode === 'logs' ? authLogs : securityAlerts;
  }, [viewMode, authLogs, securityAlerts]);

  /**
   * Get current columns based on view mode
   */
  const currentColumns = useMemo(() => {
    return viewMode === 'logs' ? logColumns : alertColumns;
  }, [viewMode, logColumns, alertColumns]);

  /**
   * Get current actions based on view mode
   */
  const currentActions = useMemo(() => {
    return viewMode === 'logs' ? logActions : alertActions;
  }, [viewMode, logActions, alertActions]);

  /**
   * Get current filter definitions based on view mode
   */
  const currentFilterDefinitions = useMemo(() => {
    return viewMode === 'logs' ? logFilterDefinitions : alertFilterDefinitions;
  }, [viewMode, logFilterDefinitions, alertFilterDefinitions]);

  /**
   * Load data on mount
   */
  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Authentication Logs</h1>
          <p className="text-sm text-gray-500 mt-1">
            Monitor authentication events and security incidents
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              type="button"
              onClick={() => setViewMode('logs')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'logs'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Activity className="w-4 h-4 mr-1 inline" />
              Logs
            </button>
            <button
              type="button"
              onClick={() => setViewMode('alerts')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'alerts'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <AlertTriangle className="w-4 h-4 mr-1 inline" />
              Alerts ({securityAlerts.filter(a => !a.isAcknowledged).length})
            </button>
          </div>

          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>

          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Events"
          value={metrics?.totalEvents}
          icon={Activity}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Success Rate"
          value={metrics ? `${100 - metrics.failureRate}%` : undefined}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Suspicious Activities"
          value={metrics?.suspiciousActivities}
          icon={AlertTriangle}
          theme="warning"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Active Sessions"
          value={metrics?.activeServices}
          icon={Users}
          theme="info"
          isLoading={isLoading}
        />
      </div>

      {/* Main Content */}
      <div className="flex gap-6">
        {/* Filter Panel */}
        {showFilters && (
          <div className="w-80">
            <FilterPanel
              filterDefinitions={currentFilterDefinitions}
              activeFilters={activeFilters}
              isOpen={showFilters}
              onFiltersChange={setActiveFilters}
              onClose={() => setShowFilters(false)}
              title={`${viewMode === 'logs' ? 'Log' : 'Alert'} Filters`}
            />
          </div>
        )}

        {/* Data Table */}
        <div className="flex-1">
          <DataTable
            data={currentData}
            columns={currentColumns}
            isLoading={isLoading}
            error={error}
            pagination={viewMode === 'logs' ? pagination : undefined}
            sort={sort}
            selectedRows={selectedLogs}
            getRowId={(item) => item.id}
            rowActions={currentActions}
            searchable={true}
            searchPlaceholder={`Search ${viewMode}...`}
            selectable={false}
            onSort={setSort}
            onPageChange={viewMode === 'logs' ? (page) => setPagination(prev => ({ ...prev, page })) : undefined}
            onPageSizeChange={viewMode === 'logs' ? (pageSize) => setPagination(prev => ({ ...prev, pageSize })) : undefined}
            onRowSelect={setSelectedLogs}
            onRefresh={loadData}
            emptyMessage={`No ${viewMode} found.`}
          />
        </div>
      </div>
    </div>
  );
};

/**
 * Default export
 */
export default AuthenticationLogsPage;