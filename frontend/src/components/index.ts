// ~/frontend/src/components/index.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - Components Index
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

/**
 * Components Index - Exportación centralizada de componentes
 */

// UI Components Base
export { Button, Input, Card, Modal } from './ui';
export type { ButtonProps, InputProps, CardProps, ModalProps } from './ui';

// Demo Components
export { default as ThemeExample } from './ThemeExample';
export { default as UtilityClassesDemo } from './UtilityClassesDemo';

// Feature Components (Auth)
export { default as OTPVerification } from './auth/OTPVerification';
export { default as ForgotPassword } from './auth/ForgotPassword';
export { default as ResetPassword } from './auth/ResetPassword';
export { default as BaseComponentsDemo } from './BaseComponentsDemo';
export { default as DarkModeDemo } from './DarkModeDemo';
