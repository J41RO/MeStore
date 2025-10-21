# QUICK REFERENCE - AUTH ENDPOINTS
## Guía Rápida de Endpoints de Autenticación MeStore

**Uso**: Para consulta rápida durante desarrollo
**Versión**: 1.0.0
**Fecha**: 2025-10-13

---

## 🚀 ENDPOINTS PRINCIPALES (22 TOTAL)

### LOGIN (2)
```bash
# Login regular
POST /api/v1/auth/login
Body: {"email": "user@example.com", "password": "Pass123"}
→ 200: {access_token, refresh_token, user}

# Login admin
POST /api/v1/auth/admin-login
Body: {"email": "admin@mestocker.com", "password": "Admin123456"}
→ 200: {access_token, refresh_token, user}
```

### REGISTRO (4)
```bash
# Registro multi-tipo (RECOMENDADO)
POST /api/v1/auth/register-multi-type
Body: {email, password, nombre, telefono, ...}
→ 201: {user_id, user_type, account_status, vendor_status, next_steps}

# Registro legacy
POST /api/v1/auth/register
→ 201: {access_token, user}

# Registro customer específico
POST /api/v1/auth/register/customer
→ 201: {user_id, email, phone, account_status}
```

### VERIFICACIÓN (6)
```bash
# Enviar código email (autenticado)
POST /api/v1/auth/send-verification-email
Headers: {Authorization: "Bearer <token>"}
Body: {"email": "user@example.com"}
→ 200: {success, message, expires_in}

# Enviar SMS (autenticado)
POST /api/v1/auth/send-verification-sms
Headers: {Authorization: "Bearer <token>"}
Body: {"phone": "+573001234567"}
→ 200: {success, message, expires_in}

# Enviar SMS (público) 🔥 RATE LIMITED
POST /api/v1/auth/send-sms-public
Body: {"phone": "+573001234567"}
→ 200: {success, message, expires_in}

# Verificar email con código
POST /api/v1/auth/verify/email
Body: {"email": "user@example.com", "code": "123456"}
→ 200: {success, email_verified, phone_verified, account_active}

# Verificar teléfono con código
POST /api/v1/auth/verify/phone
Body: {"phone": "+573001234567", "code": "123456"}
→ 200: {success, email_verified, phone_verified, account_active}

# Verificar email con link (GET)
GET /api/v1/auth/verify-email?token=abc123xyz
→ 200: {success, message, email_verified}
```

### SESIÓN (4)
```bash
# Info usuario actual
GET /api/v1/auth/me
Headers: {Authorization: "Bearer <token>"}
→ 200: {id, email, user_type, nombre, account_status, vendor_status}

# Actualizar perfil
PUT /api/v1/auth/users/me
Headers: {Authorization: "Bearer <token>"}
Body: {nombre, telefono, direccion, ciudad}
→ 200: {success, message, user}

# Refrescar token
POST /api/v1/auth/refresh-token
Body: {"refresh_token": "xyz..."}
→ 200: {access_token, refresh_token}

# Logout
POST /api/v1/auth/logout
Headers: {Authorization: "Bearer <token>"}
Body: {"refresh_token": "xyz..."}
→ 200: {success, message}
```

### RECUPERAR CONTRASEÑA (2)
```bash
# Solicitar reset
POST /api/v1/auth/forgot-password
Body: {"email": "user@example.com"}
→ 200: {success, message}

# Confirmar reset
POST /api/v1/auth/reset-password
Body: {"token": "abc...", "new_password": "NewPass123", "confirm_password": "NewPass123"}
→ 200: {success, message}
```

### ADMIN VENDORS (3) 🔒
```bash
# Listar vendedores pendientes
GET /api/v1/auth/admin/pending-sellers
Headers: {Authorization: "Bearer <admin_token>"}
Rate Limit: 30/min
→ 200: {count, sellers: [{id, email, vendor_status, ...}]}

# Aprobar vendedor
POST /api/v1/auth/admin/approve-seller/{user_id}
Headers: {Authorization: "Bearer <admin_token>"}
Rate Limit: 10/min
→ 200: {success, message, seller_id, vendor_status}

# Rechazar vendedor
POST /api/v1/auth/admin/reject-seller/{user_id}
Headers: {Authorization: "Bearer <admin_token>"}
Body: {"reason": "Razón del rechazo (min 20 chars)"}
Rate Limit: 10/min
→ 200: {success, message, seller_id, vendor_status, rejection_reason}
```

