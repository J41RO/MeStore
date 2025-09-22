/**
 * Colombian Market Visual Design System
 * Optimized for cultural preferences and marketplace UX
 */

// Colombian Market Color Psychology
export const COLOMBIAN_COLORS = {
  // Trust and reliability (Financial institutions, professional services)
  trust: {
    primary: '#2563eb', // Blue - Professional, reliable
    secondary: '#0f766e', // Teal - Modern, trustworthy
    accent: '#059669' // Green - Growth, prosperity
  },

  // Warmth and celebration (Local commerce, festivals)
  warmth: {
    primary: '#ea580c', // Orange - Energy, enthusiasm
    secondary: '#d97706', // Amber - Warmth, optimism
    accent: '#eab308' // Yellow - Joy, celebration
  },

  // Premium and luxury (High-end products)
  premium: {
    primary: '#1e40af', // Deep blue - Luxury, sophistication
    secondary: '#7c2d12', // Brown - Craftsmanship, heritage
    accent: '#a855f7' // Purple - Elegance, exclusivity
  },

  // Nature and sustainability (Organic, eco-friendly)
  nature: {
    primary: '#16a34a', // Green - Nature, health
    secondary: '#0d9488', // Emerald - Fresh, natural
    accent: '#65a30d' // Lime - Growth, vitality
  },

  // Alerts and status
  status: {
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#2563eb'
  }
};

// Product category visual system
export const PRODUCT_CATEGORIES = {
  electronics: {
    name: 'Electrónicos',
    colors: COLOMBIAN_COLORS.trust,
    icon: '📱',
    gradient: 'from-blue-50 to-blue-100',
    border: 'border-blue-200',
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    hover: 'hover:bg-blue-100',
    accent: 'accent-blue-500'
  },
  clothing: {
    name: 'Ropa y Accesorios',
    colors: COLOMBIAN_COLORS.warmth,
    icon: '👕',
    gradient: 'from-orange-50 to-orange-100',
    border: 'border-orange-200',
    bg: 'bg-orange-50',
    text: 'text-orange-700',
    hover: 'hover:bg-orange-100',
    accent: 'accent-orange-500'
  },
  home: {
    name: 'Hogar y Decoración',
    colors: COLOMBIAN_COLORS.nature,
    icon: '🏠',
    gradient: 'from-green-50 to-green-100',
    border: 'border-green-200',
    bg: 'bg-green-50',
    text: 'text-green-700',
    hover: 'hover:bg-green-100',
    accent: 'accent-green-500'
  },
  beauty: {
    name: 'Belleza y Cuidado',
    colors: { primary: '#ec4899', secondary: '#be185d', accent: '#f472b6' },
    icon: '💄',
    gradient: 'from-pink-50 to-pink-100',
    border: 'border-pink-200',
    bg: 'bg-pink-50',
    text: 'text-pink-700',
    hover: 'hover:bg-pink-100',
    accent: 'accent-pink-500'
  },
  sports: {
    name: 'Deportes y Fitness',
    colors: { primary: '#059669', secondary: '#047857', accent: '#10b981' },
    icon: '⚽',
    gradient: 'from-emerald-50 to-emerald-100',
    border: 'border-emerald-200',
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    hover: 'hover:bg-emerald-100',
    accent: 'accent-emerald-500'
  },
  books: {
    name: 'Libros y Educación',
    colors: COLOMBIAN_COLORS.premium,
    icon: '📚',
    gradient: 'from-purple-50 to-purple-100',
    border: 'border-purple-200',
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    hover: 'hover:bg-purple-100',
    accent: 'accent-purple-500'
  },
  automotive: {
    name: 'Automotriz',
    colors: { primary: '#374151', secondary: '#1f2937', accent: '#6b7280' },
    icon: '🚗',
    gradient: 'from-gray-50 to-gray-100',
    border: 'border-gray-200',
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    hover: 'hover:bg-gray-100',
    accent: 'accent-gray-500'
  }
} as const;

