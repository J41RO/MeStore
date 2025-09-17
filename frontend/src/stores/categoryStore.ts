import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  Category,
  CategoryTree,
  CategoryFilter,
  CategoryBreadcrumb,
  CategoryStats,
  CategoryState,
  CategoryActions,
  CategoryStore,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CategorySearchParams
} from '../types/category.types';
import { categoryService } from '../services/categoryService';

const initialState: CategoryState = {
  // Data
  categories: [],
  categoryTree: [],
  selectedCategory: null,
  breadcrumb: [],

  // UI State
  isLoading: false,
  error: null,
  expandedCategories: [],
  selectedCategories: [],

  // Filters
  activeFilters: {
    category_ids: [],
    include_subcategories: true,
  },
  searchQuery: '',

  // Stats
  stats: null,
};

export const useCategoryStore = create<CategoryStore>()(
  persist(
    immer((set, get) => ({
      ...initialState,

      // Data Actions
      loadCategories: async () => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const response = await categoryService.getCategories();
          set((state) => {
            state.categories = response.categories;
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.error = error.message;
            state.isLoading = false;
          });
        }
      },

      loadCategoryTree: async () => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const response = await categoryService.getCategoryTree();
          set((state) => {
            state.categoryTree = response.tree;
            state.stats = response.stats;
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.error = error.message;
            state.isLoading = false;
          });
        }
      },

      createCategory: async (data: CreateCategoryRequest) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const newCategory = await categoryService.createCategory(data);
          set((state) => {
            state.categories.push(newCategory);
            state.isLoading = false;
          });

          // Reload tree to reflect changes
          get().loadCategoryTree();
          return newCategory;
        } catch (error: any) {
          set((state) => {
            state.error = error.message;
            state.isLoading = false;
          });
          throw error;
        }
      },

      updateCategory: async (data: UpdateCategoryRequest) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const updatedCategory = await categoryService.updateCategory(data.id, data);
          set((state) => {
            const index = state.categories.findIndex(cat => cat.id === data.id);
            if (index !== -1) {
              state.categories[index] = updatedCategory;
            }
            state.isLoading = false;
          });

          // Reload tree to reflect changes
          get().loadCategoryTree();
          return updatedCategory;
        } catch (error: any) {
          set((state) => {
            state.error = error.message;
            state.isLoading = false;
          });
          throw error;
        }
      },

      deleteCategory: async (id: string) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          await categoryService.deleteCategory(id);
          set((state) => {
            state.categories = state.categories.filter(cat => cat.id !== id);
            if (state.selectedCategory?.id === id) {
              state.selectedCategory = null;
            }
            state.isLoading = false;
          });

          // Reload tree to reflect changes
          get().loadCategoryTree();
        } catch (error: any) {
          set((state) => {
            state.error = error.message;
            state.isLoading = false;
          });
          throw error;
        }
      },

      // Selection Actions
      selectCategory: (category: Category) => {
        set((state) => {
          state.selectedCategory = category;
          state.breadcrumb = get().getCategoryPath(category.id);
        });
      },

      clearSelection: () => {
        set((state) => {
          state.selectedCategory = null;
          state.breadcrumb = [];
        });
      },

      // UI Actions
      toggleCategoryExpansion: (categoryId: string) => {
        set((state) => {
          const index = state.expandedCategories.indexOf(categoryId);
          if (index === -1) {
            state.expandedCategories.push(categoryId);
          } else {
            state.expandedCategories.splice(index, 1);
          }
        });
      },

      expandAllCategories: () => {
        const allCategoryIds = categoryService.flattenCategoryTree(get().categoryTree)
          .map(cat => cat.id);
        set((state) => {
          state.expandedCategories = allCategoryIds;
        });
      },

      collapseAllCategories: () => {
        set((state) => {
          state.expandedCategories = [];
        });
      },

      // Filter Actions
      setFilters: (filters: Partial<CategoryFilter>) => {
        set((state) => {
          state.activeFilters = { ...state.activeFilters, ...filters };
        });
      },

      clearFilters: () => {
        set((state) => {
          state.activeFilters = {
            category_ids: [],
            include_subcategories: true,
          };
        });
      },

      setSearchQuery: (query: string) => {
        set((state) => {
          state.searchQuery = query;
        });
      },

      // Utility Actions
      getCategoryPath: (categoryId: string): CategoryBreadcrumb[] => {
        const { categories } = get();
        const ancestors = categoryService.getCategoryAncestors(categoryId, categories);
        const currentCategory = categories.find(cat => cat.id === categoryId);

        const path: CategoryBreadcrumb[] = ancestors.map(cat => ({
          id: cat.id,
          name: cat.name,
          slug: cat.slug,
          url: `/categories/${cat.slug}`,
        }));

        if (currentCategory) {
          path.push({
            id: currentCategory.id,
            name: currentCategory.name,
            slug: currentCategory.slug,
            url: `/categories/${currentCategory.slug}`,
          });
        }

        return path;
      },

      getCategoryChildren: (categoryId: string): Category[] => {
        const { categories } = get();
        return categories.filter(cat => cat.parent_id === categoryId);
      },

      getCategoryParents: (categoryId: string): Category[] => {
        const { categories } = get();
        return categoryService.getCategoryAncestors(categoryId, categories);
      },

      // Reset Actions
      reset: () => {
        set(() => ({ ...initialState }));
      },
    })),
    {
      name: 'category-storage',
      partialize: (state) => ({
        expandedCategories: state.expandedCategories,
        selectedCategories: state.selectedCategories,
        activeFilters: state.activeFilters,
        searchQuery: state.searchQuery,
      }),
    }
  )
);

