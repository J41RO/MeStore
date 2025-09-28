import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, useRef } from 'react';

// Tipos para las categorías de sidebar
export type SidebarCategory = 'controlCenter' | 'userManagement' | 'operations' | 'system';

// Estado de collapse por categoría
export interface CollapsedState {
  [key: string]: boolean;
}

// Interfaz del contexto
export interface SidebarContextValue {
  collapsedState: CollapsedState;
  toggleCategory: (category: SidebarCategory) => void;
  isCategoryCollapsed: (category: SidebarCategory) => boolean;
  resetCollapseState: () => void;
  expandAllCategories: () => void;
  collapseAllCategories: () => void;
}

// Crear el contexto
const SidebarContext = createContext<SidebarContextValue | undefined>(undefined);

// Configuración por defecto
const DEFAULT_COLLAPSED_STATE: CollapsedState = {};
const STORAGE_KEY = 'sidebar-collapsed-state';

// Proveedor del contexto con optimizaciones de memoria
export const SidebarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsedState, setCollapsedState] = useState<CollapsedState>(DEFAULT_COLLAPSED_STATE);

  // Referencias para optimización de memoria
  const saveTimeoutRef = useRef<NodeJS.Timeout>();
  const isInitialized = useRef(false);

  // Cargar estado desde localStorage al inicializar (optimizado)
  useEffect(() => {
    if (isInitialized.current) return;

    try {
      const savedState = localStorage.getItem(STORAGE_KEY);
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        // Validar estructura del estado guardado
        if (typeof parsedState === 'object' && parsedState !== null) {
          setCollapsedState(parsedState);
        }
      }
    } catch (error) {
      console.warn('Error loading sidebar state from localStorage:', error);
      setCollapsedState(DEFAULT_COLLAPSED_STATE);
    }

    isInitialized.current = true;
  }, []);

  // Guardar estado en localStorage con debounce para mejor performance
  useEffect(() => {
    if (!isInitialized.current) return;

    // Limpiar timeout anterior
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Debounce para evitar writes frecuentes a localStorage
    saveTimeoutRef.current = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(collapsedState));
      } catch (error) {
        console.warn('Error saving sidebar state to localStorage:', error);
      }
    }, 300); // 300ms debounce

    // Cleanup function
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [collapsedState]);

  // Cleanup al desmontarse
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Toggle de categoría individual
  const toggleCategory = useCallback((category: SidebarCategory) => {
    setCollapsedState(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  }, []);

  // Verificar si una categoría está colapsada
  const isCategoryCollapsed = useCallback((category: SidebarCategory) => {
    return Boolean(collapsedState[category]);
  }, [collapsedState]);

  // Reset a estado por defecto con limpieza de memoria
  const resetCollapseState = useCallback(() => {
    setCollapsedState(DEFAULT_COLLAPSED_STATE);
    // Limpiar localStorage inmediatamente en reset
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_COLLAPSED_STATE));
    } catch (error) {
      console.warn('Error resetting sidebar state in localStorage:', error);
    }
  }, []);

  // Expandir todas las categorías
  const expandAllCategories = useCallback(() => {
    setCollapsedState({});
  }, []);

  // Colapsar todas las categorías (memoizado para performance)
  const collapseAllCategories = useCallback(() => {
    const allCategories: SidebarCategory[] = ['controlCenter', 'userManagement', 'operations', 'system'];
    const allCollapsed = allCategories.reduce((acc, category) => {
      acc[category] = true;
      return acc;
    }, {} as CollapsedState);
    setCollapsedState(allCollapsed);
  }, []);

  // Memoizar el valor del contexto para evitar re-renders innecesarios (optimizado)
  const contextValue = useMemo(() => ({
    collapsedState,
    toggleCategory,
    isCategoryCollapsed,
    resetCollapseState,
    expandAllCategories,
    collapseAllCategories
  }), [
    collapsedState,
    toggleCategory,
    isCategoryCollapsed,
    resetCollapseState,
    expandAllCategories,
    collapseAllCategories
  ]);

  return (
    <SidebarContext.Provider value={contextValue}>
      {children}
    </SidebarContext.Provider>
  );
};

// Hook para usar el contexto
export const useSidebar = (): SidebarContextValue => {
  const context = useContext(SidebarContext);

  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }

  return context;
};