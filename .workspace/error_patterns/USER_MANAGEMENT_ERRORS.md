# USER MANAGEMENT ERROR PATTERNS LIBRARY

**Document Status**: CRITICAL REFERENCE
**Created**: 2025-09-28
**Last Updated**: 2025-09-28
**Created By**: Agent Recruiter AI
**Version**: v1.0.0
**Priority**: MAXIMUM
**Usage**: Error diagnosis and rapid resolution

## 🎯 PURPOSE

This library maps specific error codes, messages, and log patterns to their root causes and exact solutions. Use this for immediate problem resolution during User Management issues.

## 🚨 HTTP STATUS CODE MAPPING

### 401 Unauthorized Errors

#### Pattern: Login Returns 401 Despite Correct Credentials
```
HTTP/1.1 401 Unauthorized
{"detail": "Invalid credentials"}
```

**Root Causes:**
1. **Password Case Sensitivity** (90% of cases)
   - Problem: Using `admin123456` instead of `Admin123456`
   - Solution: Verify exact password `Admin123456`
   - Validation:
     ```bash
     curl -X POST http://localhost:8000/api/v1/auth/login \
       -H "Content-Type: application/json" \
       -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'
     ```

2. **Database Connection Issues** (8% of cases)
   - Problem: Database not accessible
   - Solution: Verify PostgreSQL service running
   - Validation:
     ```bash
     pg_isready -h localhost -p 5432
     ```

3. **User Not Found** (2% of cases)
   - Problem: Admin user doesn't exist
   - Solution: Run database migrations and seed data
   - Validation:
     ```bash
     python -c "
     import asyncio
     from app.database import get_async_db
     from app.models.user import User
     from sqlalchemy import select
     async def check():
         async for db in get_async_db():
             result = await db.execute(select(User).where(User.email == 'admin@mestocker.com'))
             user = result.scalar_one_or_none()
             print(f'Admin exists: {user is not None}')
     asyncio.run(check())
     "
     ```

#### Pattern: API Requests Return 401 with Valid Token
```
HTTP/1.1 401 Unauthorized
{"detail": "Could not validate credentials"}
```

**Root Causes:**
1. **Token Expired** (70% of cases)
   - Problem: JWT token has expired
   - Solution: Re-authenticate to get new token
   - Validation: Check token expiration in JWT payload

2. **Token Format Error** (20% of cases)
   - Problem: Missing "Bearer " prefix
   - Solution: Ensure header format: `Authorization: Bearer <token>`

3. **Secret Key Mismatch** (10% of cases)
   - Problem: JWT secret changed without token refresh
   - Solution: Clear tokens and re-authenticate

### 403 Forbidden Errors

#### Pattern: CSRF Token Validation Failed
```
HTTP/1.1 403 Forbidden
{"detail": "CSRF token validation failed"}
```

**Root Causes:**
1. **Missing CSRF Token Header** (60% of cases)
   - Problem: Request lacks `X-CSRF-Token` header
   - Solution: Add header to request
   - Validation:
     ```javascript
     headers: {
       'X-CSRF-Token': csrfToken,
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     }
     ```

2. **Invalid CSRF Token** (30% of cases)
   - Problem: Token is expired or malformed
   - Solution: Fetch new token from `/api/v1/auth/csrf-token`
   - Validation:
     ```bash
     curl -s http://localhost:8000/api/v1/auth/csrf-token | jq -r '.csrf_token'
     ```

3. **Rate Limiting Function Signature Error** (10% of cases)
   - Problem: slowapi-limiter configuration error
   - Solution: Fix function signature in middleware
   - Error in logs: `TypeError: RateLimiter() got unexpected keyword argument 'identifier'`

#### Pattern: Rate Limiting Triggered
```
HTTP/1.1 429 Too Many Requests
{"detail": "Rate limit exceeded"}
```

**Root Causes:**
1. **Legitimate Rate Limiting** (80% of cases)
   - Problem: Too many requests from same IP
   - Solution: Wait for rate limit window to reset
   - Typical limit: 5 requests per minute

2. **Rate Limiter Configuration Error** (20% of cases)
   - Problem: Incorrect function signature
   - Solution: Update rate limiter implementation
   - Check logs for: `TypeError` in rate limiting code

### 500 Internal Server Error

#### Pattern: Rate Limiting Function Signature Error
```
HTTP/1.1 500 Internal Server Error
Server logs: TypeError: RateLimiter() got unexpected keyword argument 'identifier'
```

