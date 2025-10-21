# REFERENCIA RÁPIDA - FLUJO DE REGISTRO DE VENDEDORES

## ARCHIVOS CLAVE

| Componente | Ubicación | Líneas |
|-----------|-----------|--------|
| Endpoints | `/app/api/v1/endpoints/auth.py` | 158-2474 |
| Modelo User | `/app/models/user.py` | 1-1090 |
| Modelo VendorDocument | `/app/models/vendor_document.py` | 1-49 |
| OTP Service | `/app/services/otp_service.py` | 1-192 |
| SMS Service | `/app/services/sms_service.py` | 1-557 |
| Email Service | `/app/services/email_service.py` | 1-400+ |
| Schemas | `/app/schemas/auth.py` | 1-727 |

## ENDPOINTS MÁS UTILIZADOS

### Registro
```bash
# Registro simple (BUYER o VENDOR)
POST /auth/register
{
  "email": "user@example.com",
  "password": "Segura123!",
  "nombre": "Juan",
  "telefono": "+573001234567",
  "user_type": "VENDOR"
}

# Registro avanzado (detección automática)
POST /auth/register-multi-type
```

### Verificación
```bash
# Email por link
GET /auth/verify-email?token=XXXXXXXXX

# Email por OTP
POST /auth/verify-email-otp
{"otp_code": "123456"}

# SMS por OTP
POST /auth/verify-phone-otp
{"otp_code": "123456"}
```

### Admin
```bash
# Vendedores pendientes
GET /auth/admin/pending-sellers

# Aprobar
POST /auth/admin/approve-seller/{user_id}

# Rechazar
POST /auth/admin/reject-seller/{user_id}
{"reason": "Razón del rechazo (mín 20 caracteres)"}
```

## ESTADOS DE USUARIO

```
BUYER:
  account_status: PENDING → ACTIVE
  vendor_status: N/A

VENDOR Natural:
  vendor_status: DRAFT → APPROVED
                      ↘ REJECTED

VENDOR Jurídica:
  vendor_status: PENDING_DOCUMENTS → PENDING_APPROVAL → APPROVED
                                                    ↘ REJECTED
```

## PROBLEMAS CRÍTICOS A ARREGLAR

1. **BackgroundTasks = None** (línea 2239)
   - Email de aprobación no se envía
   - Fix: `background_tasks: BackgroundTasks = Depends()`

2. **reject-seller usa dict** (línea 2341)
   - Sin validación Pydantic
   - Fix: Crear `VendorRejectionRequest` model

3. **Rate limiting sin fallback** (línea 84 sms_service.py)
   - Sin Redis = spam posible
   - Fix: Agregar DB fallback

4. **Falta verificación de documentos** (vendedores.py)
   - Admin no puede validar docs
   - Fix: PUT `/vendedores/documents/{id}/verify`

5. **Sin state machine** (multiple endpoints)
   - Estados pueden cambiar mal
   - Fix: Implementar `VendorStatusTransition`

## DEPENDENCIAS IMPORTANTES

- **IntegratedAuthService**: Autenticación con protección fuerza bruta
- **OTPService**: Generación y validación de códigos
- **SMSService**: Envío de SMS con Twilio
- **EmailService**: Envío de emails con Resend
- **slowapi**: Rate limiting
- **Redis**: Cache y rate limiting (OPCIONAL pero recomendado)

## VARIABLES .env REQUERIDAS

```env
# JWT
SECRET_KEY=xxxxx
ALGORITHM=HS256

# Twilio
TWILIO_ACCOUNT_SID=xxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_FROM_NUMBER=+57xxxxxxxxx
TWILIO_VERIFY_SERVICE_SID=xxxxx

# Resend
RESEND_API_KEY=xxxxx

# URLs
FRONTEND_URL=https://app.mestore.com
DEV_FRONTEND_URL=http://localhost:5173

# Redis
REDIS_URL=redis://localhost:6379/0
```

## SEGURIDAD VERIFICADA

✅ JWT con expiration
✅ Protección contra fuerza bruta
✅ OTP con límite de intentos (5)
✅ OTP con expiración (10 min)
✅ Cooldown entre envíos (60 seg)
✅ Rate limiting por IP
✅ HTML-escaping en emails
✅ Validación XSS en rechazo
✅ Prevención self-approval

## PRÓXIMAS PRIORIDADES

1. Arreglar BackgroundTasks (URGENTE)
2. Crear VendorRejectionRequest (URGENTE)
3. Endpoint verificación documentos (IMPORTANTE)
4. State machine para transiciones (IMPORTANTE)
5. Rate limiting fallback (IMPORTANTE)

## DOCUMENTACIÓN COMPLETA

Ver: `/docs/VENDOR_REGISTRATION_FLOW_ANALYSIS.md` (22 KB)
Ver: `/docs/CRITICAL_ISSUES_WITH_CODE.md` (6.1 KB)

