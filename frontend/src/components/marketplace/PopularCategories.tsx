import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Smartphone, 
  Shirt, 
  Home, 
  Dumbbell, 
  BookOpen, 
  Sparkles, 
  Baby, 
  Car 
} from 'lucide-react';

interface Category {
  id: string;
  name: string;
  icon: React.ReactNode;
  productCount: number;
  image: string;
  color: string;
}

const PopularCategories: React.FC = () => {
  const categories: Category[] = [
    {
      id: 'electronics',
      name: 'Electrónicos',
      icon: <Smartphone className="w-8 h-8" />,
      productCount: 150,
      image: '/images/categories/electronics.jpg',
      color: 'bg-blue-500'
    },
    {
      id: 'fashion',
      name: 'Ropa y Moda',
      icon: <Shirt className="w-8 h-8" />,
      productCount: 200,
      image: '/images/categories/fashion.jpg',
      color: 'bg-pink-500'
    },
    {
      id: 'home',
      name: 'Hogar y Jardín',
      icon: <Home className="w-8 h-8" />,
      productCount: 120,
      image: '/images/categories/home.jpg',
      color: 'bg-green-500'
    },
    {
      id: 'sports',
      name: 'Deportes y Fitness',
      icon: <Dumbbell className="w-8 h-8" />,
      productCount: 80,
      image: '/images/categories/sports.jpg',
      color: 'bg-red-500'
    },
    {
      id: 'books',
      name: 'Libros y Educación',
      icon: <BookOpen className="w-8 h-8" />,
      productCount: 90,
      image: '/images/categories/books.jpg',
      color: 'bg-purple-500'
    },
    {
      id: 'beauty',
      name: 'Belleza y Cuidado Personal',
      icon: <Sparkles className="w-8 h-8" />,
      productCount: 110,
      image: '/images/categories/beauty.jpg',
      color: 'bg-yellow-500'
    },
    {
      id: 'baby',
      name: 'Bebés y Niños',
      icon: <Baby className="w-8 h-8" />,
      productCount: 75,
      image: '/images/categories/baby.jpg',
      color: 'bg-indigo-500'
    },
    {
      id: 'automotive',
      name: 'Automotriz',
      icon: <Car className="w-8 h-8" />,
      productCount: 60,
      image: '/images/categories/automotive.jpg',
      color: 'bg-gray-600'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
      {categories.map((category) => (
        <Link
          key={category.id}
          to={`/marketplace/category/${category.id}`}
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