import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, ZoomIn, ImageIcon } from 'lucide-react';

interface ProductImage {
  id: number;
  image_url: string;
  is_primary: boolean;
}

interface ProductImageGalleryProps {
  images: ProductImage[];
  productName: string;
}

const ProductImageGallery: React.FC<ProductImageGalleryProps> = ({ 
  images, 
  productName 
}) => {
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isZoomed, setIsZoomed] = useState(false);
  const [imageLoadErrors, setImageLoadErrors] = useState<Set<number>>(new Set());

  // Sort images: primary first, then by id
  const sortedImages = React.useMemo(() => {
    if (!images || images.length === 0) return [];
    
    return [...images].sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1;
      if (!a.is_primary && b.is_primary) return 1;
      return a.id - b.id;
    });
  }, [images]);

  // Reset selected index when images change
  useEffect(() => {
    setSelectedImageIndex(0);
    setImageLoadErrors(new Set());
  }, [images]);

  const handleImageError = (imageId: number) => {
    setImageLoadErrors(prev => new Set([...prev, imageId]));
  };

  const handlePreviousImage = () => {
    setSelectedImageIndex(prev => 
      prev === 0 ? sortedImages.length - 1 : prev - 1
    );
  };

  const handleNextImage = () => {
    setSelectedImageIndex(prev => 
      prev === sortedImages.length - 1 ? 0 : prev + 1
    );
  };

  const handleThumbnailClick = (index: number) => {
    setSelectedImageIndex(index);
  };

  const handleZoomToggle = () => {
    setIsZoomed(!isZoomed);
  };

  const getImageUrl = (url: string) => {
    // If the URL is already absolute, use it as is
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    // If it's a relative URL, make it absolute
    if (url.startsWith('/')) {
      return url;
    }
    // If it's just a filename, assume it's in uploads
    return `/uploads/images/${url}`;
  };

  const PlaceholderImage: React.FC<{ className?: string; showIcon?: boolean }> = ({ 
    className = "", 
    showIcon = true 
  }) => (
    <div className={`bg-gray-100 flex items-center justify-center ${className}`}>
      {showIcon && (
        <div className="text-gray-400 text-center">
          <ImageIcon className="h-12 w-12 mx-auto mb-2" />
          <p className="text-sm">Sin imagen</p>
        </div>
      )}
    </div>
  );

  // If no images provided or all images failed to load
  if (!sortedImages.length || sortedImages.every(img => imageLoadErrors.has(img.id))) {
    return (
      <div className="space-y-4">
        <div className="aspect-square w-full bg-gray-100 rounded-lg overflow-hidden">
          <PlaceholderImage className="w-full h-full" />
        </div>
      </div>
    );
  }

  const currentImage = sortedImages[selectedImageIndex];
  const hasMultipleImages = sortedImages.length > 1;

  // Ensure we have a valid current image
  if (!currentImage) {
    return (
      <div className="space-y-4">
        <div className="aspect-square w-full bg-gray-100 rounded-lg overflow-hidden">
          <PlaceholderImage className="w-full h-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Main Image */}
      <div className="relative aspect-square w-full bg-gray-100 rounded-lg overflow-hidden group">
        {imageLoadErrors.has(currentImage.id) ? (
          <PlaceholderImage className="w-full h-full" />
        ) : (
          <>
            <img
              src={getImageUrl(currentImage.image_url)}
              alt={`${productName} - Imagen ${selectedImageIndex + 1}`}
              className={`w-full h-full object-cover transition-transform duration-300 ${
                isZoomed ? 'scale-125' : 'scale-100 hover:scale-105'
              }`}
              onError={() => handleImageError(currentImage.id)}
            />
            
            {/* Zoom Button */}
            <button
              onClick={handleZoomToggle}
              className="absolute top-4 right-4 bg-black bg-opacity-50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-opacity-70"
              title={isZoomed ? 'Zoom out' : 'Zoom in'}
            >
              <ZoomIn className="h-4 w-4" />
            </button>

            {/* Navigation Arrows (only if multiple images) */}
            {hasMultipleImages && (
              <>
                <button
                  onClick={handlePreviousImage}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-opacity-70"
                  title="Imagen anterior"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>

                <button
                  onClick={handleNextImage}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-opacity-70"
                  title="Siguiente imagen"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </>
            )}

            {/* Image Counter (only if multiple images) */}
            {hasMultipleImages && (
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white text-sm px-2 py-1 rounded">
                {selectedImageIndex + 1} / {sortedImages.length}
              </div>
            )}
          </>
        )}
      </div>

      {/* Thumbnails (only show if multiple images) */}
      {hasMultipleImages && (
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {sortedImages.map((image, index) => (
            <button
              key={image.id}
              onClick={() => handleThumbnailClick(index)}
              className={`flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 transition-all duration-200 ${
                index === selectedImageIndex
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {imageLoadErrors.has(image.id) ? (
                <PlaceholderImage className="w-full h-full" showIcon={false} />
              ) : (
                <img
                  src={getImageUrl(image.image_url)}
                  alt={`${productName} - Miniatura ${index + 1}`}
                  className="w-full h-full object-cover"
                  onError={() => handleImageError(image.id)}
                />
              )}
            </button>
          ))}
        </div>
      )}

      {/* Mobile Touch Indicators */}
      {hasMultipleImages && (
        <div className="flex justify-center space-x-1 md:hidden">
          {sortedImages.map((_, index) => (
            <button
              key={index}
              onClick={() => handleThumbnailClick(index)}
              className={`w-2 h-2 rounded-full transition-colors duration-200 ${
                index === selectedImageIndex ? 'bg-blue-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      )}

      {/* Keyboard Navigation Hint */}
      {hasMultipleImages && (
        <div className="text-center text-xs text-gray-500 hidden md:block">
          Usa las flechas del teclado o haz clic en las imágenes para navegar
        </div>
      )}
    </div>
  );
};

export default ProductImageGallery;