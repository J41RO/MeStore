/**
 * IntegrationsPage Component - Third-party integrations and API configurations
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Globe, Zap, Settings, CheckCircle } from 'lucide-react';
import { DashboardCard, StatusBadge, DataTable } from '../../../components/admin/common';

export const IntegrationsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [integrations, setIntegrations] = useState<any[]>([]);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setIntegrations([
      { id: '1', name: 'Google Analytics', type: 'Analytics', status: 'connected', lastSync: '2024-03-15' },
      { id: '2', name: 'SendGrid', type: 'Email Service', status: 'connected', lastSync: '2024-03-15' },
      { id: '3', name: 'Slack', type: 'Communication', status: 'disconnected', lastSync: null },
      { id: '4', name: 'AWS S3', type: 'Storage', status: 'connected', lastSync: '2024-03-15' }
    ]);
    setIsLoading(false);
  }, []);

  const columns = [
    { id: 'name', header: 'Integration', accessor: 'name', sortable: true },
    { id: 'type', header: 'Type', accessor: 'type', sortable: true },
    { id: 'status', header: 'Status', accessor: 'status', sortable: true, cell: (value: any) => <StatusBadge variant={value === 'connected' ? 'success' : 'warning'} size="sm">{value}</StatusBadge> },
    { id: 'lastSync', header: 'Last Sync', accessor: 'lastSync', sortable: true, cell: (value: any) => value || 'Never' }
  ];

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Integrations</h1>
        <p className="text-sm text-gray-500 mt-1">Third-party integrations and API configurations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <DashboardCard title="Total Integrations" value={integrations.length} icon={Globe} theme="primary" isLoading={isLoading} />
        <DashboardCard title="Connected" value={integrations.filter(i => i.status === 'connected').length} icon={CheckCircle} theme="success" isLoading={isLoading} />
        <DashboardCard title="Active APIs" value={3} icon={Zap} theme="info" isLoading={isLoading} />
        <DashboardCard title="Configuration Health" value="98%" icon={Settings} theme="warning" isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium">Available Integrations</h3>
        </div>
        <DataTable data={integrations} columns={columns} isLoading={isLoading} searchable={true} emptyMessage="No integrations configured." />
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">API Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">API Rate Limit</label>
            <input type="number" className="block w-full border-gray-300 rounded-md shadow-sm" placeholder="1000 requests/hour" readOnly />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Webhook URL</label>
            <input type="url" className="block w-full border-gray-300 rounded-md shadow-sm" placeholder="https://api.mestore.com/webhooks" readOnly />
          </div>
        </div>
        <p className="text-gray-500 text-sm mt-4">Advanced API configuration and webhook management interface will be implemented here.</p>
      </div>
    </div>
  );
};

export default IntegrationsPage;