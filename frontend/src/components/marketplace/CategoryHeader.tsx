import React from 'react';
import { Breadcrumb } from '../ui/Breadcrumb/Breadcrumb';
import { 
  Smartphone, 
  Shirt, 
  Home, 
  Dumbbell, 
  BookOpen, 
  Sparkles, 
  Baby, 
  Car,
  Grid3x3
} from 'lucide-react';

interface CategoryHeaderProps {
  categoryName: string;
  productCount: number;
  categorySlug: string;
  loading?: boolean;
}

// Mapeo de iconos por categoría
const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  'electronics': <Smartphone className="w-8 h-8" />,
  'fashion': <Shirt className="w-8 h-8" />,
  'home': <Home className="w-8 h-8" />,
  'sports': <Dumbbell className="w-8 h-8" />,
  'books': <BookOpen className="w-8 h-8" />,
  'beauty': <Sparkles className="w-8 h-8" />,
  'baby': <Baby className="w-8 h-8" />,
  'automotive': <Car className="w-8 h-8" />
};

// Colores por categoría
const CATEGORY_COLORS: Record<string, string> = {
  'electronics': 'bg-blue-500',
  'fashion': 'bg-pink-500',
  'home': 'bg-green-500',
  'sports': 'bg-red-500',
  'books': 'bg-purple-500',
  'beauty': 'bg-yellow-500',
  'baby': 'bg-indigo-500',
  'automotive': 'bg-gray-600'
};

// Descripciones por categoría
const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  'electronics': 'Encuentra los últimos dispositivos electrónicos, smartphones, computadoras y accesorios tecnológicos.',
  'fashion': 'Descubre las últimas tendencias en ropa, calzado y accesorios para hombres, mujeres y niños.',
  'home': 'Todo lo que necesitas para tu hogar y jardín: muebles, decoración, electrodomésticos y más.',
  'sports': 'Equipamiento deportivo, ropa fitness y accesorios para mantenerte activo y saludable.',
  'books': 'Libros, material educativo, revistas y recursos para el aprendizaje y el entretenimiento.',
  'beauty': 'Productos de belleza, cuidado personal, cosméticos y perfumes de las mejores marcas.',
  'baby': 'Todo lo necesario para bebés y niños: ropa, juguetes, alimentación y cuidado infantil.',
  'automotive': 'Repuestos, accesorios y productos para el cuidado y mantenimiento de tu vehículo.'
};

const CategoryHeader: React.FC<CategoryHeaderProps> = ({
  categoryName,
  productCount,
  categorySlug,
  loading = false
}) => {
  const categoryIcon = CATEGORY_ICONS[categorySlug] || <Grid3x3 className="w-8 h-8" />;
  const categoryColor = CATEGORY_COLORS[categorySlug] || 'bg-gray-500';
  const categoryDescription = CATEGORY_DESCRIPTIONS[categorySlug] || 'Explora nuestra selección de productos en esta categoría.';

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {/* Breadcrumb Navigation */}
      <div className="px-6 pt-4 pb-2 bg-gray-50 border-b">
        <Breadcrumb />
      </div>

      {/* Category Header Content */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          {/* Left Section - Category Info */}
          <div className="flex items-start space-x-4">
            {/* Category Icon */}
            <div className={`${categoryColor} text-white p-4 rounded-xl shadow-lg flex-shrink-0`}>
              {categoryIcon}
            </div>

            {/* Category Details */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {categoryName}
              </h1>
              
              <p className="text-gray-600 mb-4 max-w-2xl leading-relaxed">
                {categoryDescription}
              </p>

              {/* Product Count */}
              <div className="flex items-center space-x-2">
                <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                  {loading ? (
                    <span className="inline-flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-700" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Cargando...
                    </span>
                  ) : (
                    `${productCount.toLocaleString()} productos disponibles`
                  )}
                </div>
                
                {productCount > 0 && !loading && (
                  <span className="text-green-600 text-sm">
                    ✓ En stock
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Right Section - Category Stats */}
          <div className="hidden lg:flex flex-col items-end space-y-2">
            <div className="bg-gray-50 rounded-lg p-4 text-center min-w-[120px]">
              <div className="text-2xl font-bold text-gray-900">
                {loading ? '---' : productCount.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Productos</div>
            </div>
            
            {!loading && productCount > 0 && (
              <div className="bg-green-50 rounded-lg p-3 text-center min-w-[120px]">
                <div className="text-lg font-semibold text-green-700">
                  Disponible
                </div>
                <div className="text-xs text-green-600">Envío inmediato</div>
              </div>
            )}
          </div>
        </div>

        {/* Category Tags/Features */}
        <div className="mt-6 flex flex-wrap gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            🚚 Envío gratis
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            ✨ Productos verificados
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            🛡️ Garantía incluida
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
            💳 Pago seguro
          </span>
        </div>
      </div>

      {/* Bottom Border Accent */}
      <div className={`h-1 ${categoryColor}`}></div>
    </div>
  );
};

export default CategoryHeader;