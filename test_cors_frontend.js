#!/usr/bin/env node

/**
 * Script de test CORS para verificar conectividad entre frontend y backend
 * Uso: node test_cors_frontend.js [url_backend]
 */

import https from 'https';
import http from 'http';
import { URL } from 'url';

const DEFAULT_BACKEND_URL = 'http://localhost:8000';
const FRONTEND_ORIGIN = 'http://localhost:5173';

async function testCorsConnectivity(backendUrl = DEFAULT_BACKEND_URL) {
  console.log('🔍 Testing CORS connectivity...');
  console.log(`Backend URL: ${backendUrl}`);
  console.log(`Frontend Origin: ${FRONTEND_ORIGIN}`);
  console.log('─'.repeat(50));

  const results = {
    healthCheck: false,
    corsHeaders: false,
    preflightSupport: false,
    authEndpoint: false,
    errors: [],
    suggestions: []
  };

  // Test 1: Health Check
  console.log('⚡ Testing health endpoint...');
  try {
    const healthResponse = await makeRequest(backendUrl + '/health', 'GET');
    results.healthCheck = healthResponse.statusCode === 200;

    if (results.healthCheck) {
      console.log('✅ Health check successful');

      // Verificar headers CORS en la respuesta
      const corsHeaders = extractCorsHeaders(healthResponse.headers);
      if (corsHeaders.origin || corsHeaders.methods) {
        results.corsHeaders = true;
        console.log('✅ CORS headers found:', corsHeaders);
      } else {
        console.log('⚠️ No CORS headers found in response');
        results.suggestions.push('Add CORS middleware to backend');
      }
    } else {
      console.log(`❌ Health check failed: ${healthResponse.statusCode}`);
      results.errors.push(`Health endpoint returned ${healthResponse.statusCode}`);
    }
  } catch (error) {
    console.log(`❌ Health check error: ${error.message}`);
    results.errors.push(`Health check failed: ${error.message}`);

    if (error.code === 'ECONNREFUSED') {
      results.suggestions.push('Backend server is not running on the specified port');
    } else if (error.code === 'ENOTFOUND') {
      results.suggestions.push('Backend hostname/IP is not reachable');
    }
  }

  // Test 2: Preflight Request (OPTIONS)
  console.log('🔐 Testing CORS preflight...');
  try {
    const preflightResponse = await makeRequest(backendUrl + '/api/auth/login', 'OPTIONS', {
      'Origin': FRONTEND_ORIGIN,
      'Access-Control-Request-Method': 'POST',
      'Access-Control-Request-Headers': 'Content-Type,Authorization'
    });

    if (preflightResponse.statusCode === 200 || preflightResponse.statusCode === 204) {
      results.preflightSupport = true;
      console.log('✅ Preflight request successful');

      const corsHeaders = extractCorsHeaders(preflightResponse.headers);
      console.log('CORS preflight headers:', corsHeaders);

      // Verificar si nuestro origen está permitido
      if (corsHeaders.origin === '*' || corsHeaders.origin === FRONTEND_ORIGIN) {
        console.log('✅ Origin is allowed');
      } else {
        console.log(`⚠️ Origin may not be allowed. Returned: ${corsHeaders.origin}`);
        results.suggestions.push(`Add ${FRONTEND_ORIGIN} to CORS_ORIGINS in backend config`);
      }
    } else {
      console.log(`⚠️ Preflight returned: ${preflightResponse.statusCode}`);
      results.suggestions.push('Check CORS preflight handling in backend');
    }
  } catch (error) {
    console.log(`❌ Preflight error: ${error.message}`);
    results.errors.push(`Preflight failed: ${error.message}`);
  }

  // Test 3: Auth Endpoint Availability
  console.log('🔑 Testing auth endpoint...');
  try {
    const authResponse = await makeRequest(backendUrl + '/api/auth/login', 'POST', {
      'Origin': FRONTEND_ORIGIN,
      'Content-Type': 'application/json'
    }, '{}');

    // 422 (validation error) or 400 (bad request) significa que el endpoint está disponible
    if (authResponse.statusCode === 422 || authResponse.statusCode === 400) {
      results.authEndpoint = true;
      console.log('✅ Auth endpoint available (validation error expected)');
    } else if (authResponse.statusCode === 404) {
      console.log('❌ Auth endpoint not found');
      results.errors.push('Auth endpoint not available');
    } else {
      console.log(`⚠️ Auth endpoint returned: ${authResponse.statusCode}`);
    }
  } catch (error) {
    console.log(`❌ Auth endpoint error: ${error.message}`);
    results.errors.push(`Auth endpoint failed: ${error.message}`);
  }

  // Summary
  console.log('\n📊 Test Summary');
  console.log('─'.repeat(50));
  console.log(`Health Check: ${results.healthCheck ? '✅' : '❌'}`);
  console.log(`CORS Headers: ${results.corsHeaders ? '✅' : '❌'}`);
  console.log(`Preflight Support: ${results.preflightSupport ? '✅' : '❌'}`);
  console.log(`Auth Endpoint: ${results.authEndpoint ? '✅' : '❌'}`);

  const successCount = Object.values(results).filter(v => v === true).length;
  const totalTests = 4;

  console.log(`\nOverall: ${successCount}/${totalTests} tests passed`);

  if (results.errors.length > 0) {
    console.log('\n❌ Errors:');
    results.errors.forEach((error, index) => {
      console.log(`  ${index + 1}. ${error}`);
    });
  }

  if (results.suggestions.length > 0) {
    console.log('\n💡 Suggestions:');
    results.suggestions.forEach((suggestion, index) => {
      console.log(`  ${index + 1}. ${suggestion}`);
    });
  }

  const allPassed = successCount === totalTests;
  console.log(`\n${allPassed ? '🎉 All tests passed!' : '⚠️ Some tests failed'}`);

  return allPassed;
}

function makeRequest(url, method = 'GET', headers = {}, body = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const protocol = urlObj.protocol === 'https:' ? https : http;

    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'User-Agent': 'CORS-Test-Script/1.0',
        ...headers
      }
    };

    const req = protocol.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (body) {
      req.write(body);
    }

    req.end();
  });
}

function extractCorsHeaders(headers) {
  return {
    origin: headers['access-control-allow-origin'],
    methods: headers['access-control-allow-methods'],
    headers: headers['access-control-allow-headers'],
    credentials: headers['access-control-allow-credentials'],
    maxAge: headers['access-control-max-age']
  };
}

// Ejecutar si se llama directamente
const backendUrl = process.argv[2] || DEFAULT_BACKEND_URL;

testCorsConnectivity(backendUrl)
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Test failed with error:', error);
    process.exit(1);
  });

export { testCorsConnectivity };