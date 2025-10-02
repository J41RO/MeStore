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

// TEST: Force HMR update - timestamp: 2025-09-30 SQUAD FIX
const ProductForm: React.FC<ProductFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  onSuccess,
}) => {
  // 🚨 LOG CRÍTICO - ESTE DEBE APARECER EN CONSOLA
  console.log('🚨🚨🚨 [SQUAD] ProductForm /components/forms/ProductForm.tsx MONTADO');
  console.log('🚨 [SQUAD] Mode:', mode);
  console.log('🚨 [SQUAD] initialData:', initialData);
  console.log('🚨 [SQUAD] initialData?.id:', initialData?.id);

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
    defaultValues: mode === 'edit' && initialData ? {
      // En modo EDIT: mapear campos del backend a nombres del formulario
      id: initialData.id,
      name: initialData.name || '',
      description: initialData.description || '',
      precio_venta: initialData.price || initialData.precio_venta || 100,
      precio_costo: initialData.cost || initialData.precio_costo || 100,
      category: initialData.category || initialData.categoria || '',
      stock: initialData.stock || initialData.stock_quantity || 0,
      sku: initialData.sku || '',
      largo: initialData.dimensions?.length || initialData.largo || 0.1,
      ancho: initialData.dimensions?.width || initialData.ancho || 0.1,
      alto: initialData.dimensions?.height || initialData.alto || 0.1,
      peso: initialData.weight?.value || initialData.peso || 0.01,
    } as ProductFormData : {
      // En modo CREATE: usar valores por defecto
      ...defaultProductValues,
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

  // Cálculo de validación personalizado con progreso
  const formProgress = useMemo(() => {
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
      // Si hay error, no cuenta
      if (errors[field.name]) return false;

      // Campos de texto: deben existir y cumplir longitud mínima
      if (field.minLength) {
        if (!field.value || field.value.length < field.minLength) return false;
      }

      // Campos numéricos: deben tener valor real (no undefined/null/empty) y cumplir valor mínimo
      if (field.minValue !== undefined) {
        if (field.value === undefined || field.value === null || field.value === '') return false;
        if (field.value < field.minValue) return false;
      }

      // Campo select (category): debe tener valor
      if (field.name === 'category') {
        if (!field.value || field.value === '') return false;
      }

      return true;
    }).length;

    const allFieldsValid = completedCount === 7;
    const pricesValid = watchedPrecioCosto && watchedPrecioVenta && watchedPrecioCosto < watchedPrecioVenta;

    return {
      completedCount,
      progressPercent: Math.round((completedCount / 7) * 100),
      isValid: allFieldsValid && pricesValid
    };
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

  const isFormValid = formProgress.isValid;

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
  }, [setValidationState]);

  // Validación de margen de ganancia
  const validateMargin = useCallback((precioVenta: number, precioCosto: number) => {
    if (!precioVenta || !precioCosto) return true;

    const margen = ((precioVenta - precioCosto) / precioVenta) * 100;
    const isHealthy = margen >= 10 && margen <= 80;

    setValidationState(prev => ({ ...prev, marginHealthy: isHealthy }));
    return isHealthy;
  }, [setValidationState]);

  // Campo mapping ya se maneja en defaultValues del useForm
  // No necesitamos useEffect con setValue() porque defaultValues carga los datos al inicializar

  // Message handlers - Defined before useEffect to avoid reference issues
  const clearMessage = useCallback(() => {
    setMessage(null);
  }, []);

  const showMessage = useCallback((text: string, type: MessageState['type']) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  }, []);

  // DESHABILITADO TEMPORALMENTE: Watchers para validaciones en tiempo real
  // CAUSA INFINITE LOOP - Necesita refactorización completa
  /*
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
  */

  // FIX: Extraer productId como valor primitivo para evitar infinite re-renders
  // El problema era que initialData es un objeto que cambia de referencia en cada render del padre
  const productId = initialData?.id;

  // Load existing images when in edit mode
  useEffect(() => {
    console.log('🔄 [ProductForm] useEffect de imágenes ejecutado');
    console.log('📦 [ProductForm] mode:', mode);
    console.log('🆔 [ProductForm] productId:', productId);

    const loadExistingImages = async () => {
      if (mode === 'edit' && productId) {
        console.log('✅ [ProductForm] MODO EDICIÓN DETECTADO - Cargando imágenes para ID:', productId);
        setLoadingExistingImages(true);
        try {
          console.log('📡 [ProductForm] Llamando a getProductImages...');
          const images = await getProductImages(productId as string);
          console.log('✅ [ProductForm] Imágenes recibidas:', images);
          console.log('📸 [ProductForm] Total imágenes:', images.length);
          setExistingImages(images);
          console.log('✅ [ProductForm] State actualizado con', images.length, 'imágenes');
        } catch (error) {
          console.error('❌ [ProductForm] Error loading existing images:', error);
          showMessage('Error cargando imágenes existentes', 'error');
        } finally {
          setLoadingExistingImages(false);
        }
      } else {
        console.log('⚠️ [ProductForm] NO se cargaron imágenes:');
        console.log('   - mode === "edit"?', mode === 'edit');
        console.log('   - productId?', !!productId);
      }
    };

    loadExistingImages();
  }, [mode, productId]); // showMessage es estable (useCallback), no necesita estar en deps

  const onFormSubmit = async (data: ProductFormData) => {
    console.log('🚨🚨🚨🚨🚨 [SQUAD] onFormSubmit EJECUTADO');
    console.log('🚨 [SQUAD] Data recibida:', data);
    console.log('🚨 [SQUAD] Mode:', mode);
    console.log('🚨 [SQUAD] initialData?.id:', initialData?.id);

    setLoading(true);
    clearMessage();

    try {
      // SOLO validar en modo CREATE - En modo EDIT permitir guardar cambios sin validación completa
      if (mode === 'create') {
        console.log('🆕 [SQUAD] MODO CREAR - Aplicando validación completa');
        const isFormValid = await trigger();
        console.log('🔍 [SQUAD] isFormValid:', isFormValid);
        if (!isFormValid) {
          console.log('❌ [SQUAD] Validación FALLIDA - Abortando creación');
          showMessage('Por favor completa todos los campos obligatorios', 'error');
          setLoading(false);
          return;
        }
      } else {
        console.log('✅✅✅ [SQUAD] MODO EDICIÓN CONFIRMADO - BYPASS DE VALIDACIÓN ACTIVADO ✅✅✅');
        console.log('✅ [SQUAD] Producto ID para actualizar:', initialData?.id);
      }

      console.log('🔄 Transformando datos para API...');
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

      console.log('📤 apiData preparada:', apiData);

      let productId: string;

      if (mode === 'create') {
        console.log('🆕 Modo CREATE - Llamando a api.products.create()...');
        const response = await api.products.create(apiData);
        console.log('✅ Respuesta de API:', response);
        productId = response.data.id;
        showMessage('Producto creado exitosamente', 'success');
        console.log('🎉 Producto creado con ID:', productId);
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
      console.log('🖼️ [ProductForm] Verificando operaciones de imágenes...');
      console.log('   - Nuevas imágenes:', selectedImages.length);
      console.log('   - Imágenes a eliminar:', deletedImageIds.length);

      if (selectedImages.length > 0 || deletedImageIds.length > 0) {
        setUploadingImages(true);
        try {
          // Delete images that were marked for deletion
          if (deletedImageIds.length > 0) {
            console.log('🗑️ [ProductForm] Eliminando', deletedImageIds.length, 'imágenes...');
            for (const imageId of deletedImageIds) {
              console.log('🗑️ [ProductForm] DELETE imagen:', imageId);
              await deleteProductImage(imageId);
              console.log('✅ [ProductForm] Imagen eliminada:', imageId);
            }
          }

          // Upload new images if any
          if (selectedImages.length > 0) {
            console.log('📤 [ProductForm] Subiendo', selectedImages.length, 'imágenes nuevas...');
            const imageFiles = selectedImages.map(img => img.file);
            await uploadProductImages(productId, imageFiles);
            console.log('✅ [ProductForm] Imágenes subidas exitosamente');
          }

          showMessage('Producto e imágenes guardados exitosamente', 'success');
        } catch (imageError) {
          console.error('❌ [ProductForm] Error en gestión de imágenes:', imageError);
          showMessage('Producto guardado pero falló la gestión de imágenes', 'error');
        } finally {
          setUploadingImages(false);
        }
      } else {
        console.log('ℹ️ [ProductForm] No hay cambios en imágenes');
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
      console.error('❌❌❌ ERROR CAPTURADO en onFormSubmit:', error);
      console.error('❌ Error type:', typeof error);
      console.error('❌ Error details:', JSON.stringify(error, null, 2));

      let errorMessage = 'Error al procesar el producto';

      if (error instanceof Error) {
        errorMessage = error.message;
        console.error('❌ Error.message:', error.message);
        console.error('❌ Error.stack:', error.stack);
      }

      showMessage(errorMessage, 'error');
      console.log('🔴 Mensaje de error mostrado al usuario:', errorMessage);
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
    console.log('🗑️ [ProductForm] Eliminando imagen existente:', imageId);
    // Mark for deletion
    setDeletedImageIds(prev => {
      const updated = [...prev, imageId];
      console.log('📝 [ProductForm] Imágenes marcadas para eliminar:', updated);
      return updated;
    });
    // Remove from UI
    setExistingImages(prev => {
      const updated = prev.filter(img => img.id !== imageId);
      console.log('✅ [ProductForm] Imágenes restantes en UI:', updated.length);
      return updated;
    });
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
              label="Largo*"
              name="largo"
              register={register}
              error={errors.largo?.message}
              min={0}
              step={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Ancho*"
              name="ancho"
              register={register}
              error={errors.ancho?.message}
              min={0}
              step={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Alto*"
              name="alto"
              register={register}
              error={errors.alto?.message}
              min={0}
              step={1}
              max={500}
              unit="cm"
              placeholder="0"
              required
            />
            <NumberField
              label="Peso*"
              name="peso"
              register={register}
              error={errors.peso?.message}
              min={0}
              step={0.01}
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
            <ul className="text-xs mt-2 space-y-1" style={{ color: '#cbd5e1 !important' }}>
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

        {/* Progreso del Formulario - Solo en modo CREAR */}
        {mode === 'create' && (
          <div className='mt-6 p-4 bg-slate-700/50 border border-slate-600/50 rounded-lg'>
            <div className='flex items-center justify-between mb-3'>
              <span className='text-sm font-medium text-white'>Progreso del formulario</span>
              <span className='text-sm font-bold text-blue-400'>
                {formProgress.progressPercent}% ({formProgress.completedCount}/7 campos)
              </span>
            </div>
            <div className='w-full bg-slate-600 rounded-full h-2'>
              <div
                className='bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-500'
                style={{ width: `${formProgress.progressPercent}%` }}
              />
            </div>
            {isFormValid && (
              <p className='mt-3 text-sm text-emerald-400 text-center'>Formulario completo</p>
            )}
          </div>
        )}

        <div className='flex gap-4 pt-8'>
          <button
            type='button'
            onClick={async (e) => {
              console.log('🔴🔴🔴 BOTÓN CLICKEADO - BYPASS REACT HOOK FORM');
              e.preventDefault();

              try {
                setLoading(true);

                // Obtener datos del formulario manualmente
                const formValues = watch();
                console.log('📦 Form values:', formValues);

                // Preparar datos para API según el modo
                let productData: any;

                if (mode === 'edit') {
                  // Para UPDATE: usar nombres de campos del backend - solo enviar valores que existan
                  productData = {};

                  // Agregar solo campos que tengan valor para evitar validaciones innecesarias
                  if (formValues.name) productData.name = formValues.name;
                  if (formValues.description) productData.description = formValues.description;
                  if (formValues.sku) productData.sku = formValues.sku;

                  // Campos numéricos - permitir 0 como valor válido
                  const precioVenta = parseFloat(formValues.precio_venta as any);
                  if (!isNaN(precioVenta)) productData.precio_venta = precioVenta;

                  const precioCosto = parseFloat(formValues.precio_costo as any);
                  if (!isNaN(precioCosto)) productData.precio_costo = precioCosto;

                  const peso = parseFloat(formValues.peso as any);
                  // Backend requiere peso >= 0.001, usar 0.01 como mínimo seguro
                  if (!isNaN(peso) && peso >= 0.01) productData.peso = peso;

                  // Category viene del formulario como 'category' pero backend espera 'categoria'
                  if (formValues.category) productData.categoria = formValues.category;

                  // Dimensiones - solo si existen valores válidos (> 0)
                  const largo = parseFloat(formValues.largo as any);
                  const ancho = parseFloat(formValues.ancho as any);
                  const alto = parseFloat(formValues.alto as any);
                  if (!isNaN(largo) && largo > 0 && !isNaN(ancho) && ancho > 0 && !isNaN(alto) && alto > 0) {
                    productData.dimensiones = {
                      largo: largo,
                      ancho: ancho,
                      alto: alto,
                    };
                  }

                  console.log('✏️ Datos para UPDATE (nombres backend):', productData);
                  console.log('📊 Campos enviados:', Object.keys(productData));
                } else {
                  // Para CREATE: usar nombres esperados por el endpoint POST
                  productData = {
                    name: formValues.name,
                    description: formValues.description,
                    price: parseFloat(formValues.precio_venta as any) || 0,
                    stock: parseInt(formValues.stock as any) || 0,
                    category: formValues.category,
                    sku: formValues.sku || `PROD-${Date.now()}`,
                    dimensions: {
                      length: parseFloat(formValues.largo as any) || 0,
                      width: parseFloat(formValues.ancho as any) || 0,
                      height: parseFloat(formValues.alto as any) || 0,
                      unit: 'cm'
                    },
                    weight: {
                      value: parseFloat(formValues.peso as any) || 0,
                      unit: 'kg'
                    }
                  };
                  console.log('➕ Datos para CREATE:', productData);
                }

                // Buscar token en múltiples ubicaciones
                console.log('🔍 Buscando token en localStorage...');
                console.log('📋 localStorage keys:', Object.keys(localStorage));

                let token = localStorage.getItem('token')
                         || localStorage.getItem('access_token')
                         || localStorage.getItem('authToken')
                         || localStorage.getItem('accessToken');

                console.log('🔍 Token desde localStorage:', token ? '✅ Encontrado' : '❌ No encontrado');

                // Si no está en localStorage, intentar obtenerlo de sessionStorage
                if (!token) {
                  console.log('🔍 Intentando sessionStorage...');
                  token = sessionStorage.getItem('token')
                       || sessionStorage.getItem('access_token')
                       || sessionStorage.getItem('authToken');
                  console.log('🔍 Token desde sessionStorage:', token ? '✅ Encontrado' : '❌ No encontrado');
                }

                if (!token) {
                  console.error('❌ NO SE ENCONTRÓ TOKEN EN NINGÚN LADO');
                  console.log('📋 Valores de localStorage:', { ...localStorage });
                  console.log('📋 Valores de sessionStorage:', { ...sessionStorage });
                  throw new Error('No se encontró token de autenticación. Por favor inicia sesión nuevamente.');
                }

                console.log('🔑 Token encontrado:', token.substring(0, 20) + '...');
                console.log('📡 Enviando a backend...');
                console.log('🔧 Modo:', mode);
                console.log('📦 Datos a enviar:', productData);

                // Determinar URL y método según el modo
                const url = mode === 'edit' && initialData?.id
                  ? `http://192.168.1.137:8000/api/v1/products/${initialData.id}`
                  : 'http://192.168.1.137:8000/api/v1/products';
                const method = mode === 'edit' ? 'PUT' : 'POST';

                console.log(`🌐 ${method} ${url}`);

                const response = await fetch(url, {
                  method,
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                  },
                  body: JSON.stringify(productData)
                });

                console.log('📥 Response status:', response.status);

                if (!response.ok) {
                  const errorData = await response.json();
                  console.error('❌ Error del servidor:', errorData);
                  throw new Error(JSON.stringify(errorData));
                }

                const result = await response.json();
                console.log(`✅✅✅ PRODUCTO ${mode === 'edit' ? 'ACTUALIZADO' : 'CREADO'}:`, result);

                // Ejecutar onSuccess ANTES del alert para no bloquear
                console.log('🔔 Llamando a onSuccess callback...');
                console.log('🔍 onSuccess type:', typeof onSuccess);
                if (onSuccess) {
                  console.log('✅ Ejecutando onSuccess()...');
                  onSuccess();
                  console.log('✅ onSuccess() completado');
                } else {
                  console.warn('⚠️ onSuccess no está definido');
                }

                console.log('🔄 Cerrando modal y recargando lista...');
                setLoading(false);

                // Alert al final para no bloquear el refresh
                alert(`¡Producto ${mode === 'edit' ? 'actualizado' : 'creado'} exitosamente!`);
              } catch (error) {
                console.error('❌❌❌ ERROR:', error);
                alert(`Error al ${mode === 'edit' ? 'actualizar' : 'crear'} producto: ` + (error instanceof Error ? error.message : 'Unknown error'));
                setLoading(false);
              }
            }}
            disabled={mode === 'edit' ? (loading || uploadingImages) : (loading || uploadingImages || !isFormValid)}
            className={`flex-1 px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center transition-all duration-300 transform ${
              (mode === 'edit' ? (loading || uploadingImages) : (loading || uploadingImages || !isFormValid))
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
