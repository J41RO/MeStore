# 📋 ANÁLISIS COMPLETO: Google OAuth Callback Flow

**Fecha**: 2025-10-13
**Componente**: Google OAuth Integration (Login.tsx + Backend)
**Tipo**: Análisis de callback y flujo post-autenticación
**Status**: ✅ ANÁLISIS COMPLETO

---

## 📊 RESUMEN EJECUTIVO

### 🎯 RESPUESTAS DIRECTAS A LAS 4 PREGUNTAS:

**1. ¿URL de redirect configurada coincide con Google Console?**
- ⚠️ **PARCIALMENTE** - URLs hardcoded en backend NO incluyen producción
- ✅ URLs de desarrollo: `localhost:5173`, `127.0.0.1:5173`, `192.168.1.137:5173`
- ❌ URLs de producción faltantes: Render/Vercel URLs

**2. ¿Qué pasa después del callback exitoso?**
- ✅ Usuario redirigido DIRECTAMENTE al dashboard según user_type
- ✅ Token JWT guardado en authStore
- ✅ Datos de usuario guardados en Zustand state
- ❌ NO hay paso intermedio de registro

**3. ¿Usuario nuevo va directo a dashboard o debe completar Steps 2-4?**
- 🚨 **VA DIRECTO A DASHBOARD** sin completar registro multi-paso
- ❌ Usuario VENDOR sin perfil de vendedor (solo cuenta User)
- ❌ NO completa Steps 2-4 del VendorRegistrationFlow
- ❌ Datos faltantes: NIT, dirección, ciudad, documentos

**4. ¿Manejo de errores si Google OAuth falla?**
- ✅ Error handling en frontend (try-catch + display)
- ✅ Error handling en backend (HTTPException)
- ⚠️ Mensajes genéricos poco específicos
- ❌ NO hay retry automático

---

## 🔍 ANÁLISIS DETALLADO

### 📌 1. URL DE REDIRECT CONFIGURADA

#### Frontend Configuration (main.tsx:69)

```typescript
<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your_google_client_id_here'}>
```

**Variable de entorno**:
- `VITE_GOOGLE_CLIENT_ID=122286459611-6gn242ufa5h0q3dtd1j6732ugil8h1f9.apps.googleusercontent.com`

**Ubicación**: `frontend/.env.production`

#### Backend Configuration (google_oauth.py:202-211)

```python
"redirect_uris": [
    "http://localhost:5173",           # ← Desarrollo local
    "http://127.0.0.1:5173",           # ← Loopback
    "http://192.168.1.137:5173"        # ← ⚠️ IP HARDCODED (desarrollo)
],
"javascript_origins": [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.137:5173"
]
```

**🚨 PROBLEMA CRÍTICO P0-1**: URLs de producción faltantes

**URLs que DEBEN agregarse**:
```python
"redirect_uris": [
    # Desarrollo
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.137:5173",

    # Producción Frontend (Vercel)
    "https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app",

    # Producción Backend (Render)
    "https://mestore.onrender.com"
],
"javascript_origins": [
    # Desarrollo
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Producción
    "https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app",
    "https://mestore.onrender.com"
]
```

#### Google Console Configuration Required

**Configuración en Google Cloud Console → Credentials → OAuth 2.0 Client IDs**:

1. **Authorized JavaScript origins**:
   - `http://localhost:5173` ✅
   - `http://127.0.0.1:5173` ✅
   - `https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app` ⚠️ AGREGAR

2. **Authorized redirect URIs**:
   - `http://localhost:5173` ✅
   - `http://127.0.0.1:5173` ✅
   - `https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app` ⚠️ AGREGAR

**⚠️ ADVERTENCIA**: Si las URLs de producción NO están en Google Console, OAuth fallará con error:
```
redirect_uri_mismatch: The redirect URI in the request,
https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app,
does not match the ones authorized for the OAuth client.
```

---

### 📌 2. QUÉ PASA DESPUÉS DEL CALLBACK EXITOSO

#### Flujo Completo del Callback

**Paso 1: Usuario hace click en "Continuar con Google"** (Login.tsx:387-394)

```typescript
<GoogleSignInButton
  onSuccess={handleGoogleSuccess}  // ← Callback handler
  onError={handleGoogleError}
  text="signin_with"
  theme="outline"
  size="large"
  width="100%"
/>
```

