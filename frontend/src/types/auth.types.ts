/**
 * Types for Authentication API Integration
 * Matches backend Pydantic schemas and FastAPI endpoints
 */

import type { EntityId, Timestamp, BaseEntity, StandardResponse } from './core.types';

// User types matching backend UserType enum (English lowercase)
export enum UserType {
  BUYER = 'buyer',
  VENDOR = 'vendor',
  ADMIN = 'admin',
  SUPERUSER = 'superuser'
}

// Base user interface matching backend User model
export interface User extends BaseEntity {
  id: EntityId;
  email: string;
  user_type: UserType;
  nombre?: string;
  full_name?: string;
  apellido?: string;
  telefono?: string;
  cedula?: string;
  email_verified?: boolean;
  phone_verified?: boolean;
  is_active?: boolean;
  // created_at, updated_at, deleted_at inherited from BaseEntity
}

// Login request matching backend LoginRequest schema
export interface LoginRequest {
  email: string;
  password: string;
}

// Register request matching backend registration schemas
export interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  apellido?: string;
  telefono?: string;
  cedula?: string;
  user_type: UserType;
}

// Token response matching backend TokenResponse schema
export interface TokenResponse extends StandardResponse<{
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user?: User;
}> {}

// Auth response for general auth operations
export interface AuthResponse extends StandardResponse<any> {}

// User info response for /me endpoint
export interface UserInfoResponse {
  id: EntityId;
  email: string;
  nombre: string;
  user_type: string;
  email_verified: boolean;
  phone_verified: boolean;
  is_active: boolean;
}

// Password reset request
export interface PasswordResetRequest {
  email: string;
}

// Password reset confirmation
export interface PasswordResetConfirm {
  token: string;
  new_password: string;
  confirm_password: string;
}

// Password reset response
export interface PasswordResetResponse {
  success: boolean;
  message: string;
}

// Refresh token request
export interface RefreshTokenRequest {
  refresh_token: string;
}

// OTP request for 2FA
export interface OTPSendRequest {
  email: string;
  type: 'sms' | 'email';
}

// OTP verification
export interface OTPVerifyRequest {
  email: string;
  otp_code: string;
}

// OTP response
export interface OTPResponse {
  success: boolean;
  message: string;
  verified?: boolean;
}

// Auth store state interface
export interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Auth actions interface
export interface AuthActions {
  // Core auth actions
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;

  // User info actions
  getCurrentUser: () => Promise<User | null>;
  updateUser: (user: User) => void;

  // Session management
  checkAuth: () => boolean;
  clearAuth: () => void;

  // Role helpers
  isAdmin: () => boolean;
  isSuperuser: () => boolean;
  isVendor: () => boolean;
  isBuyer: () => boolean;
  getUserType: () => UserType | null;

  // Loading and error states
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

// Complete auth store type
export interface AuthStore extends AuthState, AuthActions {}

// API error interface for consistent error handling
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: Record<string, any>;
}

// Form validation error type
export interface ValidationError {
  field: string;
  message: string;
}

// Login form props
export interface LoginFormProps {
  onLoginSuccess?: (data: TokenResponse) => void;
  onLoginError?: (error: ApiError) => void;
  className?: string;
  redirectPath?: string;
  showRememberMe?: boolean;
}

// Register form props
export interface RegisterFormProps {
  onRegisterSuccess?: (data: TokenResponse) => void;
  onRegisterError?: (error: ApiError) => void;
  onValidationChange?: (isValid: boolean) => void;
  className?: string;
  showValidationFeedback?: boolean;
  userType?: UserType;
}

// Auth guard props
export interface AuthGuardProps {
  children: React.ReactNode;
  requiredRoles?: UserType[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

// Auth context props
export interface AuthContextProps {
  children: React.ReactNode;
}

// Auth hook return type
export interface UseAuthReturn extends AuthState, AuthActions {}

// Custom hooks return types
export interface UseLoginReturn {
  login: (credentials: LoginRequest) => Promise<boolean>;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

export interface UseRegisterReturn {
  register: (userData: RegisterRequest) => Promise<boolean>;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

export interface UseLogoutReturn {
  logout: () => Promise<void>;
  isLoading: boolean;
}

// Auth service interface
export interface AuthService {
  login: (credentials: LoginRequest) => Promise<TokenResponse>;
  register: (userData: RegisterRequest) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  refreshToken: (token: string) => Promise<TokenResponse>;
  getCurrentUser: () => Promise<UserInfoResponse>;
  forgotPassword: (request: PasswordResetRequest) => Promise<PasswordResetResponse>;
  resetPassword: (request: PasswordResetConfirm) => Promise<PasswordResetResponse>;
  sendOTP: (request: OTPSendRequest) => Promise<OTPResponse>;
  verifyOTP: (request: OTPVerifyRequest) => Promise<OTPResponse>;
}

// Interceptor types for axios
export interface RequestInterceptorConfig {
  onRequest?: (config: any) => any;
  onRequestError?: (error: any) => Promise<any>;
}

export interface ResponseInterceptorConfig {
  onResponse?: (response: any) => any;
  onResponseError?: (error: any) => Promise<any>;
}

export interface AuthInterceptorConfig extends RequestInterceptorConfig, ResponseInterceptorConfig {
  autoRefresh?: boolean;
  refreshEndpoint?: string;
  excludeUrls?: string[];
}