// Product status visual indicators
export const PRODUCT_STATUS = {
  active: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-200',
    icon: '✅',
    label: 'Activo'
  },
  inactive: {
    bg: 'bg-gray-100',
    text: 'text-gray-600',
    border: 'border-gray-200',
    icon: '⏸️',
    label: 'Inactivo'
  },
  featured: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-200',
    icon: '⭐',
    label: 'Destacado'
  },
  outOfStock: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-200',
    icon: '❌',
    label: 'Agotado'
  },
  lowStock: {
    bg: 'bg-orange-100',
    text: 'text-orange-800',
    border: 'border-orange-200',
    icon: '⚠️',
    label: 'Stock Bajo'
  }
} as const;

// Colombian market specific spacing and sizing
export const SPACING = {
  // Touch-friendly mobile targets (44px minimum)
  touchTarget: {
    minWidth: '44px',
    minHeight: '44px',
    padding: '12px'
  },

  // Card spacing for Colombian reading patterns
  card: {
    padding: '16px',
    margin: '12px',
    borderRadius: '12px',
    gap: '16px'
  },

  // Grid layouts optimized for Colombian device usage
  grid: {
    mobile: 'grid-cols-1',
    tablet: 'sm:grid-cols-2',
    desktop: 'lg:grid-cols-3 xl:grid-cols-4',
    gap: 'gap-4'
  },

  // Typography hierarchy
  text: {
    hero: 'text-3xl font-bold',
    title: 'text-xl font-semibold',
    subtitle: 'text-lg font-medium',
    body: 'text-base',
    caption: 'text-sm',
    small: 'text-xs'
  }
} as const;

// Animation settings for smooth 60fps performance
export const ANIMATIONS = {
  // Drag and drop
  drag: {
    duration: 200,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    scale: 1.05,
    opacity: 0.8
  },

  // Hover effects
  hover: {
    duration: 150,
    scale: 1.02,
    shadowIntensity: 'hover:shadow-lg'
  },

  // State transitions
  state: {
    duration: 200,
    easing: 'ease-in-out'
  },

  // Loading and feedback
  loading: {
    spin: 'animate-spin',
    pulse: 'animate-pulse',
    bounce: 'animate-bounce'
  }
} as const;

// Accessibility helpers
export const ACCESSIBILITY = {
  // Focus indicators
  focus: {
    ring: 'focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
    outline: 'focus:outline-none'
  },

  // Screen reader
  srOnly: 'sr-only',

  // Color contrast (WCAG AA compliant)
  contrast: {
    text: 'contrast-[1.5]',
    background: 'contrast-[1.3]'
  },

  // Motion preferences
  motion: {
    reduce: 'motion-reduce:transition-none motion-reduce:animate-none'
  }
} as const;

// Utility functions
export const getProductCategoryStyle = (categoryId: string) => {
  return PRODUCT_CATEGORIES[categoryId as keyof typeof PRODUCT_CATEGORIES] || PRODUCT_CATEGORIES.electronics;
};

export const getStatusStyle = (status: keyof typeof PRODUCT_STATUS) => {
  return PRODUCT_STATUS[status];
};

export const formatColombianCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

export const formatColombianDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Performance optimization helpers
export const generateOptimizedClasses = (category: string, isSelected: boolean, isDragging: boolean) => {
  const categoryStyle = getProductCategoryStyle(category);

  return {
    card: `
      relative bg-white rounded-lg border-2 transition-all duration-200 hover:shadow-lg group
      ${isSelected ? `border-primary-500 shadow-mestocker ${categoryStyle.bg}` : `${categoryStyle.border} hover:border-neutral-300`}
      ${isDragging ? 'opacity-50 rotate-1 scale-105' : ''}
      ${ACCESSIBILITY.motion.reduce}
    `.trim(),

    category: `
      inline-block px-2 py-1 text-xs font-medium rounded
      ${categoryStyle.bg} ${categoryStyle.text}
    `.trim()
  };
};

export default {
  COLOMBIAN_COLORS,
  PRODUCT_CATEGORIES,
  PRODUCT_STATUS,
  SPACING,
  ANIMATIONS,
  ACCESSIBILITY,
  getProductCategoryStyle,
  getStatusStyle,
  formatColombianCurrency,
  formatColombianDate,
  generateOptimizedClasses
};