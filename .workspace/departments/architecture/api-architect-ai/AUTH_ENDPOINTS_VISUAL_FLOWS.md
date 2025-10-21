# FLUJOS VISUALES - AUTH ENDPOINTS
## Diagramas Detallados de Autenticación MeStore

**Propósito**: Visualización clara de todos los flujos de autenticación
**Versión**: 1.0.0
**Fecha**: 2025-10-13

---

## 📊 MAPA COMPLETO DE ENDPOINTS

```
                        AUTHENTICATION API
                     /api/v1/auth/* (22 endpoints)
                               |
        ┌──────────────────────┼──────────────────────┐
        |                      |                      |
    🔐 LOGIN              📝 REGISTRO          🔐 ADMIN
    (2 endpoints)        (10 endpoints)       (3 endpoints)
        |                      |                      |
    ┌───┴───┐          ┌───────┼────────┐      ┌─────┴─────┐
    |       |          |       |        |      |           |
  login  admin-    register verify  session  pending  approve
         login              (6)     (5)     sellers  /reject
                                                     sellers
```

---

## 🎯 FLUJO COMPLETO: BUYER REGISTRATION

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO BUYER (COMPRADOR)                          │
│                        Tiempo estimado: 5 min                        │
└─────────────────────────────────────────────────────────────────────┘

    👤 USUARIO                    🖥️ FRONTEND              🔧 BACKEND
       │                              │                        │
       │ 1. Accede a landing          │                        │
       │ ──────────────────────────> │                        │
       │                              │                        │
       │ 2. Click "Registrarse"       │                        │
       │ ──────────────────────────> │                        │
       │                              │                        │
       │ 3. Selecciona "COMPRADOR"    │                        │
       │ ──────────────────────────> │                        │
       │                              │                        │
       │ 4. Llena formulario:         │                        │
       │    - Email                   │                        │
       │    - Password                │                        │
       │    - Nombre                  │                        │
       │    - Teléfono                │                        │
       │ ──────────────────────────> │                        │
       │                              │                        │
       │                              │ POST /register-multi-type
       │                              │ ────────────────────> │
       │                              │                        │
       │                              │                   [VALIDAR]
       │                              │                   ✅ Email único
       │                              │                   ✅ Phone único
       │                              │                   ✅ Password fuerte
       │                              │                        │
       │                              │                   [CREAR USER]
       │                              │                   user_type: BUYER
       │                              │                   account_status: PENDING
       │                              │                   email_verified: False
       │                              │                   phone_verified: False
       │                              │                        │
       │                              │                   [GENERAR TOKEN]
       │                              │                   email_verification_token
       │                              │                   expires: 24h
       │                              │                        │
       │                              │                   [BACKGROUND TASKS]
       │                              │                   📧 Send email link
       │                              │                   📱 Send SMS code
       │                              │                        │
       │                              │ ◀──────────────────── │
       │                              │ 201 Created            │
       │                              │ {user_id, next_steps}  │
       │                              │                        │
       │ ◀──────────────────────────┤                        │
       │ Redirigir a /verify         │                        │
       │                              │                        │
       │ 5. Recibe EMAIL con link     │                        │
       │    y SMS con código          │                        │
       │                              │                        │
       │ 6A. OPCIÓN 1: Click link email                       │
       │ ──────────────────────────────────────────────────> │
       │                              │ GET /verify-email?token=xxx
       │                              │                        │
       │                              │                   [VALIDAR TOKEN]
       │                              │                   ✅ Token válido
       │                              │                   ✅ No expirado
       │                              │                        │
       │                              │                   [UPDATE USER]
       │                              │                   email_verified: True
       │                              │                        │
       │                              │                   [BACKGROUND]
       │                              │                   📧 Welcome email
       │                              │                        │
       │ ◀──────────────────────────────────────────────────┤
       │ "Email verificado exitosamente"                      │
       │                              │                        │
       │ 6B. OPCIÓN 2: Ingresar código manualmente            │
       │    Código: 123456            │                        │
       │ ──────────────────────────> │                        │
       │                              │ POST /verify/email     │
       │                              │ {email, code: "123456"}│
       │                              │ ────────────────────> │
       │                              │                        │
       │                              │                   [VALIDAR CODE]
       │                              │                   ✅ Código correcto
       │                              │                   ✅ No expirado
       │                              │                        │
       │                              │                   [UPDATE USER]
       │                              │                   email_verified: True
       │                              │                        │
       │                              │ ◀──────────────────── │
       │                              │ {email_verified: true} │
       │                              │                        │
       │ 7. Ingresar código SMS       │                        │
       │    Código: 654321            │                        │
       │ ──────────────────────────> │                        │
       │                              │ POST /verify/phone     │
       │                              │ {phone, code: "654321"}│
       │                              │ ────────────────────> │
       │                              │                        │
       │                              │                   [TWILIO VERIFY]
       │                              │                   ✅ Verificar con Twilio
       │                              │                        │
       │                              │                   [UPDATE USER]
       │                              │                   phone_verified: True
       │                              │                        │
       │                              │                   [ACTIVAR CUENTA]
       │                              │                   ✅ email_verified: True
       │                              │                   ✅ phone_verified: True
       │                              │                   → account_status: ACTIVE
       │                              │                        │
       │                              │ ◀──────────────────── │
       │                              │ {account_active: true} │
       │                              │                        │
       │ ◀──────────────────────────┤                        │
       │ "¡Cuenta activada!"          │                        │
       │ Redirigir a /dashboard       │                        │
       │                              │                        │
       │ 8. Usuario puede:            │                        │
       │    ✅ Comprar productos      │                        │
       │    ✅ Hacer pedidos          │                        │
       │    ✅ Ver historial          │                        │
       │                              │                        │

┌─────────────────────────────────────────────────────────────────────┐
│                          ESTADO FINAL                                │
│                                                                      │
│  user_type: BUYER                                                   │
│  account_status: ACTIVE                                             │
│  email_verified: True                                               │
│  phone_verified: True                                               │
│  vendor_status: null                                                │
│                                                                      │
│  ✅ Usuario puede usar la plataforma completamente                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏢 FLUJO COMPLETO: VENDOR NATURAL REGISTRATION

```
┌─────────────────────────────────────────────────────────────────────┐
│               FLUJO VENDOR PERSONA NATURAL                          │
│                  Tiempo estimado: 10 min + aprobación admin         │
└─────────────────────────────────────────────────────────────────────┘

    👤 VENDEDOR               🖥️ FRONTEND              🔧 BACKEND            👨‍💼 ADMIN
       │                         │                        │                    │
       │ 1. Selecciona           │                        │                    │
       │    "SER VENDEDOR"       │                        │                    │
       │ ─────────────────────> │                        │                    │
       │                         │                        │                    │
       │ 2. Selecciona           │                        │                    │
       │    "PERSONA NATURAL"    │                        │                    │
       │ ─────────────────────> │                        │                    │
       │                         │                        │                    │
       │ 3. Llena formulario:    │                        │                    │
       │    📋 Cédula            │                        │                    │
       │    👤 Nombre            │                        │                    │
       │    👤 Apellido          │                        │                    │
       │    📧 Email             │                        │                    │
       │    🔐 Password          │                        │                    │
       │    📱 Teléfono          │                        │                    │
       │    🏠 Dirección fiscal  │                        │                    │
       │    🌆 Ciudad            │                        │                    │
       │    📍 Departamento      │                        │                    │
       │ ─────────────────────> │                        │                    │
       │                         │ POST /register-multi-type                  │
       │                         │ ─────────────────────> │                    │
       │                         │                        │                    │
       │                         │                   [DETECTAR TIPO]           │
       │                         │                   ✅ cedula presente        │
       │                         │                   → VENDOR Natural          │
       │                         │                        │                    │
       │                         │                   [CREAR USER]              │
       │                         │                   user_type: VENDOR         │
       │                         │                   tipo_vendedor: "persona_natural"
       │                         │                   account_status: PENDING   │
       │                         │                   vendor_status: DRAFT      │
       │                         │                        │                    │
       │                         │ ◀───────────────────── │                    │
       │                         │ 201 Created            │                    │
       │                         │ {                      │                    │
       │                         │   user_id,             │                    │
       │                         │   vendor_status: "DRAFT"                    │
       │                         │   next_steps: [        │                    │
       │                         │     "verify_email",    │                    │
       │                         │     "verify_phone",    │                    │
       │                         │     "wait_admin_approval"                   │
       │                         │   ]                    │                    │
       │                         │ }                      │                    │
       │                         │                        │                    │
       │ ◀───────────────────── │                        │                    │
       │ Redirigir a /verify     │                        │                    │
       │                         │                        │                    │
       │ 4. Verificar Email      │                        │                    │
       │    (igual que BUYER)    │ POST /verify/email     │                    │
       │ ───────────────────────────────────────────────> │                    │
       │                         │                        │                    │
       │                         │                   [UPDATE]                  │
       │                         │                   email_verified: True      │
       │                         │                   vendor_status: DRAFT (sin cambio)
       │                         │                        │                    │
       │ 5. Verificar Teléfono   │                        │                    │
       │    (igual que BUYER)    │ POST /verify/phone     │                    │
       │ ───────────────────────────────────────────────> │                    │
       │                         │                        │                    │
       │                         │                   [UPDATE]                  │
       │                         │                   phone_verified: True      │
       │                         │                   vendor_status: PENDING_APPROVAL
       │                         │                        │                    │
       │                         │ ◀───────────────────── │                    │
       │                         │ {message: "Cuenta verificada.              │
       │                         │   Esperando aprobación admin"}             │
       │                         │                        │                    │
       │ ◀───────────────────── │                        │                    │
       │ Redirigir a             │                        │                    │
       │ /registration-pending   │                        │                    │
       │                         │                        │                    │
       │ ⏳ ESPERA...            │                        │                    │
       │                         │                        │                    │
       │                         │                        │    6. Admin accede │
       │                         │                        │       al portal    │
       │                         │                        │    ──────────────> │
       │                         │                        │                    │
       │                         │                        │    POST /admin-login
       │                         │                        │ ◀─────────────────┤
       │                         │                        │ {access_token}     │
       │                         │                        │ ─────────────────> │
       │                         │                        │                    │
       │                         │                        │    7. Ver pendientes
       │                         │                        │    GET /admin/pending-sellers
       │                         │                        │ ◀─────────────────┤
       │                         │                        │                    │
       │                         │                   [QUERY DB]                │
       │                         │                   ✅ user_type=VENDOR       │
       │                         │                   ✅ vendor_status IN       │
       │                         │                      [DRAFT, PENDING_APPROVAL]
       │                         │                        │                    │
       │                         │                        │ ─────────────────> │
       │                         │                        │ {                  │
       │                         │                        │   count: 1,        │
       │                         │                        │   sellers: [{      │
       │                         │                        │     id, email,     │
       │                         │                        │     cedula,        │
       │                         │                        │     nombre,        │
       │                         │                        │     apellido,      │
       │                         │                        │     direccion...   │
       │                         │                        │   }]               │
       │                         │                        │ }                  │
       │                         │                        │                    │
       │                         │                        │    8A. APROBAR     │
       │                         │                        │    POST /admin/approve-seller/{id}
       │                         │                        │ ◀─────────────────┤
       │                         │                        │                    │
       │                         │                   [VALIDAR]                 │
       │                         │                   ✅ Admin privilegios      │
       │                         │                   ✅ No self-approval       │
       │                         │                   ✅ Usuario es VENDOR      │
       │                         │                        │                    │
       │                         │                   [UPDATE]                  │
       │                         │                   vendor_status: APPROVED   │
       │                         │                   account_status: ACTIVE    │
       │                         │                        │                    │
       │                         │                   [BACKGROUND]              │
       │                         │                   📧 Email aprobación       │
       │                         │                        │                    │
       │                         │                        │ ─────────────────> │
       │                         │                        │ {success: true}    │
       │                         │                        │                    │
       │ 📧 Recibe email:        │                        │                    │
       │    "¡Fuiste aprobado!"  │                        │                    │
       │                         │                        │                    │
       │ 9. Login como vendedor  │                        │                    │
       │ ─────────────────────> │ POST /login            │                    │
       │                         │ ─────────────────────> │                    │
       │                         │ ◀───────────────────── │                    │
       │                         │ {access_token}         │                    │
       │ ◀───────────────────── │                        │                    │
       │                         │                        │                    │
       │ 10. Usuario puede:      │                        │                    │
       │     ✅ Crear productos  │                        │                    │
       │     ✅ Gestionar stock  │                        │                    │
       │     ✅ Ver pedidos      │                        │                    │
       │     ✅ Recibir pagos    │                        │                    │
       │                         │                        │                    │

┌─────────────────────────────────────────────────────────────────────┐
│                          ESTADO FINAL                                │
│                                                                      │
│  user_type: VENDOR                                                  │
│  tipo_vendedor: "persona_natural"                                   │
│  account_status: ACTIVE                                             │
│  vendor_status: APPROVED                                            │
│  email_verified: True                                               │
│  phone_verified: True                                               │
│                                                                      │
│  ✅ Vendedor puede vender en la plataforma                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏢 FLUJO ADMIN: GESTIÓN DE VENDEDORES

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO ADMINISTRATIVO                              │
│                 Gestión de Vendedores Pendientes                     │
└─────────────────────────────────────────────────────────────────────┘

    👨‍💼 ADMIN                  🖥️ ADMIN PORTAL         🔧 BACKEND
       │                            │                        │
       │ 1. Accede a landing        │                        │
       │ ─────────────────────────> │                        │
       │                            │                        │
       │ 2. Click "Portal Admin"    │                        │
       │    (footer link)           │                        │
       │ ─────────────────────────> │                        │
       │                            │                        │
       │    Redirigir a /admin-portal                        │
       │                            │                        │
       │ 3. Click "Acceder"         │                        │
       │ ─────────────────────────> │                        │
       │                            │                        │
       │    Redirigir a /admin-login                         │
       │                            │                        │
       │ 4. Ingresar credenciales:  │                        │
       │    📧 admin@mestocker.com  │                        │
       │    🔐 Admin123456          │                        │
       │ ─────────────────────────> │                        │
       │                            │ POST /admin-login      │
       │                            │ ─────────────────────> │
       │                            │                        │
       │                            │                   [VALIDAR]
       │                            │                   ✅ Credenciales OK
       │                            │                   ✅ user_type IN
       │                            │                      [ADMIN, SUPERUSER]
       │                            │                        │
       │                            │                   [GENERAR TOKENS]
       │                            │                   access_token (1h)
       │                            │                   refresh_token (7d)
       │                            │                        │
       │                            │                   [SECURITY LOG]
       │                            │                   📝 Admin login:
       │                            │                      - admin_id
       │                            │                      - IP address
       │                            │                      - timestamp
       │                            │                        │
       │                            │ ◀───────────────────── │
       │                            │ 200 OK                 │
       │                            │ {access_token, user}   │
       │                            │                        │
       │ ◀───────────────────────── │                        │
       │ Redirigir a                │                        │
       │ /admin-secure-portal/      │                        │
       │ vendors                    │                        │
       │                            │                        │
       │ 5. Ver vendedores          │                        │
       │    pendientes              │                        │
       │ ─────────────────────────> │                        │
       │                            │ GET /admin/pending-sellers
       │                            │ Authorization: Bearer <token>
       │                            │ ─────────────────────> │
       │                            │                        │
       │                            │                   [RATE LIMIT]
       │                            │                   ✅ 30/min OK     │
       │                            │                        │
       │                            │                   [VERIFICAR PERMISOS]
       │                            │                   ✅ ADMIN role     │
       │                            │                        │
       │                            │                   [QUERY DB]
       │                            │                   SELECT * FROM users
       │                            │                   WHERE user_type='VENDOR'
       │                            │                   AND vendor_status IN
       │                            │                   ('DRAFT',
       │                            │                    'PENDING_DOCUMENTS',
       │                            │                    'PENDING_APPROVAL')
       │                            │                   ORDER BY created_at DESC
       │                            │                        │
       │                            │                   [SERIALIZAR]
       │                            │                   Para cada vendedor:
       │                            │                   - id, email, tipo
       │                            │                   - identificación
       │                            │                   - datos fiscales
       │                            │                   - created_at
       │                            │                        │
       │                            │ ◀───────────────────── │
       │                            │ 200 OK                 │
       │                            │ {                      │
       │                            │   count: 3,            │
       │                            │   sellers: [           │
       │                            │     {                  │
       │                            │       id: "uuid-1",    │
       │                            │       email: "vendor1@...",
       │                            │       tipo_vendedor: "persona_natural",
       │                            │       cedula: "123...", │
       │                            │       ...              │
       │                            │     },                 │
       │                            │     {...},             │
       │                            │     {...}              │
       │                            │   ]                    │
       │                            │ }                      │
       │                            │                        │
       │ ◀───────────────────────── │                        │
       │ Mostrar tabla con          │                        │
       │ vendedores pendientes      │                        │
       │                            │                        │
       │ 6A. DECISIÓN: APROBAR      │                        │
       │     Click "Aprobar"        │                        │
       │     Vendedor ID: uuid-1    │                        │
       │ ─────────────────────────> │                        │
       │                            │ POST /admin/approve-seller/uuid-1
       │                            │ Authorization: Bearer <token>
       │                            │ ─────────────────────> │
       │                            │                        │
       │                            │                   [RATE LIMIT]
       │                            │                   ✅ 10/min OK     │
       │                            │                        │
       │                            │                   [SECURITY CHECKS]
       │                            │                   ✅ Admin permisos │
       │                            │                   ✅ Vendedor existe│
       │                            │                   ✅ Es VENDOR      │
       │                            │                   ✅ No self-approval
       │                            │                      (admin != seller)
       │                            │                        │
       │                            │                   [UPDATE USER]
       │                            │                   vendor_status = APPROVED
       │                            │                   account_status = ACTIVE
       │                            │                        │
       │                            │                   [BACKGROUND TASK]
       │                            │                   📧 Send approval email
       │                            │                      to vendor1@...
       │                            │                        │
       │                            │                   [AUDIT LOG]
       │                            │                   📝 Approval logged:
       │                            │                      - seller_id
       │                            │                      - admin_id
       │                            │                      - timestamp
       │                            │                      - IP address
       │                            │                        │
       │                            │ ◀───────────────────── │
       │                            │ 200 OK                 │
       │                            │ {                      │
       │                            │   success: true,       │
       │                            │   message: "Vendedor aprobado",
       │                            │   vendor_status: "APPROVED"
       │                            │ }                      │
       │                            │                        │
       │ ◀───────────────────────── │                        │
       │ Mostrar notificación:      │                        │
       │ "✅ Vendedor aprobado"     │                        │
       │ Actualizar lista           │                        │
       │ (remover de pendientes)    │                        │
       │                            │                        │
       │ 6B. DECISIÓN: RECHAZAR     │                        │
       │     Click "Rechazar"       │                        │
       │     Vendedor ID: uuid-2    │                        │
       │ ─────────────────────────> │                        │
       │                            │                        │
       │    Mostrar modal:          │                        │
       │    "Razón del rechazo"     │                        │
       │                            │                        │
       │ 7. Escribir razón:         │                        │
       │    "Documentos inválidos"  │                        │
       │ ─────────────────────────> │                        │
       │                            │                        │
       │                            │ POST /admin/reject-seller/uuid-2
       │                            │ Authorization: Bearer <token>
       │                            │ Body: {                │
       │                            │   reason: "Documentos inválidos"
       │                            │ }                      │
       │                            │ ─────────────────────> │
       │                            │                        │
       │                            │                   [VALIDAR REASON]
       │                            │                   ✅ >= 20 chars    │
       │                            │                   ✅ No XSS patterns│
       │                            │                      (<script, etc.)│
       │                            │                        │
       │                            │                   [SECURITY CHECKS]
       │                            │                   ✅ Admin permisos │
       │                            │                   ✅ No self-rejection
       │                            │                        │
       │                            │                   [UPDATE USER]
       │                            │                   vendor_status = REJECTED
       │                            │                   rejection_reason = "..."
       │                            │                   rejected_at = now()
       │                            │                   rejected_by_id = admin.id
       │                            │                        │
       │                            │                   [BACKGROUND TASK]
       │                            │                   📧 Send rejection email
       │                            │                      with reason
       │                            │                        │
       │                            │                   [AUDIT LOG]
       │                            │                   📝 Rejection logged
       │                            │                        │
       │                            │ ◀───────────────────── │
       │                            │ 200 OK                 │
       │                            │ {                      │
       │                            │   success: true,       │
       │                            │   vendor_status: "REJECTED"
       │                            │ }                      │
       │                            │                        │
       │ ◀───────────────────────── │                        │
       │ Mostrar notificación:      │                        │
       │ "✅ Vendedor rechazado"    │                        │
       │ Actualizar lista           │                        │
       │                            │                        │

┌─────────────────────────────────────────────────────────────────────┐
│                      AUDITORÍA COMPLETA                              │
│                                                                      │
│  Todos los eventos administrativos quedan registrados:              │
│  - Login admin (IP, timestamp)                                      │
│  - Acceso a pending-sellers (admin_id, IP)                          │
│  - Aprobaciones (admin_id, seller_id, timestamp)                    │
│  - Rechazos (admin_id, seller_id, reason, timestamp)                │
│                                                                      │
│  🔐 Protecciones activas:                                            │
│  - Rate limiting (30/min list, 10/min approve/reject)               │
│  - Self-approval/rejection bloqueado                                 │
│  - XSS protection en rejection_reason                                │
│  - Role-based access control                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUJO: TOKEN REFRESH Y LOGOUT

```
┌─────────────────────────────────────────────────────────────────────┐
│                   GESTIÓN DE SESIÓN Y TOKENS                         │
└─────────────────────────────────────────────────────────────────────┘

    👤 USUARIO              🖥️ FRONTEND              🔧 BACKEND
       │                        │                        │
       │                        │                        │
    CASO 1: ACCESS TOKEN EXPIRADO
       │                        │                        │
       │ API Request            │                        │
       │ ───────────────────> │ GET /some-endpoint     │
       │                        │ Authorization: Bearer <expired_token>
       │                        │ ─────────────────────> │
       │                        │                        │
       │                        │                   [VALIDATE TOKEN]
       │                        │                   ❌ Token expirado
       │                        │                        │
       │                        │ ◀───────────────────── │
       │                        │ 401 Unauthorized       │
       │                        │ {detail: "Token expired"}
       │                        │                        │
       │                        │ [INTERCEPTOR AXIOS]    │
       │                        │ Detecta 401            │
       │                        │                        │
       │                        │ POST /refresh-token    │
       │                        │ {refresh_token: "xyz..."}
       │                        │ ─────────────────────> │
       │                        │                        │
       │                        │                   [VALIDATE REFRESH]
       │                        │                   ✅ Refresh válido  │
       │                        │                   ✅ No expirado (7d)│
       │                        │                   ✅ Usuario existe  │
       │                        │                        │
       │                        │                   [GENERATE NEW TOKENS]
       │                        │                   access_token (1h)  │
       │                        │                   refresh_token (7d) │
       │                        │                        │
       │                        │                   [TOKEN ROTATION]
       │                        │                   🔄 Invalidar refresh viejo
       │                        │                      Generar refresh nuevo
       │                        │                        │
       │                        │ ◀───────────────────── │
       │                        │ 200 OK                 │
       │                        │ {                      │
       │                        │   access_token: "new...",
       │                        │   refresh_token: "new..."
       │                        │ }                      │
       │                        │                        │
       │                        │ [GUARDAR EN STORAGE]   │
       │                        │ localStorage.setItem() │
       │                        │                        │
       │                        │ [REINTENTAR REQUEST]   │
       │                        │ GET /some-endpoint     │
       │                        │ Authorization: Bearer <new_token>
       │                        │ ─────────────────────> │
       │                        │                        │
       │                        │                   ✅ Token válido    │
       │                        │                        │
       │                        │ ◀───────────────────── │
       │                        │ 200 OK                 │
       │                        │ {data: ...}            │
       │                        │                        │
       │ ◀─────────────────── │                        │
       │ Respuesta OK           │                        │
       │                        │                        │
       │                        │                        │
    CASO 2: LOGOUT MANUAL
       │                        │                        │
       │ Click "Cerrar Sesión"  │                        │
       │ ───────────────────> │                        │
       │                        │ POST /logout           │
       │                        │ Authorization: Bearer <token>
       │                        │ {refresh_token: "xyz..."}
       │                        │ ─────────────────────> │
       │                        │                        │
       │                        │                   [INVALIDATE TOKENS]
       │                        │                   🗑️ Add access_token to
       │                        │                      Redis blacklist
       │                        │                   🗑️ Add refresh_token to
       │                        │                      Redis blacklist
       │                        │                        │
       │                        │                   [CLEAN SESSION]
       │                        │                   Redis session cleared
       │                        │                        │
       │                        │ ◀───────────────────── │
       │                        │ 200 OK                 │
       │                        │ {                      │
       │                        │   success: true,       │
       │                        │   message: "Sesión cerrada"
       │                        │ }                      │
       │                        │                        │
       │                        │ [CLEAR FRONTEND]       │
       │                        │ localStorage.clear()   │
       │                        │ navigate('/login')     │
       │                        │                        │
       │ ◀─────────────────── │                        │
       │ Redirigir a login      │                        │
       │                        │                        │

