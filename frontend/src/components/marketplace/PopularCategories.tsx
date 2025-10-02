import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Smartphone,
  Shirt,
  Home,
  Dumbbell,
  BookOpen,
  Sparkles,
  Baby,
  Car,
  Loader2
} from 'lucide-react';
import api from '../../services/api';
import { Category as CategoryType } from '../../types/category.types';

interface CategoryDisplay {
  id: string;
  name: string;
  icon: React.ReactNode;
  productCount: number;
  color: string;
}

// Icon mapping for categories
const getCategoryIcon = (categoryName: string): React.ReactNode => {
  const name = categoryName.toLowerCase();

  if (name.includes('electr') || name.includes('tecn')) return <Smartphone className="w-8 h-8" />;
  if (name.includes('ropa') || name.includes('moda') || name.includes('vest')) return <Shirt className="w-8 h-8" />;
  if (name.includes('hogar') || name.includes('jard')) return <Home className="w-8 h-8" />;
  if (name.includes('deport') || name.includes('fitness')) return <Dumbbell className="w-8 h-8" />;
  if (name.includes('libro') || name.includes('educ')) return <BookOpen className="w-8 h-8" />;
  if (name.includes('belle') || name.includes('cuid')) return <Sparkles className="w-8 h-8" />;
  if (name.includes('beb') || name.includes('niño')) return <Baby className="w-8 h-8" />;
  if (name.includes('auto') || name.includes('veh')) return <Car className="w-8 h-8" />;

  // Default icon
  return <Smartphone className="w-8 h-8" />;
};

// Color mapping for categories
const getCategoryColor = (index: number): string => {
  const colors = [
    'bg-blue-500',
    'bg-pink-500',
    'bg-green-500',
    'bg-red-500',
    'bg-purple-500',
    'bg-yellow-500',
    'bg-indigo-500',
    'bg-gray-600'
  ];
  return colors[index % colors.length];
};

const PopularCategories: React.FC = () => {
  const [categories, setCategories] = useState<CategoryDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.products.getCategories();

        // Filter active categories, sort by product count, and take top 8
        // Extract categories from paginated response
        const activeCategories = (response.data.categories || [])
          .filter((cat: CategoryType) => cat.is_active)
          .sort((a: CategoryType, b: CategoryType) => (b.products_count || 0) - (a.products_count || 0))
          .slice(0, 8)
          .map((cat: CategoryType, index: number): CategoryDisplay => ({
            id: cat.id,
            name: cat.name,
            icon: getCategoryIcon(cat.name),
            productCount: cat.products_count || 0,
            color: getCategoryColor(index)
          }));

        setCategories(activeCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setError('Error al cargar categorías');
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  // Show loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <span className="ml-3 text-gray-600">Cargando categorías...</span>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <p className="text-gray-500 mt-2">Por favor, intenta nuevamente más tarde.</p>
      </div>
    );
  }

  // Show empty state
  if (categories.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No hay categorías disponibles en este momento.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
      {categories.map((category) => (
        <Link
          key={category.id}
          to={`/catalog?category=${category.id}`}
          className="group flex flex-col items-center p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-gray-200"
        >
          {/* Icon Container */}
          <div className={`${category.color} text-white p-4 rounded-full mb-3 group-hover:scale-110 transition-transform duration-200`}>
            {category.icon}
          </div>

          {/* Category Info */}
          <h3 className="text-sm font-medium text-gray-900 text-center mb-1 group-hover:text-blue-600 transition-colors">
            {category.name}
          </h3>

          <p className="text-xs text-gray-500">
            {category.productCount} productos
          </p>
        </Link>
      ))}
    </div>
  );
};

export default PopularCategories;