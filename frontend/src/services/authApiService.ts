/**
 * Authentication API Service for MeStore Frontend
 * Handles all auth-related API operations with consistent EntityId types
 */

import { BaseApiService } from './baseApiService';
import type {
  EntityId,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserInfoResponse,
  PasswordResetRequest,
  PasswordResetConfirm,
  PasswordResetResponse,
  RefreshTokenRequest,
  OTPSendRequest,
  OTPVerifyRequest,
  OTPResponse,
  User,
  StandardResponse,
} from '../types';

// ========================================
// AUTH API ENDPOINTS
// ========================================

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  ADMIN_LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh-token',
  ME: '/auth/me',
  UPDATE_PROFILE: '/auth/profile',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  SEND_OTP: '/auth/send-otp',
  VERIFY_OTP: '/auth/verify-otp',
  VERIFY_EMAIL: '/auth/verify-email',
  RESEND_VERIFICATION: '/auth/resend-verification',
  CHANGE_PASSWORD: '/auth/change-password',
} as const;

// ========================================
// TOKEN MANAGEMENT
// ========================================

/**
 * TokenManager - Handles token storage and retrieval
 */
class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private static readonly USER_KEY = 'user_info';

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static getUser(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  static setTokens(accessToken: string, refreshToken?: string, user?: User): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    }
    if (user) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    }
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  static isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

// ========================================
// AUTH API SERVICE
// ========================================

/**
 * AuthApiService - Complete authentication API integration
 */
export class AuthApiService extends BaseApiService {
  private readonly endpoints = AUTH_ENDPOINTS;
  public readonly tokenManager = TokenManager;

  constructor() {
    super();
    // Initialize with stored token if available
    const token = TokenManager.getAccessToken();
    if (token) {
      this.setAuthToken(token);
    }
  }

  // ========================================
  // AUTHENTICATION OPERATIONS
  // ========================================

  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>(
      this.endpoints.LOGIN,
      credentials
    );

    const tokenData = response.data;

    // Handle both StandardResponse format and direct TokenResponse
    const data = 'data' in tokenData ? tokenData.data : tokenData;

    if (data) {
      TokenManager.setTokens(data.access_token, data.refresh_token, data.user);
      this.setAuthToken(data.access_token);
    }

