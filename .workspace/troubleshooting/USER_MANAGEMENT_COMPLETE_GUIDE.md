# USER MANAGEMENT COMPLETE TROUBLESHOOTING GUIDE

**Document Status**: CRITICAL REFERENCE
**Created**: 2025-09-28
**Last Updated**: 2025-09-28
**Created By**: Agent Recruiter AI
**Version**: v1.0.0
**Priority**: MAXIMUM
**Scope**: All User Management implementations in MeStore

## 🚨 CRITICAL CONTEXT

This guide documents ALL issues encountered during User Create Modal implementation. These are REAL problems that occurred and were solved. Use this guide to prevent future implementation failures.

## 📋 STEP-BY-STEP DIAGNOSTIC PROCESS

### Phase 1: Environment Validation (CRITICAL FIRST STEP)

#### 1.1 Verify Backend Service Status
```bash
# Check if backend is running
curl -f http://localhost:8000/health || echo "Backend DOWN"

# Verify correct port and host
ps aux | grep uvicorn | grep -v grep
netstat -tlnp | grep :8000
```

#### 1.2 Verify Frontend Service Status
```bash
# Check if frontend is running
curl -f http://localhost:5173 || echo "Frontend DOWN"

# Verify Vite development server
ps aux | grep vite | grep -v grep
netstat -tlnp | grep :5173
```

#### 1.3 Authentication Verification (CRITICAL)
```bash
# Test admin credentials - CASE SENSITIVE
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'

# Expected: HTTP 200 with access_token
# If HTTP 401: PASSWORD CASE MISMATCH (admin123456 vs Admin123456)
```

### Phase 2: CORS Configuration Diagnostic

#### 2.1 Backend CORS Headers Check
```bash
# Test OPTIONS request (preflight)
curl -X OPTIONS http://localhost:8000/api/v1/users/create \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization,X-CSRF-Token" \
  -v

# CRITICAL: Look for X-CSRF-Token in Access-Control-Allow-Headers response
# If missing: CORS configuration incomplete
```

#### 2.2 Environment Override Detection
```bash
# Check for environment file overrides
cat /home/admin-jairo/MeStore/.env | grep -E "(CORS_|ALLOWED_)"
cat /home/admin-jairo/MeStore/app/.env 2>/dev/null | grep -E "(CORS_|ALLOWED_)"

# Environment files can override code configuration
# Solution: Update .env or remove conflicting entries
```

### Phase 3: Frontend Integration Diagnostic

#### 3.1 Browser Network Tab Analysis
**CRITICAL PATTERNS TO LOOK FOR:**

1. **Preflight Request Failure**
   - Status: Failed/Error
   - Error: "CORS policy: Request header field x-csrf-token is not allowed"
   - Solution: Add X-CSRF-Token to backend CORS allowed headers

2. **Authentication Header Issues**
   - Status: 401 Unauthorized
   - Missing Authorization header
   - Solution: Verify token storage and axios interceptor

3. **CSRF Token Validation Failure**
   - Status: 403 Forbidden
   - Error: "CSRF token validation failed"
   - Solution: Verify token generation and header transmission

#### 3.2 Console Log Patterns
```javascript
// CRITICAL ERROR PATTERNS:

// Pattern 1: CORS Header Rejection
"Access to XMLHttpRequest blocked by CORS policy: Request header field 'x-csrf-token' is not allowed"
// Solution: Backend CORS configuration update required

// Pattern 2: Authentication Failure
"Request failed with status code 401"
// Solution: Check admin password case sensitivity

// Pattern 3: CSRF Validation Error
"Request failed with status code 403"
// Solution: Rate limiting function signature mismatch
```

### Phase 4: Backend Endpoint Diagnostic

#### 4.1 Rate Limiting Function Signature
```python
# CRITICAL ERROR PATTERN:
# TypeError: RateLimiter() got unexpected keyword argument 'identifier'

# Check function signature in app/core/middleware.py
# Incorrect:
@limiter.limit("5/minute", key_func=lambda: request.client.host, identifier=get_client_ip)

# Correct:
@limiter.limit("5/minute", key_func=get_client_ip)
```

#### 4.2 Authorization Middleware Conflicts
```python
# Check for permission conflicts in superuser endpoints
# File: app/api/v1/endpoints/superuser_endpoints.py

# CRITICAL: Verify dependency order
@router.post("/users/create")
async def create_user_endpoint(
    user_data: UserCreateSchema,
    current_user: User = Depends(get_current_superuser),  # FIRST
    db: AsyncSession = Depends(get_async_db),              # SECOND
    csrf_token: str = Depends(verify_csrf_token)           # THIRD
):
```

## 🔍 COMMON ERROR PATTERNS AND SOLUTIONS

### Error Pattern 1: CORS Header Rejection
**Symptoms:**
- Browser blocks preflight request
- "Request header field 'x-csrf-token' is not allowed"
- Frontend shows network error

**Root Cause:** X-CSRF-Token not in CORS allowed headers

**Solution:**
```python
# File: app/core/config.py
CORS_ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",  # ADD THIS
    "Accept",
    "Origin",
    "X-Requested-With"
]
```

