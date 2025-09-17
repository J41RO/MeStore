# 🧪 Instrucciones para Probar el Sistema de Autenticación

## 📋 Credenciales de Prueba

| Usuario | Email | Password | Rol | Dashboard URL |
|---------|-------|----------|-----|---------------|
| Comprador | `buyer@mestore.com` | `123456` | COMPRADOR | `http://localhost:5173/app/dashboard` |
| Vendedor | `vendor@mestore.com` | `123456` | VENDEDOR | `http://localhost:5173/app/vendor-dashboard` |
| Admin | `admin@mestore.com` | `123456` | ADMIN | `http://localhost:5173/admin-secure-portal/dashboard` |
| Super Admin | `super@mestore.com` | `123456` | SUPERUSER | `http://localhost:5173/admin-secure-portal/dashboard` |

## 🧪 Métodos de Prueba

### Método 1: Archivo HTML de Test
1. Abre el archivo `test_browser_flow.html` en tu navegador
2. Usa las credenciales de prueba para hacer login
3. Verifica que el token se guarde en localStorage
4. Haz clic en "Probar Dashboard" para acceder

### Método 2: Prueba Manual en Frontend
1. Ve a `http://localhost:5173`
2. Busca la página de login
3. Usa cualquiera de las credenciales de arriba
4. Deberías ser redirigido automáticamente a tu dashboard correspondiente

### Método 3: Acceso Directo (Después de Login)
1. Primero haz login usando cualquier método
2. Luego accede directamente a la URL de tu dashboard
3. Ahora debería funcionar sin mostrar "Acceso Restringido"

## 🔧 Problemas Solucionados

### ✅ Problema 1: Serialización de user_type
**Problema:** El backend devolvía `"UserType.VENDEDOR"` en lugar de `"VENDEDOR"`
**Solución:** Cambiado `str(user_type)` por `user_type.value` en el endpoint `/auth/me`

### ✅ Problema 2: Estado de autenticación no persistía
**Problema:** Al acceder directamente a URLs, el estado no se hidrataba correctamente
**Solución:** Mejorado el método `checkAuth()` para manejar la hidratación del estado desde localStorage

## 🎯 Flujo Esperado

1. **Sin autenticación:** Acceso directo a `/app/dashboard` → Redirige a `/auth/login`
2. **Con autenticación:** Acceso directo funciona y muestra el dashboard correspondiente
3. **Roles correctos:** Cada usuario ve solo su área permitida
4. **Redirección automática:** Después del login, vas automáticamente a tu dashboard

## 🚨 Si Aún Tienes Problemas

### Limpiar Estado
```javascript
// En la consola del navegador:
localStorage.clear();
location.reload();
```

### Verificar Estado
```javascript
// Ver tokens:
console.log('Token:', localStorage.getItem('auth_token'));
console.log('Auth Storage:', localStorage.getItem('auth-storage'));

// Ver estado de Zustand (si tienes React DevTools):
// Busca el store 'auth-storage' en las DevTools
```

### Verificar Red
- Abre DevTools → Network
- Verifica que las llamadas a `/auth/login` y `/auth/me` respondan 200
- Verifica que el `user_type` en la respuesta de `/auth/me` sea correcto (sin prefijo `UserType.`)

## 📊 Scripts de Verificación Disponibles

- `python test_login.py` - Prueba todos los logins desde backend
- `python test_frontend_access.py` - Verifica flujo completo
- `python debug_auth.py` - Debug detallado de autenticación
- `test_browser_flow.html` - Interfaz web para pruebas interactivas

## ✅ Estado Actual

- ✅ Backend: Autenticación funciona
- ✅ Backend: Roles se serializan correctamente  
- ✅ Frontend: Store de autenticación mejorado
- ✅ Frontend: AuthGuard protege rutas correctamente
- ✅ Frontend: RoleGuard valida permisos correctamente
- ✅ Persistencia: Estado se mantiene entre recargas

**El sistema debería funcionar completamente ahora. Si aún ves "Acceso Restringido", por favor:**
1. Limpia localStorage
2. Haz login nuevamente
3. Verifica en DevTools que el estado se guarde correctamente