    return response.data;
  }

  /**
   * Admin login with enhanced validation
   */
  async adminLogin(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>(
      this.endpoints.ADMIN_LOGIN,
      credentials
    );

    const tokenData = response.data;
    const data = 'data' in tokenData ? tokenData.data : tokenData;

    if (data) {
      TokenManager.setTokens(data.access_token, data.refresh_token, data.user);
      this.setAuthToken(data.access_token);
    }

    return response.data;
  }

  /**
   * Register new user
   */
  async register(userData: RegisterRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>(
      this.endpoints.REGISTER,
      userData
    );

    const tokenData = response.data;
    const data = 'data' in tokenData ? tokenData.data : tokenData;

    if (data) {
      TokenManager.setTokens(data.access_token, data.refresh_token, data.user);
      this.setAuthToken(data.access_token);
    }

    return response.data;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await this.client.post(this.endpoints.LOGOUT);
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      TokenManager.clearTokens();
      this.clearAuthToken();
    }
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const request: RefreshTokenRequest = { refresh_token: refreshToken };
    const response = await this.client.post<TokenResponse>(
      this.endpoints.REFRESH,
      request
    );

    const tokenData = response.data;
    const data = 'data' in tokenData ? tokenData.data : tokenData;

    if (data) {
      TokenManager.setTokens(data.access_token, data.refresh_token, data.user);
      this.setAuthToken(data.access_token);
    }

    return response.data;
  }

  // ========================================
  // USER INFORMATION
  // ========================================

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<StandardResponse<UserInfoResponse>>(
      this.endpoints.ME
    );

    const userInfo = this.extractResponseData(response);

    // Convert UserInfoResponse to User format
    const user: User = {
      id: userInfo.id,
      email: userInfo.email,
      user_type: userInfo.user_type as any,
      nombre: userInfo.nombre,
      email_verified: userInfo.email_verified,
      phone_verified: userInfo.phone_verified,
      is_active: userInfo.is_active,
      created_at: new Date().toISOString(), // Fallback if not provided
      updated_at: new Date().toISOString(), // Fallback if not provided
    };

    // Update stored user info
    TokenManager.setTokens(
      TokenManager.getAccessToken()!,
      TokenManager.getRefreshToken() || undefined,
      user
    );

    return user;
  }

  /**
   * Update user profile
   */
  async updateProfile(updateData: Partial<User>): Promise<User> {
    const response = await this.client.put<StandardResponse<User>>(
      this.endpoints.UPDATE_PROFILE,
      updateData
    );

    const user = this.extractResponseData(response);

    // Update stored user info
    TokenManager.setTokens(
      TokenManager.getAccessToken()!,
      TokenManager.getRefreshToken() || undefined,
      user
    );

    return user;
  }

  // ========================================
  // PASSWORD MANAGEMENT
  // ========================================

  /**
   * Request password reset
   */
  async forgotPassword(request: PasswordResetRequest): Promise<PasswordResetResponse> {
    const response = await this.client.post<PasswordResetResponse>(
      this.endpoints.FORGOT_PASSWORD,
      request
    );
    return response.data;
  }

  /**
   * Reset password with token
   */
  async resetPassword(request: PasswordResetConfirm): Promise<PasswordResetResponse> {
    const response = await this.client.post<PasswordResetResponse>(
      this.endpoints.RESET_PASSWORD,
      request
    );
    return response.data;
  }

  /**
   * Change password for authenticated user
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    const data = {
      current_password: currentPassword,
      new_password: newPassword,
    };

    await this.client.post(this.endpoints.CHANGE_PASSWORD, data);
    return true;
  }

  // ========================================
  // TWO-FACTOR AUTHENTICATION
  // ========================================

  /**
   * Send OTP for verification
   */
  async sendOTP(request: OTPSendRequest): Promise<OTPResponse> {
    const response = await this.client.post<OTPResponse>(
      this.endpoints.SEND_OTP,
      request
    );
    return response.data;
  }

  /**
   * Verify OTP code
   */
  async verifyOTP(request: OTPVerifyRequest): Promise<OTPResponse> {
    const response = await this.client.post<OTPResponse>(
      this.endpoints.VERIFY_OTP,
      request
    );
    return response.data;
  }

  // ========================================
  // EMAIL VERIFICATION
  // ========================================

  /**
   * Verify email address with token
   */
  async verifyEmail(token: string): Promise<boolean> {
    await this.client.post(`${this.endpoints.VERIFY_EMAIL}?token=${token}`);
    return true;
  }

  /**
   * Resend email verification
   */
  async resendEmailVerification(): Promise<boolean> {
    await this.client.post(this.endpoints.RESEND_VERIFICATION);
    return true;
  }

  // ========================================
  // TOKEN VALIDATION
  // ========================================

  /**
   * Check if current token is valid
   */
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Auto-refresh token if needed
   */
  async ensureValidToken(): Promise<boolean> {
    if (!TokenManager.getAccessToken()) {
      return false;
    }

    const isValid = await this.validateToken();
    if (!isValid && TokenManager.getRefreshToken()) {
      try {
        await this.refreshToken();
        return true;
      } catch (error) {
        TokenManager.clearTokens();
        this.clearAuthToken();
        return false;
      }
    }

    return isValid;
  }

  // ========================================
  // AUTHENTICATION STATE
  // ========================================

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return TokenManager.isAuthenticated();
  }

  /**
   * Get stored user information
   */
  getStoredUser(): User | null {
    return TokenManager.getUser();
  }

  /**
   * Get stored access token
   */
  getStoredToken(): string | null {
    return TokenManager.getAccessToken();
  }

  /**
   * Clear all authentication data
   */
  clearAuthData(): void {
    TokenManager.clearTokens();
    this.clearAuthToken();
  }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

/**
 * Default auth API service instance
 */
export const authApiService = new AuthApiService();

// ========================================
// EXPORTS
// ========================================

export { AuthApiService, TokenManager };
export default authApiService;