import { useState, useMemo } from 'react';
import { VendorProfile } from '../types/user.types';

export const useVendorList = (vendors: VendorProfile[]) => {
  const [selectedEstado, setSelectedEstado] = useState('todos');
  const [selectedTipo, setSelectedTipo] = useState('todos');

  const filteredVendors = useMemo(() => {
    return vendors.filter(vendor => {
      const estadoMatch = selectedEstado === 'todos' || 
        (selectedEstado === 'activo' && vendor.profileStatus.isActive) ||
        (selectedEstado === 'inactivo' && vendor.profileStatus.isActive === false);
      return estadoMatch;
    });
  }, [vendors, selectedEstado, selectedTipo]);

  return {
    filteredVendors,
    selectedEstado,
    selectedTipo,
    setSelectedEstado,
    setSelectedTipo,
  };
};