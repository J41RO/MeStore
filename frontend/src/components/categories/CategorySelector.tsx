import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  ChevronDown,
  Search,
  X,
  Check,
  Package,
  Folder,
  AlertCircle,
  Info
} from 'lucide-react';
import { CategorySelectorProps, Category, CategoryTree } from '../../types/category.types';
import { useCategorySelection, useCategorySearch } from '../../hooks/useCategories';

// Individual category option component
interface CategoryOptionProps {
  category: Category;
  isSelected: boolean;
  canSelect: boolean;
  onToggle: (categoryId: string) => void;
  level?: number;
  showPath?: boolean;
}

const CategoryOption: React.FC<CategoryOptionProps> = ({
  category,
  isSelected,
  canSelect,
  onToggle,
  level = 0,
  showPath = false
}) => {
  const handleClick = useCallback(() => {
    if (canSelect || isSelected) {
      onToggle(category.id);
    }
  }, [canSelect, isSelected, onToggle, category.id]);

  return (
    <div
      className={`
        flex items-center gap-3 p-3 cursor-pointer transition-colors rounded-md
        ${isSelected
          ? 'bg-blue-50 border-l-4 border-blue-500 dark:bg-blue-900/20 dark:border-blue-400'
          : canSelect
          ? 'hover:bg-gray-50 dark:hover:bg-gray-800'
          : 'opacity-50 cursor-not-allowed'
        }
        ${!category.is_active ? 'opacity-60' : ''}
      `}
      style={{ paddingLeft: `${12 + level * 20}px` }}
      onClick={handleClick}
    >
      {/* Selection indicator */}
      <div
        className={`
          w-4 h-4 border rounded flex items-center justify-center flex-shrink-0
          ${isSelected
            ? 'bg-blue-600 border-blue-600 text-white'
            : 'border-gray-300 dark:border-gray-600'
          }
        `}
      >
        {isSelected && <Check size={12} />}
      </div>

      {/* Category icon */}
      <div className="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400">
        {category.icon ? (
          <img
            src={category.icon}
            alt={category.name}
            className="w-full h-full object-contain"
          />
        ) : (
          <Package size={14} />
        )}
      </div>

      {/* Category info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={`
              text-sm font-medium truncate
              ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'}
            `}
          >
            {category.name}
          </span>
          {!category.is_active && (
            <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-full dark:bg-yellow-900/20 dark:text-yellow-400">
              Inactive
            </span>
          )}
        </div>
        {showPath && category.level > 0 && (
          <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
            Level {category.level}
          </div>
        )}
      </div>

      {/* Product count */}
      {category.product_count !== undefined && (
        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full dark:bg-gray-700 dark:text-gray-400">
          {category.product_count}
        </span>
      )}
    </div>
  );
};

// Selected category tag component
interface SelectedCategoryTagProps {
  category: Category;
  onRemove: (categoryId: string) => void;
}

const SelectedCategoryTag: React.FC<SelectedCategoryTagProps> = ({
  category,
  onRemove
}) => {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm dark:bg-blue-900/20 dark:text-blue-300">
      {category.icon && (
        <img
          src={category.icon}
          alt={category.name}
          className="w-3 h-3 object-contain"
        />
      )}
      <span className="truncate max-w-[120px]">{category.name}</span>
      <button
        onClick={() => onRemove(category.id)}
        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
      >
        <X size={12} />
      </button>
    </div>
  );
};

// Main CategorySelector component
const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategories = [],
  onSelectionChange,
  maxSelections,
  required = false,
  allowMultiple = true,
  filterByLevel,
  placeholder = 'Select categories...',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const { searchResults } = useCategorySearch();
  const {
    toggleSelection,
    clearSelection,
    isSelected,
    canSelect,
    isAtLimit
  } = useCategorySelection(maxSelections, allowMultiple);

  // Get categories to display
  const availableCategories = useMemo(() => {
    let categories = searchQuery ? searchResults : [];

    // Filter by level if specified
    if (filterByLevel !== undefined) {
      categories = categories.filter(cat => cat.level <= filterByLevel);
    }

    // Filter out inactive categories for better UX
    categories = categories.filter(cat => cat.is_active);

    return categories.sort((a, b) => {
      if (a.level !== b.level) return a.level - b.level;
      return a.sort_order - b.sort_order;
    });
  }, [searchResults, searchQuery, filterByLevel]);

  // Get selected category objects
  const selectedCategoryObjects = useMemo(() => {
    return selectedCategories
      .map(id => availableCategories.find(cat => cat.id === id))
      .filter(Boolean) as Category[];
  }, [selectedCategories, availableCategories]);

  // Handle category toggle
  const handleCategoryToggle = useCallback((categoryId: string) => {
    if (!allowMultiple) {
      // Single selection mode
      const newSelection = isSelected(categoryId) ? [] : [categoryId];
      onSelectionChange(newSelection);
    } else {
      // Multiple selection mode
      toggleSelection(categoryId);
      const isCurrentlySelected = selectedCategories.includes(categoryId);
      let newSelection;

      if (isCurrentlySelected) {
        newSelection = selectedCategories.filter(id => id !== categoryId);
      } else if (canSelect(categoryId)) {
        newSelection = [...selectedCategories, categoryId];
      } else {
        return; // Can't select more
      }

      onSelectionChange(newSelection);
    }
  }, [
    allowMultiple,
    isSelected,
    selectedCategories,
    onSelectionChange,
    toggleSelection,
    canSelect
  ]);

  // Handle remove selected category
  const handleRemoveCategory = useCallback((categoryId: string) => {
    const newSelection = selectedCategories.filter(id => id !== categoryId);
    onSelectionChange(newSelection);
  }, [selectedCategories, onSelectionChange]);

  // Handle clear all
  const handleClearAll = useCallback(() => {
    onSelectionChange([]);
    clearSelection();
  }, [onSelectionChange, clearSelection]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Validation state
  const hasError = required && selectedCategories.length === 0;
  const showLimitWarning = isAtLimit && allowMultiple;

  return (
    <div ref={containerRef} className={`category-selector relative ${className}`}>
      {/* Selected categories display */}
      {selectedCategoryObjects.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-2">
            {selectedCategoryObjects.map((category) => (
              <SelectedCategoryTag
                key={category.id}
                category={category}
                onRemove={handleRemoveCategory}
              />
            ))}
          </div>
          {allowMultiple && selectedCategoryObjects.length > 1 && (
            <button
              onClick={handleClearAll}
              className="mt-2 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Clear all
            </button>
          )}
        </div>
      )}

      {/* Selector trigger */}
      <div
        className={`
          relative cursor-pointer border rounded-md px-3 py-2 transition-colors
          ${isOpen ? 'ring-2 ring-blue-500 border-blue-500' : 'border-gray-300 dark:border-gray-600'}
          ${hasError ? 'border-red-500 ring-2 ring-red-200' : ''}
          bg-white dark:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500
        `}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center justify-between">
          <span
            className={`
              text-sm
              ${selectedCategories.length === 0
                ? 'text-gray-500 dark:text-gray-400'
                : 'text-gray-900 dark:text-white'
              }
            `}
          >
            {selectedCategories.length === 0
              ? placeholder
              : allowMultiple
              ? `${selectedCategories.length} selected`
              : selectedCategoryObjects[0]?.name
            }
          </span>
          <ChevronDown
            size={16}
            className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          />
        </div>
      </div>

      {/* Error message */}
      {hasError && (
        <div className="mt-1 flex items-center gap-1 text-red-600 text-xs">
          <AlertCircle size={12} />
          <span>Please select at least one category</span>
        </div>
      )}

      {/* Limit warning */}
      {showLimitWarning && (
        <div className="mt-1 flex items-center gap-1 text-yellow-600 text-xs">
          <Info size={12} />
          <span>Maximum {maxSelections} categories allowed</span>
        </div>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 max-h-80 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search categories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                autoFocus
              />
            </div>
          </div>

          {/* Options */}
          <div className="max-h-60 overflow-y-auto">
            {availableCategories.length === 0 ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                {searchQuery ? 'No categories found' : 'No categories available'}
              </div>
            ) : (
              availableCategories.map((category) => (
                <CategoryOption
                  key={category.id}
                  category={category}
                  isSelected={isSelected(category.id)}
                  canSelect={canSelect(category.id)}
                  onToggle={handleCategoryToggle}
                  level={category.level}
                  showPath={searchQuery.length > 0}
                />
              ))
            )}
          </div>

          {/* Footer info */}
          {allowMultiple && (
            <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <div className="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
                <span>
                  {selectedCategories.length} of {maxSelections || '∞'} selected
                </span>
                {selectedCategories.length > 0 && (
                  <button
                    onClick={handleClearAll}
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  >
                    Clear all
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CategorySelector;