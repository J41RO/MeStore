import React, { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { X, CheckCircle, AlertTriangle } from 'lucide-react';
import {
  createProductSchema,
  updateProductSchema,
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
import { debounce } from 'lodash';
import FormField from './FormField';
import NumberField from './NumberField';
import SelectField from './SelectField';
import TextAreaField from './TextAreaField';

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

interface ValidationState {
  nameAvailable: boolean | null;
  priceReasonable: boolean | null;
  dimensionsValid: boolean | null;
  marginHealthy: boolean | null;
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
  const [validationState, setValidationState] = useState<ValidationState>({
    nameAvailable: null,
    priceReasonable: null,
    dimensionsValid: null,
    marginHealthy: null
  });

  // Seleccionar schema según el modo
  const schema = mode === 'edit' ? updateProductSchema : createProductSchema;

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    setValue,
    watch,
    trigger,
  } = useForm<ProductFormData>({
    resolver: yupResolver(schema) as any,
    mode: 'onChange', // Validación en tiempo real
    defaultValues: {
      ...defaultProductValues,
      ...initialData,
      id: initialData?.id || undefined,
    } as ProductFormData,
  });

  // Watch para validaciones dependientes
  const precioVenta = watch('precio_venta');
  const precioCosto = watch('precio_costo');
  const watchedName = watch('name');
  const watchedDimensions = watch(['largo', 'ancho', 'alto', 'peso']);

  // Validación asíncrona de nombre único
  const checkNameAvailability = useCallback(
    debounce(async (name: string) => {
      if (name.length < 3) return;
      
      try {
        const response = await fetch(`/api/v1/products/check-name?name=${encodeURIComponent(name)}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        const { available } = await response.json();
        setValidationState(prev => ({ ...prev, nameAvailable: available }));
      } catch (error) {
        console.error('Error checking name availability:', error);
      }
    }, 500),
    []
  );

  // Validación de dimensiones vs peso
  const validateDimensions = useCallback((largo: number, ancho: number, alto: number, peso: number) => {
    const volumen = largo * ancho * alto; // cm³
    const densidad = peso / (volumen / 1000000); // kg/m³
    
    const isReasonable = densidad > 0.1 && densidad < 10000; // Rango razonable
    setValidationState(prev => ({ ...prev, dimensionsValid: isReasonable }));
    
    return isReasonable;
  }, []);

  // Validación de margen de ganancia
  const validateMargin = useCallback((precioVenta: number, precioCosto: number) => {
    if (!precioVenta || !precioCosto) return true;
    
    const margen = ((precioVenta - precioCosto) / precioVenta) * 100;
    const isHealthy = margen >= 10 && margen <= 80;
    
    setValidationState(prev => ({ ...prev, marginHealthy: isHealthy }));
    return isHealthy;
  }, []);

  useEffect(() => {
    if (mode === 'edit' && initialData) {
      Object.entries(initialData).forEach(([key, value]) => {
        setValue(key as keyof ProductFormData, value);
      });
    }
  }, [mode, initialData, setValue]);

  // Watchers para validaciones en tiempo real
  useEffect(() => {
    if (watchedName) {
      checkNameAvailability(watchedName);
    }
  }, [watchedName, checkNameAvailability]);

  useEffect(() => {
    const [largo, ancho, alto, peso] = watchedDimensions;
    if (largo && ancho && alto && peso) {
      validateDimensions(largo, ancho, alto, peso);
    }
  }, [watchedDimensions, validateDimensions]);

  // Validación de margen en tiempo real
  useEffect(() => {
    if (precioVenta && precioCosto) {
      validateMargin(precioVenta, precioCosto);
      
      const margen = ((precioVenta - precioCosto) / precioVenta) * 100;
      if (margen < 10) {
        showMessage('Margen de ganancia es menor al 10%', 'info');
      }
    }
  }, [precioVenta, precioCosto, validateMargin]);

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
      // Validación final antes de envío
      const isFormValid = await trigger();
      if (!isFormValid) return;

      // Transform form data to API format
      const apiData: CreateProductData = {
        name: data.name,
        description: data.description,
        price: data.precio_venta, // Transform precio_venta to price
        stock: data.stock,
        category: data.category,
        sku: data.sku,
        dimensions: {
          length: data.largo,
          width: data.ancho,
          height: data.alto,
          unit: 'cm'
        },
        weight: {
          value: data.peso,
          unit: 'kg'
        }
      };

      let productId: string;

      if (mode === 'create') {
        const response = await api.products.create(apiData);
        productId = response.data.id;
        showMessage('Producto creado exitosamente', 'success');
      } else {
        const productIdString = (initialData as any)?.id;
        if (!productIdString) {
          throw new Error('ID del producto requerido para actualización');
        }
        const updateData: UpdateProductData = {
          ...apiData,
          id: parseInt(productIdString, 10)
        };
        await api.products.update(productIdString, updateData);
        productId = productIdString;
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
        reset(defaultProductValues as ProductFormData);
        setSelectedImages([]);
        setExistingImages([]);
        setDeletedImageIds([]);
        // Limpiar estados de validación
        setValidationState({
          nameAvailable: null,
          priceReasonable: null,
          dimensionsValid: null,
          marginHealthy: null
        });
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

      <form onSubmit={handleSubmit(onFormSubmit as any)} className='space-y-6'>
        {/* Campo nombre con validación asíncrona */}
        <div className="space-y-1">
          <FormField
            label="Nombre del Producto"
            name="name"
            register={register}
            error={errors.name?.message}
            placeholder="Ej: iPhone 14 Pro Max"
            required
            helpText="Nombre único y descriptivo del producto"
          />
          {validationState.nameAvailable === false && (
            <p className="text-sm text-amber-600 flex items-center animate-fade-in">
              <AlertTriangle className="w-4 h-4 mr-1" />
              Este nombre ya está en uso
            </p>
          )}
          {validationState.nameAvailable === true && (
            <p className="text-sm text-green-600 flex items-center animate-fade-in">
              <CheckCircle className="w-4 h-4 mr-1" />
              Nombre disponible
            </p>
          )}
        </div>

        {/* Campo descripción con contador de caracteres */}
        <TextAreaField
          label="Descripción"
          name="description"
          register={register}
          error={errors.description?.message}
          placeholder="Describe las características principales del producto..."
          required
          rows={4}
          maxLength={1000}
          showCharCount
          watch={watch}
          helpText="Descripción detallada que ayude a los clientes a entender el producto"
        />

        {/* Campos de pricing */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <NumberField
            label="Precio de Venta"
            name="precio_venta"
            register={register}
            error={errors.precio_venta?.message}
            min={1000}
            max={50000000}
            currency
            placeholder="0.00"
            required
            helpText="Precio al cual se venderá el producto (COP)"
          />

          <NumberField
            label="Precio de Costo"
            name="precio_costo"
            register={register}
            error={errors.precio_costo?.message}
            min={1}
            max={49999999}
            currency
            placeholder="0.00"
            required
            helpText="Precio de adquisición o costo del producto"
          />
        </div>

        {/* Indicador de margen de ganancia */}
        {precioVenta && precioCosto && (
          <div className="bg-gray-50 p-4 rounded-lg border">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Análisis de Precio</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Margen de ganancia:</span>
                <span className={`text-sm font-medium ${
                  validationState.marginHealthy ? 'text-green-600' : 'text-amber-600'
                }`}>
                  {(((precioVenta - precioCosto) / precioVenta) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Ganancia por unidad:</span>
                <span className="text-sm font-medium text-gray-900">
                  ${(precioVenta - precioCosto).toLocaleString()} COP
                </span>
              </div>
              {!validationState.marginHealthy && (
                <p className="text-sm text-amber-600 flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-1" />
                  Margen recomendado entre 10% y 80%
                </p>
              )}
            </div>
          </div>
        )}

        {/* Campos básicos */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <SelectField
            label="Categoría"
            name="category"
            register={register}
            error={errors.category?.message}
            options={categoryOptions}
            placeholder="Selecciona una categoría"
            required
            helpText="Categoría principal del producto"
          />

          <NumberField
            label="Stock Inicial"
            name="stock"
            register={register}
            error={errors.stock?.message}
            min={0}
            max={100000}
            step={1}
            unit="unidades"
            placeholder="0"
            required
            helpText="Cantidad inicial en inventario"
          />
        </div>

        {/* Campos de dimensiones físicas */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Dimensiones y Peso</h3>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
            <NumberField
              label="Largo"
              name="largo"
              register={register}
              error={errors.largo?.message}
              min={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Ancho"
              name="ancho"
              register={register}
              error={errors.ancho?.message}
              min={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Alto"
              name="alto"
              register={register}
              error={errors.alto?.message}
              min={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Peso"
              name="peso"
              register={register}
              error={errors.peso?.message}
              min={0.01}
              max={1000}
              unit="kg"
              placeholder="0.00"
              required
            />
          </div>
          
          {/* Validación de coherencia de dimensiones */}
          {watchedDimensions.every(val => val && val > 0) && (
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>Volumen calculado:</strong> {(watchedDimensions[0] * watchedDimensions[1] * watchedDimensions[2]).toLocaleString()} cm³
              </p>
              {validationState.dimensionsValid === false && (
                <p className="text-sm text-amber-600 flex items-center mt-1">
                  <AlertTriangle className="w-4 h-4 mr-1" />
                  Las dimensiones y peso parecen inconsistentes
                </p>
              )}
            </div>
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
        <FormField
          label="SKU (Opcional)"
          name="sku"
          register={register}
          error={errors.sku?.message}
          placeholder="Ej: PROD-001"
          helpText="Código único de producto"
        />
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
