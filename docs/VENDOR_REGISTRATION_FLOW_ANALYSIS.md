# ANÁLISIS EXHAUSTIVO DEL FLUJO DE REGISTRO DE VENDEDORES - MeStore

## RESUMEN EJECUTIVO

El proyecto MeStore implementa un flujo completo de registro, verificación y aprobación de vendedores con tres tipos principales: BUYER, VENDOR Persona Natural y VENDOR Persona Jurídica. El flujo incluye:

1. **Autenticación con JWT** segura con integratedAuthService
2. **Verificación dual**: Email (token link) + SMS (Twilio OTP)
3. **Aprobación administrativa**: Estados granulares (DRAFT → APPROVED/REJECTED)
4. **Documentos de vendor**: Para personas jurídicas
5. **Estados de cuenta**: PENDING → ACTIVE

---

## 1. ENDPOINTS DE AUTENTICACIÓN Y VERIFICACIÓN

### 1.1 ENDPOINTS DE REGISTRO

#### POST /auth/register
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 475)
- **Tipo**: Registro BUYER/VENDOR simple con verificación dual
- **Body esperado**:
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "Segura123!",
    "nombre": "Juan",
    "telefono": "+573001234567",
    "user_type": "VENDOR"
  }
  ```
- **Respuesta**: TokenResponse con JWT access/refresh
- **Estado implementado**: ✅ FUNCIONAL
- **Flujo**:
  1. Valida unicidad de email y teléfono
  2. Crea usuario con email_verified=False, phone_verified=False
  3. Genera token de verificación email (32 bytes URL-safe)
  4. Envía email con link de verificación (24h validez)
  5. Envía SMS con código Twilio Verify
  6. Retorna tokens JWT inmediatamente

#### POST /auth/register-multi-type
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 1828)
- **Tipo**: Registro avanzado con detección automática de tipo
- **Detección automática**:
  - Si tiene `nit` → VENDOR Persona Jurídica
  - Si tiene `cedula` + `direccion_fiscal` → VENDOR Persona Natural
  - Si no tiene campos de vendor → BUYER
- **Respuesta**: MultiTypeRegistrationResponse
- **Estado implementado**: ✅ FUNCIONAL
- **Diferencias por tipo**:

  **BUYER**:
  - account_status: PENDING → ACTIVE (después de verificar)
  - vendor_status: None
  - vendor_type: None
  - Activación automática después de verificación

  **VENDOR Persona Natural**:
  - account_status: PENDING
  - vendor_status: DRAFT (requiere aprobación admin)
  - tipo_vendedor: "persona_natural"
  - Requiere: cedula, nombre, apellido, dirección fiscal

  **VENDOR Persona Jurídica**:
  - account_status: PENDING
  - vendor_status: PENDING_DOCUMENTS (requiere documentos)
  - tipo_vendedor: "persona_juridica"
  - Requiere: NIT, razón social, representante legal

#### POST /auth/verify-email
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 1127)
- **Tipo**: GET con parámetro token
- **Parámetro**: `token` (string, token generado en /register)
- **Funcionamiento**:
  1. Valida token contra email_verification_token en DB
  2. Verifica que no esté expirado (24h)
  3. Marca email_verified = True
  4. Si teléfono también verificado → account_status = ACTIVE
  5. Limpia token usado
- **Estado implementado**: ✅ FUNCIONAL
- **Respuesta**: VerificationResponse con estado de verificación

#### POST /auth/send-verification-email
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 666)
- **Requisito**: Autenticación JWT requerida
- **Body**: `{"otp_type": "EMAIL"}`
- **Funcionamiento**:
  1. Genera código OTP de 6 dígitos
  2. Asigna al usuario con expiración 10 minutos
  3. Envía por email usando EmailService
  4. Respeta cooldown de 1 minuto
- **Estado implementado**: ✅ FUNCIONAL

#### POST /auth/send-verification-sms
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 720)
- **Requisito**: Autenticación JWT requerida
- **Body**: `{"otp_type": "SMS"}`
- **Funcionamiento**:
  1. Genera código OTP de 6 dígitos
  2. Envía vía Twilio SMSService
  3. Formatea números internacionales (+57 Colombia)
  4. Verifica rate limiting (máx 5 SMS/hora)
- **Estado implementado**: ✅ FUNCIONAL (con Twilio en simulación)

#### POST /auth/verify-email-otp
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 810)
- **Requisito**: Autenticación JWT requerida
- **Body**: `{"otp_code": "123456"}`
- **Funcionamiento**:
  1. Valida código contra otp_secret
  2. Verifica expiración (10 minutos)
  3. Cuenta intentos fallidos (máx 5)
  4. Si correcto → email_verified = True
  5. Si ambos verificados (email + SMS) → account_status = ACTIVE
- **Estado implementado**: ✅ FUNCIONAL

#### POST /auth/verify-phone-otp
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 950)
- **Requisito**: Autenticación JWT requerida
- **Body**: `{"otp_code": "123456"}`
- **Funcionamiento**: Igual a verify-email-otp pero para teléfono
- **Estado implementado**: ✅ FUNCIONAL

#### POST /auth/login
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 158)
- **Body**: `{"email": "user@example.com", "password": "pass123"}`
- **Seguridad**: 
  - Protección contra fuerza bruta
  - Rate limiting por IP
  - Validación de credenciales con IntegratedAuthService
- **Estado implementado**: ✅ FUNCIONAL

#### POST /auth/admin-login
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 242)
- **Solo para**: ADMIN, SUPERUSER, OWNER, ADMIN_SALES, etc.
- **Seguridad**: Validación de roles administrativos
- **Estado implementado**: ✅ FUNCIONAL

---

## 2. SERVICIOS DE VERIFICACIÓN

### 2.1 OTP SERVICE
- **Archivo**: `/home/admin-jairo/MeStore/app/services/otp_service.py`
- **Configuración**:
  - Longitud código: 6 dígitos
  - Validez: 10 minutos
  - Máx intentos: 5
  - Cooldown entre envíos: 60 segundos
- **Métodos principales**:
  - `generate_otp_code()`: Genera 6 dígitos aleatorios
  - `create_otp_for_user()`: Asigna OTP al usuario
  - `validate_otp_code()`: Valida y procesa resultado
  - `can_send_otp()`: Verifica cooldown
  - `cleanup_expired_otps()`: Limpia OTP expirados
- **Estado implementado**: ✅ FUNCIONAL

### 2.2 SMS SERVICE (Twilio)
- **Archivo**: `/home/admin-jairo/MeStore/app/services/sms_service.py`
- **Configuración**:
  - Proveedor: Twilio
  - Rate limit: 5 SMS/hora por número
  - Formato: E.164 internacional
  - Fallback: Modo simulación en desarrollo
- **Métodos principales**:
  - `send_otp_sms()`: Envía SMS con código OTP
  - `send_verification_code()`: Usa Twilio Verify API
  - `verify_code()`: Valida código Twilio Verify
  - `_format_international_phone()`: Formatea números
  - `_check_rate_limit()`: Verifica límites
- **Características**:
  - ✅ Soporte Colombia (+57)
  - ✅ Normalización de teléfonos locales (3XX XXX XXXX)
  - ✅ Rate limiting con Redis
  - ✅ Modo simulación para desarrollo
- **Estado implementado**: ✅ FUNCIONAL (en simulación)

### 2.3 EMAIL SERVICE (Resend)
- **Archivo**: `/home/admin-jairo/MeStore/app/services/email_service.py`
- **Proveedor**: Resend
- **Métodos de verificación**:
  - `send_otp_email()`: Envía código OTP
  - `send_verification_email()`: Envía link de verificación
  - `send_approval_email()`: Notifica aprobación
  - `send_rejection_email()`: Notifica rechazo
- **Características**:
  - ✅ Modo simulación en desarrollo
  - ✅ HTML-escaping para prevenir XSS
  - ✅ Templates atractivos
- **Estado implementado**: ✅ FUNCIONAL (en simulación)

---

## 3. FLUJO DE APROBACIÓN ADMIN

### 3.1 ENDPOINTS DE GESTIÓN DE VENDEDORES

#### GET /auth/admin/pending-sellers
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 2130)
- **Requisito**: Autenticación + ADMIN/SUPERUSER/OWNER
- **Rate limit**: 30/minuto
- **Respuesta**:
  ```json
  {
    "success": true,
    "count": 2,
    "sellers": [
      {
        "id": "uuid-here",
        "email": "vendor@example.com",
        "user_type": "VENDOR",
        "vendor_status": "draft",
        "tipo_vendedor": "persona_natural",
        "nombre_display": "Juan Pérez",
        "identificacion": "1234567890",
        "telefono": "+573001234567",
        "direccion_fiscal": "Calle 123",
        "ciudad_fiscal": "Bogotá",
        "departamento_fiscal": "Cundinamarca",
        "created_at": "2025-01-15T10:30:00Z"
      }
    ]
  }
  ```
- **Filtros automáticos**:
  - user_type = VENDOR
  - vendor_status IN [DRAFT, PENDING_DOCUMENTS, PENDING_APPROVAL]
  - Ordenado por created_at descendente
- **Estado implementado**: ✅ FUNCIONAL
- **Seguridad**: ✅ Logging de acceso administrativo

#### POST /auth/admin/approve-seller/{user_id}
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 2232)
- **Requisito**: ADMIN/SUPERUSER/OWNER
- **Rate limit**: 10/minuto
- **Acciones**:
  1. Valida que sea vendedor (user_type=VENDOR)
  2. Cambia vendor_status → APPROVED
  3. Activa cuenta (account_status=ACTIVE)
  4. Envía email de notificación
  5. Registra en audit logs
- **Respuesta**: 
  ```json
  {
    "success": true,
    "message": "Vendedor email@example.com aprobado exitosamente",
    "seller_id": "uuid-here",
    "vendor_status": "approved"
  }
  ```
- **Seguridad**:
  - ✅ Previene auto-aprobación (self-approval)
  - ✅ Validación de permisos administrativos
  - ✅ Logging de acceso
- **Estado implementado**: ✅ FUNCIONAL
- **Bugs potenciales**: 
  - BackgroundTasks puede ser None (línea 2239)

#### POST /auth/admin/reject-seller/{user_id}
- **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 2337)
- **Requisito**: ADMIN/SUPERUSER/OWNER
- **Rate limit**: 10/minuto
- **Body**: 
  ```json
  {
    "reason": "Razón detallada del rechazo (mínimo 20 caracteres)"
  }
  ```
- **Acciones**:
  1. Valida razón (mín 20 caracteres)
  2. Valida contra patrones XSS
  3. Cambia vendor_status → REJECTED
  4. Guarda rejection_reason
  5. Registra rejected_at y rejected_by_id
  6. Envía email con razón del rechazo
- **Respuesta**:
  ```json
  {
    "success": true,
    "message": "Vendedor email@example.com rechazado",
    "seller_id": "uuid-here",
    "vendor_status": "rejected",
    "rejection_reason": "Razón aquí"
  }
  ```
- **Seguridad**:
  - ✅ Validación de XSS en razón
  - ✅ Previene auto-rechazo
  - ✅ Auditoría completa
- **Estado implementado**: ✅ FUNCIONAL

---

## 4. MODELOS Y SCHEMAS

### 4.1 MODELO USER
- **Archivo**: `/home/admin-jairo/MeStore/app/models/user.py`
- **Campos clave de verificación**:
  
  | Campo | Tipo | Descripción |
  |-------|------|-------------|
  | email | String(255) | Email único |
  | password_hash | String(255) | Hash bcrypt |
  | user_type | Enum | BUYER, VENDOR, ADMIN, SUPERUSER, OWNER |
  | account_status | Enum | PENDING, ACTIVE, SUSPENDED, DELETED |
  | vendor_status | Enum | DRAFT, PENDING_DOCUMENTS, PENDING_APPROVAL, APPROVED, REJECTED |
  | email_verified | Boolean | Email verificado con OTP |
  | phone_verified | Boolean | Teléfono verificado con OTP |
  | otp_secret | String(6) | Código OTP temporal |
  | otp_expires_at | DateTime | Expiración OTP |
  | otp_attempts | Integer | Intentos fallidos |
  | otp_type | String | EMAIL o SMS |
  | email_verification_token | String(100) | Token link verificación |
  | email_verification_expires | DateTime | Expiración token email |

- **Campos de Persona Natural**:
  - cedula, nombre, apellido, telefono, direccion_fiscal, ciudad_fiscal, departamento_fiscal

- **Campos de Persona Jurídica**:
  - nit, razon_social, nombre_comercial, representante_legal, cedula_representante, email_representante, telefono_empresa

- **Campos de Rechazo**:
  - rejection_reason (Text)
  - rejected_at (DateTime)
  - rejected_by_id (Foreign Key a User)

- **Estado implementado**: ✅ COMPLETO

### 4.2 MODELO VENDOR_DOCUMENT
- **Archivo**: `/home/admin-jairo/MeStore/app/models/vendor_document.py`
- **Campos**:
  - id: UUID
  - vendor_id: FK a User
  - document_type: Enum [CEDULA, RUT, CERTIFICADO_BANCARIO, CAMARA_COMERCIO]
  - file_path: Ruta del archivo
  - original_filename: Nombre original
  - file_size: Tamaño en bytes
  - mime_type: Tipo MIME
  - status: Enum [PENDING, VERIFIED, REJECTED]
  - verified_by: FK a User (admin que verificó)
  - verification_notes: Notas de verificación
  - Timestamps: uploaded_at, verified_at, updated_at
- **Estado implementado**: ✅ MODELO DEFINIDO
- **Endpoints**: 
  - ✅ POST /vendedores/upload-document (línea 1957)
  - ✅ GET /vendedores/documents (línea 2102)

### 4.3 ENUM TYPES

**VendorStatus**:
```python
DRAFT = "draft"                      # Registro iniciado
PENDING_DOCUMENTS = "pending_documents"  # Documentos pendientes
PENDING_APPROVAL = "pending_approval"    # Pendiente aprobación admin
APPROVED = "approved"                # Aprobado y activo
REJECTED = "rejected"                # Rechazado
```

**AccountStatus**:
```python
PENDING = "pending"      # Pendiente verificación
ACTIVE = "active"        # Verificado y activo
SUSPENDED = "suspended"  # Suspendido temporalmente
DELETED = "deleted"      # Soft delete
```

**UserType**:
```python
CUSTOMER = "CUSTOMER"
BUYER = "BUYER"
VENDOR = "VENDOR"
ADMIN_MARKETING = "ADMIN_MARKETING"
ADMIN_LOGISTICS = "ADMIN_LOGISTICS"
ADMIN_SUPPORT = "ADMIN_SUPPORT"
ADMIN_SALES = "ADMIN_SALES"
ADMIN = "ADMIN"
SUPERUSER = "SUPERUSER"
OWNER = "OWNER"
SYSTEM = "SYSTEM"
```

### 4.4 SCHEMAS (PYDANTIC)

**OTPSendRequest** (línea 164 en auth.py):
```python
otp_type: str  # EMAIL o SMS
```

**OTPVerifyRequest** (línea 181):
```python
otp_code: str  # 6 dígitos
```

**MultiTypeRegistrationResponse** (línea 695):
```python
success: bool
message: str
user_id: str
email: str
user_type: str  # BUYER, VENDOR
vendor_type: Optional[str]  # persona_natural, persona_juridica
account_status: str  # pending, active, draft
vendor_status: Optional[str]
requires_approval: bool
next_steps: List[str]
```

---

## 5. FLUJO COMPLETO ESPERADO

### BUYER
1. **Registro**: POST /register
2. **Email**: Recibe link en email (24h validez)
3. **SMS**: Recibe código OTP en SMS
4. **Verifica Email**: GET /verify-email?token=...
5. **Verifica SMS**: POST /verify-phone-otp
6. **ESTADO**: account_status = ACTIVE

### VENDOR PERSONA NATURAL
1. **Registro**: POST /register-multi-type (con cedula, direccion_fiscal)
2. **Verificación**: Email + SMS (igual BUYER)
3. **Estado**: vendor_status = DRAFT
4. **Admin revisa**: GET /admin/pending-sellers
5. **Aprobación**: POST /admin/approve-seller/{id}
6. **ESTADO**: vendor_status = APPROVED, account_status = ACTIVE

### VENDOR PERSONA JURÍDICA
1. **Registro**: POST /register-multi-type (con nit, razon_social)
2. **Verificación**: Email + SMS
3. **Estado**: vendor_status = PENDING_DOCUMENTS
4. **Sube documentos**: POST /vendedores/upload-document
5. **Admin revisa**: GET /vendedores/documents
6. **Aprobación**: POST /admin/approve-seller/{id}
7. **ESTADO**: vendor_status = APPROVED, account_status = ACTIVE

---

## 6. PROBLEMAS ENCONTRADOS

### CRÍTICOS (P0)

1. **BackgroundTasks puede ser None en approve-seller**
   - **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 2239)
   - **Código**:
     ```python
     async def approve_seller(
         user_id: str,
         request: Request,
         current_user: User = Depends(get_current_user_clean),
         db: AsyncSession = Depends(get_db),
         background_tasks: BackgroundTasks = None  # ❌ PUEDE SER NONE
     ) -> dict:
         ...
         if background_tasks:  # Verifica pero puede fallar internamente
             email_service.send_approval_email(...)
     ```
   - **Impacto**: Email de aprobación no se envía si BackgroundTasks es None
   - **Solución**: Hacer BackgroundTasks requerido con `Depends()`

2. **Falta validación de rejection_reason como BodyModel**
   - **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 2341)
   - **Código**:
     ```python
     async def reject_seller(
         user_id: str,
         rejection_data: dict,  # ❌ DEBE SER PYDANTIC MODEL
         request: Request,
         ...
     ) -> dict:
     ```
   - **Impacto**: Sin validación automática, validaciones manuales pueden fallar
   - **Solución**: Crear `VendorRejectionRequest` Pydantic model

3. **Rate limiting para SMS puede no funcionar sin Redis**
   - **Archivo**: `/home/admin-jairo/MeStore/app/services/sms_service.py` (línea 84)
   - **Código**:
     ```python
     if not self.redis_service:
         return True, "Rate limiting disabled"  # ❌ SE SALTA
     ```
   - **Impacto**: Sin Redis, spam de SMS es posible
   - **Solución**: Implementar rate limiting fallback en DB

### MAYORES (P1)

4. **Falta handler para rejection_by relationship**
   - **Archivo**: `/home/admin-jairo/MeStore/app/models/user.py` (línea 805)
   - **Código**:
     ```python
     rejected_by = relationship(
         "User",
         foreign_keys=[rejected_by_id],
         remote_side=[id],
         uselist=False
     )
     ```
   - **Impacto**: Aunque definido, no se usa en endpoints
   - **Solución**: Incluir en respuesta de get_pending_sellers para auditoría

5. **Email de verificación con token no está documentado en swagger**
   - **Archivo**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` (línea 1127)
   - **Impacto**: Clientes no saben el formato esperado
   - **Solución**: Agregar documentation completa

