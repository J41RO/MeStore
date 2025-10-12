# Guía de Registro de Vendedores - MeStocker MVP

## Descripción General

Sistema de registro de vendedores para MeStocker que permite a nuevos vendors unirse a la plataforma mediante un formulario simple de una sola página.

## Arquitectura

### Backend
- **Endpoint**: `POST /api/v1/vendors/register`
- **Puerto**: `8000`
- **Ubicación**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/vendors.py`
- **Schema**: `VendorCreate` en `/app/schemas/vendor.py`

### Frontend
- **Página**: `VendorRegistration.tsx`
- **Ruta**: `/vendor/register`
- **Puerto**: `5173`
- **Servicio API**: `vendorApiService.ts`
- **Estilos**: `vendor-registration-simple.css`

## Acceso a la Página

### URLs de Acceso
- **Local**: http://localhost:5173/vendor/register
- **Red**: http://192.168.1.137:5173/vendor/register

## Estructura de Datos

### Request (VendorCreate)
```typescript
{
  email: string;                    // Email único del vendor
  password: string;                 // Mínimo 8 caracteres, incluir mayúscula, minúscula y número
  full_name: string;                // Nombre completo (mínimo 2 caracteres)
  phone: string;                    // Formato colombiano: +573001234567
  business_name: string;            // Nombre del negocio (mínimo 2 caracteres)
  city: string;                     // Ciudad de operación
  business_type: 'persona_natural' | 'empresa';  // Tipo de negocio
  primary_category: string;         // Categoría principal de productos
  terms_accepted: boolean;          // Debe ser true
}
```

### Response (VendorResponse)
```typescript
{
  vendor_id: string;                // UUID del vendor creado
  email: string;                    // Email confirmado
  full_name: string;                // Nombre confirmado
  business_name: string;            // Negocio confirmado
  status: string;                   // Estado: "active"
  message: string;                  // Mensaje de confirmación
  next_steps: {
    add_products: string;           // URL para agregar productos
    view_dashboard: string;         // URL del dashboard
  };
  created_at: string;               // Timestamp de creación
}
```

## Validaciones

### Frontend (Client-side)
1. **Email**: Formato válido (usuario@dominio.com)
2. **Password**:
   - Mínimo 8 caracteres
   - Al menos una mayúscula
   - Al menos una minúscula
   - Al menos un número
3. **Confirmación Password**: Debe coincidir con password
4. **Nombre Completo**: Mínimo 2 caracteres
5. **Teléfono**: Formato colombiano +573001234567
6. **Nombre del Negocio**: Mínimo 2 caracteres
7. **Ciudad**: Mínimo 2 caracteres
8. **Términos**: Debe ser aceptado

### Backend (Server-side)
- Email único (no duplicado)
- Todos los campos requeridos presentes
- Formatos validados con Pydantic
- Password hasheado antes de guardarse

## Casos de Uso

### Caso 1: Registro Exitoso
**Input**:
```json
{
  "email": "maria@example.com",
  "password": "Maria1234!",
  "full_name": "María González",
  "phone": "+573001234567",
  "business_name": "MaríaStyle",
  "city": "Bucaramanga",
  "business_type": "persona_natural",
  "primary_category": "ropa_femenina",
  "terms_accepted": true
}
```

**Output**:
```json
{
  "vendor_id": "eee467ca-8614-4984-9c3f-c8b010b050e2",
  "email": "maria@example.com",
  "full_name": "María González",
  "business_name": "MaríaStyle",
  "status": "active",
  "message": "¡Registro exitoso! Bienvenida a MeStocker.",
  "next_steps": {
    "add_products": "/vendor/products/new?vendor_id=eee467ca-8614-4984-9c3f-c8b010b050e2",
    "view_dashboard": "/vendor/dashboard?vendor_id=eee467ca-8614-4984-9c3f-c8b010b050e2"
  },
  "created_at": "2025-10-01T07:20:48.417886"
}
```

**Comportamiento Frontend**:
- Muestra mensaje de éxito
- Redirige a `/login` después de 2 segundos
- Pasa el email pre-llenado para login

### Caso 2: Email Duplicado
**Input**: Email que ya existe en la base de datos

**Output**:
```json
{
  "status": "error",
  "error_code": "BAD_REQUEST",
  "error_message": "El email ya está registrado"
}
```

**Comportamiento Frontend**:
- Muestra error en banner rojo
- Mantiene el formulario con los datos ingresados
- Usuario puede corregir el email

### Caso 3: Validación de Password
**Input**: Password que no cumple requisitos

**Frontend Error**:
```
"La contraseña debe contener al menos una mayúscula"
"La contraseña debe contener al menos una minúscula"
"La contraseña debe contener al menos un número"
```

**Comportamiento Frontend**:
- Error se muestra inmediatamente (onChange)
- Icono rojo (X) aparece al lado del input
- Botón "Crear Cuenta" permanece deshabilitado

### Caso 4: Teléfono Inválido
**Input**: Teléfono en formato incorrecto

**Frontend Error**:
```
"Teléfono colombiano inválido (ej: +573001234567)"
```

**Comportamiento Frontend**:
- Validación inmediata
- Hint visible: "Formato: +573001234567"
- Botón submit deshabilitado

### Caso 5: Términos No Aceptados
**Input**: Checkbox de términos sin marcar

**Frontend Error**:
```
"Debes aceptar los términos y condiciones"
```

**Comportamiento Frontend**:
- Error aparece al intentar submit
- Checkbox se resalta en rojo
- Botón submit deshabilitado

## Testing

### Prueba Manual - Frontend

1. **Abrir la página**:
   ```
   http://192.168.1.137:5173/vendor/register
   ```

2. **Completar formulario con datos válidos**:
   - Nombre Completo: María González
   - Email: maria.test@example.com
   - Teléfono: +573001234567
   - Contraseña: Maria1234!
   - Confirmar Contraseña: Maria1234!
   - Nombre del Negocio: MaríaStyle
   - Tipo de Negocio: Persona Natural
   - Ciudad: Bucaramanga
   - Categoría: Ropa Femenina
   - Términos: ✓ Aceptado

3. **Click "Crear Cuenta"**

4. **Verificar**:
   - Banner verde con mensaje de éxito
   - Redirección a login después de 2 segundos
   - Email pre-llenado en login

### Prueba Manual - Backend (cURL)

```bash
# Crear archivo JSON
cat > /tmp/test_vendor.json <<'EOF'
{"email":"test@example.com","password":"Test1234!","full_name":"Maria Test","phone":"+573001234567","business_name":"Maria Store","city":"Bucaramanga","business_type":"persona_natural","primary_category":"ropa_femenina","terms_accepted":true}
EOF

