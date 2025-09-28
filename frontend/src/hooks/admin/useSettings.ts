/**
 * useSettings Hook - System settings management
 */

import { useState, useCallback, useEffect } from 'react';

export interface SystemSettings {
  siteName: string;
  siteDescription: string;
  timezone: string;
  language: string;
  maintenanceMode: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  twoFactorEnabled: boolean;
  sessionTimeout: number;
}

export const useSettings = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  const fetchSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      const mockSettings: SystemSettings = {
        siteName: 'MeStore Marketplace',
        siteDescription: 'Premier Colombian marketplace platform',
        timezone: 'America/Bogota',
        language: 'es-CO',
        maintenanceMode: false,
        emailNotifications: true,
        smsNotifications: false,
        twoFactorEnabled: true,
        sessionTimeout: 30
      };
      setSettings(mockSettings);
      setIsDirty(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  }, []);

  const updateSetting = useCallback((key: keyof SystemSettings, value: any) => {
    setSettings(prev => prev ? { ...prev, [key]: value } : null);
    setIsDirty(true);
  }, []);

  const saveSettings = useCallback(async () => {
    if (!settings || !isDirty) return;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsDirty(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [settings, isDirty]);

  const resetSettings = useCallback(() => {
    fetchSettings();
  }, [fetchSettings]);

  useEffect(() => { fetchSettings(); }, [fetchSettings]);

  return { settings, loading, error, isDirty, updateSetting, saveSettings, resetSettings };
};