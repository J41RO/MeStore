import React, { useState, useEffect } from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => {
  const [isPressed, setIsPressed] = useState<boolean>(false);
  const [variant, setVariant] = useState<string>('primary');

  useEffect(() => {
    console.log('Button mounted');
  }, []);

  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
    >
      {label}
    </button>
  );
};

export default Button;