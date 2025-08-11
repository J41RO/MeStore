// Hook personalizado para generar breadcrumbs automáticamente
import { useLocation } from 'react-router-dom';

// Mapeo de rutas técnicas a labels legibles en español
const routeLabels: Record<string, string> = {
  'dashboard': 'Panel de Control',
  'productos': 'Productos',
  'vendedores': 'Vendedores',
  'compradores': 'Compradores',
  'auth': 'Autenticación',
  'login': 'Iniciar Sesión',
  'register': 'Registro',
  'perfil': 'Perfil',
  'configuracion': 'Configuración',
  'reportes': 'Reportes'
};

// Función para obtener label personalizado o capitalizado
const getLabel = (segment: string): string => {
  return routeLabels[segment.toLowerCase()] || 
         segment.charAt(0).toUpperCase() + segment.slice(1);
};

export interface BreadcrumbItem {
  label: string;
  path: string;
  isActive: boolean;
}

export const useBreadcrumb = (): BreadcrumbItem[] => {
  const location = useLocation();
  
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Inicio', path: '/', isActive: false }
  ];
  
  // Generar breadcrumbs acumulativos
  pathSegments.forEach((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/');
    const isActive = index === pathSegments.length - 1;
    
    breadcrumbs.push({
      label: getLabel(segment),
      path,
      isActive
    });
  });
  
  return breadcrumbs;
};