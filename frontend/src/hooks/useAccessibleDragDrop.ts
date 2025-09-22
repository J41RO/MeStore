/**
 * Accessible Drag & Drop Hook - WCAG 2.1 AA Compliant
 * Provides keyboard alternatives and screen reader support for drag & drop operations
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { screenReader, keyboardNavigation } from '../utils/accessibility';

interface AccessibleDragDropConfig<T> {
  items: T[];
  getId: (item: T) => string;
  onReorder: (items: T[]) => void;
  announceMove?: (item: T, fromIndex: number, toIndex: number) => string;
  announceStart?: (item: T) => string;
  announceEnd?: (item: T) => string;
}

interface DragDropState {
  draggedIndex: number | null;
  focusedIndex: number;
  isKeyboardMode: boolean;
  draggedItem: any | null;
}

export const useAccessibleDragDrop = <T>({
  items,
  getId,
  onReorder,
  announceMove = (item: any, from: number, to: number) =>
    `Elemento movido desde posición ${from + 1} a posición ${to + 1}`,
  announceStart = (item: any) =>
    `Iniciando arrastre del elemento ${getId(item)}`,
  announceEnd = (item: any) =>
    `Finalizando arrastre del elemento ${getId(item)}`
}: AccessibleDragDropConfig<T>) => {

  const [state, setState] = useState<DragDropState>({
    draggedIndex: null,
    focusedIndex: 0,
    isKeyboardMode: false,
    draggedItem: null
  });

  const containerRef = useRef<HTMLDivElement>(null);

  // Announce instructions to screen readers
  useEffect(() => {
    const instructions = `
      Lista reordenable con ${items.length} elementos.
      Para mover con teclado: Usa las flechas para navegar, Espacio para seleccionar,
      flechas arriba/abajo para mover, Enter para confirmar, Escape para cancelar.
      También puedes usar arrastrar y soltar con el mouse.
    `;

    if (containerRef.current && items.length > 0) {
      screenReader.announce(instructions, 'polite');
    }
  }, [items.length]);

  // Handle keyboard navigation and actions
  const handleKeyDown = useCallback((event: KeyboardEvent, index: number) => {
    const { key } = event;

    // Navigation keys
    if (key === 'ArrowDown' || key === 'ArrowUp') {
      event.preventDefault();
      const direction = key === 'ArrowDown' ? 1 : -1;

      if (state.draggedIndex !== null) {
        // Moving dragged item
        const newIndex = Math.max(0, Math.min(items.length - 1, state.draggedIndex + direction));
        if (newIndex !== state.draggedIndex) {
          const newItems = [...items];
          const [movedItem] = newItems.splice(state.draggedIndex, 1);
          newItems.splice(newIndex, 0, movedItem);

          onReorder(newItems);
          setState(prev => ({ ...prev, draggedIndex: newIndex }));

          screenReader.announce(
            announceMove(movedItem, state.draggedIndex, newIndex),
            'assertive'
          );
        }
      } else {
        // Normal navigation
        const newIndex = Math.max(0, Math.min(items.length - 1, index + direction));
        setState(prev => ({ ...prev, focusedIndex: newIndex }));

        // Focus the new item
        const newElement = containerRef.current?.querySelector(
          `[data-index="${newIndex}"]`
        ) as HTMLElement;
        newElement?.focus();
      }
    }

    // Action keys
    else if (key === ' ' || key === 'Enter') {
      event.preventDefault();

      if (state.draggedIndex === null) {
        // Start dragging
        setState(prev => ({
          ...prev,
          draggedIndex: index,
          isKeyboardMode: true,
          draggedItem: items[index]
        }));

        screenReader.announce(
          `${announceStart(items[index])}. Usa las flechas arriba y abajo para mover, Enter para confirmar, Escape para cancelar.`,
          'assertive'
        );
      } else if (key === 'Enter') {
        // Confirm drop
        setState(prev => ({
          ...prev,
          draggedIndex: null,
          isKeyboardMode: false,
          draggedItem: null
        }));

        screenReader.announce(
          announceEnd(items[state.draggedIndex]),
          'assertive'
        );
      }
    }

    // Cancel dragging
    else if (key === 'Escape' && state.draggedIndex !== null) {
      event.preventDefault();
      setState(prev => ({
        ...prev,
        draggedIndex: null,
        isKeyboardMode: false,
        draggedItem: null
      }));

      screenReader.announce('Arrastre cancelado', 'assertive');
    }
  }, [items, state.draggedIndex, onReorder, announceMove, announceStart, announceEnd]);

  // Mouse/touch drag handlers
  const handleDragStart = useCallback((index: number) => {
    setState(prev => ({
      ...prev,
      draggedIndex: index,
      isKeyboardMode: false,
      draggedItem: items[index]
    }));

    screenReader.announce(announceStart(items[index]), 'polite');
  }, [items, announceStart]);

  const handleDragEnd = useCallback(() => {
    if (state.draggedItem) {
      screenReader.announce(announceEnd(state.draggedItem), 'polite');
    }

    setState(prev => ({
      ...prev,
      draggedIndex: null,
      isKeyboardMode: false,
      draggedItem: null
    }));
  }, [state.draggedItem, announceEnd]);

  const handleDrop = useCallback((fromIndex: number, toIndex: number) => {
    const newItems = [...items];
    const [movedItem] = newItems.splice(fromIndex, 1);
    newItems.splice(toIndex, 0, movedItem);

    onReorder(newItems);

    screenReader.announce(
      announceMove(movedItem, fromIndex, toIndex),
      'assertive'
    );
  }, [items, onReorder, announceMove]);

  // Get item props for accessibility
  const getItemProps = useCallback((item: T, index: number) => {
    const isDragged = state.draggedIndex === index;
    const isFocused = state.focusedIndex === index;

    return {
      'data-index': index,
      'data-dragged': isDragged,
      tabIndex: isFocused ? 0 : -1,
      role: 'option',
      'aria-grabbed': isDragged,
      'aria-describedby': `item-${getId(item)}-instructions`,
      'aria-label': `Elemento ${index + 1} de ${items.length}: ${getId(item)}`,
      onKeyDown: (event: React.KeyboardEvent) => handleKeyDown(event.nativeEvent, index),
      style: {
        transform: isDragged && state.isKeyboardMode ? 'scale(1.05)' : undefined,
        opacity: isDragged ? 0.8 : 1,
        outline: isFocused ? '2px solid #3b82f6' : undefined,
        outlineOffset: '2px'
      }
    };
  }, [state, items, getId, handleKeyDown]);

  // Get container props
  const getContainerProps = useCallback(() => ({
    ref: containerRef,
    role: 'listbox',
    'aria-label': `Lista reordenable con ${items.length} elementos`,
    'aria-multiselectable': false,
    'aria-describedby': 'drag-drop-instructions',
    tabIndex: -1
  }), [items.length]);

  // Instructions component
  const Instructions = useCallback(() => {
    return React.createElement('div', {
      id: 'drag-drop-instructions',
      className: 'sr-only'
    }, [
      'Lista reordenable. Usa las teclas de flecha para navegar entre elementos. ',
      'Presiona Espacio para comenzar a arrastrar un elemento. ',
      'Mientras arrastras, usa flecha arriba y abajo para mover el elemento. ',
      'Presiona Enter para confirmar la nueva posición o Escape para cancelar. ',
      'También puedes usar arrastrar y soltar con el mouse o touch.'
    ].join(''));
  }, []);

  return {
    state,
    containerProps: getContainerProps(),
    getItemProps,
    handleDragStart,
    handleDragEnd,
    handleDrop,
    Instructions,
    // Helper to announce current state
    announceState: useCallback(() => {
      if (state.draggedIndex !== null) {
        const item = items[state.draggedIndex];
        screenReader.announce(
          `Arrastrando ${getId(item)} en posición ${state.draggedIndex + 1} de ${items.length}`,
          'polite'
        );
      }
    }, [state.draggedIndex, items, getId])
  };
};