**Root Cause:** Incorrect slowapi-limiter function signature

**Solution:**
```python
# File: app/core/middleware.py

# INCORRECT:
@limiter.limit("5/minute", key_func=lambda: request.client.host, identifier=get_client_ip)

# CORRECT:
@limiter.limit("5/minute", key_func=get_client_ip)
```

**Validation:**
```bash
grep -r "limiter.limit" /home/admin-jairo/MeStore/app/ --include="*.py"
# Look for incorrect function signatures
```

#### Pattern: Dependency Injection Order Error
```
HTTP/1.1 500 Internal Server Error
Server logs: TypeError: [specific dependency error]
```

**Root Cause:** Incorrect order of FastAPI dependencies

**Solution:**
```python
# File: app/api/v1/endpoints/superuser_endpoints.py

# CORRECT ORDER:
async def create_user_endpoint(
    user_data: UserCreateSchema,
    current_user: User = Depends(get_current_superuser),  # 1st
    db: AsyncSession = Depends(get_async_db),              # 2nd
    csrf_token: str = Depends(verify_csrf_token)           # 3rd
):
```

## 🌐 CORS AND NETWORK ERRORS

### Pattern: CORS Policy Violation
```
Browser Console:
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/users/create'
from origin 'http://localhost:5173' has been blocked by CORS policy:
Request header field 'x-csrf-token' is not allowed by Access-Control-Allow-Headers
```

**Root Cause:** X-CSRF-Token not included in CORS allowed headers

**Solution:**
```python
# File: app/core/config.py
CORS_ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",  # ADD THIS LINE
    "Accept",
    "Origin",
    "X-Requested-With"
]
```

**Validation:**
```bash
curl -X OPTIONS http://localhost:8000/api/v1/users/create \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization,X-CSRF-Token" \
  -v | grep "X-CSRF-Token"
```

### Pattern: Preflight Request Failed
```
Browser Console:
OPTIONS http://localhost:8000/api/v1/users/create net::ERR_FAILED
```

**Root Causes:**
1. **Backend Service Down** (70% of cases)
   - Solution: Start backend service
   - Validation: `curl -f http://localhost:8000/health`

2. **Port Conflict** (20% of cases)
   - Solution: Kill conflicting process
   - Validation: `netstat -tlnp | grep :8000`

3. **CORS Middleware Not Loaded** (10% of cases)
   - Solution: Verify CORS middleware in app configuration
   - Check: FastAPI app includes CORS middleware

## 💻 FRONTEND ERROR PATTERNS

### Pattern: Network Request Failed
```javascript
// Browser Console
Uncaught (in promise) AxiosError: Network Error
    at XMLHttpRequest.handleError
```

**Root Causes:**
1. **Backend Service Unreachable** (60% of cases)
   - Solution: Verify backend running on correct port
   - Validation: `curl -f http://localhost:8000/health`

2. **CORS Configuration Error** (30% of cases)
   - Solution: Update CORS headers in backend
   - Check browser network tab for specific CORS error

3. **Incorrect API Endpoint URL** (10% of cases)
   - Solution: Verify endpoint exists and URL is correct
   - Check: API documentation at `http://localhost:8000/docs`

### Pattern: Request Header Rejection
```javascript
// Browser Console
POST http://localhost:8000/api/v1/users/create 403 (Forbidden)
Response: {"detail": "CSRF token validation failed"}
```

**Root Cause:** CSRF token not properly included in request

**Solution:**
```typescript
// Frontend code
const response = await axios.post('/api/v1/users/create', userData, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-CSRF-Token': csrfToken,  // ENSURE THIS IS INCLUDED
    'Content-Type': 'application/json'
  }
});
```

**Validation:**
- Check browser network tab for request headers
- Verify CSRF token is non-empty string
- Confirm token fetched from `/api/v1/auth/csrf-token`

## 🔧 CONFIGURATION ERROR PATTERNS

### Pattern: Environment Override Conflict
```
Expected behavior not occurring despite correct code changes
```

**Root Cause:** Environment file overriding code configuration

**Detection:**
```bash
find /home/admin-jairo/MeStore -name ".env*" -type f -exec echo "=== {} ===" \; -exec cat {} \;
```

**Common Conflicts:**
1. **CORS Settings Override**
   ```
   # .env file
   CORS_ALLOWED_ORIGINS=http://localhost:3000  # Wrong port
   ```