**Paso 2: Google retorna con credentialResponse** (Login.tsx:149-184)

```typescript
const handleGoogleSuccess = async (credentialResponse: any) => {
  setIsLoading(true);
  setError(null);

  try {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    // POST al backend con id_token de Google
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/google/login`, {
      id_token: credentialResponse.credential,  // ← Token de Google
      user_type: 'BUYER'                        // ← ⚠️ HARDCODED como BUYER
    });

    if (response.data.success && response.data.access_token) {
      // Guardar token y usuario en Zustand store
      const { setToken, setUser } = useAuthStore.getState();
      setToken(response.data.access_token);    // ← JWT token
      setUser(response.data.user);             // ← Datos usuario

      // Redireccionar según user_type
      const redirectPath = getRedirectPath(
        response.data.user.user_type,
        undefined,
        returnTo || undefined
      );
      navigate(redirectPath);                   // ← Navegación inmediata

      // Limpiar checkout intent
      localStorage.removeItem('pendingCheckout');
      localStorage.removeItem('checkoutReturnUrl');
    }
  } catch (error: any) {
    setError(error.response?.data?.detail || 'Error en login con Google');
  } finally {
    setIsLoading(false);
  }
};
```

**🚨 PROBLEMA CRÍTICO P0-2**: `user_type` hardcoded como `'BUYER'`
- Si usuario es VENDOR, se crea como BUYER
- NO hay forma de seleccionar VENDOR durante OAuth
- Usuario debe cambiar tipo después del login

#### Redirección Inteligente (Login.tsx:11-32)

```typescript
const getRedirectPath = (userType: UserType, portalType?: string, returnTo?: string): string => {
  // Si hay returnTo (ej: checkout), usar eso
  if (returnTo) {
    return returnTo;
  }

  switch (userType) {
    case UserType.VENDOR:
      return '/app/vendor-dashboard';    // ← Dashboard vendedor
    case UserType.BUYER:
      return '/app/dashboard';           // ← Dashboard comprador
    case UserType.ADMIN:
    case UserType.SUPERUSER:
      if (portalType === 'secure') {
        return '/admin-secure-portal/dashboard';
      }
      return '/admin/dashboard';
    default:
      return '/dashboard';
  }
};
```

**✅ CORRECTO**: Redirección basada en user_type

---

### 📌 3. USUARIO NUEVO: ¿Dashboard o Steps 2-4?

#### 🚨 DESCUBRIMIENTO CRÍTICO: VA DIRECTO A DASHBOARD

**Flujo Backend** (google_oauth_service.py:241-302)

```python
async def authenticate_or_create_user(
    self,
    db: AsyncSession,
    token: str,
    user_type: str = "BUYER"
) -> Tuple[bool, str, Optional[User], Optional[str]]:
    try:
        # Verificar token de Google
        google_info = await self.verify_google_token(token)
        if not google_info:
            return False, "Token de Google inválido", None, None

        google_id = google_info.get('sub')
        email = google_info.get('email')

        # Buscar usuario por Google ID
        user = await self.find_user_by_google_id(db, google_id)

        if user:
            # Usuario existe → Login inmediato
            jwt_token = auth_service.create_access_token(data={"sub": user.email})
            return True, "Login exitoso", user, jwt_token

        # Buscar por email
        user = await self.find_user_by_email(db, email)

        if user:
            # Usuario existe pero sin Google → Vincular Google
            success, message = await self.link_google_to_existing_user(db, user, google_info)
            if success:
                jwt_token = auth_service.create_access_token(data={"sub": user.email})
                return True, "Cuenta vinculada y login exitoso", user, jwt_token

        # ⚠️ Usuario NO existe → Crear nuevo
        success, message, user = await self.create_user_from_google(db, google_info, user_type)

        if success and user:
            jwt_token = auth_service.create_access_token(data={"sub": user.email})
            return True, "Usuario creado y login exitoso", user, jwt_token  # ← ✅ Login inmediato
