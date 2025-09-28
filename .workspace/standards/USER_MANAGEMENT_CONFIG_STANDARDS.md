# USER MANAGEMENT CONFIGURATION STANDARDS

**Document Status**: MANDATORY COMPLIANCE
**Created**: 2025-09-28
**Last Updated**: 2025-09-28
**Created By**: Agent Recruiter AI
**Version**: v1.0.0
**Priority**: CRITICAL
**Scope**: ALL User Management implementations

## 🎯 PURPOSE

This document establishes mandatory configuration standards for User Management systems based on real implementation experience. These standards prevent the common configuration errors that cause system failures.

## 🔒 PROTECTED CONFIGURATION VALUES

### Critical Admin User (NEVER MODIFY)
```python
# PROTECTED VALUES - NEVER CHANGE
ADMIN_EMAIL = "admin@mestocker.com"
ADMIN_PASSWORD = "Admin123456"  # CASE SENSITIVE
ADMIN_ROLE = "superuser"
ADMIN_STATUS = "active"
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Password MUST be exactly "Admin123456" (capital A)
- ✅ Email MUST be exactly "admin@mestocker.com"
- ✅ Role MUST be "superuser"
- ✅ Account MUST remain active
- ❌ NEVER delete this account
- ❌ NEVER change credentials without system-wide notification

## 🌐 CORS CONFIGURATION STANDARDS

### Mandatory CORS Headers
```python
# File: app/core/config.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",    # Frontend development
    "http://192.168.1.137:5173", # Network development
    "https://production-domain.com"  # Production (when deployed)
]

CORS_ALLOWED_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH"
]

CORS_ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",  # CRITICAL: Must include for User Management
    "Accept",
    "Origin",
    "X-Requested-With",
    "Access-Control-Allow-Origin"
]

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["X-CSRF-Token"]
```

**COMPLIANCE REQUIREMENTS:**
- ✅ X-CSRF-Token MUST be in allowed headers
- ✅ Credentials MUST be allowed (True)
- ✅ Both localhost and network IPs for development
- ❌ NEVER remove X-CSRF-Token from headers
- ❌ NEVER set allow_credentials to False

### CORS Validation Commands
```bash
# Test CORS preflight for User Management endpoints
curl -X OPTIONS http://localhost:8000/api/v1/users/create \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization,X-CSRF-Token" \
  -v

# MUST return: Access-Control-Allow-Headers containing X-CSRF-Token
```

## 🔐 AUTHENTICATION CONFIGURATION STANDARDS

### JWT Configuration
```python
# File: app/core/config.py
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Secret key MUST be at least 32 characters in production
- ✅ Algorithm MUST be HS256
- ✅ Access token expiry MUST NOT exceed 2 hours
- ✅ Refresh token expiry MUST NOT exceed 30 days

### Password Security Standards
```python
# File: app/core/security.py
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = False  # Optional

# Hashing configuration
BCRYPT_ROUNDS = 12  # Strong but performant
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Minimum 8 character passwords
- ✅ Must include uppercase, lowercase, and numbers
- ✅ bcrypt rounds between 10-14 (12 recommended)

## 🛡️ CSRF PROTECTION STANDARDS

### CSRF Token Configuration
```python
# File: app/core/security.py
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", "csrf-secret-key-change-in-production")
CSRF_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_COOKIE_SECURE = True  # Production only
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Header name MUST be "X-CSRF-Token"
- ✅ Token expiry MUST NOT exceed 60 minutes
- ✅ HttpOnly MUST be False for frontend access
- ✅ Secure MUST be True in production (HTTPS)

### CSRF Endpoint Standards
```python
# MANDATORY endpoint for token retrieval
@router.get("/csrf-token")
async def get_csrf_token():
    return {"csrf_token": generate_csrf_token()}

# MANDATORY in all protected endpoints
csrf_token: str = Depends(verify_csrf_token)
```

