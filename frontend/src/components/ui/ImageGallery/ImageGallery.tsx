// ---------------------------------------------------------------------------------------------
// ImageGallery.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageGallery Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ImageGallery.tsx
// Ruta: ~/src/components/ui/ImageGallery/ImageGallery.tsx
// Autor: IA Desarrolladora Universal
// Fecha de Creación: 2025-08-19
// Última Actualización: 2025-08-19
// Versión: 1.0.0
// Propósito: Componente React para galería de imágenes con gestión múltiple
//            Incluye selección múltiple, drag & drop para reordenar, búsqueda y filtros
//
// Modificaciones:
// 2025-08-19 - Creación inicial con vista grid responsive y selección múltiple
//
// ---------------------------------------------------------------------------------------------

import React, { useCallback, useMemo, useState } from 'react';
import { ImageGalleryProps, ViewMode } from './ImageGallery.types';

/**
 * Componente ImageGallery para gestión avanzada de múltiples imágenes
 * 
 * Características principales:
 * - Vista en grid, list o masonry responsive
 * - Selección múltiple con checkboxes
 * - Drag & drop para reordenar imágenes
 * - Búsqueda y filtrado en tiempo real
 * - Acciones masivas (seleccionar todo, limpiar, eliminar)
 * - Acciones por imagen (favoritos, eliminar, información)
 * - Soporte para thumbnails y metadata
 * 
 * @example
 * 
 * 
 * @param props - Propiedades del componente ImageGallery
 * @returns JSX.Element Componente de galería completamente funcional
 */
const ImageGallery: React.FC<ImageGalleryProps> = ({
  images,
  viewMode = 'grid',
  allowMultiSelect = true,
  allowReorder = true,
  onSelectionChange,
  onReorder,
  onDelete,
  onToggleFavorite,
  onSearch,
  thumbnailSize = 200,
  className = ''
}) => {
  // Estados locales
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [currentViewMode, setCurrentViewMode] = useState<ViewMode>(viewMode);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  // Filtrar imágenes basado en búsqueda
  const filteredImages = useMemo(() => {
    
    return images.filter(image =>
      image.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [images, searchQuery]);

  // Manejar selección de imagen
  const handleImageSelect = useCallback((imageId: string, isSelected: boolean) => {
    const newSelection = new Set(selectedImages);
    
    if (isSelected) {
      newSelection.add(imageId);
    } else {
      newSelection.delete(imageId);
    }
    
    setSelectedImages(newSelection);
    
    if (onSelectionChange) {
      const selectedImagesList = images.filter(img => newSelection.has(img.id));
      onSelectionChange(selectedImagesList);
    }
  }, [selectedImages, images, onSelectionChange]);

  // Funciones para drag & drop de reordenamiento
  const handleImageDragStart = useCallback((e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  }, []);

  const handleImageDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }, []);

  const handleImageDrop = useCallback((e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) return;

    const newImages = [...filteredImages];
    const draggedImageArray = newImages.splice(draggedIndex, 1);
    const draggedImage = draggedImageArray[0];
    if (draggedImage === undefined) return;
    newImages.splice(dropIndex, 0, draggedImage);

    setDraggedIndex(null);
    onReorder?.(newImages);
  }, [draggedIndex, filteredImages, onReorder]);

  // Acciones masivas
  const handleSelectAll = useCallback(() => {
    const allIds = new Set(filteredImages.map(img => img.id));
    setSelectedImages(allIds);
    if (onSelectionChange) {
      onSelectionChange(filteredImages);
    }
  }, [filteredImages, onSelectionChange]);

  const handleClearSelection = useCallback(() => {
    setSelectedImages(new Set());
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  }, [onSelectionChange]);

  const handleDeleteSelected = useCallback(() => {
    if (onDelete) {
      selectedImages.forEach(imageId => onDelete(imageId));
    }
    setSelectedImages(new Set());
  }, [selectedImages, onDelete]);

  // Renderizado del componente
  return (
    <div className={`image-gallery ${className}`}>
      {/* Toolbar */}
      <div className="gallery-toolbar mb-4 flex flex-wrap items-center justify-between gap-4">
        {/* Búsqueda */}
        <div className="flex-1 min-w-64">
          <input
            type="text"
            placeholder="Buscar imágenes..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              onSearch?.(e.target.value);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        {/* Acciones masivas */}
        <div className="flex items-center gap-2">
          {allowMultiSelect && (
            <>
              <button
                onClick={handleSelectAll}
                className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                disabled={filteredImages.length === 0}
              >
                Seleccionar Todo
              </button>
              <button
                onClick={handleClearSelection}
                className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                disabled={selectedImages.size === 0}
              >
                Limpiar
              </button>
              {selectedImages.size > 0 && onDelete && (
                <button
                  onClick={handleDeleteSelected}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Eliminar ({selectedImages.size})
                </button>
              )}
            </>
          )}
        </div>

        {/* Controles de vista */}
        <div className="flex items-center gap-2">
          {(['grid', 'list', 'masonry'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setCurrentViewMode(mode)}
              className={`px-3 py-1 rounded ${
                currentViewMode === mode
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Grid de imágenes */}
      <div className={`gallery-grid ${
        currentViewMode === 'grid' ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4' :
        currentViewMode === 'list' ? 'space-y-2' :
        'columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4'
      }`}>
        {filteredImages.map((image, index) => (
          <div
            key={image.id}
            className="gallery-item relative group cursor-move"
            style={{ width: currentViewMode === 'grid' ? thumbnailSize : 'auto' }}
            draggable={allowReorder}
            onDragStart={allowReorder ? (e) => handleImageDragStart(e, index) : undefined}
            onDragOver={allowReorder ? handleImageDragOver : undefined}
            onDrop={allowReorder ? (e) => handleImageDrop(e, index) : undefined}
          >
            {/* Checkbox para selección */}
            {allowMultiSelect && (
              <div className="absolute top-2 left-2 z-10">
                <input
                  type="checkbox"
                  checked={selectedImages.has(image.id)}
                  onChange={(e) => handleImageSelect(image.id, e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
            )}
            
            {/* Imagen */}
            <img
              src={image.thumbnail || image.url}
              alt={image.name}
              className="w-full h-auto object-cover rounded-lg shadow-sm hover:shadow-md transition-shadow"
            />
            
            {/* Overlay con acciones */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
              <div className="flex gap-2">
                {onToggleFavorite && (
                  <button
                    onClick={() => onToggleFavorite(image.id)}
                    className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100"
                    title={image.favorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
                  >
                    <span className={image.favorite ? 'text-red-500' : 'text-gray-500'}>♥</span>
                  </button>
                )}
                
                {onDelete && (
                  <button
                    onClick={() => onDelete(image.id)}
                    className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100"
                    title="Eliminar imagen"
                  >
                    <span className="text-red-500">🗑</span>
                  </button>
                )}
              </div>
            </div>
            
            {/* Información de la imagen */}
            <div className="mt-2 text-xs text-gray-600">
              <div className="truncate">{image.name}</div>
              <div>{(image.size / 1024).toFixed(1)} KB</div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Mensaje cuando no hay imágenes */}
      {filteredImages.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          {searchQuery ? 'No se encontraron imágenes que coincidan con la búsqueda' : 'No hay imágenes para mostrar'}
        </div>
      )}
    </div>
  );
};

export default ImageGallery;