import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { X } from 'lucide-react';
import {
  createProductSchema,
  ProductFormData,
  defaultProductValues,
  getCategoryOptions,
} from '../../schemas/productSchema';
import { CreateProductData, UpdateProductData } from '../../types/api.types';
import api from '../../services/api';
import ImageUpload from '../ui/ImageUpload/ImageUpload';
import { ImageFile } from '../ui/ImageUpload/ImageUpload.types';
import { uploadProductImages, validateProductImageFiles, getProductImages, deleteProductImage } from '../../services/productImageService';
import type { ProductImage } from '../../services/productImageService';

export interface ProductFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<ProductFormData>;
  onSubmit?: (data: any) => void;
  onCancel?: () => void;
  onSuccess?: () => void;
}

interface MessageState {
  text: string;
  type: 'success' | 'error' | 'info';
}

const ProductForm: React.FC<ProductFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<MessageState | null>(null);
  const [selectedImages, setSelectedImages] = useState<ImageFile[]>([]);
  const [existingImages, setExistingImages] = useState<ProductImage[]>([]);
  const [deletedImageIds, setDeletedImageIds] = useState<string[]>([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [loadingExistingImages, setLoadingExistingImages] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    setValue,
  } = useForm<any>({
    resolver: yupResolver(createProductSchema) as any,
    mode: 'onChange',
    defaultValues: {
      ...defaultProductValues,
      ...initialData,
    },
  });

  useEffect(() => {
    if (mode === 'edit' && initialData) {
      Object.entries(initialData).forEach(([key, value]) => {
        setValue(key as keyof ProductFormData, value);
      });
    }
  }, [mode, initialData, setValue]);

  // Load existing images when in edit mode
  useEffect(() => {
    const loadExistingImages = async () => {
      if (mode === 'edit' && initialData?.id) {
        setLoadingExistingImages(true);
        try {
          const images = await getProductImages(initialData.id as string);
          setExistingImages(images);
        } catch (error) {
          console.error('Error loading existing images:', error);
          showMessage('Error cargando imágenes existentes', 'error');
        } finally {
          setLoadingExistingImages(false);
        }
      }
    };

    loadExistingImages();
  }, [mode, initialData?.id]);

  const clearMessage = () => {
    setMessage(null);
  };

  const showMessage = (text: string, type: MessageState['type']) => {
    setMessage({ text, type });
    setTimeout(clearMessage, 5000);
  };

  const onFormSubmit = async (data: ProductFormData) => {
    setLoading(true);
    clearMessage();

    try {
      let productId: string;

      if (mode === 'create') {
        const response = await api.products.create(data as CreateProductData);
        productId = response.data.id;
        showMessage('Producto creado exitosamente', 'success');
      } else {
        productId = (initialData as any)?.id;
        if (!productId) {
          throw new Error('ID del producto requerido para actualización');
        }
        await api.products.update(productId, data as UpdateProductData);
        showMessage('Producto actualizado exitosamente', 'success');
      }

      // Handle image operations
      if (selectedImages.length > 0 || deletedImageIds.length > 0) {
        setUploadingImages(true);
        try {
          // Delete images that were marked for deletion
          for (const imageId of deletedImageIds) {
            await deleteProductImage(imageId);
          }

          // Upload new images if any
          if (selectedImages.length > 0) {
            const imageFiles = selectedImages.map(img => img.file);
            await uploadProductImages(productId, imageFiles);
          }

          showMessage('Producto e imágenes guardados exitosamente', 'success');
        } catch (imageError) {
          console.error('Error uploading images:', imageError);
          showMessage('Producto guardado pero falló la gestión de imágenes', 'error');
        } finally {
          setUploadingImages(false);
        }
      }

      if (onSubmit) {
        onSubmit(data);
      }

      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1000);
      }

      if (mode === 'create') {
        reset(defaultProductValues);
      }
    } catch (error) {
      console.error('Error al procesar producto:', error);

      let errorMessage = 'Error al procesar el producto';

      if (error instanceof Error) {
        errorMessage = error.message;
      }

      showMessage(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    reset();
    clearMessage();
    if (onCancel) {
      onCancel();
    }
  };

  const handleImageUpload = (images: ImageFile[]) => {
    // Validate files first
    const files = images.map(img => img.file);
    const errors = validateProductImageFiles(files, 5, 5 * 1024 * 1024);
    
    if (errors.length > 0) {
      showMessage(`Error en imágenes: ${errors.join(', ')}`, 'error');
      return;
    }

    // Add to selected images (avoiding duplicates)
    setSelectedImages(prevImages => {
      const newImages = [...prevImages];
      images.forEach(newImg => {
        // Check if file already exists
        const exists = newImages.some(existing => 
          existing.file.name === newImg.file.name && 
          existing.file.size === newImg.file.size
        );
        if (!exists) {
          newImages.push(newImg);
        }
      });
      return newImages.slice(0, 5); // Limit to 5 images
    });
  };

  const handleRemoveImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleDeleteExistingImage = (imageId: string) => {
    // Mark for deletion
    setDeletedImageIds(prev => [...prev, imageId]);
    // Remove from UI
    setExistingImages(prev => prev.filter(img => img.id !== imageId));
  };

  const categoryOptions = getCategoryOptions();

  return (
    <div className='product-form'>
      <div className='form-header mb-6'>
        <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
          {mode === 'create' ? 'Crear Nuevo Producto' : 'Editar Producto'}
        </h2>
      </div>

      {message && (
        <div className='p-4 rounded-lg mb-6 bg-green-50 border border-green-200 text-green-800'>
          <div className='flex'>
            <div className='flex-1'>{message.text}</div>
            <button onClick={clearMessage} className='ml-2'>
              ×
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onFormSubmit)} className='space-y-6'>
        <div>
          <label htmlFor='name' className='block text-sm font-medium mb-2'>
            Nombre del Producto *
          </label>
          <input
            id='name'
            type='text'
            {...register('name')}
            className='w-full px-3 py-2 border rounded-lg'
            placeholder='Ej: iPhone 14 Pro Max'
          />
          {errors.name && (
            <p className='mt-1 text-sm text-red-600'>
              {errors.name?.message as string}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor='description'
            className='block text-sm font-medium mb-2'
          >
            Descripción *
          </label>
          <textarea
            id='description'
            {...register('description')}
            rows={4}
            className='w-full px-3 py-2 border rounded-lg'
            placeholder='Describe las características principales...'
          />
          {errors.description && (
            <p className='mt-1 text-sm text-red-600'>
              {errors.description?.message as string}
            </p>
          )}
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <div>
            <label htmlFor='price' className='block text-sm font-medium mb-2'>
              Precio ($) *
            </label>
            <input
              id='price'
              type='number'
              step='0.01'
              min='0'
              max='999999'
              {...register('price')}
              className='w-full px-3 py-2 border rounded-lg'
              placeholder='0.00'
            />
            {errors.price && (
              <p className='mt-1 text-sm text-red-600'>
                {errors.price?.message as string}
              </p>
            )}
          </div>

          <div>
            <label htmlFor='stock' className='block text-sm font-medium mb-2'>
              Stock *
            </label>
            <input
              id='stock'
              type='number'
              min='0'
              {...register('stock')}
              className='w-full px-3 py-2 border rounded-lg'
              placeholder='0'
            />
            {errors.stock && (
              <p className='mt-1 text-sm text-red-600'>
                {errors.stock?.message as string}
              </p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor='category' className='block text-sm font-medium mb-2'>
            Categoría *
          </label>
          <select
            id='category'
            {...register('category')}
            className='w-full px-3 py-2 border rounded-lg'
          >
            <option value=''>Selecciona una categoría</option>
            {categoryOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.category && (
            <p className='mt-1 text-sm text-red-600'>
              {errors.category?.message as string}
            </p>
          )}
        </div>

        {/* Image Upload Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Imágenes del Producto</h3>

          {/* Show existing images in edit mode */}
          {mode === 'edit' && (
            <div>
              {loadingExistingImages ? (
                <div className="flex items-center justify-center py-8 border rounded-lg">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Cargando imágenes existentes...</span>
                </div>
              ) : existingImages.length > 0 ? (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    Imágenes actuales ({existingImages.length})
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    {existingImages.map((image) => (
                      <div key={image.id} className="relative group">
                        <img
                          src={image.public_url}
                          alt={image.original_filename}
                          className="w-full h-32 object-cover rounded-lg border border-gray-200"
                        />
                        <button
                          type="button"
                          onClick={() => handleDeleteExistingImage(image.id)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100"
                          disabled={loading || uploadingImages}
                        >
                          <X className="w-4 h-4" />
                        </button>
                        <div className="absolute bottom-1 left-1 bg-black bg-opacity-50 text-white text-xs px-1 rounded">
                          {Math.round(image.file_size / 1024)}KB
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500 mb-4">No hay imágenes existentes</p>
              )}
            </div>
          )}

          {/* Upload new images */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              {mode === 'edit' ? 'Agregar nuevas imágenes' : 'Imágenes del producto'}
            </h4>
            <ImageUpload
              onImageUpload={handleImageUpload}
              maxFiles={5 - existingImages.length}
              maxSize={5 * 1024 * 1024} // 5MB
              acceptedTypes={['image/jpeg', 'image/png', 'image/webp', 'image/gif']}
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-gray-400 transition-colors"
              showPreview={false}
              disabled={loading || uploadingImages || (existingImages.length >= 5)}
            />
          </div>

          {/* Preview of selected new images */}
          {selectedImages.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                Nuevas imágenes seleccionadas ({selectedImages.length})
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {selectedImages.map((imageFile, index) => (
                  <div key={`${imageFile.file.name}-${index}`} className="relative group">
                    <img
                      src={imageFile.preview}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg border border-gray-200"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition-colors"
                      disabled={loading || uploadingImages}
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <div className="absolute bottom-1 left-1 bg-black bg-opacity-50 text-white text-xs px-1 rounded">
                      {Math.round(imageFile.file.size / 1024)}KB
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-sm text-gray-500">
            Máximo 5 imágenes total (JPG, PNG, WebP, GIF). Máximo 5MB por imagen.
            {existingImages.length > 0 && (
              <span className="block">
                Tienes {existingImages.length} imagen(es) existente(s). 
                Puedes agregar {5 - existingImages.length} más.
              </span>
            )}
          </p>
        </div>

        {/* SKU Field */}
        <div>
          <label htmlFor='sku' className='block text-sm font-medium mb-2'>
            SKU (Opcional)
          </label>
          <input
            id='sku'
            type='text'
            {...register('sku')}
            className='w-full px-3 py-2 border rounded-lg'
            placeholder='Ej: PROD-001'
          />
          {errors.sku && (
            <p className='mt-1 text-sm text-red-600'>
              {errors.sku?.message as string}
            </p>
          )}
        </div>

        {/* Dimensions Fields */}
        <div>
          <label className='block text-sm font-medium mb-2'>
            Dimensiones (Opcional)
          </label>
          <div className='grid grid-cols-4 gap-2'>
            <input
              placeholder='Largo'
              type='number'
              {...register('dimensions.length')}
              className='px-3 py-2 border rounded-lg'
            />
            <input
              placeholder='Ancho'
              type='number'
              {...register('dimensions.width')}
              className='px-3 py-2 border rounded-lg'
            />
            <input
              placeholder='Alto'
              type='number'
              {...register('dimensions.height')}
              className='px-3 py-2 border rounded-lg'
            />
            <select
              {...register('dimensions.unit')}
              className='px-3 py-2 border rounded-lg'
            >
              <option value=''>Unidad</option>
              <option value='cm'>cm</option>
              <option value='m'>m</option>
              <option value='mm'>mm</option>
            </select>
          </div>
        </div>

        {/* Weight Fields */}
        <div>
          <label className='block text-sm font-medium mb-2'>
            Peso (Opcional)
          </label>
          <div className='grid grid-cols-2 gap-2'>
            <input
              placeholder='Peso'
              type='number'
              {...register('weight.value')}
              className='px-3 py-2 border rounded-lg'
            />
            <select
              {...register('weight.unit')}
              className='px-3 py-2 border rounded-lg'
            >
              <option value=''>Unidad</option>
              <option value='g'>g</option>
              <option value='kg'>kg</option>
              <option value='lb'>lb</option>
            </select>
          </div>
        </div>
        <div className='flex gap-3 pt-6'>
          <button
            type='submit'
            disabled={loading || uploadingImages || !isValid}
            className='flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg disabled:bg-gray-300 flex items-center justify-center'
          >
            {uploadingImages ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Subiendo imágenes...
              </>
            ) : loading ? (
              'Procesando...'
            ) : mode === 'create' ? (
              'Crear Producto'
            ) : (
              'Actualizar Producto'
            )}
          </button>

          <button
            type='button'
            onClick={handleCancel}
            disabled={loading || uploadingImages}
            className='px-6 py-3 border text-gray-700 rounded-lg disabled:opacity-50'
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;
