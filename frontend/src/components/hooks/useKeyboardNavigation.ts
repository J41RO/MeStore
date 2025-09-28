/**
 * useKeyboardNavigation Hook
 * WCAG 2.1 AA Compliant Keyboard Navigation for Hierarchical Sidebar
 *
 * Implements:
 * - Arrow key navigation within categories
 * - Tab/Shift+Tab for category headers
 * - Enter/Space for activation
 * - Escape for closing/navigation
 * - Home/End for first/last navigation
 */

import { useCallback, useRef, useState, useEffect } from 'react';

export interface KeyboardNavigationOptions {
  containerRef: React.RefObject<HTMLElement>;
  onEscape?: () => void;
  announceChanges?: (message: string) => void;
}

export interface KeyboardNavigationReturn {
  currentFocus: number;
  handleKeyDown: (event: React.KeyboardEvent) => void;
  setFocusToFirst: () => void;
  setFocusToLast: () => void;
}

export const useKeyboardNavigation = ({
  containerRef,
  onEscape,
  announceChanges
}: KeyboardNavigationOptions): KeyboardNavigationReturn => {
  const [currentFocus, setCurrentFocus] = useState(-1);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Obtener todos los elementos focusables dentro del contenedor
  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!containerRef.current) return [];

    const focusableSelectors = [
      'button:not([disabled])',
      'a[href]:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"]):not([disabled])',
      '[role="button"]:not([disabled])',
      '[role="menuitem"]:not([disabled])'
    ].join(', ');

    const elements = Array.from(
      containerRef.current.querySelectorAll(focusableSelectors)
    ) as HTMLElement[];

    // Filtrar elementos que están realmente visibles
    return elements.filter(element => {
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);

      return (
        rect.width > 0 &&
        rect.height > 0 &&
        style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        !element.hasAttribute('aria-hidden')
      );
    });
  }, [containerRef]);

  // Enfocar elemento por índice
  const focusElementByIndex = useCallback((index: number) => {
    const focusableElements = getFocusableElements();
    if (focusableElements.length === 0) return;

    const validIndex = Math.max(0, Math.min(index, focusableElements.length - 1));
    const element = focusableElements[validIndex];

    if (element) {
      element.focus();
      setCurrentFocus(validIndex);

      // Anunciar cambio de foco para screen readers
      if (announceChanges) {
        const categoryHeader = element.closest('[role="button"]');
        const menuItem = element.closest('[role="menuitem"]');

        if (categoryHeader && categoryHeader.textContent) {
          announceChanges(`Categoría: ${categoryHeader.textContent.trim()}`);
        } else if (menuItem && menuItem.textContent) {
          announceChanges(`Elemento de menú: ${menuItem.textContent.trim()}`);
        }
      }
    }
  }, [getFocusableElements, announceChanges]);

  // Navegar a la siguiente categoría
  const navigateToNextCategory = useCallback(() => {
    const focusableElements = getFocusableElements();
    const currentElement = focusableElements[currentFocus];

    if (!currentElement) return;

    // Encontrar la siguiente categoría
    const categories = focusableElements.filter(el =>
      el.getAttribute('role') === 'button' && el.hasAttribute('aria-expanded')
    );

    const currentCategoryIndex = categories.findIndex(cat => cat === currentElement);
    if (currentCategoryIndex >= 0 && currentCategoryIndex < categories.length - 1) {
      const nextCategory = categories[currentCategoryIndex + 1];
      const nextIndex = focusableElements.indexOf(nextCategory);
      focusElementByIndex(nextIndex);
    }
  }, [currentFocus, focusElementByIndex, getFocusableElements]);

  // Navegar a la categoría anterior
  const navigateToPreviousCategory = useCallback(() => {
    const focusableElements = getFocusableElements();
    const currentElement = focusableElements[currentFocus];

    if (!currentElement) return;

    const categories = focusableElements.filter(el =>
      el.getAttribute('role') === 'button' && el.hasAttribute('aria-expanded')
    );

    const currentCategoryIndex = categories.findIndex(cat => cat === currentElement);
    if (currentCategoryIndex > 0) {
      const prevCategory = categories[currentCategoryIndex - 1];
      const prevIndex = focusableElements.indexOf(prevCategory);
      focusElementByIndex(prevIndex);
    }
  }, [currentFocus, focusElementByIndex, getFocusableElements]);

  // Navegar dentro de una categoría expandida
  const navigateWithinCategory = useCallback((direction: 'up' | 'down') => {
    const focusableElements = getFocusableElements();
    const currentElement = focusableElements[currentFocus];

    if (!currentElement) return;

    // Encontrar el contenedor de la categoría actual
    const categoryContainer = currentElement.closest('[data-testid="menu-category-container"]');
    if (!categoryContainer) return;

    // Obtener todos los elementos focusables dentro de esta categoría
    const categoryElements = Array.from(
      categoryContainer.querySelectorAll('button:not([disabled]), a[href]:not([disabled])')
    ) as HTMLElement[];

    const currentIndexInCategory = categoryElements.indexOf(currentElement);
    if (currentIndexInCategory === -1) return;

    let nextIndexInCategory;
    if (direction === 'down') {
      nextIndexInCategory = Math.min(currentIndexInCategory + 1, categoryElements.length - 1);
    } else {
      nextIndexInCategory = Math.max(currentIndexInCategory - 1, 0);
    }

    const nextElement = categoryElements[nextIndexInCategory];
    if (nextElement) {
      const globalIndex = focusableElements.indexOf(nextElement);
      focusElementByIndex(globalIndex);
    }
  }, [currentFocus, focusElementByIndex, getFocusableElements]);

  // Manejar eventos de teclado
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    const { key, altKey, ctrlKey, metaKey } = event;

    // Ignorar si hay modificadores (excepto Shift para Shift+Tab)
    if (altKey || ctrlKey || metaKey) return;

    switch (key) {
      case 'ArrowDown':
        event.preventDefault();
        navigateWithinCategory('down');
        break;

      case 'ArrowUp':
        event.preventDefault();
        navigateWithinCategory('up');
        break;

      case 'ArrowRight':
        event.preventDefault();
        navigateToNextCategory();
        break;

      case 'ArrowLeft':
        event.preventDefault();
        navigateToPreviousCategory();
        break;

      case 'Home':
        event.preventDefault();
        focusElementByIndex(0);
        if (announceChanges) {
          announceChanges('Primer elemento del menú');
        }
        break;

      case 'End':
        event.preventDefault();
        const focusableElements = getFocusableElements();
        focusElementByIndex(focusableElements.length - 1);
        if (announceChanges) {
          announceChanges('Último elemento del menú');
        }
        break;

      case 'Escape':
        if (onEscape) {
          event.preventDefault();
          onEscape();
          if (announceChanges) {
            announceChanges('Menú cerrado');
          }
        }
        break;

      case 'Tab':
        // Permitir navegación Tab normal, pero rastrear foco
        const tabFocusableElements = getFocusableElements();
        const currentTabElement = document.activeElement as HTMLElement;
        const currentTabIndex = tabFocusableElements.indexOf(currentTabElement);

        if (currentTabIndex >= 0) {
          setCurrentFocus(currentTabIndex);
        }
        break;

      default:
        // Para otros casos, actualizar el índice de foco actual
        const elements = getFocusableElements();
        const activeElement = document.activeElement as HTMLElement;
        const activeIndex = elements.indexOf(activeElement);

        if (activeIndex >= 0) {
          setCurrentFocus(activeIndex);
        }
        break;
    }
  }, [
    navigateWithinCategory,
    navigateToNextCategory,
    navigateToPreviousCategory,
    focusElementByIndex,
    getFocusableElements,
    onEscape,
    announceChanges
  ]);

  // Enfocar primer elemento
  const setFocusToFirst = useCallback(() => {
    focusElementByIndex(0);
  }, [focusElementByIndex]);

  // Enfocar último elemento
  const setFocusToLast = useCallback(() => {
    const focusableElements = getFocusableElements();
    focusElementByIndex(focusableElements.length - 1);
  }, [focusElementByIndex, getFocusableElements]);

  // Efecto para manejar el foco inicial y la limpieza
  useEffect(() => {
    // Guardar el elemento que tenía foco antes de entrar al componente
    const handleFocusIn = (event: FocusEvent) => {
      if (containerRef.current?.contains(event.target as Node)) {
        const focusableElements = getFocusableElements();
        const targetIndex = focusableElements.indexOf(event.target as HTMLElement);
        if (targetIndex >= 0) {
          setCurrentFocus(targetIndex);
        }
      } else {
        // El foco salió del contenedor
        previousFocusRef.current = event.target as HTMLElement;
      }
    };

    document.addEventListener('focusin', handleFocusIn);

    return () => {
      document.removeEventListener('focusin', handleFocusIn);
    };
  }, [containerRef, getFocusableElements]);

  return {
    currentFocus,
    handleKeyDown,
    setFocusToFirst,
    setFocusToLast
  };
};

export default useKeyboardNavigation;