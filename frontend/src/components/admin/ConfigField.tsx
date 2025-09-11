import React, { useState, useCallback } from 'react';
import { validateSettingValue, formatSettingValue } from '../../hooks/useSystemConfig';
import { Save, X, RefreshCw, AlertCircle, Info } from 'lucide-react';

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

interface ConfigFieldProps {
  setting: SystemSetting;
  onSave: (key: string, value: any) => Promise<void>;
  onResetToDefault?: (key: string) => Promise<void>;
  disabled?: boolean;
}

const ConfigField: React.FC<ConfigFieldProps> = ({
  setting,
  onSave,
  onResetToDefault,
  disabled = false
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [localValue, setLocalValue] = useState<any>(setting.typed_value);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle edit mode toggle
  const handleEdit = useCallback(() => {
    if (!setting.is_editable || disabled) return;
    setIsEditing(true);
    setLocalValue(setting.typed_value);
    setError(null);
  }, [setting.is_editable, setting.typed_value, disabled]);

  // Handle cancel edit
  const handleCancel = useCallback(() => {
    setIsEditing(false);
    setLocalValue(setting.typed_value);
    setError(null);
  }, [setting.typed_value]);

  // Handle save
  const handleSave = useCallback(async () => {
    try {
      setError(null);
      setIsSaving(true);

      // Validate value
      const validation = validateSettingValue(localValue, setting.data_type);
      if (!validation.valid) {
        setError(validation.error || 'Invalid value');
        return;
      }

      await onSave(setting.key, localValue);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Error saving setting');
    } finally {
      setIsSaving(false);
    }
  }, [localValue, setting.data_type, setting.key, onSave]);

  // Handle reset to default
  const handleResetToDefault = useCallback(async () => {
    if (!onResetToDefault || !setting.default_value) return;
    
    try {
      setError(null);
      await onResetToDefault(setting.key);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Error resetting to default');
    }
  }, [onResetToDefault, setting.key, setting.default_value]);

  // Render input based on data type
  const renderInput = () => {
    const baseClasses = "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";
    
    switch (setting.data_type) {
      case 'boolean':
        return (
          <div className="flex items-center space-x-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={Boolean(localValue)}
                onChange={(e) => setLocalValue(e.target.checked)}
                className="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out"
              />
              <span className="ml-2 text-sm text-gray-700">
                {Boolean(localValue) ? 'Activado' : 'Desactivado'}
              </span>
            </label>
          </div>
        );

      case 'integer':
        return (
          <input
            type="number"
            step="1"
            value={localValue || ''}
            onChange={(e) => setLocalValue(parseInt(e.target.value) || 0)}
            className={baseClasses}
            placeholder="Ingrese un número entero"
          />
        );

      case 'float':
        return (
          <input
            type="number"
            step="0.01"
            value={localValue || ''}
            onChange={(e) => setLocalValue(parseFloat(e.target.value) || 0)}
            className={baseClasses}
            placeholder="Ingrese un número decimal"
          />
        );

      case 'json':
        return (
          <textarea
            value={typeof localValue === 'object' ? JSON.stringify(localValue, null, 2) : localValue}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setLocalValue(parsed);
              } catch {
                setLocalValue(e.target.value);
              }
            }}
            className={`${baseClasses} h-32 font-mono text-sm`}
            placeholder="Ingrese JSON válido"
          />
        );

      case 'string':
      default:
        return (
          <input
            type="text"
            value={localValue || ''}
            onChange={(e) => setLocalValue(e.target.value)}
            className={baseClasses}
            placeholder="Ingrese texto"
          />
        );
    }
  };

  // Get display value
  const displayValue = formatSettingValue(setting);

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h4 className="font-medium text-gray-900">{setting.key}</h4>
            {setting.is_public && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                Público
              </span>
            )}
            {!setting.is_editable && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                Solo lectura
              </span>
            )}
          </div>
          
          <p className="text-sm text-gray-600 mt-1 flex items-start">
            <Info className="w-4 h-4 mr-1 mt-0.5 text-gray-400 flex-shrink-0" />
            {setting.description}
          </p>
          
          <div className="mt-2 text-xs text-gray-500">
            <span>Tipo: {setting.data_type}</span>
            {setting.default_value && (
              <span className="ml-4">Por defecto: {setting.default_value}</span>
            )}
          </div>
        </div>

        {setting.is_editable && !disabled && (
          <div className="flex items-center space-x-2 ml-4">
            {!isEditing ? (
              <button
                onClick={handleEdit}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Editar
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {isSaving ? (
                    <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                  ) : (
                    <Save className="w-3 h-3 mr-1" />
                  )}
                  Guardar
                </button>
                <button
                  onClick={handleCancel}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                >
                  <X className="w-3 h-3 mr-1" />
                  Cancelar
                </button>
                {setting.default_value && onResetToDefault && (
                  <button
                    onClick={handleResetToDefault}
                    className="text-xs text-gray-500 hover:text-gray-700"
                    title="Restablecer a valor por defecto"
                  >
                    Reset
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Value display/edit */}
      <div className="mt-3">
        {isEditing ? (
          <div>
            {renderInput()}
            {error && (
              <div className="mt-2 flex items-center text-red-600 text-sm">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-gray-50 px-3 py-2 rounded border">
            <span className="text-sm font-mono text-gray-800">
              {displayValue}
            </span>
          </div>
        )}
      </div>

      {/* Last updated info */}
      {setting.updated_at && (
        <div className="mt-2 text-xs text-gray-400">
          Última actualización: {new Date(setting.updated_at).toLocaleString('es-ES')}
        </div>
      )}
    </div>
  );
};

export default ConfigField;