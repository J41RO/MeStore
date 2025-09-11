import React, { useState, useCallback } from 'react';
import { useSystemConfig } from '../../hooks/useSystemConfig';
import ConfigSection from '../../components/admin/ConfigSection';
import { 
  Settings, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Search,
  Filter,
  Download,
  Upload
} from 'lucide-react';

const SystemConfig: React.FC = () => {
  const {
    categories,
    loading,
    error,
    refreshSettings,
    updateSetting,
    bulkUpdateSettings,
    getSettingsByCategory
  } = useSystemConfig();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Show success message temporarily
  const showSuccess = useCallback((message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  }, []);

  // Show error message temporarily
  const showError = useCallback((message: string) => {
    setErrorMessage(message);
    setTimeout(() => setErrorMessage(null), 5000);
  }, []);

  // Handle single setting save
  const handleSaveSetting = useCallback(async (key: string, value: any) => {
    try {
      await updateSetting(key, value);
      showSuccess(`Configuración '${key}' actualizada correctamente`);
    } catch (err: any) {
      showError(err.message || 'Error al actualizar la configuración');
      throw err; // Re-throw to handle in component
    }
  }, [updateSetting, showSuccess, showError]);

  // Handle bulk save for category
  const handleBulkSave = useCallback(async (categoryName: string, updates: Record<string, any>) => {
    try {
      await bulkUpdateSettings(updates);
      showSuccess(`Configuraciones de '${categoryName}' actualizadas correctamente`);
    } catch (err: any) {
      showError(err.message || 'Error al actualizar las configuraciones');
      throw err;
    }
  }, [bulkUpdateSettings, showSuccess, showError]);

  // Handle reset to default
  const handleResetToDefault = useCallback(async (key: string) => {
    // This would require implementing a reset endpoint
    showError('Reset to default not implemented yet');
  }, [showError]);

  // Handle refresh
  const handleRefresh = useCallback(async () => {
    try {
      setIsRefreshing(true);
      await refreshSettings();
      showSuccess('Configuraciones actualizadas');
    } catch (err: any) {
      showError('Error al actualizar configuraciones');
    } finally {
      setIsRefreshing(false);
    }
  }, [refreshSettings, showSuccess, showError]);

  // Filter categories based on search and selection
  const filteredCategories = categories.filter(category => {
    if (selectedCategory !== 'all' && category.name !== selectedCategory) {
      return false;
    }
    
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesCategory = category.display_name.toLowerCase().includes(searchLower) ||
                             category.description.toLowerCase().includes(searchLower);
      
      const matchesSettings = category.settings?.some(setting => 
        setting.key.toLowerCase().includes(searchLower) ||
        setting.description.toLowerCase().includes(searchLower)
      );
      
      return matchesCategory || matchesSettings;
    }
    
    return true;
  });

  // Get summary statistics
  const totalSettings = categories.reduce((sum, cat) => sum + cat.setting_count, 0);
  const editableSettings = categories.reduce((sum, cat) => 
    sum + (cat.settings?.filter(s => s.is_editable).length || 0), 0
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando configuraciones del sistema...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Settings className="w-8 h-8 mr-3 text-blue-600" />
              Configuración del Sistema
            </h1>
            <p className="text-gray-600 mt-2">
              Administra configuraciones generales del sistema MeStocker
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Actualizar
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center">
              <Settings className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-blue-900">{totalSettings}</p>
                <p className="text-sm text-blue-700">Total configuraciones</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-green-900">{editableSettings}</p>
                <p className="text-sm text-green-700">Editables</p>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center">
              <Filter className="w-8 h-8 text-yellow-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-yellow-900">{categories.length}</p>
                <p className="text-sm text-yellow-700">Categorías</p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center">
              <AlertCircle className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-purple-900">
                  {totalSettings - editableSettings}
                </p>
                <p className="text-sm text-purple-700">Solo lectura</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar configuraciones..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todas las categorías</option>
              {categories.map(category => (
                <option key={category.name} value={category.name}>
                  {category.display_name} ({category.setting_count})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
            <p className="text-green-800">{successMessage}</p>
          </div>
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <p className="text-red-800">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Global Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <p className="text-red-800">Error: {error}</p>
          </div>
        </div>
      )}

      {/* Configuration Sections */}
      <div className="space-y-6">
        {filteredCategories.length > 0 ? (
          filteredCategories.map((category) => (
            <ConfigSection
              key={category.name}
              category={category}
              onSaveSetting={handleSaveSetting}
              onBulkSave={handleBulkSave}
              onResetToDefault={handleResetToDefault}
              disabled={loading || isRefreshing}
            />
          ))
        ) : (
          <div className="bg-white shadow rounded-lg p-12 text-center">
            <Settings className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No se encontraron configuraciones
            </h3>
            <p className="text-gray-600">
              {searchTerm || selectedCategory !== 'all'
                ? 'Prueba con diferentes filtros de búsqueda'
                : 'No hay configuraciones disponibles en el sistema'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemConfig;
