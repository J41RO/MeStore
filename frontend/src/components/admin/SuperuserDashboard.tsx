import React, { useState, useEffect } from 'react';
import { superuserService, SuperuserDashboardStats } from '../../services/superuserService';

interface DashboardCardProps {
  title: string;
  value: number | string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon: string;
  color: 'blue' | 'green' | 'yellow' | 'purple' | 'red';
  description?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  color,
  description,
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-500 text-blue-900',
    green: 'bg-green-50 border-green-500 text-green-900',
    yellow: 'bg-yellow-50 border-yellow-500 text-yellow-900',
    purple: 'bg-purple-50 border-purple-500 text-purple-900',
    red: 'bg-red-50 border-red-500 text-red-900',
  };

  const changeColorClasses = {
    increase: 'text-green-600 bg-green-100',
    decrease: 'text-red-600 bg-red-100',
    neutral: 'text-gray-600 bg-gray-100',
  };

  const changeIcons = {
    increase: '↗',
    decrease: '↘',
    neutral: '→',
  };

  return (
    <div className={`p-6 rounded-lg border-l-4 shadow-sm ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {description && (
            <p className="text-sm opacity-60 mt-1">{description}</p>
          )}
        </div>
        <div className="text-4xl opacity-20">{icon}</div>
      </div>
      {change !== undefined && (
        <div className="mt-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${changeColorClasses[changeType]}`}>
            {changeIcons[changeType]} {Math.abs(change)}%
          </span>
          <span className="text-xs text-gray-500 ml-2">vs last period</span>
        </div>
      )}
    </div>
  );
};

interface ActivityChartProps {
  data: { date: string; newUsers: number; activeUsers: number }[];
}

const ActivityChart: React.FC<ActivityChartProps> = ({ data }) => {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <p>No activity data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.flatMap(d => [d.newUsers, d.activeUsers]));

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
          <span>New Users</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
          <span>Active Users</span>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2 h-48">
        {data.map((day, index) => {
          const newUsersHeight = (day.newUsers / maxValue) * 100;
          const activeUsersHeight = (day.activeUsers / maxValue) * 100;

          return (
            <div key={index} className="flex flex-col justify-end items-center space-y-1">
              <div className="flex flex-col justify-end items-center w-full h-32 space-y-1">
                <div
                  className="w-4 bg-green-500 rounded-t"
                  style={{ height: `${activeUsersHeight}%` }}
                  title={`${day.activeUsers} active users`}
                ></div>
                <div
                  className="w-4 bg-blue-500 rounded-t"
                  style={{ height: `${newUsersHeight}%` }}
                  title={`${day.newUsers} new users`}
                ></div>
              </div>
              <span className="text-xs text-gray-600 transform -rotate-45 origin-bottom-left">
                {new Date(day.date).getDate()}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const SuperuserDashboard: React.FC = () => {
  const [stats, setStats] = useState<SuperuserDashboardStats>({
    totalUsers: 0,
    activeUsers: 0,
    verifiedUsers: 0,
    usersByType: { BUYER: 0, VENDOR: 0, ADMIN: 0, SUPERUSER: 0 },
    recentActivity: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      const dashboardStats = await superuserService.getDashboardStats();
      setStats(dashboardStats);
      setError(null);
    } catch (err) {
      setError('Error loading dashboard statistics');
      console.error('Dashboard stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="text-red-500 mr-3">⚠</div>
          <div>
            <h3 className="text-lg font-medium text-red-900">Error Loading Dashboard</h3>
            <p className="text-red-700 mt-1">{error}</p>
            <button
              onClick={loadDashboardStats}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const activeUserPercentage = stats.totalUsers > 0
    ? Math.round((stats.activeUsers / stats.totalUsers) * 100)
    : 0;

  const verifiedUserPercentage = stats.totalUsers > 0
    ? Math.round((stats.verifiedUsers / stats.totalUsers) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Superuser Dashboard</h1>
          <p className="text-gray-600 mt-1">Complete system overview and user management</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={loadDashboardStats}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            🔄 Refresh
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
            📊 Export Report
          </button>
        </div>
      </div>

      {/* Main Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard
          title="Total Users"
          value={stats.totalUsers.toLocaleString()}
          change={5.2}
          changeType="increase"
          icon="👥"
          color="blue"
          description="All registered users"
        />
        <DashboardCard
          title="Active Users"
          value={stats.activeUsers.toLocaleString()}
          change={activeUserPercentage}
          changeType="increase"
          icon="✅"
          color="green"
          description={`${activeUserPercentage}% of total users`}
        />
        <DashboardCard
          title="Verified Users"
          value={stats.verifiedUsers.toLocaleString()}
          icon="🔒"
          color="yellow"
          description={`${verifiedUserPercentage}% verified`}
        />
        <DashboardCard
          title="Pending Issues"
          value="3"
          change={-25}
          changeType="decrease"
          icon="⚠"
          color="red"
          description="Requiring attention"
        />
      </div>

      {/* User Types Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Users by Type</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">🛒</span>
                <div>
                  <p className="font-medium text-gray-900">Buyers</p>
                  <p className="text-sm text-gray-600">Customer accounts</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600">{stats.usersByType.BUYER}</p>
                <p className="text-sm text-gray-500">
                  {stats.totalUsers > 0 ? Math.round((stats.usersByType.BUYER / stats.totalUsers) * 100) : 0}%
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">🏪</span>
                <div>
                  <p className="font-medium text-gray-900">Vendors</p>
                  <p className="text-sm text-gray-600">Seller accounts</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-green-600">{stats.usersByType.VENDOR}</p>
                <p className="text-sm text-gray-500">
                  {stats.totalUsers > 0 ? Math.round((stats.usersByType.VENDOR / stats.totalUsers) * 100) : 0}%
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">⚙</span>
                <div>
                  <p className="font-medium text-gray-900">Admins</p>
                  <p className="text-sm text-gray-600">Administrator accounts</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-purple-600">{stats.usersByType.ADMIN}</p>
                <p className="text-sm text-gray-500">
                  {stats.totalUsers > 0 ? Math.round((stats.usersByType.ADMIN / stats.totalUsers) * 100) : 0}%
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">👑</span>
                <div>
                  <p className="font-medium text-gray-900">Superusers</p>
                  <p className="text-sm text-gray-600">Super administrator accounts</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-red-600">{stats.usersByType.SUPERUSER}</p>
                <p className="text-sm text-gray-500">
                  {stats.totalUsers > 0 ? Math.round((stats.usersByType.SUPERUSER / stats.totalUsers) * 100) : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Chart */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <ActivityChart data={stats.recentActivity} />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <span className="text-2xl mr-3">👤</span>
            <div className="text-left">
              <p className="font-medium text-blue-900">Create User</p>
              <p className="text-sm text-blue-700">Add new user account</p>
            </div>
          </button>

          <button className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <span className="text-2xl mr-3">📊</span>
            <div className="text-left">
              <p className="font-medium text-green-900">View Reports</p>
              <p className="text-sm text-green-700">System analytics</p>
            </div>
          </button>

          <button className="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
            <span className="text-2xl mr-3">⚠</span>
            <div className="text-left">
              <p className="font-medium text-yellow-900">Review Issues</p>
              <p className="text-sm text-yellow-700">Pending problems</p>
            </div>
          </button>

          <button className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <span className="text-2xl mr-3">🔧</span>
            <div className="text-left">
              <p className="font-medium text-purple-900">System Settings</p>
              <p className="text-sm text-purple-700">Configure system</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuperuserDashboard;