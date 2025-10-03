/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{html,md}',
    './src/components/**/*.tsx',
    './src/pages/**/*.tsx',
    './src/hooks/**/*.ts',
    './src/utils/**/*.ts',
  ],
  safelist: [
    'bg-primary-500',
    'bg-primary-600',
    'hover:bg-primary-600',
    'bg-secondary-500',
    'bg-secondary-600',
    'hover:bg-secondary-600',
    'text-primary-600',
    'border-neutral-200',
    'border-neutral-300',
    'shadow-mestocker',
    'focus:ring-primary-500',
    'rounded-lg',
    'rounded-md',

    // Dark mode classes
    'dark:bg-neutral-800',
    'dark:bg-neutral-900',
    'dark:text-neutral-100',
    'dark:text-neutral-200',
    'dark:border-neutral-700',
    'dark:border-neutral-600',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        secondary: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        accent: {
          50: '#fef7ec',
          100: '#feecdb',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        mestocker: {
          blue: '#3b82f6',
          green: '#10b981',
          orange: '#f97316',
          red: '#ef4444',
          yellow: '#eab308',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      spacing: {
        18: '4.5rem',
        88: '22rem',
        128: '32rem',
        144: '36rem',
      },
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        DEFAULT: '0.375rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.5rem',
        full: '9999px',
      },
      boxShadow: {
        'mestocker-sm': '0 1px 2px 0 rgba(59, 130, 246, 0.05)',
        mestocker:
          '0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06)',
        'mestocker-lg':
          '0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05)',
        'mestocker-xl':
          '0 20px 25px -5px rgba(59, 130, 246, 0.1), 0 10px 10px -5px rgba(59, 130, 246, 0.04)',
      },
      // Breakpoints personalizados para mobile/tablet/desktop
      screens: {
        xs: '475px', // Extra small devices (large phones)
        sm: '640px', // Small devices (landscape phones)
        md: '768px', // Medium devices (tablets)
        lg: '1024px', // Large devices (desktops)
        xl: '1280px', // Extra large devices (large desktops)
        '2xl': '1536px', // 2X Extra large devices (larger desktops)

        // Breakpoints específicos para el proyecto
        mobile: '475px', // Móviles en landscape
        tablet: '768px', // Tablets
        desktop: '1024px', // Desktop estándar
        'desktop-lg': '1280px', // Desktop grande

        // Breakpoints para rangos específicos
        'tablet-only': { min: '768px', max: '1023px' },
        'desktop-only': { min: '1024px' },
        'mobile-only': { max: '767px' },
      },
      // Custom animations for loading states and UI polish
      animation: {
        // Existing animations
        'spin': 'spin 1s linear infinite',
        'spin-slow': 'spin 2s linear infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
        'indeterminate-progress': 'indeterminate-progress 1.5s ease-in-out infinite',

        // Fade animations
        'fade-in': 'fadeIn 0.3s ease-out',
        'fade-out': 'fadeOut 0.3s ease-in',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'fade-in-down': 'fadeInDown 0.5s ease-out',

        // Slide animations
        'slide-in-left': 'slideInLeft 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.4s ease-out',
        'slide-in-up': 'slideInUp 0.4s ease-out',
        'slide-in-down': 'slideInDown 0.4s ease-out',

        // Scale animations
        'scale-in': 'scaleIn 0.3s ease-out',
        'scale-out': 'scaleOut 0.3s ease-in',

        // Bounce animations
        'bounce': 'bounce 1s infinite',
        'bounce-in': 'bounceIn 0.6s ease-out',

        // Shake animation
        'shake': 'shake 0.5s ease-in-out',

        // Heartbeat animation
        'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
      },
      keyframes: {
        // Existing keyframes
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'indeterminate-progress': {
          '0%': { left: '-35%', right: '100%' },
          '60%': { left: '100%', right: '-90%' },
          '100%': { left: '100%', right: '-90%' },
        },

        // Fade keyframes
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },

        // Slide keyframes
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        slideInDown: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(0)' },
        },

        // Scale keyframes
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        scaleOut: {
          '0%': { opacity: '1', transform: 'scale(1)' },
          '100%': { opacity: '0', transform: 'scale(0.9)' },
        },

        // Bounce keyframes
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        bounceIn: {
          '0%': { opacity: '0', transform: 'scale(0.3)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)' },
        },

        // Shake keyframe
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-10px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(10px)' },
        },

        // Heartbeat keyframe
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '10%, 30%': { transform: 'scale(1.1)' },
          '20%, 40%': { transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
};
