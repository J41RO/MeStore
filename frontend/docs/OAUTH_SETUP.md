# OAuth Setup Guide - MeStocker
## Guía Completa para Activación de OAuth Google y Facebook

### 📋 Resumen Ejecutivo
Este documento contiene las instrucciones completas para activar OAuth real en MeStocker. Actualmente, el sistema tiene una implementación UI Ready con lógica placeholder que simula la funcionalidad OAuth para desarrollo y testing.

### ✅ Estado Actual (OAuth UI Ready)
- **Frontend**: Botones OAuth implementados con estilos oficiales
- **Hooks**: useGoogleAuth y useFacebookAuth con lógica placeholder
- **Variables de entorno**: Configuradas con placeholders
- **UI/UX**: Experiencia visual idéntica a OAuth real
- **Tests**: Funcionalidad simulada completamente operativa

### 🚀 Activación Real (2-3 horas)

#### PASO 1: Configuración Google OAuth (45 min)

##### 1.1 Google Cloud Console Setup
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear nuevo proyecto o seleccionar existente
3. Habilitar Google+ API:
   ```
   APIs & Services > Library > Google+ API > Enable
   ```
4. Crear credenciales OAuth 2.0:
   ```
   APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID
   ```

##### 1.2 Configuración de Client ID
```javascript
Application Type: Web Application
Name: MeStocker OAuth
Authorized JavaScript Origins:
- http://localhost:5173
- http://192.168.1.137:5173
- https://yourdomain.com (producción)

Authorized Redirect URIs:
- http://localhost:5173/auth/google/callback
- http://192.168.1.137:5173/auth/google/callback
- https://yourdomain.com/auth/google/callback
```

##### 1.3 Actualizar Variables de Entorno
Reemplazar en `.env.development`:
```bash
# Reemplazar placeholders con valores reales
VITE_GOOGLE_CLIENT_ID=tu_google_client_id_real.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_SECRET=tu_google_client_secret_real
```

#### PASO 2: Configuración Facebook OAuth (45 min)

