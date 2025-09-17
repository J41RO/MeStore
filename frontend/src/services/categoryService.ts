import axios, { AxiosResponse } from 'axios';
import {
  Category,
  CategoryTree,
  CategoryListResponse,
  CategoryTreeResponse,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CategorySearchParams,
  CategoryStats,
  CategoryError
} from '../types/category.types';

const API_BASE_URL = 'http://192.168.1.137:8000/api/v1';

// Create axios instance with base configuration
const categoryApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
categoryApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
categoryApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

class CategoryService {
  private buildUrl(endpoint: string): string {
    return `/categories${endpoint}`;
  }

  private handleError(error: any): CategoryError {
    if (error.response?.data) {
      return {
        code: error.response.status.toString(),
        message: error.response.data.message || error.response.data.detail || 'An error occurred',
        details: error.response.data
      };
    }
    return {
      code: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      details: error
    };
  }

  // Get all categories with optional search parameters
  async getCategories(params?: CategorySearchParams): Promise<CategoryListResponse> {
    try {
      const response: AxiosResponse<CategoryListResponse> = await categoryApi.get(
        this.buildUrl(''),
        { params }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get category tree structure
  async getCategoryTree(): Promise<CategoryTreeResponse> {
    try {
      const response: AxiosResponse<CategoryTreeResponse> = await categoryApi.get(
        this.buildUrl('/tree')
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get a single category by ID
  async getCategoryById(id: string): Promise<Category> {
    try {
      const response: AxiosResponse<Category> = await categoryApi.get(
        this.buildUrl(`/${id}`)
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Create a new category
  async createCategory(data: CreateCategoryRequest): Promise<Category> {
    try {
      const response: AxiosResponse<Category> = await categoryApi.post(
        this.buildUrl(''),
        data
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Update an existing category
  async updateCategory(id: string, data: Partial<UpdateCategoryRequest>): Promise<Category> {
    try {
      const response: AxiosResponse<Category> = await categoryApi.put(
        this.buildUrl(`/${id}`),
        data
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Delete a category
  async deleteCategory(id: string): Promise<void> {
    try {
      await categoryApi.delete(this.buildUrl(`/${id}`));
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get category statistics
  async getCategoryStats(): Promise<CategoryStats> {
    try {
      const response: AxiosResponse<CategoryStats> = await categoryApi.get(
        this.buildUrl('/stats')
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get category path (breadcrumb)
  async getCategoryPath(id: string): Promise<Category[]> {
    try {
      const response: AxiosResponse<Category[]> = await categoryApi.get(
        this.buildUrl(`/${id}/path`)
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get categories by parent ID
  async getCategoriesByParent(parentId: string | null): Promise<Category[]> {
    try {
      const params = parentId ? { parent_id: parentId } : { parent_id: null };
      const response: AxiosResponse<CategoryListResponse> = await categoryApi.get(
        this.buildUrl(''),
        { params }
      );
      return response.data.categories;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Search categories by name
  async searchCategories(query: string): Promise<Category[]> {
    try {
      const response: AxiosResponse<CategoryListResponse> = await categoryApi.get(
        this.buildUrl('/search'),
        { params: { q: query } }
      );
      return response.data.categories;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Reorder categories
  async reorderCategories(categoryIds: string[]): Promise<void> {
    try {
      await categoryApi.post(this.buildUrl('/reorder'), {
        category_ids: categoryIds
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Move category to new parent
  async moveCategory(categoryId: string, newParentId: string | null): Promise<Category> {
    try {
      const response: AxiosResponse<Category> = await categoryApi.post(
        this.buildUrl(`/${categoryId}/move`),
        { parent_id: newParentId }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Bulk operations
  async bulkUpdateCategories(updates: Array<{ id: string; data: Partial<UpdateCategoryRequest> }>): Promise<Category[]> {
    try {
      const response: AxiosResponse<Category[]> = await categoryApi.post(
        this.buildUrl('/bulk-update'),
        { updates }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async bulkDeleteCategories(categoryIds: string[]): Promise<void> {
    try {
      await categoryApi.post(this.buildUrl('/bulk-delete'), {
        category_ids: categoryIds
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Utility methods for client-side operations
  buildCategoryTree(categories: Category[]): CategoryTree[] {
    const categoryMap = new Map<string, CategoryTree>();
    const rootCategories: CategoryTree[] = [];

    // Create map of all categories with children array
    categories.forEach(category => {
      categoryMap.set(category.id, {
        ...category,
        children: [],
        isExpanded: false,
        isSelected: false
      });
    });

    // Build tree structure
    categories.forEach(category => {
      const categoryNode = categoryMap.get(category.id)!;

      if (category.parent_id) {
        const parent = categoryMap.get(category.parent_id);
        if (parent) {
          parent.children.push(categoryNode);
        }
      } else {
        rootCategories.push(categoryNode);
      }
    });

    // Sort by sort_order
    const sortCategories = (cats: CategoryTree[]) => {
      cats.sort((a, b) => a.sort_order - b.sort_order);
      cats.forEach(cat => {
        if (cat.children.length > 0) {
          sortCategories(cat.children);
        }
      });
    };

    sortCategories(rootCategories);
    return rootCategories;
  }

  getCategoryAncestors(categoryId: string, categories: Category[]): Category[] {
    const categoryMap = new Map(categories.map(cat => [cat.id, cat]));
    const ancestors: Category[] = [];
    let currentCategory = categoryMap.get(categoryId);

    while (currentCategory && currentCategory.parent_id) {
      const parent = categoryMap.get(currentCategory.parent_id);
      if (parent) {
        ancestors.unshift(parent);
        currentCategory = parent;
      } else {
        break;
      }
    }

    return ancestors;
  }

  getCategoryDescendants(categoryId: string, categories: Category[]): Category[] {
    const descendants: Category[] = [];
    const childCategories = categories.filter(cat => cat.parent_id === categoryId);

    childCategories.forEach(child => {
      descendants.push(child);
      descendants.push(...this.getCategoryDescendants(child.id, categories));
    });

    return descendants;
  }

  flattenCategoryTree(tree: CategoryTree[]): Category[] {
    const flattened: Category[] = [];

    const flatten = (nodes: CategoryTree[]) => {
      nodes.forEach(node => {
        flattened.push(node);
        if (node.children.length > 0) {
          flatten(node.children);
        }
      });
    };

    flatten(tree);
    return flattened;
  }

  findCategoryInTree(tree: CategoryTree[], categoryId: string): CategoryTree | null {
    for (const node of tree) {
      if (node.id === categoryId) {
        return node;
      }
      if (node.children.length > 0) {
        const found = this.findCategoryInTree(node.children, categoryId);
        if (found) {
          return found;
        }
      }
    }
    return null;
  }

  filterCategoriesByLevel(categories: Category[], maxLevel: number): Category[] {
    return categories.filter(category => category.level <= maxLevel);
  }

  getValidParentCategories(categories: Category[], currentCategoryId?: string): Category[] {
    return categories.filter(category => {
      // Cannot be its own parent
      if (currentCategoryId && category.id === currentCategoryId) {
        return false;
      }

      // Cannot be a descendant (to prevent circular references)
      if (currentCategoryId) {
        const descendants = this.getCategoryDescendants(currentCategoryId, categories);
        if (descendants.some(desc => desc.id === category.id)) {
          return false;
        }
      }

      return true;
    });
  }
}

// Export singleton instance
export const categoryService = new CategoryService();
export default categoryService;