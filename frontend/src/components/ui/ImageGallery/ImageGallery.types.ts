// ---------------------------------------------------------------------------------------------
// ImageGallery.types.ts
// ---------------------------------------------------------------------------------------------
// Descripción: Definiciones de tipos TypeScript para el componente ImageGallery
// Autor: IA Desarrolladora Universal
// Última Actualización: 2025-08-19
// Versión: 1.0.0
// Propósito: Definición de tipos TypeScript para el componente ImageGallery con gestión múltiple
//            Incluye interfaces para imágenes de galería, modos de vista y propiedades del componente
//
// Modificaciones:
// 2025-08-19 - Creación inicial con interfaces GalleryImage, ViewMode e ImageGalleryProps
//
// ---------------------------------------------------------------------------------------------

/**
 * Interfaz para representar una imagen en la galería
 */
export interface GalleryImage {
  /** ID único de la imagen */
  id: string;
  /** URL de la imagen */
  url: string;
  /** URL de thumbnail para vista previa */
  thumbnail?: string;
  /** Nombre del archivo */
  name: string;
  /** Tamaño del archivo en bytes */
  size: number;
  /** Fecha de creación/subida */
  createdAt: Date;
  /** Indica si la imagen está seleccionada */
  selected?: boolean;
  /** Indica si es imagen favorita */
  favorite?: boolean;
  /** Metadatos adicionales de la imagen */
  metadata?: {
    width?: number;
    height?: number;
    type?: string;
  };
}

/**
 * Modos de vista disponibles para la galería
 */
export type ViewMode = 'grid' | 'list' | 'masonry';

/**
 * Propiedades del componente ImageGallery
 */
export interface ImageGalleryProps {
  /** Array de imágenes para mostrar en la galería */
  images: GalleryImage[];
  /** Modo de vista inicial */
  viewMode?: ViewMode;
  /** Permite selección múltiple */
  allowMultiSelect?: boolean;
  /** Permite reordenar imágenes con drag & drop */
  allowReorder?: boolean;
  /** Callback cuando cambia la selección */
  onSelectionChange?: (selectedImages: GalleryImage[]) => void;
  /** Callback cuando se reordenan las imágenes */
  onReorder?: (reorderedImages: GalleryImage[]) => void;
  /** Callback cuando se elimina una imagen */
  onDelete?: (imageId: string) => void;
  /** Callback cuando se marca/desmarca como favorita */
  onToggleFavorite?: (imageId: string) => void;
  /** Callback para búsqueda/filtrado */
  onSearch?: (query: string) => void;
  /** Tamaño de las miniaturas en píxeles */
  thumbnailSize?: number;
  /** Clase CSS adicional */
  className?: string;
}
