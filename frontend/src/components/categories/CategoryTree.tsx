import React, { memo, useCallback, useMemo } from 'react';
import { ChevronRight, ChevronDown, Package, Folder, FolderOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { CategoryTree as CategoryTreeType, CategoryTreeProps } from '../../types/category.types';
import { useCategoryTree } from '../../hooks/useCategories';

// Individual tree node component
interface CategoryTreeNodeProps {
  category: CategoryTreeType;
  level: number;
  onCategorySelect?: (category: CategoryTreeType) => void;
  onCategoryExpand?: (categoryId: string, isExpanded: boolean) => void;
  selectedCategoryId?: string;
  showProductCount?: boolean;
  maxDepth?: number;
  className?: string;
}

const CategoryTreeNode: React.FC<CategoryTreeNodeProps> = memo(({
  category,
  level,
  onCategorySelect,
  onCategoryExpand,
  selectedCategoryId,
  showProductCount = true,
  maxDepth,
  className = ''
}) => {
  const navigate = useNavigate();
  const hasChildren = category.children && category.children.length > 0;
  const isSelected = selectedCategoryId === category.id;
  const isExpanded = category.isExpanded;
  const shouldShowChildren = hasChildren && isExpanded && (!maxDepth || level < maxDepth);

  const handleToggleExpand = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasChildren && onCategoryExpand) {
      onCategoryExpand(category.id, !isExpanded);
    }
  }, [hasChildren, onCategoryExpand, category.id, isExpanded]);

  const handleCategoryClick = useCallback(() => {
    if (onCategorySelect) {
      onCategorySelect(category);
    } else {
      // Default navigation behavior
      navigate(`/categories/${category.slug}`);
    }
  }, [onCategorySelect, category, navigate]);

  const IconComponent = useMemo(() => {
    if (hasChildren) {
      return isExpanded ? FolderOpen : Folder;
    }
    return Package;
  }, [hasChildren, isExpanded]);

  const ChevronComponent = useMemo(() => {
    if (!hasChildren) return null;
    return isExpanded ? ChevronDown : ChevronRight;
  }, [hasChildren, isExpanded]);

  return (
    <div className={`category-tree-node ${className}`}>
      <div
        className={`
          flex items-center gap-2 py-2 px-3 cursor-pointer rounded-md transition-all duration-200
          hover:bg-gray-50 dark:hover:bg-gray-800
          ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500' : ''}
          ${!category.is_active ? 'opacity-50' : ''}
        `}
        style={{ marginLeft: `${level * 20}px` }}
        onClick={handleCategoryClick}
      >
        {/* Expand/Collapse Button */}
        <button
          onClick={handleToggleExpand}
          className={`
            flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-sm
            hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors
            ${hasChildren ? 'visible' : 'invisible'}
          `}
          aria-label={isExpanded ? 'Collapse category' : 'Expand category'}
        >
          {ChevronComponent && <ChevronComponent size={14} />}
        </button>

        {/* Category Icon */}
        <div className="flex-shrink-0 w-5 h-5 text-gray-500 dark:text-gray-400">
          {category.icon ? (
            <img
              src={category.icon}
              alt={category.name}
              className="w-full h-full object-contain"
            />
          ) : (
            <IconComponent size={16} />
          )}
        </div>

        {/* Category Name */}
        <span
          className={`
            flex-1 text-sm font-medium truncate
            ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'}
          `}
          title={category.name}
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
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }
            `}
          >
            {category.product_count}
          </span>
        )}

        {/* Inactive Indicator */}
        {!category.is_active && (
          <span className="flex-shrink-0 px-2 py-1 text-xs bg-red-100 text-red-600 rounded-full dark:bg-red-900/20 dark:text-red-400">
            Inactive
          </span>
        )}
      </div>

      {/* Children */}
      {shouldShowChildren && (
        <div className="category-tree-children">
          {category.children.map((child) => (
            <CategoryTreeNode
              key={child.id}
              category={child}
              level={level + 1}
              onCategorySelect={onCategorySelect}
              onCategoryExpand={onCategoryExpand}
              selectedCategoryId={selectedCategoryId}
              showProductCount={showProductCount}
              maxDepth={maxDepth}
              className={className}
            />
          ))}
        </div>
      )}
    </div>
  );
});

CategoryTreeNode.displayName = 'CategoryTreeNode';

// Main CategoryTree component
const CategoryTree: React.FC<CategoryTreeProps> = ({
  data,
  onCategorySelect,
  onCategoryExpand,
  selectedCategoryId,
  expandedCategories,
  showProductCount = true,
  maxDepth,
  className = ''
}) => {
  const { toggleExpansion, expandAll, collapseAll } = useCategoryTree();

  // Use provided data or fallback to store data
  const treeData = useMemo(() => {
    if (data && data.length > 0) {
      return data;
    }
    return [];
  }, [data]);

  const handleCategoryExpand = useCallback((categoryId: string, isExpanded: boolean) => {
    if (onCategoryExpand) {
      onCategoryExpand(categoryId, isExpanded);
    } else {
      toggleExpansion(categoryId);
    }
  }, [onCategoryExpand, toggleExpansion]);

  const hasCategories = treeData.length > 0;
  const hasExpandableCategories = useMemo(() => {
    const hasExpandable = (categories: CategoryTreeType[]): boolean => {
      return categories.some(cat =>
        (cat.children && cat.children.length > 0) ||
        hasExpandable(cat.children || [])
      );
    };
    return hasExpandable(treeData);
  }, [treeData]);

  if (!hasCategories) {
    return (
      <div className={`category-tree-empty ${className}`}>
        <div className="flex flex-col items-center justify-center py-8 text-gray-500 dark:text-gray-400">
          <Folder size={48} className="mb-4 opacity-50" />
          <p className="text-sm font-medium">No categories found</p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Categories will appear here once they are created
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`category-tree ${className}`}>
      {/* Tree Controls */}
      {hasExpandableCategories && (
        <div className="category-tree-controls flex gap-2 mb-4 p-2 bg-gray-50 dark:bg-gray-800 rounded-md">
          <button
            onClick={expandAll}
            className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            Collapse All
          </button>
        </div>
      )}

      {/* Tree Structure */}
      <div className="category-tree-content space-y-1">
        {treeData.map((category) => (
          <CategoryTreeNode
            key={category.id}
            category={category}
            level={0}
            onCategorySelect={onCategorySelect}
            onCategoryExpand={handleCategoryExpand}
            selectedCategoryId={selectedCategoryId}
            showProductCount={showProductCount}
            maxDepth={maxDepth}
            className={className}
          />
        ))}
      </div>

      {/* Tree Stats */}
      {showProductCount && (
        <div className="category-tree-stats mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Total Categories: {treeData.length} |
            Total Products: {treeData.reduce((sum, cat) => sum + (cat.product_count || 0), 0)}
          </div>
        </div>
      )}
    </div>
  );
};

export default memo(CategoryTree);