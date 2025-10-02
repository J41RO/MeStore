/**
 * ProductForm - Comprehensive product creation/editing form
 *
 * Features:
 * - React Hook Form with validation
 * - Image upload with preview and management
 * - Real-time inventory tracking setup
 * - Category selection and management
 * - Price and stock management
 * - Product status controls (active/inactive/draft)
 * - Colombian peso formatting
 * - Accessibility support (ARIA labels)
 * - Responsive design for mobile/desktop
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useProductStore } from '../../stores/productStore.new';
import { useCategoryStore } from '../../stores/categoryStore';
import {
  PhotoIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  CubeIcon,
  TagIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Product, CreateProductRequest, UpdateProductRequest } from '../../types';

interface ProductFormProps {
  product?: Product | null;
  onSubmit: () => void;
  onCancel: () => void;
}

/**
 * Form data interface
 */
interface ProductFormData {
  name: string;
  description: string;
  price: number;
  category_id: string;
  sku: string;
  stock_quantity: number;
  low_stock_threshold: number;
  weight?: number;
  dimensions?: string;
  is_active: boolean;
  is_featured: boolean;
  tags: string;
  meta_title?: string;
  meta_description?: string;
}

/**
 * Image upload interface
 */
interface ImageUpload {
  id: string;
  file?: File;
  url: string;
  isUploading: boolean;
  uploadProgress: number;
  error?: string;
}

/**
 * Image upload component
 */
interface ImageUploadAreaProps {
  images: ImageUpload[];
  onImagesChange: (images: ImageUpload[]) => void;
  maxImages?: number;
}

