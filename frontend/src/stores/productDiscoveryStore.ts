// ~/src/stores/productDiscoveryStore.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Product Discovery State Management with Zustand
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: productDiscoveryStore.ts
// Ruta: ~/src/stores/productDiscoveryStore.ts
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Estado optimizado para descubrimiento de productos
//
// Performance Features:
// - Optimized state updates with immer
// - Memoized selectors
// - Debounced search actions
// - Cache management
// - Real-time synchronization
// - Performance monitoring
// ---------------------------------------------------------------------------------------------

import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { StateCreator } from 'zustand';

// Types
interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  images: string[];
  rating: number;
  reviewCount: number;
  brand: string;
  category: string;
  subcategory: string;
  tags: string[];
  location: string;
  stock: number;
  shipping: {
    free: boolean;
    express: boolean;
    estimatedDays: number;
  };
  vendor: {
    id: string;
    name: string;
    rating: number;
    verified: boolean;
  };
  badges: string[];
  createdAt: string;
  updatedAt: string;
  similarity?: number;
  recommendationScore?: number;
  recommendationReason?: string;
  position?: number;
}

interface SearchFilters {
  categories: string[];
  priceRange: [number, number];
  rating: number;
  brands: string[];
  locations: string[];
  availability: string[];
  shipping: string[];
  features: string[];
  condition: string[];
}

interface SearchState {
  query: string;
  filters: SearchFilters;
  sortBy: string;
  results: Product[];
  totalResults: number;
  currentPage: number;
  hasNextPage: boolean;
  isLoading: boolean;
  error: string | null;
  lastSearchTime: number;
}

interface RecommendationState {
  trending: Product[];
  personalized: Product[];
  similar: Product[];
  recentlyViewed: Product[];
  categories: Record<string, Product[]>;
  isLoading: boolean;
  error: string | null;
  lastUpdated: number;
}

interface CacheState {
  searchResults: Record<string, {
    data: Product[];
    timestamp: number;
    totalResults: number;
  }>;
  recommendations: Record<string, {
    data: Product[];
    timestamp: number;
  }>;
  suggestions: Record<string, {
    data: any[];
    timestamp: number;
  }>;
}

interface PerformanceMetrics {
  searchLatency: number[];
  renderTime: number[];
  cacheHitRate: number;
  totalSearches: number;
  averageResultsPerSearch: number;
  userEngagement: {
    clickThroughRate: number;
    dwellTime: number;
    bounceRate: number;
  };
}

interface UserBehavior {
  searchHistory: Array<{
    query: string;
    timestamp: number;
    results: number;
  }>;
  viewedProducts: Set<string>;
  clickedProducts: Array<{
    productId: string;
    timestamp: number;
    source: string;
    position: number;
  }>;
  preferences: {
    categories: string[];
    brands: string[];
    priceRange: [number, number];
  };
}

interface ProductDiscoveryState {
  // Search state
  search: SearchState;

  // Recommendations state
  recommendations: RecommendationState;

  // Cache state
  cache: CacheState;

  // Performance metrics
  performance: PerformanceMetrics;

  // User behavior
  userBehavior: UserBehavior;

  // Configuration
  config: {
    cacheTimeout: number;
    debounceDelay: number;
    resultsPerPage: number;
    enableRealTime: boolean;
    performanceMode: 'balanced' | 'performance' | 'quality';
  };
}

interface ProductDiscoveryActions {
  // Search actions
  setQuery: (query: string) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  setSortBy: (sortBy: string) => void;
  search: (query: string, filters?: Partial<SearchFilters>) => Promise<void>;
  loadMore: () => Promise<void>;
  clearSearch: () => void;

  // Recommendation actions
  loadRecommendations: (type: string, params?: any) => Promise<void>;
  refreshRecommendations: () => Promise<void>;

  // Cache actions
  getCachedResults: (key: string) => any;
  setCachedResults: (key: string, data: any) => void;
  clearCache: (type?: string) => void;

