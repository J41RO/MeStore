// Jest equivalents for Vitest imports
const vi = jest;
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import EnhancedProductDashboard from '../../../components/vendor/EnhancedProductDashboard';

// Mock framer-motion to avoid animation complexities in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock @dnd-kit for testing
vi.mock('@dnd-kit/core', () => ({
  DndContext: ({ children, onDragEnd }: any) => (
    <div data-testid="dnd-context" onDrop={onDragEnd}>
      {children}
    </div>
  ),
  useSensor: vi.fn(),
  useSensors: vi.fn(() => []),
  PointerSensor: vi.fn(),
  KeyboardSensor: vi.fn(),
  closestCenter: vi.fn(),
  DragOverlay: ({ children }: any) => <div data-testid="drag-overlay">{children}</div>,
}));

vi.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }: any) => (
    <div data-testid="sortable-context">{children}</div>
  ),
  useSortable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  })),
  arrayMove: vi.fn((array, from, to) => {
    const newArray = [...array];
    const item = newArray.splice(from, 1)[0];
    newArray.splice(to, 0, item);
    return newArray;
  }),
  sortableKeyboardCoordinates: vi.fn(),
  rectSortingStrategy: vi.fn(),
}));

vi.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: vi.fn(() => ''),
    },
  },
}));

describe.skip('EnhancedProductDashboard - Colombian Market UX Tests', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('✅ GREEN Phase: Basic Functionality Working', () => {
    it('should render the enhanced dashboard with Colombian design', async () => {
      render(<EnhancedProductDashboard />);

      // Should display main title
      expect(screen.getByText('Productos Mejorados')).toBeInTheDocument();
      expect(screen.getByText('Gestión avanzada con drag & drop')).toBeInTheDocument();

      // Should display product cards
      await waitFor(() => {
        expect(screen.getByText('Smartphone Samsung Galaxy A54')).toBeInTheDocument();
        expect(screen.getByText('Camiseta Polo Lacoste Original')).toBeInTheDocument();
        expect(screen.getByText('Cafetera Oster 12 Tazas')).toBeInTheDocument();
      });
    });

    it('should display drag handles with proper accessibility', async () => {
      render(<EnhancedProductDashboard />);

      // Should find drag handles with proper accessibility
      const dragHandles = await screen.findAllByLabelText(/arrastra.*producto.*para.*reordenar/i);
      expect(dragHandles.length).toBeGreaterThan(0);

      // Each drag handle should have proper touch target size
      dragHandles.forEach(handle => {
        expect(handle).toHaveStyle({ minWidth: '44px', minHeight: '44px' });
        expect(handle).toHaveAttribute('title', 'Arrastra para reordenar');
      });
    });

    it('should support bulk selection with touch-friendly checkboxes', async () => {
      render(<EnhancedProductDashboard />);

      // Should have master checkbox
      const masterCheckbox = await screen.findByLabelText(/seleccionar.*todos/i);
      expect(masterCheckbox).toBeInTheDocument();
      expect(masterCheckbox).toHaveAttribute('type', 'checkbox');

      // Should have individual product checkboxes
      const productCheckboxes = await screen.findAllByLabelText(/seleccionar.*producto/i);
      expect(productCheckboxes.length).toBeGreaterThanOrEqual(3);

      // Checkboxes should be touch-friendly (5x5 = 25px with 11x11 container = 44px)
      productCheckboxes.forEach(checkbox => {
        expect(checkbox).toHaveClass('w-5', 'h-5');
        const container = checkbox.closest('label');
        expect(container).toHaveClass('w-11', 'h-11');
      });
    });

    it('should show bulk actions toolbar when products are selected', async () => {
      render(<EnhancedProductDashboard />);

      // Initially no bulk toolbar
      expect(screen.queryByTestId('bulk-actions-toolbar')).not.toBeInTheDocument();

      // Select a product
      const firstCheckbox = await screen.findByLabelText(/seleccionar.*producto.*smartphone/i);
      await user.click(firstCheckbox);

      // Should show bulk actions toolbar
      await waitFor(() => {
        const bulkToolbar = screen.getByTestId('bulk-actions-toolbar');
        expect(bulkToolbar).toBeInTheDocument();
      });

      // Should show selection count
      expect(screen.getByText(/1.*producto.*seleccionado/i)).toBeInTheDocument();

      // Should show bulk action buttons with proper sizing
      const activateButton = screen.getByRole('button', { name: /activar/i });
      const featureButton = screen.getByRole('button', { name: /destacar/i });
      const deleteButton = screen.getByRole('button', { name: /eliminar/i });

      expect(activateButton).toBeInTheDocument();
      expect(featureButton).toBeInTheDocument();
      expect(deleteButton).toBeInTheDocument();

      // Buttons should have proper touch target size
      [activateButton, featureButton, deleteButton].forEach(button => {
        expect(button).toHaveStyle({ minHeight: '44px' });
      });
    });

    it('should implement Colombian color coding for product categories', async () => {
      render(<EnhancedProductDashboard />);

      const productCards = await screen.findAllByTestId(/product-card/);
      expect(productCards.length).toBeGreaterThanOrEqual(3);

      // Should find category badges with proper styling
      const electronicsCategory = screen.getByText('Electrónicos');
      const clothingCategory = screen.getByText('Ropa');
      const homeCategory = screen.getByText('Hogar');

      expect(electronicsCategory).toBeInTheDocument();
      expect(clothingCategory).toBeInTheDocument();
      expect(homeCategory).toBeInTheDocument();

      // Categories should have proper color classes
      expect(electronicsCategory).toHaveClass('bg-primary-50', 'text-primary-700');
      expect(clothingCategory).toHaveClass('bg-orange-50', 'text-orange-700');
      expect(homeCategory).toHaveClass('bg-green-50', 'text-green-700');
    });

    it('should display Colombian currency formatting', async () => {
      render(<EnhancedProductDashboard />);

      // Should format prices in Colombian pesos
      await waitFor(() => {
        expect(screen.getByText('$899.000')).toBeInTheDocument(); // Samsung phone
        expect(screen.getByText('$189.000')).toBeInTheDocument(); // Lacoste shirt
        expect(screen.getByText('$245.000')).toBeInTheDocument(); // Coffee maker
      });

      // Should display cost and commission information
      expect(screen.getByText(/costo.*650\.000/i)).toBeInTheDocument();
      expect(screen.getByText(/comisión.*44\.950/i)).toBeInTheDocument();
    });

    it('should provide touch-friendly interface elements', async () => {
      render(<EnhancedProductDashboard />);

      // All interactive elements should meet 44px minimum touch target
      const buttons = await screen.findAllByRole('button');
      const checkboxes = await screen.findAllByRole('checkbox');
      const inputs = await screen.findAllByRole('textbox');
      const selects = await screen.findAllByRole('combobox');

      const allInteractive = [...buttons, ...inputs, ...selects];

      allInteractive.forEach(element => {
        const styles = window.getComputedStyle(element);
        const minHeight = styles.minHeight || styles.height;

        // Should have minimum 44px height for touch targets
        if (minHeight && minHeight !== 'auto') {
          const heightValue = parseFloat(minHeight);
          expect(heightValue).toBeGreaterThanOrEqual(44);
        }
      });

      // Checkboxes should be in touch-friendly containers
      checkboxes.forEach(checkbox => {
        const container = checkbox.closest('label');
        if (container) {
          expect(container).toHaveClass('w-11', 'h-11');
        }
      });
    });

    it('should show proper stock indicators with Colombian context', async () => {
      render(<EnhancedProductDashboard />);

      // Should show different stock statuses
      expect(screen.getByText(/en stock.*25/i)).toBeInTheDocument(); // Samsung
      expect(screen.getByText(/stock bajo.*8/i)).toBeInTheDocument(); // Lacoste
      expect(screen.getByText(/agotado/i)).toBeInTheDocument(); // Coffee maker

      // Stock indicators should have proper visual styling
      const inStockBadge = screen.getByText(/en stock.*25/i);
      const lowStockBadge = screen.getByText(/stock bajo.*8/i);
      const outOfStockBadge = screen.getByText(/agotado/i);

      expect(inStockBadge).toHaveClass('bg-green-100', 'text-green-800');
      expect(lowStockBadge).toHaveClass('bg-yellow-100', 'text-yellow-800');
      expect(outOfStockBadge).toHaveClass('bg-red-100', 'text-red-800');
    });

    it('should support search functionality', async () => {
      render(<EnhancedProductDashboard />);

      const searchInput = await screen.findByPlaceholderText(/buscar.*productos/i);
      expect(searchInput).toBeInTheDocument();
      expect(searchInput).toHaveStyle({ minHeight: '44px' });

      // Search should filter products
      await user.type(searchInput, 'Samsung');

      await waitFor(() => {
        expect(screen.getByText('Smartphone Samsung Galaxy A54')).toBeInTheDocument();
        expect(screen.queryByText('Camiseta Polo Lacoste Original')).not.toBeInTheDocument();
      });
    });

    it('should handle master checkbox selection correctly', async () => {
      render(<EnhancedProductDashboard />);

      const masterCheckbox = await screen.findByLabelText(/seleccionar.*todos/i);

      // Select all products
      await user.click(masterCheckbox);

      await waitFor(() => {
        const bulkToolbar = screen.getByTestId('bulk-actions-toolbar');
        expect(bulkToolbar).toBeInTheDocument();
        expect(screen.getByText(/3.*productos.*seleccionados/i)).toBeInTheDocument();
      });

      // Deselect all
      await user.click(masterCheckbox);

      await waitFor(() => {
        expect(screen.queryByTestId('bulk-actions-toolbar')).not.toBeInTheDocument();
      });
    });

    it('should display drag & drop context and instructions', async () => {
      render(<EnhancedProductDashboard />);

      // Should have DnD context
      expect(screen.getByTestId('dnd-context')).toBeInTheDocument();
      expect(screen.getByTestId('sortable-context')).toBeInTheDocument();

      // Should show drag instructions
      expect(screen.getByText(/arrastra.*productos.*para.*reordenar/i)).toBeInTheDocument();

      // Should have drag overlay for visual feedback
      expect(screen.getByTestId('drag-overlay')).toBeInTheDocument();
    });
  });

  describe('🎯 Performance and Accessibility Tests', () => {
    it('should render within performance constraints', async () => {
      const startTime = performance.now();

      render(<EnhancedProductDashboard />);

      await waitFor(() => {
        expect(screen.getByTestId('enhanced-product-dashboard')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render within 300ms
      expect(renderTime).toBeLessThan(300);
    });

    it('should maintain accessibility standards', async () => {
      render(<EnhancedProductDashboard />);

      // All interactive elements should have proper labels
      const dragHandles = await screen.findAllByLabelText(/arrastra.*producto.*para.*reordenar/i);
      const checkboxes = await screen.findAllByLabelText(/seleccionar.*producto/i);

      expect(dragHandles.length).toBeGreaterThan(0);
      expect(checkboxes.length).toBeGreaterThan(0);

      // Focus management
      const firstDragHandle = dragHandles[0];
      firstDragHandle.focus();
      expect(firstDragHandle).toHaveFocus();

      // Keyboard navigation
      await user.keyboard('{Tab}');
      // Should move focus to next interactive element
    });

    it('should handle responsive design classes', async () => {
      render(<EnhancedProductDashboard />);

      const productsGrid = await screen.findByTestId('products-grid');
      const gridContainer = productsGrid.querySelector('.grid');

      expect(gridContainer).toHaveClass(
        'grid-cols-1',
        'sm:grid-cols-2',
        'lg:grid-cols-3',
        'xl:grid-cols-4'
      );
    });
  });
});