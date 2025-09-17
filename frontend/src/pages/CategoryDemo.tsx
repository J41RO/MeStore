import React, { useState } from 'react';
import { Settings, User, ShoppingCart, Package } from 'lucide-react';
import {
  CategoryTree,
  CategoryManager,
  CategorySelector,
  CategoryBreadcrumb,
  CategoryFilter,
  ResponsiveCategoryBreadcrumb,
  CompactCategoryFilter
} from '../components/categories';
import { useCategories } from '../hooks/useCategories';
import { useAuthStore } from '../stores/authStore';
import {
  Category,
  CategoryTree as CategoryTreeType,
  CategoryFilter as CategoryFilterType
} from '../types/category.types';

// Mock data for demonstration
const mockCategoryTree: CategoryTreeType[] = [
  {
    id: '1',
    name: 'Electronics',
    description: 'Electronic devices and accessories',
    slug: 'electronics',
    parent_id: null,
    level: 0,
    is_active: true,
    sort_order: 1,
    product_count: 150,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    isExpanded: true,
    isSelected: false,
    children: [
      {
        id: '2',
        name: 'Smartphones',
        description: 'Mobile phones and accessories',
        slug: 'smartphones',
        parent_id: '1',
        level: 1,
        is_active: true,
        sort_order: 1,
        product_count: 45,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        isExpanded: false,
        isSelected: false,
        children: []
      },
      {
        id: '3',
        name: 'Laptops',
        description: 'Portable computers',
        slug: 'laptops',
        parent_id: '1',
        level: 1,
        is_active: true,
        sort_order: 2,
        product_count: 32,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        isExpanded: false,
        isSelected: false,
        children: []
      }
    ]
  },
  {
    id: '4',
    name: 'Clothing',
    description: 'Fashion and apparel',
    slug: 'clothing',
    parent_id: null,
    level: 0,
    is_active: true,
    sort_order: 2,
    product_count: 89,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    isExpanded: false,
    isSelected: false,
    children: [
      {
        id: '5',
        name: 'Men\'s Clothing',
        description: 'Clothing for men',
        slug: 'mens-clothing',
        parent_id: '4',
        level: 1,
        is_active: true,
        sort_order: 1,
        product_count: 45,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        isExpanded: false,
        isSelected: false,
        children: []
      }
    ]
  }
];

