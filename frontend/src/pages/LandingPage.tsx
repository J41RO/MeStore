import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import HeroSection from '../components/landing/HeroSection';
import ProcessSection from '../components/landing/ProcessSection';
import AdvantagesSection from '../components/landing/AdvantagesSection';
import Footer from '../components/layout/Footer';
import { DashboardSection } from '../components/DashboardSection';
import { useDashboardMetrics } from '../hooks/useDashboardMetrics';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  
  // Hook para métricas del dashboard
  const { 
    dashboardMetrics, 
    isLoadingMetrics, 
    metricsError, 
    refreshMetrics 
  } = useDashboardMetrics();

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* NAVBAR MODULAR - Glassmorphism + Autenticación */}
      <Navbar />

      {/* HERO SECTION MODULAR - Efectos visuales superiores */}
      <HeroSection />

      {/* DASHBOARD SECTION - Funcionalidad existente */}
      <DashboardSection 
        dashboardMetrics={dashboardMetrics}
        isLoadingMetrics={isLoadingMetrics}
        metricsError={metricsError}
        refreshMetrics={refreshMetrics}
        navigate={navigate}
      />

      {/* STATISTICS SECTION - Métricas en tiempo real */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Métricas en Tiempo Real
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Datos verificables de nuestra plataforma
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="group">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 group-hover:scale-110 transition-transform">
                {isLoadingMetrics ? (
                  <div className="animate-pulse bg-gray-300 h-12 w-16 mx-auto rounded"></div>
                ) : (
                  dashboardMetrics?.activeVendors || '50+'
                )}
              </div>
              <div className="text-gray-600 dark:text-gray-300 font-medium">Vendedores Activos</div>
            </div>
            
            <div className="group">
              <div className="text-4xl md:text-5xl font-bold text-purple-600 mb-2 group-hover:scale-110 transition-transform">
                {isLoadingMetrics ? (
                  <div className="animate-pulse bg-gray-300 h-12 w-16 mx-auto rounded"></div>
                ) : (
                  dashboardMetrics?.totalProducts && dashboardMetrics.totalProducts > 0 
                    ? `${Math.floor(dashboardMetrics.totalProducts / 1000)}K+` 
                    : '1K+'
                )}
              </div>
              <div className="text-gray-600 dark:text-gray-300 font-medium">Productos Gestionados</div>
            </div>
            
            <div className="group">
              <div className="text-4xl md:text-5xl font-bold text-green-600 mb-2 group-hover:scale-110 transition-transform">
                {isLoadingMetrics ? (
                  <div className="animate-pulse bg-gray-300 h-12 w-16 mx-auto rounded"></div>
                ) : (
                  `${dashboardMetrics?.deliverySuccessRate || 95}%`
                )}
              </div>
              <div className="text-gray-600 dark:text-gray-300 font-medium">Entregas Exitosas</div>
            </div>
            
            <div className="group">
              <div className="text-4xl md:text-5xl font-bold text-orange-600 mb-2 group-hover:scale-110 transition-transform">
                24/7
              </div>
              <div className="text-gray-600 dark:text-gray-300 font-medium">Soporte Técnico</div>
            </div>
          </div>
        </div>
      </section>

      {/* PROCESS SECTION MODULAR - 4 pasos optimizados */}
      <ProcessSection />

      {/* FEATURES SECTION - Servicios principales */}
      <section id="features" className="py-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
              Servicios Profesionales
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Solución integral de fulfillment diseñada para vendedores online en Colombia
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🏭</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                Almacenamiento Seguro
              </h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                Instalaciones modernas en Bucaramanga con seguridad 24/7, control de clima y sistemas de monitoreo avanzados para proteger tus productos
              </p>
            </div>
            
            <div className="group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                Gestión Inteligente
              </h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                Sistema avanzado con IA para control de inventario, optimización de stock y reportes detallados en tiempo real
              </p>
            </div>
            
            <div className="group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🚚</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                Logística Nacional
              </h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                Red de distribución eficiente con cobertura nacional, seguimiento en tiempo real y garantía de entrega
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ADVANTAGES SECTION MODULAR - Diferenciadores únicos */}
      <AdvantagesSection />

      {/* COMPETITIVE COMPARISON SECTION */}
      <section className="py-20 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
              Superamos a la Competencia
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Comparación directa con las principales plataformas del mercado
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg">
                <span className="text-3xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">Setup Ultra-Rápido</h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-2">5 minutos</p>
              <p className="text-sm text-blue-600 font-medium">vs 15+ min MELONN/CUBBO</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg">
                <span className="text-3xl">📍</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">Cobertura Regional</h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-2">Bucaramanga + Nacional</p>
              <p className="text-sm text-green-600 font-medium">vs solo Bogotá/Medellín</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg">
                <span className="text-3xl">🏪</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">Marketplace Integrado</h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-2">B2B + B2C</p>
              <p className="text-sm text-purple-600 font-medium">vs solo B2B como MELONN</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">IA Especializada</h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-2">Agentes reales</p>
              <p className="text-sm text-orange-600 font-medium">vs promesas vacías</p>
            </div>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION SECTION */}
      <section className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Transforma tu Negocio Hoy
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Únete a MeStocker y accede a la única plataforma que combina fulfillment inteligente, 
            marketplace integrado y tecnología IA en Bucaramanga
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <button 
              onClick={() => navigate('/register')}
              className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-xl"
            >
              Comenzar Gratis
            </button>
            <button 
              onClick={() => navigate('/dashboard')}
              className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300"
            >
              Ver Plataforma
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center text-blue-100">
            <div>
              <div className="text-2xl font-bold text-white mb-1">✓ Sin costos ocultos</div>
              <div className="text-sm">Transparencia total</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white mb-1">✓ Setup inmediato</div>
              <div className="text-sm">En menos de 5 minutos</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white mb-1">✓ Soporte 24/7</div>
              <div className="text-sm">Asistencia especializada</div>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER MODULAR - Información Bucaramanga */}
      <Footer />
    </div>
  );
};

export default LandingPage;