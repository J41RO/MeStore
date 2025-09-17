import React, { useMemo } from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  CategoryBreadcrumbProps,
  CategoryBreadcrumb as CategoryBreadcrumbType
} from '../../types/category.types';
import { useCategoryBreadcrumb } from '../../hooks/useCategories';

// Individual breadcrumb item component
interface BreadcrumbItemProps {
  item: CategoryBreadcrumbType;
  isLast: boolean;
  onClick: (item: CategoryBreadcrumbType) => void;
  separator: string;
}

const BreadcrumbItem: React.FC<BreadcrumbItemProps> = ({
  item,
  isLast,
  onClick,
  separator
}) => {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onClick(item);
  };

  return (
    <div className="flex items-center">
      {isLast ? (
        // Last item - not clickable
        <span
          className="text-gray-600 dark:text-gray-300 font-medium truncate max-w-[200px]"
          title={item.name}
        >
          {item.name}
        </span>
      ) : (
        // Clickable item
        <>
          <button
            onClick={handleClick}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:underline transition-colors truncate max-w-[200px]"
            title={item.name}
          >
            {item.name}
          </button>
          <span className="mx-2 text-gray-400 dark:text-gray-600 flex-shrink-0">
            {separator === 'chevron' ? <ChevronRight size={14} /> : separator}
          </span>
        </>
      )}
    </div>
  );
};

// Home breadcrumb item
interface HomeBreadcrumbProps {
  onClick: () => void;
  separator: string;
  label?: string;
}

const HomeBreadcrumb: React.FC<HomeBreadcrumbProps> = ({
  onClick,
  separator,
  label = 'Home'
}) => {
  return (
    <div className="flex items-center">
      <button
        onClick={onClick}
        className="flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:underline transition-colors"
        title="Go to home"
      >
        <Home size={14} />
        <span className="hidden sm:inline">{label}</span>
      </button>
      <span className="mx-2 text-gray-400 dark:text-gray-600 flex-shrink-0">
        {separator === 'chevron' ? <ChevronRight size={14} /> : separator}
      </span>
    </div>
  );
};

// Collapsed breadcrumb indicator
interface CollapsedBreadcrumbProps {
  onClick: () => void;
  separator: string;
}

const CollapsedBreadcrumb: React.FC<CollapsedBreadcrumbProps> = ({
  onClick,
  separator
}) => {
  return (
    <div className="flex items-center">
      <button
        onClick={onClick}
        className="px-2 py-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
        title="Show all breadcrumbs"
      >
        ...
      </button>
      <span className="mx-2 text-gray-400 dark:text-gray-600 flex-shrink-0">
        {separator === 'chevron' ? <ChevronRight size={14} /> : separator}
      </span>
    </div>
  );
};

// Main CategoryBreadcrumb component
const CategoryBreadcrumb: React.FC<CategoryBreadcrumbProps> = ({
  categoryId,
  customPath,
  onNavigate,
  separator = 'chevron',
  showHome = true,
  className = ''
}) => {
  const navigate = useNavigate();
  const { breadcrumb: hookBreadcrumb, isLoading } = useCategoryBreadcrumb(categoryId);

  // Use custom path or hook breadcrumb
  const breadcrumbPath = useMemo(() => {
    return customPath || hookBreadcrumb;
  }, [customPath, hookBreadcrumb]);

  // State for collapsed view
  const [isExpanded, setIsExpanded] = React.useState(false);

  // Determine if we should collapse breadcrumbs
  const shouldCollapse = breadcrumbPath.length > 4;
  const maxVisibleItems = 3;

  // Get visible breadcrumb items
  const visibleBreadcrumbs = useMemo(() => {
    if (!shouldCollapse || isExpanded) {
      return breadcrumbPath;
    }

    // Show first item, ellipsis, and last 2 items
    if (breadcrumbPath.length <= maxVisibleItems) {
      return breadcrumbPath;
    }

    return [
      breadcrumbPath[0],
      ...breadcrumbPath.slice(-2)
    ];
  }, [breadcrumbPath, shouldCollapse, isExpanded, maxVisibleItems]);

  // Handle navigation
  const handleNavigate = (item: CategoryBreadcrumbType) => {
    if (onNavigate) {
      onNavigate(item);
    } else {
      // Default navigation behavior
      navigate(item.url);
    }
  };

  // Handle home navigation
  const handleHomeNavigate = () => {
    if (onNavigate) {
      onNavigate({
        id: 'home',
        name: 'Home',
        slug: '',
        url: '/'
      });
    } else {
      navigate('/');
    }
  };

  // Handle expand collapsed breadcrumbs
  const handleExpandCollapsed = () => {
    setIsExpanded(true);
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className={`category-breadcrumb ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          <ChevronRight size={14} className="text-gray-400" />
          <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        </div>
      </div>
    );
  }

  // Don't render if no breadcrumb path
  if (!breadcrumbPath || breadcrumbPath.length === 0) {
    return null;
  }

  return (
    <nav
      className={`category-breadcrumb ${className}`}
      aria-label="Category breadcrumb"
    >
      <div className="flex items-center flex-wrap gap-1 text-sm">
        {/* Home breadcrumb */}
        {showHome && (
          <HomeBreadcrumb
            onClick={handleHomeNavigate}
            separator={separator}
          />
        )}

        {/* Category breadcrumbs */}
        {shouldCollapse && !isExpanded && (
          <>
            <BreadcrumbItem
              item={visibleBreadcrumbs[0]}
              isLast={false}
              onClick={handleNavigate}
              separator={separator}
            />
            <CollapsedBreadcrumb
              onClick={handleExpandCollapsed}
              separator={separator}
            />
            {visibleBreadcrumbs.slice(1).map((item, index) => (
              <BreadcrumbItem
                key={item.id}
                item={item}
                isLast={index === visibleBreadcrumbs.length - 2}
                onClick={handleNavigate}
                separator={separator}
              />
            ))}
          </>
        )}

        {(!shouldCollapse || isExpanded) && (
          breadcrumbPath.map((item, index) => (
            <BreadcrumbItem
              key={item.id}
              item={item}
              isLast={index === breadcrumbPath.length - 1}
              onClick={handleNavigate}
              separator={separator}
            />
          ))
        )}
      </div>

      {/* Schema.org structured data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            itemListElement: [
              ...(showHome ? [{
                '@type': 'ListItem',
                position: 1,
                name: 'Home',
                item: window.location.origin
              }] : []),
              ...breadcrumbPath.map((item, index) => ({
                '@type': 'ListItem',
                position: (showHome ? 2 : 1) + index,
                name: item.name,
                item: `${window.location.origin}${item.url}`
              }))
            ]
          })
        }}
      />
    </nav>
  );
};

// Responsive breadcrumb variant for mobile
export const ResponsiveCategoryBreadcrumb: React.FC<CategoryBreadcrumbProps> = (props) => {
  return (
    <div className="w-full">
      {/* Mobile version - show only current category */}
      <div className="sm:hidden">
        <CategoryBreadcrumb
          {...props}
          showHome={false}
          className="truncate"
        />
      </div>

      {/* Desktop version - show full breadcrumb */}
      <div className="hidden sm:block">
        <CategoryBreadcrumb {...props} />
      </div>
    </div>
  );
};

// Compact breadcrumb variant
export const CompactCategoryBreadcrumb: React.FC<CategoryBreadcrumbProps> = (props) => {
  const { breadcrumb } = useCategoryBreadcrumb(props.categoryId);

  if (!breadcrumb || breadcrumb.length === 0) {
    return null;
  }

  const lastCategory = breadcrumb[breadcrumb.length - 1];

  return (
    <div className={`compact-category-breadcrumb ${props.className || ''}`}>
      <span className="text-xs text-gray-500 dark:text-gray-400">
        in{' '}
        <button
          onClick={() => props.onNavigate?.(lastCategory)}
          className="text-blue-600 dark:text-blue-400 hover:underline"
        >
          {lastCategory.name}
        </button>
      </span>
    </div>
  );
};

export default CategoryBreadcrumb;