// Demo section component
interface DemoSectionProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const DemoSection: React.FC<DemoSectionProps> = ({
  title,
  description,
  icon,
  children
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              {icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {description}
              </p>
            </div>
          </div>
          <div className="text-gray-400">
            {isExpanded ? '−' : '+'}
          </div>
        </button>
      </div>
      {isExpanded && (
        <div className="p-4">
          {children}
        </div>
      )}
    </div>
  );
};

// Main demo page component
const CategoryDemo: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [categoryFilters, setCategoryFilters] = useState<CategoryFilterType>({
    category_ids: [],
    include_subcategories: true
  });

  const handleCategorySelect = (category: Category) => {
    console.log('Selected category:', category);
  };

  const handleCategoryCreate = (category: Category) => {
    console.log('Created category:', category);
  };

  const handleCategoryUpdate = (category: Category) => {
    console.log('Updated category:', category);
  };

  const handleCategoryDelete = (categoryId: string) => {
    console.log('Deleted category:', categoryId);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Category Management System Demo
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Interactive demonstration of all category components for MeStore marketplace
            </p>
            <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
              Current user: {user?.name || 'Guest'} ({user?.user_type || 'No role'})
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* CategoryTree Demo */}
          <DemoSection
            title="Category Tree"
            description="Interactive category navigation for public users"
            icon={<Package className="w-5 h-5 text-blue-600" />}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Standard Tree View
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4 max-h-96 overflow-y-auto">
                  <CategoryTree
                    data={mockCategoryTree}
                    onCategorySelect={handleCategorySelect}
                    showProductCount={true}
                    maxDepth={3}
                  />
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Compact Tree View
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4 max-h-96 overflow-y-auto">
                  <CategoryTree
                    data={mockCategoryTree}
                    onCategorySelect={handleCategorySelect}
                    showProductCount={false}
                    selectedCategoryId="2"
                  />
                </div>
              </div>
            </div>
          </DemoSection>

          {/* CategoryBreadcrumb Demo */}
          <DemoSection
            title="Category Breadcrumb"
            description="Navigation breadcrumbs for category hierarchy"
            icon={<Package className="w-5 h-5 text-blue-600" />}
          >
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Standard Breadcrumb
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4">
                  <CategoryBreadcrumb
                    customPath={[
                      { id: 'electronics', name: 'Electronics', slug: 'electronics', url: '/categories/electronics' },
                      { id: 'smartphones', name: 'Smartphones', slug: 'smartphones', url: '/categories/smartphones' }
                    ]}
                    showHome={true}
                  />
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Responsive Breadcrumb
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4">
                  <ResponsiveCategoryBreadcrumb
                    customPath={[
                      { id: 'electronics', name: 'Electronics', slug: 'electronics', url: '/categories/electronics' },
                      { id: 'smartphones', name: 'Smartphones', slug: 'smartphones', url: '/categories/smartphones' },
                      { id: 'iphones', name: 'iPhones', slug: 'iphones', url: '/categories/iphones' }
                    ]}
                  />
                </div>
              </div>
            </div>
          </DemoSection>

          {/* CategorySelector Demo */}
          <DemoSection
            title="Category Selector"
            description="Multi-select category picker for vendors"
            icon={<User className="w-5 h-5 text-blue-600" />}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Multi-Select (Max 3)
                </h4>
                <CategorySelector
                  selectedCategories={selectedCategories}
                  onSelectionChange={setSelectedCategories}
                  maxSelections={3}
                  allowMultiple={true}
                  placeholder="Select up to 3 categories..."
                />
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Single Select
                </h4>
                <CategorySelector
                  selectedCategories={selectedCategories.slice(0, 1)}
                  onSelectionChange={(cats) => setSelectedCategories(cats)}
                  allowMultiple={false}
                  placeholder="Select one category..."
                />
              </div>
            </div>
          </DemoSection>

          {/* CategoryFilter Demo */}
          <DemoSection
            title="Category Filter"
            description="Advanced filtering for product search"
            icon={<ShoppingCart className="w-5 h-5 text-blue-600" />}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Standard Filter
                </h4>
                <CategoryFilter
                  selectedFilters={categoryFilters}
                  onFiltersChange={setCategoryFilters}
                  availableCategories={mockCategoryTree}
                  showProductCount={true}
                  collapsible={false}
                />
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Compact Filter
                </h4>
                <CompactCategoryFilter
                  selectedFilters={categoryFilters}
                  onFiltersChange={setCategoryFilters}
                  availableCategories={mockCategoryTree}
                />
              </div>
            </div>
          </DemoSection>

          {/* CategoryManager Demo */}
          {user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER' ? (
            <DemoSection
              title="Category Manager"
              description="Full CRUD operations for administrators"
              icon={<Settings className="w-5 h-5 text-blue-600" />}
            >
              <div className="space-y-4">
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4">
                  <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                    <strong>Note:</strong> This is a demo version. Real CRUD operations would connect to the actual API.
                  </p>
                </div>
                <CategoryManager
                  onCategoryCreate={handleCategoryCreate}
                  onCategoryUpdate={handleCategoryUpdate}
                  onCategoryDelete={handleCategoryDelete}
                  allowDragDrop={true}
                />
              </div>
            </DemoSection>
          ) : (
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-6 text-center">
              <Settings className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Category Manager
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Admin access required to view the category management interface.
              </p>
            </div>
          )}

          {/* Integration Examples */}
          <DemoSection
            title="Integration Examples"
            description="Real-world usage patterns and combinations"
            icon={<Package className="w-5 h-5 text-blue-600" />}
          >
            <div className="space-y-6">
              {/* E-commerce Product Page */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  E-commerce Product Page Layout
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4 bg-gray-50 dark:bg-gray-800">
                  <CategoryBreadcrumb
                    customPath={[
                      { id: 'electronics', name: 'Electronics', slug: 'electronics', url: '/categories/electronics' },
                      { id: 'smartphones', name: 'Smartphones', slug: 'smartphones', url: '/categories/smartphones' }
                    ]}
                    className="mb-4"
                  />
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="lg:col-span-1">
                      <CompactCategoryFilter
                        selectedFilters={categoryFilters}
                        onFiltersChange={setCategoryFilters}
                        availableCategories={mockCategoryTree}
                      />
                    </div>
                    <div className="lg:col-span-3">
                      <div className="bg-white dark:bg-gray-700 rounded-md p-4 h-48 flex items-center justify-center">
                        <p className="text-gray-500 dark:text-gray-400">Product grid would go here</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Vendor Dashboard */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Vendor Product Creation Form
                </h4>
                <div className="border border-gray-200 dark:border-gray-700 rounded-md p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Product Name
                      </label>
                      <input
                        type="text"
                        placeholder="Enter product name"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Categories *
                      </label>
                      <CategorySelector
                        selectedCategories={selectedCategories}
                        onSelectionChange={setSelectedCategories}
                        maxSelections={5}
                        required={true}
                        placeholder="Select product categories..."
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </DemoSection>

          {/* Performance Notes */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
              Performance & Integration Notes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800 dark:text-blue-200">
              <div>
                <h4 className="font-medium mb-2">✅ Optimizations Implemented:</h4>
                <ul className="space-y-1 list-disc list-inside">
                  <li>React.memo for component memoization</li>
                  <li>useMemo for expensive calculations</li>
                  <li>useCallback for stable function references</li>
                  <li>Zustand for efficient state management</li>
                  <li>Lazy loading for large category trees</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">🔗 Integration Ready:</h4>
                <ul className="space-y-1 list-disc list-inside">
                  <li>TypeScript interfaces for type safety</li>
                  <li>Custom hooks for business logic</li>
                  <li>Service layer for API communication</li>
                  <li>Responsive design with Tailwind CSS</li>
                  <li>Accessibility features built-in</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CategoryDemo;