  // User behavior actions
  trackSearch: (query: string, results: number) => void;
  trackProductView: (productId: string, context: any) => void;
  trackProductClick: (productId: string, context: any) => void;
  updatePreferences: (preferences: Partial<UserBehavior['preferences']>) => void;

  // Performance actions
  trackPerformance: (metric: string, value: number) => void;
  getPerformanceReport: () => PerformanceMetrics;

  // Utility actions
  reset: () => void;
  optimize: () => void;
}

type ProductDiscoveryStore = ProductDiscoveryState & ProductDiscoveryActions;

// Initial state
const initialState: ProductDiscoveryState = {
  search: {
    query: '',
    filters: {
      categories: [],
      priceRange: [0, 10000000],
      rating: 0,
      brands: [],
      locations: [],
      availability: [],
      shipping: [],
      features: [],
      condition: [],
    },
    sortBy: 'relevance',
    results: [],
    totalResults: 0,
    currentPage: 1,
    hasNextPage: false,
    isLoading: false,
    error: null,
    lastSearchTime: 0,
  },

  recommendations: {
    trending: [],
    personalized: [],
    similar: [],
    recentlyViewed: [],
    categories: {},
    isLoading: false,
    error: null,
    lastUpdated: 0,
  },

  cache: {
    searchResults: {},
    recommendations: {},
    suggestions: {},
  },

  performance: {
    searchLatency: [],
    renderTime: [],
    cacheHitRate: 0,
    totalSearches: 0,
    averageResultsPerSearch: 0,
    userEngagement: {
      clickThroughRate: 0,
      dwellTime: 0,
      bounceRate: 0,
    },
  },

  userBehavior: {
    searchHistory: [],
    viewedProducts: new Set(),
    clickedProducts: [],
    preferences: {
      categories: [],
      brands: [],
      priceRange: [0, 10000000],
    },
  },

  config: {
    cacheTimeout: 5 * 60 * 1000, // 5 minutes
    debounceDelay: 300,
    resultsPerPage: 20,
    enableRealTime: true,
    performanceMode: 'balanced',
  },
};

// API functions (would be replaced with actual API calls)
const searchAPI = {
  searchProducts: async (query: string, filters: any, page: number = 1): Promise<{
    products: Product[];
    total: number;
    hasNext: boolean;
  }> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 100));

    // Mock data
    const mockProducts: Product[] = Array.from({ length: 20 }, (_, i) => ({
      id: `product_${Date.now()}_${i}`,
      name: `Producto ${i + 1} - ${query}`,
      price: Math.floor(Math.random() * 500000) + 50000,
      originalPrice: Math.random() > 0.7 ? Math.floor(Math.random() * 600000) + 100000 : undefined,
      images: [`/api/placeholder/300/300?text=Product${i + 1}`],
      rating: Math.round((Math.random() * 2 + 3) * 10) / 10,
      reviewCount: Math.floor(Math.random() * 1000),
      brand: ['Samsung', 'Apple', 'Sony', 'LG', 'Xiaomi'][Math.floor(Math.random() * 5)],
      category: ['Electronics', 'Clothing', 'Home', 'Sports'][Math.floor(Math.random() * 4)],
      subcategory: 'Smartphones',
      tags: ['new', 'popular', 'sale'].filter(() => Math.random() > 0.7),
      location: ['Bogotá', 'Medellín', 'Cali', 'Barranquilla'][Math.floor(Math.random() * 4)],
      stock: Math.floor(Math.random() * 100),
      shipping: {
        free: Math.random() > 0.5,
        express: Math.random() > 0.7,
        estimatedDays: Math.floor(Math.random() * 7) + 1,
      },
      vendor: {
        id: `vendor_${i}`,
        name: `Vendor ${i + 1}`,
        rating: Math.round((Math.random() * 2 + 3) * 10) / 10,
        verified: Math.random() > 0.3,
      },
      badges: ['Bestseller', 'New', 'Sale'].filter(() => Math.random() > 0.8),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }));

    return {
      products: mockProducts,
      total: Math.floor(Math.random() * 1000) + 100,
      hasNext: Math.random() > 0.3,
    };
  },

  getRecommendations: async (type: string, params: any = {}): Promise<Product[]> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 150));

    // Mock recommendations
    return Array.from({ length: 12 }, (_, i) => ({
      id: `rec_${type}_${Date.now()}_${i}`,
      name: `Recomendado ${i + 1} - ${type}`,
      price: Math.floor(Math.random() * 300000) + 30000,
      images: [`/api/placeholder/300/300?text=Rec${i + 1}`],
      rating: Math.round((Math.random() * 1.5 + 3.5) * 10) / 10,
      reviewCount: Math.floor(Math.random() * 500),
      brand: ['Nike', 'Adidas', 'Puma', 'Reebok'][Math.floor(Math.random() * 4)],
      category: 'Sports',
      subcategory: 'Shoes',
      tags: ['recommended', 'trending'],
      location: 'Bogotá',
      stock: Math.floor(Math.random() * 50) + 5,
      shipping: {
        free: true,
        express: Math.random() > 0.5,
        estimatedDays: Math.floor(Math.random() * 3) + 1,
      },
      vendor: {
        id: `vendor_rec_${i}`,
        name: `Premium Store ${i + 1}`,
        rating: Math.round((Math.random() * 1 + 4) * 10) / 10,
        verified: true,
      },
      badges: ['Recommended'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      recommendationScore: Math.random(),
      recommendationReason: ['Similar to your views', 'Popular in your area', 'Trending now'][Math.floor(Math.random() * 3)],
    }));
  },
};