```

**Creación de Usuario desde Google** (google_oauth_service.py:134-196)

```python
async def create_user_from_google(
    self,
    db: AsyncSession,
    google_info: Dict,
    user_type: str = "BUYER"
) -> Tuple[bool, str, Optional[User]]:
    try:
        # Extraer información de Google
        email = google_info.get('email')
        name = google_info.get('name', '')
        picture = google_info.get('picture', '')
        google_id = google_info.get('sub')
        email_verified = google_info.get('email_verified', False)

        # Dividir nombre
        name_parts = name.split(' ', 1) if name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # ⚠️ Crear usuario SOLO con datos de Google
        user = User(
            email=email,
            password_hash="oauth_no_password",  # ← Placeholder OAuth
            nombre=first_name,                   # ← Solo nombre de Google
            apellido=last_name,                  # ← Solo apellido de Google
            user_type=UserType(user_type),       # ← BUYER hardcoded
            is_active=True,
            is_verified=True,                    # ← Verificado por Google
            email_verified=True,
            google_id=google_id,
            google_email=email,
            google_name=name,
            google_picture=picture,
            google_verified_email=email_verified,
            oauth_provider="google",
            oauth_linked_at=datetime.utcnow()

            # ❌ FALTA: telefono
            # ❌ FALTA: Perfil de vendedor (si user_type=VENDOR)
            # ❌ FALTA: NIT, dirección, ciudad, departamento
            # ❌ FALTA: Documentos de verificación
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return True, "Usuario creado exitosamente", user
```

#### 🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS

**P0-1: Usuario VENDOR sin perfil de vendedor**

**Situación actual**:
```
Usuario hace OAuth con Google como VENDOR
  ↓
Backend crea User con user_type=VENDOR
  ↓
NO crea registro en tabla Vendors
  ↓
Usuario redirigido a /app/vendor-dashboard
  ↓
🚨 Dashboard falla: NO tiene perfil de vendedor
```

**Datos faltantes en tabla Vendors**:
- `nombre_empresa` (NULL)
- `tipo_persona` (NULL)
- `nit` (NULL)
- `direccion` (NULL)
- `ciudad` (NULL)
- `departamento` (NULL)
- `telefono` (NULL)
- Documentos de verificación (vacío)

**P0-2: NO hay paso intermedio para completar registro**

**Flujo esperado vs actual**:

| Flujo Esperado | Flujo Actual |
|----------------|--------------|
| 1. OAuth con Google | 1. OAuth con Google ✅ |
| 2. Usuario creado con datos básicos | 2. Usuario creado ✅ |
| 3. **Redirección a Steps 2-4** | 3. **Redirección DIRECTA a dashboard** ❌ |
| 4. Completar información de negocio | 4. NO ocurre ❌ |
| 5. Subir documentos | 5. NO ocurre ❌ |
| 6. Dashboard habilitado | 6. Dashboard sin datos ❌ |

**P0-3: Usuario BUYER también tiene datos incompletos**

**Datos faltantes**:
- `telefono` (NULL)
- `direccion` (NULL) - necesario para checkout
- `ciudad` (NULL)

---

### 📌 4. MANEJO DE ERRORES SI GOOGLE OAUTH FALLA

#### Frontend Error Handling (Login.tsx:149-184)

```typescript
const handleGoogleSuccess = async (credentialResponse: any) => {
  setIsLoading(true);
  setError(null);  // ← Limpia error previo

  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/google/login`, {
      id_token: credentialResponse.credential,
      user_type: 'BUYER'
    });

    if (response.data.success && response.data.access_token) {
      // ... éxito
    } else {
      // ⚠️ Caso: success=false pero sin exception
      setError(response.data.message || 'Error en login con Google');
    }
  } catch (error: any) {
    // ✅ Manejo de excepciones
    console.error('Error en Google login:', error);
    setError(error.response?.data?.detail || 'Error en login con Google');
  } finally {
    setIsLoading(false);  // ← Siempre limpia loading
  }
};
```

**Error Callback Simple** (Login.tsx:186-188)

```typescript
const handleGoogleError = () => {
  setError('Error en login con Google. Inténtalo de nuevo.');
};
```

**🚨 PROBLEMA P1-1**: Mensaje de error muy genérico
- NO especifica si es problema de red, token inválido, o servidor
- Usuario no sabe qué hacer para resolver

#### Display de Error en UI (Login.tsx:241-245)

```typescript
{error && (
  <div className="p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
    <p className="text-sm text-red-700 font-medium">{error}</p>
  </div>
)}
```

**✅ CORRECTO**:
- Banner visible con ARIA role="alert"
- Color rojo distintivo
- Accesible

#### Backend Error Handling (google_oauth.py:45-113)

```python
@router.post("/login", response_model=GoogleAuthResponse)
async def google_login(
    request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"Google login attempt for user_type: {request.user_type}")

        # Validar tipo de usuario
        if request.user_type not in ["BUYER", "VENDOR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de usuario inválido. Debe ser BUYER o VENDOR"
            )

        # Autenticar o crear usuario
        success, message, user, jwt_token = await google_oauth_service.authenticate_or_create_user(
            db=db,
            token=request.id_token,
            user_type=request.user_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )

        # ... éxito

    except HTTPException:
        raise  # ← Re-lanza HTTPException sin modificar
    except Exception as e:
        logger.error(f"Error in Google login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en login con Google: {str(e)}"
        )
```

**✅ CORRECTO**:
- Logging de errores
- HTTPException con códigos específicos (400, 401, 500)
- Re-lanza HTTPException sin modificar
- Catch-all para excepciones inesperadas

#### Token Verification Errors (google_oauth_service.py:54-92)

```python
async def verify_google_token(self, token: str) -> Optional[Dict]:
    try:
        client_id = self._get_google_client_id()

        # Verificar token con Google API
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id
        )

        # Validar audience
        if idinfo['aud'] != client_id:
            logger.error("Token audience mismatch")
            return None

        # Validar issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.error("Token issuer invalid")
            return None

        logger.info(f"Google token verified for user: {idinfo.get('email')}")
        return idinfo

    except GoogleAuthError as e:
        logger.error(f"Google auth error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying Google token: {str(e)}")
        return None
```

**✅ CORRECTO**:
- Validación de audience (client ID)
- Validación de issuer (Google)
- Manejo específico de GoogleAuthError
- Logging detallado

#### Escenarios de Error Documentados

**Escenario 1: Token inválido o expirado**

```
Usuario hace click en Google OAuth
  ↓
Google retorna con token expirado
  ↓
Backend: verify_google_token() retorna None
  ↓
authenticate_or_create_user() retorna: (False, "Token de Google inválido", None, None)
  ↓
Endpoint lanza HTTPException 401
  ↓
Frontend catch: setError("Token de Google inválido")
  ↓
UI: Banner rojo "Error en login con Google"
```

**Escenario 2: Client ID mismatch**

```
Token audience no coincide con client_id configurado
  ↓
verify_google_token(): idinfo['aud'] != client_id
  ↓
Logger.error("Token audience mismatch")
  ↓
Retorna None → "Token de Google inválido"
  ↓
UI: Error genérico
```

**Escenario 3: Error de red / timeout**

```
axios.post() falla con timeout
  ↓
Frontend catch (error: any)
  ↓
error.response?.data?.detail → undefined
  ↓
Fallback: "Error en login con Google"
  ↓
🚨 Usuario no sabe si es problema de red o servidor
```

**Escenario 4: Redirect URI mismatch (Google Console)**

```
Usuario hace click en Google OAuth
  ↓
Google valida redirect_uri
  ↓
redirect_uri NO está en lista autorizada
  ↓
Google retorna error antes de callback
  ↓
handleGoogleError() ejecuta
  ↓
UI: "Error en login con Google. Inténtalo de nuevo."
  ↓
🚨 Error NO tiene información de qué falló
```

---

## 🎯 TABLA COMPARATIVA: FLUJO OAUTH vs REGISTRO MANUAL

| Aspecto | OAuth con Google | Registro Manual VendorRegistrationFlow |
|---------|------------------|----------------------------------------|
| **Paso 1: Datos básicos** | ✅ Auto (desde Google) | ✅ Formulario Step 1 |
| **Email verificado** | ✅ Automático | ❌ Requiere OTP |
| **Nombre completo** | ✅ Desde Google profile | ✅ Formulario |
| **Teléfono** | ❌ NO capturado | ✅ Formulario + validación |
| **Paso 2: Negocio** | ❌ OMITIDO | ✅ Step 2 completo |
| **NIT** | ❌ OMITIDO | ✅ Validación con checksum |
| **Dirección** | ❌ OMITIDO | ✅ Con ciudad y departamento |
| **Paso 3: Verificación** | ✅ Google verifica email | ⚠️ Mock OTP (no real) |
| **Verificación SMS** | ❌ NO hay | ⚠️ Mock (no implementado) |
| **Paso 4: Documentos** | ❌ OMITIDO | ✅ Upload con validación |
| **Perfil Vendor creado** | ❌ NO | ✅ Tabla Vendors populated |
| **Dashboard accesible** | ✅ Inmediato (pero incompleto) | ✅ Completo con datos |
| **Tiempo del usuario** | ⚡ 10 segundos | ⏱️ 2 minutos |

**📊 Resultados**:
- **OAuth**: Más rápido pero **datos INCOMPLETOS**
- **Manual**: Más lento pero **datos COMPLETOS y validados**

---

## 🚨 ISSUES CRÍTICOS PRIORIZADOS

### 🔴 P0 - BLOQUEANTES (Impiden uso de OAuth en producción)

**P0-1: URLs de producción faltantes**
- **Archivo**: `app/api/v1/endpoints/google_oauth.py:202-211`
- **Problema**: Hardcoded dev URLs, no producción
- **Impacto**: OAuth falla en producción con redirect_uri_mismatch
- **Fix**: Agregar URLs de Vercel/Render + configurar en Google Console
- **Tiempo**: 30 minutos

**P0-2: user_type hardcoded como BUYER**
- **Archivo**: `frontend/src/pages/Login.tsx:159`
- **Problema**: `user_type: 'BUYER'` siempre
- **Impacto**: Vendedores no pueden hacer OAuth como VENDOR
- **Fix**: UI selector antes de OAuth o detectar desde landing
- **Tiempo**: 1 hora

**P0-3: Usuario VENDOR sin perfil de vendedor**
- **Archivo**: `app/services/google_oauth_service.py:134-196`
- **Problema**: Solo crea User, NO crea registro en Vendors
- **Impacto**: Dashboard vendedor inaccesible, datos faltantes
- **Fix**: Crear Vendor profile automático o redirigir a Steps 2-4
- **Tiempo**: 2 horas

**P0-4: NO hay redirección a completar registro**
- **Archivo**: `frontend/src/pages/Login.tsx:169`
- **Problema**: OAuth → Dashboard directo, omite Steps 2-4
- **Impacto**: Datos críticos faltantes (NIT, dirección, docs)
- **Fix**: Detectar usuario incompleto → redirigir a VendorRegistrationFlow
- **Tiempo**: 3 horas

### 🟡 P1 - ALTA PRIORIDAD

**P1-1: Mensajes de error genéricos**
- **Archivo**: `frontend/src/pages/Login.tsx:180, 187`
- **Problema**: "Error en login con Google" no especifica causa
- **Fix**: Mensajes específicos por tipo de error
- **Tiempo**: 30 minutos

**P1-2: NO hay retry automático**
- **Problema**: Usuario debe recargar página para reintentar
- **Fix**: Botón "Reintentar" en banner de error
- **Tiempo**: 20 minutos

**P1-3: Token JWT usa email en vez de user.id**
- **Archivo**: `app/services/google_oauth_service.py:276, 286, 295`
- **Problema**: `create_access_token(data={"sub": user.email})`
- **Impacto**: Session breaks si usuario cambia email
- **Fix**: Usar `user.id` como subject
- **Tiempo**: 15 minutos

---

## 🎯 SOLUCIONES PROPUESTAS

### Solución 1: Redirección Condicional Post-OAuth

**Lógica de detección de perfil incompleto**:

```typescript
// Login.tsx - handleGoogleSuccess
if (response.data.success && response.data.access_token) {
  const { setToken, setUser } = useAuthStore.getState();
  setToken(response.data.access_token);
  setUser(response.data.user);

  // ✅ NUEVO: Detectar si perfil está completo
  const user = response.data.user;
  const isProfileComplete = checkProfileComplete(user);

  let redirectPath;

  if (!isProfileComplete && user.user_type === 'VENDOR') {
    // Redirigir a completar registro (Steps 2-4)
    redirectPath = '/register/vendor/complete?oauth=true';

    // Pre-llenar datos de Google en localStorage
    localStorage.setItem('oauth-partial-data', JSON.stringify({
      email: user.email,
      nombre: user.nombre,
      apellido: user.apellido,
      email_verified: true,
      oauth_provider: 'google'
    }));
  } else {
    // Dashboard normal
    redirectPath = getRedirectPath(user.user_type, undefined, returnTo || undefined);
  }

  navigate(redirectPath);
}

// Helper function
function checkProfileComplete(user: any): boolean {
  if (user.user_type === 'VENDOR') {
    // Verificar datos críticos de vendedor
    return !!(
      user.telefono &&
      user.vendor_profile?.nombre_empresa &&
      user.vendor_profile?.nit &&
      user.vendor_profile?.direccion &&
      user.vendor_profile?.ciudad
    );
  }

  if (user.user_type === 'BUYER') {
    // Verificar datos críticos de comprador
    return !!(user.telefono);  // Mínimo: teléfono
  }

  return true;
}
```

### Solución 2: Crear Vendor Profile Automático (Placeholder)

**Backend: Crear perfil incompleto automáticamente**:

```python
# google_oauth_service.py - create_user_from_google
async def create_user_from_google(
    self,
    db: AsyncSession,
    google_info: Dict,
    user_type: str = "BUYER"
) -> Tuple[bool, str, Optional[User]]:
    try:
        # ... crear usuario (código existente)

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # ✅ NUEVO: Si es VENDOR, crear perfil placeholder
        if user_type == "VENDOR":
            from app.models.vendor import Vendor

            vendor_profile = Vendor(
                user_id=user.id,
                nombre_empresa=f"Empresa de {name}",  # Placeholder
                email=email,
                telefono=None,  # NULL - debe completar
                tipo_persona="persona_natural",  # Default
                nit=None,  # NULL - debe completar
                direccion=None,  # NULL - debe completar
                ciudad=None,  # NULL - debe completar
                departamento=None,  # NULL - debe completar
                is_active=False,  # Inactivo hasta completar
                verificado=False,
                vendor_status="DRAFT"  # Estado borrador
            )

            db.add(vendor_profile)
            await db.commit()

            logger.info(f"Created placeholder vendor profile for: {email}")

        return True, "Usuario creado exitosamente", user
```

**Frontend: Detectar vendor_status=DRAFT y forzar completar**:

```typescript
// VendorDashboard.tsx - useEffect
useEffect(() => {
  const checkVendorProfile = async () => {
    const response = await axios.get('/api/v1/vendors/me');
    const vendor = response.data;

    if (vendor.vendor_status === 'DRAFT') {
      // Forzar completar registro
      navigate('/register/vendor/complete?required=true');
    }
  };

  checkVendorProfile();
}, []);
```

### Solución 3: UI Selector de Tipo de Usuario Antes de OAuth

**Login.tsx - Agregar selector**:

```typescript
const [userTypeForOAuth, setUserTypeForOAuth] = useState<'BUYER' | 'VENDOR'>('BUYER');

// Modificar handleGoogleSuccess
const response = await axios.post(`${API_BASE_URL}/api/v1/auth/google/login`, {
  id_token: credentialResponse.credential,
  user_type: userTypeForOAuth  // ← Usar estado en vez de hardcoded
});

// UI
<div className="mb-4 space-y-3">
  <label className="block text-sm font-medium text-gray-700">
    ¿Cómo quieres usar MeStocker?
  </label>
  <div className="flex gap-3">
    <button
      type="button"
      onClick={() => setUserTypeForOAuth('BUYER')}
      className={`flex-1 p-3 border rounded-lg ${
        userTypeForOAuth === 'BUYER'
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300'
      }`}
    >
      🛒 Comprar productos
    </button>
    <button
      type="button"
      onClick={() => setUserTypeForOAuth('VENDOR')}
      className={`flex-1 p-3 border rounded-lg ${
        userTypeForOAuth === 'VENDOR'
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300'
      }`}
    >
      🏪 Vender productos
    </button>
  </div>
</div>

<GoogleSignInButton ... />
```

---

## 📊 FLUJO RECOMENDADO COMPLETO

### Escenario 1: Usuario BUYER con OAuth

```
1. Usuario click "Continuar con Google"
   ↓
2. Selector: Selecciona "🛒 Comprar productos" (BUYER)
   ↓
3. Google OAuth popup → Autorización
   ↓
4. Callback con id_token
   ↓
5. POST /api/v1/auth/google/login { user_type: "BUYER" }
   ↓
6. Backend:
   - Verifica token ✅
   - Busca usuario por google_id → NO existe
   - Crea User con user_type=BUYER ✅
   - Retorna JWT token ✅
   ↓
7. Frontend:
   - Guarda token en authStore ✅
   - Detecta: telefono=NULL → Perfil incompleto
   - Muestra modal: "¿Quieres agregar tu teléfono?" [Después] [Agregar]
   ↓
8. Usuario click [Después]
   ↓
9. Redirección: /app/dashboard ✅
   ↓
10. Dashboard funcional (puede comprar, teléfono opcional)
```

### Escenario 2: Usuario VENDOR con OAuth

```
1. Usuario click "Continuar con Google"
   ↓
2. Selector: Selecciona "🏪 Vender productos" (VENDOR)
   ↓
3. Google OAuth popup → Autorización
   ↓
4. Callback con id_token
   ↓
5. POST /api/v1/auth/google/login { user_type: "VENDOR" }
   ↓
6. Backend:
   - Verifica token ✅
   - Busca usuario por google_id → NO existe
   - Crea User con user_type=VENDOR ✅
   - Crea Vendor profile con vendor_status=DRAFT ✅
   - Retorna JWT token ✅
   ↓
7. Frontend:
   - Guarda token en authStore ✅
   - Detecta: vendor_status=DRAFT → Perfil incompleto ⚠️
   - Muestra pantalla: "¡Bienvenido! Completa tu perfil de vendedor"
   ↓
8. Redirección: /register/vendor/complete?oauth=true
   ↓
9. VendorRegistrationFlow (Steps 2-4):
   - Step 2: Negocio (NIT, dirección, ciudad) ✅
   - Step 3: Verificación (teléfono por SMS) ✅
   - Step 4: Documentos (cédula, RUT) ✅
   ↓
10. Backend: Actualiza vendor_status=PENDING_APPROVAL
   ↓
11. Redirección: /app/vendor-dashboard
   ↓
12. Dashboard funcional con datos completos ✅
```

---

## 🏆 CONCLUSIONES FINALES

### ✅ Fortalezas del Sistema OAuth

1. **Token Verification**: Robusta validación con Google API
2. **Error Handling**: Try-catch en frontend y backend
3. **Logging**: Detallado para debugging
4. **Security**: Validación de audience e issuer
5. **User Experience**: Login rápido (10 segundos)

### ❌ Debilidades Críticas

1. **URLs Producción Faltantes**: OAuth no funciona en deploy
2. **user_type Hardcoded**: Vendedores no pueden usar OAuth
3. **Perfil Incompleto**: Usuario VENDOR sin datos de negocio
4. **Sin Redirección a Completar**: Omite Steps 2-4 críticos
5. **Mensajes Genéricos**: Errores poco específicos

### 🎯 Recomendación Ejecutiva

**⚠️ OAUTH NO LISTO PARA PRODUCCIÓN (VENDOR)**

**Razones**:
- P0-3: Usuario VENDOR queda sin perfil de vendedor
- P0-4: Datos críticos faltantes (NIT, dirección, documentos)
- P0-1: URLs de producción no configuradas

**Timeline para Producción**: 6-8 horas

**Prioridad de Implementación**:
1. **CRÍTICO**: P0-1 (URLs producción) + P0-2 (selector user_type)
2. **URGENTE**: P0-3 (vendor profile) + P0-4 (redirección completar)
3. **IMPORTANTE**: P1-1 (mensajes error) + P1-3 (JWT con user.id)

**Workaround Temporal**:
- Deshabilitar OAuth para VENDOR hasta completar fixes
- Solo permitir OAuth para BUYER (funciona relativamente bien)
- Mostrar mensaje: "Vendedores: Usa registro manual para obtener todas las funcionalidades"

---

**Análisis completado por**: Assistant Claude Code
**Fecha**: 2025-10-13
**Archivos analizados**: 5 (Login.tsx, main.tsx, google_oauth.py, google_oauth_service.py, .env)
**Líneas analizadas**: ~800 líneas
**Responsables sugeridos**: react-specialist-ai (frontend), backend-framework-ai (OAuth), security-backend-ai (URLs producción)
