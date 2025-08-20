// ~/src/components/ui/ImageUpload/ImageUpload.types.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageUpload Component Types
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ImageUpload.types.ts
// Ruta: ~/src/components/ui/ImageUpload/ImageUpload.types.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-18
// Última Actualización: 2025-08-18
// Versión: 1.0.0
// Propósito: Definición de tipos TypeScript para el componente ImageUpload con drag & drop
//            Incluye interfaces para archivos de imagen y propiedades del componente
//
// Modificaciones:
// 2025-08-18 - Creación inicial con interfaces ImageFile e ImageUploadProps
//
// ---------------------------------------------------------------------------------------------

/**
 * Interfaz para representar un archivo de imagen con preview
 */
export interface ImageFile {
  /** El archivo original de imagen */
  file: File;
  /** URL de preview para mostrar la imagen */
  preview: string;
  /** Identificador único del archivo */
  /** Progreso de upload (0-100) opcional */
  uploadProgress?: number;
  id: string;
}
/**
 * Interfaz para tracking de progreso de upload
 */
export interface UploadProgress {
  /** ID del archivo en upload */
  fileId: string;
  /** Progreso de 0 a 100 */
  progress: number;
  /** Estado del upload */
  status: 'uploading' | 'completed' | 'error';
}

/**
 * Propiedades del componente ImageUpload
 */
export interface ImageUploadProps {
  /** Callback ejecutado cuando se suben imágenes */
  /** Callback opcional para tracking de progreso de upload */
  onUploadProgress?: (fileId: string, progress: number) => void;
  onImageUpload: (files: ImageFile[]) => void;
  /** Número máximo de archivos permitidos (default: 5) */
  maxFiles?: number;
  /** Tamaño máximo por archivo en bytes (default: 5MB) */
  maxSize?: number;
  /** Tipos de archivo aceptados (default: jpeg, png, webp) */
  acceptedTypes?: string[];
  /** Clases CSS adicionales */
  /** Mostrar preview de imágenes seleccionadas (default: true) */
  showPreview?: boolean;
  /** Deshabilitar el componente (default: false) */
  disabled?: boolean;
  className?: string;
}