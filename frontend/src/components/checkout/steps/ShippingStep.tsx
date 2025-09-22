import React, { useState, useEffect } from 'react';
import { useCheckoutStore, ShippingAddress } from '../../../stores/checkoutStore';
import AddressForm from '../AddressForm';

const ShippingStep: React.FC = () => {
  const {
    shipping_address,
    saved_addresses,
    shipping_cost,
    setShippingAddress,
    setShippingCost,
    goToNextStep,
    goToPreviousStep,
    canProceedToNextStep,
    setError,
    clearErrors
  } = useCheckoutStore();

  const [selectedAddressId, setSelectedAddressId] = useState<string>('');
  const [showNewAddressForm, setShowNewAddressForm] = useState(false);
  const [isCalculatingShipping, setIsCalculatingShipping] = useState(false);

  useEffect(() => {
    clearErrors();

    // If there's a shipping address selected, set it as selected
    if (shipping_address?.id) {
      setSelectedAddressId(shipping_address.id);
    }
    // If no address is selected but there are saved addresses, select the default one
    else if (saved_addresses.length > 0) {
      const defaultAddress = saved_addresses.find(addr => addr.is_default);
      if (defaultAddress) {
        setSelectedAddressId(defaultAddress.id || '');
        setShippingAddress(defaultAddress);
      }
    }
    // If no saved addresses, show the form
    else {
      setShowNewAddressForm(true);
    }
  }, [saved_addresses, shipping_address, setShippingAddress, clearErrors]);

  const handleAddressSelect = async (addressId: string) => {
    const address = saved_addresses.find(addr => addr.id === addressId);
    if (address) {
      setSelectedAddressId(addressId);
      setShippingAddress(address);
      await calculateShippingCost(address);
    }
  };

  const calculateShippingCost = async (address: ShippingAddress) => {
    setIsCalculatingShipping(true);
    try {
      // Simulate shipping cost calculation
      // In real implementation, this would call a shipping API
      const baseCost = 15000; // Base shipping cost
      const distanceFactor = address.city?.toLowerCase().includes('bogotá') ? 1 : 1.5;
      const calculatedCost = baseCost * distanceFactor;

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      setShippingCost(calculatedCost);
    } catch (error) {
      console.error('Error calculating shipping cost:', error);
      setError('No se pudo calcular el costo de envío. Inténtalo de nuevo.');
      setShippingCost(15000); // Fallback cost
    } finally {
      setIsCalculatingShipping(false);
    }
  };

  const handleNewAddressAdded = (address: ShippingAddress) => {
    setShippingAddress(address);
    setShowNewAddressForm(false);
    calculateShippingCost(address);
  };

  const handleContinue = () => {
    if (canProceedToNextStep()) {
      goToNextStep();
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Información de Envío
        </h2>
        <p className="text-gray-600">
          Selecciona o agrega una dirección de entrega
        </p>
      </div>

      {/* Saved Addresses */}
      {saved_addresses.length > 0 && !showNewAddressForm && (
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Direcciones Guardadas
          </h3>

          <div className="space-y-3">
            {saved_addresses.map((address) => (
              <div
                key={address.id}
                className={`
                  border rounded-lg p-4 cursor-pointer transition-colors
                  ${selectedAddressId === address.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                  }
                `}
                onClick={() => handleAddressSelect(address.id || '')}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <input
                      type="radio"
                      name="shipping-address"
                      value={address.id}
                      checked={selectedAddressId === address.id}
                      onChange={() => handleAddressSelect(address.id || '')}
                      className="mt-1 text-blue-600 focus:ring-blue-500"
                    />

                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{address.name}</h4>
                        {address.is_default && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            Predeterminada
                          </span>
                        )}
                      </div>

                      <p className="text-gray-600 text-sm mt-1">{address.address}</p>
                      <p className="text-gray-600 text-sm">
                        {address.city}
                        {address.department && `, ${address.department}`}
                      </p>
                      {address.postal_code && (
                        <p className="text-gray-600 text-sm">CP: {address.postal_code}</p>
                      )}
                      <p className="text-gray-600 text-sm">{address.phone}</p>
                      {address.additional_info && (
                        <p className="text-gray-500 text-xs mt-1 italic">
                          {address.additional_info}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setShowNewAddressForm(true)}
            className="mt-4 text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            + Agregar nueva dirección
          </button>
        </div>
      )}

      {/* New Address Form */}
      {showNewAddressForm && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {saved_addresses.length > 0 ? 'Nueva Dirección' : 'Agregar Dirección de Envío'}
            </h3>
            {saved_addresses.length > 0 && (
              <button
                onClick={() => setShowNewAddressForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          <AddressForm
            onSubmit={handleNewAddressAdded}
            onCancel={saved_addresses.length > 0 ? () => setShowNewAddressForm(false) : undefined}
          />
        </div>
      )}

      {/* Shipping Cost */}
      {shipping_address && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            Costo de Envío
          </h3>

          {isCalculatingShipping ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">Calculando costo de envío...</span>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Envío estándar (3-5 días hábiles)</span>
                <span className="font-semibold text-gray-900">
                  {shipping_cost === 0 ? 'Gratis' : formatCurrency(shipping_cost)}
                </span>
              </div>

              <div className="text-sm text-gray-500">
                Entrega estimada: {new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toLocaleDateString('es-CO', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={goToPreviousStep}
          className="text-gray-600 hover:text-gray-800 font-medium"
        >
          ← Volver al Carrito
        </button>

        <button
          onClick={handleContinue}
          disabled={!canProceedToNextStep() || isCalculatingShipping}
          className={`
            px-6 py-3 rounded-md font-medium transition-colors
            ${canProceedToNextStep() && !isCalculatingShipping
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isCalculatingShipping ? 'Calculando...' : 'Continuar al Pago →'}
        </button>
      </div>
    </div>
  );
};

export default ShippingStep;