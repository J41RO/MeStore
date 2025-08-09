import React from 'react';
import { useTheme } from '@/hooks/useTheme';
import { ThemeToggleProps } from './ThemeToggle.types';

const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className = '',
  showLabel = false,
  size = 'md',
}) => {
  const { theme, effectiveTheme, toggleTheme } = useTheme();

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const buttonSizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-2.5',
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      case 'system':
        return `System (${effectiveTheme})`;
      default:
        return 'Theme';
    }
  };

  const getIcon = () => {
    if (effectiveTheme === 'dark') {
      // Sun icon for switching to light
      return (
        <svg
          className={sizeClasses[size]}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      );
    } else {
      // Moon icon for switching to dark
      return (
        <svg
          className={sizeClasses[size]}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      );
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={toggleTheme}
        className={`
          ${buttonSizeClasses[size]}
          rounded-md 
          bg-neutral-100 hover:bg-neutral-200 
          dark:bg-neutral-800 dark:hover:bg-neutral-700 
          text-neutral-700 dark:text-neutral-200
          transition-all duration-200 
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
          dark:focus:ring-offset-neutral-900
        `}
        aria-label={`Switch to ${theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light'} theme`}
        title={`Current: ${getThemeLabel()}`}
      >
        {getIcon()}
      </button>
      
      {showLabel && (
        <span className="text-sm text-neutral-600 dark:text-neutral-400">
          {getThemeLabel()}
        </span>
      )}
    </div>
  );
};

export default ThemeToggle;
