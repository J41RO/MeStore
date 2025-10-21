'use client';

import { useEffect, useState } from 'react';
import { Database, Users, UserCheck, Shield, Activity } from 'lucide-react';

interface UserData {
  id: string;
  email: string;
  user_type: string;
  created_at: string;
}

export default function DatabasePage() {
  const [stats, setStats] = useState<any>(null);
  const [recentUsers, setRecentUsers] = useState<UserData[]>([]);
  const [sqlQuery, setSqlQuery] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatabaseStats();
  }, []);

  async function fetchDatabaseStats() {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();

      setStats(data.users);
      setRecentUsers(data.users?.recent_users || []);
    } catch (error) {
      console.error('Error fetching database stats:', error);
    } finally {
      setLoading(false);
    }
  }

  async function executeQuery() {
    if (!sqlQuery.trim()) return;

    try {
      // Esta funcionalidad requeriría un endpoint backend adicional
      // Por ahora mostramos un mensaje informativo
      setQueryResult({
        message: 'Query execution requires backend endpoint /api/v1/monitoring/query',
        query: sqlQuery,
      });
    } catch (error) {
      console.error('Error executing query:', error);
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-400" />
            Database Administration
          </h1>
          <p className="text-gray-400 mt-1">
            Monitor and manage PostgreSQL database
          </p>
        </div>

        <button
          onClick={fetchDatabaseStats}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Refresh Stats
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={stats?.total || 0}
          icon={<Users className="w-6 h-6 text-blue-400" />}
          loading={loading}
        />

        <StatCard
          title="Vendors"
          value={stats?.vendors || 0}
          icon={<UserCheck className="w-6 h-6 text-green-400" />}
          loading={loading}
        />

        <StatCard
          title="Buyers"
          value={stats?.buyers || 0}
          icon={<Users className="w-6 h-6 text-purple-400" />}
          loading={loading}
        />

        <StatCard
          title="Admins"
          value={stats?.admins || 0}
          icon={<Shield className="w-6 h-6 text-orange-400" />}
          loading={loading}
        />
      </div>

      {/* Recent Users Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            Recent Users (Last 10)
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Created At
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  ID
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {recentUsers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-400">
                    No recent users found
                  </td>
                </tr>
              ) : (
                recentUsers.map((user) => (
                  <tr
                    key={user.id}
                    className="hover:bg-gray-700/30 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-300">{user.email}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.user_type === 'VENDOR'
                            ? 'bg-green-500/10 text-green-400'
                            : user.user_type === 'ADMIN'
                            ? 'bg-orange-500/10 text-orange-400'
                            : 'bg-blue-500/10 text-blue-400'
                        }`}
                      >
                        {user.user_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(user.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-xs text-gray-500 bg-gray-900/50 px-2 py-1 rounded">
                        {user.id.slice(0, 8)}...
                      </code>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* SQL Query Panel */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Custom SQL Query</h2>
          <p className="text-sm text-gray-400 mt-1">
            Execute custom SQL queries (read-only recommended)
          </p>
        </div>

        <div className="p-6 space-y-4">
          <textarea
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            placeholder="SELECT * FROM users LIMIT 10;"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-300 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px]"
          />

          <div className="flex items-center justify-between">
            <button
              onClick={executeQuery}
              disabled={!sqlQuery.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Execute Query
            </button>

            <div className="text-sm text-yellow-500 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              <span>Requires backend endpoint configuration</span>
            </div>
          </div>

          {queryResult && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
              <pre className="text-sm text-gray-300 overflow-x-auto">
                {JSON.stringify(queryResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Database Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Connection Info
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Database Type:</span>
              <span className="text-gray-300 font-medium">PostgreSQL</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Environment:</span>
              <span className="text-gray-300 font-medium">
                {process.env.NODE_ENV}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Status:</span>
              <span className="text-green-400 font-medium">Connected</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Quick Actions
          </h3>
          <div className="space-y-2">
            <button className="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-left">
              View Active Connections
            </button>
            <button className="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-left">
              Export User Data
            </button>
            <button className="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-left">
              Database Backup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  loading,
}: {
  title: string;
  value: number;
  icon: React.ReactNode;
  loading?: boolean;
}) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-400">{title}</h3>
        {icon}
      </div>

      {loading ? (
        <div className="h-8 bg-gray-700 rounded animate-pulse"></div>
      ) : (
        <p className="text-3xl font-bold text-white">{value.toLocaleString()}</p>
      )}
    </div>
  );
}