## ⚡ RATE LIMITING STANDARDS

### Rate Limiter Configuration
```python
# File: app/core/middleware.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# CORRECT function signature
limiter = Limiter(key_func=get_remote_address)

# CORRECT endpoint decoration
@limiter.limit("5/minute")
@router.post("/users/create")
async def create_user_endpoint(...):
    pass
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Use slowapi-limiter library
- ✅ Use get_remote_address for key function
- ✅ Apply reasonable limits (5/minute for creation endpoints)
- ❌ NEVER use incorrect function signatures with 'identifier' parameter

### Rate Limiting Patterns
```python
# Authentication endpoints
@limiter.limit("10/minute")  # Login attempts

# User creation endpoints
@limiter.limit("5/minute")   # Account creation

# Data retrieval endpoints
@limiter.limit("60/minute")  # General API calls

# Administrative endpoints
@limiter.limit("30/minute")  # Admin operations
```

## 🗄️ DATABASE CONFIGURATION STANDARDS

### Connection Configuration
```python
# File: app/core/config.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/mestore"
)

# Connection pool settings
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 30
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Use asyncpg driver for PostgreSQL
- ✅ Pool size appropriate for load (20 minimum)
- ✅ Connection recycling enabled (1 hour)

### Migration Standards
```python
# File: alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/mestore

# Version locations
version_locations = alembic/versions
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Migrations MUST be tested before production
- ✅ Backup database before migration
- ✅ Use async-compatible migration scripts

## 🚀 SERVICE DEPLOYMENT STANDARDS

### Port Configuration
```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "8000:8000"    # FIXED: Backend always on 8000

  frontend:
    ports:
      - "5173:5173"    # FIXED: Frontend always on 5173

  postgres:
    ports:
      - "5432:5432"    # FIXED: Database always on 5432
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Backend MUST run on port 8000
- ✅ Frontend MUST run on port 5173
- ✅ Database MUST run on port 5432
- ❌ NEVER change these ports without updating all configurations

### Network Configuration
```yaml
# Network accessibility requirements
backend:
  host: "0.0.0.0"     # Network accessible
  port: 8000

frontend:
  host: "0.0.0.0"     # Network accessible
  port: 5173
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Services MUST be network accessible (0.0.0.0)
- ✅ NOT restricted to localhost only
- ✅ Firewall rules allow internal network access

## 📝 ENVIRONMENT VARIABLE STANDARDS

### Required Environment Variables
```bash
# .env file template
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mestore

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-at-least-32-chars
CSRF_SECRET_KEY=your-super-secret-csrf-key-at-least-32-chars

# CORS (Optional - code defaults recommended)
# CORS_ALLOWED_ORIGINS=http://localhost:5173,http://192.168.1.137:5173

# Rate Limiting
RATE_LIMIT_ENABLED=true

# Debug (Development only)
DEBUG=true
```

**COMPLIANCE REQUIREMENTS:**
- ✅ All secret keys MUST be at least 32 characters
- ✅ Database URL MUST use asyncpg driver
- ✅ Debug MUST be False in production
- ❌ NEVER commit secrets to version control

### Environment Priority Order
1. **Environment Variables** (highest priority)
2. **`.env` file in project root**
3. **`app/.env` file**
4. **Code defaults** (lowest priority)

**CRITICAL**: Environment files can completely override code configuration.

## 🧪 TESTING CONFIGURATION STANDARDS

### Test Database Configuration
```python
# tests/conftest.py
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_mestore"

# Isolated test transactions
@pytest.fixture
async def db_session():
    async with async_session() as session:
        transaction = await session.begin()
        yield session
        await transaction.rollback()
