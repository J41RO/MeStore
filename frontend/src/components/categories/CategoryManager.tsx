import React, { useState, useCallback, useMemo } from 'react';
import {
  Plus,
  Edit2,
  Trash2,
  Move,
  Save,
  X,
  Search,
  Filter,
  MoreVertical,
  Eye,
  EyeOff,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import { useCategoryManagement, useCategorySearch } from '../../hooks/useCategories';
import { useAuthStore } from '../../stores/authStore';
import {
  Category,
  CategoryManagerProps,
  CreateCategoryRequest,
  UpdateCategoryRequest
} from '../../types/category.types';

// Category form component
interface CategoryFormProps {
  category?: Category;
  parentCategories: Category[];
  onSave: (data: CreateCategoryRequest | UpdateCategoryRequest) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

const CategoryForm: React.FC<CategoryFormProps> = ({
  category,
  parentCategories,
  onSave,
  onCancel,
  isLoading
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<CreateCategoryRequest>({
    defaultValues: {
      name: category?.name || '',
      description: category?.description || '',
      parent_id: category?.parent_id || null,
      is_active: category?.is_active ?? true,
      sort_order: category?.sort_order || 0,
      icon: category?.icon || '',
    }
  });

  const onSubmit = useCallback(async (data: CreateCategoryRequest) => {
    try {
      if (category) {
        await onSave({ ...data, id: category.id } as UpdateCategoryRequest);
      } else {
        await onSave(data);
      }
      reset();
    } catch (error) {
      console.error('Error saving category:', error);
    }
  }, [category, onSave, reset]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {category ? 'Edit Category' : 'Create Category'}
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name *
            </label>
            <input
              {...register('name', { required: 'Name is required' })}
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="Category name"
            />
            {errors.name && (
              <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="Category description"
            />
          </div>

          {/* Parent Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Parent Category
            </label>
            <select
              {...register('parent_id')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">No parent (Root category)</option>
              {parentCategories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {'  '.repeat(cat.level)}{cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Icon URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Icon URL
            </label>
            <input
              {...register('icon')}
              type="url"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="https://example.com/icon.svg"
            />
          </div>

          {/* Sort Order */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Sort Order
            </label>
            <input
              {...register('sort_order', { valueAsNumber: true })}
              type="number"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="0"
            />
          </div>

          {/* Active Status */}
          <div className="flex items-center">
            <input
              {...register('is_active')}
              type="checkbox"
              id="is_active"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Active
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save size={16} />
              {isLoading ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Category item component with actions
interface CategoryItemProps {
  category: Category;
  onEdit: (category: Category) => void;
  onDelete: (category: Category) => void;
  onToggleActive: (category: Category) => void;
  onMove: (category: Category, direction: 'up' | 'down') => void;
  isLast: boolean;
  isFirst: boolean;
}

const CategoryItem: React.FC<CategoryItemProps> = ({
  category,
  onEdit,
  onDelete,
  onToggleActive,
  onMove,
  isLast,
  isFirst
}) => {
  const [showActions, setShowActions] = useState(false);

  return (
    <div
      className={`
        group flex items-center gap-3 p-3 border rounded-lg transition-all duration-200
        ${category.is_active ? 'border-gray-200 dark:border-gray-700' : 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10'}
        hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm
      `}
      style={{ marginLeft: `${category.level * 20}px` }}
    >
      {/* Category Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          {category.icon && (
            <img
              src={category.icon}
              alt={category.name}
              className="w-5 h-5 object-contain"
            />
          )}
          <h4 className={`font-medium truncate ${!category.is_active ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>
            {category.name}
          </h4>
          {!category.is_active && (
            <span className="flex-shrink-0 px-2 py-1 text-xs bg-red-100 text-red-600 rounded-full dark:bg-red-900/20 dark:text-red-400">
              Inactive
            </span>
          )}
        </div>
        {category.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
            {category.description}
          </p>
        )}
        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>Level {category.level}</span>
          {category.product_count !== undefined && (
            <span>{category.product_count} products</span>
          )}
          <span>Order: {category.sort_order}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {/* Move buttons */}
        <button
          onClick={() => onMove(category, 'up')}
          disabled={isFirst}
          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
          title="Move up"
        >
          <ArrowUp size={14} />
        </button>
        <button
          onClick={() => onMove(category, 'down')}
          disabled={isLast}
          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
          title="Move down"
        >
          <ArrowDown size={14} />
        </button>

        {/* Toggle active */}
        <button
          onClick={() => onToggleActive(category)}
          className="p-1 text-gray-400 hover:text-gray-600"
          title={category.is_active ? 'Deactivate' : 'Activate'}
        >
          {category.is_active ? <EyeOff size={14} /> : <Eye size={14} />}
        </button>

        {/* Edit */}
        <button
          onClick={() => onEdit(category)}
          className="p-1 text-blue-400 hover:text-blue-600"
          title="Edit category"
        >
          <Edit2 size={14} />
        </button>

        {/* Delete */}
        <button
          onClick={() => onDelete(category)}
          className="p-1 text-red-400 hover:text-red-600"
          title="Delete category"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
};

// Main CategoryManager component
const CategoryManager: React.FC<CategoryManagerProps> = ({
  onCategoryCreate,
  onCategoryUpdate,
  onCategoryDelete,
  allowDragDrop = false,
  className = ''
}) => {
  const { isAdmin } = useAuthStore();
  const {
    categories,
    isLoading,
    error,
    createCategory,
    updateCategory,
    deleteCategory,
    loadCategories
  } = useCategoryManagement();

  const { searchQuery, searchResults, setSearchQuery } = useCategorySearch();

  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [deletingCategory, setDeletingCategory] = useState<Category | null>(null);
  const [showInactive, setShowInactive] = useState(false);

  // Check permissions
  if (!isAdmin()) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 dark:text-red-400">
          You don't have permission to manage categories.
        </p>
      </div>
    );
  }

  // Filter categories
  const filteredCategories = useMemo(() => {
    let filtered = searchQuery ? searchResults : categories;
    if (!showInactive) {
      filtered = filtered.filter(cat => cat.is_active);
    }
    return filtered.sort((a, b) => {
      if (a.level !== b.level) return a.level - b.level;
      return a.sort_order - b.sort_order;
    });
  }, [searchQuery, searchResults, categories, showInactive]);

  // Valid parent categories (exclude current category and its descendants)
  const validParentCategories = useMemo(() => {
    return categories.filter(cat => {
      if (editingCategory && cat.id === editingCategory.id) return false;
      // Add logic to exclude descendants if needed
      return true;
    });
  }, [categories, editingCategory]);

  // Handle form submission
  const handleSaveCategory = useCallback(async (data: CreateCategoryRequest | UpdateCategoryRequest) => {
    try {
      let result;
      if ('id' in data) {
        result = await updateCategory(data);
        onCategoryUpdate?.(result.data!);
      } else {
        result = await createCategory(data);
        onCategoryCreate?.(result.data!);
      }

      if (result.success) {
        setShowForm(false);
        setEditingCategory(null);
        loadCategories();
      }
    } catch (error) {
      console.error('Error saving category:', error);
    }
  }, [createCategory, updateCategory, onCategoryCreate, onCategoryUpdate, loadCategories]);

  // Handle delete
  const handleDeleteCategory = useCallback(async (category: Category) => {
    try {
      const result = await deleteCategory(category.id);
      if (result.success) {
        onCategoryDelete?.(category.id);
        setDeletingCategory(null);
        loadCategories();
      }
    } catch (error) {
      console.error('Error deleting category:', error);
    }
  }, [deleteCategory, onCategoryDelete, loadCategories]);

  // Handle toggle active
  const handleToggleActive = useCallback(async (category: Category) => {
    try {
      const result = await updateCategory({
        id: category.id,
        is_active: !category.is_active
      });
      if (result.success) {
        loadCategories();
      }
    } catch (error) {
      console.error('Error toggling category status:', error);
    }
  }, [updateCategory, loadCategories]);

  // Handle move (simple sort_order adjustment)
  const handleMoveCategory = useCallback(async (category: Category, direction: 'up' | 'down') => {
    const siblings = categories.filter(cat => cat.parent_id === category.parent_id);
    const currentIndex = siblings.findIndex(cat => cat.id === category.id);
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;

    if (newIndex >= 0 && newIndex < siblings.length) {
      const targetCategory = siblings[newIndex];

      try {
        await Promise.all([
          updateCategory({
            id: category.id,
            sort_order: targetCategory.sort_order
          }),
          updateCategory({
            id: targetCategory.id,
            sort_order: category.sort_order
          })
        ]);
        loadCategories();
      } catch (error) {
        console.error('Error moving category:', error);
      }
    }
  }, [categories, updateCategory, loadCategories]);

  return (
    <div className={`category-manager ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Category Management
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your marketplace categories
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus size={16} />
          Add Category
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        <button
          onClick={() => setShowInactive(!showInactive)}
          className={`flex items-center gap-2 px-4 py-2 rounded-md border ${
            showInactive
              ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300'
              : 'bg-white border-gray-300 text-gray-700 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300'
          }`}
        >
          <Filter size={16} />
          {showInactive ? 'Hide Inactive' : 'Show Inactive'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Categories List */}
      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredCategories.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No categories found matching your search.' : 'No categories created yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredCategories.map((category, index) => (
            <CategoryItem
              key={category.id}
              category={category}
              onEdit={setEditingCategory}
              onDelete={setDeletingCategory}
              onToggleActive={handleToggleActive}
              onMove={handleMoveCategory}
              isFirst={index === 0}
              isLast={index === filteredCategories.length - 1}
            />
          ))}
        </div>
      )}

      {/* Category Form Modal */}
      {(showForm || editingCategory) && (
        <CategoryForm
          category={editingCategory || undefined}
          parentCategories={validParentCategories}
          onSave={handleSaveCategory}
          onCancel={() => {
            setShowForm(false);
            setEditingCategory(null);
          }}
          isLoading={isLoading}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deletingCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Delete Category
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Are you sure you want to delete "{deletingCategory.name}"? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleDeleteCategory(deletingCategory)}
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {isLoading ? 'Deleting...' : 'Delete'}
              </button>
              <button
                onClick={() => setDeletingCategory(null)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-600 dark:text-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoryManager;