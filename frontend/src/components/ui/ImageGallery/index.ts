// ---------------------------------------------------------------------------------------------
// index.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageGallery Index
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: index.ts
// Ruta: ~/src/components/ui/ImageGallery/index.ts
// Autor: IA Desarrolladora Universal
// Fecha de Creación: 2025-08-19
// Última Actualización: 2025-08-19
// Versión: 1.0.0
// Propósito: Archivo de exportación principal para el componente ImageGallery
//            Facilita la importación del componente y sus tipos desde otros archivos
//
// Modificaciones:
// 2025-08-19 - Creación inicial con exports del componente y tipos
//
// ---------------------------------------------------------------------------------------------

/**
 * Exportación por defecto del componente ImageGallery
 */
export { default } from './ImageGallery';

/**
 * Exportación de tipos TypeScript
 */
export type { ImageGalleryProps, GalleryImage, ViewMode } from './ImageGallery.types';

/**
 * Ejemplo de uso:
 * import ImageGallery, { ImageGalleryProps, GalleryImage, ViewMode } from '@/components/ui/ImageGallery';
 * 
 * const images: GalleryImage[] = [...];
 * 
 * <ImageGallery
 *   images={images}
 *   viewMode="grid"
 *   allowMultiSelect={true}
 *   onSelectionChange={(selected) => console.log(selected)}
 * />
 */