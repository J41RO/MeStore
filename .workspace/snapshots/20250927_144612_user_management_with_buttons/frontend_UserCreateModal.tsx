import React, { useState } from 'react';
import { CreateUserData, User, superuserService } from '../../services/superuserService';

interface UserCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUserCreated: (newUser: User) => void;
}

interface FormErrors {
  [key: string]: string;
}

const UserCreateModal: React.FC<UserCreateModalProps> = ({
  isOpen,
  onClose,
  onUserCreated,
}) => {
  const [formData, setFormData] = useState<CreateUserData>({
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    user_type: 'BUYER',
    security_clearance_level: 1,
    telefono: '',
    documento: '',
  });

  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'basic' | 'details' | 'security'>('basic');

  const handleInputChange = (key: keyof CreateUserData, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    // Clear error when user starts typing
    if (errors[key]) {
      setErrors(prev => ({ ...prev, [key]: '' }));
    }
  };

  const validateStep = (currentStep: string): boolean => {
    const newErrors: FormErrors = {};

    if (currentStep === 'basic') {
      if (!formData.email) newErrors.email = 'Email is required';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email address';
      }

      if (!formData.password) newErrors.password = 'Password is required';
      else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
        newErrors.password = 'Password must contain uppercase, lowercase, and number';
      }

      if (!confirmPassword) newErrors.confirmPassword = 'Please confirm password';
      else if (formData.password !== confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }

      if (!formData.nombre) newErrors.nombre = 'First name is required';
      if (!formData.apellido) newErrors.apellido = 'Last name is required';
    }

    if (currentStep === 'details') {
      if (formData.telefono && !/^\+?[\d\s\-\(\)]+$/.test(formData.telefono)) {
        newErrors.telefono = 'Please enter a valid phone number';
      }

      if (formData.documento && formData.documento.length < 5) {
        newErrors.documento = 'Document must be at least 5 characters';
      }
    }

    if (currentStep === 'security') {
      if (!formData.user_type) newErrors.user_type = 'User type is required';

      if (formData.security_clearance_level < 1 || formData.security_clearance_level > 7) {
        newErrors.security_clearance_level = 'Security level must be between 1 and 7';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      if (step === 'basic') setStep('details');
      else if (step === 'details') setStep('security');
    }
  };

  const handlePrevious = () => {
    if (step === 'security') setStep('details');
    else if (step === 'details') setStep('basic');
  };

  const handleSubmit = async () => {
    if (!validateStep('security')) return;

    setLoading(true);
    try {
      const newUser = await superuserService.createUser(formData);
      onUserCreated(newUser);
      handleClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Error creating user';
      if (errorMessage.includes('email')) {
        setErrors({ email: 'Email already exists' });
        setStep('basic');
      } else {
        setErrors({ general: errorMessage });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      email: '',
      password: '',
      nombre: '',
      apellido: '',
      user_type: 'BUYER',
      security_clearance_level: 1,
      telefono: '',
      documento: '',
    });
    setConfirmPassword('');
    setErrors({});
    setStep('basic');
    onClose();
  };

  const getStepNumber = (stepName: string): number => {
    switch (stepName) {
      case 'basic': return 1;
      case 'details': return 2;
      case 'security': return 3;
      default: return 1;
    }
  };

  const getUserTypeIcon = (type: string) => {
    switch (type) {
      case 'BUYER': return '🛒';
      case 'VENDOR': return '🏪';
      case 'ADMIN': return '⚙';
      case 'SUPERUSER': return '👑';
      default: return '👤';
    }
  };

  const getSecurityLevelDescription = (level: number) => {
    if (level >= 6) return 'Critical - Maximum security access';
    if (level >= 5) return 'High - Administrative privileges';
    if (level >= 3) return 'Medium - Enhanced access';
    return 'Standard - Basic user access';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={handleClose}
        ></div>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Create New User</h3>
                <p className="text-sm text-gray-500">
                  Step {getStepNumber(step)} of 3: {step === 'basic' ? 'Basic Information' : step === 'details' ? 'Additional Details' : 'Security Settings'}
                </p>
              </div>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="bg-gray-50 px-6 py-3">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${step === 'basic' ? 'text-blue-600' : step !== 'basic' ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                  step === 'basic' ? 'bg-blue-100' : getStepNumber(step) > 1 ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  {getStepNumber(step) > 1 ? '✓' : '1'}
                </div>
                <span className="ml-2 text-sm">Basic</span>
              </div>
              <div className="flex-1 border-t border-gray-300"></div>
              <div className={`flex items-center ${step === 'details' ? 'text-blue-600' : getStepNumber(step) > 2 ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                  step === 'details' ? 'bg-blue-100' : getStepNumber(step) > 2 ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  {getStepNumber(step) > 2 ? '✓' : '2'}
                </div>
                <span className="ml-2 text-sm">Details</span>
              </div>
              <div className="flex-1 border-t border-gray-300"></div>
              <div className={`flex items-center ${step === 'security' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                  step === 'security' ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  3
                </div>
                <span className="ml-2 text-sm">Security</span>
              </div>
            </div>
          </div>

          {/* Form Content */}
          <div className="p-6">
            {errors.general && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {errors.general}
              </div>
            )}

            {/* Step 1: Basic Information */}
            {step === 'basic' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.email ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                    placeholder="user@example.com"
                  />
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      First Name *
                    </label>
                    <input
                      type="text"
                      value={formData.nombre}
                      onChange={(e) => handleInputChange('nombre', e.target.value)}
                      className={`mt-1 block w-full px-3 py-2 border ${
                        errors.nombre ? 'border-red-300' : 'border-gray-300'
                      } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                    />
                    {errors.nombre && <p className="mt-1 text-sm text-red-600">{errors.nombre}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      value={formData.apellido}
                      onChange={(e) => handleInputChange('apellido', e.target.value)}
                      className={`mt-1 block w-full px-3 py-2 border ${
                        errors.apellido ? 'border-red-300' : 'border-gray-300'
                      } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                    />
                    {errors.apellido && <p className="mt-1 text-sm text-red-600">{errors.apellido}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Password *
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.password ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  />
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
                  <p className="mt-1 text-xs text-gray-500">
                    Must be at least 8 characters with uppercase, lowercase, and number
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Confirm Password *
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  />
                  {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>}
                </div>
              </div>
            )}

            {/* Step 2: Additional Details */}
            {step === 'details' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => handleInputChange('telefono', e.target.value)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.telefono ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                    placeholder="+1 (555) 123-4567"
                  />
                  {errors.telefono && <p className="mt-1 text-sm text-red-600">{errors.telefono}</p>}
                  <p className="mt-1 text-xs text-gray-500">Optional - Include country code if international</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Document/ID Number
                  </label>
                  <input
                    type="text"
                    value={formData.documento}
                    onChange={(e) => handleInputChange('documento', e.target.value)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.documento ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                    placeholder="ID, Passport, or Tax ID"
                  />
                  {errors.documento && <p className="mt-1 text-sm text-red-600">{errors.documento}</p>}
                  <p className="mt-1 text-xs text-gray-500">Optional - Government issued ID or business tax ID</p>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-start">
                    <div className="text-blue-400 mr-3 mt-0.5">ℹ</div>
                    <div>
                      <h4 className="text-sm font-medium text-blue-900">Additional Information</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Phone and document information can help with verification and account recovery.
                        Both fields are optional but recommended for better security.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Security Settings */}
            {step === 'security' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    User Type *
                  </label>
                  <select
                    value={formData.user_type}
                    onChange={(e) => handleInputChange('user_type', e.target.value as any)}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.user_type ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  >
                    <option value="BUYER">{getUserTypeIcon('BUYER')} Buyer - Customer account</option>
                    <option value="VENDOR">{getUserTypeIcon('VENDOR')} Vendor - Seller account</option>
                    <option value="ADMIN">{getUserTypeIcon('ADMIN')} Admin - Administrator account</option>
                    <option value="SUPERUSER">{getUserTypeIcon('SUPERUSER')} Superuser - Full system access</option>
                  </select>
                  {errors.user_type && <p className="mt-1 text-sm text-red-600">{errors.user_type}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Security Clearance Level *
                  </label>
                  <select
                    value={formData.security_clearance_level}
                    onChange={(e) => handleInputChange('security_clearance_level', parseInt(e.target.value))}
                    className={`mt-1 block w-full px-3 py-2 border ${
                      errors.security_clearance_level ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  >
                    <option value={1}>Level 1 - Standard</option>
                    <option value={2}>Level 2 - Standard+</option>
                    <option value={3}>Level 3 - Medium</option>
                    <option value={4}>Level 4 - Medium+</option>
                    <option value={5}>Level 5 - High</option>
                    <option value={6}>Level 6 - High+</option>
                    <option value={7}>Level 7 - Critical</option>
                  </select>
                  {errors.security_clearance_level && (
                    <p className="mt-1 text-sm text-red-600">{errors.security_clearance_level}</p>
                  )}
                  <p className="mt-1 text-xs text-gray-500">
                    {getSecurityLevelDescription(formData.security_clearance_level)}
                  </p>
                </div>

                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-start">
                    <div className="text-yellow-400 mr-3 mt-0.5">⚠</div>
                    <div>
                      <h4 className="text-sm font-medium text-yellow-900">Security Notice</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        The new user will be created as active and verified by default.
                        They will receive login credentials and can immediately access the system
                        based on their assigned user type and security level.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3 flex justify-between">
            <div>
              {step !== 'basic' && (
                <button
                  onClick={handlePrevious}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  ← Previous
                </button>
              )}
            </div>
            <div className="flex space-x-3">
              <button
                onClick={handleClose}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              {step === 'security' ? (
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </div>
                  ) : (
                    '✓ Create User'
                  )}
                </button>
              ) : (
                <button
                  onClick={handleNext}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Next →
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserCreateModal;