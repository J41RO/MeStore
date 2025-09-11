import React, { useState } from 'react';
import ConfigField from './ConfigField';
import { ChevronDown, ChevronRight, Settings, Save, RefreshCw } from 'lucide-react';

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

interface ConfigSectionProps {
  category: ConfigCategory;
  onSaveSetting: (key: string, value: any) => Promise<void>;
  onBulkSave?: (categoryName: string, updates: Record<string, any>) => Promise<void>;
  onResetToDefault?: (key: string) => Promise<void>;
  disabled?: boolean;
  initialExpanded?: boolean;
}

const ConfigSection: React.FC<ConfigSectionProps> = ({
  category,
  onSaveSetting,
  onBulkSave,
  onResetToDefault,
  disabled = false,
  initialExpanded = true
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);
  const [bulkEditMode, setBulkEditMode] = useState(false);
  const [bulkChanges, setBulkChanges] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Get category icon
  const getCategoryIcon = (categoryName: string) => {
    const icons: Record<string, React.ReactNode> = {
      general: <Settings className="w-5 h-5" />,
      email: <span className="text-lg">📧</span>,
      business: <span className="text-lg">💼</span>,
      security: <span className="text-lg">🔒</span>,
    };
    return icons[categoryName] || <Settings className="w-5 h-5" />;
  };

  // Get category color
  const getCategoryColor = (categoryName: string) => {
    const colors: Record<string, string> = {
      general: 'bg-blue-100 text-blue-800 border-blue-200',
      email: 'bg-green-100 text-green-800 border-green-200',
      business: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      security: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[categoryName] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  // Handle bulk edit toggle
  const handleBulkEditToggle = () => {
    setBulkEditMode(!bulkEditMode);
    setBulkChanges({});
  };

  // Handle bulk change
  const handleBulkChange = (key: string, value: any) => {
    setBulkChanges(prev => ({ ...prev, [key]: value }));
  };

  // Handle bulk save
  const handleBulkSave = async () => {
    if (!onBulkSave || Object.keys(bulkChanges).length === 0) return;

    try {
      setIsSaving(true);
      await onBulkSave(category.name, bulkChanges);
      setBulkChanges({});
      setBulkEditMode(false);
    } catch (error) {
      console.error('Error in bulk save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Get editable settings count
  const editableCount = category.settings?.filter(s => s.is_editable).length || 0;
  const totalCount = category.settings?.length || 0;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Category Header */}
      <div className={`${getCategoryColor(category.name)} border-b`}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-black hover:bg-opacity-5 transition-colors"
        >
          <div className="flex items-center space-x-3">
            {getCategoryIcon(category.name)}
            <div className="text-left">
              <h3 className="font-semibold text-lg">{category.display_name}</h3>
              <p className="text-sm opacity-80">{category.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <span className="font-medium">{totalCount}</span> configuraciones
              {editableCount < totalCount && (
                <span className="ml-2 text-xs opacity-75">
                  ({editableCount} editables)
                </span>
              )}
            </div>
            
            {isExpanded ? (
              <ChevronDown className="w-5 h-5" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </div>
        </button>
      </div>

      {/* Category Content */}
      {isExpanded && (
        <div className="bg-white">
          {/* Bulk Edit Controls */}
          {onBulkSave && editableCount > 1 && (
            <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleBulkEditToggle}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      bulkEditMode
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {bulkEditMode ? 'Cancelar edición masiva' : 'Edición masiva'}
                  </button>
                  
                  {bulkEditMode && Object.keys(bulkChanges).length > 0 && (
                    <span className="text-sm text-gray-600">
                      {Object.keys(bulkChanges).length} cambios pendientes
                    </span>
                  )}
                </div>

                {bulkEditMode && Object.keys(bulkChanges).length > 0 && (
                  <button
                    onClick={handleBulkSave}
                    disabled={isSaving}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
                  >
                    {isSaving ? (
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4 mr-2" />
                    )}
                    Guardar todos
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Settings List */}
          <div className="p-6">
            {category.settings && category.settings.length > 0 ? (
              <div className="space-y-4">
                {category.settings.map((setting) => (
                  <ConfigField
                    key={setting.id}
                    setting={setting}
                    onSave={bulkEditMode ? 
                      (key, value) => {
                        handleBulkChange(key, value);
                        return Promise.resolve();
                      } : 
                      onSaveSetting
                    }
                    onResetToDefault={onResetToDefault}
                    disabled={disabled || isSaving}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Settings className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>No hay configuraciones disponibles en esta categoría</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigSection;