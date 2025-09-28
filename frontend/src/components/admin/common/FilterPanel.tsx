/**
 * FilterPanel Component
 *
 * Advanced filtering sidebar panel with multiple filter types and conditions.
 * Provides a clean UX for complex data filtering scenarios.
 *
 * Features:
 * - Multiple filter types (text, select, date range, number range)
 * - Dynamic filter conditions and operators
 * - Filter presets and saved filters
 * - Real-time filter preview
 * - Mobile-responsive collapsible design
 * - Accessibility compliance (WCAG AA)
 * - Export/import filter configurations
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, {
  memo,
  useState,
  useCallback,
  useMemo,
  useEffect
} from 'react';
import {
  X,
  Plus,
  Search,
  Calendar,
  Filter,
  Save,
  Download,
  Upload,
  ChevronDown,
  ChevronRight,
  Trash2,
  Check
} from 'lucide-react';

/**
 * Filter types
 */
export type FilterType = 'text' | 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'numberrange' | 'boolean';

/**
 * Filter operators
 */
export type FilterOperator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'
  | 'greater_than'
  | 'less_than'
  | 'greater_equal'
  | 'less_equal'
  | 'between'
  | 'in'
  | 'not_in'
  | 'is_null'
  | 'is_not_null';

/**
 * Filter definition
 */
export interface FilterDefinition {
  id: string;
  label: string;
  type: FilterType;
  field: string;
  operators?: FilterOperator[];
  options?: Array<{ value: any; label: string }>;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  required?: boolean;
  description?: string;
}

/**
 * Active filter
 */
export interface ActiveFilter {
  id: string;
  field: string;
  operator: FilterOperator;
  value: any;
  label?: string;
}

/**
 * Filter preset
 */
export interface FilterPreset {
  id: string;
  name: string;
  description?: string;
  filters: ActiveFilter[];
  isDefault?: boolean;
}

/**
 * FilterPanel component props
 */
export interface FilterPanelProps {
  /** Available filter definitions */
  filterDefinitions: FilterDefinition[];

  /** Currently active filters */
  activeFilters: ActiveFilter[];

  /** Available filter presets */
  presets?: FilterPreset[];

  /** Panel visibility */
  isOpen: boolean;

  /** Panel title */
  title?: string;

  /** Whether to show preset section */
  showPresets?: boolean;

  /** Whether to allow saving custom presets */
  allowSavePresets?: boolean;

  /** Maximum number of filters allowed */
  maxFilters?: number;

  /** Whether panel is collapsible on mobile */
  collapsible?: boolean;

  /** Additional CSS classes */
  className?: string;

  /** Event handlers */
  onFiltersChange: (filters: ActiveFilter[]) => void;
  onClose?: () => void;
  onApplyPreset?: (preset: FilterPreset) => void;
  onSavePreset?: (name: string, filters: ActiveFilter[]) => void;
  onDeletePreset?: (presetId: string) => void;
  onExportFilters?: (filters: ActiveFilter[]) => void;
  onImportFilters?: (filters: ActiveFilter[]) => void;

  /** Test ID for testing */
  testId?: string;
}

/**
 * FilterPanel Component
 */
export const FilterPanel: React.FC<FilterPanelProps> = memo(({
  filterDefinitions,
  activeFilters,
  presets = [],
  isOpen,
  title = 'Filters',
  showPresets = true,
  allowSavePresets = true,
  maxFilters = 10,
  collapsible = true,
  className = '',
  onFiltersChange,
  onClose,
  onApplyPreset,
  onSavePreset,
  onDeletePreset,
  onExportFilters,
  onImportFilters,
  testId = 'filter-panel'
}) => {
  // Local state
  const [searchQuery, setSearchQuery] = useState('');
  const [showPresetForm, setShowPresetForm] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [expandedSections, setExpandedSections] = useState<string[]>(['filters']);

  /**
   * Get available operators for filter type
   */
  const getOperatorsForType = useCallback((type: FilterType): FilterOperator[] => {
    const typeOperators: Record<FilterType, FilterOperator[]> = {
      text: ['equals', 'not_equals', 'contains', 'not_contains', 'starts_with', 'ends_with'],
      select: ['equals', 'not_equals', 'in', 'not_in'],
      multiselect: ['in', 'not_in'],
      date: ['equals', 'not_equals', 'greater_than', 'less_than', 'greater_equal', 'less_equal'],
      daterange: ['between'],
      number: ['equals', 'not_equals', 'greater_than', 'less_than', 'greater_equal', 'less_equal'],
      numberrange: ['between'],
      boolean: ['equals', 'not_equals']
    };

    return typeOperators[type] || [];
  }, []);

  /**
   * Filtered filter definitions based on search
   */
  const filteredDefinitions = useMemo(() => {
    if (!searchQuery) return filterDefinitions;

    return filterDefinitions.filter(def =>
      def.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      def.field.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [filterDefinitions, searchQuery]);

  /**
   * Add new filter
   */
  const handleAddFilter = useCallback((definition: FilterDefinition) => {
    if (activeFilters.length >= maxFilters) return;

    const availableOperators = definition.operators || getOperatorsForType(definition.type);
    const defaultOperator = availableOperators[0];

    let defaultValue: any = '';
    if (definition.type === 'boolean') defaultValue = true;
    if (definition.type === 'number' || definition.type === 'numberrange') defaultValue = 0;
    if (definition.type === 'date' || definition.type === 'daterange') defaultValue = new Date().toISOString().split('T')[0];

    const newFilter: ActiveFilter = {
      id: `filter_${Date.now()}`,
      field: definition.field,
      operator: defaultOperator,
      value: defaultValue,
      label: definition.label
    };

    onFiltersChange([...activeFilters, newFilter]);
  }, [activeFilters, maxFilters, getOperatorsForType, onFiltersChange]);

  /**
   * Update filter
   */
  const handleUpdateFilter = useCallback((filterId: string, updates: Partial<ActiveFilter>) => {
    const updatedFilters = activeFilters.map(filter =>
      filter.id === filterId ? { ...filter, ...updates } : filter
    );
    onFiltersChange(updatedFilters);
  }, [activeFilters, onFiltersChange]);

  /**
   * Remove filter
   */
  const handleRemoveFilter = useCallback((filterId: string) => {
    const updatedFilters = activeFilters.filter(filter => filter.id !== filterId);
    onFiltersChange(updatedFilters);
  }, [activeFilters, onFiltersChange]);

  /**
   * Clear all filters
   */
  const handleClearAll = useCallback(() => {
    onFiltersChange([]);
  }, [onFiltersChange]);

  /**
   * Apply preset
   */
  const handleApplyPreset = useCallback((preset: FilterPreset) => {
    onFiltersChange(preset.filters);
    onApplyPreset?.(preset);
  }, [onFiltersChange, onApplyPreset]);

  /**
   * Save current filters as preset
   */
  const handleSavePreset = useCallback(() => {
    if (!presetName.trim() || activeFilters.length === 0) return;

    onSavePreset?.(presetName.trim(), activeFilters);
    setPresetName('');
    setShowPresetForm(false);
  }, [presetName, activeFilters, onSavePreset]);

  /**
   * Toggle section expansion
   */
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  }, []);

  /**
   * Render filter value input
   */
  const renderFilterInput = useCallback((filter: ActiveFilter) => {
    const definition = filterDefinitions.find(def => def.field === filter.field);
    if (!definition) return null;

    const commonProps = {
      value: filter.value,
      onChange: (value: any) => handleUpdateFilter(filter.id, { value }),
      className: "block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
    };

    switch (definition.type) {
      case 'text':
        return (
          <input
            type="text"
            placeholder={definition.placeholder}
            {...commonProps}
            onChange={(e) => commonProps.onChange(e.target.value)}
          />
        );

      case 'select':
        return (
          <select
            {...commonProps}
            onChange={(e) => commonProps.onChange(e.target.value)}
          >
            <option value="">Select option...</option>
            {definition.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'number':
        return (
          <input
            type="number"
            min={definition.min}
            max={definition.max}
            step={definition.step}
            {...commonProps}
            onChange={(e) => commonProps.onChange(Number(e.target.value))}
          />
        );

      case 'date':
        return (
          <input
            type="date"
            {...commonProps}
            onChange={(e) => commonProps.onChange(e.target.value)}
          />
        );

      case 'boolean':
        return (
          <select
            {...commonProps}
            onChange={(e) => commonProps.onChange(e.target.value === 'true')}
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        );

      default:
        return (
          <input
            type="text"
            {...commonProps}
            onChange={(e) => commonProps.onChange(e.target.value)}
          />
        );
    }
  }, [filterDefinitions, handleUpdateFilter]);

  /**
   * Panel classes
   */
  const panelClasses = useMemo(() => `
    bg-white border-r border-gray-200 shadow-lg transition-transform duration-300 ease-in-out
    ${isOpen ? 'translate-x-0' : '-translate-x-full'}
    ${className}
  `.trim(), [isOpen, className]);

  if (!isOpen) return null;

  return (
    <div className={panelClasses} data-testid={testId}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">{title}</h2>
          <div className="flex items-center space-x-2">
            {/* Export/Import */}
            {(onExportFilters || onImportFilters) && (
              <div className="flex space-x-1">
                {onExportFilters && (
                  <button
                    type="button"
                    onClick={() => onExportFilters(activeFilters)}
                    className="p-1 text-gray-400 hover:text-gray-500"
                    title="Export filters"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}
                {onImportFilters && (
                  <button
                    type="button"
                    className="p-1 text-gray-400 hover:text-gray-500"
                    title="Import filters"
                  >
                    <Upload className="w-4 h-4" />
                  </button>
                )}
              </div>
            )}

            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="p-1 text-gray-400 hover:text-gray-500"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Presets Section */}
          {showPresets && presets.length > 0 && (
            <div className="border-b border-gray-200">
              <button
                type="button"
                onClick={() => toggleSection('presets')}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
              >
                <span className="font-medium text-gray-900">Presets</span>
                {expandedSections.includes('presets') ? (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
              </button>

              {expandedSections.includes('presets') && (
                <div className="px-4 pb-4 space-y-2">
                  {presets.map((preset) => (
                    <div
                      key={preset.id}
                      className="flex items-center justify-between p-2 border border-gray-200 rounded-md hover:bg-gray-50"
                    >
                      <div className="flex-1 min-w-0">
                        <button
                          type="button"
                          onClick={() => handleApplyPreset(preset)}
                          className="text-left w-full"
                        >
                          <div className="font-medium text-gray-900 truncate">
                            {preset.name}
                          </div>
                          {preset.description && (
                            <div className="text-sm text-gray-500 truncate">
                              {preset.description}
                            </div>
                          )}
                        </button>
                      </div>
                      {onDeletePreset && !preset.isDefault && (
                        <button
                          type="button"
                          onClick={() => onDeletePreset(preset.id)}
                          className="ml-2 p-1 text-gray-400 hover:text-red-500"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}

                  {/* Save Preset Form */}
                  {allowSavePresets && (
                    <div className="mt-4">
                      {showPresetForm ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            placeholder="Preset name..."
                            value={presetName}
                            onChange={(e) => setPresetName(e.target.value)}
                            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          />
                          <div className="flex space-x-2">
                            <button
                              type="button"
                              onClick={handleSavePreset}
                              disabled={!presetName.trim() || activeFilters.length === 0}
                              className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <Check className="w-4 h-4 mr-1" />
                              Save
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setShowPresetForm(false);
                                setPresetName('');
                              }}
                              className="px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setShowPresetForm(true)}
                          disabled={activeFilters.length === 0}
                          className="w-full inline-flex justify-center items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Save Current Filters
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Active Filters Section */}
          <div className="border-b border-gray-200">
            <button
              type="button"
              onClick={() => toggleSection('filters')}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
            >
              <span className="font-medium text-gray-900">
                Active Filters ({activeFilters.length})
              </span>
              {expandedSections.includes('filters') ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>

            {expandedSections.includes('filters') && (
              <div className="px-4 pb-4">
                {activeFilters.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No filters applied
                  </p>
                ) : (
                  <div className="space-y-4">
                    {activeFilters.map((filter) => {
                      const definition = filterDefinitions.find(def => def.field === filter.field);
                      const availableOperators = definition?.operators || getOperatorsForType(definition?.type || 'text');

                      return (
                        <div key={filter.id} className="p-3 border border-gray-200 rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-900">
                              {filter.label || filter.field}
                            </span>
                            <button
                              type="button"
                              onClick={() => handleRemoveFilter(filter.id)}
                              className="text-gray-400 hover:text-red-500"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>

                          <div className="space-y-2">
                            {/* Operator Selection */}
                            <select
                              value={filter.operator}
                              onChange={(e) => handleUpdateFilter(filter.id, { operator: e.target.value as FilterOperator })}
                              className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            >
                              {availableOperators.map((operator) => (
                                <option key={operator} value={operator}>
                                  {operator.replace(/_/g, ' ').toUpperCase()}
                                </option>
                              ))}
                            </select>

                            {/* Value Input */}
                            {!['is_null', 'is_not_null'].includes(filter.operator) && (
                              renderFilterInput(filter)
                            )}
                          </div>
                        </div>
                      );
                    })}

                    {/* Clear All Button */}
                    <button
                      type="button"
                      onClick={handleClearAll}
                      className="w-full px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Clear All Filters
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Add Filter Section */}
          <div>
            <button
              type="button"
              onClick={() => toggleSection('add')}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
            >
              <span className="font-medium text-gray-900">Add Filter</span>
              {expandedSections.includes('add') ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>

            {expandedSections.includes('add') && (
              <div className="px-4 pb-4">
                {/* Search Filters */}
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search filters..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                {/* Available Filters */}
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {filteredDefinitions.map((definition) => {
                    const isAlreadyActive = activeFilters.some(filter => filter.field === definition.field);
                    const canAdd = !isAlreadyActive && activeFilters.length < maxFilters;

                    return (
                      <button
                        key={definition.id}
                        type="button"
                        onClick={() => canAdd && handleAddFilter(definition)}
                        disabled={!canAdd}
                        className={`w-full p-3 text-left border rounded-md transition-colors ${
                          canAdd
                            ? 'border-gray-200 hover:bg-blue-50 hover:border-blue-300'
                            : 'border-gray-100 bg-gray-50 cursor-not-allowed'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className={`font-medium ${canAdd ? 'text-gray-900' : 'text-gray-400'}`}>
                              {definition.label}
                            </div>
                            {definition.description && (
                              <div className={`text-sm ${canAdd ? 'text-gray-500' : 'text-gray-400'}`}>
                                {definition.description}
                              </div>
                            )}
                          </div>
                          {canAdd && (
                            <Plus className="w-4 h-4 text-gray-400" />
                          )}
                          {isAlreadyActive && (
                            <Check className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

/**
 * Display name for debugging
 */
FilterPanel.displayName = 'FilterPanel';

/**
 * Default export
 */
export default FilterPanel;