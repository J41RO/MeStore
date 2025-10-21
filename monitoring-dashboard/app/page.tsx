'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  Users,
  Database,
  Server,
  AlertTriangle,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import LogsPanel from '@/components/LogsPanel';
import MetricsChart from '@/components/MetricsChart';
import AlertsPanel from '@/components/AlertsPanel';
import TestingPanel from '@/components/TestingPanel';

interface DashboardStats {
  users?: {
    total: number;
    vendors: number;
    buyers: number;
    admins: number;
    active_today: number;
  };
  auth?: {
    login_attempts_success: number;
    login_attempts_failed: number;
    oauth_google_callbacks: number;
    active_tokens: number;
    blacklisted_tokens: number;
  };
  api?: {
    total_requests: number;
    successful_requests: number;
    failed_4xx: number;
    failed_5xx: number;
    avg_response_time: number;
  };
  redis?: {
    total_keys: number;
    memory_used: string;
    blacklisted_tokens: number;
    rate_limit_violations: number;
  };
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({});
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState<number>(5000);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    fetchStats();

    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  async function fetchStats() {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();

      setStats(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-400" />
            System Monitoring Dashboard
          </h1>
          <p className="text-gray-400 mt-1">
            Real-time monitoring and analytics for MeStore backend
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs text-gray-400">Last update</p>
            <p className="text-sm text-gray-300 font-medium">
              {lastUpdate.toLocaleTimeString()}
            </p>
          </div>

          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="5000">Refresh: 5s</option>
            <option value="10000">Refresh: 10s</option>
            <option value="30000">Refresh: 30s</option>
            <option value="60000">Refresh: 60s</option>
            <option value="0">Manual</option>
          </select>

          <button
            onClick={fetchStats}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Refresh Now
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Users Stats */}
        <StatsCard
          title="Total Users"
          value={stats.users?.total || 0}
          icon={<Users className="w-6 h-6" />}
          color="blue"
          subtitle={`${stats.users?.active_today || 0} active today`}
          loading={loading}
        />

        {/* API Stats */}
        <StatsCard
          title="API Requests"
          value={stats.api?.total_requests || 0}
          icon={<Server className="w-6 h-6" />}
          color="green"
          subtitle={`${stats.api?.avg_response_time || 0}ms avg`}
          loading={loading}
        />

        {/* Auth Stats */}
        <StatsCard
          title="Active Sessions"
          value={stats.auth?.active_tokens || 0}
          icon={<CheckCircle className="w-6 h-6" />}
          color="purple"
          subtitle={`${stats.auth?.login_attempts_success || 0} logins today`}
          loading={loading}
        />

        {/* Redis Stats */}
        <StatsCard
          title="Redis Keys"
          value={stats.redis?.total_keys || 0}
          icon={<Database className="w-6 h-6" />}
          color="orange"
          subtitle={stats.redis?.memory_used || '0 MB'}
          loading={loading}
        />
      </div>

      {/* Detailed Stats Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Breakdown */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-400" />
            User Breakdown
          </h3>

          <div className="space-y-3">
            <MetricRow
              label="Vendors"
              value={stats.users?.vendors || 0}
              total={stats.users?.total || 1}
              color="blue"
            />
            <MetricRow
              label="Buyers"
              value={stats.users?.buyers || 0}
              total={stats.users?.total || 1}
              color="green"
            />
            <MetricRow
              label="Admins"
              value={stats.users?.admins || 0}
              total={stats.users?.total || 1}
              color="purple"
            />
          </div>
        </div>

        {/* API Health */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-green-400" />
            API Health
          </h3>

          <div className="space-y-3">
            <MetricRow
              label="Successful"
              value={stats.api?.successful_requests || 0}
              total={stats.api?.total_requests || 1}
              color="green"
              icon={<CheckCircle className="w-4 h-4" />}
            />
            <MetricRow
              label="Client Errors (4xx)"
              value={stats.api?.failed_4xx || 0}
              total={stats.api?.total_requests || 1}
              color="yellow"
              icon={<AlertTriangle className="w-4 h-4" />}
            />
            <MetricRow
              label="Server Errors (5xx)"
              value={stats.api?.failed_5xx || 0}
              total={stats.api?.total_requests || 1}
              color="red"
              icon={<XCircle className="w-4 h-4" />}
            />
          </div>
        </div>
      </div>

      {/* Charts and Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MetricsChart />
        </div>
        <div>
          <AlertsPanel />
        </div>
      </div>

      {/* Logs and Testing */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <LogsPanel />
        </div>
        <div>
          <TestingPanel />
        </div>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  icon,
  color,
  subtitle,
  loading,
}: {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
  loading?: boolean;
}) {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    green: 'text-green-400 bg-green-500/10 border-green-500/20',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    orange: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  }[color];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-400">{title}</h3>
        <div className={`p-2 rounded-lg border ${colorClasses}`}>{icon}</div>
      </div>

      {loading ? (
        <div className="h-8 bg-gray-700 rounded animate-pulse"></div>
      ) : (
        <>
          <p className="text-3xl font-bold text-white mb-1">
            {value.toLocaleString()}
          </p>
          {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
        </>
      )}
    </div>
  );
}

function MetricRow({
  label,
  value,
  total,
  color,
  icon,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
  icon?: React.ReactNode;
}) {
  const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  }[color];

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-300 flex items-center gap-2">
          {icon}
          {label}
        </span>
        <span className="text-sm font-medium text-white">
          {value.toLocaleString()} ({percentage}%)
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`${colorClasses} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
