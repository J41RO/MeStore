// ~/src/components/search/SearchBar.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - SearchBar Component with Autocomplete
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SearchBar.tsx
// Ruta: ~/src/components/search/SearchBar.tsx
// Autor: React Specialist AI
// Fecha de Creación: 2025-09-17
// Última Actualización: 2025-09-17
// Versión: 1.0.0
// Propósito: Componente principal de barra de búsqueda con autocomplete
//
// ---------------------------------------------------------------------------------------------

import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import {
  Search,
  Mic,
  X,
  Settings,
  Clock,
  TrendingUp,
  ChevronRight,
} from 'lucide-react';
import { useSearch, useSearchSuggestions, useSearchHistory } from '../../hooks/search';
import { SearchBarProps } from '../../types/search.types';
import { searchUtils } from '../../services/searchService';

interface SearchBarState {
  inputValue: string;
  isFocused: boolean;
  showSuggestions: boolean;
  isRecording: boolean;
}

/**
 * Componente principal de barra de búsqueda
 */
const SearchBar: React.FC<SearchBarProps> = memo(({
  className = '',
  onSearchChange,
  onFilterChange,
  onResultClick,
  placeholder = 'Buscar productos...',
  autoFocus = false,
  showVoiceSearch = false,
  showAdvancedLink = true,
  enableAutocomplete = true,
  size = 'md',
}) => {
  // Hooks
  const {
    query,
    quickSearch,
    clearSearch,
    config,
    isSearching,
  } = useSearch();

  const {
    suggestions,
    recentSearches,
    popularSearches,
    isLoading: suggestionsLoading,
    hasResults: hasSuggestions,
    getSuggestions,
    clearSuggestions,
    selectSuggestion,
    highlightedIndex,
    handleKeyboardNavigation,
    setHighlightedIndex,
    formatSuggestion,
    getSuggestionIcon,
  } = useSearchSuggestions();

  const {
    getRecentTerms,
    getPopularTerms,
  } = useSearchHistory();

  // Estado local
  const [state, setState] = useState<SearchBarState>({
    inputValue: query,
    isFocused: false,
    showSuggestions: false,
    isRecording: false,
  });

  // Referencias
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  /**
   * Manejar cambios en el input
   */
  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;

    setState(prev => ({ ...prev, inputValue: value }));

    // Callback externo
    onSearchChange?.(value);

    // Obtener sugerencias si está habilitado
    if (enableAutocomplete) {
      getSuggestions(value);
    }
  }, [onSearchChange, enableAutocomplete, getSuggestions]);

  /**
   * Manejar envío del formulario
   */
  const handleSubmit = useCallback((event: React.FormEvent) => {
    event.preventDefault();

    const validation = searchUtils.validateQuery(state.inputValue);
    if (!validation.isValid) {
      alert(validation.message);
      return;
    }

    quickSearch(state.inputValue);
    setState(prev => ({ ...prev, showSuggestions: false }));
    inputRef.current?.blur();
  }, [state.inputValue, quickSearch]);

  /**
   * Manejar focus del input
   */
  const handleFocus = useCallback(() => {
    setState(prev => ({
      ...prev,
      isFocused: true,
      showSuggestions: enableAutocomplete && (hasSuggestions || state.inputValue.length >= config.minQueryLength),
    }));
  }, [enableAutocomplete, hasSuggestions, state.inputValue.length, config.minQueryLength]);

  /**
   * Manejar blur del input
   */
  const handleBlur = useCallback((event: React.FocusEvent) => {
    // Delay para permitir clicks en sugerencias
    setTimeout(() => {
      if (!containerRef.current?.contains(document.activeElement)) {
        setState(prev => ({
          ...prev,
          isFocused: false,
          showSuggestions: false,
        }));
        setHighlightedIndex(-1);
      }
    }, 200);
  }, [setHighlightedIndex]);

  /**
   * Manejar navegación con teclado
   */
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (state.showSuggestions) {
      handleKeyboardNavigation(event.nativeEvent);
    }

    if (event.key === 'Escape') {
      setState(prev => ({ ...prev, showSuggestions: false }));
      inputRef.current?.blur();
    }
  }, [state.showSuggestions, handleKeyboardNavigation]);

  /**
   * Limpiar búsqueda
   */
  const handleClear = useCallback(() => {
    setState(prev => ({ ...prev, inputValue: '' }));
    clearSearch();
    clearSuggestions();
    inputRef.current?.focus();
  }, [clearSearch, clearSuggestions]);

  /**
   * Seleccionar sugerencia
   */
  const handleSuggestionClick = useCallback((suggestion: any) => {
    selectSuggestion(suggestion);
    setState(prev => ({
      ...prev,
      inputValue: suggestion.text,
      showSuggestions: false,
    }));
  }, [selectSuggestion]);

  /**
   * Búsqueda por voz (placeholder)
   */
  const handleVoiceSearch = useCallback(() => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Búsqueda por voz no disponible en este navegador');
      return;
    }

    setState(prev => ({ ...prev, isRecording: true }));

    // Implementar Web Speech API
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setState(prev => ({
        ...prev,
        inputValue: transcript,
        isRecording: false,
      }));
      quickSearch(transcript);
    };

    recognition.onerror = () => {
      setState(prev => ({ ...prev, isRecording: false }));
    };

    recognition.onend = () => {
      setState(prev => ({ ...prev, isRecording: false }));
    };

    recognition.start();
  }, [quickSearch]);

  /**
   * Sincronizar input con query del store
   */
  useEffect(() => {
    if (query !== state.inputValue && !state.isFocused) {
      setState(prev => ({ ...prev, inputValue: query }));
    }
  }, [query, state.inputValue, state.isFocused]);

  /**
   * Auto focus si está habilitado
   */
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  /**
   * Clases CSS basadas en el tamaño
   */
  const sizeClasses = {
    sm: 'h-8 text-sm',
    md: 'h-10 text-base',
    lg: 'h-12 text-lg',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  /**
   * Renderizar sugerencias
   */
  const renderSuggestions = () => {
    if (!state.showSuggestions || (!hasSuggestions && !suggestionsLoading)) {
      return null;
    }

    const allSuggestions = [
      ...suggestions.map(s => ({ ...s, category: 'suggestions' })),
      ...recentSearches.slice(0, 3).map(s => ({ ...s, category: 'recent' })),
      ...popularSearches.slice(0, 3).map(s => ({ ...s, category: 'popular' })),
    ];

    return (
      <div
        ref={suggestionsRef}
        className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-b-lg shadow-lg max-h-80 overflow-y-auto z-50"
      >
        {suggestionsLoading && (
          <div className="p-3 text-center text-gray-500">
            <div className="animate-spin inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="ml-2">Buscando...</span>
          </div>
        )}

        {!suggestionsLoading && allSuggestions.length === 0 && state.inputValue.length >= config.minQueryLength && (
          <div className="p-4 text-center text-gray-500">
            No se encontraron sugerencias
          </div>
        )}

        {allSuggestions.map((suggestion, index) => (
          <div
            key={`${suggestion.category}_${suggestion.id}`}
            className={`px-4 py-2 cursor-pointer flex items-center space-x-3 hover:bg-gray-50 ${
              index === highlightedIndex ? 'bg-blue-50' : ''
            }`}
            onClick={() => handleSuggestionClick(suggestion)}
          >
            <span className="text-lg">
              {suggestion.category === 'recent' && <Clock className="w-4 h-4 text-gray-400" />}
              {suggestion.category === 'popular' && <TrendingUp className="w-4 h-4 text-gray-400" />}
              {suggestion.category === 'suggestions' && <span>{getSuggestionIcon(suggestion.type)}</span>}
            </span>

            <div className="flex-1">
              <div
                className="text-gray-900"
                dangerouslySetInnerHTML={{ __html: formatSuggestion(suggestion) }}
              />
              {suggestion.count && (
                <div className="text-xs text-gray-500">
                  {suggestion.count} resultados
                </div>
              )}
            </div>

            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
        ))}

        {/* Búsquedas recientes */}
        {state.inputValue.length === 0 && (
          <div className="border-t border-gray-200">
            <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
              Búsquedas recientes
            </div>
            {getRecentTerms().slice(0, 5).map((term, index) => (
              <div
                key={`recent_${index}`}
                className="px-4 py-2 cursor-pointer flex items-center space-x-3 hover:bg-gray-50"
                onClick={() => handleSuggestionClick({ id: `recent_${index}`, text: term, type: 'query' })}
              >
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="flex-1 text-gray-900">{term}</span>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={`
            relative flex items-center bg-white border rounded-lg transition-all duration-200
            ${state.isFocused ? 'border-blue-500 ring-2 ring-blue-100' : 'border-gray-300'}
            ${sizeClasses[size]}
          `}
        >
          {/* Icono de búsqueda */}
          <div className="absolute left-3 flex items-center">
            {isSearching ? (
              <div className="animate-spin">
                <Search className={`${iconSizes[size]} text-blue-500`} />
              </div>
            ) : (
              <Search className={`${iconSizes[size]} text-gray-400`} />
            )}
          </div>

          {/* Input principal */}
          <input
            ref={inputRef}
            type="text"
            value={state.inputValue}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`
              w-full pl-10 pr-20 border-0 rounded-lg focus:outline-none focus:ring-0
              ${sizeClasses[size]}
            `}
            autoComplete="off"
            spellCheck={false}
          />

          {/* Botones de acción */}
          <div className="absolute right-2 flex items-center space-x-1">
            {/* Limpiar */}
            {state.inputValue && (
              <button
                type="button"
                onClick={handleClear}
                className="p-1 text-gray-400 hover:text-gray-600 rounded"
              >
                <X className={iconSizes[size]} />
              </button>
            )}

            {/* Búsqueda por voz */}
            {showVoiceSearch && (
              <button
                type="button"
                onClick={handleVoiceSearch}
                disabled={state.isRecording}
                className={`
                  p-1 rounded transition-colors
                  ${state.isRecording
                    ? 'text-red-500 animate-pulse'
                    : 'text-gray-400 hover:text-gray-600'
                  }
                `}
              >
                <Mic className={iconSizes[size]} />
              </button>
            )}

            {/* Búsqueda avanzada */}
            {showAdvancedLink && (
              <button
                type="button"
                className="p-1 text-gray-400 hover:text-gray-600 rounded"
                onClick={() => {
                  // TODO: Abrir modal de búsqueda avanzada
                  console.log('Open advanced search modal');
                }}
              >
                <Settings className={iconSizes[size]} />
              </button>
            )}
          </div>
        </div>

        {/* Sugerencias */}
        {renderSuggestions()}
      </form>
    </div>
  );
});

SearchBar.displayName = 'SearchBar';

export default SearchBar;