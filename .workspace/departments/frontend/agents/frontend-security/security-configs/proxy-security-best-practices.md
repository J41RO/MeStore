# Frontend Proxy Security Best Practices

## Overview
This document outlines security best practices for configuring and managing Vite proxy settings in the MeStocker marketplace frontend, ensuring secure API communication while maintaining development efficiency.

## Environment-Based Configuration Strategy

### Development Environment
```typescript
// vite.config.ts - Development Proxy Configuration
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://192.168.1.137:8000",
        changeOrigin: true,
        secure: false,  // Only for development
        logLevel: 'debug',
        configure: (proxy, options) => {
          // Enhanced proxy monitoring for security
          proxy.on('error', (err, req, res) => {
            console.log('❌ Proxy error:', err.message);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('🚀 Proxy request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('✅ Proxy response:', proxyRes.statusCode);
          });
        }
      }
    }
  }
});
```

### Production Environment
```typescript
// Production - Direct backend communication
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.mestocker.com';
```

## API Client Security Configuration

### Environment-Aware API Clients
```typescript
// Secure API client configuration
const apiClient = axios.create({
  baseURL: import.meta.env.DEV
    ? undefined  // Use Vite proxy in development
    : (import.meta.env.VITE_API_BASE_URL || 'https://api.mestocker.com'),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,  // Important for CORS with credentials
});
```

## Security Headers and CORS

### Required Security Headers
```typescript
headers: {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',  // CSRF protection
  'Cache-Control': 'no-cache',  // Prevent sensitive data caching
}
```

### CORS Configuration
- **Development**: Use proxy to avoid CORS issues
- **Production**: Ensure backend CORS configuration includes frontend domain
- **Credentials**: Always use `withCredentials: true` for authenticated requests

## Authentication Security

### Token Management
```typescript
// Secure token handling in interceptors
apiClient.interceptors.request.use(request => {
  const token = localStorage.getItem('access_token');
  if (token && !isTokenExpired(token)) {
    request.headers.Authorization = `Bearer ${token}`;
  }
  return request;
});
```

### Response Security
```typescript
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Secure logout on authentication failure
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Environment Variables Security

### Development (.env.development)
```bash
# No API base URL - use Vite proxy
# VITE_API_BASE_URL disabled for proxy routing
VITE_APP_ENV=development
VITE_LOG_REMOTE=false
```

### Production (.env.production)
```bash
VITE_API_BASE_URL=https://api.mestocker.com
VITE_APP_ENV=production
VITE_LOG_REMOTE=true
```

## Proxy Security Monitoring

### Request Logging
- Log all proxy requests for debugging
- Monitor for unusual request patterns
- Track authentication failures
- Alert on proxy errors

### Security Validation
```typescript
// Validate proxy responses
proxy.on('proxyRes', (proxyRes, req, res) => {
  // Check for security headers
  if (!proxyRes.headers['x-frame-options']) {
    console.warn('⚠️ Missing X-Frame-Options header');
  }

  // Monitor for authentication errors
  if (proxyRes.statusCode === 401) {
    console.warn('🔒 Authentication failure:', req.url);
  }
});
```

## Common Security Pitfalls

### 1. Environment Variable Leakage
❌ **Wrong**: Setting API URL in development
```bash
VITE_API_BASE_URL=http://192.168.1.137:8000  # Bypasses proxy
```

✅ **Correct**: Using proxy in development
```bash
# VITE_API_BASE_URL disabled for proxy routing
```

### 2. Inconsistent API Clients
❌ **Wrong**: Mixed proxy and direct configurations
```typescript
// Some services use proxy, others don't
const authClient = axios.create(); // Uses proxy
const apiClient = axios.create({ baseURL: 'http://backend' }); // Bypasses proxy
```

✅ **Correct**: Consistent environment-aware configuration
```typescript
const baseURL = import.meta.env.DEV ? undefined : VITE_API_BASE_URL;
```

### 3. Insecure Proxy Configuration
❌ **Wrong**: No security monitoring
```typescript
proxy: {
  "/api": {
    target: "http://backend",
    changeOrigin: true
  }
}
```

✅ **Correct**: Enhanced security monitoring
```typescript
proxy: {
  "/api": {
    target: "http://backend",
    changeOrigin: true,
    secure: false,  // Only for development
    configure: (proxy) => {
      // Add comprehensive logging and monitoring
    }
  }
}
```

## Security Checklist

### Development Security
- [ ] Proxy configuration uses secure target URLs
- [ ] Environment variables don't expose sensitive data
- [ ] Request/response logging enabled for debugging
- [ ] CORS issues resolved through proxy, not permissive headers
- [ ] Authentication tokens properly handled through proxy

### Production Security
- [ ] Direct HTTPS communication to backend
- [ ] Secure environment variables configuration
- [ ] No development-only headers or configurations
- [ ] Proper CORS configuration on backend
- [ ] CSP headers configured to prevent XSS

### Code Security
- [ ] All API clients use environment-aware configuration
- [ ] Token validation and expiration checking
- [ ] Secure logout on authentication failures
- [ ] Input validation on all user inputs
- [ ] No sensitive data in client-side logs

## Incident Response

### Proxy Security Issues
1. **Immediate**: Check proxy logs for security violations
2. **Investigate**: Analyze request patterns and response codes
3. **Escalate**: Contact Backend Security AI for coordination
4. **Document**: Update security decision log with findings

### Authentication Failures
1. **Monitor**: Track 401/403 responses through proxy
2. **Validate**: Ensure proper token handling
3. **Coordinate**: Work with Backend Security AI on token validation
4. **Update**: Implement additional security measures if needed

## Contact Information
- **Frontend Security AI**: This agent
- **Backend Security AI**: `/workspace/departments/backend/agents/backend-security/`
- **Cybersecurity AI**: `/workspace/departments/cybersecurity/`

---

**Last Updated**: 2025-09-19
**Next Review**: 2025-10-19
**Security Level**: HIGH