┌─────────────────────────────────────────────────────────────────────┐
│                      TOKEN LIFECYCLE                                 │
│                                                                      │
│  Access Token:                                                       │
│  - Expiry: 1 hora                                                    │
│  - Uso: Headers Authorization en cada request                       │
│  - Refresh: Automático con refresh_token                            │
│                                                                      │
│  Refresh Token:                                                      │
│  - Expiry: 7 días                                                    │
│  - Uso: Solo para renovar access_token                              │
│  - Rotation: Se genera nuevo en cada refresh                        │
│  - Invalidación: En logout, se agrega a blacklist Redis             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 PROTECCIONES DE SEGURIDAD

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CAPAS DE SEGURIDAD IMPLEMENTADAS                   │
└─────────────────────────────────────────────────────────────────────┘

CAPA 1: RATE LIMITING
  ┌────────────────────────────────────────────────┐
  │ Slowapi (Admin endpoints)                      │
  │ - /admin/pending-sellers: 30/min por IP       │
  │ - /admin/approve-seller: 10/min por IP        │
  │ - /admin/reject-seller: 10/min por IP         │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ Redis Custom (SMS público)                     │
  │ - Por IP: 3 SMS/hora                           │
  │ - Por teléfono: 2 SMS/hora                     │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ IntegratedAuthService (Login)                  │
  │ - Brute force: 5 intentos por email+IP        │
  │ - Bloqueo temporal después de exceder          │
  └────────────────────────────────────────────────┘

