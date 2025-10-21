'use client';

import React, { useState } from 'react';
import {
  Send,
  CheckCircle,
  XCircle,
  Loader2,
  User,
  Mail,
  Phone,
  Lock,
  FileJson,
  Chrome,
} from 'lucide-react';
import { backendClient } from '@/lib/backend-client';

interface TestResult {
  success: boolean;
  request: any;
  response: any;
  error?: string;
  timestamp: Date;
}

interface RegistrationForm {
  email: string;
  business_name: string;
  phone: string;
}

interface LoginForm {
  email: string;
  password: string;
}

export default function TestingPanel() {
  // Registration state
  const [regForm, setRegForm] = useState<RegistrationForm>({
    email: '',
    business_name: '',
    phone: '',
  });
  const [regLoading, setRegLoading] = useState(false);
  const [regResult, setRegResult] = useState<TestResult | null>(null);

  // Login state
  const [loginForm, setLoginForm] = useState<LoginForm>({
    email: '',
    password: '',
  });
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginResult, setLoginResult] = useState<TestResult | null>(null);

  // OAuth state
  const [oauthLoading, setOauthLoading] = useState(false);
  const [oauthResult, setOauthResult] = useState<TestResult | null>(null);

  // Test Registration
  const handleTestRegistration = async () => {
    setRegLoading(true);
    setRegResult(null);

    try {
      const response = await backendClient.testRegistration(regForm);

      setRegResult({
        success: true,
        request: regForm,
        response: response,
        timestamp: new Date(),
      });
    } catch (error) {
      setRegResult({
        success: false,
        request: regForm,
        response: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      });
    } finally {
      setRegLoading(false);
    }
  };

  // Test Login
  const handleTestLogin = async () => {
    setLoginLoading(true);
    setLoginResult(null);

    try {
      const response = await backendClient.testLogin(
        loginForm.email,
        loginForm.password
      );

      setLoginResult({
        success: true,
        request: { email: loginForm.email, password: '••••••••' },
        response: response,
        timestamp: new Date(),
      });
    } catch (error) {
      setLoginResult({
        success: false,
        request: { email: loginForm.email, password: '••••••••' },
        response: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      });
    } finally {
      setLoginLoading(false);
    }
  };

  // Test OAuth (simulated)
  const handleTestOAuth = async () => {
    setOauthLoading(true);
    setOauthResult(null);

    try {
      // In production, this would use real Google OAuth token
      // For testing, we'll simulate the flow
      const mockIdToken = 'mock_google_id_token_for_testing';

      const response = await backendClient.testGoogleOAuth(mockIdToken);

      setOauthResult({
        success: true,
        request: { provider: 'Google', id_token: 'mock_token' },
        response: response,
        timestamp: new Date(),
      });
    } catch (error) {
      setOauthResult({
        success: false,
        request: { provider: 'Google', id_token: 'mock_token' },
        response: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      });
    } finally {
      setOauthLoading(false);
    }
  };

  // Render test result
  const renderTestResult = (result: TestResult | null, title: string) => {
    if (!result) return null;

    return (
      <div className="mt-4 space-y-3">
        <div className="flex items-center gap-2">
          {result.success ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <XCircle className="w-5 h-5 text-red-500" />
          )}
          <span
            className={`font-semibold ${
              result.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}
          >
            {result.success ? 'Success' : 'Failed'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {result.timestamp.toLocaleTimeString()}
          </span>
        </div>

        {/* Request */}
        <details className="group">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center gap-2">
            <FileJson className="w-4 h-4" />
            Request Data
          </summary>
          <pre className="mt-2 p-3 bg-gray-900 dark:bg-gray-950 text-gray-100 rounded-lg overflow-x-auto text-xs">
            {JSON.stringify(result.request, null, 2)}
          </pre>
        </details>

        {/* Response */}
        {result.success && result.response && (
          <details className="group">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center gap-2">
              <FileJson className="w-4 h-4" />
              Response Data
            </summary>
            <pre className="mt-2 p-3 bg-gray-900 dark:bg-gray-950 text-gray-100 rounded-lg overflow-x-auto text-xs">
              {JSON.stringify(result.response, null, 2)}
            </pre>
          </details>
        )}

        {/* Error */}
        {!result.success && result.error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-700 dark:text-red-300 font-mono">
              {result.error}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full overflow-y-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="sticky top-0 z-10 p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          API Testing
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Test authentication endpoints with real backend
        </p>
      </div>

      <div className="p-4 space-y-6">
        {/* Registration Test */}
        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <User className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Test Registration
            </h3>
          </div>

          <div className="space-y-3">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={regForm.email}
                  onChange={(e) =>
                    setRegForm({ ...regForm, email: e.target.value })
                  }
                  placeholder="test@example.com"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Business Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Business Name
              </label>
              <input
                type="text"
                value={regForm.business_name}
                onChange={(e) =>
                  setRegForm({ ...regForm, business_name: e.target.value })
                }
                placeholder="My Business"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Phone
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="tel"
                  value={regForm.phone}
                  onChange={(e) =>
                    setRegForm({ ...regForm, phone: e.target.value })
                  }
                  placeholder="+1234567890"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Test Button */}
            <button
              onClick={handleTestRegistration}
              disabled={regLoading || !regForm.email || !regForm.business_name || !regForm.phone}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {regLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Test Registration
                </>
              )}
            </button>
          </div>

          {renderTestResult(regResult, 'Registration')}
        </div>

        {/* Login Test */}
        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <Lock className="w-5 h-5 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Test Login
            </h3>
          </div>

          <div className="space-y-3">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, email: e.target.value })
                  }
                  placeholder="test@example.com"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, password: e.target.value })
                  }
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Test Button */}
            <button
              onClick={handleTestLogin}
              disabled={loginLoading || !loginForm.email || !loginForm.password}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loginLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Test Login
                </>
              )}
            </button>

            {/* Quick Test Credentials */}
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-xs text-blue-700 dark:text-blue-300 mb-2 font-semibold">
                Quick Test Credentials:
              </p>
              <div className="space-y-1 text-xs">
                <p className="text-blue-600 dark:text-blue-400">
                  Email: admin@mestocker.com
                </p>
                <p className="text-blue-600 dark:text-blue-400">
                  Password: Admin123456
                </p>
              </div>
            </div>
          </div>

          {renderTestResult(loginResult, 'Login')}
        </div>

        {/* OAuth Test */}
        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <Chrome className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Test OAuth (Google)
            </h3>
          </div>

          <div className="space-y-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Simulates Google OAuth authentication flow with mock credentials.
            </p>

            {/* Test Button */}
            <button
              onClick={handleTestOAuth}
              disabled={oauthLoading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {oauthLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <Chrome className="w-4 h-4" />
                  Test Google OAuth
                </>
              )}
            </button>

            <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <p className="text-xs text-yellow-700 dark:text-yellow-300">
                Note: This uses a mock ID token for testing purposes. In production,
                this would use real Google OAuth credentials.
              </p>
            </div>
          </div>

          {renderTestResult(oauthResult, 'OAuth')}
        </div>
      </div>
    </div>
  );
}
