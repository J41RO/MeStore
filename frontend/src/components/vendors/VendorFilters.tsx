// ~/src/components/vendors/VendorFilters.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente de filtros de vendors
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------



interface VendorFiltersProps {
  onEstadoChange: (estado: string) => void;
  onTipoChange: (tipo: string) => void;
  selectedEstado: string;
  selectedTipo: string;
}

const ESTADOS = ['todos', 'activo', 'inactivo', 'pendiente'];
const TIPOS_CUENTA = ['todos', 'básica', 'premium', 'empresarial'];

export default function VendorFilters({ onEstadoChange, onTipoChange, selectedEstado, selectedTipo }: VendorFiltersProps) {
  return (
    <div className="vendor-filters">
      <select value={selectedEstado} onChange={(e) => onEstadoChange(e.target.value)}>
        {ESTADOS.map(estado => <option key={estado} value={estado}>{estado}</option>)}
      </select>
      <select value={selectedTipo} onChange={(e) => onTipoChange(e.target.value)}>
        {TIPOS_CUENTA.map(tipo => <option key={tipo} value={tipo}>{tipo}</option>)}
      </select>
    </div>
  );
}