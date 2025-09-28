/**
 * FinancialReportsPage Component - Financial statements, P&L and accounting reports
 */

import React, { useState, useCallback, useEffect } from 'react';
import { DollarSign, Download, TrendingUp, PieChart } from 'lucide-react';
import { DashboardCard, commonComponentUtils } from '../../../components/admin/common';

export const FinancialReportsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState<any>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    setMetrics({
      totalRevenue: 450000000,
      totalExpenses: 320000000,
      netProfit: 130000000,
      profitMargin: 28.9
    });
    setIsLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Reports</h1>
          <p className="text-sm text-gray-500 mt-1">Financial statements, P&L and accounting reports</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
          <Download className="w-4 h-4 mr-2" />Export Reports
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <DashboardCard title="Total Revenue" value={metrics ? commonComponentUtils.formatCurrency(metrics.totalRevenue) : undefined} icon={DollarSign} theme="primary" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Total Expenses" value={metrics ? commonComponentUtils.formatCurrency(metrics.totalExpenses) : undefined} icon={TrendingUp} theme="warning" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Net Profit" value={metrics ? commonComponentUtils.formatCurrency(metrics.netProfit) : undefined} icon={TrendingUp} theme="success" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Profit Margin" value={metrics ? `${metrics.profitMargin}%` : undefined} icon={PieChart} theme="info" isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">Financial Reports Dashboard</h3>
        <p className="text-gray-500">Comprehensive financial reporting interface with P&L statements, balance sheets, cash flow reports, and accounting analytics will be implemented here.</p>
      </div>
    </div>
  );
};

export default FinancialReportsPage;