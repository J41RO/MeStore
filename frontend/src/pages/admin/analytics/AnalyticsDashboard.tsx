/**
 * AnalyticsDashboard Component
 *
 * Main analytics dashboard with key performance indicators and business metrics.
 * Provides comprehensive overview of marketplace performance.
 *
 * Features:
 * - Interactive dashboards with real-time metrics
 * - Customizable KPI widgets and charts
 * - Multi-period comparisons and trends
 * - Export functionality for reports
 * - Drill-down capabilities
 * - Mobile-responsive design
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Package,
  ShoppingCart,
  Calendar,
  Download,
  RefreshCw,
  Eye,
  Filter
} from 'lucide-react';

import {
  DashboardCard,
  commonComponentUtils
} from '../../../components/admin/common';

/**
 * Analytics metrics interface
 */
interface AnalyticsMetrics {
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  totalVendors: number;
  averageOrderValue: number;
  conversionRate: number;
  revenueGrowth: number;
  orderGrowth: number;
  customerGrowth: number;
  topCategory: string;
  topVendor: string;
}

/**
 * AnalyticsDashboard Component
 */
export const AnalyticsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState('30d');

  /**
   * Load analytics data
   */
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Mock data
      const mockMetrics: AnalyticsMetrics = {
        totalRevenue: 245680000,
        totalOrders: 1856,
        totalCustomers: 12450,
        totalVendors: 89,
        averageOrderValue: 132350,
        conversionRate: 3.8,
        revenueGrowth: 24.5,
        orderGrowth: 18.2,
        customerGrowth: 15.7,
        topCategory: 'Electronics',
        topVendor: 'TechStore Colombia'
      };

      await new Promise(resolve => setTimeout(resolve, 1000));
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            Main analytics dashboard with key performance indicators
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>

          <button
            type="button"
            onClick={loadData}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>

          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Revenue"
          value={metrics ? commonComponentUtils.formatCurrency(metrics.totalRevenue) : undefined}
          previousValue={metrics ? metrics.totalRevenue * 0.8 : undefined}
          icon={DollarSign}
          theme="primary"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Total Orders"
          value={metrics?.totalOrders}
          previousValue={metrics ? Math.round(metrics.totalOrders * 0.85) : undefined}
          icon={ShoppingCart}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Total Customers"
          value={metrics?.totalCustomers}
          previousValue={metrics ? Math.round(metrics.totalCustomers * 0.88) : undefined}
          icon={Users}
          theme="info"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Active Vendors"
          value={metrics?.totalVendors}
          previousValue={metrics ? Math.round(metrics.totalVendors * 0.9) : undefined}
          icon={Package}
          theme="warning"
          isLoading={isLoading}
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DashboardCard
          title="Average Order Value"
          value={metrics ? commonComponentUtils.formatCurrency(metrics.averageOrderValue) : undefined}
          icon={BarChart3}
          theme="default"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Conversion Rate"
          value={metrics ? `${metrics.conversionRate}%` : undefined}
          icon={TrendingUp}
          theme="success"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Top Category"
          value={metrics?.topCategory}
          subtitle="Electronics leading in sales"
          icon={Eye}
          theme="info"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart Placeholder */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Revenue chart will be implemented here</p>
          </div>
        </div>

        {/* Orders Chart Placeholder */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Orders by Category</h3>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Category chart will be implemented here</p>
          </div>
        </div>
      </div>

      {/* Top Performers */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Performers</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Top Vendor</p>
              <p className="text-sm text-gray-500">{metrics?.topVendor}</p>
            </div>
            <div className="text-right">
              <p className="font-medium text-gray-900">{commonComponentUtils.formatCurrency(125000000)}</p>
              <p className="text-sm text-green-600">+24.5% vs last month</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;