const ImageUploadArea: React.FC<ImageUploadAreaProps> = ({
  images,
  onImagesChange,
  maxImages = 10,
}) => {
  const [dragOver, setDragOver] = useState(false);

  /**
   * Handle file selection
   */
  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newImages: ImageUpload[] = [];
    Array.from(files).forEach((file, index) => {
      if (images.length + newImages.length >= maxImages) return;

      if (file.type.startsWith('image/')) {
        const imageId = `new-${Date.now()}-${index}`;
        const imageUrl = URL.createObjectURL(file);

        newImages.push({
          id: imageId,
          file,
          url: imageUrl,
          isUploading: false,
          uploadProgress: 0,
        });
      }
    });

    onImagesChange([...images, ...newImages]);
  };

  /**
   * Handle drag and drop
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  /**
   * Remove image
   */
  const handleRemoveImage = (imageId: string) => {
    const updatedImages = images.filter(img => img.id !== imageId);
    onImagesChange(updatedImages);
  };

  /**
   * Move image position
   */
  const handleMoveImage = (fromIndex: number, toIndex: number) => {
    const updatedImages = [...images];
    const [movedImage] = updatedImages.splice(fromIndex, 1);
    updatedImages.splice(toIndex, 0, movedImage);
    onImagesChange(updatedImages);
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragOver
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <label htmlFor="image-upload" className="cursor-pointer">
            <span className="text-sm font-medium text-blue-600 hover:text-blue-500">
              Seleccionar imágenes
            </span>
            <input
              id="image-upload"
              type="file"
              multiple
              accept="image/*"
              className="sr-only"
              onChange={(e) => handleFileSelect(e.target.files)}
            />
          </label>
          <p className="text-sm text-gray-500 mt-1">
            o arrastra y suelta aquí
          </p>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          PNG, JPG, GIF hasta 10MB. Máximo {maxImages} imágenes.
        </p>
      </div>

      {/* Image Preview Grid */}
      {images.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <div key={image.id} className="relative group">
              <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={image.url}
                  alt={`Producto ${index + 1}`}
                  className="w-full h-full object-cover"
                />

                {/* Upload Progress */}
                {image.isUploading && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-white rounded-lg p-3">
                      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <p className="text-xs text-gray-600">{image.uploadProgress}%</p>
                    </div>
                  </div>
                )}

                {/* Error State */}
                {image.error && (
                  <div className="absolute inset-0 bg-red-500 bg-opacity-50 flex items-center justify-center">
                    <ExclamationTriangleIcon className="w-8 h-8 text-white" />
                  </div>
                )}

                {/* Primary Image Badge */}
                {index === 0 && (
                  <div className="absolute top-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                    Principal
                  </div>
                )}

                {/* Remove Button */}
                <button
                  onClick={() => handleRemoveImage(image.id)}
                  className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <XMarkIcon className="w-4 h-4" />
                </button>

                {/* Move Buttons */}
                <div className="absolute bottom-2 left-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {index > 0 && (
                    <button
                      onClick={() => handleMoveImage(index, index - 1)}
                      className="bg-gray-800 text-white text-xs px-2 py-1 rounded"
                    >
                      ←
                    </button>
                  )}
                  {index < images.length - 1 && (
                    <button
                      onClick={() => handleMoveImage(index, index + 1)}
                      className="bg-gray-800 text-white text-xs px-2 py-1 rounded"
                    >
                      →
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Main ProductForm component
 */
const ProductForm: React.FC<ProductFormProps> = ({
  product,
  onSubmit,
  onCancel,
}) => {
  // Store hooks
  const { createProduct, updateProduct, isCreating, isUpdating, createError, updateError } = useProductStore();
  const { categories, fetchCategories } = useCategoryStore();

  // Form setup
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isDirty },
    reset,
    watch,
    setValue,
  } = useForm<ProductFormData>({
    defaultValues: {
      name: product?.name || '',
      description: product?.description || '',
      price: product?.price || 0,
      category_id: product?.category_id || '',
      sku: product?.sku || '',
      stock_quantity: product?.stock_quantity || 0,
      low_stock_threshold: product?.low_stock_threshold || 10,
      weight: product?.weight || undefined,
      dimensions: product?.dimensions || '',
      is_active: product?.is_active ?? true,
      is_featured: product?.is_featured ?? false,
      tags: product?.tags?.join(', ') || '',
      meta_title: product?.meta_title || '',
      meta_description: product?.meta_description || '',
    },
  });

  // Local state
  const [images, setImages] = useState<ImageUpload[]>([]);
  const [initialImages, setInitialImages] = useState<ImageUpload[]>([]); // Track original images
  const [activeTab, setActiveTab] = useState<'basic' | 'inventory' | 'seo'>('basic');
  const [isSaving, setIsSaving] = useState(false);

  // Watch form values for dynamic updates
  const watchPrice = watch('price');
  const watchStock = watch('stock_quantity');
  const watchLowStockThreshold = watch('low_stock_threshold');

  /**
   * Initialize form and load product images in edit mode
   */
  useEffect(() => {
    console.log('🔄 ProductForm useEffect ejecutado');
    console.log('📦 product:', product);
    console.log('🆔 product?.id:', product?.id);
    console.log('🖼️ product?.images:', product?.images);

    fetchCategories();

    // Load existing images when editing a product
    const loadProductImages = async () => {
      if (product?.id) {
        console.log('✅ MODO EDICIÓN DETECTADO - ID:', product.id);

        try {
          const token = localStorage.getItem('authToken') || localStorage.getItem('token') || '';
          console.log('🔑 Token encontrado:', token ? 'Sí (' + token.substring(0, 20) + '...)' : 'No');

          const url = `http://192.168.1.137:8000/api/v1/products/${product.id}/imagenes`;
          console.log('📡 Haciendo GET a:', url);

          // Fetch images from backend
          const response = await fetch(url, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          console.log('📥 Response status:', response.status);

          if (response.ok) {
            const imagesData = await response.json();
            console.log('✅ Imágenes cargadas para producto:', product.id);
            console.log('📸 Total imágenes:', imagesData.length);
            console.log('🖼️ Datos de imágenes:', imagesData);

            // Map backend images to ImageUpload format
            const productImages: ImageUpload[] = imagesData.map((img: any, index: number) => ({
              id: img.id, // Use the actual backend image ID
              url: img.public_url || img.url,
              isUploading: false,
              uploadProgress: 100,
            }));

            console.log('🎨 Imágenes mapeadas:', productImages);
            setImages(productImages);
            setInitialImages(productImages); // Store initial state to detect deletions
            console.log('✅ State de imágenes actualizado');
          } else {
            const errorText = await response.text();
            console.warn('⚠️ No se pudieron cargar las imágenes del producto');
            console.warn('⚠️ Response status:', response.status);
            console.warn('⚠️ Response body:', errorText);
          }
        } catch (error) {
          console.error('❌ Error cargando imágenes del producto:', error);
        }
      } else {
        console.log('➕ MODO CREAR - No hay product.id');
      }
    };

    loadProductImages();
  }, [fetchCategories, product]);

  /**
   * Generate SKU automatically
   */
  const generateSKU = useCallback(() => {
    const name = watch('name');
    if (name) {
      const sku = name
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, '')
        .substring(0, 8) +
        Date.now().toString().slice(-4);
      setValue('sku', sku);
    }
  }, [watch, setValue]);

  /**
   * Handle form submission
   */
  const onFormSubmit = async (data: ProductFormData) => {
    setIsSaving(true);

    try {
      // Prepare product data (without images - those are handled separately)
      const productData = {
        ...data,
        tags: data.tags ? data.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
      };

      let success = false;
      let productId: string;

      if (product) {
        // Update existing product
        const updateData: UpdateProductRequest = {
          id: product.id,
          ...productData,
        };
        const result = await updateProduct(product.id, updateData);
        success = !!result;
        productId = product.id;
        console.log('✅ Producto actualizado:', productId);
      } else {
        // Create new product
        const createData: CreateProductRequest = productData as CreateProductRequest;
        const result = await createProduct(createData);
        success = !!result;
        productId = result?.id || '';
        console.log('✅ Producto creado:', productId);
      }

      // Handle image operations (delete removed images, upload new ones)
      if (success && productId && product) { // Only for edit mode
        const token = localStorage.getItem('authToken') || localStorage.getItem('token') || '';

        // 1. Delete removed images
        const currentImageIds = images.map(img => img.id);
        const deletedImages = initialImages.filter(img => !currentImageIds.includes(img.id));

        for (const deletedImage of deletedImages) {
          try {
            console.log('🗑️ Eliminando imagen:', deletedImage.id);
            const deleteResponse = await fetch(
              `http://192.168.1.137:8000/api/v1/products/imagenes/${deletedImage.id}`,
              {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              }
            );

            if (deleteResponse.ok) {
              console.log('✅ Imagen eliminada:', deletedImage.id);
            } else {
              console.error('❌ Error eliminando imagen:', await deleteResponse.text());
            }
          } catch (error) {
            console.error('❌ Error en DELETE imagen:', error);
          }
        }

        // 2. Upload new images
        const newImages = images.filter(img => img.file); // Images with file property are new

        if (newImages.length > 0) {
          console.log('📤 Subiendo', newImages.length, 'imágenes nuevas...');

          const formData = new FormData();
          newImages.forEach(img => {
            if (img.file) {
              formData.append('files', img.file);
            }
          });

          const uploadResponse = await fetch(
            `http://192.168.1.137:8000/api/v1/products/${productId}/imagenes`,
            {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
              body: formData,
            }
          );

          if (uploadResponse.ok) {
            const uploadResult = await uploadResponse.json();
            console.log('✅ Imágenes subidas exitosamente:', uploadResult);
          } else {
            console.error('❌ Error subiendo imágenes:', await uploadResponse.text());
          }
        }
      } else if (success && productId && !product) {
        // Create mode - just upload images
        const newImages = images.filter(img => img.file);

        if (newImages.length > 0) {
          console.log('📤 Subiendo', newImages.length, 'imágenes para producto nuevo...');

          const formData = new FormData();
          newImages.forEach(img => {
            if (img.file) {
              formData.append('files', img.file);
            }
          });

          const token = localStorage.getItem('authToken') || localStorage.getItem('token') || '';
          const uploadResponse = await fetch(
            `http://192.168.1.137:8000/api/v1/products/${productId}/imagenes`,
            {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
              body: formData,
            }
          );

          if (uploadResponse.ok) {
            const uploadResult = await uploadResponse.json();
            console.log('✅ Imágenes subidas exitosamente:', uploadResult);
          } else {
            console.error('❌ Error subiendo imágenes:', await uploadResponse.text());
          }
        }
      }

      if (success) {
        onSubmit();
      }
    } catch (error) {
      console.error('❌ Error en form submission:', error);
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Format price display
   */
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const currentError = createError || updateError;
  const isSubmitting = isCreating || isUpdating || isSaving;
  const isEditMode = !!product; // Determine if we're editing

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {product ? 'Editar Producto' : 'Agregar Producto'}
          </h2>
          <p className="text-gray-600 mt-1">
            {product ? 'Actualiza la información de tu producto' : 'Completa la información para agregar un nuevo producto'}
          </p>
        </div>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XMarkIcon className="w-6 h-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)}>
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'basic', name: 'Información Básica', icon: TagIcon },
              { id: 'inventory', name: 'Inventario', icon: CubeIcon },
              { id: 'seo', name: 'SEO y Marketing', icon: InformationCircleIcon },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Form Content */}
        <div className="p-6 space-y-8">
          {/* Error Display */}
          {currentError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-800">{currentError}</p>
                </div>
              </div>
            </div>
          )}

          {/* Basic Information Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              {/* Product Images */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Imágenes del Producto
                </label>
                <ImageUploadArea
                  images={images}
                  onImagesChange={setImages}
                  maxImages={10}
                />
              </div>

              {/* Product Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Producto *
                </label>
                <input
                  {...register('name', {
                    required: 'El nombre del producto es obligatorio',
                    minLength: {
                      value: 3,
                      message: 'El nombre debe tener al menos 3 caracteres'
                    },
                    maxLength: {
                      value: 200,
                      message: 'El nombre no puede exceder 200 caracteres'
                    }
                  })}
                  type="text"
                  className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Ej: Camiseta de algodón premium para hombre"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Descripción
                </label>
                <textarea
                  {...register('description', {
                    maxLength: {
                      value: 1000,
                      message: 'La descripción no puede exceder 1000 caracteres'
                    }
                  })}
                  rows={4}
                  className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.description ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Describe las características, materiales, uso recomendado..."
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>

              {/* Price and Category Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Price */}
                <div>
                  <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-2">
                    Precio (COP) *
                  </label>
                  <div className="relative">
                    <CurrencyDollarIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      {...register('price', {
                        required: 'El precio es obligatorio',
                        min: {
                          value: 1,
                          message: 'El precio debe ser mayor a 0'
                        },
                        max: {
                          value: 999999999,
                          message: 'El precio es demasiado alto'
                        }
                      })}
                      type="number"
                      step="1"
                      min="1"
                      className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        errors.price ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="50000"
                    />
                  </div>
                  {watchPrice > 0 && (
                    <p className="mt-1 text-sm text-gray-600">
                      Precio formateado: {formatPrice(watchPrice)}
                    </p>
                  )}
                  {errors.price && (
                    <p className="mt-1 text-sm text-red-600">{errors.price.message}</p>
                  )}
                </div>

                {/* Category */}
                <div>
                  <label htmlFor="category_id" className="block text-sm font-medium text-gray-700 mb-2">
                    Categoría *
                  </label>
                  <select
                    {...register('category_id', {
                      required: 'La categoría es obligatoria'
                    })}
                    className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.category_id ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Selecciona una categoría</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  {errors.category_id && (
                    <p className="mt-1 text-sm text-red-600">{errors.category_id.message}</p>
                  )}
                </div>
              </div>

              {/* SKU and Tags Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* SKU */}
                <div>
                  <label htmlFor="sku" className="block text-sm font-medium text-gray-700 mb-2">
                    SKU (Código del Producto)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      {...register('sku', {
                        pattern: {
                          value: /^[A-Z0-9-_]+$/,
                          message: 'El SKU solo puede contener letras mayúsculas, números, guiones y guiones bajos'
                        }
                      })}
                      type="text"
                      className={`flex-1 px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        errors.sku ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Ej: CAM-ALG-001"
                    />
                    <button
                      type="button"
                      onClick={generateSKU}
                      className="px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                    >
                      Generar
                    </button>
                  </div>
                  {errors.sku && (
                    <p className="mt-1 text-sm text-red-600">{errors.sku.message}</p>
                  )}
                </div>

                {/* Tags */}
                <div>
                  <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
                    Etiquetas
                  </label>
                  <input
                    {...register('tags')}
                    type="text"
                    className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="algodón, casual, hombre (separadas por comas)"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Separa las etiquetas con comas. Ayudan a los compradores a encontrar tu producto.
                  </p>
                </div>
              </div>

              {/* Status Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center">
                    <Controller
                      name="is_active"
                      control={control}
                      render={({ field }) => (
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={field.onChange}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      )}
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      Producto activo (visible para compradores)
                    </label>
                  </div>

                  <div className="flex items-center">
                    <Controller
                      name="is_featured"
                      control={control}
                      render={({ field }) => (
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={field.onChange}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      )}
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      Producto destacado (aparece en secciones especiales)
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Inventory Tab */}
          {activeTab === 'inventory' && (
            <div className="space-y-6">
              {/* Stock Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Stock Quantity */}
                <div>
                  <label htmlFor="stock_quantity" className="block text-sm font-medium text-gray-700 mb-2">
                    Cantidad en Stock *
                  </label>
                  <input
                    {...register('stock_quantity', {
                      required: 'La cantidad en stock es obligatoria',
                      min: {
                        value: 0,
                        message: 'La cantidad no puede ser negativa'
                      }
                    })}
                    type="number"
                    min="0"
                    className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.stock_quantity ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="100"
                  />
                  {errors.stock_quantity && (
                    <p className="mt-1 text-sm text-red-600">{errors.stock_quantity.message}</p>
                  )}
                </div>

                {/* Low Stock Threshold */}
                <div>
                  <label htmlFor="low_stock_threshold" className="block text-sm font-medium text-gray-700 mb-2">
                    Alerta de Stock Bajo
                  </label>
                  <input
                    {...register('low_stock_threshold', {
                      min: {
                        value: 1,
                        message: 'El umbral debe ser al menos 1'
                      }
                    })}
                    type="number"
                    min="1"
                    className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.low_stock_threshold ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="10"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Te alertaremos cuando el stock llegue a este nivel
                  </p>
                  {errors.low_stock_threshold && (
                    <p className="mt-1 text-sm text-red-600">{errors.low_stock_threshold.message}</p>
                  )}
                </div>
              </div>

              {/* Stock Status Display */}
              {watchStock !== undefined && watchLowStockThreshold && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Estado del Inventario</h4>
                  <div className="flex items-center space-x-4">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      watchStock === 0
                        ? 'bg-red-100 text-red-800'
                        : watchStock <= watchLowStockThreshold
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {watchStock === 0
                        ? 'Sin stock'
                        : watchStock <= watchLowStockThreshold
                        ? 'Stock bajo'
                        : 'En stock'
                      }
                    </div>
                    <span className="text-sm text-gray-600">
                      {watchStock} unidades disponibles
                    </span>
                  </div>
                </div>
              )}

              {/* Physical Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Weight */}
                <div>
                  <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-2">
                    Peso (gramos)
                  </label>
                  <input
                    {...register('weight', {
                      min: {
                        value: 0,
                        message: 'El peso no puede ser negativo'
                      }
                    })}
                    type="number"
                    min="0"
                    step="0.1"
                    className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.weight ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="500"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Usado para calcular costos de envío
                  </p>
                  {errors.weight && (
                    <p className="mt-1 text-sm text-red-600">{errors.weight.message}</p>
                  )}
                </div>

                {/* Dimensions */}
                <div>
                  <label htmlFor="dimensions" className="block text-sm font-medium text-gray-700 mb-2">
                    Dimensiones (cm)
                  </label>
                  <input
                    {...register('dimensions')}
                    type="text"
                    className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="30 x 20 x 5"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Formato: Largo x Ancho x Alto
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SEO Tab */}
          {activeTab === 'seo' && (
            <div className="space-y-6">
              {/* Meta Title */}
              <div>
                <label htmlFor="meta_title" className="block text-sm font-medium text-gray-700 mb-2">
                  Título SEO
                </label>
                <input
                  {...register('meta_title', {
                    maxLength: {
                      value: 60,
                      message: 'El título SEO no debe exceder 60 caracteres'
                    }
                  })}
                  type="text"
                  className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.meta_title ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Título optimizado para motores de búsqueda"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Recomendado: 50-60 caracteres. Aparece en los resultados de búsqueda.
                </p>
                {errors.meta_title && (
                  <p className="mt-1 text-sm text-red-600">{errors.meta_title.message}</p>
                )}
              </div>

              {/* Meta Description */}
              <div>
                <label htmlFor="meta_description" className="block text-sm font-medium text-gray-700 mb-2">
                  Descripción SEO
                </label>
                <textarea
                  {...register('meta_description', {
                    maxLength: {
                      value: 160,
                      message: 'La descripción SEO no debe exceder 160 caracteres'
                    }
                  })}
                  rows={3}
                  className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.meta_description ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Descripción que aparecerá en los resultados de búsqueda..."
                />
                <p className="mt-1 text-xs text-gray-500">
                  Recomendado: 150-160 caracteres. Describe brevemente el producto.
                </p>
                {errors.meta_description && (
                  <p className="mt-1 text-sm text-red-600">{errors.meta_description.message}</p>
                )}
              </div>

              {/* SEO Tips */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Consejos SEO</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Incluye palabras clave relevantes en el título y descripción</li>
                  <li>• Usa títulos únicos y descriptivos para cada producto</li>
                  <li>• Las etiquetas ayudan a categorizar mejor tu producto</li>
                  <li>• Imágenes con nombres descriptivos mejoran el SEO</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-4">
            {isDirty && (
              <div className="flex items-center text-amber-600">
                <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
                <span className="text-sm">Tienes cambios sin guardar</span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {isSubmitting && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              )}
              <span>
                {isSubmitting
                  ? (product ? 'Actualizando...' : 'Creando...')
                  : (product ? 'Actualizar Producto' : 'Crear Producto')
                }
              </span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;