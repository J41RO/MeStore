# Category Management Components

A comprehensive set of React components for managing categories in the MeStore marketplace. Built with React 18, TypeScript, Zustand, and Tailwind CSS.

## Components Overview

### 🌳 CategoryTree
Interactive tree view for category navigation with expand/collapse functionality.

**Use Cases:**
- Public category browsing
- Product category navigation
- Admin category overview

**Props:**
```typescript
interface CategoryTreeProps {
  data: CategoryTree[];
  onCategorySelect?: (category: Category) => void;
  onCategoryExpand?: (categoryId: string, isExpanded: boolean) => void;
  selectedCategoryId?: string;
  expandedCategories?: string[];
  showProductCount?: boolean;
  maxDepth?: number;
  className?: string;
}
```

**Example:**
```tsx
import { CategoryTree } from './components/categories';

<CategoryTree
  data={categoryTree}
  onCategorySelect={(category) => navigate(`/categories/${category.slug}`)}
  showProductCount={true}
  maxDepth={3}
/>
```

### 👨‍💼 CategoryManager
Full CRUD interface for administrators to manage categories.

**Use Cases:**
- Admin category management
- Category creation/editing
- Category reordering
- Bulk operations

**Features:**
- ✅ Create, Read, Update, Delete categories
- ✅ Drag & drop reordering
- ✅ Bulk operations
- ✅ Search and filtering
- ✅ Active/inactive toggle
- ✅ Form validation

**Example:**
```tsx
import { CategoryManager } from './components/categories';

<CategoryManager
  onCategoryCreate={(category) => console.log('Created:', category)}
  onCategoryUpdate={(category) => console.log('Updated:', category)}
  onCategoryDelete={(id) => console.log('Deleted:', id)}
  allowDragDrop={true}
/>
```

### 🛍️ CategorySelector
Multi-select dropdown for vendors to assign categories to products.

**Use Cases:**
- Product category assignment
- Vendor product creation
- Category selection in forms

**Features:**
- ✅ Single/multi-select modes
- ✅ Maximum selection limits
- ✅ Search functionality
- ✅ Selected category tags
- ✅ Validation states

**Example:**
```tsx
import { CategorySelector } from './components/categories';

<CategorySelector
  selectedCategories={selectedCats}
  onSelectionChange={setSelectedCats}
  maxSelections={3}
  allowMultiple={true}
  required={true}
  placeholder="Select product categories..."
/>
```

### 🍞 CategoryBreadcrumb
Navigation breadcrumb showing category hierarchy.

**Use Cases:**
- Page navigation
- Category path display
- SEO breadcrumbs

**Features:**
- ✅ Responsive design
- ✅ Auto-collapse for long paths
- ✅ Custom separators
- ✅ Schema.org structured data
- ✅ Click navigation

**Variants:**
- `CategoryBreadcrumb` - Standard breadcrumb
- `ResponsiveCategoryBreadcrumb` - Mobile-optimized
- `CompactCategoryBreadcrumb` - Minimal version

**Example:**
```tsx
import { CategoryBreadcrumb, ResponsiveCategoryBreadcrumb } from './components/categories';

<CategoryBreadcrumb
  categoryId="smartphones"
  showHome={true}
  separator="chevron"
  onNavigate={(item) => navigate(item.url)}
/>

<ResponsiveCategoryBreadcrumb categoryId="laptops" />
```

### 🔍 CategoryFilter
Advanced filtering component for product search.

**Use Cases:**
- Product filtering
- Search sidebars
- E-commerce navigation

**Features:**
- ✅ Tree-based filtering
- ✅ Include/exclude subcategories
- ✅ Search within categories
- ✅ Active filter summary
- ✅ Clear all filters
- ✅ Collapsible interface

**Variants:**
- `CategoryFilter` - Full-featured filter
- `CompactCategoryFilter` - Simplified version

**Example:**
```tsx
import { CategoryFilter, CompactCategoryFilter } from './components/categories';

<CategoryFilter
  selectedFilters={filters}
  onFiltersChange={setFilters}
  availableCategories={categoryTree}
  showProductCount={true}
  collapsible={true}
/>

<CompactCategoryFilter
  selectedFilters={filters}
  onFiltersChange={setFilters}
  availableCategories={categoryTree}
/>
```

