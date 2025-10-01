import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, TrendingUp, ArrowRight } from 'lucide-react';
import MarketplaceLayout from '../components/marketplace/MarketplaceLayout';
import FeaturedProducts from '../components/marketplace/FeaturedProducts';
import PopularCategories from '../components/marketplace/PopularCategories';
import TrendingProducts from '../components/marketplace/TrendingProducts';
import NewsletterSignup from '../components/marketplace/NewsletterSignup';
import api from '../services/api';
import { Product } from '../types';

interface MarketplaceHomeProps {}

const MarketplaceHome: React.FC<MarketplaceHomeProps> = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load featured products on mount
    loadFeaturedProducts();
  }, []);

  const loadFeaturedProducts = async () => {
    try {
      setIsLoading(true);

      // Try to fetch from dedicated featured endpoint
      try {
        const response = await api.marketplace.getFeatured();
        setFeaturedProducts(response.data || []);
      } catch (featuredError) {
        console.log('Featured endpoint not available, using fallback');

        // Fallback: Get regular products with high rating/sales
        // Fetch approved products sorted by sales or rating
        const fallbackResponse = await api.products.getAll({
          limit: 6,
          sort_by: 'salesCount',
          sort_order: 'desc',
          in_stock: true
        });

        // Handle paginated response
        const products = fallbackResponse.data?.data || fallbackResponse.data || [];
        setFeaturedProducts(products.slice(0, 6));
      }
    } catch (error) {
      console.error('Error loading featured products:', error);
      setFeaturedProducts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      // Navegar a página de búsqueda
      window.location.href = `/marketplace/search?q=${encodeURIComponent(searchTerm)}`;
    }
  };

  return (
    <MarketplaceLayout>
      {/* Hero Section - Búsqueda Principal */}
      <section className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 text-white">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Descubre el Mejor
              <span className="block text-yellow-400">Marketplace Local</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
              Productos únicos de vendedores locales en Bucaramanga. 
              Calidad garantizada, entrega rápida.
            </p>
            
            {/* Barra de Búsqueda Principal */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="¿Qué estás buscando hoy?"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-6 py-4 text-lg text-gray-900 bg-white rounded-full shadow-lg focus:outline-none focus:ring-4 focus:ring-yellow-400 pr-16"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-yellow-500 hover:bg-yellow-600 text-white p-3 rounded-full transition-colors"
                >
                  <Search className="w-6 h-6" />
                </button>
              </div>
            </form>

            {/* Estadísticas Llamativas */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400">500+</div>
                <div className="text-lg">Productos Únicos</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400">50+</div>
                <div className="text-lg">Vendedores Locales</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400">24h</div>
                <div className="text-lg">Entrega Express</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categorías Populares */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Explora por Categorías
            </h2>
            <p className="text-lg text-gray-600">
              Encuentra exactamente lo que necesitas
            </p>
          </div>
          <PopularCategories />
        </div>
      </section>

      {/* Productos Destacados */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Productos Destacados
              </h2>
              <p className="text-lg text-gray-600">
                Los favoritos de nuestros compradores
              </p>
            </div>
            <Link
              to="/marketplace/featured"
              className="flex items-center text-blue-600 hover:text-blue-700 font-medium"
            >
              Ver todos
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
          </div>
          <FeaturedProducts products={featuredProducts} isLoading={isLoading} />
        </div>
      </section>

      {/* Productos Trending */}
      <section className="py-16 bg-gradient-to-r from-green-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4 flex items-center justify-center">
              <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
              Tendencias del Momento
            </h2>
            <p className="text-lg text-gray-600">
              Lo más popular esta semana
            </p>
          </div>
          <TrendingProducts />
        </div>
      </section>

      {/* Newsletter Signup */}
      <NewsletterSignup />
    </MarketplaceLayout>
  );
};

export default MarketplaceHome;