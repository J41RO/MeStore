import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { vendorApiService, VendorRegistrationData } from '../services/vendorApiService';
import '../styles/vendor-registration-simple.css';

interface FormErrors {
  [key: string]: string;
}

export const VendorRegistration: React.FC = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [successMessage, setSuccessMessage] = useState('');

  const [formData, setFormData] = useState<VendorRegistrationData>({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    business_name: '',
    city: '',
    business_type: 'persona_natural',
    primary_category: 'ropa_femenina',
    terms_accepted: false,
  });

  const [confirmPassword, setConfirmPassword] = useState('');

  const categories = [
    { value: 'ropa_femenina', label: 'Ropa Femenina' },
    { value: 'ropa_masculina', label: 'Ropa Masculina' },
    { value: 'accesorios', label: 'Accesorios' },
    { value: 'calzado', label: 'Calzado' },
    { value: 'hogar', label: 'Hogar y Decoración' },
    { value: 'tecnologia', label: 'Tecnología' },
    { value: 'deportes', label: 'Deportes' },
    { value: 'belleza', label: 'Belleza' },
    { value: 'juguetes', label: 'Juguetes' },
    { value: 'libros', label: 'Libros' },
    { value: 'otros', label: 'Otros' },
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Limpiar error del campo cuando usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validar email
    if (!formData.email) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    // Validar password
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 8) {
      newErrors.password = 'La contraseña debe tener al menos 8 caracteres';
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = 'La contraseña debe contener al menos una mayúscula';
    } else if (!/[a-z]/.test(formData.password)) {
      newErrors.password = 'La contraseña debe contener al menos una minúscula';
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = 'La contraseña debe contener al menos un número';
    }

    // Validar confirmación de password
    if (formData.password !== confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }

    // Validar nombre completo
    if (!formData.full_name || formData.full_name.trim().length < 2) {
      newErrors.full_name = 'El nombre completo es requerido';
    }

    // Validar teléfono
    if (!formData.phone) {
      newErrors.phone = 'El teléfono es requerido';
    } else if (!/^(\+57|57)?[3][0-9]{9}$/.test(formData.phone.replace(/[\s-]/g, ''))) {
      newErrors.phone = 'Teléfono colombiano inválido (ej: +573001234567)';
    }

    // Validar nombre del negocio
    if (!formData.business_name || formData.business_name.trim().length < 2) {
      newErrors.business_name = 'El nombre del negocio es requerido';
    }

    // Validar ciudad
    if (!formData.city || formData.city.trim().length < 2) {
      newErrors.city = 'La ciudad es requerida';
    }

    // Validar términos
    if (!formData.terms_accepted) {
      newErrors.terms_accepted = 'Debes aceptar los términos y condiciones';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});
    setSuccessMessage('');

    try {
      const response = await vendorApiService.register(formData);

      setSuccessMessage(response.message);

      // Redirigir después de 2 segundos
      setTimeout(() => {
        // Puedes redirigir al login o directamente al dashboard
        navigate('/login', {
          state: {
            message: 'Registro exitoso. Por favor inicia sesión.',
            email: formData.email
          }
        });
      }, 2000);

    } catch (error: any) {
      console.error('Error al registrar vendor:', error);

      if (error.status === 400) {
        setErrors({ general: error.message });
      } else if (error.details && error.details.length > 0) {
        const fieldErrors: FormErrors = {};
        error.details.forEach((detail: any) => {
          fieldErrors[detail.field] = detail.message;
        });
        setErrors(fieldErrors);
      } else {
        setErrors({ general: error.message || 'Error al registrar. Intenta nuevamente.' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="vendor-registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h1>Únete a MeStocker</h1>
          <p className="subtitle">Comienza a vender tus productos hoy mismo</p>
        </div>

        {successMessage && (
          <div className="success-banner">
            <span className="success-icon">✓</span>
            {successMessage}
          </div>
        )}

        {errors.general && (
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="registration-form">
          {/* Sección: Información Personal */}
          <div className="form-section">
            <h2 className="section-title">Información Personal</h2>

            <div className="form-group">
              <label htmlFor="full_name">Nombre Completo *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className={errors.full_name ? 'input-error' : ''}
                placeholder="Ej: María González"
                disabled={isSubmitting}
              />
              {errors.full_name && <span className="error-text">{errors.full_name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={errors.email ? 'input-error' : ''}
                placeholder="tu@email.com"
                disabled={isSubmitting}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="phone">Teléfono *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className={errors.phone ? 'input-error' : ''}
                placeholder="+573001234567"
                disabled={isSubmitting}
              />
              {errors.phone && <span className="error-text">{errors.phone}</span>}
              <small className="input-hint">Formato: +573001234567</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="password">Contraseña *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={errors.password ? 'input-error' : ''}
                  placeholder="Mínimo 8 caracteres"
                  disabled={isSubmitting}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirmar Contraseña *</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    if (errors.confirmPassword) {
                      setErrors(prev => ({ ...prev, confirmPassword: '' }));
                    }
                  }}
                  className={errors.confirmPassword ? 'input-error' : ''}
                  placeholder="Repite tu contraseña"
                  disabled={isSubmitting}
                />
                {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
              </div>
            </div>
          </div>

          {/* Sección: Información del Negocio */}
          <div className="form-section">
            <h2 className="section-title">Información del Negocio</h2>

            <div className="form-group">
              <label htmlFor="business_name">Nombre del Negocio *</label>
              <input
                type="text"
                id="business_name"
                name="business_name"
                value={formData.business_name}
                onChange={handleInputChange}
                className={errors.business_name ? 'input-error' : ''}
                placeholder="Ej: MaríaStyle"
                disabled={isSubmitting}
              />
              {errors.business_name && <span className="error-text">{errors.business_name}</span>}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="business_type">Tipo de Negocio *</label>
                <select
                  id="business_type"
                  name="business_type"
                  value={formData.business_type}
                  onChange={handleInputChange}
                  className={errors.business_type ? 'input-error' : ''}
                  disabled={isSubmitting}
                >
                  <option value="persona_natural">Persona Natural</option>
                  <option value="empresa">Empresa</option>
                </select>
                {errors.business_type && <span className="error-text">{errors.business_type}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="city">Ciudad *</label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  className={errors.city ? 'input-error' : ''}
                  placeholder="Ej: Bucaramanga"
                  disabled={isSubmitting}
                />
                {errors.city && <span className="error-text">{errors.city}</span>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="primary_category">Categoría Principal *</label>
              <select
                id="primary_category"
                name="primary_category"
                value={formData.primary_category}
                onChange={handleInputChange}
                className={errors.primary_category ? 'input-error' : ''}
                disabled={isSubmitting}
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
              {errors.primary_category && <span className="error-text">{errors.primary_category}</span>}
            </div>
          </div>

          {/* Sección: Términos y Condiciones */}
          <div className="form-section">
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleInputChange}
                  className={errors.terms_accepted ? 'input-error' : ''}
                  disabled={isSubmitting}
                />
                <span>
                  Acepto los <a href="/terms" target="_blank" rel="noopener noreferrer">términos y condiciones</a> y la{' '}
                  <a href="/privacy" target="_blank" rel="noopener noreferrer">política de privacidad</a>
                </span>
              </label>
              {errors.terms_accepted && <span className="error-text">{errors.terms_accepted}</span>}
            </div>
          </div>

          {/* Botón de Submit */}
          <div className="form-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Registrando...' : 'Crear Cuenta'}
            </button>
          </div>

          <div className="form-footer">
            <p>
              ¿Ya tienes cuenta?{' '}
              <a href="/login" className="link-primary">
                Inicia sesión
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VendorRegistration;
