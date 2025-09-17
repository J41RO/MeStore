// ~/src/hooks/search/useSearchAnalytics.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Search Analytics Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useSearchAnalytics.ts
// Ruta: ~/src/hooks/search/useSearchAnalytics.ts
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Hook para tracking y analytics de búsqueda (opcional)
//
// ---------------------------------------------------------------------------------------------

import { useCallback, useRef, useEffect } from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { searchService } from '../../services/searchService';
import { SearchAnalytics } from '../../types/search.types';

interface UseSearchAnalyticsReturn {
  // Tracking methods
  trackSearch: (query: string, resultCount: number) => void;
  trackClick: (productId: string, position: number) => void;
  trackFilterUsage: (filterKey: string, filterValue: any) => void;
  trackNoResults: (query: string) => void;

  // Session tracking
  startSession: () => void;
  endSession: () => void;

  // Performance tracking
  trackPerformance: (operation: string, duration: number) => void;

  // Conversion tracking
  trackConversion: (productId: string, query: string) => void;
}

/**
 * Hook para analytics y tracking de búsqueda
 */
export const useSearchAnalytics = (): UseSearchAnalyticsReturn => {
  const store = useSearchStore();
  const sessionRef = useRef<string | null>(null);
  const clickedResultsRef = useRef<string[]>([]);
  const searchStartTimeRef = useRef<number | null>(null);

  /**
   * Generar ID de sesión único
   */
  const generateSessionId = useCallback((): string => {
    return `search_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  /**
   * Obtener tipo de usuario desde el store de auth
   */
  const getUserType = useCallback((): string => {
    // Obtener del localStorage o store de autenticación
    const userRole = localStorage.getItem('user_role') || 'buyer';
    return userRole as 'buyer' | 'vendor' | 'admin';
  }, []);

  /**
   * Iniciar sesión de búsqueda
   */
  const startSession = useCallback(() => {
    sessionRef.current = generateSessionId();
    clickedResultsRef.current = [];
    searchStartTimeRef.current = Date.now();
  }, [generateSessionId]);

  /**
   * Finalizar sesión de búsqueda
   */
  const endSession = useCallback(() => {
    sessionRef.current = null;
    clickedResultsRef.current = [];
    searchStartTimeRef.current = null;
  }, []);

  /**
   * Trackear búsqueda
   */
  const trackSearch = useCallback(async (query: string, resultCount: number) => {
    if (!sessionRef.current) {
      startSession();
    }

    const responseTime = searchStartTimeRef.current
      ? Date.now() - searchStartTimeRef.current
      : 0;

    const analytics: SearchAnalytics = {
      query,
      timestamp: new Date(),
      resultCount,
      clickedResults: [...clickedResultsRef.current],
      filters: store.filters,
      userType: getUserType(),
      sessionId: sessionRef.current!,
      responseTime,
    };

    try {
      await searchService.trackSearch({
        query: analytics.query,
        resultCount: analytics.resultCount,
        clickedResults: analytics.clickedResults,
        userType: analytics.userType,
      });
    } catch (error) {
      console.warn('Analytics tracking failed:', error);
    }

    // Reset para próxima búsqueda
    clickedResultsRef.current = [];
    searchStartTimeRef.current = Date.now();
  }, [store.filters, getUserType, startSession]);

  /**
   * Trackear click en resultado
   */
  const trackClick = useCallback((productId: string, position: number) => {
    // Agregar a resultados clickeados
    if (!clickedResultsRef.current.includes(productId)) {
      clickedResultsRef.current.push(productId);
    }

    // Analytics adicionales para clicks
    const clickEvent = {
      type: 'result_click',
      productId,
      position,
      query: store.query,
      timestamp: new Date(),
      sessionId: sessionRef.current,
    };

    // Enviar event analytics (opcional)
    if (window.gtag) {
      window.gtag('event', 'search_result_click', {
        search_term: store.query,
        item_id: productId,
        position: position,
      });
    }

    console.log('Search click tracked:', clickEvent);
  }, [store.query]);

  /**
   * Trackear uso de filtros
   */
  const trackFilterUsage = useCallback((filterKey: string, filterValue: any) => {
    const filterEvent = {
      type: 'filter_usage',
      filterKey,
      filterValue,
      query: store.query,
      timestamp: new Date(),
      sessionId: sessionRef.current,
    };

    // Analytics para filtros
    if (window.gtag) {
      window.gtag('event', 'search_filter_used', {
        search_term: store.query,
        filter_type: filterKey,
        filter_value: Array.isArray(filterValue) ? filterValue.join(',') : filterValue,
      });
    }

    console.log('Filter usage tracked:', filterEvent);
  }, [store.query]);

  /**
   * Trackear búsquedas sin resultados
   */
  const trackNoResults = useCallback(async (query: string) => {
    try {
      await searchService.reportNoResults(query, store.filters);

      // Analytics para no results
      if (window.gtag) {
        window.gtag('event', 'search_no_results', {
          search_term: query,
        });
      }
    } catch (error) {
      console.warn('No results tracking failed:', error);
    }
  }, [store.filters]);

  /**
   * Trackear performance
   */
  const trackPerformance = useCallback((operation: string, duration: number) => {
    const performanceEvent = {
      type: 'performance',
      operation,
      duration,
      timestamp: new Date(),
      sessionId: sessionRef.current,
    };

    // Web Vitals / Performance analytics
    if (window.gtag) {
      window.gtag('event', 'timing_complete', {
        name: operation,
        value: duration,
      });
    }

    console.log('Performance tracked:', performanceEvent);
  }, []);

  /**
   * Trackear conversiones
   */
  const trackConversion = useCallback((productId: string, query: string) => {
    const conversionEvent = {
      type: 'conversion',
      productId,
      query,
      timestamp: new Date(),
      sessionId: sessionRef.current,
    };

    // E-commerce analytics
    if (window.gtag) {
      window.gtag('event', 'search_conversion', {
        search_term: query,
        item_id: productId,
      });
    }

    console.log('Conversion tracked:', conversionEvent);
  }, []);

  /**
   * Auto-iniciar sesión si no existe
   */
  useEffect(() => {
    if (!sessionRef.current) {
      startSession();
    }

    // Cleanup al desmontar
    return () => {
      endSession();
    };
  }, [startSession, endSession]);

  /**
   * Trackear automáticamente cuando cambian los resultados
   */
  useEffect(() => {
    if (store.results && store.query) {
      trackSearch(store.query, store.results.totalFound);
    }
  }, [store.results, store.query, trackSearch]);

  /**
   * Trackear automáticamente búsquedas sin resultados
   */
  useEffect(() => {
    if (store.results && store.results.totalFound === 0 && store.query) {
      trackNoResults(store.query);
    }
  }, [store.results, store.query, trackNoResults]);

  return {
    // Tracking methods
    trackSearch,
    trackClick,
    trackFilterUsage,
    trackNoResults,

    // Session tracking
    startSession,
    endSession,

    // Performance tracking
    trackPerformance,

    // Conversion tracking
    trackConversion,
  };
};