// ~/src/components/ui/ImageUpload/index.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageUpload Component Exports
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: index.ts
// Ruta: ~/src/components/ui/ImageUpload/index.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-18
// Última Actualización: 2025-08-18
// Versión: 1.0.0
// Propósito: Exportaciones centralizadas para el componente ImageUpload
//            Permite importación limpia desde otros módulos
//
// Modificaciones:
// 2025-08-18 - Creación inicial con exportaciones de componente y tipos
//
// ---------------------------------------------------------------------------------------------

/**
 * Exportación por defecto del componente ImageUpload
 */
export { default } from './ImageUpload';

/**
 * Exportación de tipos TypeScript
 */
export type { ImageUploadProps, ImageFile } from './ImageUpload.types';

/**
 * Ejemplo de uso:
 * 
 * import ImageUpload, { ImageUploadProps, ImageFile } from '@/components/ui/ImageUpload';
 * 
 * const handleImageUpload = (files: ImageFile[]) => {
 *   console.log('Imágenes subidas:', files);
 * };
 * 
 * <ImageUpload
 *   onImageUpload={handleImageUpload}
 *   maxFiles={3}
 *   maxSize={2 * 1024 * 1024} // 2MB
 *   acceptedTypes={['image/jpeg', 'image/png']}
 *   showPreview={true}
 *   disabled={false}
 * />
 */