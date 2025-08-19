

import React from 'react';
import ImageUpload from '../components/ui/ImageUpload/ImageUpload';

const TestImageUpload = () => {
  const handleImageUpload = (images: any[]) => {
    console.log('Imágenes subidas:', images);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">
          🧪 Test ImageUpload Component - Placeholders Loading
        </h1>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <ImageUpload 
            onImageUpload={handleImageUpload}
            maxFiles={5}
            showPreview={true}
          />
        </div>
      </div>
    </div>
  );
};

export default TestImageUpload;