// Store creation
const createProductDiscoveryStore: StateCreator<
  ProductDiscoveryStore,
  [
    ['zustand/devtools', never],
    ['zustand/persist', unknown],
    ['zustand/subscribeWithSelector', never],
    ['zustand/immer', never]
  ]
> = (set, get) => ({
  ...initialState,

  // Search actions
  setQuery: (query) => {
    set((state) => {
      state.search.query = query;
    });
  },

  setFilters: (filters) => {
    set((state) => {
      state.search.filters = { ...state.search.filters, ...filters };
    });
  },

  setSortBy: (sortBy) => {
    set((state) => {
      state.search.sortBy = sortBy;
    });
  },

  search: async (query, filters = {}) => {
    const startTime = performance.now();
    const state = get();

    // Generate cache key
    const cacheKey = `${query}_${JSON.stringify({ ...state.search.filters, ...filters })}_${state.search.sortBy}`;

    // Check cache first
    const cached = state.cache.searchResults[cacheKey];
    const now = Date.now();

    if (cached && (now - cached.timestamp) < state.config.cacheTimeout) {
      set((state) => {
        state.search.results = cached.data;
        state.search.totalResults = cached.totalResults;
        state.search.isLoading = false;
        state.search.error = null;
        state.search.currentPage = 1;
        state.performance.cacheHitRate = (state.performance.cacheHitRate * state.performance.totalSearches + 1) / (state.performance.totalSearches + 1);
      });
      return;
    }

    set((state) => {
      state.search.isLoading = true;
      state.search.error = null;
      state.search.query = query;
      state.search.filters = { ...state.search.filters, ...filters };
    });

    try {
      const result = await searchAPI.searchProducts(query, { ...state.search.filters, ...filters });
      const searchTime = performance.now() - startTime;

      set((state) => {
        // Update search state
        state.search.results = result.products;
        state.search.totalResults = result.total;
        state.search.hasNextPage = result.hasNext;
        state.search.isLoading = false;
        state.search.error = null;
        state.search.currentPage = 1;
        state.search.lastSearchTime = now;

        // Cache results
        state.cache.searchResults[cacheKey] = {
          data: result.products,
          timestamp: now,
          totalResults: result.total,
        };

        // Update performance metrics
        state.performance.searchLatency.push(searchTime);
        if (state.performance.searchLatency.length > 100) {
          state.performance.searchLatency = state.performance.searchLatency.slice(-50);
        }

        state.performance.totalSearches += 1;
        state.performance.averageResultsPerSearch = (
          (state.performance.averageResultsPerSearch * (state.performance.totalSearches - 1) + result.total)
          / state.performance.totalSearches
        );

        // Track search
        state.userBehavior.searchHistory.push({
          query,
          timestamp: now,
          results: result.total,
        });
        if (state.userBehavior.searchHistory.length > 100) {
          state.userBehavior.searchHistory = state.userBehavior.searchHistory.slice(-50);
        }
      });

    } catch (error) {
      set((state) => {
        state.search.isLoading = false;
        state.search.error = error instanceof Error ? error.message : 'Error de búsqueda';
      });
    }
  },

  loadMore: async () => {
    const state = get();
    if (!state.search.hasNextPage || state.search.isLoading) return;

    set((state) => {
      state.search.isLoading = true;
    });

    try {
      const result = await searchAPI.searchProducts(
        state.search.query,
        state.search.filters,
        state.search.currentPage + 1
      );

      set((state) => {
        state.search.results = [...state.search.results, ...result.products];
        state.search.hasNextPage = result.hasNext;
        state.search.currentPage += 1;
        state.search.isLoading = false;
      });

    } catch (error) {
      set((state) => {
        state.search.isLoading = false;
        state.search.error = error instanceof Error ? error.message : 'Error cargando más resultados';
      });
    }
  },

  clearSearch: () => {
    set((state) => {
      state.search.query = '';
      state.search.results = [];
      state.search.totalResults = 0;
      state.search.currentPage = 1;
      state.search.hasNextPage = false;
      state.search.error = null;
    });
  },

  // Recommendation actions
  loadRecommendations: async (type, params = {}) => {
    const cacheKey = `${type}_${JSON.stringify(params)}`;
    const state = get();
    const cached = state.cache.recommendations[cacheKey];
    const now = Date.now();

    if (cached && (now - cached.timestamp) < state.config.cacheTimeout) {
      set((state) => {
        (state.recommendations as any)[type] = cached.data;
      });
      return;
    }

    set((state) => {
      state.recommendations.isLoading = true;
      state.recommendations.error = null;
    });

    try {
      const recommendations = await searchAPI.getRecommendations(type, params);

      set((state) => {
        (state.recommendations as any)[type] = recommendations;
        state.recommendations.isLoading = false;
        state.recommendations.error = null;
        state.recommendations.lastUpdated = now;

        // Cache recommendations
        state.cache.recommendations[cacheKey] = {
          data: recommendations,
          timestamp: now,
        };
      });

    } catch (error) {
      set((state) => {
        state.recommendations.isLoading = false;
        state.recommendations.error = error instanceof Error ? error.message : 'Error cargando recomendaciones';
      });
    }
  },

  refreshRecommendations: async () => {
    const state = get();

    // Clear recommendation cache
    set((state) => {
      state.cache.recommendations = {};
    });

    // Reload all recommendation types
    await Promise.allSettled([
      get().loadRecommendations('trending'),
      get().loadRecommendations('personalized'),
      get().loadRecommendations('similar'),
    ]);
  },

  // Cache actions
  getCachedResults: (key) => {
    const state = get();
    const cached = state.cache.searchResults[key] || state.cache.recommendations[key] || state.cache.suggestions[key];
    const now = Date.now();

    if (cached && (now - cached.timestamp) < state.config.cacheTimeout) {
      return cached.data;
    }

    return null;
  },

  setCachedResults: (key, data) => {
    set((state) => {
      if (key.includes('search')) {
        state.cache.searchResults[key] = {
          data,
          timestamp: Date.now(),
          totalResults: Array.isArray(data) ? data.length : 0,
        };
      } else if (key.includes('rec')) {
        state.cache.recommendations[key] = {
          data,
          timestamp: Date.now(),
        };
      } else {
        state.cache.suggestions[key] = {
          data,
          timestamp: Date.now(),
        };
      }
    });
  },

  clearCache: (type) => {
    set((state) => {
      if (!type) {
        state.cache = { searchResults: {}, recommendations: {}, suggestions: {} };
      } else if (type === 'search') {
        state.cache.searchResults = {};
      } else if (type === 'recommendations') {
        state.cache.recommendations = {};
      } else if (type === 'suggestions') {
        state.cache.suggestions = {};
      }
    });
  },

  // User behavior actions
  trackSearch: (query, results) => {
    set((state) => {
      state.userBehavior.searchHistory.push({
        query,
        timestamp: Date.now(),
        results,
      });
      if (state.userBehavior.searchHistory.length > 100) {
        state.userBehavior.searchHistory = state.userBehavior.searchHistory.slice(-50);
      }
    });
  },

  trackProductView: (productId, context) => {
    set((state) => {
      state.userBehavior.viewedProducts.add(productId);
    });
  },

  trackProductClick: (productId, context) => {
    set((state) => {
      state.userBehavior.clickedProducts.push({
        productId,
        timestamp: Date.now(),
        source: context.source || 'unknown',
        position: context.position || 0,
      });
      if (state.userBehavior.clickedProducts.length > 200) {
        state.userBehavior.clickedProducts = state.userBehavior.clickedProducts.slice(-100);
      }
    });
  },

  updatePreferences: (preferences) => {
    set((state) => {
      state.userBehavior.preferences = { ...state.userBehavior.preferences, ...preferences };
    });
  },

  // Performance actions
  trackPerformance: (metric, value) => {
    set((state) => {
      if (metric === 'searchLatency') {
        state.performance.searchLatency.push(value);
        if (state.performance.searchLatency.length > 100) {
          state.performance.searchLatency = state.performance.searchLatency.slice(-50);
        }
      } else if (metric === 'renderTime') {
        state.performance.renderTime.push(value);
        if (state.performance.renderTime.length > 100) {
          state.performance.renderTime = state.performance.renderTime.slice(-50);
        }
      }
    });
  },

  getPerformanceReport: () => {
    const state = get();
    return state.performance;
  },

  // Utility actions
  reset: () => {
    set(() => ({ ...initialState }));
  },

  optimize: () => {
    set((state) => {
      // Clean old cache entries
      const now = Date.now();
      const timeout = state.config.cacheTimeout;

      Object.keys(state.cache.searchResults).forEach(key => {
        if (now - state.cache.searchResults[key].timestamp > timeout) {
          delete state.cache.searchResults[key];
        }
      });

      Object.keys(state.cache.recommendations).forEach(key => {
        if (now - state.cache.recommendations[key].timestamp > timeout) {
          delete state.cache.recommendations[key];
        }
      });

      Object.keys(state.cache.suggestions).forEach(key => {
        if (now - state.cache.suggestions[key].timestamp > timeout) {
          delete state.cache.suggestions[key];
        }
      });

      // Trim performance arrays
      if (state.performance.searchLatency.length > 50) {
        state.performance.searchLatency = state.performance.searchLatency.slice(-25);
      }
      if (state.performance.renderTime.length > 50) {
        state.performance.renderTime = state.performance.renderTime.slice(-25);
      }
    });
  },
});

// Create the store
export const useProductDiscoveryStore = create<ProductDiscoveryStore>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer(createProductDiscoveryStore)
      ),
      {
        name: 'product-discovery-store',
        partialize: (state) => ({
          userBehavior: {
            preferences: state.userBehavior.preferences,
            searchHistory: state.userBehavior.searchHistory.slice(-20),
          },
          config: state.config,
        }),
      }
    ),
    {
      name: 'product-discovery',
    }
  )
);

// Selectors for optimized access
export const useSearchState = () => useProductDiscoveryStore((state) => state.search);
export const useRecommendations = () => useProductDiscoveryStore((state) => state.recommendations);
export const usePerformanceMetrics = () => useProductDiscoveryStore((state) => state.performance);
export const useUserBehavior = () => useProductDiscoveryStore((state) => state.userBehavior);

// Debounced search action
let searchTimeout: NodeJS.Timeout;
export const debouncedSearch = (query: string, delay: number = 300) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    useProductDiscoveryStore.getState().search(query);
  }, delay);
};