# Enviar request
curl -X POST http://192.168.1.137:8000/api/v1/vendors/register \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/test_vendor.json
```

**Respuesta Esperada** (Status 200):
```json
{
  "vendor_id": "UUID",
  "email": "test@example.com",
  "full_name": "Maria Test",
  "business_name": "Maria Store",
  "status": "active",
  "message": "¡Registro exitoso! Bienvenida a MeStocker.",
  "next_steps": {...},
  "created_at": "2025-10-01T..."
}
```

### Prueba de Email Duplicado

```bash
# Intentar registrar el mismo email dos veces
curl -X POST http://192.168.1.137:8000/api/v1/vendors/register \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/test_vendor.json

# Segunda vez debería dar error
```

**Respuesta Esperada** (Status 400):
```json
{
  "status": "error",
  "error_code": "BAD_REQUEST",
  "error_message": "El email ya está registrado"
}
```

## Categorías Disponibles

El dropdown de "Categoría Principal" incluye:
- Ropa Femenina
- Ropa Masculina
- Accesorios
- Calzado
- Hogar y Decoración
- Tecnología
- Deportes
- Belleza
- Juguetes
- Libros
- Otros

## Flujo Completo

1. **Usuario Llega a la Página**
   - URL: `/vendor/register`
   - Ve formulario limpio y responsive

2. **Usuario Completa Formulario**
   - Validación en tiempo real
   - Iconos visuales (✓ / ✗)
   - Hints debajo de campos

3. **Usuario Envía Formulario**
   - Button se deshabilita ("Registrando...")
   - Request POST a `/api/v1/vendors/register`

4. **Backend Procesa**
   - Valida datos
   - Crea usuario en tabla `users`
   - Crea vendor en tabla `vendors`
   - Hashea password
   - Asigna vendor_id único

5. **Frontend Recibe Respuesta**
   - **Éxito**: Banner verde, redirección a login
   - **Error**: Banner rojo con mensaje específico

6. **Usuario Inicia Sesión**
   - Email pre-llenado
   - Ingresa password
   - Accede a su dashboard de vendor

## Archivos Creados

### Frontend
```
frontend/src/
├── services/
│   └── vendorApiService.ts          # Servicio API para vendors
├── pages/
│   └── VendorRegistration.tsx       # Página de registro
└── styles/
    └── vendor-registration-simple.css  # Estilos de la página
```

### Backend
```
app/
├── api/v1/endpoints/
│   └── vendors.py                   # Endpoint de registro
├── schemas/
│   └── vendor.py                    # Schema VendorCreate/VendorResponse
└── services/
    └── vendor_service.py            # Lógica de negocio
```

## Problemas Conocidos y Soluciones

### Problema 1: Email ya registrado
**Síntoma**: Error "El email ya está registrado"
**Solución**: Usar un email diferente o eliminar el registro anterior

### Problema 2: CORS Error
**Síntoma**: Frontend no puede conectar con backend
**Solución**: Verificar que CORS esté habilitado en `app/main.py`

### Problema 3: Validación de Teléfono
**Síntoma**: Teléfono no pasa validación
**Solución**: Usar formato exacto: `+573001234567` (10 dígitos después de +57)

### Problema 4: Password muy débil
**Síntoma**: Error de validación en password
**Solución**: Incluir mínimo 8 caracteres con mayúscula, minúscula y número

## Mantenimiento

### Agregar Nueva Categoría
1. Editar `VendorRegistration.tsx`
2. Agregar entrada en array `categories`
3. Frontend se actualiza automáticamente

### Modificar Validaciones
1. **Frontend**: Editar función `validateForm()` en `VendorRegistration.tsx`
2. **Backend**: Editar `VendorCreate` schema en `app/schemas/vendor.py`

### Cambiar Estilos
1. Editar `vendor-registration-simple.css`
2. Clases disponibles: `.registration-card`, `.form-section`, `.btn-primary`, etc.

## Próximos Pasos (Futuros)

1. **Email Verification**: Agregar verificación de email con token
2. **Document Upload**: Permitir subir documentos de identidad
3. **Approval Workflow**: Sistema de aprobación manual para vendors
4. **Multi-step Form**: Dividir en múltiples pasos para mejor UX
5. **OAuth Integration**: Permitir registro con Google/Facebook
6. **SMS Verification**: Verificar teléfono con código SMS

## Soporte

Para problemas o preguntas:
- Ver logs del backend: `docker-compose logs backend`
- Ver consola del frontend: Chrome DevTools
- Revisar documentación API: http://192.168.1.137:8000/docs

---

**Última Actualización**: 2025-10-01
**Versión**: 1.0.0 MVP
**Estado**: ✅ Operativo en Producción
