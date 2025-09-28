/**
 * CustomReportsPage Component - Create and manage custom business reports
 */

import React, { useState, useCallback, useEffect } from 'react';
import { FileText, Plus, Download, Edit } from 'lucide-react';
import { DashboardCard, DataTable } from '../../../components/admin/common';

export const CustomReportsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [reports, setReports] = useState<any[]>([]);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setReports([
      { id: '1', name: 'Monthly Vendor Performance', type: 'Vendor Analysis', lastRun: '2024-03-15', status: 'active' },
      { id: '2', name: 'Customer Behavior Analysis', type: 'Customer Insights', lastRun: '2024-03-14', status: 'scheduled' }
    ]);
    setIsLoading(false);
  }, []);

  const columns = [
    { id: 'name', header: 'Report Name', accessor: 'name', sortable: true },
    { id: 'type', header: 'Type', accessor: 'type', sortable: true },
    { id: 'lastRun', header: 'Last Run', accessor: 'lastRun', sortable: true },
    { id: 'status', header: 'Status', accessor: 'status', sortable: true }
  ];

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Custom Reports</h1>
          <p className="text-sm text-gray-500 mt-1">Create and manage custom business reports</p>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />Export All
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />New Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DashboardCard title="Total Reports" value={reports.length} icon={FileText} theme="primary" isLoading={isLoading} />
        <DashboardCard title="Active Reports" value={reports.filter(r => r.status === 'active').length} icon={Edit} theme="success" isLoading={isLoading} />
        <DashboardCard title="Scheduled Reports" value={reports.filter(r => r.status === 'scheduled').length} icon={Plus} theme="info" isLoading={isLoading} />
      </div>

      <DataTable data={reports} columns={columns} isLoading={isLoading} searchable={true} emptyMessage="No custom reports found." />
    </div>
  );
};

export default CustomReportsPage;