```

**COMPLIANCE REQUIREMENTS:**
- ✅ Separate test database required
- ✅ Transaction rollback for test isolation
- ✅ No test data in production database

### Test Service Configuration
```yaml
# docker-compose.test.yml
services:
  test-postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: test_mestore
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5433:5432"  # Different port for testing
```

## 📊 MONITORING AND LOGGING STANDARDS

### Logging Configuration
```python
# File: app/core/config.py
LOGGING_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/mestore.log"

# Security event logging
SECURITY_LOG_ENABLED = True
SECURITY_LOG_FILE = "logs/security.log"
```

**COMPLIANCE REQUIREMENTS:**
- ✅ INFO level minimum for production
- ✅ Security events MUST be logged
- ✅ Log rotation configured for production

### Health Check Standards
```python
# Mandatory health check endpoint
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": await check_database_connection(),
        "cache": await check_cache_connection()
    }
```

## 🔍 VALIDATION COMMANDS

### Configuration Validation Script
```bash
#!/bin/bash
echo "=== USER MANAGEMENT CONFIGURATION VALIDATION ==="

# 1. Service ports
echo "1. Checking service ports..."
netstat -tlnp | grep :8000 && echo "✅ Backend port 8000" || echo "❌ Backend port 8000"
netstat -tlnp | grep :5173 && echo "✅ Frontend port 5173" || echo "❌ Frontend port 5173"

# 2. CORS validation
echo "2. Checking CORS configuration..."
curl -X OPTIONS http://localhost:8000/api/v1/users/create \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Headers: X-CSRF-Token" \
  -v 2>&1 | grep "X-CSRF-Token" && echo "✅ CORS X-CSRF-Token" || echo "❌ CORS X-CSRF-Token"

# 3. Authentication validation
echo "3. Checking authentication..."
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' | \
  jq -r '.access_token' | grep -v null && echo "✅ Admin auth" || echo "❌ Admin auth"

# 4. CSRF token validation
echo "4. Checking CSRF token..."
curl -s http://localhost:8000/api/v1/auth/csrf-token | \
  jq -r '.csrf_token' | grep -v null && echo "✅ CSRF token" || echo "❌ CSRF token"

echo "=== VALIDATION COMPLETE ==="
```

## 📋 COMPLIANCE CHECKLIST

### Pre-Deployment Checklist
- [ ] ✅ Admin credentials configured correctly
- [ ] ✅ CORS headers include X-CSRF-Token
- [ ] ✅ Rate limiting function signatures correct
- [ ] ✅ JWT secret keys at least 32 characters
- [ ] ✅ Database URL uses asyncpg driver
- [ ] ✅ Services run on standard ports (8000, 5173)
- [ ] ✅ Network accessibility configured
- [ ] ✅ Environment variables properly set
- [ ] ✅ Test database isolated from production
- [ ] ✅ Health check endpoints functional
- [ ] ✅ Security logging enabled
- [ ] ✅ CSRF protection active

### Post-Deployment Validation
- [ ] ✅ All configuration validation commands pass
- [ ] ✅ Complete user creation flow functional
- [ ] ✅ Rate limiting properly enforced
- [ ] ✅ CORS policies working correctly
- [ ] ✅ Authentication and authorization functional
- [ ] ✅ Error handling and logging working
- [ ] ✅ Performance within acceptable limits

## 🆘 NON-COMPLIANCE CONSEQUENCES

### Configuration violations can cause:
- 🚨 **Complete system failure** (incorrect CORS, auth config)
- 🛡️ **Security vulnerabilities** (weak secrets, improper CSRF)
- ⚡ **Performance issues** (incorrect rate limiting, database config)
- 🔒 **Authentication failures** (JWT misconfiguration)
- 🌐 **Network accessibility issues** (port/host misconfiguration)

### Compliance enforcement:
- **Automated validation** in CI/CD pipeline
- **Mandatory review** for configuration changes
- **Rollback procedures** for non-compliant deployments

---

**REMEMBER**: These standards are based on real implementation failures. Every requirement prevents specific problems that have occurred. Compliance is mandatory, not optional.