# DashboardLayout Component

## Descripción

Componente de layout principal para el dashboard de MeStore. Proporciona una estructura responsive con sidebar de navegación y área de contenido principal.

## Props

### DashboardLayoutProps

```typescript
interface DashboardLayoutProps {
  children: React.ReactNode; // Contenido a renderizar en el área principal
}
Características
🖥️ Desktop

Sidebar fijo en el lado izquierdo (264px de ancho)
Navegación visible permanentemente
Header con título y avatar de usuario

📱 Mobile

Sidebar colapsable con overlay
Botón hamburger en el header
Auto-cierre del sidebar al navegar
Animaciones slide suaves

🎨 Navegación

4 secciones principales: Dashboard, Productos, Órdenes, Configuración
Estados activos basados en la ruta actual
Hover effects y transiciones
Prevención de navegación por defecto con manejo manual

♿ Accesibilidad

Estructura semántica correcta
Focus states para navegación por teclado
Responsive design para diferentes tamaños de pantalla

Uso
tsximport DashboardLayout from './components/DashboardLayout';

function App() {
  return (
    <DashboardLayout>
      <div>Contenido del dashboard</div>
    </DashboardLayout>
  );
}
Dependencias

React Router DOM (useLocation hook)
Tailwind CSS para estilos
React hooks (useState)

Estructura de Archivos

src/components/DashboardLayout.tsx - Componente principal
src/components/__tests__/DashboardLayout.test.tsx - Tests unitarios
src/components/DashboardLayout.md - Esta documentación

Testing
Ejecutar tests específicos:
bashnpm test -- --testPathPattern=DashboardLayout
Notas de Implementación

Usa Tailwind classes inline para mejor performance
Template strings conservadores para evitar problemas de parsing
Estado local para control del sidebar mobile
Navegación manual via window.location.href para compatibilidad
```