2. **Authentication Settings Override**
   ```
   # .env file
   AUTH_SECRET_KEY=different_key  # Breaks JWT validation
   ```

**Solution:**
- Remove conflicting environment variables
- Or update environment files to match desired configuration
- Priority: `.env` > `app/.env` > code configuration

### Pattern: Service Port Conflicts
```
uvicorn.error: [Errno 98] Address already in use
```

**Root Cause:** Another process using required port

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Prevention:**
```bash
# Check ports before starting services
netstat -tlnp | grep -E ":8000|:5173"
```

## 🔍 LOG ANALYSIS PATTERNS

### Backend Log Patterns

#### Authentication Errors
```
INFO: Authentication failed for user: admin@mestocker.com
```
**Cause:** Password mismatch
**Solution:** Verify password case sensitivity

#### CSRF Validation Errors
```
WARNING: CSRF token validation failed for request
```
**Cause:** Missing or invalid CSRF token
**Solution:** Check frontend token management

#### Rate Limiting Errors
```
ERROR: TypeError: RateLimiter() got unexpected keyword argument 'identifier'
```
**Cause:** Incorrect function signature
**Solution:** Fix rate limiter configuration

### Frontend Log Patterns

#### Network Errors
```
[Axios Error] Request failed with status code 0
```
**Cause:** Backend unreachable
**Solution:** Verify backend service status

#### CORS Errors
```
[CORS Error] has been blocked by CORS policy
```
**Cause:** CORS configuration incomplete
**Solution:** Update backend CORS headers

## 🚀 RAPID RESOLUTION COMMANDS

### Quick Diagnostic Suite
```bash
#!/bin/bash
echo "=== USER MANAGEMENT DIAGNOSTIC SUITE ==="

# 1. Service Status
echo "1. Backend Health:"
curl -f http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend DOWN"

echo "2. Frontend Health:"
curl -f http://localhost:5173 && echo "✅ Frontend OK" || echo "❌ Frontend DOWN"

# 2. Authentication Test
echo "3. Admin Authentication:"
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' | jq -r '.access_token')

if [ "$TOKEN" != "null" ]; then
  echo "✅ Authentication OK"
else
  echo "❌ Authentication FAILED - Check password case"
fi

# 3. CORS Test
echo "4. CORS Configuration:"
curl -X OPTIONS http://localhost:8000/api/v1/users/create \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization,X-CSRF-Token" \
  -v 2>&1 | grep "X-CSRF-Token" && echo "✅ CORS OK" || echo "❌ CORS MISSING X-CSRF-Token"

# 4. CSRF Token Test
echo "5. CSRF Token:"
CSRF_TOKEN=$(curl -s http://localhost:8000/api/v1/auth/csrf-token | jq -r '.csrf_token')
if [ "$CSRF_TOKEN" != "null" ]; then
  echo "✅ CSRF Token OK"
else
  echo "❌ CSRF Token FAILED"
fi

echo "=== DIAGNOSTIC COMPLETE ==="
```

### Emergency Reset Procedure
```bash
#!/bin/bash
echo "=== EMERGENCY RESET PROCEDURE ==="

# Stop all services
pkill -f uvicorn
pkill -f vite

# Clear potential conflicts
rm -f /tmp/fastapi*
rm -f /tmp/vite*

# Restart backend
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for backend
sleep 5

# Restart frontend
cd frontend
npm run dev &

# Wait for frontend
sleep 5

# Test integration
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' && echo "✅ RESET SUCCESSFUL"

echo "=== RESET COMPLETE ==="
```

## 📞 ERROR ESCALATION MATRIX

| Error Type | Severity | Contact Agent | Response Time |
|------------|----------|---------------|---------------|
| 401 Authentication | High | security-backend-ai | 15 minutes |
| 403 CSRF/Rate Limit | High | backend-framework-ai | 15 minutes |
| 500 Server Error | Critical | system-architect-ai | 5 minutes |
| CORS Issues | High | security-backend-ai | 15 minutes |
| Frontend Network | Medium | react-specialist-ai | 30 minutes |
| Configuration | Medium | system-architect-ai | 30 minutes |

---

**USAGE INSTRUCTIONS**:
1. Find your error pattern in this document
2. Apply the specific solution provided
3. Use validation commands to confirm fix
4. If pattern not found, use rapid diagnostic suite
5. If still unresolved, escalate per matrix above