### MENORES (P2)

6. **Falta endpoint para reenviar email de verificación**
   - **Impacto**: Usuario no puede regenerar link si expira
   - **Solución**: POST /resend-verification-email

7. **Falta endpoint para cambiar estado de documento**
   - **Impacto**: Admin no puede marcar documentos como verificados
   - **Solución**: PUT /vendedores/documents/{doc_id} para admin

8. **Falta validación de transición de estados**
   - **Impacto**: Estados pueden cambiar en orden incorrecto
   - **Solución**: Implementar state machine

---

## 7. QUÉ ESTÁ IMPLEMENTADO ✅

| Componente | Estado | Notas |
|-----------|--------|-------|
| Registro BUYER | ✅ | /register y /register-multi-type |
| Registro VENDOR Natural | ✅ | /register-multi-type con cedula |
| Registro VENDOR Jurídica | ✅ | /register-multi-type con nit |
| Verificación Email (link) | ✅ | GET /verify-email con token |
| Verificación Email (OTP) | ✅ | POST /verify-email-otp |
| Verificación SMS (OTP) | ✅ | POST /verify-phone-otp |
| Aprobación Admin | ✅ | POST /admin/approve-seller |
| Rechazo Admin | ✅ | POST /admin/reject-seller |
| Listado vendedores pendientes | ✅ | GET /admin/pending-sellers |
| Documentos de vendor | ✅ | Upload/get, pero sin validación |
| Email de aprobación | ✅ | Implementado pero background_tasks issue |
| Email de rechazo | ✅ | Implementado correctamente |
| SMS con Twilio | ✅ | En simulación en desarrollo |
| OTP service | ✅ | Generación y validación funciona |
| Rate limiting SMS | ⚠️ | Requiere Redis |
| Protección contra fuerza bruta | ✅ | En login |
| Validación XSS | ✅ | En rechazo de vendedor |
| Auditoría de acciones admin | ✅ | Logging extensivo |

---

## 8. QUÉ FALTA POR IMPLEMENTAR ❌

| Feature | Prioridad | Impacto |
|---------|-----------|---------|
| Endpoint verificación documento por admin | P1 | Alto: Admin no puede marcar docs |
| Reenvío email verificación | P1 | Alto: Link de 24h puede expirar |
| State machine para transiciones | P2 | Medio: Permite estados inválidos |
| Notificación en-tiempo-real aprobación | P3 | Bajo: WebSocket para UI actualización |
| Appeal/reconsideración de rechazo | P3 | Bajo: UX vendor después de rechazo |

---

## 9. RESUMEN DE ENDPOINTS COMPLETO

### Autenticación Pública
```
POST /auth/register
POST /auth/register-multi-type
POST /auth/login
GET  /auth/verify-email?token=...
POST /auth/send-verification-email
POST /auth/send-verification-sms
POST /auth/verify-email-otp
POST /auth/verify-phone-otp
POST /auth/refresh-token
POST /auth/logout
```

### Administración (Admin + Superuser + Owner)
```
GET  /auth/admin/pending-sellers
POST /auth/admin/approve-seller/{user_id}
POST /auth/admin/reject-seller/{user_id}
GET  /vendedores/documents
POST /vendedores/upload-document
```

### User
```
GET  /auth/me
PUT  /auth/users/me
```

