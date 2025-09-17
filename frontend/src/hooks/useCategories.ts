import { useCallback, useEffect, useMemo } from 'react';
import { useCategoryStore, categorySelectors } from '../stores/categoryStore';
import {
  Category,
  CategoryTree,
  CategoryFilter,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CategorySearchParams
} from '../types/category.types';

// Main hook for category management
export const useCategories = () => {
  const store = useCategoryStore();

  // Load categories on mount if not already loaded
  useEffect(() => {
    if (store.categories.length === 0 && !store.isLoading) {
      store.loadCategories();
    }
  }, [store.categories.length, store.isLoading, store.loadCategories]);

  // Load category tree on mount if not already loaded
  useEffect(() => {
    if (store.categoryTree.length === 0 && !store.isLoading) {
      store.loadCategoryTree();
    }
  }, [store.categoryTree.length, store.isLoading, store.loadCategoryTree]);

  return {
    // Data
    categories: store.categories,
    categoryTree: store.categoryTree,
    selectedCategory: store.selectedCategory,
    breadcrumb: store.breadcrumb,
    stats: store.stats,

    // UI State
    isLoading: store.isLoading,
    error: store.error,
    searchQuery: store.searchQuery,
    activeFilters: store.activeFilters,

    // Actions
    loadCategories: store.loadCategories,
    loadCategoryTree: store.loadCategoryTree,
    createCategory: store.createCategory,
    updateCategory: store.updateCategory,
    deleteCategory: store.deleteCategory,
    selectCategory: store.selectCategory,
    clearSelection: store.clearSelection,
    setFilters: store.setFilters,
    clearFilters: store.clearFilters,
    setSearchQuery: store.setSearchQuery,
    reset: store.reset,

    // Utility methods
    getCategoryPath: store.getCategoryPath,
    getCategoryChildren: store.getCategoryChildren,
    getCategoryParents: store.getCategoryParents,
  };
};

// Hook for category tree operations
export const useCategoryTree = () => {
  const store = useCategoryStore();

  const categoryTreeWithState = useMemo(
    () => categorySelectors.getCategoryTreeWithState(store),
    [store.categoryTree, store.expandedCategories, store.selectedCategories]
  );

  const toggleExpansion = useCallback((categoryId: string) => {
    store.toggleCategoryExpansion(categoryId);
  }, [store.toggleCategoryExpansion]);

  const expandAll = useCallback(() => {
    store.expandAllCategories();
  }, [store.expandAllCategories]);

  const collapseAll = useCallback(() => {
    store.collapseAllCategories();
  }, [store.collapseAllCategories]);

  return {
    categoryTree: categoryTreeWithState,
    expandedCategories: store.expandedCategories,
    isLoading: store.isLoading,
    error: store.error,
    toggleExpansion,
    expandAll,
    collapseAll,
  };
};

// Hook for category selection (for vendor product assignment)
export const useCategorySelection = (
  maxSelections?: number,
  allowMultiple = true
) => {
  const store = useCategoryStore();

  const toggleSelection = useCallback((categoryId: string) => {
    const { selectedCategories } = store;
    const isSelected = selectedCategories.includes(categoryId);

    if (!allowMultiple) {
      // Single selection mode
      store.selectedCategories = [categoryId];
      return;
    }

    if (isSelected) {
      // Deselect
      const newSelected = selectedCategories.filter(id => id !== categoryId);
      store.selectedCategories = newSelected;
    } else {
      // Select (if under limit)
      if (!maxSelections || selectedCategories.length < maxSelections) {
        store.selectedCategories = [...selectedCategories, categoryId];
      }
    }
  }, [store, maxSelections, allowMultiple]);

  const clearSelection = useCallback(() => {
    store.selectedCategories = [];
  }, [store]);

  const isSelected = useCallback((categoryId: string) => {
    return store.selectedCategories.includes(categoryId);
  }, [store.selectedCategories]);

  const canSelect = useCallback((categoryId: string) => {
    if (store.selectedCategories.includes(categoryId)) {
      return false; // Already selected
    }
    if (!maxSelections) {
      return true; // No limit
    }
    return store.selectedCategories.length < maxSelections;
  }, [store.selectedCategories, maxSelections]);

  return {
    selectedCategories: store.selectedCategories,
    toggleSelection,
    clearSelection,
    isSelected,
    canSelect,
    isAtLimit: maxSelections ? store.selectedCategories.length >= maxSelections : false,
  };
};

