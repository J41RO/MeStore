# 🛡️ PREVENTION ALERT: CORS Configuration Checklist

## 🚨 ALERTA PREVENTIVA PERMANENTE

### Alert ID: PREV_CORS_001
### Created: 2025-09-28
### Creator: Agent Recruiter AI
### Purpose: Prevent CORS X-CSRF-Token configuration issues

---

## 🎯 MANDATORY CORS CONFIGURATION CHECKLIST

### ✅ REQUIRED HEADERS FOR MESTORE
```javascript
// MANDATORY headers que SIEMPRE deben estar en CORS_ALLOW_HEADERS:
CORS_ALLOW_HEADERS = [
    "Content-Type",      // ✅ Standard content type
    "Authorization",     // ✅ Bearer token authentication
    "Accept",           // ✅ Response format specification
    "Origin",           // ✅ Request origin identification
    "X-Requested-With", // ✅ AJAX request identification
    "X-CSRF-Token"      // 🚨 CRÍTICO: Frontend CSRF protection
]
```

### 🚨 CRITICAL WARNING SIGNS
Si ves estos síntomas, CHECK CORS IMMEDIATELY:
- ❌ POST/PUT/DELETE requests failing with 400 Bad Request
- ❌ OPTIONS preflight requests being rejected
- ❌ Frontend console errors about CORS policy
- ❌ User registration/login not working
- ❌ Any "Access-Control-Allow-Headers" errors

---

## 👥 AGENTS MUST FOLLOW THIS CHECKLIST

### 🛠️ backend-framework-ai
**BEFORE MODIFYING CORS:**
```bash
# 1. VERIFY current headers
grep -r "CORS_ALLOW_HEADERS" app/
grep -r "X-CSRF-Token" app/

# 2. CONFIRM X-CSRF-Token is included
# 3. TEST OPTIONS preflight requests
# 4. VALIDATE POST/PUT/DELETE operations work
```

### 🏗️ system-architect-ai
**ARCHITECTURAL VALIDATION:**
- ✅ Confirm CORS policy aligns with security requirements
- ✅ Verify headers don't expose unnecessary attack surface
- ✅ Document approved headers in architecture docs
- ✅ Validate frontend-backend header coordination

### 🛡️ security-backend-ai
**SECURITY CHECKLIST:**
- ✅ X-CSRF-Token properly validates CSRF protection
- ✅ No security implications of additional headers
- ✅ Frontend sending headers securely
- ✅ No credentials leaked through headers

### 🎨 frontend-security-ai
**FRONTEND VALIDATION:**
- ✅ Confirm which headers frontend actually sends
- ✅ Verify headers are required for functionality
- ✅ Document frontend header requirements
- ✅ Test cross-origin requests work properly

---

## 🔬 MANDATORY TESTS

### Test 1: CORS Preflight Validation
```python
def test_cors_allows_csrf_token():
    """MANDATORY: Verify X-CSRF-Token allowed in CORS"""
    response = client.options("/api/v1/users/", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-CSRF-Token"
    })
    assert response.status_code == 200
    allowed_headers = response.headers.get("Access-Control-Allow-Headers", "")
    assert "X-CSRF-Token" in allowed_headers
```

### Test 2: POST Request with CSRF Token
```python
def test_post_with_csrf_token_works():
    """MANDATORY: Verify POST requests work with X-CSRF-Token"""
    response = client.post("/api/v1/users/",
        json={"email": "test@test.com", "password": "test123"},
        headers={"X-CSRF-Token": "test-token"}
    )
    # Should NOT fail due to CORS (may fail for other reasons)
    assert response.status_code != 400  # 400 = CORS failure
```

### Test 3: Integration Test
```python
def test_frontend_backend_cors_integration():
    """MANDATORY: Verify frontend headers work with backend CORS"""
    # Simulate exact headers frontend sends
    frontend_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
        "X-CSRF-Token": "csrf-token",
        "Origin": "http://localhost:5173"
    }
    response = client.post("/api/v1/auth/login",
        json={"email": "test@test.com", "password": "test123"},
        headers=frontend_headers
    )
    assert response.status_code != 400  # No CORS rejection
```

---

## 📋 CONFIGURATION VALIDATION COMMANDS

### Quick CORS Check
```bash
# Run this BEFORE any CORS modifications:
cd /home/admin-jairo/MeStore

# 1. Check current CORS configuration
grep -n "CORS_ALLOW_HEADERS" app/main.py app/core/config.py

# 2. Verify X-CSRF-Token is present
grep -r "X-CSRF-Token" app/ || echo "❌ X-CSRF-Token NOT FOUND"

# 3. Test server starts without errors
python -c "from app.main import app; print('✅ App imports successfully')"

# 4. Run CORS-specific tests
python -m pytest tests/ -k "cors" -v
```

### Full Validation Suite
```bash
# MANDATORY before committing CORS changes:

# 1. Unit tests
python -m pytest tests/test_cors.py -v

# 2. Integration tests
python -m pytest tests/test_api/ -k "preflight or options" -v

# 3. Authentication flow tests
python -m pytest tests/test_auth.py -v

# 4. Frontend simulation tests
npm run test -- --grep "cors"
```

---

## 🚨 ESCALATION TRIGGERS

### IMMEDIATE ESCALATION if:
- ❌ Any POST/PUT/DELETE requests fail after CORS changes
- ❌ Frontend cannot authenticate users
- ❌ CORS tests fail in CI/CD pipeline
- ❌ Production complaints about authentication issues

### ESCALATION PATH:
1. **Responsible Agent** (usually backend-framework-ai)
2. **system-architect-ai** (if architectural decision needed)
3. **master-orchestrator** (if coordination issues)
4. **director-enterprise-ceo** (if business impact)

---

## 🔄 MAINTENANCE SCHEDULE

### Weekly Check (Automated)
- ✅ Verify CORS configuration unchanged
- ✅ Run CORS test suite
- ✅ Check for new headers needed by frontend

### Monthly Review
- ✅ Review frontend header requirements
- ✅ Security audit of allowed headers
- ✅ Performance impact of CORS policy
- ✅ Update documentation if needed

### After Each Frontend Update
- ✅ Check if new headers required
- ✅ Validate existing CORS still works
- ✅ Update tests for new header requirements

---

## 📚 REFERENCE DOCUMENTATION

### Files to Always Check
```
app/main.py              # Primary CORS configuration
app/core/config.py       # CORS environment variables
frontend/src/services/   # Headers frontend sends
tests/test_cors.py       # CORS validation tests
.workspace/critical_issues/CORS_X_CSRF_TOKEN_ISSUE.md  # Historical issue
```

### External References
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CSRF Token Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

**⚡ REMEMBER: CORS issues = PRODUCTION DOWN**
**🚨 ALWAYS test CORS changes in development first**
**📞 When in doubt, ASK the responsible agent**

---
**🛡️ This alert prevents critical production failures**
**📅 Created**: 2025-09-28
**🤖 Creator**: Agent Recruiter AI
**🔄 Review**: Required after each CORS modification