// Selectors for performance optimization
export const categorySelectors = {
  // Get root categories (no parent)
  getRootCategories: (state: CategoryStore) =>
    state.categories.filter(cat => !cat.parent_id),

  // Get categories by level
  getCategoriesByLevel: (state: CategoryStore, level: number) =>
    state.categories.filter(cat => cat.level === level),

  // Get active categories
  getActiveCategories: (state: CategoryStore) =>
    state.categories.filter(cat => cat.is_active),

  // Get categories with products
  getCategoriesWithProducts: (state: CategoryStore) =>
    state.categories.filter(cat => cat.product_count && cat.product_count > 0),

  // Check if category is expanded
  isCategoryExpanded: (state: CategoryStore, categoryId: string) =>
    state.expandedCategories.includes(categoryId),

  // Check if category is selected
  isCategorySelected: (state: CategoryStore, categoryId: string) =>
    state.selectedCategories.includes(categoryId),

  // Get filtered categories based on search
  getFilteredCategories: (state: CategoryStore) => {
    const { categories, searchQuery, activeFilters } = state;
    let filtered = [...categories];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(cat =>
        cat.name.toLowerCase().includes(query) ||
        (cat.description && cat.description.toLowerCase().includes(query))
      );
    }

    // Apply category filters
    if (activeFilters.category_ids.length > 0) {
      if (activeFilters.include_subcategories) {
        // Include subcategories
        const allRelevantIds = new Set<string>();
        activeFilters.category_ids.forEach(categoryId => {
          allRelevantIds.add(categoryId);
          const descendants = categoryService.getCategoryDescendants(categoryId, categories);
          descendants.forEach(desc => allRelevantIds.add(desc.id));
        });
        filtered = filtered.filter(cat => allRelevantIds.has(cat.id));
      } else {
        // Only exact matches
        filtered = filtered.filter(cat => activeFilters.category_ids.includes(cat.id));
      }
    }

    return filtered;
  },

  // Get category tree with current state
  getCategoryTreeWithState: (state: CategoryStore) => {
    const { categoryTree, expandedCategories, selectedCategories } = state;

    const addStateToTree = (nodes: CategoryTree[]): CategoryTree[] => {
      return nodes.map(node => ({
        ...node,
        isExpanded: expandedCategories.includes(node.id),
        isSelected: selectedCategories.includes(node.id),
        children: addStateToTree(node.children),
      }));
    };

    return addStateToTree(categoryTree);
  },
};

export default useCategoryStore;