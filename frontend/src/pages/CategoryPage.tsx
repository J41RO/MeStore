import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import MarketplaceLayout from '../components/marketplace/MarketplaceLayout';
import CategoryHeader from '../components/marketplace/CategoryHeader';
import CategoryFilters from '../components/marketplace/CategoryFilters';
import SearchResults from '../components/marketplace/SearchResults';

interface Product {
  id: number;
  name: string;
  description: string;
  precio_venta: number;
  categoria: string;
  sku: string;
  estado: string;
  vendor?: {
    business_name: string;
  };
  images?: Array<{
    id: number;
    image_url: string;
    is_primary: boolean;
  }>;
}

interface CategoryFilters {
  categoria: string;
  precio_min: string;
  precio_max: string;
  sort_by: string;
  sort_order: string;
  brand?: string;
  size?: string;
  color?: string;
  condition?: string;
  availability?: string;
}

// Mapeo de slugs a nombres de categorías
const CATEGORY_NAMES: Record<string, string> = {
  'electronics': 'Electrónicos',
  'fashion': 'Ropa y Moda',
  'home': 'Hogar y Jardín', 
  'sports': 'Deportes y Fitness',
  'books': 'Libros y Educación',
  'beauty': 'Belleza y Cuidado Personal',
  'baby': 'Bebés y Niños',
  'automotive': 'Automotriz'
};

const CategoryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 12;

  // Obtener el nombre de la categoría desde el slug
  const currentCategory = slug ? CATEGORY_NAMES[slug] || slug : '';

  const [filters, setFilters] = useState<CategoryFilters>({
    categoria: currentCategory,
    precio_min: searchParams.get('precio_min') || '',
    precio_max: searchParams.get('precio_max') || '',
    sort_by: searchParams.get('sort_by') || 'created_at',
    sort_order: searchParams.get('sort_order') || 'desc',
    brand: searchParams.get('brand') || '',
    size: searchParams.get('size') || '',
    color: searchParams.get('color') || '',
    condition: searchParams.get('condition') || '',
    availability: searchParams.get('availability') || ''
  });

  // Función para cargar productos de la categoría
  const loadCategoryProducts = async () => {
    if (!currentCategory) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        categoria: currentCategory,
        page: currentPage.toString(),
        limit: productsPerPage.toString(),
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
        estado: 'aprobado'
      });

      // Add optional filters
      if (filters.precio_min) params.set('precio_min', filters.precio_min);
      if (filters.precio_max) params.set('precio_max', filters.precio_max);
      if (filters.brand) params.set('brand', filters.brand);
      if (filters.size) params.set('size', filters.size);
      if (filters.color) params.set('color', filters.color);
      if (filters.condition) params.set('condition', filters.condition);
      if (filters.availability) params.set('availability', filters.availability);

      const response = await fetch(`/api/v1/products?${params.toString()}`, {
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (Array.isArray(data)) {
        setProducts(data);
        setTotalCount(data.length);
      } else if (data.productos && Array.isArray(data.productos)) {
        setProducts(data.productos);
        setTotalCount(data.total || data.productos.length);
      } else {
        setProducts([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error cargando productos de categoría:', error);
      setError(error instanceof Error ? error.message : 'Error desconocido');
      setProducts([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  // Cargar productos cuando cambie la categoría, página o filtros
  useEffect(() => {
    if (currentCategory) {
      loadCategoryProducts();
    }
  }, [currentCategory, currentPage, filters]);

  // Actualizar filtros cuando cambien los parámetros de URL
  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      categoria: currentCategory,
      precio_min: searchParams.get('precio_min') || '',
      precio_max: searchParams.get('precio_max') || '',
      sort_by: searchParams.get('sort_by') || 'created_at',
      sort_order: searchParams.get('sort_order') || 'desc',
      brand: searchParams.get('brand') || '',
      size: searchParams.get('size') || '',
      color: searchParams.get('color') || '',
      condition: searchParams.get('condition') || '',
      availability: searchParams.get('availability') || ''
    }));
  }, [searchParams, currentCategory]);

  // Manejar cambios en filtros
  const handleFiltersChange = (newFilters: Partial<CategoryFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);

    // Actualizar URL con nuevos parámetros
    const params = new URLSearchParams();
    if (updatedFilters.precio_min) params.set('precio_min', updatedFilters.precio_min);
    if (updatedFilters.precio_max) params.set('precio_max', updatedFilters.precio_max);
    if (updatedFilters.sort_by !== 'created_at') params.set('sort_by', updatedFilters.sort_by);
    if (updatedFilters.sort_order !== 'desc') params.set('sort_order', updatedFilters.sort_order);
    if (updatedFilters.brand) params.set('brand', updatedFilters.brand);
    if (updatedFilters.size) params.set('size', updatedFilters.size);
    if (updatedFilters.color) params.set('color', updatedFilters.color);
    if (updatedFilters.condition) params.set('condition', updatedFilters.condition);
    if (updatedFilters.availability) params.set('availability', updatedFilters.availability);

    setSearchParams(params);
    setCurrentPage(1); // Reset página al cambiar filtros
  };

  if (!slug) {
    return (
      <MarketplaceLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Categoría no encontrada</h1>
            <p className="text-gray-600">La categoría solicitada no existe.</p>
          </div>
        </div>
      </MarketplaceLayout>
    );
  }

  return (
    <MarketplaceLayout>
      <div className="bg-gray-50 min-h-screen">
        <div className="container mx-auto px-4 py-6">
          {/* Category Header */}
          <div className="mb-6">
            <CategoryHeader
              categoryName={currentCategory}
              productCount={totalCount}
              categorySlug={slug || ''}
              loading={loading}
            />
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Filters Sidebar */}
            <div className="lg:w-1/4">
              <CategoryFilters
                categorySlug={slug || ''}
                filters={{
                  precio_min: filters.precio_min,
                  precio_max: filters.precio_max,
                  sort_by: filters.sort_by,
                  sort_order: filters.sort_order,
                  brand: filters.brand,
                  size: filters.size,
                  color: filters.color,
                  condition: filters.condition,
                  availability: filters.availability
                }}
                onFiltersChange={handleFiltersChange}
                productCount={totalCount}
              />
            </div>

            {/* Products Section */}
            <div className="lg:w-3/4">
              {/* Sort Options Header */}
              <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {loading ? 'Cargando productos...' : `${totalCount} producto${totalCount !== 1 ? 's' : ''} encontrado${totalCount !== 1 ? 's' : ''}`}
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium text-gray-700">
                      Ordenar por:
                    </label>
                    <select
                      value={`${filters.sort_by}-${filters.sort_order}`}
                      onChange={(e) => {
                        const [sort_by, sort_order] = e.target.value.split('-');
                        handleFiltersChange({ sort_by, sort_order });
                      }}
                      className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="created_at-desc">Más recientes</option>
                      <option value="created_at-asc">Más antiguos</option>
                      <option value="precio_venta-asc">Precio: menor a mayor</option>
                      <option value="precio_venta-desc">Precio: mayor a menor</option>
                      <option value="name-asc">Nombre: A-Z</option>
                      <option value="name-desc">Nombre: Z-A</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Products Results */}
              <SearchResults
                products={products}
                loading={loading}
                error={error}
                hasMore={currentPage < Math.ceil(totalCount / productsPerPage)}
                onLoadMore={() => setCurrentPage(prev => prev + 1)}
                searchQuery={currentCategory}
              />
            </div>
          </div>
        </div>
      </div>
    </MarketplaceLayout>
  );
};

export default CategoryPage;