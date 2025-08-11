// Componente breadcrumb básico para navegación
import React from 'react';
import { Link } from 'react-router-dom';
import { useBreadcrumb } from '../../../hooks/useBreadcrumb';

export const Breadcrumb: React.FC = () => {
  const breadcrumbs = useBreadcrumb();
  
  return (
    <nav aria-label="breadcrumb">
      <ol style={{ display: 'flex', listStyle: 'none', padding: 0, margin: 0 }}>
        {breadcrumbs.map((item, index) => (
          <li key={item.path}>
            {item.isActive ? (
              <span>{item.label}</span>
            ) : (
              <Link to={item.path}>{item.label}</Link>
            )}
            {index < breadcrumbs.length - 1 && <span> / </span>}
          </li>
        ))}
      </ol>
    </nav>
  );
};