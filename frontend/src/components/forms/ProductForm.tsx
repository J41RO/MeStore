import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { 
  createProductSchema, 
  ProductFormData, 
  defaultProductValues,
  getCategoryOptions 
} from '../../schemas/productSchema';
import { CreateProductData, UpdateProductData } from '../../types/api.types';
import { api } from '../../services/api';

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
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<MessageState | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    setValue
  } = useForm<any>({
    resolver: yupResolver(createProductSchema) as any,
    mode: 'onChange',
    defaultValues: {
      ...defaultProductValues,
      ...initialData
    }
  });

  useEffect(() => {
    if (mode === 'edit' && initialData) {
      Object.entries(initialData).forEach(([key, value]) => {
        setValue(key as keyof ProductFormData, value);
      });
    }
  }, [mode, initialData, setValue]);

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
      if (mode === 'create') {
        await api.products.create(data as CreateProductData);
        showMessage('Producto creado exitosamente', 'success');
      } else {
        const productId = (initialData as any)?.id;
        if (!productId) {
          throw new Error('ID del producto requerido para actualización');
        }
        await api.products.update(productId, data as UpdateProductData);
        showMessage('Producto actualizado exitosamente', 'success');
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

  const categoryOptions = getCategoryOptions();

  return (
    <div className="product-form">
      <div className="form-header mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {mode === 'create' ? 'Crear Nuevo Producto' : 'Editar Producto'}
        </h2>
      </div>

      {message && (
        <div className="p-4 rounded-lg mb-6 bg-green-50 border border-green-200 text-green-800">
          <div className="flex">
            <div className="flex-1">{message.text}</div>
            <button onClick={clearMessage} className="ml-2">×</button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-2">
            Nombre del Producto *
          </label>
          <input
            id="name"
            type="text"
            {...register('name')}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="Ej: iPhone 14 Pro Max"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name?.message as string}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-2">
            Descripción *
          </label>
          <textarea
            id="description"
            {...register('description')}
            rows={4}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="Describe las características principales..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description?.message as string}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="price" className="block text-sm font-medium mb-2">
              Precio ($) *
            </label>
            <input
              id="price"
              type="number"
              step="0.01"
              min="0"
              max="999999"
              {...register('price')}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="0.00"
            />
            {errors.price && (
              <p className="mt-1 text-sm text-red-600">{errors.price?.message as string}</p>
            )}
          </div>

          <div>
            <label htmlFor="stock" className="block text-sm font-medium mb-2">
              Stock *
            </label>
            <input
              id="stock"
              type="number"
              min="0"
              {...register('stock')}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="0"
            />
            {errors.stock && (
              <p className="mt-1 text-sm text-red-600">{errors.stock?.message as string}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-medium mb-2">
            Categoría *
          </label>
          <select
            id="category"
            {...register('category')}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="">Selecciona una categoría</option>
            {categoryOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.category && (
            <p className="mt-1 text-sm text-red-600">{errors.category?.message as string}</p>
          )}
        </div>

        <div>
          <label htmlFor="imageUrl" className="block text-sm font-medium mb-2">
            URL de Imagen (Opcional)
          </label>
          <input
            id="imageUrl"
            type="url"
            {...register('imageUrl')}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="https://ejemplo.com/imagen.jpg"
          />
          {errors.imageUrl && (
            <p className="mt-1 text-sm text-red-600">{errors.imageUrl?.message as string}</p>
          )}
        </div>

        {/* SKU Field */}
        <div>
          <label htmlFor="sku" className="block text-sm font-medium mb-2">
            SKU (Opcional)
          </label>
          <input
            id="sku"
            type="text"
            {...register('sku')}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="Ej: PROD-001"
          />
          {errors.sku && (
            <p className="mt-1 text-sm text-red-600">{errors.sku?.message as string}</p>
          )}
        </div>

        {/* Dimensions Fields */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Dimensiones (Opcional)
          </label>
          <div className="grid grid-cols-4 gap-2">
            <input placeholder="Largo" type="number" {...register('dimensions.length')} className="px-3 py-2 border rounded-lg" />
            <input placeholder="Ancho" type="number" {...register('dimensions.width')} className="px-3 py-2 border rounded-lg" />
            <input placeholder="Alto" type="number" {...register('dimensions.height')} className="px-3 py-2 border rounded-lg" />
            <select {...register('dimensions.unit')} className="px-3 py-2 border rounded-lg">
              <option value="">Unidad</option>
              <option value="cm">cm</option>
              <option value="m">m</option>
              <option value="mm">mm</option>
            </select>
          </div>
        </div>

        {/* Weight Fields */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Peso (Opcional)
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input placeholder="Peso" type="number" {...register('weight.value')} className="px-3 py-2 border rounded-lg" />
            <select {...register('weight.unit')} className="px-3 py-2 border rounded-lg">
              <option value="">Unidad</option>
              <option value="g">g</option>
              <option value="kg">kg</option>
              <option value="lb">lb</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 pt-6">
          <button
            type="submit"
            disabled={loading || !isValid}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg disabled:bg-gray-300"
          >
            {loading ? 'Procesando...' : (mode === 'create' ? 'Crear Producto' : 'Actualizar Producto')}
          </button>

          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            className="px-6 py-3 border text-gray-700 rounded-lg"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;