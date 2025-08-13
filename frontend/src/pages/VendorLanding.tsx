import React from 'react';
import { useNavigate } from 'react-router-dom';

const VendorLanding: React.FC = () => {
  const navigate = useNavigate();

  const handleRegisterClick = () => {
    navigate('/register');
  };

  const handleLearnMoreClick = () => {
    const benefitsSection = document.querySelector(`[data-section="benefits"]`);
    if (benefitsSection) {
      benefitsSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <section className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
            Únete a Nuestra Plataforma
            <span className="block text-blue-600 dark:text-blue-400">
              Como Vendedor
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-gray-600 dark:text-gray-300">
            Conecta con miles de clientes, aumenta tus ventas y haz crecer tu negocio con nuestras herramientas avanzadas.
          </p>
          <div className="flex items-center justify-center gap-4 mt-10">
            <button 
              onClick={handleRegisterClick}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl"
            >
              Únete Ahora Gratis
            </button>
            <button 
              onClick={handleLearnMoreClick}
              className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 px-8 py-3 text-lg rounded-lg transition-all duration-200"
            >
              Conoce Más
            </button>
          </div>
        </div>
      </section>

      {/* Stats Preview */}
      <section className="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">10K+</div>
            <div className="text-gray-600 dark:text-gray-300 mt-2">Vendedores Activos</div>
          </div>
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">$2M+</div>
            <div className="text-gray-600 dark:text-gray-300 mt-2">Ventas Mensuales</div>
          </div>
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">98%</div>
            <div className="text-gray-600 dark:text-gray-300 mt-2">Satisfacción</div>
          </div>
        </div>
      </section>

      {/* Beneficios para Vendedores */}
      <section data-section="benefits" className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            ¿Por qué elegir nuestra plataforma?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-300">
            Descubre los beneficios exclusivos que ofrecemos a nuestros vendedores
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Beneficio 1: Comisiones Competitivas */}
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl hover:shadow-xl transition-shadow duration-300">
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Comisiones Altas</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Hasta 15% de comisión por venta. Las mejores tarifas del mercado para maximizar tus ganancias.
            </p>
          </div>

          {/* Beneficio 2: Alcance Global */}
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl hover:shadow-xl transition-shadow duration-300">
            <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <span className="text-2xl">🌍</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Alcance Global</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Accede a miles de clientes potenciales en múltiples países y expande tu negocio sin límites.
            </p>
          </div>

          {/* Beneficio 3: Herramientas Avanzadas */}
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl hover:shadow-xl transition-shadow duration-300">
            <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
              <span className="text-2xl">🛠️</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Herramientas Pro</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Analytics avanzados, gestión de inventario, automatización de pedidos y mucho más.
            </p>
          </div>

          {/* Beneficio 4: Soporte 24/7 */}
          <div className="text-center p-6 bg-white dark:bg-gray-800 shadow-lg rounded-xl hover:shadow-xl transition-shadow duration-300">
            <div className="w-16 h-16 mx-auto mb-4 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center">
              <span className="text-2xl">🚀</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Soporte Total</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Equipo de soporte dedicado 24/7, capacitación gratuita y recursos de marketing incluidos.
            </p>
          </div>
        </div>
      </section>

      {/* Call to Action Final */}
      <section className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4 sm:text-4xl">
            ¿Listo para comenzar tu éxito?
          </h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            Únete a miles de vendedores que ya están creciendo con nosotros. 
            El registro es gratis y puedes comenzar a vender inmediatamente.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button 
              onClick={handleRegisterClick}
              className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl w-full sm:w-auto"
            >
              🚀 Registrarse Gratis Ahora
            </button>
            <button 
              className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-200 w-full sm:w-auto"
            >
              📞 Hablar con un Asesor
            </button>
          </div>
          <div className="mt-6 text-sm text-blue-100">
            ✅ Sin comisiones de registro • ✅ Soporte 24/7 • ✅ Pagos seguros
          </div>
        </div>
      </section>
    </div>
  );
};

export default VendorLanding;