CAPA 2: VALIDACIÓN DE ENTRADA
  ┌────────────────────────────────────────────────┐
  │ Phone E.164 Format                             │
  │ ✅ +573001234567 (Correcto)                    │
  │ ❌ 3001234567 (Incorrecto)                     │
  │ ❌ 300-123-4567 (Incorrecto)                   │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ XSS Protection (Rejection Reason)              │
  │ ❌ Bloqueados: <script, javascript:,           │
  │    onerror=, onload=, onclick=, <iframe        │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ Password Strength                              │
  │ - Mínimo 8 caracteres                          │
  │ - Al menos 1 mayúscula                         │
  │ - Al menos 1 número                            │
  └────────────────────────────────────────────────┘

CAPA 3: AUTORIZACIÓN Y ROLES
  ┌────────────────────────────────────────────────┐
  │ Admin Endpoints                                │
  │ Requieren user_type IN:                        │
  │ - ADMIN                                        │
  │ - SUPERUSER                                    │
  │ - OWNER                                        │
  │ - ADMIN_SALES (approve/reject)                 │
  │ - ADMIN_SUPPORT (read-only pending)            │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ Self-Action Prevention                         │
  │ ❌ Admin NO puede aprobar/rechazar su propia   │
  │    cuenta de vendedor                          │
  │ Validación: seller.id != current_user.id       │
  └────────────────────────────────────────────────┘

CAPA 4: AUDITORÍA Y LOGGING
  ┌────────────────────────────────────────────────┐
  │ Security Events Logged                         │
  │ - Login attempts (success/fail)                │
  │ - Admin access (endpoint, admin_id, IP)        │
  │ - Seller approvals (admin_id, seller_id)       │
  │ - Seller rejections (admin_id, reason)         │
  │ - SMS sends (phone, IP, status)                │
  │ - Rate limit hits                              │
  │ - XSS attempts blocked                         │
  │ - Self-approval attempts blocked               │
  └────────────────────────────────────────────────┘

CAPA 5: TOKEN SECURITY
  ┌────────────────────────────────────────────────┐
  │ JWT Configuration                              │
  │ - Algorithm: HS256                             │
  │ - Access expiry: 1 hora                        │
  │ - Refresh expiry: 7 días                       │
  │ - Token rotation on refresh                    │
  │ - Blacklist on logout (Redis)                  │
  └────────────────────────────────────────────────┘
  ┌────────────────────────────────────────────────┐
  │ Session Management                             │
  │ - Redis para tracking de sesiones              │
  │ - IP y User-Agent guardados                    │
  │ - Invalidación automática en logout            │
  └────────────────────────────────────────────────┘
```

---

## 📊 MATRIZ DE DECISIÓN: TIPO DE USUARIO

```
┌─────────────────────────────────────────────────────────────────────┐
│              AUTO-DETECCIÓN DE TIPO EN /register-multi-type         │
└─────────────────────────────────────────────────────────────────────┘

