import { render, screen, fireEvent } from '@testing-library/react';
import SearchResults from './SearchResults';

const mockProducts = [
  {
    id: 1,
    name: 'Test Product 1',
    description: 'Test description 1',
    precio_venta: 50000,
    categoria: 'electronica',
    sku: 'TEST001',
    estado: 'aprobado',
    vendor: {
      business_name: 'Test Vendor 1'
    },
    images: [
      {
        id: 1,
        image_url: 'https://example.com/image1.jpg',
        is_primary: true
      }
    ]
  },
  {
    id: 2,
    name: 'Test Product 2',
    description: 'Test description 2',
    precio_venta: 75000,
    categoria: 'ropa',
    sku: 'TEST002',
    estado: 'aprobado',
    vendor: {
      business_name: 'Test Vendor 2'
    }
  }
];

const mockOnLoadMore = jest.fn();

describe('SearchResults', () => {
  beforeEach(() => {
    mockOnLoadMore.mockClear();
  });

  it('renders loading skeletons when loading and no products', () => {
    render(
      <SearchResults
        products={[]}
        loading={true}
        error={null}
        hasMore={false}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    // Should render skeleton loading elements
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders error state when there is an error', () => {
    render(
      <SearchResults
        products={[]}
        loading={false}
        error="Error al cargar productos"
        hasMore={false}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    expect(screen.getAllByText('Error al cargar productos')[0]).toBeInTheDocument();
    expect(screen.getByText('Intentar de nuevo')).toBeInTheDocument();
  });

  it('renders no results message when no products found', () => {
    render(
      <SearchResults
        products={[]}
        loading={false}
        error={null}
        hasMore={false}
        onLoadMore={mockOnLoadMore}
        searchQuery="test"
      />
    );

    expect(screen.getByText('No se encontraron productos')).toBeInTheDocument();
  });

  it('renders products correctly', () => {
    render(
      <SearchResults
        products={mockProducts}
        loading={false}
        error={null}
        hasMore={false}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    expect(screen.getByText('Test Product 2')).toBeInTheDocument();
    expect(screen.getByText('Test Vendor 1')).toBeInTheDocument();
    expect(screen.getByText('Test Vendor 2')).toBeInTheDocument();
  });

  it('shows load more button when hasMore is true', () => {
    render(
      <SearchResults
        products={mockProducts}
        loading={false}
        error={null}
        hasMore={true}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    expect(screen.getByText('Ver más productos')).toBeInTheDocument();
  });

  it('calls onLoadMore when load more button is clicked', () => {
    render(
      <SearchResults
        products={mockProducts}
        loading={false}
        error={null}
        hasMore={true}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    const loadMoreButton = screen.getByText('Ver más productos');
    fireEvent.click(loadMoreButton);

    expect(mockOnLoadMore).toHaveBeenCalled();
  });

  it('displays formatted prices correctly', () => {
    render(
      <SearchResults
        products={mockProducts}
        loading={false}
        error={null}
        hasMore={false}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    // Prices should be formatted as Colombian pesos
    expect(screen.getByText(/50\.000/)).toBeInTheDocument();
    expect(screen.getByText(/75\.000/)).toBeInTheDocument();
  });

  it('shows loading state for additional products', () => {
    render(
      <SearchResults
        products={mockProducts}
        loading={true}
        error={null}
        hasMore={true}
        onLoadMore={mockOnLoadMore}
        searchQuery=""
      />
    );

    // Should show existing products plus loading skeletons
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    expect(screen.getByText('Cargando más...')).toBeInTheDocument();
  });
});