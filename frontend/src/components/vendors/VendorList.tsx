// ~/src/components/vendors/VendorList.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente de tabla de vendors con filtros por estado y tipo de cuenta
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { useState } from 'react';
import { VendorProfile } from '../../types/user.types';
import VendorFilters from './VendorFilters';

interface VendorListProps {
  vendors: VendorProfile[];
  loading: boolean;
}

export default function VendorList({ vendors, loading }: VendorListProps) {
  const [selectedEstado, setSelectedEstado] = useState('todos');
  const [selectedTipo, setSelectedTipo] = useState('todos');
  const filteredVendors = vendors.filter(vendor => {
    const estadoMatch = selectedEstado === 'todos' || 
      (selectedEstado === 'activo' && vendor.profileStatus.isActive) ||
      (selectedEstado === 'inactivo' && vendor.profileStatus.isActive === false);
    return estadoMatch;
  });

  return (
    <div className="vendor-list-container">
      <VendorFilters 
        onEstadoChange={setSelectedEstado}
        onTipoChange={setSelectedTipo}
        selectedEstado={selectedEstado}
        selectedTipo={selectedTipo}
      />
      <h2>Vendor List</h2>
      {loading ? <p>Cargando...</p> : <p>{filteredVendors.length} vendors encontrados</p>}
    </div>
  );
}