Input Fields Present          →  Tipo Detectado  →  Estados Iniciales
═══════════════════════════════════════════════════════════════════════

email, password,              →  BUYER           →  user_type: BUYER
nombre, telefono                                    account_status: PENDING
(sin cedula, sin nit)                               vendor_status: null
                                                    next_steps:
                                                    - verify_email
                                                    - verify_phone

───────────────────────────────────────────────────────────────────────

email, password,              →  VENDOR           →  user_type: VENDOR
cedula, nombre, apellido,        Persona Natural     tipo_vendedor: "persona_natural"
telefono, direccion_fiscal,                          account_status: PENDING
ciudad_fiscal,                                       vendor_status: DRAFT
departamento_fiscal                                  next_steps:
                                                     - verify_email
                                                     - verify_phone
                                                     - wait_admin_approval

───────────────────────────────────────────────────────────────────────

email, password,              →  VENDOR           →  user_type: VENDOR
nit, razon_social,               Persona Jurídica    tipo_vendedor: "persona_juridica"
representante_legal,                                 account_status: PENDING
email_representante,                                 vendor_status: PENDING_DOCUMENTS
telefono_empresa,                                    next_steps:
direccion_fiscal,                                    - verify_email
ciudad_fiscal,                                       - verify_phone
departamento_fiscal                                  - upload_documents
                                                     - wait_admin_approval

═══════════════════════════════════════════════════════════════════════

Lógica de Detección (Código):
  if 'nit' in data and data.nit:
      → VENDOR Persona Jurídica
  elif 'cedula' in data and data.cedula and 'direccion_fiscal' in data:
      → VENDOR Persona Natural
  else:
      → BUYER
```

---

## 📈 ESTADOS DE CUENTA Y TRANSICIONES

```
┌─────────────────────────────────────────────────────────────────────┐
│                  DIAGRAMA DE ESTADOS: BUYER                          │
└─────────────────────────────────────────────────────────────────────┘

    [REGISTRO]
        ↓
   ╔═══════════╗
   ║  PENDING  ║  ← Estado inicial
   ╚═══════════╝
   email_verified: False
   phone_verified: False
        ↓
        ↓ Verificar email
        ↓
   ╔═══════════╗
   ║  PENDING  ║  ← Email verificado
   ╚═══════════╝
   email_verified: True
   phone_verified: False
        ↓
        ↓ Verificar teléfono
        ↓
   ╔═══════════╗
   ║  ACTIVE   ║  ← ✅ Cuenta activa
   ╚═══════════╝
   email_verified: True
   phone_verified: True
        ↓
        ↓ Usuario puede comprar


┌─────────────────────────────────────────────────────────────────────┐
│              DIAGRAMA DE ESTADOS: VENDOR NATURAL                     │
└─────────────────────────────────────────────────────────────────────┘

    [REGISTRO]
        ↓
   ╔═══════════╗
   ║   DRAFT   ║  ← Estado inicial vendor
   ╚═══════════╝
   account_status: PENDING
   vendor_status: DRAFT
   email_verified: False
   phone_verified: False
        ↓
        ↓ Verificar email + teléfono
        ↓
   ╔═══════════════════╗
   ║ PENDING_APPROVAL  ║  ← Esperando admin
   ╚═══════════════════╝
   account_status: PENDING
   vendor_status: PENDING_APPROVAL
   email_verified: True
   phone_verified: True
        ↓
        ├────────┬────────┐
        ↓        ↓        ↓
   ╔═══════╗  ╔═════════╗
   ║APPROVED║  ║REJECTED ║
   ╚═══════╝  ╚═════════╝
   account:    account:
   ACTIVE      PENDING
   vendor:     vendor:
   APPROVED    REJECTED
   ↓           ↓
   ✅ Puede    ❌ No puede
   vender      vender


