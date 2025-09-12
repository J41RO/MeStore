import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin, Facebook, Instagram, Twitter } from 'lucide-react';

const MarketplaceFooter: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="text-2xl font-bold text-blue-400">
              MeStore Marketplace
            </div>
            <p className="text-gray-300">
              El mejor marketplace local de Bucaramanga. 
              Conectando compradores con los mejores vendedores locales.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Enlaces Rápidos</h3>
            <div className="space-y-2">
              <Link to="/marketplace/about" className="block text-gray-300 hover:text-white transition-colors">
                Acerca de Nosotros
              </Link>
              <Link to="/marketplace/how-it-works" className="block text-gray-300 hover:text-white transition-colors">
                Cómo Funciona
              </Link>
              <Link to="/marketplace/sellers" className="block text-gray-300 hover:text-white transition-colors">
                Vendedores
              </Link>
              <Link to="/marketplace/careers" className="block text-gray-300 hover:text-white transition-colors">
                Carreras
              </Link>
            </div>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Soporte</h3>
            <div className="space-y-2">
              <Link to="/marketplace/help" className="block text-gray-300 hover:text-white transition-colors">
                Centro de Ayuda
              </Link>
              <Link to="/marketplace/contact" className="block text-gray-300 hover:text-white transition-colors">
                Contáctanos
              </Link>
              <Link to="/marketplace/returns" className="block text-gray-300 hover:text-white transition-colors">
                Devoluciones
              </Link>
              <Link to="/marketplace/shipping" className="block text-gray-300 hover:text-white transition-colors">
                Envíos
              </Link>
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Contacto</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-blue-400" />
                <span className="text-gray-300">soporte@mestore.com</span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-blue-400" />
                <span className="text-gray-300">+57 300 123 4567</span>
              </div>
              <div className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-blue-400" />
                <span className="text-gray-300">Bucaramanga, Santander</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-400 text-sm">
            © 2024 MeStore Marketplace. Todos los derechos reservados.
          </div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link to="/marketplace/privacy" className="text-gray-400 hover:text-white text-sm transition-colors">
              Privacidad
            </Link>
            <Link to="/marketplace/terms" className="text-gray-400 hover:text-white text-sm transition-colors">
              Términos
            </Link>
            <Link to="/marketplace/cookies" className="text-gray-400 hover:text-white text-sm transition-colors">
              Cookies
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default MarketplaceFooter;