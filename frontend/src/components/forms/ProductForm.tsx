import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
  const watchedDescription = watch('description');
  const watchedCategory = watch('category');
  const watchedPrecioVenta = watch('precio_venta');
  const watchedPrecioCosto = watch('precio_costo');
  const watchedStock = watch('stock');
  const watchedPeso = watch('peso');
  const watchedDimensions = watch(['largo', 'ancho', 'alto', 'peso']);

  // Cálculo de validación personalizado (consistente con checklist)
  const isFormValid = useMemo(() => {
    const requiredFields = [
      { name: 'name', value: watchedName, minLength: 3 },
      { name: 'description', value: watchedDescription, minLength: 10 },
      { name: 'category', value: watchedCategory },
      { name: 'precio_venta', value: watchedPrecioVenta, minValue: 1000 },
      { name: 'precio_costo', value: watchedPrecioCosto, minValue: 1 },
      { name: 'stock', value: watchedStock, minValue: 0 },
      { name: 'peso', value: watchedPeso, minValue: 0.01 }
    ];

    const allFieldsValid = requiredFields.every(field => {
      if (errors[field.name]) return false;
      if (!field.value && field.value !== 0) return false;
      if (field.minLength && field.value.length < field.minLength) return false;
      if (field.minValue && field.value < field.minValue) return false;
      return true;
    });

    // Validación adicional: precio_costo debe ser menor que precio_venta
    const pricesValid = watchedPrecioCosto && watchedPrecioVenta && watchedPrecioCosto < watchedPrecioVenta;

    return allFieldsValid && pricesValid;
  }, [
    errors,
    watchedName,
    watchedDescription,
    watchedCategory,
    watchedPrecioVenta,
    watchedPrecioCosto,
    watchedStock,
    watchedPeso
  ]);

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
    <div className='product-form bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen p-6 rounded-xl'>
      <div className='form-header mb-8'>
        <h2 className='text-2xl font-bold text-white'>
          {mode === 'create' ? 'Crear Nuevo Producto' : 'Editar Producto'}
        </h2>
        <p className='text-slate-200 mt-2'>
          {mode === 'create'
            ? 'Completa la información para agregar un producto a tu catálogo'
            : 'Actualiza la información de tu producto'
          }
        </p>
      </div>

      {message && (
        <div className={`p-4 rounded-lg mb-6 border transition-all duration-300 ${
          message.type === 'success'
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
            : message.type === 'error'
              ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
              : 'bg-blue-50 border-blue-200 text-blue-800 shadow-blue-100'
        } shadow-lg`}>
          <div className='flex items-center'>
            <div className='flex-1 font-medium'>{message.text}</div>
            <button
              onClick={clearMessage}
              className={`ml-3 text-lg hover:scale-110 transition-transform ${
                message.type === 'success' ? 'text-emerald-600 hover:text-emerald-800'
                : message.type === 'error' ? 'text-red-600 hover:text-red-800'
                : 'text-blue-600 hover:text-blue-800'
              }`}
            >
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
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mt-2">
              <p className="text-sm text-amber-700 flex items-center animate-fade-in font-medium">
                <AlertTriangle className="w-4 h-4 mr-2 text-amber-500" />
                Este nombre ya está en uso. Intenta con una variación.
              </p>
            </div>
          )}
          {validationState.nameAvailable === true && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 mt-2">
              <p className="text-sm text-emerald-700 flex items-center animate-fade-in font-medium">
                <CheckCircle className="w-4 h-4 mr-2 text-emerald-500" />
                ¡Perfecto! Este nombre está disponible.
              </p>
            </div>
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
          <div className="bg-gradient-to-br from-slate-50 to-blue-50 p-5 rounded-xl border border-slate-200 shadow-sm">
            <h4 className="text-base font-semibold text-slate-800 mb-3 flex items-center">
              💰 Análisis de Rentabilidad
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-white rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">Margen de ganancia:</span>
                <span className={`text-lg font-bold ${
                  validationState.marginHealthy
                    ? 'text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full'
                    : 'text-amber-600 bg-amber-50 px-3 py-1 rounded-full'
                }`}>
                  {(((precioVenta - precioCosto) / precioVenta) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-white rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">Ganancia por unidad:</span>
                <span className="text-lg font-bold text-blue-600">
                  ${(precioVenta - precioCosto).toLocaleString()} COP
                </span>
              </div>
              {!validationState.marginHealthy && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <p className="text-sm text-amber-700 flex items-center font-medium">
                    <AlertTriangle className="w-4 h-4 mr-2 text-amber-500" />
                    Recomendación: Margen saludable entre 10% y 80%
                  </p>
                </div>
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
          <h3 className="text-lg font-semibold text-white flex items-center">
            📦 Dimensiones y Peso
          </h3>
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
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-800">
                    📐 Volumen calculado: <span className="font-bold">{(watchedDimensions[0] * watchedDimensions[1] * watchedDimensions[2]).toLocaleString()} cm³</span>
                  </p>
                  <p className="text-xs text-blue-600 mt-1">
                    Densidad: {((watchedDimensions[3] || 0) / ((watchedDimensions[0] * watchedDimensions[1] * watchedDimensions[2]) / 1000000)).toFixed(2)} kg/m³
                  </p>
                </div>
                {validationState.dimensionsValid === true && (
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                )}
              </div>
              {validationState.dimensionsValid === false && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mt-3">
                  <p className="text-sm text-amber-700 flex items-center font-medium">
                    <AlertTriangle className="w-4 h-4 mr-2 text-amber-500" />
                    Las dimensiones y peso parecen inconsistentes. Verifica los datos.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Image Upload Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white flex items-center">
            🖼️ Imágenes del Producto
          </h3>

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
                  <h4 className="text-sm font-semibold text-slate-200 mb-3 bg-slate-700 rounded-lg px-3 py-2">
                    📸 Imágenes actuales ({existingImages.length})
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
                <div className="text-center py-8 border-2 border-dashed border-slate-300 rounded-lg">
                  <p className="text-sm text-slate-400 mb-2">📷 No hay imágenes existentes</p>
                  <p className="text-xs text-slate-500">Las imágenes ayudan a aumentar las ventas hasta un 65%</p>
                </div>
              )}
            </div>
          )}

          {/* Upload new images */}
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-3 bg-slate-700 rounded-lg px-3 py-2">
              {mode === 'edit' ? '➕ Agregar nuevas imágenes' : '🖼️ Imágenes del producto'}
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
              <h4 className="text-sm font-semibold text-slate-200 mb-3 bg-emerald-700 rounded-lg px-3 py-2">
                ✨ Nuevas imágenes seleccionadas ({selectedImages.length})
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

          <div className="bg-slate-800 p-4 rounded-lg border border-slate-600">
            <p className="text-sm text-slate-300 font-medium">
              📋 Requisitos de imágenes:
            </p>
            <ul className="text-xs text-slate-400 mt-2 space-y-1">
              <li>• Máximo 5 imágenes total (JPG, PNG, WebP, GIF)</li>
              <li>• Máximo 5MB por imagen</li>
              <li>• Resolución recomendada: 800x800px o superior</li>
              {existingImages.length > 0 && (
                <li className="text-blue-300">
                  • Tienes {existingImages.length} imagen(es) existente(s). Puedes agregar {5 - existingImages.length} más.
                </li>
              )}
            </ul>
          </div>
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

        {/* Sección de Ayuda y Requerimientos - DINÁMICO EN TIEMPO REAL */}
        <div className='mt-6 p-6 bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 border border-slate-600 rounded-xl shadow-xl'>
          <h4 className='text-base font-bold text-white mb-4 flex items-center'>
            🎯 Progreso del Formulario ({(() => {
              // Cálculo correcto de campos completados
              const requiredFields = [
                { name: 'name', value: watchedName, minLength: 3 },
                { name: 'description', value: watchedDescription, minLength: 10 },
                { name: 'category', value: watchedCategory },
                { name: 'precio_venta', value: watchedPrecioVenta, minValue: 1000 },
                { name: 'precio_costo', value: watchedPrecioCosto, minValue: 1 },
                { name: 'stock', value: watchedStock, minValue: 0 },
                { name: 'peso', value: watchedPeso, minValue: 0.01 }
              ];

              const completedCount = requiredFields.filter(field => {
                if (errors[field.name]) return false;
                if (!field.value && field.value !== 0) return false;
                if (field.minLength && field.value.length < field.minLength) return false;
                if (field.minValue && field.value < field.minValue) return false;
                return true;
              }).length;

              return completedCount;
            })()}/7 completados)
          </h4>

          {/* Barra de progreso dinámica */}
          <div className='mb-6'>
            <div className='flex justify-between items-center mb-3'>
              <span className='text-sm font-medium text-slate-300'>Completado</span>
              <span className='text-sm font-bold text-emerald-400'>
                {Math.round(((() => {
                  const requiredFields = [
                    { name: 'name', value: watchedName, minLength: 3 },
                    { name: 'description', value: watchedDescription, minLength: 10 },
                    { name: 'category', value: watchedCategory },
                    { name: 'precio_venta', value: watchedPrecioVenta, minValue: 1000 },
                    { name: 'precio_costo', value: watchedPrecioCosto, minValue: 1 },
                    { name: 'stock', value: watchedStock, minValue: 0 },
                    { name: 'peso', value: watchedPeso, minValue: 0.01 }
                  ];

                  const completedCount = requiredFields.filter(field => {
                    if (errors[field.name]) return false;
                    if (!field.value && field.value !== 0) return false;
                    if (field.minLength && field.value.length < field.minLength) return false;
                    if (field.minValue && field.value < field.minValue) return false;
                    return true;
                  }).length;

                  return (completedCount / 7) * 100;
                })()))}%
              </span>
            </div>
            <div className='w-full bg-slate-600 rounded-full h-3 shadow-inner'>
              <div
                className='bg-gradient-to-r from-emerald-500 via-blue-500 to-emerald-500 h-3 rounded-full transition-all duration-700 ease-out shadow-lg'
                style={{
                  width: `${(() => {
                    const requiredFields = [
                      { name: 'name', value: watchedName, minLength: 3 },
                      { name: 'description', value: watchedDescription, minLength: 10 },
                      { name: 'category', value: watchedCategory },
                      { name: 'precio_venta', value: watchedPrecioVenta, minValue: 1000 },
                      { name: 'precio_costo', value: watchedPrecioCosto, minValue: 1 },
                      { name: 'stock', value: watchedStock, minValue: 0 },
                      { name: 'peso', value: watchedPeso, minValue: 0.01 }
                    ];

                    const completedCount = requiredFields.filter(field => {
                      if (errors[field.name]) return false;
                      if (!field.value && field.value !== 0) return false;
                      if (field.minLength && field.value.length < field.minLength) return false;
                      if (field.minValue && field.value < field.minValue) return false;
                      return true;
                    }).length;

                    return (completedCount / 7) * 100;
                  })()}%`
                }}
              ></div>
            </div>
          </div>

          <div className='grid grid-cols-1 md:grid-cols-2 gap-3 text-sm'>
            {/* Nombre del producto */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.name && watchedName?.length >= 3
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.name
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.name && watchedName?.length >= 3 ? '✅' : errors.name ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Nombre del producto</span>
                {watchedName && (
                  <div className='text-xs opacity-75 mt-1'>Longitud: {watchedName.length}/100 caracteres</div>
                )}
              </div>
            </div>

            {/* Descripción */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.description && watch('description')?.length >= 10
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.description
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.description && watch('description')?.length >= 10 ? '✅' : errors.description ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Descripción</span>
                {watch('description') && (
                  <div className='text-xs opacity-75 mt-1'>Longitud: {watch('description').length}/1000 caracteres</div>
                )}
              </div>
            </div>

            {/* Precio de venta */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.precio_venta && precioVenta >= 1000
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.precio_venta
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.precio_venta && precioVenta >= 1000 ? '✅' : errors.precio_venta ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Precio de venta</span>
                {precioVenta > 0 && (
                  <div className='text-xs opacity-75 mt-1'>${precioVenta.toLocaleString()} COP</div>
                )}
              </div>
            </div>

            {/* Precio de costo */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.precio_costo && precioCosto > 0 && precioCosto < precioVenta
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.precio_costo
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.precio_costo && precioCosto > 0 && precioCosto < precioVenta ? '✅' : errors.precio_costo ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Precio de costo</span>
                {precioCosto > 0 && (
                  <div className='text-xs opacity-75 mt-1'>${precioCosto.toLocaleString()} COP</div>
                )}
              </div>
            </div>

            {/* Stock */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.stock && watch('stock') >= 0
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.stock
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.stock && watch('stock') >= 0 ? '✅' : errors.stock ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Stock inicial</span>
                <div className='text-xs opacity-75 mt-1'>{watch('stock') || 0} unidades disponibles</div>
              </div>
            </div>

            {/* Categoría */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.category && watch('category')
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.category
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.category && watch('category') ? '✅' : errors.category ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>Categoría</span>
                {watch('category') && (
                  <div className='text-xs opacity-75 mt-1 capitalize'>{watch('category')}</div>
                )}
              </div>
            </div>

            {/* SKU */}
            <div className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
              !errors.sku && watch('sku')?.length >= 3
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800 shadow-emerald-100'
                : errors.sku
                  ? 'bg-red-50 border-red-200 text-red-800 shadow-red-100'
                  : 'bg-slate-100 border-slate-300 text-slate-600'
            } shadow-sm`}>
              <span className='text-xl'>
                {!errors.sku && watch('sku')?.length >= 3 ? '✅' : errors.sku ? '❌' : '⏳'}
              </span>
              <div className='flex-1'>
                <span className='font-medium'>SKU único</span>
                {watch('sku') && (
                  <div className='text-xs opacity-75 mt-1 font-mono'>{watch('sku')}</div>
                )}
              </div>
            </div>
          </div>

          {/* Barra de progreso adicional */}
          <div className='mt-6 pt-4 border-t border-slate-600'>
            <div className='flex justify-between text-sm text-slate-300 mb-2'>
              <span className='font-medium'>Validación de errores</span>
              <span className='font-bold text-emerald-400'>{Math.round(((7 - Object.keys(errors).length) / 7) * 100)}%</span>
            </div>
            <div className='w-full bg-slate-600 rounded-full h-2 shadow-inner'>
              <div
                className='bg-gradient-to-r from-emerald-500 to-green-400 h-2 rounded-full transition-all duration-500 shadow-sm'
                style={{ width: `${((7 - Object.keys(errors).length) / 7) * 100}%` }}
              ></div>
            </div>
          </div>

          {isFormValid && (
            <div className='mt-4 p-4 bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-200 rounded-xl text-emerald-800 text-sm text-center shadow-lg'>
              <div className='flex items-center justify-center space-x-2'>
                <span className='text-2xl'>🎉</span>
                <span className='font-bold'>¡Formulario completo!</span>
              </div>
              <p className='mt-1 text-emerald-600'>El botón "Crear Producto" está habilitado y listo para usar.</p>
            </div>
          )}
        </div>

        <div className='flex gap-4 pt-8'>
          <button
            type='submit'
            disabled={loading || uploadingImages || !isFormValid}
            className={`flex-1 px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center transition-all duration-300 transform ${
              loading || uploadingImages || !isFormValid
                ? 'bg-slate-400 text-slate-200 cursor-not-allowed opacity-60 shadow-none'
                : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-xl hover:shadow-2xl hover:scale-105 hover:from-blue-700 hover:to-blue-800 active:scale-95'
            }`}
          >
            {uploadingImages ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                💾 Subiendo imágenes...
              </>
            ) : loading ? (
              <>
                <div className="animate-pulse mr-2">⏳</div>
                Procesando...
              </>
            ) : mode === 'create' ? (
              <>
                <span className="mr-2">✨</span>
                Crear Producto
              </>
            ) : (
              <>
                <span className="mr-2">🔄</span>
                Actualizar Producto
              </>
            )}
          </button>

          <button
            type='button'
            onClick={handleCancel}
            disabled={loading || uploadingImages}
            className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform ${
              loading || uploadingImages
                ? 'border-slate-400 text-slate-400 opacity-50 cursor-not-allowed'
                : 'border-2 border-slate-300 text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-400 hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl'
            }`}
          >
            <span className="mr-2">❌</span>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;
