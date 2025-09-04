import React from 'react';

interface HamburgerIconProps {
  isOpen: boolean;
  onClick?: () => void;
  className?: string;
}

const HamburgerIcon: React.FC<HamburgerIconProps> = ({
  isOpen,
  onClick,
  className = '',
}) => {
  return (
    <button
      onClick={onClick}
      className={`w-6 h-6 sm:hidden flex flex-col justify-center items-center cursor-pointer touch-target active:scale-90 p-2 ${className}`}
      type='button'
      aria-label='Toggle mobile menu'
    >
      {/* Línea superior */}
      <span
        className={`block w-5 h-0.5 bg-gray-700 dark:bg-gray-300 transition-all duration-300 transform ${
          isOpen ? 'rotate-45 translate-y-1.5' : ''
        }`}
      />
      {/* Línea media */}
      <span
        className={`block w-5 h-0.5 bg-gray-700 dark:bg-gray-300 transition-all duration-300 my-1 ${
          isOpen ? 'opacity-0' : ''
        }`}
      />
      {/* Línea inferior */}
      <span
        className={`block w-5 h-0.5 bg-gray-700 dark:bg-gray-300 transition-all duration-300 transform ${
          isOpen ? '-rotate-45 -translate-y-1.5' : ''
        }`}
      />
    </button>
  );
};

export default HamburgerIcon;
