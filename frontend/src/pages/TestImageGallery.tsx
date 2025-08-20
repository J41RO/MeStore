// import React from 'react'; // No usado directamente
import ImageGallery from '../components/ui/ImageGallery/ImageGallery';
import { GalleryImage } from '../components/ui/ImageGallery/ImageGallery.types';

const TestImageGallery = () => {
  // Mock data para demostración
  const mockImages: GalleryImage[] = [
    {
      id: '1',
      url: 'https://picsum.photos/400/300?random=1',
      thumbnail: 'https://picsum.photos/200/150?random=1',
      name: 'Paisaje Montañoso',
      size: 1024000,
      createdAt: new Date('2025-01-15'),
      selected: false,
      favorite: false,
      metadata: { width: 400, height: 300, type: 'image/jpeg' }
    },
    {
      id: '2',
      url: 'https://picsum.photos/400/300?random=2',
      thumbnail: 'https://picsum.photos/200/150?random=2',
      name: 'Ciudad Nocturna',
      size: 2048000,
      createdAt: new Date('2025-01-16'),
      selected: false,
      favorite: true,
      metadata: { width: 400, height: 300, type: 'image/png' }
    },
    {
      id: '3',
      url: 'https://picsum.photos/400/300?random=3',
      thumbnail: 'https://picsum.photos/200/150?random=3',
      name: 'Bosque Verde',
      size: 1536000,
      createdAt: new Date('2025-01-17'),
      selected: false,
      favorite: false,
      metadata: { width: 400, height: 300, type: 'image/webp' }
    },
    {
      id: '4',
      url: 'https://picsum.photos/400/300?random=4',
      thumbnail: 'https://picsum.photos/200/150?random=4',
      name: 'Playa Tropical',
      size: 1792000,
      createdAt: new Date('2025-01-18'),
      selected: false,
      favorite: true,
      metadata: { width: 400, height: 300, type: 'image/jpeg' }
    },
    {
      id: '5',
      url: 'https://picsum.photos/400/300?random=5',
      thumbnail: 'https://picsum.photos/200/150?random=5',
      name: 'Arquitectura Moderna',
      size: 2304000,
      createdAt: new Date('2025-01-19'),
      selected: false,
      favorite: false,
      metadata: { width: 400, height: 300, type: 'image/png' }
    }
  ];

  const handleSelectionChange = (selectedImages: GalleryImage[]) => {
    console.log('Selección cambiada:', selectedImages);
  };

  const handleReorder = (reorderedImages: GalleryImage[]) => {
    console.log('Imágenes reordenadas:', reorderedImages);
  };

  const handleDelete = (imageId: string) => {
    console.log('Eliminar imagen:', imageId);
  };

  const handleToggleFavorite = (imageId: string) => {
    console.log('Toggle favorito:', imageId);
  };

  const handleSearch = (query: string) => {
    console.log('Búsqueda:', query);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">
          🖼️ Test ImageGallery Component - Demo Galería
        </h1>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <ImageGallery
            images={mockImages}
            viewMode="grid"
            allowMultiSelect={true}
            allowReorder={true}
            onSelectionChange={handleSelectionChange}
            onReorder={handleReorder}
            onDelete={handleDelete}
            onToggleFavorite={handleToggleFavorite}
            onSearch={handleSearch}
            thumbnailSize={200}
          />
        </div>
      </div>
    </div>
  );
};

export default TestImageGallery;