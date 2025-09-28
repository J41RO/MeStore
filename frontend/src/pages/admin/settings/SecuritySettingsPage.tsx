/**
 * SecuritySettingsPage Component - Security policies, authentication and access control
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Shield, Lock, Key, AlertTriangle } from 'lucide-react';
import { DashboardCard, StatusBadge } from '../../../components/admin/common';

export const SecuritySettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setSettings({
      twoFactorEnabled: true,
      passwordPolicy: 'strict',
      sessionTimeout: 30,
      loginAttempts: 5,
      securityScore: 85
    });
    setIsLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Security Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Security policies, authentication and access control</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <DashboardCard title="Security Score" value={settings ? `${settings.securityScore}%` : undefined} icon={Shield} theme="success" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="2FA Status" value={settings?.twoFactorEnabled ? 'Enabled' : 'Disabled'} icon={Key} theme="info" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Session Timeout" value={settings ? `${settings.sessionTimeout} min` : undefined} icon={Lock} theme="warning" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Max Login Attempts" value={settings?.loginAttempts} icon={AlertTriangle} theme="primary" isLoading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium mb-4">Authentication Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Two-Factor Authentication</label>
                <p className="text-xs text-gray-500">Require 2FA for admin accounts</p>
              </div>
              <StatusBadge variant={settings?.twoFactorEnabled ? 'success' : 'warning'} size="sm">
                {settings?.twoFactorEnabled ? 'Enabled' : 'Disabled'}
              </StatusBadge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Password Policy</label>
                <p className="text-xs text-gray-500">Current policy level</p>
              </div>
              <StatusBadge variant="info" size="sm">Strict</StatusBadge>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium mb-4">Access Control</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">IP Whitelist</label>
                <p className="text-xs text-gray-500">Restrict admin access by IP</p>
              </div>
              <StatusBadge variant="warning" size="sm">Disabled</StatusBadge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">API Rate Limiting</label>
                <p className="text-xs text-gray-500">Limit API requests per minute</p>
              </div>
              <StatusBadge variant="success" size="sm">Active</StatusBadge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecuritySettingsPage;