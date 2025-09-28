/**
 * SalesReportsPage Component - Comprehensive sales analytics and performance reports
 */

import React, { useState, useCallback, useEffect } from 'react';
import { TrendingUp, Download, Calendar, Filter, BarChart3 } from 'lucide-react';
import { DashboardCard, DataTable, commonComponentUtils } from '../../../components/admin/common';

export const SalesReportsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState<any>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    setMetrics({
      totalSales: 345000000,
      salesGrowth: 18.5,
      topProduct: 'Samsung Galaxy A54',
      bestPeriod: 'December 2024'
    });
    setIsLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales Reports</h1>
          <p className="text-sm text-gray-500 mt-1">Comprehensive sales analytics and performance reports</p>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Filter className="w-4 h-4 mr-2" />Filters
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DashboardCard title="Total Sales" value={metrics ? commonComponentUtils.formatCurrency(metrics.totalSales) : undefined} icon={TrendingUp} theme="success" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Sales Growth" value={metrics ? `${metrics.salesGrowth}%` : undefined} icon={BarChart3} theme="info" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Top Product" value={metrics?.topProduct} icon={Calendar} theme="warning" isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">Sales Reports Interface</h3>
        <p className="text-gray-500">Advanced sales reporting interface will be implemented here with interactive charts and detailed analytics.</p>
      </div>
    </div>
  );
};

export default SalesReportsPage;