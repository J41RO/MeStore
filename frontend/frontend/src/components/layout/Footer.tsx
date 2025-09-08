import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';

interface FooterProps {
  className?: string;
}

const Footer: React.FC<FooterProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthContext();

  return (
    <footer className={}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* MeStocker Brand */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">M</span>
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                MeStocker
              </h3>
            </div>
            <p className="text-gray-400 mb-4">
              Fulfillment inteligente en Bucaramanga para toda Colombia
            </p>
            <div className="text-sm text-gray-500">
              📍 Bucaramanga, Santander
              <br />
              📞 WhatsApp: +57 300 123 4567
            </div>
          </div>
          
          {/* Servicios */}
          <div>
            <h4 className="font-semibold mb-4">Servicios</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#almacenamiento" className="hover:text-white transition-colors">Almacenamiento Seguro</a></li>
              <li><a href="#inventario" className="hover:text-white transition-colors">Gestión Inventario IA</a></li>
              <li><a href="#marketplace" className="hover:text-white transition-colors">Marketplace B2B+B2C</a></li>
              <li><a href="#envios" className="hover:text-white transition-colors">Logística Nacional</a></li>
            </ul>
          </div>
          
          {/* Recursos */}
          <div>
            <h4 className="font-semibold mb-4">Recursos</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#guia" className="hover:text-white transition-colors">Guía Gratuita Fulfillment</a></li>
              <li><a href="#calculator" className="hover:text-white transition-colors">Calculadora ROI</a></li>
              <li><a href="#casos" className="hover:text-white transition-colors">Casos Éxito</a></li>
              <li><a href="#blog" className="hover:text-white transition-colors">Blog</a></li>
            </ul>
          </div>
          
          {/* Autenticación */}
          <div>
            <h4 className="font-semibold mb-4">Acceso</h4>
            <div className="space-y-3">
                <>
                  <Link
                    to="/login"
                    className="block text-gray-400 hover:text-white transition-colors"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link
                    to="/register"
                    className="block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:from-blue-700 hover:to-purple-700 transition-all"
                  >
                    Registrarse Gratis
                  </Link>
                </>
              ) : (
                <button
                  onClick={() => navigate('/dashboard')}
                  className="block bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:shadow-lg transition-all"
                >
                  Ir a Dashboard
                </button>
              )}
              <Link
                to="/admin-portal"
                className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
              >
                Portal Admin
              </Link>
            </div>
          </div>
        </div>
        
        {/* Footer Bottom */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 mb-4 md:mb-0">
            © 2024 MeStocker Bucaramanga. Todos los derechos reservados.
          </p>
          <div className="flex space-x-6 text-gray-400">
            <a href="#terminos" className="hover:text-white transition-colors">Términos</a>
            <a href="#privacidad" className="hover:text-white transition-colors">Privacidad</a>
            <a href="#contacto" className="hover:text-white transition-colors">Contacto</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;