// Hook for category filtering (for buyer product search)
export const useCategoryFilter = () => {
  const store = useCategoryStore();

  const filteredCategories = useMemo(
    () => categorySelectors.getFilteredCategories(store),
    [store.categories, store.searchQuery, store.activeFilters]
  );

  const toggleCategoryFilter = useCallback((categoryId: string) => {
    const { activeFilters } = store;
    const isFiltered = activeFilters.category_ids.includes(categoryId);

    if (isFiltered) {
      store.setFilters({
        category_ids: activeFilters.category_ids.filter(id => id !== categoryId)
      });
    } else {
      store.setFilters({
        category_ids: [...activeFilters.category_ids, categoryId]
      });
    }
  }, [store]);

  const setIncludeSubcategories = useCallback((include: boolean) => {
    store.setFilters({ include_subcategories: include });
  }, [store]);

  return {
    filteredCategories,
    activeFilters: store.activeFilters,
    searchQuery: store.searchQuery,
    toggleCategoryFilter,
    setIncludeSubcategories,
    setSearchQuery: store.setSearchQuery,
    clearFilters: store.clearFilters,
  };
};

// Hook for category management (admin operations)
export const useCategoryManagement = () => {
  const store = useCategoryStore();

  const createCategory = useCallback(async (data: CreateCategoryRequest) => {
    try {
      const newCategory = await store.createCategory(data);
      return { success: true, data: newCategory };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }, [store.createCategory]);

  const updateCategory = useCallback(async (data: UpdateCategoryRequest) => {
    try {
      const updatedCategory = await store.updateCategory(data);
      return { success: true, data: updatedCategory };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }, [store.updateCategory]);

  const deleteCategory = useCallback(async (id: string) => {
    try {
      await store.deleteCategory(id);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }, [store.deleteCategory]);

  return {
    categories: store.categories,
    categoryTree: store.categoryTree,
    isLoading: store.isLoading,
    error: store.error,
    createCategory,
    updateCategory,
    deleteCategory,
    loadCategories: store.loadCategories,
    loadCategoryTree: store.loadCategoryTree,
  };
};

// Hook for category breadcrumb navigation
export const useCategoryBreadcrumb = (categoryId?: string) => {
  const store = useCategoryStore();

  const breadcrumb = useMemo(() => {
    if (!categoryId) return [];
    return store.getCategoryPath(categoryId);
  }, [categoryId, store.categories, store.getCategoryPath]);

  return {
    breadcrumb,
    isLoading: store.isLoading,
  };
};

// Hook for category statistics
export const useCategoryStats = () => {
  const store = useCategoryStore();

  useEffect(() => {
    if (!store.stats && !store.isLoading) {
      store.loadCategoryTree(); // This also loads stats
    }
  }, [store.stats, store.isLoading, store.loadCategoryTree]);

  const derivedStats = useMemo(() => {
    const rootCategories = categorySelectors.getRootCategories(store);
    const activeCategories = categorySelectors.getActiveCategories(store);
    const categoriesWithProducts = categorySelectors.getCategoriesWithProducts(store);

    return {
      ...store.stats,
      root_categories: rootCategories.length,
      active_categories: activeCategories.length,
      categories_with_products: categoriesWithProducts.length,
    };
  }, [store.stats, store.categories]);

  return {
    stats: derivedStats,
    isLoading: store.isLoading,
    error: store.error,
  };
};

// Hook for category search
export const useCategorySearch = () => {
  const store = useCategoryStore();

  const searchResults = useMemo(() => {
    if (!store.searchQuery.trim()) {
      return store.categories;
    }

    const query = store.searchQuery.toLowerCase();
    return store.categories.filter(category =>
      category.name.toLowerCase().includes(query) ||
      (category.description && category.description.toLowerCase().includes(query))
    );
  }, [store.categories, store.searchQuery]);

  return {
    searchQuery: store.searchQuery,
    searchResults,
    setSearchQuery: store.setSearchQuery,
    isLoading: store.isLoading,
  };
};

// Utility hook for category operations
export const useCategoryUtils = () => {
  const store = useCategoryStore();

  const findCategory = useCallback((categoryId: string): Category | undefined => {
    return store.categories.find(cat => cat.id === categoryId);
  }, [store.categories]);

  const findCategoryBySlug = useCallback((slug: string): Category | undefined => {
    return store.categories.find(cat => cat.slug === slug);
  }, [store.categories]);

  const getCategoryDepth = useCallback((categoryId: string): number => {
    const category = findCategory(categoryId);
    return category?.level || 0;
  }, [findCategory]);

  const hasChildren = useCallback((categoryId: string): boolean => {
    return store.categories.some(cat => cat.parent_id === categoryId);
  }, [store.categories]);

  const getChildCount = useCallback((categoryId: string): number => {
    return store.categories.filter(cat => cat.parent_id === categoryId).length;
  }, [store.categories]);

  const getTotalProductCount = useCallback((categoryId: string): number => {
    const category = findCategory(categoryId);
    if (!category) return 0;

    let totalCount = category.product_count || 0;

    // Add product count from all descendants
    const descendants = store.getCategoryChildren(categoryId);
    descendants.forEach(child => {
      totalCount += getTotalProductCount(child.id);
    });

    return totalCount;
  }, [findCategory, store.getCategoryChildren]);

  return {
    findCategory,
    findCategoryBySlug,
    getCategoryDepth,
    hasChildren,
    getChildCount,
    getTotalProductCount,
  };
};

export default useCategories;