import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchFilters from './SearchFilters';

const mockFilters = {
  search: '',
  categoria: '',
  precio_min: '',
  precio_max: '',
  sort_by: 'created_at',
  sort_order: 'desc'
};

const mockOnFiltersChange = jest.fn();
const mockOnSearch = jest.fn();

describe('SearchFilters', () => {
  beforeEach(() => {
    mockOnFiltersChange.mockClear();
    mockOnSearch.mockClear();
  });

  it('renders search input correctly', () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    expect(screen.getByPlaceholderText('Buscar productos...')).toBeInTheDocument();
  });

  it('handles search form submission', async () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    const searchInput = screen.getByPlaceholderText('Buscar productos...');
    const searchButton = screen.getByText('Buscar');

    fireEvent.change(searchInput, { target: { value: 'test product' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith('test product');
    });
  });

  it('renders category filter with all options', () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    const categorySelect = screen.getByDisplayValue('Todas las categorías');
    expect(categorySelect).toBeInTheDocument();
  });

  it('handles category filter change', () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    const categorySelect = screen.getByDisplayValue('Todas las categorías');
    fireEvent.change(categorySelect, { target: { value: 'electronica' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      ...mockFilters,
      categoria: 'electronica'
    });
  });

  it('renders price range inputs', () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    expect(screen.getByPlaceholderText('Min')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Max')).toBeInTheDocument();
  });

  it('handles price filter changes', () => {
    render(
      <SearchFilters
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    const minPriceInput = screen.getByPlaceholderText('Min');
    fireEvent.change(minPriceInput, { target: { value: '10000' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      ...mockFilters,
      precio_min: '10000'
    });
  });

  it('shows clear filters button when filters are active', () => {
    const filtersWithValues = {
      ...mockFilters,
      categoria: 'electronica',
      precio_min: '10000'
    };

    render(
      <SearchFilters
        filters={filtersWithValues}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument();
  });

  it('clears filters when clear button is clicked', () => {
    const filtersWithValues = {
      ...mockFilters,
      categoria: 'electronica',
      precio_min: '10000'
    };

    render(
      <SearchFilters
        filters={filtersWithValues}
        onFiltersChange={mockOnFiltersChange}
        onSearch={mockOnSearch}
      />
    );

    const clearButton = screen.getByText('Limpiar filtros');
    fireEvent.click(clearButton);

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      search: '',
      categoria: '',
      precio_min: '',
      precio_max: '',
      sort_by: 'created_at',
      sort_order: 'desc'
    });
  });
});