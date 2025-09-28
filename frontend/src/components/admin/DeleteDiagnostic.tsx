import React, { useState } from 'react';

/**
 * DELETE Diagnostic Component
 *
 * TEMPORARY COMPONENT for debugging DELETE authentication issues.
 * This component provides detailed logging and testing for DELETE requests
 * to help identify the root cause of the CORS/authentication error.
 *
 * TO USE: Add this component to UserManagement.tsx temporarily
 * TO REMOVE: Delete after issue is resolved
 */
const DeleteDiagnostic: React.FC = () => {
  const [testResults, setTestResults] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addResult = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestResults(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const testTokenValidity = async () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      addResult('❌ No token found in localStorage');
      return false;
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const isExpired = payload.exp < currentTime;

      addResult(`🔑 Token info: exp=${new Date(payload.exp * 1000).toLocaleString()}`);
      addResult(`⏰ Current time: ${new Date().toLocaleString()}`);
      addResult(`${isExpired ? '❌' : '✅'} Token ${isExpired ? 'EXPIRED' : 'VALID'}`);

      return !isExpired;
    } catch (e) {
      addResult(`❌ Token parsing error: ${e}`);
      return false;
    }
  };

  const testBasicAuth = async () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      addResult('❌ No token for auth test');
      return;
    }

    try {
      addResult('🧪 Testing GET /users/stats for auth validation...');

      const response = await fetch('http://192.168.1.137:8000/api/v1/superuser-admin/users/stats', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      addResult(`📡 GET stats response: ${response.status} ${response.statusText}`);

      if (response.ok) {
        addResult('✅ Basic authentication works');
        return true;
      } else {
        addResult('❌ Basic authentication failed');
        return false;
      }
    } catch (error) {
      addResult(`❌ Basic auth test error: ${error}`);
      return false;
    }
  };

  const testPreflightRequest = async () => {
    try {
      addResult('🚁 Testing CORS preflight for DELETE...');

      const response = await fetch('http://192.168.1.137:8000/api/v1/superuser-admin/users/test-user-id', {
        method: 'OPTIONS',
        headers: {
          'Access-Control-Request-Method': 'DELETE',
          'Access-Control-Request-Headers': 'Authorization,Content-Type',
          'Origin': 'http://192.168.1.137:5173'
        }
      });

      addResult(`🚁 OPTIONS response: ${response.status} ${response.statusText}`);

      const corsHeaders = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
      };

      addResult(`🔧 CORS headers: ${JSON.stringify(corsHeaders, null, 2)}`);

      return response.ok;
    } catch (error) {
      addResult(`❌ Preflight test error: ${error}`);
      return false;
    }
  };

  const testActualDelete = async () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      addResult('❌ No token for DELETE test');
      return;
    }

    try {
      addResult('🗑️ Testing actual DELETE request...');

      // Use a fake user ID for testing
      const testUserId = '00000000-0000-0000-0000-000000000000';
      const deleteUrl = `http://192.168.1.137:8000/api/v1/superuser-admin/users/${testUserId}?reason=Diagnostic%20Test`;

      addResult(`🎯 DELETE URL: ${deleteUrl}`);
      addResult(`🔑 Token (first 20 chars): ${token.substring(0, 20)}...`);

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      };

      addResult(`📤 Headers: ${JSON.stringify(headers, null, 2)}`);

      const response = await fetch(deleteUrl, {
        method: 'DELETE',
        headers: headers,
        credentials: 'omit'
      });

      addResult(`📡 DELETE response: ${response.status} ${response.statusText}`);
      addResult(`📋 Response headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()), null, 2)}`);

      if (response.ok) {
        const data = await response.json();
        addResult(`✅ DELETE success: ${JSON.stringify(data)}`);
      } else {
        try {
          const errorData = await response.json();
          addResult(`❌ DELETE error data: ${JSON.stringify(errorData)}`);
        } catch (parseError) {
          addResult(`❌ DELETE failed, could not parse error: ${parseError}`);
        }
      }
    } catch (error) {
      addResult(`💥 DELETE request failed: ${error}`);

      // Analyze the error
      if (error instanceof TypeError && error.message.includes('fetch')) {
        addResult('🚨 This looks like a CORS error masking an auth issue!');
      }
    }
  };

  const runFullDiagnostic = async () => {
    setIsLoading(true);
    clearResults();

    addResult('🔬 Starting comprehensive DELETE diagnostic...');
    addResult('====================================================');

    // Step 1: Token validation
    addResult('STEP 1: Token Validation');
    const tokenValid = await testTokenValidity();

    if (!tokenValid) {
      addResult('🛑 Stopping: Invalid token');
      setIsLoading(false);
      return;
    }

    // Step 2: Basic auth test
    addResult('\nSTEP 2: Basic Authentication Test');
    const authWorks = await testBasicAuth();

    if (!authWorks) {
      addResult('🛑 Stopping: Basic auth failed');
      setIsLoading(false);
      return;
    }

    // Step 3: CORS preflight test
    addResult('\nSTEP 3: CORS Preflight Test');
    await testPreflightRequest();

    // Step 4: Actual DELETE test
    addResult('\nSTEP 4: Actual DELETE Test');
    await testActualDelete();

    addResult('\n====================================================');
    addResult('✅ Diagnostic complete!');
    setIsLoading(false);
  };

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-yellow-800">🔬 DELETE Diagnostic Tool</h3>
        <div className="space-x-2">
          <button
            onClick={runFullDiagnostic}
            disabled={isLoading}
            className="bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700 disabled:opacity-50"
          >
            {isLoading ? 'Running...' : 'Run Full Diagnostic'}
          </button>
          <button
            onClick={clearResults}
            className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
          >
            Clear
          </button>
        </div>
      </div>

      {testResults.length > 0 && (
        <div className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono max-h-96 overflow-y-auto">
          {testResults.map((result, index) => (
            <div key={index} className="mb-1">{result}</div>
          ))}
        </div>
      )}

      {testResults.length === 0 && !isLoading && (
        <p className="text-yellow-700 text-sm">
          Click "Run Full Diagnostic" to test DELETE authentication step by step
        </p>
      )}
    </div>
  );
};

export default DeleteDiagnostic;