// frontend/src/components/vendor/VendorProductForm.tsx
// PRODUCTION_READY: Formulario completo para creación/edición de productos
// Optimizado para vendedores colombianos con validación y UX excepcional

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Save,
  X,
  Upload,
  Image as ImageIcon,
  Trash2,
  Plus,
  DollarSign,
  Package,
  Tag,
  AlertCircle,
  Check,
  Star,
  Eye,
  EyeOff,
  Calculator,
  HelpCircle,
  Camera,
  Zap
} from 'lucide-react';
import { Product, CreateProductRequest, UpdateProductRequest } from '../../types/product.types';

interface VendorProductFormProps {
  product?: Product | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateProductRequest | UpdateProductRequest) => Promise<void>;
  className?: string;
}

interface FormData {
  name: string;
  description: string;
  sku: string;
  price: number;
  precio_costo: number;
  stock: number;
  category_id: string;
  peso: number;
  tags: string[];
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;
  images: File[];
  existingImages: string[];
}

interface FormErrors {
  [key: string]: string;
}

const CATEGORIES = [
  { id: 'electronics', name: 'Electrónicos', icon: '📱' },
  { id: 'clothing', name: 'Ropa y Accesorios', icon: '👕' },
  { id: 'home', name: 'Hogar y Jardín', icon: '🏠' },
  { id: 'automotive', name: 'Automotriz', icon: '🚗' },
  { id: 'books', name: 'Libros y Medios', icon: '📚' },
  { id: 'health', name: 'Salud y Belleza', icon: '💊' },
  { id: 'sports', name: 'Deportes y Aire Libre', icon: '⚽' },
  { id: 'toys', name: 'Juguetes y Juegos', icon: '🧸' },
  { id: 'food', name: 'Alimentos y Bebidas', icon: '🍔' },
  { id: 'industrial', name: 'Industrial', icon: '🔧' }
];