### Error Pattern 2: Authentication Password Case Mismatch
**Symptoms:**
- Login returns 401 Unauthorized
- Correct email, password appears correct
- Backend logs show "Invalid credentials"

**Root Cause:** Password case sensitivity (Admin123456 vs admin123456)

**Solution:**
```bash
# Verify exact password in database
python -c "
import asyncio
from app.database import get_async_db
from app.models.user import User
from sqlalchemy import select

async def check_admin():
    async for db in get_async_db():
        result = await db.execute(select(User).where(User.email == 'admin@mestocker.com'))
        user = result.scalar_one_or_none()
        print(f'Admin exists: {user is not None}')
        if user:
            print(f'Email: {user.email}')
            # Check password hash matches expected input
asyncio.run(check_admin())
"
```

### Error Pattern 3: Environment Variable Override
**Symptoms:**
- Code changes not taking effect
- CORS configuration ignored
- Unexpected behavior despite correct code

**Root Cause:** .env files overriding application configuration

**Solution:**
```bash
# Check all possible .env locations
find /home/admin-jairo/MeStore -name ".env*" -type f -exec echo "=== {} ===" \; -exec cat {} \;

# Remove or update conflicting entries
# Priority: .env > app/.env > code configuration
```

### Error Pattern 4: Rate Limiting Function Signature Error
**Symptoms:**
- 500 Internal Server Error on POST requests
- TypeError about unexpected keyword argument 'identifier'
- Rate limiter fails to initialize

**Root Cause:** Incorrect slowapi-limiter function signature

**Solution:**
```python
# Incorrect:
@limiter.limit("5/minute", key_func=lambda: request.client.host, identifier=get_client_ip)

# Correct:
@limiter.limit("5/minute", key_func=get_client_ip)
```

### Error Pattern 5: CSRF Token Validation Chain Failure
**Symptoms:**
- 403 Forbidden on authenticated requests
- CSRF token appears in headers but validation fails
- Intermittent failures

**Root Cause:** Token generation/validation mismatch or dependency injection order

**Solution:**
```python
# Verify token generation endpoint
GET /api/v1/auth/csrf-token
# Must return: {"csrf_token": "valid-token"}

# Verify header transmission
X-CSRF-Token: valid-token

# Check dependency injection order in endpoints
```

## 📊 DIAGNOSTIC FLOWCHART

```
START: User Management Issue
├── Is Backend Running? (Port 8000)
│   ├── NO → Start backend service
│   └── YES → Continue
├── Is Frontend Running? (Port 5173)
│   ├── NO → Start frontend service
│   └── YES → Continue
├── Can you login as admin?
│   ├── NO → Check password case (Admin123456)
│   └── YES → Continue
├── Do OPTIONS requests work?
│   ├── NO → Check CORS headers (X-CSRF-Token)
│   └── YES → Continue
├── Do authenticated requests work?
│   ├── NO → Check rate limiting function signature
│   └── YES → Continue
├── Check environment file overrides
└── Verify complete integration chain
```

## 🚀 RECOVERY PROCEDURES

### Quick Fix Checklist (5 minutes)
1. ✅ Verify backend running on port 8000
2. ✅ Verify frontend running on port 5173
3. ✅ Test admin login with correct password case
4. ✅ Check CORS headers include X-CSRF-Token
5. ✅ Verify no environment file conflicts

### Complete Reset Procedure (15 minutes)
```bash
# 1. Stop all services
pkill -f uvicorn
pkill -f vite

# 2. Check for environment conflicts
cat .env | grep -E "(CORS_|ALLOWED_|AUTH_)"

# 3. Restart backend
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Restart frontend
cd frontend
npm run dev

# 5. Test complete integration chain
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'
```

## 📞 ESCALATION PROCEDURES

### Level 1: Self-Service (Use this guide)
- Follow diagnostic flowchart
- Apply common error pattern solutions
- Use recovery procedures

### Level 2: Agent Consultation
Contact responsible agents in order:
1. **backend-framework-ai** - Backend endpoint issues
2. **security-backend-ai** - Authentication/CSRF issues
3. **react-specialist-ai** - Frontend integration issues
4. **system-architect-ai** - Architecture/configuration issues

### Level 3: Master Orchestrator
Escalate when:
- Multiple agents cannot resolve
- Critical system failure
- Complete integration breakdown

## 🔬 TESTING VALIDATION COMMANDS

```bash
# Complete integration test
./scripts/test_user_management_integration.sh

# Individual component tests
python -m pytest tests/test_user_management.py -v
cd frontend && npm run test -- UserCreateModal

# Network connectivity test
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:5173

# Authentication flow test
./scripts/test_auth_flow.sh
```

## 📚 ADDITIONAL RESOURCES

- **Backend Configuration**: `/home/admin-jairo/MeStore/app/core/config.py`
- **Frontend Integration**: `/home/admin-jairo/MeStore/frontend/src/components/admin/`
- **CORS Middleware**: `/home/admin-jairo/MeStore/app/core/middleware.py`
- **Authentication Service**: `/home/admin-jairo/MeStore/app/api/v1/deps/auth.py`

---

**REMEMBER**: This guide contains REAL solutions to REAL problems. Every error pattern documented here has occurred and been resolved. Use this as your primary troubleshooting resource.