---

## 10. SEGURIDAD

### Implementado ✅
- JWT con signing y expiration
- Protección contra fuerza bruta
- Rate limiting (slowapi)
- HTML-escaping en emails
- Validación XSS en rechazo
- Prevención self-approval/rejection
- Auditoría de acciones administrativas
- OTP con expiración y límite de intentos

### Recomendaciones
- Implementar CSRF protection si aplica frontend
- Validar todas las transiciones de estado
- Requiere HTTPS en producción (verbiage.config FRONTEND_URL)
- Considerar MFA para admins
- Auditar regularmente access logs

---

## 11. CONFIGURACIÓN REQUERIDA (.env)

```
# JWT
SECRET_KEY=<valor fuerte>
ALGORITHM=HS256

# Twilio SMS
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>
TWILIO_FROM_NUMBER=+57XXXXXXXXX
TWILIO_VERIFY_SERVICE_SID=<sid>
SMS_ENABLED=true
SMS_RATE_LIMIT_PER_NUMBER=5

# Resend Email
RESEND_API_KEY=<api_key>
EMAIL_FROM=onboarding@resend.dev
EMAIL_FROM_NAME=MeStocker

# URLs
FRONTEND_URL=https://app.mestore.com
DEV_FRONTEND_URL=http://localhost:5173

# Redis (para rate limiting)
REDIS_URL=redis://localhost:6379/0
```

---

## 12. DATOS DE REFERENCIA

### Estados de Transición Válidos

```
BUYER:
PENDING (account) → ACTIVE (account)

VENDOR Natural:
DRAFT → PENDING_APPROVAL → APPROVED (vendor)
       → REJECTED (vendor)

VENDOR Jurídica:
PENDING_DOCUMENTS → [espera docs] → PENDING_APPROVAL → APPROVED
                 → REJECTED
```