┌─────────────────────────────────────────────────────────────────────┐
│              DIAGRAMA DE ESTADOS: VENDOR JURÍDICA                    │
└─────────────────────────────────────────────────────────────────────┘

    [REGISTRO]
        ↓
   ╔═══════════════════╗
   ║PENDING_DOCUMENTS  ║  ← Estado inicial empresa
   ╚═══════════════════╝
   account_status: PENDING
   vendor_status: PENDING_DOCUMENTS
   email_verified: False
   phone_verified: False
        ↓
        ↓ Verificar email + teléfono
        ↓
   ╔═══════════════════╗
   ║PENDING_DOCUMENTS  ║  ← Esperando documentos
   ╚═══════════════════╝
   email_verified: True
   phone_verified: True
        ↓
        ↓ (Futuro) Subir documentos
        ↓
   ╔═══════════════════╗
   ║ PENDING_APPROVAL  ║  ← Esperando admin review
   ╚═══════════════════╝
   Documentos subidos
        ↓
        ├────────┬────────┐
        ↓        ↓        ↓
   ╔═══════╗  ╔═════════╗
   ║APPROVED║  ║REJECTED ║
   ╚═══════╝  ╚═════════╝
   account:    account:
   ACTIVE      PENDING
   vendor:     vendor:
   APPROVED    REJECTED
   ↓           ↓
   ✅ Empresa  ❌ Empresa
   puede       no puede
   vender      vender
```

---

**Fin de Flujos Visuales**

**Documentos Relacionados**:
- AUTH_ENDPOINTS_AUDIT_REPORT.md (Reporte completo)
- AUTH_ENDPOINTS_QUICK_REFERENCE.md (Guía rápida)

**Generado por**: api-architect-ai
**Fecha**: 2025-10-13
**Workspace Protocol**: ✅ FOLLOWED
