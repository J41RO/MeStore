import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, User, Menu, X, Heart, LogOut } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import CartButton from './CartButton';
import CartDrawer from './CartDrawer';

const MarketplaceNavbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const { isLoggedIn, userName, userEmail, signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    navigate('/marketplace');
  };

  const categories = [
    'Electrónicos',
    'Ropa y Moda',
    'Hogar y Jardín',
    'Deportes',
    'Libros',
    'Belleza',
    'Juguetes',
    'Automotriz'
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/marketplace/search?q=${encodeURIComponent(searchTerm)}`);
    }
  };

  return (
    <>
      {/* Top Bar */}
      <div className="bg-gray-900 text-white py-2">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center text-sm">
            <div className="flex space-x-6">
              <span>📦 Envío gratis en compras mayores a $100,000</span>
              <span>⚡ Entrega en 24h en Bucaramanga</span>
            </div>
            <div className="flex space-x-4">
              <Link to="/marketplace/help" className="hover:text-yellow-400">
                Ayuda
              </Link>
              <Link to="/marketplace/track" className="hover:text-yellow-400">
                Rastrear Pedido
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/marketplace" className="flex items-center">
              <div className="text-2xl font-bold text-blue-600">
                MeStore
              </div>
              <span className="ml-2 text-sm text-gray-500">Marketplace</span>
            </Link>

            {/* Search Bar - Desktop */}
            <div className="hidden md:flex flex-1 max-w-2xl mx-8">
              <form onSubmit={handleSearch} className="w-full">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Buscar productos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="submit"
                    className="absolute right-0 top-0 h-full px-4 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 transition-colors"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-4">
              <Link
                to="/marketplace/wishlist"
                className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                aria-label="Lista de deseos"
              >
                <Heart className="w-6 h-6" />
              </Link>

              {/* Cart Button with Badge */}
              <CartButton />

              {/* User Menu - Desktop */}
              {isLoggedIn ? (
                <div className="hidden md:flex items-center space-x-2 group relative">
                  <div className="flex items-center space-x-2 text-gray-700 cursor-pointer">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                      {userName.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{userName}</span>
                      <span className="text-xs text-gray-500">{userEmail}</span>
                    </div>
                  </div>
                  {/* Dropdown Menu */}
                  <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block z-50">
                    <Link
                      to="/marketplace/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Mi Perfil
                    </Link>
                    <Link
                      to="/marketplace/orders"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Mis Pedidos
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Cerrar Sesión</span>
                    </button>
                  </div>
                </div>
              ) : (
                <Link
                  to="/auth/login"
                  className="hidden md:flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
                >
                  <User className="w-6 h-6" />
                  <span>Ingresar</span>
                </Link>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 text-gray-600 hover:text-blue-600"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Categories Bar */}
        <div className="hidden lg:block bg-gray-50 border-t">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8 py-3">
              {categories.map((category) => (
                <Link
                  key={category}
                  to={`/marketplace/category/${category.toLowerCase().replace(/\s+/g, '-')}`}
                  className="text-sm text-gray-700 hover:text-blue-600 whitespace-nowrap transition-colors"
                >
                  {category}
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-4 space-y-4">
              {/* Mobile Search */}
              <form onSubmit={handleSearch}>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Buscar productos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="submit"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
                  >
                    <Search className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </form>

              {/* Mobile Categories */}
              <div className="space-y-2">
                <h3 className="font-medium text-gray-900">Categorías</h3>
                {categories.map((category) => (
                  <Link
                    key={category}
                    to={`/marketplace/category/${category.toLowerCase().replace(/\s+/g, '-')}`}
                    className="block text-gray-600 hover:text-blue-600 py-1"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {category}
                  </Link>
                ))}
              </div>

              {/* Mobile User Actions */}
              <div className="border-t pt-4 space-y-2">
                {isLoggedIn ? (
                  <>
                    <div className="flex items-center space-x-3 pb-2">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                        {userName.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{userName}</span>
                        <span className="text-xs text-gray-500">{userEmail}</span>
                      </div>
                    </div>
                    <Link
                      to="/marketplace/profile"
                      className="block text-gray-600 hover:text-blue-600 py-1"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Mi Perfil
                    </Link>
                    <Link
                      to="/marketplace/orders"
                      className="block text-gray-600 hover:text-blue-600 py-1"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Mis Pedidos
                    </Link>
                    <Link
                      to="/marketplace/wishlist"
                      className="block text-gray-600 hover:text-blue-600 py-1"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Lista de Deseos
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsMenuOpen(false);
                      }}
                      className="w-full text-left text-red-600 hover:text-red-700 py-1 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Cerrar Sesión</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/auth/login"
                      className="block text-gray-600 hover:text-blue-600 py-1"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Iniciar Sesión
                    </Link>
                    <Link
                      to="/marketplace/wishlist"
                      className="block text-gray-600 hover:text-blue-600 py-1"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Lista de Deseos
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Cart Drawer - Sliding Panel */}
      <CartDrawer />
    </>
  );
};

export default MarketplaceNavbar;