##### 2.1 Facebook Developers Console
1. Ir a [Facebook for Developers](https://developers.facebook.com/)
2. Crear nueva app:
   ```
   My Apps > Create App > Consumer > Continue
   ```
3. Configurar Facebook Login:
   ```
   Add Product > Facebook Login > Set Up
   ```

##### 2.2 Configuración de App Settings
```javascript
App Name: MeStocker
App Domains: yourdomain.com
Privacy Policy URL: https://yourdomain.com/privacy
Terms of Service URL: https://yourdomain.com/terms

Valid OAuth Redirect URIs:
- http://localhost:5173/auth/facebook/callback
- http://192.168.1.137:5173/auth/facebook/callback
- https://yourdomain.com/auth/facebook/callback
```

##### 2.3 Actualizar Variables de Entorno
Reemplazar en `.env.development`:
```bash
# Reemplazar placeholders con valores reales
VITE_FACEBOOK_APP_ID=tu_facebook_app_id_real
VITE_FACEBOOK_APP_SECRET=tu_facebook_app_secret_real
```

#### PASO 3: Actualización de Código (60 min)

##### 3.1 Configurar Google OAuth Provider
En `src/main.tsx`:
```tsx
import { GoogleOAuthProvider } from '@react-oauth/google';

// Envolver la app con el provider
<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
  <App />
</GoogleOAuthProvider>
```

##### 3.2 Actualizar useGoogleAuth Hook
Reemplazar lógica simulada en `src/hooks/useGoogleAuth.ts`:
```typescript
// Reemplazar en la función login:
if (credentialResponse.credential) {
  // Decodificar JWT real
  const decoded = jwt_decode(credentialResponse.credential);
  
  // Validar con backend real
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/google/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      credential: credentialResponse.credential,
      clientId: credentialResponse.clientId
    })
  });
  
  if (response.ok) {
    const userInfo = await response.json();
    setUserInfo(userInfo);
  }
}
```

##### 3.3 Cargar Facebook SDK
En `src/hooks/useFacebookAuth.ts`:
```typescript
useEffect(() => {
  // Cargar Facebook SDK real
  window.fbAsyncInit = function() {
    FB.init({
      appId: import.meta.env.VITE_FACEBOOK_APP_ID,
      cookie: true,
      xfbml: true,
      version: 'v18.0'
    });
    setIsInitialized(true);
  };

  // Cargar script del SDK
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));
}, []);
```

#### PASO 4: Backend Endpoints (30 min)

##### 4.1 Google Verification Endpoint
Crear en `app/api/v1/auth/google.py`:
```python
from google.oauth2 import id_token
from google.auth.transport import requests

@router.post("/verify")
async def verify_google_token(token_data: GoogleTokenData):
    try:
        # Verificar token con Google
        idinfo = id_token.verify_oauth2_token(
            token_data.credential, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Extraer datos del usuario
        user_data = {
            "google_id": idinfo['sub'],
            "email": idinfo['email'],
            "name": idinfo['name'],
            "picture": idinfo.get('picture')
        }
        
        # Crear o actualizar usuario en base de datos
        user = await create_or_update_google_user(user_data)
        
        return {"success": True, "user": user}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")
```

##### 4.2 Facebook Verification Endpoint
Crear en `app/api/v1/auth/facebook.py`:
```python
import requests

@router.post("/verify")
async def verify_facebook_token(token_data: FacebookTokenData):
    # Verificar token con Facebook Graph API
    response = requests.get(
        f"https://graph.facebook.com/me",
        params={
            "access_token": token_data.access_token,
            "fields": "id,name,email,picture"
        }
    )
    
    if response.status_code == 200:
        user_data = response.json()
        user = await create_or_update_facebook_user(user_data)
        return {"success": True, "user": user}
    else:
        raise HTTPException(status_code=400, detail="Invalid Facebook token")
```

### 🧪 Testing Real OAuth

#### Google OAuth Test
1. Hacer clic en "Registrarse con Google"
2. Seleccionar cuenta Google real
3. Autorizar permisos
4. Verificar datos pre-llenados en formulario

#### Facebook OAuth Test
1. Hacer clic en "Registrarse con Facebook"  
2. Autorizar con Facebook real
3. Verificar datos pre-llenados en formulario

### 🔒 Consideraciones de Seguridad

#### Variables de Entorno Seguras
```bash
# Producción - usar variables secretas
VITE_GOOGLE_CLIENT_ID=publico_ok
GOOGLE_CLIENT_SECRET=servidor_solamente_secreto
VITE_FACEBOOK_APP_ID=publico_ok  
FACEBOOK_APP_SECRET=servidor_solamente_secreto
```

#### Validaciones Backend
- Siempre verificar tokens en backend
- No confiar en datos del frontend
- Implementar rate limiting
- Logs de autenticación OAuth

### 📋 Checklist de Activación

#### Pre-requisitos
- [ ] Dominio configurado (para producción)
- [ ] Certificado SSL (para producción)
- [ ] Cuentas de desarrollador (Google Cloud + Facebook)

#### Configuración
- [ ] Google Cloud Console configurado
- [ ] Facebook Developers Console configurado
- [ ] Variables de entorno actualizadas
- [ ] Providers configurados en frontend

#### Código
- [ ] Google OAuth Provider integrado
- [ ] Facebook SDK cargado
- [ ] Hooks actualizados con lógica real
- [ ] Backend endpoints implementados

#### Testing
- [ ] Google OAuth funcional
- [ ] Facebook OAuth funcional
- [ ] Datos pre-llenados correctamente
- [ ] Validación backend funcionando

#### Producción
- [ ] Variables de entorno de producción
- [ ] Dominios autorizados actualizados
- [ ] Monitoreo de errores OAuth
- [ ] Documentación actualizada

### 🚨 Notas Importantes

#### Limitaciones Actuales (Modo Placeholder)
- OAuth funciona solo en simulación
- Datos mock pre-definidos
- No se conecta con APIs externas reales
- Perfecto para desarrollo y testing UI

#### Beneficios del Enfoque UI Ready
- Desarrollo frontend sin dependencias externas
- Testing de UX/UI completo
- Activación rápida cuando sea necesario
- No bloquea desarrollo de otras features

### 📞 Soporte Técnico

#### Errores Comunes
1. **"Invalid Client ID"**: Verificar VITE_GOOGLE_CLIENT_ID
2. **"Redirect URI mismatch"**: Actualizar URIs autorizadas
3. **Facebook SDK not loaded**: Verificar conexión a internet
4. **CORS errors**: Configurar dominios autorizados

#### Debug Mode
```bash
# Activar logs detallados
VITE_OAUTH_DEBUG=true
```

### 🎯 Tiempo Estimado de Activación
- **Setup Google**: 45 minutos
- **Setup Facebook**: 45 minutos  
- **Actualización código**: 60 minutos
- **Testing**: 30 minutos
- **Total**: 3 horas aproximadamente

### ✅ Entregable Final
Al completar esta guía tendrás:
- OAuth Google y Facebook completamente funcional
- Usuarios registrados automáticamente
- Formularios pre-llenados con datos reales
- Sistema de autenticación robusto y seguro

### 🔧 Corrección Inmediata del Error Actual

El error actual se debe a que falta configurar el GoogleOAuthProvider. Para corregirlo:

```tsx
// src/main.tsx - Agregar al inicio
import { GoogleOAuthProvider } from '@react-oauth/google';

// Envolver App con:
<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your_google_client_id_here'}>
  <App />
</GoogleOAuthProvider>
```

### 📊 Estado de Implementación Actual

#### ✅ Completado
- Dependencias OAuth instaladas (@react-oauth/google, react-icons)
- Variables de entorno configuradas
- Botones OAuth con estilos oficiales
- Hooks OAuth Ready implementados
- Build exitoso verificado

#### ⚠️ Pendiente de Corrección
- GoogleOAuthProvider configuración en main.tsx
- Test funcional de botones OAuth

#### 🎯 Siguiente Paso Inmediato
1. Configurar GoogleOAuthProvider en main.tsx
2. Verificar página /register funcional
3. Completar documentación OAuth