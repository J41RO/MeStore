// ~/src/hooks/useProductDiscovery.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Product Discovery Hook with Performance Optimization
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useProductDiscovery.ts
// Ruta: ~/src/hooks/useProductDiscovery.ts
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Hook optimizado para descubrimiento de productos
//
// Performance Features:
// - Memoized computations
// - Debounced search operations
// - Intelligent caching
// - Background data fetching
// - Performance monitoring
// ---------------------------------------------------------------------------------------------

import { useCallback, useMemo, useEffect, useRef } from 'react';
import { useProductDiscoveryStore, useSearchState, useRecommendations, useUserBehavior } from '../stores/productDiscoveryStore';

export const useProductDiscovery = () => {
  const store = useProductDiscoveryStore();
  const searchState = useSearchState();
  const recommendations = useRecommendations();
  const userBehavior = useUserBehavior();

  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const performanceStartRef = useRef<number>(0);

  // Memoized search results with performance tracking
  const searchResults = useMemo(() => {
    return searchState.results.map((product, index) => ({
      ...product,
      position: index,
    }));
  }, [searchState.results]);

  // Memoized trending products
  const trendingProducts = useMemo(() => {
    return recommendations.trending.slice(0, 12);
  }, [recommendations.trending]);

  // Memoized popular searches from user behavior
  const popularSearches = useMemo(() => {
    const searchCounts = userBehavior.searchHistory.reduce((acc, search) => {
      acc[search.query] = (acc[search.query] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(searchCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([query]) => query);
  }, [userBehavior.searchHistory]);

  // Optimized search function with debouncing and performance tracking
  const searchProducts = useCallback(async (
    query: string,
    options: {
      filters?: any;
      debounce?: number;
      cache?: boolean;
      limit?: number;
    } = {}
  ) => {
    const { filters, debounce = 300, cache = true, limit = 20 } = options;

    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Start performance tracking
    performanceStartRef.current = performance.now();

    return new Promise((resolve) => {
      searchTimeoutRef.current = setTimeout(async () => {
        try {
          await store.search(query, filters);

          // Track performance
          const searchTime = performance.now() - performanceStartRef.current;
          store.trackPerformance('searchLatency', searchTime);

          resolve(store.search.results);
        } catch (error) {
          console.error('Search error:', error);
          resolve([]);
        }
      }, debounce);
    });
  }, [store]);

  // Get recommendations with caching
  const getRecommendations = useCallback(async (
    type: string,
    params: any = {}
  ) => {
    const startTime = performance.now();

    try {
      await store.loadRecommendations(type, params);

      // Track performance
      const loadTime = performance.now() - startTime;
      store.trackPerformance('renderTime', loadTime);

      return recommendations[type as keyof typeof recommendations] || [];
    } catch (error) {
      console.error('Recommendations error:', error);
      return [];
    }
  }, [store, recommendations]);

  // Optimize search query for better performance
  const optimizeSearchQuery = useCallback((query: string): string => {
    // Remove extra spaces and normalize
    let optimized = query.trim().toLowerCase();

    // Remove special characters that might slow down search
    optimized = optimized.replace(/[^\w\s\u00C0-\u017F]/g, '');

    // Limit query length for performance
    if (optimized.length > 100) {
      optimized = optimized.substring(0, 100);
    }

    return optimized;
  }, []);

  // Track search behavior for analytics
  const trackSearchBehavior = useCallback((data: {
    query?: string;
    results?: number;
    responseTime?: number;
    cached?: boolean;
    action?: string;
    productId?: string;
    position?: number;
  }) => {
    if (data.query && typeof data.results === 'number') {
      store.trackSearch(data.query, data.results);
    }

    if (data.productId && data.action === 'product_click') {
      store.trackProductClick(data.productId, {
        source: 'search',
        position: data.position || 0,
        query: searchState.query,
      });
    }
  }, [store, searchState.query]);

  // Load more results with pagination
  const loadMoreResults = useCallback(async () => {
    if (searchState.hasNextPage && !searchState.isLoading) {
      const startTime = performance.now();
      await store.loadMore();
      const loadTime = performance.now() - startTime;
      store.trackPerformance('renderTime', loadTime);
    }
  }, [store, searchState.hasNextPage, searchState.isLoading]);

  // Clear search with cleanup
  const clearSearch = useCallback(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    store.clearSearch();
  }, [store]);

  // Refresh recommendations
  const refreshRecommendations = useCallback(async () => {
    const startTime = performance.now();
    await store.refreshRecommendations();
    const loadTime = performance.now() - startTime;
    store.trackPerformance('renderTime', loadTime);
  }, [store]);

  // Get search suggestions (mock implementation)
  const getSearchSuggestions = useCallback(async (query: string) => {
    if (query.length < 2) return [];

    // Check cache first
    const cacheKey = `suggestions_${query}`;
    const cached = store.getCachedResults(cacheKey);
    if (cached) return cached;

    // Simulate API call for suggestions
    const suggestions = [
      { id: 1, text: `${query} smartphone`, type: 'suggestion' },
      { id: 2, text: `${query} laptop`, type: 'suggestion' },
      { id: 3, text: `${query} tablet`, type: 'suggestion' },
    ].filter(() => Math.random() > 0.3);

    // Cache suggestions
    store.setCachedResults(cacheKey, suggestions);

    return suggestions;
  }, [store]);

  // Performance optimization - cleanup old data
  useEffect(() => {
    const interval = setInterval(() => {
      store.optimize();
    }, 5 * 60 * 1000); // Every 5 minutes

    return () => clearInterval(interval);
  }, [store]);

  // Pagination info
  const pagination = useMemo(() => ({
    currentPage: searchState.currentPage,
    hasNextPage: searchState.hasNextPage,
    totalResults: searchState.totalResults,
    resultsPerPage: store.config.resultsPerPage,
    totalPages: Math.ceil(searchState.totalResults / store.config.resultsPerPage),
  }), [searchState, store.config.resultsPerPage]);

  return {
    // Search state
    products: searchResults,
    searchResults,
    isLoading: searchState.isLoading,
    error: searchState.error,
    query: searchState.query,
    filters: searchState.filters,
    totalResults: searchState.totalResults,
    pagination,

    // Recommendations
    recommendations: {
      trending: trendingProducts,
      personalized: recommendations.personalized,
      similar: recommendations.similar,
      recentlyViewed: recommendations.recentlyViewed,
    },

    // User behavior
    searchHistory: userBehavior.searchHistory,
    popularSearches,

    // Actions
    searchProducts,
    getRecommendations,
    getSearchSuggestions,
    optimizeSearchQuery,
    trackSearchBehavior,
    loadMoreResults,
    clearSearch,
    refreshRecommendations,

    // Utils
    setQuery: store.setQuery,
    setFilters: store.setFilters,
    setSortBy: store.setSortBy,
    updatePreferences: store.updatePreferences,
  };
};