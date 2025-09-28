# 🛡️ CORS CONFIGURATION STANDARDS - MeStore

## 📋 DOCUMENT METADATA
- **Created**: 2025-09-28
- **Last Updated**: 2025-09-28
- **Created by**: Agent Recruiter AI
- **Version**: v1.0.0
- **Status**: ACTIVE
- **Applies to**: All backend agents, system architects, security specialists

---

## 🎯 PURPOSE

This document establishes **MANDATORY** standards for CORS (Cross-Origin Resource Sharing) configuration in MeStore to prevent critical production failures like the X-CSRF-Token issue detected on 2025-09-28.

**Critical Context**: CORS misconfigurations can completely block frontend-backend communication, resulting in:
- Total system unavailability for POST/PUT/DELETE operations
- User registration and authentication failures
- Transaction processing failures
- Admin panel inaccessibility

---

## 🚨 MANDATORY CORS HEADERS

### Required Headers (NEVER REMOVE)
```javascript
// MANDATORY in ALL CORS configurations:
CORS_ALLOW_HEADERS = [
    "Content-Type",      // Standard JSON/form content
    "Authorization",     // Bearer token authentication
    "Accept",           // Response format specification
    "Origin",           // Request origin for CORS validation
    "X-Requested-With", // AJAX/XMLHttpRequest identification
    "X-CSRF-Token"      // 🚨 CRITICAL: Frontend CSRF protection
]
```

### Optional Headers (Project-Specific)
```javascript
// Add these ONLY if needed by frontend:
OPTIONAL_HEADERS = [
    "X-API-Key",        // If API key authentication used
    "X-Request-ID",     // For request tracing
    "Cache-Control",    // If cache headers needed
    "X-Client-Version"  // For version-specific handling
]
```

### Forbidden Headers (SECURITY)
```javascript
// NEVER allow these headers:
FORBIDDEN_HEADERS = [
    "Cookie",           // Security risk: credential exposure
    "X-Forwarded-For",  // Should be handled by proxy
    "X-Real-IP",        // Should be handled by proxy
    "Server",           // Information disclosure
    "X-Powered-By"      // Information disclosure
]
```

---

## 🏗️ IMPLEMENTATION STANDARDS

### FastAPI Configuration (app/main.py)
```python
from fastapi.middleware.cors import CORSMiddleware

# STANDARD CORS configuration for MeStore
CORS_ORIGINS = [
    "http://localhost:5173",    # Vite dev server
    "http://127.0.0.1:5173",    # Vite dev server alternative
    "http://192.168.1.137:5173", # Network access
    # Add production domains here
]

CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
    "X-CSRF-Token"  # 🚨 CRITICAL: Must be included
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=CORS_ALLOW_HEADERS,
)
```

### Environment Variables (app/core/config.py)
```python
# CORS configuration through environment variables
CORS_ORIGINS: List[str] = Field(
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.137:5173"
    ],
    env="CORS_ORIGINS"
)

CORS_ALLOW_HEADERS: List[str] = Field(
    default=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
    env="CORS_ALLOW_HEADERS"
)
```

---

## 🧪 MANDATORY TESTING STANDARDS

### Test 1: Basic CORS Functionality
```python
def test_cors_basic_headers():
    """Verify standard CORS headers are allowed"""
    response = client.options("/api/v1/users/", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    })
    assert response.status_code == 200
    allowed = response.headers.get("Access-Control-Allow-Headers", "")
    assert "Content-Type" in allowed
    assert "Authorization" in allowed
```

### Test 2: X-CSRF-Token Header (CRITICAL)
```python
def test_cors_csrf_token_allowed():
    """CRITICAL: Verify X-CSRF-Token is allowed in CORS"""
    response = client.options("/api/v1/users/", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-CSRF-Token"
    })
    assert response.status_code == 200
    allowed = response.headers.get("Access-Control-Allow-Headers", "")
    assert "X-CSRF-Token" in allowed, "X-CSRF-Token MUST be allowed for frontend authentication"
```

### Test 3: POST with CSRF Token
```python
def test_post_request_with_csrf_token():
    """Verify POST requests work with X-CSRF-Token header"""
    response = client.post("/api/v1/auth/login",
        json={"email": "test@test.com", "password": "test123"},
        headers={
            "Origin": "http://localhost:5173",
            "X-CSRF-Token": "test-csrf-token"
        }
    )
    # Should NOT fail due to CORS (may fail for auth reasons)
    assert response.status_code != 400, "CORS should not block requests with X-CSRF-Token"
```

### Test 4: Multiple Headers Combination
```python
def test_cors_multiple_headers():
    """Test realistic frontend header combination"""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization,X-CSRF-Token"
    }
    response = client.options("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    allowed = response.headers.get("Access-Control-Allow-Headers", "")
    for header in ["Content-Type", "Authorization", "X-CSRF-Token"]:
        assert header in allowed, f"Header {header} must be allowed"
```

---

## 👥 AGENT RESPONSIBILITIES

### 🛠️ backend-framework-ai (PRIMARY RESPONSIBLE)
**MUST DO:**
- ✅ Implement all CORS configuration changes
- ✅ Ensure X-CSRF-Token is ALWAYS included in allowed headers
- ✅ Run all CORS tests before committing
- ✅ Coordinate with frontend team on header requirements
- ✅ Document any deviations from standards

**NEVER DO:**
- ❌ Remove X-CSRF-Token from allowed headers
- ❌ Change CORS configuration without testing
- ❌ Add credentials=True without security review

