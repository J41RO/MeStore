/**
 * NotificationSettingsPage Component - System notifications and alert preferences
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Bell, Mail, MessageSquare, Settings } from 'lucide-react';
import { DashboardCard, StatusBadge } from '../../../components/admin/common';

export const NotificationSettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setSettings({
      emailNotifications: true,
      smsNotifications: false,
      pushNotifications: true,
      systemAlerts: true
    });
    setIsLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notification Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Configure system notifications and alert preferences</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <DashboardCard title="Email Notifications" value={settings?.emailNotifications ? 'Enabled' : 'Disabled'} icon={Mail} theme={settings?.emailNotifications ? 'success' : 'warning'} isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="SMS Notifications" value={settings?.smsNotifications ? 'Enabled' : 'Disabled'} icon={MessageSquare} theme={settings?.smsNotifications ? 'success' : 'warning'} isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Push Notifications" value={settings?.pushNotifications ? 'Enabled' : 'Disabled'} icon={Bell} theme={settings?.pushNotifications ? 'success' : 'warning'} isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="System Alerts" value={settings?.systemAlerts ? 'Enabled' : 'Disabled'} icon={Settings} theme={settings?.systemAlerts ? 'success' : 'warning'} isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-6">Notification Preferences</h3>
        <div className="space-y-6">
          {[
            { title: 'Order Notifications', description: 'New orders and order updates', enabled: true },
            { title: 'User Registration', description: 'New user registrations and activations', enabled: true },
            { title: 'Vendor Applications', description: 'New vendor applications and approvals', enabled: true },
            { title: 'System Alerts', description: 'System errors and performance alerts', enabled: true },
            { title: 'Security Alerts', description: 'Login attempts and security events', enabled: false }
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <h4 className="text-sm font-medium text-gray-900">{item.title}</h4>
                <p className="text-xs text-gray-500 mt-1">{item.description}</p>
              </div>
              <StatusBadge variant={item.enabled ? 'success' : 'inactive'} size="sm">
                {item.enabled ? 'Enabled' : 'Disabled'}
              </StatusBadge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NotificationSettingsPage;