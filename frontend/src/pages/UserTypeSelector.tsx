import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, Store, Building2, ArrowRight, Check } from 'lucide-react';

type UserType = 'BUYER' | 'VENDOR';
type VendorType = 'persona_natural' | 'persona_juridica';

interface TypeOption {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  popular?: boolean;
}

const UserTypeSelector: React.FC = () => {
  const navigate = useNavigate();
  const [selectedUserType, setSelectedUserType] = useState<UserType | null>(null);
  const [selectedVendorType, setSelectedVendorType] = useState<VendorType | null>(null);

  const buyerOption: TypeOption = {
    id: 'buyer',
    title: 'Quiero Comprar',
    description: 'Accede a productos y servicios de vendedores verificados',
    icon: <ShoppingBag className="w-12 h-12" />,
    popular: true
  };

  const vendorOptions: TypeOption[] = [
    {
      id: 'persona_natural',
      title: 'Persona Natural',
      description: 'Vende como persona independiente con tu cédula',
      icon: <Store className="w-10 h-10" />
    },
    {
      id: 'persona_juridica',
      title: 'Persona Jurídica',
      description: 'Registra tu empresa con NIT y documentos legales',
      icon: <Building2 className="w-10 h-10" />
    }
  ];

  const handleContinue = () => {
    if (!selectedUserType) return;

    if (selectedUserType === 'BUYER') {
      navigate('/register', {
        state: {
          userType: 'BUYER',
          vendorType: null
        }
      });
    } else if (selectedUserType === 'VENDOR' && selectedVendorType) {
      navigate('/register', {
        state: {
          userType: 'VENDOR',
          vendorType: selectedVendorType
        }
      });
    }
  };

  const canContinue = selectedUserType === 'BUYER' ||
                     (selectedUserType === 'VENDOR' && selectedVendorType !== null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Únete a MeStocker
          </h1>
          <p className="text-xl text-gray-600">
            ¿Cómo quieres usar nuestra plataforma?
          </p>
        </div>

        {/* Main Selection - Buyer vs Vendor */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Buyer Card */}
          <button
            onClick={() => {
              setSelectedUserType('BUYER');
              setSelectedVendorType(null);
            }}
            className={`relative p-8 rounded-2xl border-2 transition-all duration-200 text-left ${
              selectedUserType === 'BUYER'
                ? 'border-blue-600 bg-blue-50 shadow-xl scale-105'
                : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-lg'
            }`}
          >
            {buyerOption.popular && (
              <div className="absolute -top-3 -right-3 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                Popular
              </div>
            )}

            {selectedUserType === 'BUYER' && (
              <div className="absolute top-4 right-4">
                <div className="bg-blue-600 rounded-full p-1">
                  <Check className="w-5 h-5 text-white" />
                </div>
              </div>
            )}

            <div className="flex flex-col items-center text-center space-y-4">
              <div className={`${selectedUserType === 'BUYER' ? 'text-blue-600' : 'text-gray-600'}`}>
                {buyerOption.icon}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {buyerOption.title}
                </h3>
                <p className="text-gray-600">
                  {buyerOption.description}
                </p>
              </div>
            </div>
          </button>

          {/* Vendor Card */}
          <button
            onClick={() => setSelectedUserType('VENDOR')}
            className={`relative p-8 rounded-2xl border-2 transition-all duration-200 text-left ${
              selectedUserType === 'VENDOR'
                ? 'border-purple-600 bg-purple-50 shadow-xl scale-105'
                : 'border-gray-200 bg-white hover:border-purple-300 hover:shadow-lg'
            }`}
          >
            {selectedUserType === 'VENDOR' && (
              <div className="absolute top-4 right-4">
                <div className="bg-purple-600 rounded-full p-1">
                  <Check className="w-5 h-5 text-white" />
                </div>
              </div>
            )}

            <div className="flex flex-col items-center text-center space-y-4">
              <div className={`${selectedUserType === 'VENDOR' ? 'text-purple-600' : 'text-gray-600'}`}>
                <Store className="w-12 h-12" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Quiero Vender
                </h3>
                <p className="text-gray-600">
                  Ofrece tus productos y servicios en nuestra plataforma
                </p>
              </div>
            </div>
          </button>
        </div>

        {/* Vendor Type Selection (only shown if VENDOR is selected) */}
        {selectedUserType === 'VENDOR' && (
          <div className="mb-8 animate-fadeIn">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
              Selecciona tu tipo de vendedor
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {vendorOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedVendorType(option.id as VendorType)}
                  className={`relative p-6 rounded-xl border-2 transition-all duration-200 text-left ${
                    selectedVendorType === option.id
                      ? 'border-purple-600 bg-purple-50 shadow-lg'
                      : 'border-gray-200 bg-white hover:border-purple-300 hover:shadow-md'
                  }`}
                >
                  {selectedVendorType === option.id && (
                    <div className="absolute top-3 right-3">
                      <div className="bg-purple-600 rounded-full p-1">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}

                  <div className="flex items-start space-x-4">
                    <div className={`${selectedVendorType === option.id ? 'text-purple-600' : 'text-gray-600'}`}>
                      {option.icon}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-gray-900 mb-1">
                        {option.title}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {option.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Continue Button */}
        <div className="flex justify-center">
          <button
            onClick={handleContinue}
            disabled={!canContinue}
            className={`flex items-center space-x-2 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 ${
              canContinue
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <span>Continuar</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            ¿Ya tienes cuenta?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-blue-600 font-semibold hover:underline"
            >
              Inicia sesión
            </button>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default UserTypeSelector;
