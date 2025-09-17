import React, { useState, useCallback, useMemo } from 'react';
import {
  ChevronRight,
  ChevronDown,
  Filter,
  X,
  Check,
  Package,
  Folder,
  RotateCcw,
  Search
} from 'lucide-react';
import {
  CategoryFilterProps,
  CategoryTree,
  CategoryFilter as CategoryFilterType
} from '../../types/category.types';
import { useCategoryFilter } from '../../hooks/useCategories';

// Individual filter tree node component
interface FilterTreeNodeProps {
  category: CategoryTree;
  level: number;
  selectedFilters: CategoryFilterType;
  onToggleCategory: (categoryId: string) => void;
  onToggleExpansion: (categoryId: string) => void;
  showProductCount?: boolean;
  includeSubcategories: boolean;
}

const FilterTreeNode: React.FC<FilterTreeNodeProps> = ({
  category,
  level,
  selectedFilters,
  onToggleCategory,
  onToggleExpansion,
  showProductCount = true,
  includeSubcategories
}) => {
  const hasChildren = category.children && category.children.length > 0;
  const isExpanded = category.isExpanded;
  const isSelected = selectedFilters.category_ids.includes(category.id);

  // Check if any descendant is selected (for visual indication)
  const hasSelectedDescendant = useMemo(() => {
    const checkDescendants = (cats: CategoryTree[]): boolean => {
      return cats.some(cat =>
        selectedFilters.category_ids.includes(cat.id) ||
        checkDescendants(cat.children || [])
      );
    };
    return hasChildren && checkDescendants(category.children!);
  }, [hasChildren, category.children, selectedFilters.category_ids]);

  const handleToggleExpansion = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasChildren) {
      onToggleExpansion(category.id);
    }
  }, [hasChildren, onToggleExpansion, category.id]);

  const handleToggleSelection = useCallback(() => {
    onToggleCategory(category.id);
  }, [onToggleCategory, category.id]);

  const ChevronComponent = useMemo(() => {
    if (!hasChildren) return null;
    return isExpanded ? ChevronDown : ChevronRight;
  }, [hasChildren, isExpanded]);

  return (
    <div className="filter-tree-node">
      <div
        className={`
          flex items-center gap-2 py-2 px-2 cursor-pointer rounded-md transition-all duration-200
          hover:bg-gray-50 dark:hover:bg-gray-800
          ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
          ${hasSelectedDescendant && !isSelected ? 'bg-green-50 dark:bg-green-900/10' : ''}
        `}
        style={{ marginLeft: `${level * 16}px` }}
      >
        {/* Expand/Collapse Button */}
        <button
          onClick={handleToggleExpansion}
          className={`
            flex-shrink-0 w-4 h-4 flex items-center justify-center rounded-sm
            hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors
            ${hasChildren ? 'visible' : 'invisible'}
          `}
          aria-label={isExpanded ? 'Collapse category' : 'Expand category'}
        >
          {ChevronComponent && <ChevronComponent size={12} />}
        </button>

        {/* Selection Checkbox */}
        <div
          className={`
            w-4 h-4 border rounded flex items-center justify-center flex-shrink-0 cursor-pointer
            ${isSelected
              ? 'bg-blue-600 border-blue-600 text-white'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
            }
          `}
          onClick={handleToggleSelection}
        >
          {isSelected && <Check size={10} />}
        </div>

        {/* Category Icon */}
        <div className="flex-shrink-0 w-4 h-4 text-gray-500 dark:text-gray-400">
          {category.icon ? (
            <img
              src={category.icon}
              alt={category.name}
              className="w-full h-full object-contain"
            />
          ) : hasChildren ? (
            <Folder size={12} />
          ) : (
            <Package size={12} />
          )}
        </div>

        {/* Category Name */}
        <span
          className={`
            flex-1 text-sm truncate cursor-pointer
            ${isSelected ? 'text-blue-700 font-medium dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'}
            ${hasSelectedDescendant && !isSelected ? 'text-green-700 dark:text-green-400' : ''}
          `}
          title={category.name}
          onClick={handleToggleSelection}
        >
          {category.name}
        </span>

        {/* Product Count */}
        {showProductCount && category.product_count !== undefined && (
          <span
            className={`
              flex-shrink-0 px-2 py-1 text-xs rounded-full
              ${isSelected
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-200'
                : hasSelectedDescendant
                ? 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-200'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }
            `}
          >
            {category.product_count}
          </span>
        )}
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="filter-tree-children">
          {category.children!.map((child) => (
            <FilterTreeNode
              key={child.id}
              category={child}
              level={level + 1}
              selectedFilters={selectedFilters}
              onToggleCategory={onToggleCategory}
              onToggleExpansion={onToggleExpansion}
              showProductCount={showProductCount}
              includeSubcategories={includeSubcategories}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Selected categories summary component
interface SelectedCategoriesSummaryProps {
  selectedCategories: string[];
  categoryTree: CategoryTree[];
  onRemoveCategory: (categoryId: string) => void;
  onClearAll: () => void;
}

const SelectedCategoriesSummary: React.FC<SelectedCategoriesSummaryProps> = ({
  selectedCategories,
  categoryTree,
  onRemoveCategory,
  onClearAll
}) => {
  // Helper function to find category in tree
  const findCategoryInTree = useCallback((tree: CategoryTree[], categoryId: string): CategoryTree | null => {
    for (const node of tree) {
      if (node.id === categoryId) {
        return node;
      }
      if (node.children.length > 0) {
        const found = findCategoryInTree(node.children, categoryId);
        if (found) return found;
      }
    }
    return null;
  }, []);

  const selectedCategoryObjects = useMemo(() => {
    return selectedCategories
      .map(id => findCategoryInTree(categoryTree, id))
      .filter(Boolean) as CategoryTree[];
  }, [selectedCategories, categoryTree, findCategoryInTree]);

  if (selectedCategories.length === 0) {
    return null;
  }

  return (
    <div className="selected-categories-summary bg-blue-50 dark:bg-blue-900/20 rounded-md p-3 mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
          Active Filters ({selectedCategories.length})
        </span>
        <button
          onClick={onClearAll}
          className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
        >
          Clear all
        </button>
      </div>
      <div className="flex flex-wrap gap-1">
        {selectedCategoryObjects.map((category) => (
          <div
            key={category.id}
            className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs dark:bg-blue-800 dark:text-blue-200"
          >
            <span className="truncate max-w-[100px]">{category.name}</span>
            <button
              onClick={() => onRemoveCategory(category.id)}
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
            >
              <X size={10} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main CategoryFilter component
const CategoryFilter: React.FC<CategoryFilterProps> = ({
  selectedFilters,
  onFiltersChange,
  availableCategories,
  showProductCount = true,
  collapsible = true,
  className = ''
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const {
    toggleCategoryFilter,
    setIncludeSubcategories,
    clearFilters
  } = useCategoryFilter();

  // Filter categories based on search
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) {
      return availableCategories;
    }

    const filterTree = (categories: CategoryTree[]): CategoryTree[] => {
      return categories.reduce((filtered: CategoryTree[], category) => {
        const matchesSearch = category.name.toLowerCase().includes(searchQuery.toLowerCase());
        const filteredChildren = filterTree(category.children || []);

        if (matchesSearch || filteredChildren.length > 0) {
          filtered.push({
            ...category,
            children: filteredChildren,
            isExpanded: filteredChildren.length > 0 || category.isExpanded
          });
        }

        return filtered;
      }, []);
    };

    return filterTree(availableCategories);
  }, [availableCategories, searchQuery]);

  // Handle category toggle
  const handleToggleCategory = useCallback((categoryId: string) => {
    toggleCategoryFilter(categoryId);
  }, [toggleCategoryFilter]);

  // Handle expansion toggle
  const handleToggleExpansion = useCallback((categoryId: string) => {
    // This would need to be handled by the parent component or store
    // For now, we'll implement a simple local state
  }, []);

  // Handle clear all filters
  const handleClearAll = useCallback(() => {
    clearFilters();
    setSearchQuery('');
  }, [clearFilters]);

  // Handle include subcategories toggle
  const handleIncludeSubcategoriesChange = useCallback((include: boolean) => {
    setIncludeSubcategories(include);
  }, [setIncludeSubcategories]);

  const hasActiveFilters = selectedFilters.category_ids.length > 0;
  const totalProductCount = useMemo(() => {
    return availableCategories.reduce((sum, cat) => sum + (cat.product_count || 0), 0);
  }, [availableCategories]);

  return (
    <div className={`category-filter ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-500 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Categories
          </h3>
          {hasActiveFilters && (
            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full dark:bg-blue-900/20 dark:text-blue-300">
              {selectedFilters.category_ids.length}
            </span>
          )}
        </div>
        {collapsible && (
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            {isCollapsed ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
          </button>
        )}
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search categories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          {/* Options */}
          <div className="space-y-2">
            {/* Include subcategories option */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="include-subcategories"
                checked={selectedFilters.include_subcategories}
                onChange={(e) => handleIncludeSubcategoriesChange(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label
                htmlFor="include-subcategories"
                className="text-sm text-gray-700 dark:text-gray-300"
              >
                Include subcategories
              </label>
            </div>

            {/* Clear filters button */}
            {hasActiveFilters && (
              <button
                onClick={handleClearAll}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <RotateCcw size={14} />
                Clear all filters
              </button>
            )}
          </div>

          {/* Selected categories summary */}
          <SelectedCategoriesSummary
            selectedCategories={selectedFilters.category_ids}
            categoryTree={availableCategories}
            onRemoveCategory={handleToggleCategory}
            onClearAll={handleClearAll}
          />

          {/* Category tree */}
          <div className="max-h-80 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-md">
            {filteredCategories.length === 0 ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                {searchQuery ? 'No categories found' : 'No categories available'}
              </div>
            ) : (
              <div className="p-2 space-y-1">
                {filteredCategories.map((category) => (
                  <FilterTreeNode
                    key={category.id}
                    category={category}
                    level={0}
                    selectedFilters={selectedFilters}
                    onToggleCategory={handleToggleCategory}
                    onToggleExpansion={handleToggleExpansion}
                    showProductCount={showProductCount}
                    includeSubcategories={selectedFilters.include_subcategories}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Summary */}
          {showProductCount && (
            <div className="text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-2">
              Total products in all categories: {totalProductCount}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Compact variant for mobile/sidebar
export const CompactCategoryFilter: React.FC<CategoryFilterProps> = (props) => {
  return (
    <CategoryFilter
      {...props}
      collapsible={true}
      showProductCount={false}
      className={`compact-category-filter ${props.className || ''}`}
    />
  );
};

export default CategoryFilter;