---

## 🎯 FLUJOS RÁPIDOS

### BUYER (Comprador)
```
1. POST /register-multi-type
   Body: {email, password, nombre, telefono}

2. POST /verify/email
   Body: {email, code}

3. POST /verify/phone
   Body: {phone, code}

✅ account_status = ACTIVE
→ Usuario puede comprar
```

### VENDOR NATURAL
```
1. POST /register-multi-type
   Body: {email, password, cedula, nombre, apellido, direccion_fiscal, ...}

2. POST /verify/email + POST /verify/phone

3. ⏳ Esperar aprobación admin

4. Admin: POST /admin/approve-seller/{user_id}

✅ vendor_status = APPROVED, account_status = ACTIVE
→ Usuario puede vender
```

### VENDOR JURÍDICA
```
1. POST /register-multi-type
   Body: {email, password, nit, razon_social, representante_legal, ...}

2. POST /verify/email + POST /verify/phone

3. (Futuro) POST /vendors/upload-documents

4. ⏳ Esperar aprobación admin

5. Admin: POST /admin/approve-seller/{user_id}

✅ vendor_status = APPROVED, account_status = ACTIVE
→ Empresa puede vender
```

---

## 🔒 SEGURIDAD

### Rate Limits
- Admin endpoints: 10-30/min por IP
- SMS público: 3/hora por IP, 2/hora por teléfono
- Brute force: 5 intentos por email+IP

### Protecciones Activas
- ✅ XSS en reject_reason
- ✅ Self-approval bloqueado
- ✅ Self-rejection bloqueado
- ✅ Phone E.164 validation
- ✅ JWT token rotation
- ✅ Session invalidation

### Headers Requeridos
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

## 🧪 TESTING RÁPIDO

### curl Examples
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123"}'

# Registro BUYER
curl -X POST "http://localhost:8000/api/v1/auth/register-multi-type" \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@example.com","password":"Pass123","nombre":"Juan Pérez","telefono":"+573001234567"}'

# Admin login
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mestocker.com","password":"Admin123456"}'

# Listar pendientes (con token)
curl -X GET "http://localhost:8000/api/v1/auth/admin/pending-sellers" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📊 SCHEMAS RÁPIDOS

### Request Common
```typescript
interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterBuyer {
  email: string;
  password: string;
  nombre: string;
  telefono: string; // E.164 format
}

interface VerifyEmailRequest {
  email: string;
  code: string; // 6 dígitos
}

interface VerifyPhoneRequest {
  phone: string; // E.164
  code: string; // 6 dígitos
}
```

### Response Common
```typescript
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: {
    id: string;
    email: string;
    user_type: "BUYER" | "VENDOR" | "ADMIN" | "SUPERUSER";
    nombre: string;
    is_active: boolean;
    is_verified: boolean;
  };
}

interface VerificationResponse {
  success: boolean;
  message: string;
  email_verified: boolean;
  phone_verified: boolean;
  account_active: boolean;
}

interface MultiTypeRegistrationResponse {
  success: boolean;
  message: string;
  user_id: string;
  user_type: string;
  account_status: string;
  vendor_status?: string;
  next_steps: string[];
}
```

---

## ⚡ ERRORES COMUNES

| Error | Causa | Solución |
|-------|-------|----------|
| 401 Unauthorized | Token inválido/expirado | Refrescar token o login nuevamente |
| 400 Email duplicado | Email ya registrado | Usar otro email o login |
| 400 Teléfono duplicado | Teléfono ya registrado | Usar otro teléfono |
| 429 Too Many Requests | Rate limit excedido | Esperar y reintentar |
| 403 Self-approval blocked | Admin intenta aprobarse | Pedir a otro admin |
| 400 Invalid phone format | Teléfono no es E.164 | Usar formato +573001234567 |

---

## 📞 CONTACTO

**Responsables**:
- security-backend-ai (seguridad)
- api-architect-ai (diseño)
- backend-framework-ai (implementación)

**Consultas**:
```bash
python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/api/v1/endpoints/auth.py "Tu consulta"
```

---

**Última Actualización**: 2025-10-13
**Versión Completa**: AUTH_ENDPOINTS_AUDIT_REPORT.md