export const VendorProductForm: React.FC<VendorProductFormProps> = ({
  product,
  isOpen,
  onClose,
  onSubmit,
  className = ''
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [previewImages, setPreviewImages] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [newTag, setNewTag] = useState('');

  // Estado del formulario
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    sku: '',
    price: 0,
    precio_costo: 0,
    stock: 0,
    category_id: '',
    peso: 0,
    tags: [],
    is_active: true,
    is_featured: false,
    is_digital: false,
    images: [],
    existingImages: []
  });

  // Errores del formulario
  const [errors, setErrors] = useState<FormErrors>({});

  // Inicializar formulario con datos del producto
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        description: product.description,
        sku: product.sku,
        price: product.precio_venta,
        precio_costo: product.precio_costo || 0,
        stock: product.stock,
        category_id: product.category_id || '',
        peso: product.peso || 0,
        tags: product.tags || [],
        is_active: product.is_active,
        is_featured: product.is_featured,
        is_digital: product.is_digital,
        images: [],
        existingImages: product.images?.map(img => img.public_url) || []
      });
      setPreviewImages(product.images?.map(img => img.public_url) || []);
    } else {
      // Generar SKU automático para nuevos productos
      const sku = `PROD-${Date.now().toString().slice(-6)}`;
      setFormData(prev => ({ ...prev, sku }));
    }
  }, [product]);

  // Formateo de moneda colombiana
  const formatCOP = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }, []);

  // Cálculos automáticos
  const calculations = useCallback(() => {
    const margenBruto = formData.price - formData.precio_costo;
    const porcentajeMargen = formData.precio_costo > 0 ? (margenBruto / formData.precio_costo) * 100 : 0;
    const comisionMestocker = formData.price * 0.05; // 5% comisión

    return {
      margenBruto,
      porcentajeMargen,
      comisionMestocker,
      gananciaReal: margenBruto - comisionMestocker
    };
  }, [formData.price, formData.precio_costo]);

  const calc = calculations();

  // Validación del formulario
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre del producto es obligatorio';
    } else if (formData.name.length < 3) {
      newErrors.name = 'El nombre debe tener al menos 3 caracteres';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'La descripción es obligatoria';
    } else if (formData.description.length < 10) {
      newErrors.description = 'La descripción debe tener al menos 10 caracteres';
    }

    if (!formData.sku.trim()) {
      newErrors.sku = 'El SKU es obligatorio';
    }

    if (formData.price <= 0) {
      newErrors.price = 'El precio debe ser mayor a 0';
    } else if (formData.price < 1000) {
      newErrors.price = 'El precio mínimo es $1.000 COP';
    }

    if (!formData.is_digital && formData.stock < 0) {
      newErrors.stock = 'El stock no puede ser negativo';
    }

    if (!formData.category_id) {
      newErrors.category_id = 'Debe seleccionar una categoría';
    }

    if (formData.precio_costo > 0 && formData.precio_costo >= formData.price) {
      newErrors.precio_costo = 'El precio de costo debe ser menor al precio de venta';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Manejo de cambios en el formulario
  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Limpiar error específico
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Manejo de imágenes
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const totalImages = previewImages.length + files.length;

    if (totalImages > 8) {
      setErrors(prev => ({ ...prev, images: 'Máximo 8 imágenes permitidas' }));
      return;
    }

    files.forEach(file => {
      if (file.size > 5 * 1024 * 1024) { // 5MB
        setErrors(prev => ({ ...prev, images: 'Cada imagen debe ser menor a 5MB' }));
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImages(prev => [...prev, e.target?.result as string]);
      };
      reader.readAsDataURL(file);
    });

    setFormData(prev => ({ ...prev, images: [...prev.images, ...files] }));
  };

  const removeImage = (index: number) => {
    setPreviewImages(prev => prev.filter((_, i) => i !== index));
    if (index < formData.existingImages.length) {
      setFormData(prev => ({
        ...prev,
        existingImages: prev.existingImages.filter((_, i) => i !== index)
      }));
    } else {
      const newImageIndex = index - formData.existingImages.length;
      setFormData(prev => ({
        ...prev,
        images: prev.images.filter((_, i) => i !== newImageIndex)
      }));
    }
  };

  // Manejo de tags
  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      handleInputChange('tags', [...formData.tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  // Envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔵 SUBMIT CLICKED - handleSubmit ejecutado');
    console.log('🔵 FormData:', formData);

    if (!validateForm()) {
      console.log('❌ VALIDACIÓN FALLIDA:', errors);
      return;
    }

    console.log('✅ VALIDACIÓN EXITOSA - Procediendo a enviar...');
    setIsSubmitting(true);

    try {
      const submitData = {
        ...formData,
        comision_mestocker: calc.comisionMestocker
      };

      console.log('🔵 Datos a enviar:', submitData);
      console.log('🔵 Llamando a onSubmit...');

      await onSubmit(submitData as any);

      console.log('✅ onSubmit exitoso - Cerrando modal');
      onClose();
    } catch (error) {
      console.error('❌ ERROR al guardar producto:', error);
      alert(`Error al crear producto: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setIsSubmitting(false);
      console.log('🔵 handleSubmit finalizado');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-200">
          <div>
            <h2 className="text-xl font-bold text-neutral-900">
              {product ? 'Editar Producto' : 'Nuevo Producto'}
            </h2>
            <p className="text-sm text-neutral-500 mt-1">
              {product ? 'Modifica la información de tu producto' : 'Agrega un nuevo producto a tu catálogo'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Indicador de pasos */}
        <div className="px-6 py-4 bg-neutral-50 border-b border-neutral-200">
          <div className="flex items-center justify-between max-w-md">
            <div className={`flex items-center ${currentStep >= 1 ? 'text-primary-600' : 'text-neutral-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= 1 ? 'bg-primary-100 text-primary-600' : 'bg-neutral-200 text-neutral-500'
              }`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">Información básica</span>
            </div>
            <div className={`flex items-center ${currentStep >= 2 ? 'text-primary-600' : 'text-neutral-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= 2 ? 'bg-primary-100 text-primary-600' : 'bg-neutral-200 text-neutral-500'
              }`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Precios y stock</span>
            </div>
            <div className={`flex items-center ${currentStep >= 3 ? 'text-primary-600' : 'text-neutral-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= 3 ? 'bg-primary-100 text-primary-600' : 'bg-neutral-200 text-neutral-500'
              }`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">Imágenes</span>
            </div>
          </div>
        </div>

        {/* Contenido del formulario */}
        <div className="overflow-y-auto max-h-[60vh]">
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Paso 1: Información básica */}
            {currentStep === 1 && (
              <div className="space-y-6">
                {/* Nombre del producto */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Nombre del producto *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="Ej: Smartphone Samsung Galaxy A54"
                    className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                      errors.name ? 'border-red-300' : 'border-neutral-300'
                    }`}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.name}
                    </p>
                  )}
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Descripción *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Describe las características principales, beneficios y especificaciones del producto..."
                    rows={4}
                    className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                      errors.description ? 'border-red-300' : 'border-neutral-300'
                    }`}
                  />
                  <div className="flex items-center justify-between mt-1">
                    {errors.description ? (
                      <p className="text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.description}
                      </p>
                    ) : (
                      <p className="text-sm text-neutral-500">
                        Mínimo 10 caracteres ({formData.description.length}/10)
                      </p>
                    )}
                  </div>
                </div>

                {/* SKU y Categoría */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      SKU (Código único) *
                    </label>
                    <input
                      type="text"
                      value={formData.sku}
                      onChange={(e) => handleInputChange('sku', e.target.value.toUpperCase())}
                      placeholder="PROD-123456"
                      className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono ${
                        errors.sku ? 'border-red-300' : 'border-neutral-300'
                      }`}
                    />
                    {errors.sku && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.sku}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Categoría *
                    </label>
                    <select
                      value={formData.category_id}
                      onChange={(e) => handleInputChange('category_id', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        errors.category_id ? 'border-red-300' : 'border-neutral-300'
                      }`}
                    >
                      <option value="">Seleccionar categoría</option>
                      {CATEGORIES.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.icon} {category.name}
                        </option>
                      ))}
                    </select>
                    {errors.category_id && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.category_id}
                      </p>
                    )}
                  </div>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Etiquetas
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.tags.map(tag => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                      >
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(tag)}
                          className="ml-1 text-primary-500 hover:text-primary-700"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      placeholder="Agregar etiqueta"
                      className="flex-1 px-3 py-2 border border-neutral-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                    <button
                      type="button"
                      onClick={addTag}
                      className="px-3 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1">
                    Presiona Enter o el botón + para agregar etiquetas
                  </p>
                </div>
              </div>
            )}

            {/* Paso 2: Precios y stock */}
            {currentStep === 2 && (
              <div className="space-y-6">
                {/* Precios */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Precio de venta * (COP)
                    </label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                      <input
                        type="number"
                        value={formData.price || ''}
                        onChange={(e) => handleInputChange('price', parseFloat(e.target.value) || 0)}
                        placeholder="0"
                        min="1000"
                        step="1000"
                        className={`w-full pl-10 pr-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                          errors.price ? 'border-red-300' : 'border-neutral-300'
                        }`}
                      />
                    </div>
                    {errors.price && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.price}
                      </p>
                    )}
                    {formData.price > 0 && (
                      <p className="mt-1 text-sm text-neutral-600">
                        {formatCOP(formData.price)}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Precio de costo (COP)
                      <span className="text-neutral-500 text-xs ml-1">(opcional)</span>
                    </label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                      <input
                        type="number"
                        value={formData.precio_costo || ''}
                        onChange={(e) => handleInputChange('precio_costo', parseFloat(e.target.value) || 0)}
                        placeholder="0"
                        min="0"
                        step="1000"
                        className={`w-full pl-10 pr-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                          errors.precio_costo ? 'border-red-300' : 'border-neutral-300'
                        }`}
                      />
                    </div>
                    {errors.precio_costo && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.precio_costo}
                      </p>
                    )}
                    {formData.precio_costo > 0 && (
                      <p className="mt-1 text-sm text-neutral-600">
                        {formatCOP(formData.precio_costo)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Calculadora de márgenes */}
                {formData.price > 0 && formData.precio_costo > 0 && (
                  <div className="bg-neutral-50 rounded-lg p-4 border border-neutral-200">
                    <h4 className="flex items-center text-sm font-medium text-neutral-700 mb-3">
                      <Calculator className="w-4 h-4 mr-2" />
                      Cálculo de rentabilidad
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-neutral-500">Margen bruto</p>
                        <p className="font-semibold text-neutral-900">{formatCOP(calc.margenBruto)}</p>
                      </div>
                      <div>
                        <p className="text-neutral-500">% Margen</p>
                        <p className="font-semibold text-secondary-600">{calc.porcentajeMargen.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-neutral-500">Comisión MeStore</p>
                        <p className="font-semibold text-accent-600">{formatCOP(calc.comisionMestocker)}</p>
                      </div>
                      <div>
                        <p className="text-neutral-500">Ganancia real</p>
                        <p className={`font-semibold ${calc.gananciaReal > 0 ? 'text-secondary-600' : 'text-red-600'}`}>
                          {formatCOP(calc.gananciaReal)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Stock y características físicas */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Stock inicial
                    </label>
                    <div className="relative">
                      <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                      <input
                        type="number"
                        value={formData.stock || ''}
                        onChange={(e) => handleInputChange('stock', parseInt(e.target.value) || 0)}
                        placeholder="0"
                        min="0"
                        disabled={formData.is_digital}
                        className={`w-full pl-10 pr-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                          errors.stock ? 'border-red-300' : 'border-neutral-300'
                        } ${formData.is_digital ? 'bg-neutral-100' : ''}`}
                      />
                    </div>
                    {errors.stock && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.stock}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Peso (gramos)
                    </label>
                    <input
                      type="number"
                      value={formData.peso || ''}
                      onChange={(e) => handleInputChange('peso', parseFloat(e.target.value) || 0)}
                      placeholder="0"
                      min="0"
                      disabled={formData.is_digital}
                      className={`w-full px-3 py-2 border border-neutral-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                        formData.is_digital ? 'bg-neutral-100' : ''
                      }`}
                    />
                  </div>

                  <div className="flex flex-col gap-3">
                    <label className="block text-sm font-medium text-neutral-700">
                      Configuración
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_digital}
                        onChange={(e) => handleInputChange('is_digital', e.target.checked)}
                        className="w-4 h-4 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2"
                      />
                      <span className="ml-2 text-sm text-neutral-700">Producto digital</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.is_featured}
                        onChange={(e) => handleInputChange('is_featured', e.target.checked)}
                        className="w-4 h-4 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2"
                      />
                      <span className="ml-2 text-sm text-neutral-700 flex items-center">
                        <Star className="w-3 h-3 mr-1" />
                        Producto destacado
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Paso 3: Imágenes */}
            {currentStep === 3 && (
              <div className="space-y-6">
                {/* Upload de imágenes */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Imágenes del producto
                  </label>
                  <div
                    className="border-2 border-dashed border-neutral-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Camera className="h-12 w-12 text-neutral-400 mx-auto mb-2" />
                    <p className="text-sm text-neutral-600 mb-1">
                      Arrastra imágenes aquí o haz clic para seleccionar
                    </p>
                    <p className="text-xs text-neutral-500">
                      Máximo 8 imágenes, 5MB cada una. Formatos: JPG, PNG, WebP
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  {errors.images && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.images}
                    </p>
                  )}
                </div>

                {/* Preview de imágenes */}
                {previewImages.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-neutral-700 mb-3">
                      Vista previa ({previewImages.length}/8)
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {previewImages.map((src, index) => (
                        <div key={index} className="relative aspect-square bg-neutral-100 rounded-lg overflow-hidden">
                          <img
                            src={src}
                            alt={`Preview ${index + 1}`}
                            className="w-full h-full object-cover"
                          />
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                          {index === 0 && (
                            <div className="absolute bottom-2 left-2 bg-primary-600 text-white text-xs px-2 py-1 rounded">
                              Principal
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </form>
        </div>

        {/* Footer con navegación */}
        <div className="flex items-center justify-between p-6 border-t border-neutral-200 bg-neutral-50">
          <div className="flex items-center gap-2">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={() => setCurrentStep(prev => prev - 1)}
                className="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 transition-colors"
              >
                Anterior
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 transition-colors"
            >
              Cancelar
            </button>

            {currentStep < 3 ? (
              <button
                type="button"
                onClick={() => {
                  if (currentStep === 1 && validateForm()) {
                    setCurrentStep(2);
                  } else if (currentStep === 2) {
                    setCurrentStep(3);
                  }
                }}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors"
              >
                Siguiente
              </button>
            ) : (
              <button
                type="submit"
                disabled={isSubmitting}
                onClick={handleSubmit}
                className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    {product ? 'Actualizar producto' : 'Crear producto'}
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorProductForm;