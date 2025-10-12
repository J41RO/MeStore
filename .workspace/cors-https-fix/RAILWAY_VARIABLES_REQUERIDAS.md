# 📋 VARIABLES REQUERIDAS PARA RAILWAY - RESEND & TWILIO

**Fecha**: 2025-10-09 21:45 UTC
**Análisis por**: @backend-framework-ai @third-party-integration-ai
**Status**: ✅ ANÁLISIS COMPLETADO

---

## 🎯 RESUMEN EJECUTIVO

**Variables Críticas Identificadas**: 10 variables
**Servicios Afectados**: Email (Resend) y SMS (Twilio)
**Obligatorias para Producción**: 4 variables CRÍTICAS
**Opcionales pero Recomendadas**: 6 variables

---

## 📧 VARIABLES RESEND (EMAIL SERVICE)

### ✅ VARIABLES REQUERIDAS (CRÍTICAS)

#### 1. `RESEND_API_KEY`
```bash
Tipo: str
Required: ✅ SÍ (CRÍTICA)
Default: None (sin default)
Descripción: API Key de Resend para envío de emails

Ubicación en código:
- app/services/email_service.py:52
- Usado en: EmailService.__init__()

Consecuencia si falta:
❌ Email service corre en modo SIMULACIÓN
❌ NO se enviarán emails reales
❌ Password reset NO funcionará en producción
❌ OTP por email NO funcionará
```

**Cómo obtenerla:**
```
1. Ir a: https://resend.com/api-keys
2. Crear nueva API Key
3. Copiar key que comienza con: re_...
4. Configurar en Railway
```

**Ejemplo valor:**
```bash
RESEND_API_KEY=re_123abc456def789ghi012jkl345mno678
```

---

#### 2. `EMAIL_FROM`
```bash
Tipo: str
Required: ⚠️ RECOMENDADA
Default: "onboarding@resend.dev"
Descripción: Email remitente para emails salientes

Ubicación en código:
- app/services/email_service.py:53

Valor recomendado:
EMAIL_FROM=noreply@mestocker.com

Consecuencia si falta:
⚠️ Usará default de Resend (onboarding@resend.dev)
⚠️ Emails podrían verse como spam
```

**Cómo configurarla:**
```
1. Verificar dominio en Resend Dashboard
2. Agregar DNS records (SPF, DKIM, DMARC)
3. Usar email verificado
```

---

#### 3. `EMAIL_FROM_NAME`
```bash
Tipo: str
Required: ⚠️ RECOMENDADA
Default: "MeStocker"
Descripción: Nombre visible del remitente

Ubicación en código:
- app/services/email_service.py:54

Valor recomendado:
EMAIL_FROM_NAME=MeStocker

Consecuencia si falta:
✅ Usará default "MeStocker" (OK)
```

---

## 📱 VARIABLES TWILIO (SMS SERVICE)

### ✅ VARIABLES REQUERIDAS (CRÍTICAS)

#### 4. `TWILIO_ACCOUNT_SID`
```bash
Tipo: str
Required: ✅ SÍ (CRÍTICA)
Default: "" (string vacío)
Descripción: Twilio Account SID para autenticación

Ubicación en código:
- app/core/config.py:113-115
- app/services/sms_service.py:40

Consecuencia si falta:
❌ SMS service corre en modo SIMULACIÓN
❌ NO se enviarán SMS reales
❌ OTP por SMS NO funcionará
❌ Notificaciones móviles NO funcionarán
```

**Cómo obtenerla:**
```
1. Ir a: https://console.twilio.com/
2. Dashboard → Account Info
3. Copiar Account SID (comienza con AC...)
4. Configurar en Railway
```

**Ejemplo valor:**
```bash
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
```

---

#### 5. `TWILIO_AUTH_TOKEN`
```bash
Tipo: str
Required: ✅ SÍ (CRÍTICA)
Default: "" (string vacío)
Descripción: Twilio Authentication Token (SECRETO)

Ubicación en código:
- app/core/config.py:116-118
- app/services/sms_service.py:41

⚠️ SEGURIDAD: Token secreto - NUNCA compartir

Consecuencia si falta:
❌ SMS service NO funcionará
❌ Autenticación con Twilio fallará
```

**Cómo obtenerla:**
```
1. Twilio Console → Account Info
2. Auth Token (hacer clic en "Show" si está oculto)
3. Copiar token completo
4. Configurar en Railway como variable de entorno
```

**Ejemplo valor:**
```bash
TWILIO_AUTH_TOKEN=abcdef1234567890abcdef1234567890
```

---

#### 6. `TWILIO_FROM_NUMBER`
```bash
Tipo: str
Required: ✅ SÍ (CRÍTICA)
Default: "" (string vacío)
Descripción: Número Twilio para enviar SMS

Ubicación en código:
- app/core/config.py:119-121
- app/services/sms_service.py:42

Formato: +[código país][número]
Ejemplo Colombia: +573001234567
Ejemplo USA: +17379771943

Consecuencia si falta:
❌ No se pueden enviar SMS
❌ API Twilio rechazará requests
```

**Cómo obtenerla:**
```
1. Twilio Console → Phone Numbers
2. Comprar número o usar trial number
3. Copiar número en formato E.164 (+1XXXXXXXXXX)
4. Configurar en Railway
```

**Ejemplo valor:**
```bash
TWILIO_FROM_NUMBER=+17379771943
```

---

#### 7. `TWILIO_VERIFY_SERVICE_SID`
```bash
Tipo: str
Required: ⚠️ RECOMENDADA (para verificación avanzada)
Default: "" (string vacío)
Descripción: Twilio Verify Service SID para OTP mejorado

Ubicación en código:
- app/core/config.py:122-124
- app/services/sms_service.py:43, 616, 707

Usado en:
- send_verification_code() - Línea 569
- verify_code() - Línea 653

Consecuencia si falta:
⚠️ Verificación avanzada NO disponible
✅ OTP básico sigue funcionando con send_otp_sms()
```

**Cómo obtenerla:**
```
1. Twilio Console → Verify → Services
2. Create new Verify Service
3. Copiar Service SID (comienza con VA...)
4. Configurar en Railway
```

**Ejemplo valor:**
```bash
TWILIO_VERIFY_SERVICE_SID=VA1234567890abcdef1234567890abcdef
```

---

## 🔧 VARIABLES OPCIONALES (CONFIGURACIÓN)

### Email Opcional (SendGrid Legacy - NO USAR)

⚠️ **NOTA**: El código usa RESEND, NO SendGrid. Estas variables están en config.py pero NO se usan:

```bash
# ❌ NO CONFIGURAR - LEGACY CODE
SENDGRID_API_KEY  # Línea 273 - NO usado por email_service.py
FROM_EMAIL        # Línea 277 - NO usado (usa EMAIL_FROM en su lugar)
FROM_NAME         # Línea 281 - NO usado (usa EMAIL_FROM_NAME en su lugar)
```

### Frontend URLs (Opcional)

```bash
FRONTEND_URL=https://www.mestocker.com
# Usado en: app/services/email_service.py:42 (templates de email)

DEV_FRONTEND_URL=http://192.168.1.137:5173
# Usado en: app/services/email_service.py:43 (desarrollo)
```

### SMS Rate Limiting (Opcional)

```bash
SMS_RATE_LIMIT_PER_NUMBER=5
# Default: 5 SMS por hora por número
# Ubicación: app/services/sms_service.py:46

SMS_RATE_LIMIT_WINDOW=3600
# Default: 3600 segundos (1 hora)
# Ubicación: app/services/sms_service.py:47
```

---

## 📊 TABLA RESUMEN - VARIABLES CRÍTICAS

| Variable | Servicio | Required | Default | Producción |
|----------|----------|----------|---------|------------|
| **RESEND_API_KEY** | Email | ✅ CRÍTICA | None | ✅ OBLIGATORIA |
| **EMAIL_FROM** | Email | ⚠️ Recomendada | onboarding@resend.dev | ✅ Configurar |
| **EMAIL_FROM_NAME** | Email | ⚠️ Recomendada | MeStocker | ✅ OK (usar default) |
| **TWILIO_ACCOUNT_SID** | SMS | ✅ CRÍTICA | "" | ✅ OBLIGATORIA |
| **TWILIO_AUTH_TOKEN** | SMS | ✅ CRÍTICA | "" | ✅ OBLIGATORIA |
| **TWILIO_FROM_NUMBER** | SMS | ✅ CRÍTICA | "" | ✅ OBLIGATORIA |
| **TWILIO_VERIFY_SERVICE_SID** | SMS | ⚠️ Recomendada | "" | ⚠️ Opcional |

---

## 🚀 CONFIGURACIÓN MÍNIMA RAILWAY (PRODUCCIÓN)

### ✅ OPCIÓN A: Solo Variables Críticas (Mínimo Funcional)

```bash
# EMAIL SERVICE - CRÍTICO
RESEND_API_KEY=re_tu_api_key_aqui
EMAIL_FROM=noreply@mestocker.com

# SMS SERVICE - CRÍTICO
TWILIO_ACCOUNT_SID=AC_tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_FROM_NUMBER=+17379771943
```

**Resultado**:
- ✅ Password reset funcionará (email)
- ✅ OTP por email funcionará
- ✅ OTP por SMS funcionará (básico)
- ✅ Notificaciones SMS funcionarán
- ⚠️ No hay verificación avanzada Twilio Verify

---

### ⭐ OPCIÓN B: Configuración Completa (Recomendada)

```bash
# EMAIL SERVICE
RESEND_API_KEY=re_tu_api_key_aqui
EMAIL_FROM=noreply@mestocker.com
EMAIL_FROM_NAME=MeStocker
FRONTEND_URL=https://www.mestocker.com

# SMS SERVICE
TWILIO_ACCOUNT_SID=AC_tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_FROM_NUMBER=+17379771943
TWILIO_VERIFY_SERVICE_SID=VA_tu_verify_service_sid_aqui

# RATE LIMITING (opcional)
SMS_RATE_LIMIT_PER_NUMBER=5
SMS_RATE_LIMIT_WINDOW=3600
```

**Resultado**:
- ✅ Todas las funcionalidades de email
- ✅ Todas las funcionalidades de SMS
- ✅ Verificación avanzada con Twilio Verify
- ✅ Rate limiting configurado
- ✅ Templates de email con URL correcta

---

## 🔍 VERIFICACIÓN EN CÓDIGO

### Email Service - Verificación de Variables

```python
# app/services/email_service.py:49-74

def __init__(self):
    self.api_key = os.getenv('RESEND_API_KEY')  # LÍNEA 52
    self.from_email = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')  # LÍNEA 53
    self.from_name = os.getenv('EMAIL_FROM_NAME', 'MeStocker')  # LÍNEA 54

    if not self.api_key or not RESEND_AVAILABLE:
        self.simulation_mode = True  # MODO SIMULACIÓN SI FALTA
        logger.warning("⚠️  EmailService running in SIMULATION MODE")
```

**Logs esperados SI falta `RESEND_API_KEY`:**
```
❌ RESEND_API_KEY no configurado. Email service en modo simulación
⚠️  EmailService running in SIMULATION MODE - no real emails will be sent
```

---

### SMS Service - Verificación de Variables

```python
# app/services/sms_service.py:35-73

def __init__(self, redis_service: Optional[RedisService] = None):
    from app.core.config import settings

    self.account_sid = settings.TWILIO_ACCOUNT_SID  # LÍNEA 40
    self.auth_token = settings.TWILIO_AUTH_TOKEN    # LÍNEA 41
    self.from_number = settings.TWILIO_FROM_NUMBER  # LÍNEA 42
    self.verify_service_sid = settings.TWILIO_VERIFY_SERVICE_SID  # LÍNEA 43

    if not all([self.account_sid, self.auth_token, self.from_number]):
        self.simulation_mode = True  # MODO SIMULACIÓN SI FALTA
        logger.warning("Credenciales Twilio incompletas. SMS service en modo simulación.")
```

**Logs esperados SI faltan variables Twilio:**
```
Credenciales Twilio incompletas. SMS service en modo simulación.
Configurar: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
```

---

## 🧪 TESTING DE VARIABLES

### Test 1: Email Service Status

```bash
# Railway Logs - Buscar:
grep "EmailService Initialization" railway.log

# Esperado con variables correctas:
✅ EmailService initialized successfully with Resend API

# Esperado sin RESEND_API_KEY:
❌ RESEND_API_KEY no configurado. Email service en modo simulación
```

---

### Test 2: SMS Service Status

```bash
# Railway Logs - Buscar:
grep "SMS Service" railway.log

# Esperado con variables correctas:
SMS Service inicializado correctamente con Twilio
Conexión Twilio exitosa. Status: active

# Esperado sin variables Twilio:
Credenciales Twilio incompletas. SMS service en modo simulación.
```

---

### Test 3: Endpoint de Test (SI existe)

```bash
# Verificar si hay endpoint de test email:
curl -X POST https://mestocker-backend-production.up.railway.app/api/v1/test/send-email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'

# Verificar si hay endpoint de test SMS:
curl -X POST https://mestocker-backend-production.up.railway.app/api/v1/test/send-sms \
  -H "Content-Type: application/json" \
  -d '{"phone":"+17379771943","message":"Test"}'
```

---

## 📁 ARCHIVOS ANALIZADOS

```
✅ app/core/config.py
   - Líneas 112-124: Variables Twilio
   - Líneas 272-282: Variables SendGrid (LEGACY - NO USAR)
   - Líneas 509-514: Variables Email (OPCIONAL)

✅ app/services/email_service.py
   - Líneas 49-74: EmailService.__init__()
   - Línea 52: RESEND_API_KEY usage
   - Línea 53: EMAIL_FROM usage
   - Línea 54: EMAIL_FROM_NAME usage

✅ app/services/sms_service.py
   - Líneas 35-73: SMSService.__init__()
   - Línea 40: TWILIO_ACCOUNT_SID usage
   - Línea 41: TWILIO_AUTH_TOKEN usage
   - Línea 42: TWILIO_FROM_NUMBER usage
   - Línea 43: TWILIO_VERIFY_SERVICE_SID usage
```

---

## 🎯 RECOMENDACIÓN FINAL

### Para Director Técnico:

**DECISIÓN ESTRATÉGICA**:

#### OPCIÓN 1: Deployment Mínimo (RÁPIDO)
```bash
# Solo 4 variables críticas
RESEND_API_KEY=...
EMAIL_FROM=noreply@mestocker.com
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+17379771943
```

**Ventajas**:
- ✅ Deploy rápido (5 variables)
- ✅ Password reset funciona
- ✅ OTP funciona (email y SMS básico)

**Desventajas**:
- ⚠️ No hay verificación avanzada Twilio Verify
- ⚠️ No hay rate limiting SMS

---

#### OPCIÓN 2: Deployment Completo (RECOMENDADO)
```bash
# 7 variables + opcionales
RESEND_API_KEY=...
EMAIL_FROM=noreply@mestocker.com
EMAIL_FROM_NAME=MeStocker
FRONTEND_URL=https://www.mestocker.com

TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+17379771943
TWILIO_VERIFY_SERVICE_SID=...

SMS_RATE_LIMIT_PER_NUMBER=5
SMS_RATE_LIMIT_WINDOW=3600
```

**Ventajas**:
- ✅ Todas las funcionalidades
- ✅ Verificación avanzada
- ✅ Rate limiting protección
- ✅ Templates email con URL correcta

**Desventajas**:
- ⚠️ Requiere más configuración inicial

---

## ✅ CHECKLIST CONFIGURACIÓN

### Pre-Railway (Obtener credenciales):
- [ ] Crear cuenta Resend (https://resend.com)
- [ ] Obtener RESEND_API_KEY
- [ ] Verificar dominio para EMAIL_FROM
- [ ] Crear cuenta Twilio (https://twilio.com)
- [ ] Obtener TWILIO_ACCOUNT_SID
- [ ] Obtener TWILIO_AUTH_TOKEN
- [ ] Comprar/obtener TWILIO_FROM_NUMBER
- [ ] (Opcional) Crear Twilio Verify Service

### Railway Configuration:
- [ ] Ir a Railway Dashboard → Environment Variables
- [ ] Agregar RESEND_API_KEY
- [ ] Agregar EMAIL_FROM
- [ ] Agregar TWILIO_ACCOUNT_SID
- [ ] Agregar TWILIO_AUTH_TOKEN
- [ ] Agregar TWILIO_FROM_NUMBER
- [ ] (Opcional) Agregar TWILIO_VERIFY_SERVICE_SID
- [ ] Guardar cambios
- [ ] Railway auto-redeploy

### Post-Deployment Verification:
- [ ] Revisar Railway logs: grep "EmailService"
- [ ] Revisar Railway logs: grep "SMS Service"
- [ ] Verificar NO hay "simulation mode" en logs
- [ ] Test password reset desde frontend
- [ ] Test OTP email desde registro
- [ ] Test OTP SMS si está configurado

---

## 🚨 TROUBLESHOOTING

### Problema: Email service en simulation mode

**Logs:**
```
❌ RESEND_API_KEY no configurado. Email service en modo simulación
```

**Solución:**
1. Verificar que RESEND_API_KEY está en Railway
2. Verificar que no tiene espacios extra
3. Verificar que comienza con `re_`
4. Redeploy Railway

---

### Problema: SMS service en simulation mode

**Logs:**
```
Credenciales Twilio incompletas. SMS service en modo simulación.
```

**Solución:**
1. Verificar las 3 variables Twilio están configuradas
2. Verificar TWILIO_ACCOUNT_SID comienza con `AC`
3. Verificar TWILIO_FROM_NUMBER tiene formato +1XXXXXXXXXX
4. Redeploy Railway

---

## 📞 SOPORTE

**Si necesitas ayuda obteniendo credenciales:**

**Resend:**
- Docs: https://resend.com/docs
- API Keys: https://resend.com/api-keys
- Domain Verification: https://resend.com/domains

**Twilio:**
- Console: https://console.twilio.com
- Phone Numbers: https://console.twilio.com/phone-numbers
- Verify Service: https://console.twilio.com/verify/services
- Docs: https://www.twilio.com/docs

---

**Generado por**: @backend-framework-ai @third-party-integration-ai
**Timestamp**: 2025-10-09T21:45:00Z
**Archivos analizados**: 3 (config.py, email_service.py, sms_service.py)

🟢 **LISTA COMPLETA - LISTO PARA CONFIGURAR RAILWAY**
