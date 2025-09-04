// ~/src/components/ui/ImageUpload/ImageUpload.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageUpload Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ImageUpload.tsx
// Ruta: ~/src/components/ui/ImageUpload/ImageUpload.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-18
// Última Actualización: 2025-08-19
// Versión: 1.1.0
// Propósito: Componente React para subida de imágenes con funcionalidad drag & drop y crop
//            Incluye validaciones de tamaño, tipo y cantidad de archivos
//
// Modificaciones:
// 2025-08-18 - Creación inicial con useDropzone y validaciones básicas
// 2025-08-19 - Agregada funcionalidad de crop con react-image-crop
//
// ---------------------------------------------------------------------------------------------

import React, { useCallback, useMemo } from 'react';
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { ImageUploadProps, ImageFile } from './ImageUpload.types';
import { ImageCrop } from '../ImageCrop';
import { CropData } from '../ImageCrop/ImageCrop.types';

/**
 * Componente ImageUpload con funcionalidad drag & drop y crop
 *
 * @param props - Propiedades del componente
 * @returns JSX.Element
 */
const ImageUpload: React.FC<ImageUploadProps> = ({
  onImageUpload,
  maxFiles = 5,
  maxSize = 5 * 1024 * 1024, // 5MB
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
  className = '',
  enableCrop = false,
  showPreview = true,
  disabled = false,
  onUploadProgress,
}) => {
  const [uploadedImages, setUploadedImages] = useState<ImageFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [imageLoadingStates, setImageLoadingStates] = useState<
    Record<string, boolean>
  >({});
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>(
    {}
  );
  const [_uploadStartTime, setUploadStartTime] = useState<
    Record<string, number>
  >({});
  const [estimatedTime, setEstimatedTime] = useState<Record<string, number>>(
    {}
  );
  const [_uploadIntervals, _setUploadIntervals] = useState<
    Record<string, NodeJS.Timeout>
  >({});
  const [showCropModal, setShowCropModal] = useState(false);
  const [imageToCrop, setImageToCrop] = useState<ImageFile | null>(null);

  // Calcular progreso total
  const totalProgress = useMemo(() => {
    const progressValues = Object.values(uploadProgress);
    if (progressValues.length === 0) return 0;
    return Math.round(
      progressValues.reduce((sum, prog) => sum + prog, 0) /
        progressValues.length
    );
  }, [uploadProgress]);

  // Calcular tiempo estimado total
  const totalEstimatedTime = useMemo(() => {
    const timeValues = Object.values(estimatedTime).filter(time => time > 0);
    if (timeValues.length === 0) return 0;
    return Math.max(...timeValues); // Tiempo máximo restante
  }, [estimatedTime]);

  /**
   * Simula progreso de upload
   */
  const simulateUploadProgress = useCallback(
    (fileId: string) => {
      const startTime = Date.now();
      setUploadStartTime(prev => ({ ...prev, [fileId]: startTime }));
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 15 + 5; // Incremento aleatorio 5-20%
        const currentTime = Date.now();
        const elapsed = (currentTime - startTime) / 1000; // segundos
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setUploadProgress(prev => ({ ...prev, [fileId]: 100 }));
          onUploadProgress?.(fileId, 100);
        } else {
          // Calcular tiempo estimado
          const speed = progress / elapsed; // progreso por segundo
          const remainingProgress = 100 - progress;
          const estimatedSeconds = Math.round(remainingProgress / speed);

          setEstimatedTime(prev => ({ ...prev, [fileId]: estimatedSeconds }));
          setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
          onUploadProgress?.(fileId, progress);
        }
      }, 200); // Más frecuente para animación suave
    },
    [onUploadProgress]
  );

  /**
   * Manejar drop de archivos
   */
  const handleDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setIsLoading(true);

      // Inicializar loading states individuales
      const newLoadingStates: Record<string, boolean> = {};
      acceptedFiles.forEach((_file, _index) => {
        const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        newLoadingStates[fileId] = true;
      });
      setImageLoadingStates(prev => ({ ...prev, ...newLoadingStates }));

      const imageFiles: ImageFile[] = acceptedFiles.map(file => ({
        file,
        preview: URL.createObjectURL(file),
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      }));

      setUploadedImages(prev => [...prev, ...imageFiles]);

      // Iniciar simulación de progreso para cada archivo
      imageFiles.forEach(imageFile => {
        simulateUploadProgress(imageFile.id);
      });
      onImageUpload(imageFiles);
      setIsLoading(false);
    },
    [onImageUpload, simulateUploadProgress]
  );

  /**
   * Convierte errores técnicos a mensajes user-friendly
   */
  const getDetailedErrorMessage = useCallback(
    (errorCode: string, fileName: string, fileSize?: number) => {
      switch (errorCode) {
        case 'file-too-large':
          const sizeMB = fileSize
            ? (fileSize / 1024 / 1024).toFixed(1)
            : 'desconocido';
          const maxMB = Math.round(maxSize / 1024 / 1024);
          return {
            icon: '⚠️',
            message: `El archivo "${fileName}" es muy grande (${sizeMB}MB). El tamaño máximo permitido es ${maxMB}MB.`,
          };
        case 'file-invalid-type':
          const allowedFormats = acceptedTypes
            .map(t => t.split('/')[1]?.toUpperCase())
            .join(', ');
          return {
            icon: '🚫',
            message: `El formato de "${fileName}" no está permitido. Formatos válidos: ${allowedFormats}`,
          };
        case 'too-many-files':
          return {
            icon: '📊',
            message: `Demasiados archivos seleccionados. Máximo permitido: ${maxFiles} archivos.`,
          };
        default:
          return {
            icon: '❌',
            message: `Error con el archivo "${fileName}": ${errorCode}`,
          };
      }
    },
    [maxSize, acceptedTypes, maxFiles]
  );

  /**
   * Eliminar imagen del preview
   */
  const removeImage = useCallback((id: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== id));
  }, []);

  /**
   * Manejar crop de imagen
   */
  const handleCropImage = useCallback((image: ImageFile) => {
    setImageToCrop(image);
    setShowCropModal(true);
  }, []);

  /**
   * Funciones para reordenar imágenes por drag & drop
   */
  const handleImageDragStart = useCallback(
    (e: React.DragEvent, index: number) => {
      setDraggedIndex(index);
      e.dataTransfer.effectAllowed = 'move';
    },
    []
  );

  const handleImageDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }, []);

  const handleImageDrop = useCallback(
    (e: React.DragEvent, dropIndex: number) => {
      e.preventDefault();
      if (draggedIndex === null || draggedIndex === dropIndex) return;

      const newImages = [...uploadedImages];
      const draggedImageArray = newImages.splice(draggedIndex, 1);
      const draggedImage = draggedImageArray[0];
      if (!draggedImage) return;
      newImages.splice(dropIndex, 0, draggedImage);

      setUploadedImages(newImages);
      onImageUpload(newImages);
      setDraggedIndex(null);
    },
    [draggedIndex, uploadedImages, onImageUpload]
  );

  /**
   * Limpiar URLs de objeto para evitar memory leaks
   */
  React.useEffect(() => {
    return () => {
      uploadedImages.forEach(img => URL.revokeObjectURL(img.preview));
    };
  }, [uploadedImages]);

  /**
   * Configuración de tipos aceptados para react-dropzone
   */
  const accept = useMemo(() => {
    const acceptObject: Record<string, string[]> = {};
    acceptedTypes.forEach(type => {
      acceptObject[type] = [];
    });
    return acceptObject;
  }, [acceptedTypes]);

  /**
   * Configuración de useDropzone
   */
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
    fileRejections,
  } = useDropzone({
    onDrop: handleDrop,
    accept,
    maxFiles,
    maxSize,
    multiple: maxFiles > 1,
    disabled,
  });

  /**
   * Clases CSS dinámicas basadas en estado
   */
  const dropzoneClasses = `
    border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
    ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
    ${isDragAccept ? 'border-green-500 bg-green-50' : ''}
    ${isDragReject ? 'border-red-500 bg-red-50' : ''}
    ${className}
  `.trim();

  return (
    <div className='w-full'>
      {/* Progress Bar Global */}
      {isLoading && totalProgress > 0 && (
        <div className='mb-4 bg-gray-200 rounded-full h-2 overflow-hidden'>
          <div
            className='h-full rounded-full transition-all duration-300 ease-out bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 animate-pulse'
            style={{ width: `${totalProgress}%` }}
          />
          <div className='flex justify-between text-xs text-gray-500 mt-1'>
            <span>Subiendo archivos...</span>
            <span>
              {`${totalProgress}%`}
              {totalEstimatedTime > 0 && ` - ${totalEstimatedTime}s restantes`}
            </span>
          </div>
        </div>
      )}

      {/* Zona de Drop */}
      <div {...getRootProps()} className={dropzoneClasses}>
        <input {...getInputProps()} />
        <div className='space-y-2'>
          <div className='text-4xl'>📁</div>
          {isLoading && <div className='text-blue-600'>⏳ Subiendo...</div>}
          {isDragActive ? (
            <p className='text-blue-600 font-medium'>
              {isDragAccept
                ? 'Suelta las imágenes aquí...'
                : 'Tipo de archivo no soportado'}
            </p>
          ) : (
            <div>
              <p className='text-gray-700 font-medium'>
                Arrastra imágenes aquí o haz clic para seleccionar
              </p>
              <p className='text-sm text-gray-500 mt-1'>
                Máximo {maxFiles} archivos, {Math.round(maxSize / 1024 / 1024)}
                MB por archivo
              </p>
              <p className='text-xs text-gray-400 mt-1'>
                Formatos:{' '}
                {acceptedTypes
                  .map(t => t.split('/')[1]?.toUpperCase() || t)
                  .join(', ')}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Preview de imágenes */}
      {showPreview && uploadedImages.length > 0 && (
        <div className='mt-6'>
          <h4 className='text-sm font-medium text-gray-700 mb-3'>
            Imágenes seleccionadas:
          </h4>
          <div className='grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4'>
            {uploadedImages.map((image, index) => (
              <div
                key={image.id}
                className='relative group cursor-move'
                draggable={true}
                onDragStart={e => handleImageDragStart(e, index)}
                onDragOver={handleImageDragOver}
                onDrop={e => handleImageDrop(e, index)}
              >
                <div className='aspect-square bg-gray-100 rounded-lg overflow-hidden'>
                  {imageLoadingStates[image.id] ? (
                    <div className='w-full h-full flex items-center justify-center bg-gray-200 animate-pulse'>
                      <div className='text-gray-400 text-2xl'>⏳</div>
                    </div>
                  ) : (
                    <img
                      src={image.preview}
                      alt={image.file.name}
                      className='w-full h-full object-cover'
                      onLoad={() =>
                        setImageLoadingStates(prev => ({
                          ...prev,
                          [image.id]: false,
                        }))
                      }
                    />
                  )}
                </div>

                {/* Mini Progress Bar por imagen */}
                {uploadProgress[image.id] &&
                  (uploadProgress[image.id] || 0) < 100 && (
                    <div className='absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-1'>
                      <div className='bg-gray-300 rounded-full h-1 overflow-hidden'>
                        <div
                          className='h-full rounded-full transition-all duration-300 bg-gradient-to-r from-green-400 via-green-500 to-green-600'
                          style={{ width: `${uploadProgress[image.id] || 0}%` }}
                        />
                      </div>
                      <div className='text-white text-xs text-center mt-1'>
                        {`${Math.round(uploadProgress[image.id] || 0)}%`}
                      </div>
                    </div>
                  )}

                {/* Botón de Crop */}
                {enableCrop && (
                  <button
                    onClick={() => handleCropImage(image)}
                    className='absolute top-2 left-2 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity'
                    title='Recortar imagen'
                  >
                    ✂️
                  </button>
                )}

                {/* Botón de Eliminar */}
                <button
                  onClick={() => removeImage(image.id)}
                  className='absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity'
                  title='Eliminar imagen'
                >
                  ×
                </button>

                {/* Información del archivo */}
                <p
                  className='text-xs text-gray-500 mt-1 truncate'
                  title={image.file.name}
                >
                  {image.file.name}
                </p>
                <p className='text-xs text-gray-400'>
                  {(image.file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Errores de validación */}
      {fileRejections.length > 0 && (
        <div className='mt-4 p-3 bg-red-50 border border-red-200 rounded-lg'>
          <h4 className='text-sm font-medium text-red-800 mb-3 flex items-center'>
            <span className='mr-2'>⚠️</span>
            Archivos que no pudieron ser procesados:
          </h4>
          <div className='space-y-2'>
            {fileRejections.map(({ file, errors }) => (
              <div
                key={file.name}
                className='p-3 bg-red-50 border border-red-200 rounded-lg'
              >
                <div className='flex items-start space-x-2'>
                  <span className='text-lg mt-0.5'>
                    {
                      getDetailedErrorMessage(
                        errors[0]?.code || 'unknown',
                        file.name,
                        file.size
                      ).icon
                    }
                  </span>
                  <div className='flex-1'>
                    <p className='text-sm text-red-800 font-medium'>
                      {
                        getDetailedErrorMessage(
                          errors[0]?.code || 'unknown',
                          file.name,
                          file.size
                        ).message
                      }
                    </p>
                    <p className='text-xs text-red-600 mt-1'>
                      Archivo: {file.name}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de Crop */}
      {showCropModal && imageToCrop && (
        <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
          <ImageCrop
            imageFile={imageToCrop.file}
            onCropComplete={(cropData: CropData) => {
              const updatedImages = uploadedImages.map(img =>
                img.id === imageToCrop.id
                  ? {
                      ...img,
                      file: cropData.croppedFile,
                      preview: cropData.croppedImageUrl,
                    }
                  : img
              );
              setUploadedImages(updatedImages);
              onImageUpload(updatedImages);
              setShowCropModal(false);
              setImageToCrop(null);
            }}
            onCancel={() => {
              setShowCropModal(false);
              setImageToCrop(null);
            }}
            aspectRatio={1}
          />
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