### 🏗️ system-architect-ai (APPROVAL AUTHORITY)
**MUST DO:**
- ✅ Approve all CORS configuration changes in app/main.py
- ✅ Validate architectural impact of header additions
- ✅ Ensure consistency across environments
- ✅ Review security implications with security team

**AUTHORITY:**
- Final approval for app/main.py modifications
- Architecture compliance validation
- Cross-environment consistency

### 🛡️ security-backend-ai (SECURITY VALIDATION)
**MUST DO:**
- ✅ Security review of all header additions
- ✅ Validate CSRF token implementation
- ✅ Assess attack surface implications
- ✅ Approve credentials and origins settings

**VETO POWER:**
- Can deny header additions if security risk
- Must approve allow_credentials=True
- Authority over security-related headers

### 🎨 frontend-security-ai (REQUIREMENTS VALIDATION)
**MUST DO:**
- ✅ Document which headers frontend actually sends
- ✅ Validate header requirements are minimal
- ✅ Test frontend works with backend CORS policy
- ✅ Report new header requirements promptly

---

## 🚨 VIOLATION CONSEQUENCES

### Severity Levels

#### CRITICAL VIOLATION (Production Down)
**Examples:**
- Removing X-CSRF-Token from allowed headers
- Blocking all POST/PUT/DELETE operations
- Breaking user authentication

**Consequences:**
- Immediate escalation to master-orchestrator
- Production rollback required
- Incident documentation mandatory
- Agent training review

#### HIGH VIOLATION (Feature Breaking)
**Examples:**
- Adding headers without testing
- Misconfiguring origins
- Enabling credentials without security review

**Consequences:**
- Development freeze until fixed
- Mandatory testing before deployment
- Security team review required

#### MEDIUM VIOLATION (Process Deviation)
**Examples:**
- Not running tests before commit
- Missing documentation
- No coordination with affected teams

**Consequences:**
- Warning documentation
- Process review required
- Additional oversight on next changes

---

## 🔄 MAINTENANCE AND UPDATES

### Weekly Automated Checks
```bash
# Run these checks automatically every week:

# 1. Verify CORS configuration unchanged unexpectedly
git log --oneline app/main.py app/core/config.py | head -5

# 2. Run CORS test suite
python -m pytest tests/test_cors.py -v

# 3. Check for new frontend header requirements
grep -r "headers:" frontend/src/services/ | grep -i csrf

# 4. Validate production CORS configuration
curl -X OPTIONS -H "Origin: https://production-domain.com" \
     -H "Access-Control-Request-Headers: X-CSRF-Token" \
     https://api.production-domain.com/api/v1/health
```

### Monthly Reviews
- Review frontend header requirements
- Security audit of allowed headers
- Performance impact assessment
- Documentation updates

### After Frontend Updates
- Check for new header requirements
- Validate existing CORS still works
- Update tests for new requirements
- Document any changes

---

## 📚 REFERENCE AND ESCALATION

### Quick Reference
```bash
# Check current CORS config
grep -A 10 "CORS_ALLOW_HEADERS" app/main.py app/core/config.py

# Test CORS quickly
python -c "
import requests
r = requests.options('http://localhost:8000/api/v1/users/', headers={
    'Origin': 'http://localhost:5173',
    'Access-Control-Request-Headers': 'X-CSRF-Token'
})
print(f'Status: {r.status_code}')
print(f'Allowed: {r.headers.get(\"Access-Control-Allow-Headers\", \"None\")}')
"

# Run CORS tests
python -m pytest tests/test_cors.py -v -x
```

### Escalation Path
1. **backend-framework-ai**: Primary implementation
2. **system-architect-ai**: Architecture approval
3. **security-backend-ai**: Security validation
4. **master-orchestrator**: Coordination issues
5. **director-enterprise-ceo**: Business impact

### Emergency Contacts
- Critical CORS failures: Immediately notify all four primary agents
- Production down: Escalate to master-orchestrator within 5 minutes
- Security concerns: security-backend-ai has veto power

---

## 📖 HISTORICAL CONTEXT

### CORS X-CSRF-Token Issue (2025-09-28)
**What Happened:**
- X-CSRF-Token header was missing from CORS_ALLOW_HEADERS
- Frontend sent header but backend rejected via CORS policy
- All POST/PUT/DELETE operations failed with 400 Bad Request
- Complete system unavailability for user interactions

**Root Cause:**
- Incomplete CORS configuration during initial setup
- No integration tests for frontend-backend header coordination
- Missing documentation of frontend header requirements

**Prevention:**
- This standards document created
- Mandatory tests implemented
- Agent notification system established
- Prevention alerts created

### Lessons Learned
1. **Frontend-Backend Coordination**: Always validate headers end-to-end
2. **Testing Gaps**: Integration tests must cover CORS scenarios
3. **Documentation**: Header requirements must be documented
4. **Monitoring**: CORS issues should trigger immediate alerts

---

**⚡ COMPLIANCE WITH THESE STANDARDS IS MANDATORY**
**🚨 DEVIATIONS REQUIRE EXPLICIT APPROVAL FROM ALL RESPONSIBLE AGENTS**
**📞 WHEN IN DOUBT, ASK - CORS ISSUES = PRODUCTION DOWN**

---
**📅 Created**: 2025-09-28
**🤖 Creator**: Agent Recruiter AI
**🔄 Next Review**: 2025-10-28
**📋 Version**: v1.0.0
**✅ Status**: ACTIVE - MANDATORY COMPLIANCE