## State Management

### Zustand Store
Global state management with `useCategoryStore`:

```typescript
const {
  categories,
  categoryTree,
  isLoading,
  error,
  loadCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  selectCategory,
  setFilters
} = useCategoryStore();
```

### Custom Hooks
Specialized hooks for different use cases:

#### `useCategories()`
Main hook for category operations:
```typescript
const {
  categories,
  categoryTree,
  isLoading,
  error,
  createCategory,
  updateCategory,
  deleteCategory
} = useCategories();
```

#### `useCategoryTree()`
Tree-specific operations:
```typescript
const {
  categoryTree,
  expandedCategories,
  toggleExpansion,
  expandAll,
  collapseAll
} = useCategoryTree();
```

#### `useCategorySelection()`
Selection management for forms:
```typescript
const {
  selectedCategories,
  toggleSelection,
  clearSelection,
  isSelected,
  canSelect,
  isAtLimit
} = useCategorySelection(maxSelections, allowMultiple);
```

#### `useCategoryFilter()`
Filtering and search:
```typescript
const {
  filteredCategories,
  activeFilters,
  searchQuery,
  toggleCategoryFilter,
  setSearchQuery,
  clearFilters
} = useCategoryFilter();
```

#### `useCategoryManagement()`
Admin operations:
```typescript
const {
  createCategory,
  updateCategory,
  deleteCategory,
  isLoading,
  error
} = useCategoryManagement();
```

## API Integration

### Service Layer
The `categoryService` handles all API communications:

```typescript
import { categoryService } from '../services/categoryService';

// Get categories
const categories = await categoryService.getCategories();

// Get category tree
const tree = await categoryService.getCategoryTree();

// Create category
const newCategory = await categoryService.createCategory({
  name: 'New Category',
  parent_id: null,
  is_active: true
});

// Update category
const updatedCategory = await categoryService.updateCategory('id', {
  name: 'Updated Name'
});

// Delete category
await categoryService.deleteCategory('id');
```

### Error Handling
All components include comprehensive error handling:

```typescript
try {
  const result = await createCategory(data);
  if (result.success) {
    // Handle success
  }
} catch (error: CategoryError) {
  // Handle error
  console.error(error.message);
}
```

## Styling & Theming

### Tailwind CSS Classes
Components use consistent Tailwind classes with dark mode support:

```css
/* Light mode */
.category-item {
  @apply bg-white border-gray-200 text-gray-900;
}

/* Dark mode */
.dark .category-item {
  @apply bg-gray-800 border-gray-700 text-white;
}
```

### Custom CSS Variables
For advanced theming:

```css
:root {
  --category-primary: #3b82f6;
  --category-secondary: #64748b;
  --category-success: #10b981;
  --category-danger: #ef4444;
}
```

## Performance Optimization

### Memoization
Components use React.memo and useMemo for optimal performance:

```typescript
const CategoryTreeNode = memo(({ category, ...props }) => {
  const isExpanded = useMemo(() => {
    return expandedCategories.includes(category.id);
  }, [expandedCategories, category.id]);

  const handleClick = useCallback(() => {
    onCategorySelect(category);
  }, [onCategorySelect, category]);

  return (
    // Component JSX
  );
});
```

### Lazy Loading
Large category trees support lazy loading:

```typescript
const { categoryTree, isLoading } = useCategoryTree();

if (isLoading) {
  return <CategoryTreeSkeleton />;
}
```

### Virtual Scrolling
For very large lists (1000+ categories):

```typescript
// Enable virtual scrolling for CategoryFilter
<CategoryFilter
  availableCategories={largeCategories}
  virtualScrolling={true}
  itemHeight={40}
  maxHeight={400}
/>
```

## Accessibility

### ARIA Labels
All interactive elements include proper ARIA labels:

```tsx
<button
  aria-label={isExpanded ? 'Collapse category' : 'Expand category'}
  aria-expanded={isExpanded}
>
  {/* Button content */}
</button>
```

### Keyboard Navigation
Full keyboard support:
- `Tab` / `Shift+Tab` - Navigate between elements
- `Enter` / `Space` - Select/toggle items
- `Arrow keys` - Navigate tree structure
- `Esc` - Close dropdowns/modals

### Screen Reader Support
Structured markup for screen readers:

```tsx
<nav aria-label="Category breadcrumb">
  <ol role="list">
    <li role="listitem">
      <a href="/categories/electronics">Electronics</a>
    </li>
  </ol>
</nav>
```

## Testing

### Component Testing
Each component includes comprehensive tests:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { CategoryTree } from './CategoryTree';

test('renders category tree with correct structure', () => {
  render(<CategoryTree data={mockCategories} />);

  expect(screen.getByText('Electronics')).toBeInTheDocument();
  expect(screen.getByText('Smartphones')).toBeInTheDocument();
});

test('handles category selection', () => {
  const onSelect = jest.fn();
  render(<CategoryTree data={mockCategories} onCategorySelect={onSelect} />);

  fireEvent.click(screen.getByText('Electronics'));
  expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({
    name: 'Electronics'
  }));
});
```

### Integration Testing
Test component interactions:

```typescript
test('category filter updates product list', async () => {
  render(<ProductSearchPage />);

  const filterComponent = screen.getByRole('region', { name: /category filter/i });
  const electronicsCheckbox = within(filterComponent).getByLabelText('Electronics');

  fireEvent.click(electronicsCheckbox);

  await waitFor(() => {
    expect(screen.getByText('150 products found')).toBeInTheDocument();
  });
});
```

## Migration Guide

### From Legacy Components
If migrating from existing category components:

1. **Update imports:**
```typescript
// Old
import CategoryList from './CategoryList';

// New
import { CategoryTree } from './components/categories';
```

2. **Update props:**
```typescript
// Old
<CategoryList
  categories={categories}
  onSelect={handleSelect}
/>

// New
<CategoryTree
  data={categoryTree}
  onCategorySelect={handleSelect}
/>
```

3. **Update state management:**
```typescript
// Old
const [categories, setCategories] = useState([]);

// New
const { categories, categoryTree } = useCategories();
```

## Best Practices

### Component Composition
Combine components for complex UIs:

```tsx
const ProductCatalogPage = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar */}
      <div className="lg:col-span-1">
        <CategoryFilter {...filterProps} />
        <CategoryTree {...treeProps} className="mt-6" />
      </div>

      {/* Main content */}
      <div className="lg:col-span-3">
        <CategoryBreadcrumb {...breadcrumbProps} />
        <ProductGrid />
      </div>
    </div>
  );
};
```

### State Optimization
Use selectors for performance:

```typescript
import { categorySelectors } from '../stores/categoryStore';

const { activeCategories } = categorySelectors.getActiveCategories(store);
```

### Error Boundaries
Wrap components in error boundaries:

```tsx
<ErrorBoundary fallback={<CategoryErrorFallback />}>
  <CategoryManager />
</ErrorBoundary>
```

## Troubleshooting

### Common Issues

1. **Categories not loading:**
   - Check API endpoint configuration
   - Verify authentication tokens
   - Check network requests in DevTools

2. **Tree not expanding:**
   - Ensure `onCategoryExpand` is provided
   - Check `expandedCategories` state
   - Verify category has children

3. **Selection not working:**
   - Check `onSelectionChange` callback
   - Verify `selectedCategories` prop
   - Check component permissions

4. **Performance issues:**
   - Enable virtual scrolling for large lists
   - Use `React.memo` on custom components
   - Implement lazy loading

### Debug Tools
Enable debug mode:

```typescript
// Add to component props
<CategoryTree
  data={categories}
  debug={process.env.NODE_ENV === 'development'}
/>
```

## Contributing

When adding new features:

1. Update TypeScript interfaces in `types/category.types.ts`
2. Add corresponding service methods in `categoryService.ts`
3. Update Zustand store in `categoryStore.ts`
4. Create/update custom hooks in `useCategories.ts`
5. Add comprehensive tests
6. Update this documentation

## License

Part of the MeStore marketplace frontend system. All rights reserved.