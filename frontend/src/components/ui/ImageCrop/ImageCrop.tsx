// src/components/ui/ImageCrop/ImageCrop.tsx
import React, { useState, useRef, useCallback } from 'react';
import ReactCrop, { Crop, PercentCrop, PixelCrop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { ImageCropProps, CropResult } from './ImageCrop.types';

const ImageCrop: React.FC<ImageCropProps> = ({
  imageFile,
  onCropComplete,
  onCancel,
  initialCrop = { unit: '%', width: 50, height: 50, x: 25, y: 25 },
  aspectRatio,
  minWidth = 50,
  minHeight = 50,
  className = '',
}) => {
  const [crop, setCrop] = useState<PercentCrop | PixelCrop>(initialCrop);
  const [completedCrop, setCompletedCrop] = useState<Crop>();
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Crear URL de la imagen cuando se monta el componente
  React.useEffect(() => {
    const url = URL.createObjectURL(imageFile);
    setImageUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [imageFile]);

  // Función para generar imagen recortada
  const getCroppedImg = useCallback(
    async (
      image: HTMLImageElement,
      crop: Crop,
      fileName: string
    ): Promise<CropResult> => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        throw new Error('No 2d context');
      }

      const scaleX = image.naturalWidth / image.width;
      const scaleY = image.naturalHeight / image.height;

      canvas.width = crop.width;
      canvas.height = crop.height;

      ctx.drawImage(
        image,
        crop.x * scaleX,
        crop.y * scaleY,
        crop.width * scaleX,
        crop.height * scaleY,
        0,
        0,
        crop.width,
        crop.height
      );

      return new Promise(resolve => {
        canvas.toBlob(blob => {
          if (!blob) {
            throw new Error('Canvas is empty');
          }
          const croppedFile = new File([blob], fileName, {
            type: imageFile.type,
            lastModified: Date.now(),
          });
          const croppedImageUrl = URL.createObjectURL(blob);
          resolve({
            croppedImageUrl,
            croppedFile,
            crop,
          });
        }, imageFile.type);
      });
    },
    [imageFile]
  );

  // Manejar aplicar crop
  const handleApplyCrop = useCallback(async () => {
    if (!completedCrop || !imgRef.current) return;

    setIsProcessing(true);
    try {
      const result = await getCroppedImg(
        imgRef.current,
        completedCrop,
        `cropped_${imageFile.name}`
      );

      onCropComplete({
        crop: completedCrop,
        croppedImageUrl: result.croppedImageUrl,
        originalFile: imageFile,
        croppedFile: result.croppedFile,
      });
    } catch (error) {
      console.error('Error cropping image:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [completedCrop, imageFile, onCropComplete, getCroppedImg]);

  return (
    <div
      className={`bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto ${className}`}
    >
      <div className='flex justify-between items-center mb-4'>
        <h3 className='text-lg font-semibold text-gray-800'>Recortar Imagen</h3>
        <button
          onClick={onCancel}
          className='text-gray-500 hover:text-gray-700'
          title='Cerrar'
        >
          ✕
        </button>
      </div>

      <div className='mb-4 flex justify-center'>
        <ReactCrop
          crop={crop}
          onChange={c => setCrop(c)}
          onComplete={c => setCompletedCrop(c)}
          aspect={aspectRatio}
          minWidth={minWidth}
          minHeight={minHeight}
        >
          <img
            ref={imgRef}
            src={imageUrl}
            alt='Crop preview'
            className='max-w-full max-h-96 object-contain'
          />
        </ReactCrop>
      </div>

      <div className='flex justify-between items-center'>
        <div className='text-sm text-gray-600'>
          <p>📁 {imageFile.name}</p>
          <p>
            📏 {Math.round(completedCrop?.width || 0)} ×{' '}
            {Math.round(completedCrop?.height || 0)} px
          </p>
        </div>

        <div className='flex space-x-3'>
          <button
            onClick={onCancel}
            className='px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors'
          >
            Cancelar
          </button>
          <button
            onClick={handleApplyCrop}
            disabled={!completedCrop || isProcessing}
            className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            {isProcessing ? 'Procesando...' : 'Aplicar Recorte'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageCrop;
