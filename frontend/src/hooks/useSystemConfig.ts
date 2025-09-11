import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface SystemSetting {
  id: string;
  key: string;
  value: string;
  category: string;
  data_type: 'string' | 'integer' | 'float' | 'boolean' | 'json';
  description: string;
  default_value?: string;
  is_public: boolean;
  is_editable: boolean;
  last_modified_by?: string;
  created_at: string;
  updated_at: string;
  typed_value: any;
}

interface ConfigCategory {
  name: string;
  display_name: string;
  description: string;
  setting_count: number;
  settings?: SystemSetting[];
}

interface UseSystemConfigReturn {
  settings: SystemSetting[];
  categories: ConfigCategory[];
  loading: boolean;
  error: string | null;
  refreshSettings: () => Promise<void>;
  updateSetting: (key: string, value: any) => Promise<void>;
  bulkUpdateSettings: (updates: Record<string, any>) => Promise<void>;
  getSetting: (key: string) => SystemSetting | undefined;
  getSettingValue: (key: string, defaultValue?: any) => any;
  getSettingsByCategory: (category: string) => SystemSetting[];
}

const API_BASE_URL = '/api/v1/system-config';

export const useSystemConfig = (): UseSystemConfigReturn => {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [categories, setCategories] = useState<ConfigCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get authentication token
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // Fetch all settings
  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const headers = getAuthHeaders();
      const response = await axios.get(API_BASE_URL, { headers });
      
      setSettings(response.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error loading settings';
      setError(errorMessage);
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const headers = getAuthHeaders();
      const response = await axios.get(`${API_BASE_URL}/categories/`, { headers });
      
      setCategories(response.data.categories);
    } catch (err: any) {
      console.error('Error fetching categories:', err);
    }
  }, []);

  // Refresh all data
  const refreshSettings = useCallback(async () => {
    await Promise.all([fetchSettings(), fetchCategories()]);
  }, [fetchSettings, fetchCategories]);

  // Update a single setting
  const updateSetting = useCallback(async (key: string, value: any) => {
    try {
      const headers = getAuthHeaders();
      const response = await axios.put(
        `${API_BASE_URL}/${key}`,
        { value: String(value) },
        { headers }
      );

      // Update local state
      setSettings(prevSettings => 
        prevSettings.map(setting => 
          setting.key === key ? response.data : setting
        )
      );

      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error updating setting';
      throw new Error(errorMessage);
    }
  }, []);

  // Bulk update multiple settings
  const bulkUpdateSettings = useCallback(async (updates: Record<string, any>) => {
    try {
      const headers = getAuthHeaders();
      
      // Convert all values to strings for the API
      const stringUpdates = Object.entries(updates).reduce((acc, [key, value]) => {
        acc[key] = String(value);
        return acc;
      }, {} as Record<string, string>);

      const response = await axios.post(
        `${API_BASE_URL}/bulk`,
        { settings: stringUpdates },
        { headers }
      );

      // Refresh settings after bulk update
      await fetchSettings();

      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error updating settings';
      throw new Error(errorMessage);
    }
  }, [fetchSettings]);

  // Get a specific setting by key
  const getSetting = useCallback((key: string): SystemSetting | undefined => {
    return settings.find(setting => setting.key === key);
  }, [settings]);

  // Get a setting value with optional default
  const getSettingValue = useCallback((key: string, defaultValue?: any): any => {
    const setting = getSetting(key);
    if (setting) {
      return setting.typed_value;
    }
    return defaultValue;
  }, [getSetting]);

  // Get settings by category
  const getSettingsByCategory = useCallback((category: string): SystemSetting[] => {
    return settings.filter(setting => setting.category === category);
  }, [settings]);

  // Load data on mount
  useEffect(() => {
    refreshSettings();
  }, [refreshSettings]);

  // Update categories with settings when settings change
  useEffect(() => {
    setCategories(prevCategories => 
      prevCategories.map(category => ({
        ...category,
        settings: getSettingsByCategory(category.name)
      }))
    );
  }, [settings, getSettingsByCategory]);

  return {
    settings,
    categories,
    loading,
    error,
    refreshSettings,
    updateSetting,
    bulkUpdateSettings,
    getSetting,
    getSettingValue,
    getSettingsByCategory,
  };
};

// Helper function to validate setting value based on data type
export const validateSettingValue = (value: any, dataType: string): { valid: boolean; error?: string } => {
  try {
    switch (dataType) {
      case 'boolean':
        // Accept various boolean representations
        if (typeof value === 'boolean') return { valid: true };
        const strVal = String(value).toLowerCase();
        if (['true', 'false', '1', '0', 'yes', 'no', 'on', 'off'].includes(strVal)) {
          return { valid: true };
        }
        return { valid: false, error: 'Must be a boolean value (true/false)' };

      case 'integer':
        const intVal = Number(value);
        if (!Number.isInteger(intVal) || isNaN(intVal)) {
          return { valid: false, error: 'Must be a valid integer' };
        }
        return { valid: true };

      case 'float':
        const floatVal = Number(value);
        if (isNaN(floatVal)) {
          return { valid: false, error: 'Must be a valid number' };
        }
        return { valid: true };

      case 'json':
        try {
          if (typeof value === 'object') {
            JSON.stringify(value);
          } else {
            JSON.parse(String(value));
          }
          return { valid: true };
        } catch {
          return { valid: false, error: 'Must be valid JSON' };
        }

      case 'string':
      default:
        return { valid: true };
    }
  } catch (error) {
    return { valid: false, error: 'Invalid value' };
  }
};

// Helper function to format setting value for display
export const formatSettingValue = (setting: SystemSetting): string => {
  if (setting.data_type === 'boolean') {
    return setting.typed_value ? 'Activado' : 'Desactivado';
  }
  
  if (setting.data_type === 'json') {
    try {
      return JSON.stringify(setting.typed_value, null, 2);
    } catch {
      return setting.value;
    }
  }
  
  return String(setting.typed_value);
};

export default useSystemConfig;