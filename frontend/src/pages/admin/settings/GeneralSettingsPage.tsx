/**
 * GeneralSettingsPage Component - Core system settings and configuration management
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Settings, Save, RefreshCw, Globe, Bell } from 'lucide-react';
import { DashboardCard } from '../../../components/admin/common';

export const GeneralSettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setSettings({
      siteName: 'MeStore Marketplace',
      siteDescription: 'Premier Colombian marketplace platform',
      timezone: 'America/Bogota',
      language: 'es-CO',
      maintenanceMode: false
    });
    setIsLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">General Settings</h1>
          <p className="text-sm text-gray-500 mt-1">Core system settings and configuration management</p>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <RefreshCw className="w-4 h-4 mr-2" />Reset
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <Save className="w-4 h-4 mr-2" />Save Changes
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DashboardCard title="Site Name" value={settings?.siteName} icon={Globe} theme="primary" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Timezone" value={settings?.timezone} icon={Settings} theme="info" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Language" value={settings?.language} icon={Bell} theme="success" isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">System Configuration</h3>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Site Name</label>
              <input type="text" className="mt-1 block w-full border-gray-300 rounded-md shadow-sm" value={settings?.siteName || ''} readOnly />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Timezone</label>
              <select className="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                <option value="America/Bogota">America/Bogota</option>
                <option value="America/Medellin">America/Medellin</option>
              </select>
            </div>
          </div>
          <p className="text-gray-500 text-sm">Advanced configuration forms will be implemented here with validation and real-time preview.</p>
        </div>
      </div>
    </div>
  );
};

export default GeneralSettingsPage;