import React from 'react';
import { CardProps, CardHeaderProps, CardBodyProps, CardFooterProps } from './Card.types';

// Componente principal Card
const CardComponent: React.FC<CardProps> = ({
  variant = 'default',
  children,
  className,
  ...props
}) => {
  const baseClasses = 'rounded-lg overflow-hidden';
  
  const variantClasses = {
    default: 'card-mestocker',
    outlined: 'border-2 border-neutral-200 bg-white',
    elevated: 'shadow-mestocker-lg bg-white border border-neutral-100',
    flat: 'bg-neutral-50',
  };

  const combinedClasses = [
    baseClasses,
    variantClasses[variant],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={combinedClasses} {...props}>
      {children}
    </div>
  );
};

// Sub-componentes
const CardHeader: React.FC<CardHeaderProps> = ({ children, className, ...props }) => {
  return (
    <div className={`px-6 py-4 border-b border-neutral-200 ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

const CardBody: React.FC<CardBodyProps> = ({ children, className, ...props }) => {
  return (
    <div className={`px-6 py-4 ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

const CardFooter: React.FC<CardFooterProps> = ({ children, className, ...props }) => {
  return (
    <div className={`px-6 py-4 border-t border-neutral-200 bg-neutral-50 ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

// Crear compound component con typing correcto
interface CardCompoundComponent extends React.FC<CardProps> {
  Header: React.FC<CardHeaderProps>;
  Body: React.FC<CardBodyProps>;
  Footer: React.FC<CardFooterProps>;
}

// Asignar compound component con casting
const Card = CardComponent as CardCompoundComponent;
Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
