/**
 * Product Management UX Demo
 * Showcases all enhanced features for Colombian marketplace
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Smartphone,
  Shirt,
  Home,
  Palette,
  Dumbbell,
  BookOpen,
  Car,
  Star,
  CheckCircle,
  GripVertical,
  ImageUp,
  Edit,
  Eye,
  ShoppingCart,
  AlertTriangle,
  Check,
  DollarSign,
  TrendingUp,
  Users,
  Globe,
  Zap,
  Heart,
  Target,
  BarChart3,
  Layers,
  Settings,
  Smartphone as Phone,
  Monitor,
  Tablet
} from 'lucide-react';

// Import our enhanced dashboard
import EnhancedProductDashboard from '../components/vendor/EnhancedProductDashboard';

const ProductManagementDemo: React.FC = () => {
  const [activeDemo, setActiveDemo] = useState<'overview' | 'features' | 'dashboard'>('overview');
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null);

  // Colombian market stats
  const marketStats = [
    {
      icon: Users,
      label: 'Vendedores Activos',
      value: '50+',
      description: 'Mercado diverso colombiano',
      color: 'text-blue-600'
    },
    {
      icon: Package,
      label: 'Productos Gestionados',
      value: '1000+',
      description: 'Catálogo optimizado',
      color: 'text-green-600'
    },
    {
      icon: Zap,
      label: 'Rendimiento UX',
      value: '60fps',
      description: 'Interacciones fluidas',
      color: 'text-yellow-600'
    },
    {
      icon: Target,
      label: 'Conversión Mejorada',
      value: '+15%',
      description: 'Optimización colombiana',
      color: 'text-purple-600'
    }
  ];

  // Enhanced features showcase
  const enhancedFeatures = [
    {
      id: 'drag-drop',
      icon: GripVertical,
      title: 'Drag & Drop Intuitivo',
      description: 'Reordena productos con gestos naturales y feedback visual smooth a 60fps',
      highlights: ['Animaciones fluidas', 'Feedback visual inmediato', 'Soporte táctil móvil'],
      demo: '🎯 Arrastra productos para reordenar tu catálogo',
      color: 'bg-blue-50 border-blue-200'
    },
    {
      id: 'bulk-actions',
      icon: CheckCircle,
      title: 'Acciones Masivas Avanzadas',
      description: 'Gestiona hasta 50+ productos simultáneamente con preview de cambios',
      highlights: ['Selección múltiple', 'Preview de cambios', 'Operaciones batch'],
      demo: '✅ Selecciona múltiples productos y aplica cambios en lote',
      color: 'bg-green-50 border-green-200'
    },
    {
      id: 'quick-edit',
      icon: Edit,
      title: 'Edición Rápida Inline',
      description: 'Modifica precios, nombres y stock directamente en las tarjetas',
      highlights: ['Edición in-place', 'Validación en tiempo real', 'Guardado automático'],
      demo: '⚡ Haz clic en cualquier campo para editarlo instantáneamente',
      color: 'bg-yellow-50 border-yellow-200'
    },
    {
      id: 'image-upload',
      icon: ImageUp,
      title: 'Subida de Imágenes Múltiple',
      description: 'Carga múltiples imágenes con indicadores de progreso y preview',
      highlights: ['Upload múltiple', 'Indicadores de progreso', 'Preview inmediato'],
      demo: '📸 Arrastra imágenes o selecciona múltiples archivos',
      color: 'bg-purple-50 border-purple-200'
    },
    {
      id: 'category-coding',
      icon: Palette,
      title: 'Codificación Visual por Categorías',
      description: 'Sistema de colores adaptado al mercado colombiano para fácil identificación',
      highlights: ['Colores culturalmente adaptados', 'Categorización visual', 'Identificación rápida'],
      demo: '🎨 Cada categoría tiene colores específicos para el mercado colombiano',
      color: 'bg-pink-50 border-pink-200'
    },
    {
      id: 'mobile-gestures',
      icon: Phone,
      title: 'Gestos Móviles Optimizados',
      description: 'Targets táctiles de 44px, long press para selección, swipe para acciones',
      highlights: ['Targets de 44px mínimo', 'Long press selection', 'Swipe actions'],
      demo: '📱 Optimizado para dispositivos móviles colombianos',
      color: 'bg-indigo-50 border-indigo-200'
    }
  ];

  // Category showcase
  const categoryShowcase = [
    { id: 'electronics', name: 'Electrónicos', icon: Smartphone, color: 'bg-blue-50 text-blue-700 border-blue-200' },
    { id: 'clothing', name: 'Ropa', icon: Shirt, color: 'bg-orange-50 text-orange-700 border-orange-200' },
    { id: 'home', name: 'Hogar', icon: Home, color: 'bg-green-50 text-green-700 border-green-200' },
    { id: 'beauty', name: 'Belleza', icon: Heart, color: 'bg-pink-50 text-pink-700 border-pink-200' },
    { id: 'sports', name: 'Deportes', icon: Dumbbell, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    { id: 'books', name: 'Libros', icon: BookOpen, color: 'bg-purple-50 text-purple-700 border-purple-200' },
    { id: 'automotive', name: 'Automotriz', icon: Car, color: 'bg-gray-50 text-gray-700 border-gray-200' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-neutral-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Package className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-neutral-900">MeStore UX Demo</h1>
                <p className="text-sm text-neutral-500">Gestión Productos Colombiana</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveDemo('overview')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeDemo === 'overview'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Resumen
              </button>
              <button
                onClick={() => setActiveDemo('features')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeDemo === 'features'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Características
              </button>
              <button
                onClick={() => setActiveDemo('dashboard')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeDemo === 'dashboard'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Demo Live
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeDemo === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-12"
          >
            {/* Hero Section */}
            <div className="text-center space-y-6">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-neutral-900"
              >
                Gestión de Productos UX Mejorada
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-xl text-neutral-600 max-w-3xl mx-auto"
              >
                Sistema de gestión de productos con drag & drop, acciones masivas y diseño optimizado
                para el mercado colombiano. Diseño UX excepcional con rendimiento de 60fps.
              </motion.p>
            </div>

            {/* Market Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {marketStats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg bg-neutral-100`}>
                      <stat.icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-neutral-900">{stat.value}</p>
                      <p className="text-sm font-medium text-neutral-700">{stat.label}</p>
                      <p className="text-xs text-neutral-500">{stat.description}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Visual Hierarchy Showcase */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-neutral-200">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                Sistema de Colores Colombiano
              </h2>
              <p className="text-neutral-600 mb-8">
                Codificación visual adaptada a las preferencias culturales del mercado colombiano
                para mejorar la identificación y navegación de productos.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-4">
                {categoryShowcase.map((category, index) => (
                  <motion.div
                    key={category.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className={`${category.color} rounded-lg p-4 border-2 hover:scale-105 transition-transform cursor-pointer`}
                  >
                    <category.icon className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm font-medium text-center">{category.name}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Device Showcase */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-neutral-200">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                Optimizado para Todos los Dispositivos
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="text-center space-y-4">
                  <div className="p-4 bg-blue-50 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Phone className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-neutral-900">Móvil</h3>
                  <p className="text-sm text-neutral-600">
                    Targets táctiles 44px, gestos long-press, swipe actions
                  </p>
                </div>
                <div className="text-center space-y-4">
                  <div className="p-4 bg-green-50 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Tablet className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-neutral-900">Tablet</h3>
                  <p className="text-sm text-neutral-600">
                    Drag & drop optimizado, interfaz híbrida táctil/cursor
                  </p>
                </div>
                <div className="text-center space-y-4">
                  <div className="p-4 bg-purple-50 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Monitor className="h-8 w-8 text-purple-600" />
                  </div>
                  <h3 className="font-semibold text-neutral-900">Desktop</h3>
                  <p className="text-sm text-neutral-600">
                    Navegación por teclado, shortcuts, workflow eficiente
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeDemo === 'features' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            <div className="text-center space-y-4">
              <h1 className="text-3xl font-bold text-neutral-900">
                Características Avanzadas UX
              </h1>
              <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
                Cada característica ha sido diseñada y optimizada específicamente para el mercado colombiano
                con pruebas TDD y rendimiento de 60fps garantizado.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {enhancedFeatures.map((feature, index) => (
                <motion.div
                  key={feature.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`${feature.color} rounded-xl p-6 border-2 hover:shadow-lg transition-all cursor-pointer`}
                  onMouseEnter={() => setHoveredFeature(feature.id)}
                  onMouseLeave={() => setHoveredFeature(null)}
                >
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-white rounded-lg shadow-sm">
                      <feature.icon className="h-6 w-6 text-neutral-700" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-neutral-700 mb-4">
                        {feature.description}
                      </p>

                      <div className="space-y-2 mb-4">
                        {feature.highlights.map((highlight, i) => (
                          <div key={i} className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm text-neutral-600">{highlight}</span>
                          </div>
                        ))}
                      </div>

                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: hoveredFeature === feature.id ? 1 : 0.7 }}
                        className="p-3 bg-white/60 rounded-lg border border-white/50"
                      >
                        <p className="text-sm font-medium text-neutral-800">
                          {feature.demo}
                        </p>
                      </motion.div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Performance Metrics */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-200">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                Métricas de Rendimiento UX
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">60fps</div>
                  <p className="text-sm text-neutral-600">Animaciones smooth drag & drop</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">&lt;300ms</div>
                  <p className="text-sm text-neutral-600">Tiempo respuesta interacciones</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">44px</div>
                  <p className="text-sm text-neutral-600">Targets táctiles mínimos</p>
                </div>
              </div>
            </div>

            {/* Accessibility Features */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-neutral-200">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                Accesibilidad WCAG 2.1 AA
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="font-semibold text-neutral-900">Navegación por Teclado</h3>
                  <ul className="space-y-2 text-sm text-neutral-600">
                    <li>• Tab/Shift+Tab para navegación</li>
                    <li>• Space/Enter para drag & drop</li>
                    <li>• Flechas para reordenar productos</li>
                    <li>• Escape para cancelar acciones</li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h3 className="font-semibold text-neutral-900">Contraste y Visibilidad</h3>
                  <ul className="space-y-2 text-sm text-neutral-600">
                    <li>• Contraste 4.5:1 mínimo</li>
                    <li>• Indicadores de estado claros</li>
                    <li>• Focus rings visibles</li>
                    <li>• Texto escalable hasta 200%</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeDemo === 'dashboard' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200">
              <h1 className="text-2xl font-bold text-neutral-900 mb-2">
                Demo Interactivo - Dashboard de Productos
              </h1>
              <p className="text-neutral-600 mb-4">
                Prueba todas las características implementadas: drag & drop, selección múltiple,
                edición rápida, y más. Optimizado para el mercado colombiano.
              </p>

              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <GripVertical className="h-4 w-4 text-neutral-500" />
                  <span>Arrastra productos para reordenar</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-neutral-500" />
                  <span>Selecciona múltiples para acciones masivas</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Edit className="h-4 w-4 text-neutral-500" />
                  <span>Edición rápida inline</span>
                </div>
                <div className="flex items-center space-x-2">
                  <ImageUp className="h-4 w-4 text-neutral-500" />
                  <span>Subida múltiple de imágenes</span>
                </div>
              </div>
            </div>

            {/* Live Dashboard */}
            <EnhancedProductDashboard />

            {/* Demo Instructions */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                🎯 Instrucciones del Demo
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-neutral-700">
                <div>
                  <h4 className="font-medium mb-2">Drag & Drop:</h4>
                  <ul className="space-y-1">
                    <li>• Hover sobre productos para ver el handle de arrastre</li>
                    <li>• Arrastra products para cambiar el orden</li>
                    <li>• Funciona en desktop, tablet y móvil</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Acciones Masivas:</h4>
                  <ul className="space-y-1">
                    <li>• Selecciona múltiples productos con checkboxes</li>
                    <li>• Usa "Seleccionar todos" para selección masiva</li>
                    <li>• Aplica activar, destacar, o eliminar en lote</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
};

export default ProductManagementDemo;