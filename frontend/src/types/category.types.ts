// Category Types for MeStore Marketplace
export interface Category {
  id: string;
  name: string;
  description?: string;
  slug: string;
  parent_id?: string | null;
  level: number;
  image_url?: string;
  icon?: string;
  is_active: boolean;
  sort_order: number;
  product_count?: number;
  created_at: string;
  updated_at: string;
  children?: Category[];
  parent?: Category;
}

export interface CategoryTree extends Category {
  children: CategoryTree[];
  isExpanded?: boolean;
  isSelected?: boolean;
}

export interface CategoryFilter {
  category_ids: string[];
  include_subcategories: boolean;
  min_products?: number;
}

export interface CategoryBreadcrumb {
  id: string;
  name: string;
  slug: string;
  url: string;
}

export interface CategoryStats {
  total_categories: number;
  active_categories: number;
  categories_with_products: number;
  max_depth: number;
  product_distribution: { [key: string]: number };
}

// API Request/Response Types
export interface CreateCategoryRequest {
  name: string;
  description?: string;
  parent_id?: string | null;
  image_url?: string;
  icon?: string;
  is_active: boolean;
  sort_order?: number;
}

export interface UpdateCategoryRequest extends Partial<CreateCategoryRequest> {
  id: string;
}

export interface CategoryListResponse {
  categories: Category[];
  total_count: number;
  page: number;
  per_page: number;
}

export interface CategoryTreeResponse {
  tree: CategoryTree[];
  stats: CategoryStats;
}

// Component Props Types
export interface CategoryTreeProps {
  data: CategoryTree[];
  onCategorySelect?: (category: Category) => void;
  onCategoryExpand?: (categoryId: string, isExpanded: boolean) => void;
  selectedCategoryId?: string;
  expandedCategories?: string[];
  showProductCount?: boolean;
  maxDepth?: number;
  className?: string;
}

export interface CategoryManagerProps {
  onCategoryCreate?: (category: Category) => void;
  onCategoryUpdate?: (category: Category) => void;
  onCategoryDelete?: (categoryId: string) => void;
  allowDragDrop?: boolean;
  className?: string;
}

export interface CategorySelectorProps {
  selectedCategories: string[];
  onSelectionChange: (categories: string[]) => void;
  maxSelections?: number;
  required?: boolean;
  allowMultiple?: boolean;
  filterByLevel?: number;
  placeholder?: string;
  className?: string;
}

export interface CategoryBreadcrumbProps {
  categoryId?: string;
  customPath?: CategoryBreadcrumb[];
  onNavigate?: (category: CategoryBreadcrumb) => void;
  separator?: string;
  showHome?: boolean;
  className?: string;
}

export interface CategoryFilterProps {
  selectedFilters: CategoryFilter;
  onFiltersChange: (filters: CategoryFilter) => void;
  availableCategories: CategoryTree[];
  showProductCount?: boolean;
  collapsible?: boolean;
  className?: string;
}

// Store State Types
export interface CategoryState {
  // Data
  categories: Category[];
  categoryTree: CategoryTree[];
  selectedCategory: Category | null;
  breadcrumb: CategoryBreadcrumb[];

  // UI State
  isLoading: boolean;
  error: string | null;
  expandedCategories: string[];
  selectedCategories: string[];

  // Filters
  activeFilters: CategoryFilter;
  searchQuery: string;

  // Stats
  stats: CategoryStats | null;
}

export interface CategoryActions {
  // Data Actions
  loadCategories: () => Promise<void>;
  loadCategoryTree: () => Promise<void>;
  createCategory: (data: CreateCategoryRequest) => Promise<Category>;
  updateCategory: (data: UpdateCategoryRequest) => Promise<Category>;
  deleteCategory: (id: string) => Promise<void>;

  // Selection Actions
  selectCategory: (category: Category) => void;
  clearSelection: () => void;

  // UI Actions
  toggleCategoryExpansion: (categoryId: string) => void;
  expandAllCategories: () => void;
  collapseAllCategories: () => void;

  // Filter Actions
  setFilters: (filters: Partial<CategoryFilter>) => void;
  clearFilters: () => void;
  setSearchQuery: (query: string) => void;

  // Utility Actions
  getCategoryPath: (categoryId: string) => CategoryBreadcrumb[];
  getCategoryChildren: (categoryId: string) => Category[];
  getCategoryParents: (categoryId: string) => Category[];

  // Reset Actions
  reset: () => void;
}

export type CategoryStore = CategoryState & CategoryActions;

// Error Types
export interface CategoryError {
  code: string;
  message: string;
  details?: any;
}

// Drag and Drop Types (for CategoryManager)
export interface DragItem {
  id: string;
  type: 'category';
  category: Category;
}

export interface DropResult {
  targetId: string;
  position: 'before' | 'after' | 'inside';
}

// Search and Pagination Types
export interface CategorySearchParams {
  query?: string;
  parent_id?: string;
  level?: number;
  is_active?: boolean;
  has_products?: boolean;
  sort_by?: 'name' | 'sort_order' | 'created_at' | 'product_count';
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

export interface CategoryPagination {
  page: number;
  per_page: number;
  total_pages: number;
  total_count: number;
  has_next: boolean;
  has_prev: boolean;
}